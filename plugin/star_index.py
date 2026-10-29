"""The local star index: a compact file of neutron stars that answers "the nearest neutron star to here" without a network request.

Where the data comes from, how it is fetched and how it is built are in `star_index_download.py` and `star_index_build.py`; this module is the file format, the reader and the query. It uses only
the standard library and keeps no file open between queries (an open file would stop Windows from replacing or deleting the index).

**What the index holds.** One entry for each system whose main star is a neutron star: the system address (id64), its position and its name. Only main stars are in the source data, so a neutron star
that is a secondary star of a system is not listed. The position is kept to 1/32 light year, which is the precision of the source.

**The file** (`star_index/neutron.wfsi`, all numbers little-endian). A header of `HEADER_BYTES` (magic, format version, then a JSON block with the counts, the section offsets and where the data came from),
and these sections, each starting on an 8-byte boundary:

- records: `count` entries of 13 bytes, sorted by grid cell and then by id64. Each is the id64 (8 bytes) and the position inside its cell as three 13-bit numbers (5 bytes, x then y then z,
  in 1/32 ly from the cell's corner). The grid cells are cubes `CELL_LY` light years on a side.
- cell table: the keys of the cells that hold at least one record (unsigned 32-bit, sorted) and then the number of the first record of each cell (and one more, the total), so a query
  finds the cells near a position with a binary search and reads only their records.
- name index and names: the name of each record is stored in a compact form (the sector name as a number into the sector table, the `AB-C d3` part packed into 3 bytes, the number after the dash as a variable-length integer) and the offset of every
  `NAME_BLOCK`th name, so one name is found by skipping at most 63 others. A name that does not have that shape is stored as it is.
- sector table: the sector names, with offsets.
- the end marker, so a file cut short is recognized.

A file that is missing, cut short, from another format version, or damaged is reported by `status` and ignored: the N.S. button then asks Spansh as before.
"""
from __future__ import annotations

import bisect
import json
import math
import os
import re
import struct
import threading
from array import array
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

MAGIC = b"WFSI"
END_MAGIC = b"WFSE"
FORMAT_VERSION = 1
HEADER_BYTES = 2064                 # 12 bytes of header, then room for the JSON block (padded with spaces), a multiple of 8
META_BYTES = HEADER_BYTES - 12
INDEX_DIRNAME = "star_index"        # in the plugin folder; listed in update._OWN_DIRS
INDEX_FILENAME = "neutron.wfsi"
RECORD_BYTES = 13
UNITS_PER_LY = 32                   # the source gives positions in multiples of 1/32 ly
CELL_UNITS = 8192                   # a cell is 8192 units = 256 ly on a side, so a position inside it fits in 13 bits per axis
CELL_LY = CELL_UNITS // UNITS_PER_LY
CELLS_PER_AXIS = 1024               # the grid covers +-131,072 ly on every axis, far more than the galaxy
CELL_ORIGIN = CELLS_PER_AXIS // 2
NAME_BLOCK = 64
N1_FOLLOWS = 31                     # in a packed name: the 5-bit code of n1 when n1 is too large for the code and is stored after it
LETTER_BASE = 26
DEFAULT_MAX_RADIUS_LY = 5000.0
FIRST_RADIUS_LY = 256.0

_NAME_TAIL = re.compile(r"^(.+) ([A-Z])([A-Z])-([A-Z]) ([a-h])(?:(\d+)-)?(\d+)$")
_SECTOR_STRUCT = struct.Struct("<I")


