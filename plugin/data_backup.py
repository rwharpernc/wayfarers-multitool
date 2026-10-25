"""
Back up my data: one zip of everything WFMT has saved about play, written to a folder the user picks.

WFMT keeps its saved data as JSON files beside the plugin (the list is `update._OWN_DATA_FILES`) plus the optional
`mining_sessions` archive. The updater never touches them but its own pre-update backups leave them out on purpose, so
until now nothing archived them. This module copies them into a timestamped zip so they can be kept, moved to another
machine or read by other tools.

Restoring is staged, not immediate: WFMT keeps its data in memory while EDMC runs and would write it back over a restored
file, so `stage_restore` unpacks a checked backup into `restore_pending/` and `apply_pending_restore` (called first thing at
start-up, before any feature reads a file) moves it into place, keeping the files it replaces in
`backups/pre-restore-<date>.zip`. Automatic backups (`run_auto_backup`) go to a folder chosen in Settings and are named
`WFMT-data-auto-...`, so only they are pruned (`AUTO_KEEP`); a manual backup is never deleted.

Left out on purpose (`LEFT_OUT`): `rcc_keys.json`, because it holds each commander's Raven Colonial key and an archive is
meant to be copied around and kept in cloud folders, and `codex_catalog.json`, a cache WFMT downloads again by itself.
The `star_index` folder (`LEFT_OUT_DIRS`) is left out too: it holds the optional local star index, about 110 MB built from a public download, which Settings can make again.
The zip also holds `backup-info.json` (WFMT version, when it was made, the files and their sizes; no commander name).
Nothing here touches EDMC's own settings, which are not files in the plugin folder.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable, List, Optional, Set
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

logger = logging.getLogger(__name__)

INFO_NAME = "backup-info.json"
ZIP_PREFIX = "WFMT-data-"
AUTO_PREFIX = "WFMT-data-auto-"
AUTO_KEEP = 10                          # automatic backups kept in the folder; older ones are deleted, manual ones never
PENDING_DIRNAME = "restore_pending"     # a checked backup waiting for the next start (listed in update._OWN_DIRS)
PENDING_MARKER = "ready.json"           # written last, so a half-unpacked folder is never applied
SAFETY_PREFIX = "pre-restore-"          # the files a restore replaced, zipped into the plugin's backups folder
SAFETY_KEEP = 5
BACKUPS_DIRNAME = "backups"
MAX_RESTORE_BYTES = 1024 * 1024 * 1024  # a backup claiming more than this unpacked is refused
CFG_FOLDER = "wfmt_backup_folder"       # where the last manual backup went, offered first next time
CFG_AUTO = "wfmt_auto_backup"
CFG_AUTO_FOLDER = "wfmt_auto_backup_folder"
CFG_AUTO_DAYS = "wfmt_auto_backup_days"
DEFAULT_AUTO_DAYS = 7
LEFT_OUT = {
    "rcc_keys.json": "holds Raven Colonial keys",
    "codex_catalog.json": "a cache WFMT downloads again",
}
LEFT_OUT_DIRS = {
    "star_index": "the optional local star index, built from a public download and rebuilt from it (star_index.py)",
}
EXTRA_DIRS = ("mining_sessions",)      # the optional per-run mining archive (mining_session_archive.py)


@dataclass
class BackupResult:
    """What a backup did. `error` is set (and `path` is None) when no archive was made."""
    path: Optional[str] = None
    files: List[str] = field(default_factory=list)
    bytes_in: int = 0
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.path is not None and not self.error

    def summary(self) -> str:
        if not self.ok:
            return f"Backup failed: {self.error}"
        return f"Saved {len(self.files)} files ({_size_text(self.bytes_in)}) to {self.path}"


def _size_text(count: int) -> str:
    if count >= 1024 * 1024:
        return f"{count / (1024 * 1024):.1f} MB"
    return f"{max(1, round(count / 1024))} KB" if count else "0 KB"


def data_file_names() -> Set[str]:
    """The data files the updater protects, which is the list a backup draws from."""
    from . import legacy_names, update      # imported when needed: update pulls in the network stack, which a backup test does not want
    return set(update._OWN_DATA_FILES) | set(legacy_names.legacy_file_names())      # old names too: an old backup still restores


def collect(plugin_dir: str, names: Optional[Iterable[str]] = None) -> List[str]:
    """Archive names (forward slashes) of the files that exist and are worth backing up, sorted."""
    wanted = set(data_file_names() if names is None else names) - set(LEFT_OUT)
    found = [name for name in wanted if os.path.isfile(os.path.join(plugin_dir, name))]
    for folder in EXTRA_DIRS:
        root = os.path.join(plugin_dir, folder)
        for base, _dirs, files in os.walk(root):
            for name in files:
                found.append(os.path.relpath(os.path.join(base, name), plugin_dir).replace(os.sep, "/"))
    return sorted(name for name in found if name.split("/")[0] not in LEFT_OUT_DIRS)


def _is_inside(path: str, folder: str) -> bool:
    try:
        return os.path.commonpath([os.path.realpath(path), os.path.realpath(folder)]) == os.path.realpath(folder)
    except ValueError:      # different drives on Windows
        return False


def _info_files(sizes: dict) -> list:
    """The file list for backup-info.json. The mining run archive's file names carry a commander name (mining_session_archive.py),
    so that folder is listed once with a count instead of file by file."""
    listed, folders = [], {}
    for name, size in sizes.items():
        folder = name.split("/")[0] if "/" in name else ""
        if folder in EXTRA_DIRS:
            count, total = folders.get(folder, (0, 0))
            folders[folder] = (count + 1, total + size)
        else:
            listed.append({"name": name, "bytes": size})
    listed += [{"name": f"{folder}/", "files": count, "bytes": total} for folder, (count, total) in sorted(folders.items())]
    return listed


def archive_name(now: datetime, prefix: str = ZIP_PREFIX) -> str:
    return f"{prefix}{now.strftime('%Y%m%d-%H%M%S')}.zip"


def create_backup(plugin_dir: str, dest_dir: str, version: str, now: Optional[datetime] = None,
                  names: Optional[Iterable[str]] = None, prefix: str = ZIP_PREFIX) -> BackupResult:
    """Zip the data files into `dest_dir` and say what happened. Never raises for a file problem; the reason is in `error`.
    The zip is written under a temporary name and renamed when complete, so a failure never leaves a half archive."""
    if not dest_dir or not os.path.isdir(dest_dir):
        return BackupResult(error="that folder does not exist")
    if _is_inside(dest_dir, plugin_dir):
        return BackupResult(error="choose a folder outside the WFMT plugin folder, which an update or a reinstall can clear")
    stamp = now or datetime.now()
    final = os.path.join(dest_dir, archive_name(stamp, prefix))
    if os.path.exists(final):
        return BackupResult(error=f"{os.path.basename(final)} already exists there; try again in a moment")
    members = collect(plugin_dir, names)
    if not members:
        return BackupResult(error="WFMT has no saved data to back up yet")

    result = BackupResult()
    handle_fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=dest_dir)
    os.close(handle_fd)
    try:
        sizes = {}
        with ZipFile(temp_path, "w", ZIP_DEFLATED) as archive:
            for member in members:
                source = os.path.join(plugin_dir, *member.split("/"))
                try:
                    archive.write(source, member)
                except OSError as error:        # a file vanished or is locked: keep the rest, say so in the log
                    logger.warning("Backup skipped %s: %s", member, error)
                    continue
                sizes[member] = os.path.getsize(source)
            info = {
                "wfmt_version": version,
                "created_utc": stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),     # a naive time is local time
                "platform": sys.platform,
                "files": _info_files(sizes),
                "left_out": dict(sorted(LEFT_OUT.items())),
            }
            archive.writestr(INFO_NAME, json.dumps(info, indent=2) + "\n")
        if not sizes:
            raise OSError("none of the data files could be read")
        os.replace(temp_path, final)
    except OSError as error:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        logger.warning("Backup to %s failed: %s", dest_dir, error)
        return BackupResult(error=str(error) or error.__class__.__name__)
    result.path, result.files, result.bytes_in = final, sorted(sizes), sum(sizes.values())
    return result


def run_dialog(plugin_dir: str, version: str, ask_folder: Callable[..., str], initial: str = "",
               names: Optional[Iterable[str]] = None) -> BackupResult:
    """Ask for a folder, then back up into it. `ask_folder` is `tkinter.filedialog.askdirectory` (a stand-in in tests).
    Cancelling the dialog gives a result with no path and no error."""
    chosen = ask_folder(title="Choose where to save the WFMT data backup", initialdir=initial or os.path.expanduser("~"))
    if not chosen:
        return BackupResult()
    return create_backup(plugin_dir, chosen, version, names=names)


# ---- restoring -----------------------------------------------------------------------------------------------------------

@dataclass
class BackupInfo:
    """What a backup zip holds, read without unpacking it. `error` is set when it is not a usable WFMT data backup."""
    error: str = ""
    version: str = ""
    created: str = ""
    platform: str = ""
    files: List[str] = field(default_factory=list)
    bytes: int = 0

    @property
    def ok(self) -> bool:
        return not self.error

    def describe(self) -> str:
        if not self.ok:
            return self.error
        return (f"WFMT {self.version or '?'}, made {self.created or 'at an unknown time'}: {len(self.files)} files "
                f"({_size_text(self.bytes)} unpacked)")


def _safe_member(name: str, allowed: Set[str]) -> bool:
    """A name a backup may hold: one of the data files, or a file inside the mining archive; never a path that leaves the folder."""
    if not name or name.startswith("/") or "\\" in name or ":" in name:
        return False
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return False
    return name in allowed if len(parts) == 1 else parts[0] in EXTRA_DIRS


def inspect_backup(zip_path: str, names: Optional[Iterable[str]] = None) -> BackupInfo:
    """Check a zip is a WFMT data backup and say what it holds. A file in it that is not a data file, or a name that could write
    outside the plugin folder, makes the whole backup refused: a restore never applies part of an unfamiliar archive."""
    allowed = set(data_file_names() if names is None else names) - set(LEFT_OUT)
    try:
        with ZipFile(zip_path) as archive:
            if INFO_NAME not in archive.namelist():
                return BackupInfo(error=f"that zip has no {INFO_NAME}, so it is not a WFMT data backup")
            try:
                meta = json.loads(archive.read(INFO_NAME).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return BackupInfo(error=f"{INFO_NAME} in that zip cannot be read")
            if not isinstance(meta, dict):
                return BackupInfo(error=f"{INFO_NAME} in that zip cannot be read")
            members = [item for item in archive.infolist() if item.filename != INFO_NAME and not item.is_dir()]
            for item in members:
                if not _safe_member(item.filename, allowed):
                    return BackupInfo(error=f"that zip holds a file WFMT does not back up ({item.filename}), so it was not used")
            total = sum(item.file_size for item in members)
            if total > MAX_RESTORE_BYTES:
                return BackupInfo(error="that zip unpacks to far more data than a WFMT backup holds, so it was not used")
            if not members:
                return BackupInfo(error="that backup holds no data files")
            return BackupInfo(version=str(meta.get("wfmt_version", "")), created=str(meta.get("created_utc", "")),
                              platform=str(meta.get("platform", "")), files=sorted(item.filename for item in members), bytes=total)
    except (BadZipFile, OSError) as error:
        return BackupInfo(error=f"that file cannot be read as a zip ({error.__class__.__name__})")


def stage_restore(zip_path: str, plugin_dir: str, names: Optional[Iterable[str]] = None) -> BackupResult:
    """Unpack a checked backup into `restore_pending/` for the next start. Nothing live is touched."""
    info = inspect_backup(zip_path, names)
    if not info.ok:
        return BackupResult(error=info.error)
    pending = os.path.join(plugin_dir, PENDING_DIRNAME)
    shutil.rmtree(pending, ignore_errors=True)
    try:
        os.makedirs(pending)
        with ZipFile(zip_path) as archive:
            for name in info.files:
                target = os.path.join(pending, *name.split("/"))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with archive.open(name) as source, open(target, "wb") as destination:
                    shutil.copyfileobj(source, destination)
        with open(os.path.join(pending, PENDING_MARKER), "w", encoding="utf-8") as handle:
            json.dump({"wfmt_version": info.version, "created_utc": info.created, "files": info.files}, handle)
    except OSError as error:
        shutil.rmtree(pending, ignore_errors=True)
        logger.warning("Could not stage the restore: %s", error)
        return BackupResult(error=str(error) or error.__class__.__name__)
    return BackupResult(path=pending, files=info.files, bytes_in=info.bytes)


def pending_restore(plugin_dir: str) -> Optional[BackupInfo]:
    """The restore waiting for the next start, or None."""
    marker = os.path.join(plugin_dir, PENDING_DIRNAME, PENDING_MARKER)
    try:
        with open(marker, encoding="utf-8") as handle:
            meta = json.load(handle)
        return BackupInfo(version=str(meta.get("wfmt_version", "")), created=str(meta.get("created_utc", "")),
                          files=[str(name) for name in meta.get("files", [])])
    except (OSError, ValueError, AttributeError, TypeError):
        return None


def cancel_pending(plugin_dir: str) -> None:
    shutil.rmtree(os.path.join(plugin_dir, PENDING_DIRNAME), ignore_errors=True)


def apply_pending_restore(plugin_dir: str, now: Optional[datetime] = None, names: Optional[Iterable[str]] = None) -> str:
    """Move a staged restore into place. Call it before anything reads a data file. Returns a line for the log ('' when nothing
    was waiting). The files being replaced are zipped into backups/pre-restore-<date>.zip first, so a restore can be undone."""
    pending = os.path.join(plugin_dir, PENDING_DIRNAME)
    if not os.path.isdir(pending):
        return ""
    info = pending_restore(plugin_dir)
    if info is None:        # staging never finished: drop it
        cancel_pending(plugin_dir)
        return "Discarded an unfinished restore"
    allowed = set(data_file_names() if names is None else names) - set(LEFT_OUT)
    files = [name for name in info.files if _safe_member(name, allowed) and os.path.isfile(os.path.join(pending, *name.split("/")))]
    stamp = now or datetime.now()
    try:
        safety_dir = os.path.join(plugin_dir, BACKUPS_DIRNAME)
        os.makedirs(safety_dir, exist_ok=True)
        with ZipFile(os.path.join(safety_dir, archive_name(stamp, SAFETY_PREFIX)), "w", ZIP_DEFLATED) as archive:
            for name in files:
                live = os.path.join(plugin_dir, *name.split("/"))
                if os.path.isfile(live):
                    archive.write(live, name)
        for name in files:
            destination = os.path.join(plugin_dir, *name.split("/"))
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            os.replace(os.path.join(pending, *name.split("/")), destination)
        _prune(safety_dir, re.compile(r"^" + re.escape(SAFETY_PREFIX) + r"\d{8}-\d{6}\.zip$"), SAFETY_KEEP)
    except OSError as error:
        logger.warning("Restore failed part way: %s", error, exc_info=True)
        cancel_pending(plugin_dir)
        return f"Restore failed ({error}); the files it replaced so far are in {BACKUPS_DIRNAME}"
    cancel_pending(plugin_dir)
    return f"Restored {len(files)} files from the backup of {info.created or 'an unknown date'}; the files they replaced are in {BACKUPS_DIRNAME}"


# ---- automatic backups ---------------------------------------------------------------------------------------------------

_AUTO_NAME = re.compile(r"^" + re.escape(AUTO_PREFIX) + r"(\d{8}-\d{6})\.zip$")


def _prune(folder: str, pattern: "re.Pattern[str]", keep: int) -> None:
    """Delete all but the newest `keep` files in `folder` whose names match `pattern` (the names sort by their timestamp)."""
    try:
        matching = sorted(name for name in os.listdir(folder) if pattern.match(name))
    except OSError:
        return
    for name in matching[:-keep] if keep > 0 else matching:
        try:
            os.remove(os.path.join(folder, name))
        except OSError:
            logger.warning("Could not delete the old backup %s", name)


def newest_auto_backup(folder: str) -> Optional[datetime]:
    """When the newest automatic backup in `folder` was made (from its name), or None."""
    try:
        stamps = [match.group(1) for match in (_AUTO_NAME.match(name) for name in os.listdir(folder)) if match]
    except OSError:
        return None
    return datetime.strptime(max(stamps), "%Y%m%d-%H%M%S") if stamps else None


def run_auto_backup(plugin_dir: str, folder: str, version: str, days: int, force: bool = False,
                    now: Optional[datetime] = None, names: Optional[Iterable[str]] = None) -> Optional[BackupResult]:
    """Back up into `folder` if the newest automatic backup there is `days` old or older (or `force`). None when it was not due."""
    when = now or datetime.now()
    if not folder:
        return None
    newest = newest_auto_backup(folder)
    if not force and newest is not None and when - newest < timedelta(days=days):
        return None
    result = create_backup(plugin_dir, folder, version, when, names, prefix=AUTO_PREFIX)
    if result.ok:
        _prune(folder, _AUTO_NAME, AUTO_KEEP)
    return result


@dataclass
class AutoSettings:
    enabled: bool = False
    folder: str = ""
    days: int = DEFAULT_AUTO_DAYS


def auto_settings(config: Any) -> AutoSettings:
    """The automatic-backup choices from EDMC's config (passed in so this module never imports it)."""
    days = config.get_int(CFG_AUTO_DAYS, default=DEFAULT_AUTO_DAYS)
    return AutoSettings(bool(config.get_bool(CFG_AUTO, default=False)), config.get_str(CFG_AUTO_FOLDER) or "",
                        min(90, max(1, days or DEFAULT_AUTO_DAYS)))


def run_configured_backup(plugin_dir: str, config: Any, version: str, force: bool = False) -> Optional[BackupResult]:
    """The automatic backup if it is switched on and a folder is chosen; logs what happened. `force` skips the 'due' check (used just
    before an update installs)."""
    settings = auto_settings(config)
    if not settings.enabled or not settings.folder:
        return None
    result = run_auto_backup(plugin_dir, settings.folder, version, settings.days, force=force)
    if result is not None:
        logger.info("Automatic backup: %s", result.summary())
    return result
