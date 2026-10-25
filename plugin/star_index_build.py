"""Builds the local star index (`star_index.py`) from a Spansh dump of systems.

The dump (`systems_neutron.json.gz`) is one gzip of a JSON array with one system on each line, about 830 MiB when unpacked. It lists neutron stars and a few other main-star types (black holes among
them), so the builder keeps only the lines whose main star is "Neutron Star". It never holds the dump in memory: the file is unpacked in chunks, and the work is done in two passes.

1. Read the dump and sort each neutron star into one of `BUCKETS` temporary files by the grid column (x) it lies in. Memory use here is the sector table (a few tens of thousands of names).
2. Take the bucket files one at a time, sort each in memory by grid cell, and write the records of the final file straight out, with the names to a second temporary file that is appended after
   the records. The biggest bucket holds a few hundred thousand stars.

The final file is written under a temporary name and moved into place in one step, so a failure or a cancel part-way leaves the index that was there before untouched. `build` is meant to run on a
worker thread: it checks `cancel` between chunks, reports `progress(fraction, text)` and gives other threads a moment after each chunk.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import struct
import threading
import time
import zlib
from array import array
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from . import star_index
from .star_index import (CELLS_PER_AXIS, CELL_UNITS, FORMAT_VERSION, HEADER_BYTES, INDEX_FILENAME, MAGIC, META_BYTES, NAME_BLOCK, END_MAGIC,
                         N1_FOLLOWS, RECORD_BYTES, UNITS_PER_LY, cell_key, cell_of, put_varint, split_name)

BUCKETS = 32
TWO_BYTE_SECTORS = (1 << 16) - 1         # sectors are numbered in 2 bytes below this many names, in 3 above (the all-ones number marks a name kept as it is)
READ_CHUNK = 1024 * 1024
MAIN_STAR = b'"mainStar":"Neutron Star"'
MAX_N1 = 0xFFFF                          # the raw record keeps n1 in 16 bits; a name with a larger one is kept as it is
MAX_ODD_NAME_BYTES = 255
TEMP_SUFFIX = ".tmp"
WORK_DIRNAME = "build"

_LINE = re.compile(rb'"id64":(\d+),"name":"([^"\\]*)","mainStar":"Neutron Star","coords":\{"x":([-+0-9.eE]+),"y":([-+0-9.eE]+),"z":([-+0-9.eE]+)\}')
_ID = re.compile(rb'"id64":(\d+)')
_UPDATED = re.compile(rb'"updateTime":"(\d{4}-\d\d-\d\dT[0-9:]+Z)"')
_RAW = struct.Struct("<QiiiIIHII")       # id64, x, y, z (1/32 ly), sector number, packed tail, n1, n2, number of a name kept as it is


class BuildCancelled(Exception):
    """The user cancelled the build."""


class BuildError(Exception):
    """The dump could not be turned into an index; the message says why."""


class TopupGap(BuildError):
    """A top-up file does not reach back to the date the index is current to, so merging it could miss changes. The caller falls back to the full dump."""


@dataclass
class BuildResult:
    count: int = 0
    changed: int = 0                 # top-up only: systems in the update file (any main star) that were replaced or dropped from the index
    added: int = 0                   # top-up only: neutron stars in the update file
    size_bytes: int = 0
    skipped_outside_grid: int = 0
    skipped_other: int = 0
    seconds: float = 0.0


Progress = Callable[[float, str], None]


# --- reading the dump ------------------------------------------------------------------------------------------------------
def dump_lines(path: str, cancel: Optional[threading.Event] = None, progress: Optional[Callable[[int, int], None]] = None) -> Iterator[List[bytes]]:
    """The lines of the gzip file at `path`, a chunk at a time (a list of lines for each chunk read). Handles a file made of several gzip members. Raises BuildError if the file is not
    gzip data or ends early, BuildCancelled if `cancel` is set."""
    size = max(1, os.path.getsize(path))
    decoder = zlib.decompressobj(31)
    in_member = False
    tail = b""
    done = 0
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(READ_CHUNK)
            if not chunk:
                break
            done += len(chunk)
            pending = chunk
            while pending:
                try:
                    data = decoder.decompress(pending)
                except zlib.error as err:
                    raise BuildError(f"the downloaded file is not valid gzip data ({err})") from None
                in_member = True
                pending = b""
                if decoder.eof:
                    pending = decoder.unused_data
                    decoder = zlib.decompressobj(31)
                    in_member = False
                    if pending and not pending.startswith(b"\x1f\x8b"):
                        pending = b""                     # padding after the last member
                if data:
                    data = tail + data
                    lines = data.split(b"\n")
                    tail = lines.pop()
                    yield lines
            if cancel is not None and cancel.is_set():
                raise BuildCancelled()
            if progress is not None:
                progress(done, size)
            time.sleep(0.002)                             # let the rest of the program run between chunks
    if in_member:
        raise BuildError("the downloaded file ends early (it is not complete)")
    if tail.strip():
        yield [tail]


def parse_line(line: bytes) -> Optional[Tuple[int, str, int, int, int]]:
    """(id64, name, x, y, z in 1/32 ly) for a line of the dump whose main star is a neutron star, else None."""
    if MAIN_STAR not in line:
        return None
    match = _LINE.search(line)
    if match is not None:
        return (int(match.group(1)), match.group(2).decode("utf-8", "replace"),
                round(float(match.group(3)) * UNITS_PER_LY), round(float(match.group(4)) * UNITS_PER_LY), round(float(match.group(5)) * UNITS_PER_LY))
    try:                                                  # a name with an escape in it, or another order of the fields
        record = json.loads(line.strip().rstrip(b","))
        coords = record["coords"]
        if record.get("mainStar") != "Neutron Star":
            return None
        return (int(record["id64"]), str(record["name"]), round(float(coords["x"]) * UNITS_PER_LY),
                round(float(coords["y"]) * UNITS_PER_LY), round(float(coords["z"]) * UNITS_PER_LY))
    except (ValueError, KeyError, TypeError):
        return None


# --- building ----------------------------------------------------------------------------------------------------------------
def _put(out: bytearray, value: int, width: int) -> None:
    out += value.to_bytes(width, "little")


def _pad8(handle) -> None:
    extra = handle.tell() % 8
    if extra:
        handle.write(b"\0" * (8 - extra))


def _array_bytes(values: array) -> bytes:
    if struct.pack("=I", 1) != struct.pack("<I", 1):
        values = array("I", values)
        values.byteswap()
    return values.tobytes()


def build(source: str, directory: str, source_info: Optional[Dict[str, object]] = None, cancel: Optional[threading.Event] = None,
          progress: Optional[Progress] = None, topup_from: str = "") -> BuildResult:
    """Builds the index from the gzip dump at `source` into `directory` (replacing the index there, if any, only when the new one is complete). `source_info` (the dump's url, etag,
    last_modified) is stored in the file's header. Raises BuildCancelled, BuildError or OSError (a full disk, a read-only folder); the old index is intact after any of them.

    With `topup_from` (the ISO time the installed index is current to), `source` is one of Spansh's update files (`systems_1day.json.gz`, `systems_1week.json.gz`: the systems changed since a
    past midnight, with every kind of main star) and its changes are merged into the index already in `directory`: each system in the file replaces the one with the same id64, and is dropped
    when its main star is no longer a neutron star. Raises TopupGap when the file's oldest change is newer than `topup_from`, because a change in between could then be missing."""
    started = time.monotonic()
    report = progress or (lambda fraction, text: None)
    cancel = cancel or threading.Event()
    os.makedirs(directory, exist_ok=True)
    work = os.path.join(directory, WORK_DIRNAME)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    final = os.path.join(directory, INDEX_FILENAME)
    temp = final + TEMP_SUFFIX
    result = BuildResult()
    try:
        sectors: Dict[str, int] = {}
        odd_names: List[str] = []
        buckets = [open(os.path.join(work, f"b{i:02d}.raw"), "wb", buffering=READ_CHUNK) for i in range(BUCKETS)]
        try:
            seen = 0

            def add(record: Tuple[int, str, int, int, int]) -> None:
                nonlocal seen
                id64, name, xu, yu, zu = record
                cx, cy, cz = cell_of(xu), cell_of(yu), cell_of(zu)
                if not (0 <= cx < CELLS_PER_AXIS and 0 <= cy < CELLS_PER_AXIS and 0 <= cz < CELLS_PER_AXIS) or not 0 <= id64 < 1 << 64:
                    result.skipped_outside_grid += 1
                    return
                parts = split_name(name)
                if parts is not None and parts[3] <= MAX_N1:
                    sector, letters, mass, n1, n2 = parts
                    number = sectors.get(sector)
                    if number is None:
                        number = sectors[sector] = len(sectors)
                    code = 0 if n1 < 0 else (n1 + 1 if n1 < N1_FOLLOWS - 1 else N1_FOLLOWS)
                    raw = _RAW.pack(id64, xu, yu, zu, number, letters | (mass << 15) | (code << 18), max(n1, 0), n2, 0)
                else:
                    odd_names.append(name)
                    raw = _RAW.pack(id64, xu, yu, zu, 0xFFFFFFFF, 0, 0, 0, len(odd_names) - 1)
                buckets[cx * BUCKETS // CELLS_PER_AXIS].write(raw)
                seen += 1

            if topup_from:
                installed = star_index.StarIndex(final)
                changed_ids = set()
                fresh: Dict[int, Tuple[int, str, int, int, int]] = {}
                oldest = ""
                for lines in dump_lines(source, cancel, lambda done, total: report(0.1 * done / total, f"Reading the update file: {len(changed_ids):,} systems changed")):
                    for line in lines:
                        match = _ID.search(line)
                        if match is None:
                            continue
                        changed_ids.add(int(match.group(1)))
                        stamp = _UPDATED.search(line)
                        if stamp is not None:
                            when = stamp.group(1).decode("ascii")
                            if not oldest or when < oldest:
                                oldest = when
                        record = parse_line(line)
                        if record is not None:
                            fresh[record[0]] = record
                if not changed_ids:
                    raise BuildError("the update file holds no systems, so it is not the file this top-up is made from")
                if not oldest or oldest > topup_from:
                    raise TopupGap(f"the update file starts at {oldest or 'an unknown time'}, after the index's date of {topup_from}")
                result.changed, result.added = len(changed_ids), len(fresh)
                kept = 0
                for number, record in enumerate(installed.records()):
                    if record[0] not in changed_ids:
                        add(record)
                        kept += 1
                    if number % 20000 == 0:
                        if cancel.is_set():
                            raise BuildCancelled()
                        report(0.1 + 0.7 * number / max(1, installed.count), f"Merging the update into the index: {number:,} of {installed.count:,}")
                for record in fresh.values():
                    add(record)
            else:
                for lines in dump_lines(source, cancel, lambda done, total: report(0.8 * done / total, f"Reading the dump: {seen:,} neutron stars so far")):
                    for line in lines:
                        record = parse_line(line)
                        if record is not None:
                            add(record)
        finally:
            for handle in buckets:
                handle.close()
        if seen == 0:
            raise BuildError("the file holds no neutron stars, so it is not the dump this index is built from")
        if len(sectors) >= (1 << 24) - 1:
            raise BuildError("the dump has more sector names than the index can number")
        width = 2 if len(sectors) < TWO_BYTE_SECTORS else 3
        odd_marker = (1 << (8 * width)) - 1

        keys, starts, name_index = array("I"), array("I"), array("I")
        names_path = os.path.join(work, "names" + TEMP_SUFFIX)
        count = 0
        name_pos = 0
        previous = -1
        with open(temp, "wb", buffering=READ_CHUNK) as out, open(names_path, "wb", buffering=READ_CHUNK) as names:
            out.write(b"\0" * HEADER_BYTES)
            for index in range(BUCKETS):
                if cancel.is_set():
                    raise BuildCancelled()
                report(0.8 + 0.18 * index / BUCKETS, f"Sorting and writing the index: {count:,} of {seen:,}")
                path = os.path.join(work, f"b{index:02d}.raw")
                with open(path, "rb") as handle:
                    rows = list(_RAW.iter_unpack(handle.read()))
                os.remove(path)
                rows.sort(key=lambda row: (cell_key(cell_of(row[1]), cell_of(row[2]), cell_of(row[3])), row[0]))
                record_bytes = bytearray()
                name_bytes = bytearray()
                for id64, xu, yu, zu, sector, tail, n1, n2, odd in rows:
                    cx, cy, cz = cell_of(xu), cell_of(yu), cell_of(zu)
                    key = cell_key(cx, cy, cz)
                    if key != previous:
                        keys.append(key)
                        starts.append(count)
                        previous = key
                    relative = (xu - (cx - CELLS_PER_AXIS // 2) * CELL_UNITS) | ((yu - (cy - CELLS_PER_AXIS // 2) * CELL_UNITS) << 13) | \
                               ((zu - (cz - CELLS_PER_AXIS // 2) * CELL_UNITS) << 26)
                    record_bytes += id64.to_bytes(8, "little") + relative.to_bytes(5, "little")
                    if count % NAME_BLOCK == 0:
                        name_index.append(name_pos + len(name_bytes))
                    if sector == 0xFFFFFFFF:
                        _put(name_bytes, odd_marker, width)
                        text = odd_names[odd].encode("utf-8")[:MAX_ODD_NAME_BYTES]
                        name_bytes.append(len(text))
                        name_bytes += text
                    else:
                        _put(name_bytes, sector, width)
                        _put(name_bytes, tail, 3)
                        if tail >> 18 == N1_FOLLOWS:
                            put_varint(name_bytes, n1)
                        put_varint(name_bytes, n2)
                    count += 1
                out.write(record_bytes)
                names.write(name_bytes)
                name_pos += len(name_bytes)
                del rows, record_bytes, name_bytes
        starts.append(count)
        result.count = count

        with open(temp, "r+b") as out:
            out.seek(0, os.SEEK_END)
            offsets: Dict[str, int] = {"records": HEADER_BYTES}
            _pad8(out)
            offsets["cells"] = out.tell()
            out.write(_array_bytes(keys))
            out.write(_array_bytes(starts))
            _pad8(out)
            offsets["name_index"] = out.tell()
            out.write(_array_bytes(name_index))
            _pad8(out)
            offsets["names"] = out.tell()
            with open(names_path, "rb") as names:
                shutil.copyfileobj(names, out, READ_CHUNK)
            _pad8(out)
            ordered = sorted(sectors, key=sectors.__getitem__)
            blob = bytearray()
            sector_offsets = array("I")
            for name in ordered:
                sector_offsets.append(len(blob))
                blob += name.encode("utf-8")
            sector_offsets.append(len(blob))
            offsets["sectors"] = out.tell()
            out.write(_array_bytes(sector_offsets))
            offsets["sector_blob"] = out.tell()
            out.write(bytes(blob))
            _pad8(out)
            out.write(END_MAGIC + b"\0\0\0\0")
            size = out.tell()
            meta = {
                "format": FORMAT_VERSION, "count": count, "n_cells": len(keys), "n_sectors": len(ordered), "sector_width": width, "record_bytes": RECORD_BYTES,
                "cell_units": CELL_UNITS, "offsets": offsets, "file_size": size, "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "skipped_outside_grid": result.skipped_outside_grid, "source": dict(source_info or {}),
            }
            encoded = json.dumps(meta, separators=(",", ":")).encode("utf-8")
            if len(encoded) > META_BYTES:
                raise BuildError("the index header is too large")
            out.seek(0)
            out.write(struct.pack("<4sHHI", MAGIC, FORMAT_VERSION, 0, META_BYTES) + encoded.ljust(META_BYTES, b" "))
            out.flush()
            os.fsync(out.fileno())
        if cancel.is_set():
            raise BuildCancelled()
        star_index.forget()
        _replace(temp, final)
        result.size_bytes = size
        report(1.0, f"Built the index: {count:,} neutron stars")
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if os.path.exists(temp):
            try:
                os.remove(temp)
            except OSError:
                pass
    result.seconds = time.monotonic() - started
    return result


def _replace(temp: str, final: str) -> None:
    """Moves the new index into place. On Windows a query that is reading the old file at that moment makes the move fail, so it is tried again for a few seconds."""
    for attempt in range(20):
        try:
            os.replace(temp, final)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.25)