class IndexUnusable(Exception):
    """The index file cannot be used. `kind` is "missing" (no file), "damaged" (cut short, not an index) or "old" (another format version)."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind


@dataclass(frozen=True)
class StarHit:
    name: str
    id64: int
    x: float
    y: float
    z: float
    distance_ly: float


@dataclass
class IndexStatus:
    """What `status` found: state is "missing", "ok", "damaged" or "old"; the rest is filled when the file could be read."""
    state: str = "missing"
    message: str = ""
    count: int = 0
    size_bytes: int = 0
    built: str = ""                 # when WFMT built the index (UTC, ISO)
    source_modified: str = ""       # the Last-Modified of the file the index is current to (the full dump, or the latest top-up), as the server sent it
    etag: str = ""                  # that file's ETag
    full_modified: str = ""         # the Last-Modified of the full dump the index started from
    full_etag: str = ""
    topups: int = 0                 # how many top-ups (the 1-day and 1-week files) have been merged in since that dump

    @property
    def usable(self) -> bool:
        return self.state == "ok"


# --- locations ------------------------------------------------------------------------------------------------------------
CONFIG_USE = "wfmt_star_index_use"  # Settings > General > Online lookups: use the local index for Neutron Star when it is installed (on unless turned off)


def use_local_index() -> bool:
    """Whether the N.S. button may use the local index: the saved tick, on when never changed."""
    try:
        from config import config
        return bool(config.get_bool(CONFIG_USE, default=True))
    except Exception:                                   # noqa: BLE001 - no settings available (a test, a tool): the default
        return True


def default_dir() -> str:
    """The star index folder inside the plugin folder."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), INDEX_DIRNAME)


def index_path(directory: Optional[str] = None) -> str:
    return os.path.join(directory or default_dir(), INDEX_FILENAME)


# --- the name codec (shared with the builder) --------------------------------------------------------------------------------
def split_name(name: str) -> Optional[Tuple[str, int, int, int, int]]:
    """(sector, letters, mass code, n1 or -1, n2) for a name like "Eol Prou RS-T d3-94", or None for a name that does not have that shape or would not read back the same."""
    match = _NAME_TAIL.match(name)
    if match is None:
        return None
    sector, a, b, c, mass, n1, n2 = match.groups()
    letters = ((ord(a) - 65) * LETTER_BASE + (ord(b) - 65)) * LETTER_BASE + (ord(c) - 65)
    found = (sector, letters, ord(mass) - 97, int(n1) if n1 is not None else -1, int(n2))
    if join_name(*found) != name:
        return None                     # leading zeros and the like: keep the name as it is
    return found


def join_name(sector: str, letters: int, mass: int, n1: int, n2: int) -> str:
    c = letters % LETTER_BASE
    b = (letters // LETTER_BASE) % LETTER_BASE
    a = letters // (LETTER_BASE * LETTER_BASE)
    tail = f"{chr(65 + a)}{chr(65 + b)}-{chr(65 + c)} {chr(97 + mass)}" + (f"{n1}-{n2}" if n1 >= 0 else f"{n2}")
    return f"{sector} {tail}"


def put_varint(out: bytearray, value: int) -> None:
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)


def get_varint(data: bytes, pos: int) -> Tuple[int, int]:
    value = shift = 0
    while True:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, pos
        shift += 7


def cell_of(units: int) -> int:
    """The grid cell (0 to CELLS_PER_AXIS - 1) holding a coordinate given in 1/32 ly; -1 or CELLS_PER_AXIS when it is outside the grid."""
    return units // CELL_UNITS + CELL_ORIGIN


def cell_key(cx: int, cy: int, cz: int) -> int:
    return (cx << 20) | (cy << 10) | cz


