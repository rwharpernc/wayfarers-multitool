"""Downloads the Spansh data dump that the local star index is built from (`star_index_build.py`). It runs only when the user presses a button in Settings; WFMT never starts it.

What is fetched: one public file, `systems_neutron.json.gz` from Spansh's download server (https://downloads.spansh.co.uk/), about 173 MiB (181,788,319 bytes when this was written). It is
one plain GET carrying only WFMT's User-Agent; nothing about the player is sent. The file is read once, turned into the index, and deleted.

How it is kept light, on top of what the courtesy layer does (`spansh_courtesy.stream_to_file`: the gate, the cap on requests in flight, the retries and the stop after repeated failures):

- **One download at a time**, across the whole plugin.
- **Conditional.** An update sends the ETag and date of the file the installed index was built from, so a file that has not changed is answered "not modified" and nothing is downloaded.
- **Resumable.** The file is written as `systems_neutron.json.gz.part` beside a small record of the file's ETag and date. After a cancel or a dropped connection the next press continues from
  the bytes already held (a Range request, with If-Range so a file that changed in between is fetched again from the start). A server that ignores Range simply sends the whole file again.
- **Checked first.** Before any of the file is written there must be room for it and for building the index (`BUILD_SPACE_BYTES`), and the file must not be larger than `MAX_DOWNLOAD_BYTES`.
  The size actually received is compared with what the server announced, and the finished file is moved into place in one step.
"""
from __future__ import annotations

import errno
import json
import os
import shutil
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Callable, Optional, Tuple

from . import http_identity, spansh_courtesy

DUMP_URL = "https://downloads.spansh.co.uk/systems_neutron.json.gz"
DUMP_PAGE_URL = "https://spansh.co.uk/dumps"
DUMP_NAME = "systems_neutron.json.gz"
DAY_URL = "https://downloads.spansh.co.uk/systems_1day.json.gz"      # the systems changed since midnight (UTC) yesterday, every main star: about 3 MB
WEEK_URL = "https://downloads.spansh.co.uk/systems_1week.json.gz"    # ... since midnight 7 days ago: about 19 MB
MAX_TOPUPS = 20                                 # after this many top-ups, or MAX_LINEAGE_DAYS, the next update downloads the full dump again
MAX_LINEAGE_DAYS = 60
PART_SUFFIX = ".part"
INFO_SUFFIX = ".part.json"
EXPECTED_BYTES = 181_788_319                    # the size when this was written (173 MiB); only used when the server does not say
MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024          # a little over the expected size; anything larger is refused rather than filling the disk
BUILD_SPACE_BYTES = 300 * 1024 * 1024           # what building needs besides the download: the temporary files and the new index (about 110 MB each), with a margin
REQUEST_TIMEOUT_S = 60
_USER_AGENT = http_identity.user_agent("star-index")

_busy = threading.Lock()


class DownloadError(Exception):
    """The download did not complete; the message is for the user."""


class NotEnoughSpace(DownloadError):
    """There is not enough free disk space."""


@dataclass
class DownloadResult:
    path: str = ""                  # the finished dump (empty when not_modified)
    not_modified: bool = False
    etag: str = ""
    last_modified: str = ""
    size: int = 0
    resumed: bool = False           # part of the file was already held and the server continued it


def parse_time(text: str) -> Optional[datetime]:
    """A UTC time from an ISO time ("2026-10-21T06:26:22Z") or an HTTP date ("Wed, 21 Oct 2026 06:26:22 GMT"), or None."""
    text = (text or "").strip()
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    try:
        value = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def iso_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def choose_update(current_to: str, topups: int, full_modified: str, now: datetime) -> Optional[Tuple[str, str]]:
    """The smallest update file that is certain to cover everything since the index was current: (url, short name), or None when the full dump is needed.

    Spansh's update files list the systems changed since midnight (UTC) 1 or 7 days before the file was made, and a file is never made later than now, so a file that starts at midnight
    `now` minus 1 (or 7) days reaches back at least that far. The builder checks the file's own oldest change as well, so a change in Spansh's scheme is caught there."""
    current = parse_time(current_to)
    started = parse_time(full_modified)
    if current is None or started is None or topups >= MAX_TOPUPS or now - started > timedelta(days=MAX_LINEAGE_DAYS):
        return None
    midnight = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    if current >= midnight - timedelta(days=1):
        return DAY_URL, "1-day"
    if current >= midnight - timedelta(days=7):
        return WEEK_URL, "1-week"
    return None


def free_bytes(directory: str) -> int:
    """Free space on the disk that holds `directory` (or the nearest folder above it that exists)."""
    probe = os.path.abspath(directory)
    while not os.path.isdir(probe):
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    return shutil.disk_usage(probe).free


def megabytes(count: int) -> str:
    return f"{count / (1024 * 1024):,.1f} MB"


def local_problem(err: OSError, directory: str) -> str:
    """A message for a failure to write in `directory`: a full disk, or a folder WFMT cannot write to (a read-only install, such as a Flatpak's, or a protected folder)."""
    if err.errno == errno.ENOSPC:
        return "The disk is full."
    if isinstance(err, PermissionError) or err.errno in (errno.EACCES, errno.EROFS, errno.EPERM):
        return (f"WFMT cannot write to {directory}. The local star index is saved in the plugin folder, so that folder must be writable "
                "(with a Flatpak or another sandboxed EDMC, allow it write access to the plugin folder).")
    return f"WFMT could not write in {directory} ({err})."


def _read_info(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            value = json.load(handle)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def download(directory: str, known_etag: str = "", known_modified: str = "", cancel: Optional[threading.Event] = None,
             progress: Optional[Callable[[int, int], None]] = None, courtesy: Optional[spansh_courtesy.Courtesy] = None,
             free_space: Callable[[str], int] = free_bytes, url: str = DUMP_URL) -> DownloadResult:
    """Fetches the dump into `directory`. `known_etag` and `known_modified` describe the file the installed index was built from; when given, the request is conditional and an unchanged file
    returns a result with `not_modified` set. Raises DownloadError (NotEnoughSpace among its kinds) with a message for the user, and spansh_courtesy.Cancelled when `cancel` is set (the partial
    file is kept so the next press continues it)."""
    if not _busy.acquire(blocking=False):
        raise DownloadError("A download is already running.")
    try:
        return _download(directory, known_etag, known_modified, cancel, progress, courtesy or spansh_courtesy.default, free_space, url)
    finally:
        _busy.release()


def _download(directory: str, known_etag: str, known_modified: str, cancel: Optional[threading.Event],
              progress: Optional[Callable[[int, int], None]], courtesy: spansh_courtesy.Courtesy, free_space: Callable[[str], int], url: str) -> DownloadResult:
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as err:
        raise DownloadError(local_problem(err, directory)) from None
    final = os.path.join(directory, DUMP_NAME)
    part = final + PART_SUFFIX
    info_path = final + INFO_SUFFIX
    held = 0
    info = _read_info(info_path)
    if os.path.isfile(part) and info.get("url") == url and (info.get("etag") or info.get("last_modified")):
        held = os.path.getsize(part)
    else:
        for stale in (part, info_path):
            _remove(stale)
    if held > 0 and info.get("total") and held == info.get("total"):         # everything arrived before the last stop: only the rename is left
        os.replace(part, final)
        _remove(info_path)
        return DownloadResult(path=final, etag=str(info.get("etag") or ""), last_modified=str(info.get("last_modified") or ""), size=held, resumed=True)
    for attempt in range(2):
        headers = {"User-Agent": _USER_AGENT, "Accept-Encoding": "identity"}
        if held > 0:
            headers["If-Range"] = str(info.get("etag") or info.get("last_modified"))
        else:
            if known_etag:
                headers["If-None-Match"] = known_etag
            if known_modified:
                headers["If-Modified-Since"] = known_modified
        request = urllib.request.Request(url, headers=headers, method="GET")

        def check(answer: spansh_courtesy.StreamResult) -> None:
            if answer.status not in (200, 206):
                raise DownloadError(f"The download server answered {answer.status}, not the file.")
            total = answer.total or EXPECTED_BYTES
            need = max(0, total - answer.size) + BUILD_SPACE_BYTES
            available = free_space(directory)
            if available < need:
                raise NotEnoughSpace(f"Not enough free disk space: the download and the index need about {megabytes(need)} and {megabytes(available)} is free.")
            with open(info_path, "w", encoding="utf-8") as handle:
                json.dump({"url": url, "etag": answer.etag, "last_modified": answer.last_modified, "total": answer.total}, handle)

        try:
            answer = courtesy.stream_to_file(request, REQUEST_TIMEOUT_S, part, cancel=cancel, progress=progress, resume_from=held,
                                             max_bytes=MAX_DOWNLOAD_BYTES, on_response=check)
        except spansh_courtesy.TooLarge:
            _remove(part)
            _remove(info_path)
            raise DownloadError(f"The file is larger than the {megabytes(MAX_DOWNLOAD_BYTES)} WFMT accepts, so it was not kept. "
                                "The dump may have grown past what this version expects; check for an update.") from None
        except urllib.error.HTTPError as err:
            if err.code == 416 and held > 0 and attempt == 0:           # the part is not a prefix of what the server has: start again
                _remove(part)
                _remove(info_path)
                held = 0
                continue
            raise DownloadError(f"The download server answered {err.code} {err.reason}.") from None
        except (spansh_courtesy.SpanshBusy, spansh_courtesy.Cancelled, DownloadError):
            raise
        except OSError as err:
            if isinstance(err, urllib.error.URLError) or isinstance(err, TimeoutError) or isinstance(err, ConnectionError):
                reason = getattr(err, "reason", err)
                raise DownloadError(f"Could not download the file ({reason}). Pressing the button again continues from what was received.") from None
            raise DownloadError(local_problem(err, directory)) from None
        if answer.not_modified:
            return DownloadResult(not_modified=True, etag=known_etag, last_modified=known_modified)
        expected = answer.total
        if expected and answer.size != expected:
            raise DownloadError(f"The download stopped at {megabytes(answer.size)} of {megabytes(expected)}. Pressing the button again continues it.")
        try:
            os.replace(part, final)
        except OSError as err:
            raise DownloadError(local_problem(err, directory)) from None
        _remove(info_path)
        return DownloadResult(path=final, etag=answer.etag, last_modified=answer.last_modified, size=answer.size, resumed=held > 0 and not answer.restarted)
    raise DownloadError("The download could not be resumed.")       # pragma: no cover


def _remove(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def discard(directory: str) -> None:
    """Removes the dump and any partial download from `directory`."""
    final = os.path.join(directory, DUMP_NAME)
    for path in (final, final + PART_SUFFIX, final + INFO_SUFFIX):
        _remove(path)