# --- reading ------------------------------------------------------------------------------------------------------------
def read_meta(path: str) -> Dict[str, object]:
    """The header block of the index at `path`, after checking that the file is whole and of this format. Raises IndexUnusable."""
    try:
        size = os.path.getsize(path)
    except FileNotFoundError:
        raise IndexUnusable("missing", "no local star index is installed") from None
    except OSError as err:
        raise IndexUnusable("damaged", f"the index cannot be read ({err})") from None
    try:
        with open(path, "rb") as handle:
            head = handle.read(HEADER_BYTES)
            if size < HEADER_BYTES + 8:
                raise IndexUnusable("damaged", "the file is too short to be a star index")
            magic, version, _reserved, meta_len = struct.unpack_from("<4sHHI", head)
            if magic != MAGIC:
                raise IndexUnusable("damaged", "the file is not a star index")
            if version != FORMAT_VERSION:
                raise IndexUnusable("old", f"the index is format {version}; this WFMT reads format {FORMAT_VERSION}")
            try:
                meta = json.loads(head[12:12 + min(meta_len, META_BYTES)].decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                raise IndexUnusable("damaged", "the index header cannot be read") from None
            handle.seek(size - 8)
            if handle.read(4) != END_MAGIC or not isinstance(meta, dict) or meta.get("file_size") != size:
                raise IndexUnusable("damaged", "the index is incomplete (it ends early)")
    except OSError as err:
        raise IndexUnusable("damaged", f"the index cannot be read ({err})") from None
    return meta


def status(directory: Optional[str] = None) -> IndexStatus:
    """What is installed, from the header only (the records are not read)."""
    path = index_path(directory)
    if not os.path.isfile(path):
        return IndexStatus("missing", "not installed")
    try:
        meta = read_meta(path)
    except IndexUnusable as err:
        return IndexStatus(err.kind, str(err), size_bytes=_size(path))
    source = meta.get("source") if isinstance(meta.get("source"), dict) else {}
    modified = str(source.get("last_modified", ""))
    etag = str(source.get("etag", ""))
    return IndexStatus("ok", "installed", count=int(meta.get("count", 0)), size_bytes=_size(path), built=str(meta.get("built", "")),
                       source_modified=modified, etag=etag, full_modified=str(source.get("full_modified", modified)),
                       full_etag=str(source.get("full_etag", etag)), topups=int(source.get("topups", 0) or 0))


def _size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


_cache_lock = threading.Lock()
_cache: Dict[str, Tuple[Tuple[int, int], array, array, Dict[str, object]]] = {}


def _cell_table(path: str) -> Tuple[array, array, Dict[str, object]]:
    """The cell keys and first-record numbers of the index at `path`, read once and kept while the file stays the same (about 8 bytes for each occupied cell)."""
    try:
        stat = os.stat(path)
    except FileNotFoundError:
        raise IndexUnusable("missing", "no local star index is installed") from None
    except OSError as err:
        raise IndexUnusable("damaged", f"the index cannot be read ({err})") from None
    token = (stat.st_size, stat.st_mtime_ns)
    with _cache_lock:
        held = _cache.get(path)
        if held is not None and held[0] == token:
            return held[1], held[2], held[3]
    meta = read_meta(path)
    keys, starts = array("I"), array("I")
    try:
        cells = int(meta["n_cells"])
        where = int(meta["offsets"]["cells"])           # type: ignore[index]
        with open(path, "rb") as handle:
            handle.seek(where)
            keys.frombytes(handle.read(4 * cells))
            starts.frombytes(handle.read(4 * (cells + 1)))
    except (KeyError, TypeError, ValueError, OSError):
        raise IndexUnusable("damaged", "the index header is not complete") from None
    if struct.pack("=I", 1) != struct.pack("<I", 1):    # a big-endian machine
        keys.byteswap()
        starts.byteswap()
    if len(keys) != cells or len(starts) != cells + 1:
        raise IndexUnusable("damaged", "the cell table is cut short")
    with _cache_lock:
        _cache.clear()                                  # one index at a time
        _cache[path] = (token, keys, starts, meta)
    return keys, starts, meta


def forget() -> None:
    """Drops what is kept in memory about the index (after it was replaced or deleted)."""
    with _cache_lock:
        _cache.clear()


class StarIndex:
    """Queries the index at `path`. Raises IndexUnusable from the constructor when the file is missing, cut short or of another format."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or index_path()
        self._keys, self._starts, self.meta = _cell_table(self.path)
        self.count = int(self.meta["count"])

    # --- the query --------------------------------------------------------------------------------------------------
    def nearest(self, x: float, y: float, z: float, count: int = 1, max_radius_ly: float = DEFAULT_MAX_RADIUS_LY) -> List[StarHit]:
        """The `count` neutron stars nearest to (x, y, z) in light years, nearest first, looking out to `max_radius_ly` (fewer come back when there are not that many that close). The search
        widens in steps, so a star in a busy area is found by reading a handful of cells."""
        count = max(1, int(count))
        radius = FIRST_RADIUS_LY
        while True:
            radius = min(radius, max_radius_ly)
            found = self._within(x, y, z, radius, count)
            if len(found) >= count or radius >= max_radius_ly:
                return found
            radius *= 2

    def _within(self, x: float, y: float, z: float, radius: float, count: int) -> List[StarHit]:
        keys, starts = self._keys, self._starts
        scale = UNITS_PER_LY / CELL_UNITS
        lo = [max(0, int(math.floor((c - radius) * scale)) + CELL_ORIGIN) for c in (x, y, z)]
        hi = [min(CELLS_PER_AXIS - 1, int(math.floor((c + radius) * scale)) + CELL_ORIGIN) for c in (x, y, z)]
        limit2 = radius * radius
        cells: List[Tuple[float, int, int, int]] = []          # (smallest possible distance squared, position in the cell table, cell x, cell y * CELLS_PER_AXIS + cell z)
        for cx in range(lo[0], hi[0] + 1):
            dx = _gap(x, cx - CELL_ORIGIN)
            for cy in range(lo[1], hi[1] + 1):
                dxy = dx + _gap(y, cy - CELL_ORIGIN)
                if dxy > limit2:
                    continue
                first = cell_key(cx, cy, lo[2])
                at = bisect.bisect_left(keys, first)
                end = cell_key(cx, cy, hi[2])
                while at < len(keys) and keys[at] <= end:
                    cz = keys[at] & 0x3FF
                    d2 = dxy + _gap(z, cz - CELL_ORIGIN)
                    if d2 <= limit2:
                        cells.append((d2, at, cx, cy * CELLS_PER_AXIS + cz))
                    at += 1
        cells.sort()
        best: List[Tuple[float, int, int, float, float, float]] = []     # (distance squared, record number, id64, x, y, z), the nearest `count` so far
        with open(self.path, "rb") as handle:
            records_at = int(self.meta["offsets"]["records"])           # type: ignore[index]
            for d2, at, cx, ycz in cells:
                if len(best) >= count and d2 > best[-1][0]:
                    break
                cy, cz = divmod(ycz, CELLS_PER_AXIS)
                first, last = starts[at], starts[at + 1]
                handle.seek(records_at + first * RECORD_BYTES)
                data = handle.read((last - first) * RECORD_BYTES)
                ox, oy, oz = (cx - CELL_ORIGIN) * CELL_UNITS, (cy - CELL_ORIGIN) * CELL_UNITS, (cz - CELL_ORIGIN) * CELL_UNITS
                for number, (id64, low, high) in enumerate(struct.iter_unpack("<QIB", data), first):
                    rel = low | (high << 32)
                    px = (ox + (rel & 0x1FFF)) / UNITS_PER_LY
                    py = (oy + ((rel >> 13) & 0x1FFF)) / UNITS_PER_LY
                    pz = (oz + ((rel >> 26) & 0x1FFF)) / UNITS_PER_LY
                    dist2 = (px - x) ** 2 + (py - y) ** 2 + (pz - z) ** 2
                    if dist2 > limit2:
                        continue
                    if len(best) < count or dist2 < best[-1][0]:
                        bisect.insort(best, (dist2, number, id64, px, py, pz))
                        del best[count:]
            return [StarHit(self._name(handle, number), id64, px, py, pz, math.sqrt(dist2)) for dist2, number, id64, px, py, pz in best]

    def records(self):
        """Every record in the file as (id64, name, x, y, z) with the position in 1/32 ly, in file order. Used to merge a top-up into the index; it reads the file once from start to end."""
        meta = self.meta
        offsets = meta["offsets"]
        width = int(meta["sector_width"])
        sectors = self._all_sectors()
        records_at, count = int(offsets["records"]), self.count                # type: ignore[index]
        keys, starts = self._keys, self._starts
        with open(self.path, "rb") as handle, open(self.path, "rb") as names:
            names.seek(int(offsets["names"]))                                  # type: ignore[index]
            names_end = int(offsets["sectors"])                                # type: ignore[index]
            data = b""
            data_at = 0
            number = 0
            for at in range(len(keys)):
                first, last = starts[at], starts[at + 1]
                cx, cy, cz = keys[at] >> 20, (keys[at] >> 10) & 0x3FF, keys[at] & 0x3FF
                ox, oy, oz = (cx - CELL_ORIGIN) * CELL_UNITS, (cy - CELL_ORIGIN) * CELL_UNITS, (cz - CELL_ORIGIN) * CELL_UNITS
                handle.seek(records_at + first * RECORD_BYTES)
                for id64, low, high in struct.iter_unpack("<QIB", handle.read((last - first) * RECORD_BYTES)):
                    if len(data) - data_at < 300:                              # the longest entry is under 270 bytes: top the buffer up
                        more = names.read(max(0, min(1 << 20, names_end - names.tell())))
                        data, data_at = data[data_at:] + more, 0
                    name, data_at = _entry_name(data, data_at, width, sectors.__getitem__)
                    rel = low | (high << 32)
                    yield id64, name, ox + (rel & 0x1FFF), oy + ((rel >> 13) & 0x1FFF), oz + ((rel >> 26) & 0x1FFF)
                    number += 1
            if number != count:
                raise IndexUnusable("damaged", "the index holds a different number of records than its header says")

    def _all_sectors(self) -> List[str]:
        offsets = self.meta["offsets"]
        total = int(self.meta["n_sectors"])
        with open(self.path, "rb") as handle:
            handle.seek(int(offsets["sectors"]))                              # type: ignore[index]
            table = struct.unpack(f"<{total + 1}I", handle.read(4 * (total + 1)))
            handle.seek(int(offsets["sector_blob"]))                          # type: ignore[index]
            blob = handle.read(table[-1])
        return [blob[table[i]:table[i + 1]].decode("utf-8", "replace") for i in range(total)]

    # --- names ----------------------------------------------------------------------------------------------------------
    def _name(self, handle, number: int) -> str:
        offsets = self.meta["offsets"]
        block, skip = divmod(number, NAME_BLOCK)
        handle.seek(int(offsets["name_index"]) + 4 * block)                   # type: ignore[index]
        start = _SECTOR_STRUCT.unpack(handle.read(4))[0]
        handle.seek(int(offsets["names"]) + start)                            # type: ignore[index]
        data = handle.read(NAME_BLOCK * 270)                                  # the longest entry is under 270 bytes
        width = int(self.meta["sector_width"])
        pos = 0
        for _ in range(skip):
            pos = _entry_end(data, pos, width)
        return _entry_name(data, pos, width, lambda sector: self._sector_name(handle, sector))[0]

    def _sector_name(self, handle, sector: int) -> str:
        offsets = self.meta["offsets"]
        handle.seek(int(offsets["sectors"]) + 4 * sector)                     # type: ignore[index]
        begin, end = struct.unpack("<II", handle.read(8))
        handle.seek(int(offsets["sector_blob"]) + begin)                      # type: ignore[index]
        return handle.read(end - begin).decode("utf-8", "replace")


def _entry_name(data: bytes, pos: int, width: int, sector_name) -> Tuple[str, int]:
    """The name in the entry that starts at `pos`, and where the entry ends. `sector_name(number)` gives a sector's text."""
    sector = int.from_bytes(data[pos:pos + width], "little")
    pos += width
    if sector == (1 << (8 * width)) - 1:                                      # a name kept as it is: length, then the text
        return data[pos + 1:pos + 1 + data[pos]].decode("utf-8", "replace"), pos + 1 + data[pos]
    packed = int.from_bytes(data[pos:pos + 3], "little")
    pos += 3
    code = packed >> 18
    n1 = code - 1                                                             # 0: there is no n1; 1 to 30: n1 is 0 to 29; 31: n1 follows
    if code == N1_FOLLOWS:
        n1, pos = get_varint(data, pos)
    n2, pos = get_varint(data, pos)
    return join_name(sector_name(sector), packed & 0x7FFF, (packed >> 15) & 7, n1, n2), pos


def _entry_end(data: bytes, pos: int, width: int) -> int:
    """Where the name entry that starts at `pos` ends."""
    sector = int.from_bytes(data[pos:pos + width], "little")
    pos += width
    if sector == (1 << (8 * width)) - 1:
        return pos + 1 + data[pos]
    packed = int.from_bytes(data[pos:pos + 3], "little")
    pos += 3
    if packed >> 18 == N1_FOLLOWS:
        pos = get_varint(data, pos)[1]
    return get_varint(data, pos)[1]


def _gap(value: float, cell: int) -> float:
    """The squared distance from `value` (ly) to the nearest edge of cell number `cell` (counted from the middle of the grid) along one axis; 0 inside the cell."""
    low = cell * CELL_LY
    high = low + CELL_LY
    if value < low:
        return (low - value) ** 2
    if value > high:
        return (value - high) ** 2
    return 0.0


# --- what the N.S. button uses ---------------------------------------------------------------------------------------------
def nearest_stars(x: float, y: float, z: float, count: int = 2, directory: Optional[str] = None) -> List[StarHit]:
    """The nearest neutron stars from the installed index. Raises IndexUnusable when there is none that can be used."""
    return StarIndex(index_path(directory)).nearest(x, y, z, count)
