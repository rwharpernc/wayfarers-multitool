"""WFMT's own diagnostic log: a separate file that records, while it is switched on, what WFMT did and why, to troubleshoot a problem alongside EDMC's log.

**Off by default.** The tick is in Settings → WFMT → Help (`CONFIG_ENABLED`). While it is off nothing is written, no file is made and `log` returns at once.

**Where.** `logs/WFMT/wfmt-diagnostics.log` in EDMC's data folder (the folder that holds EDMC's own `logs/`), rotated at 1 MB with three older files kept, so it can
never grow without bound. It is not part of EDMC's log, and not in the plugin folder, so an update never touches it.

**What goes in.**
- Everything WFMT logs through its normal logger, at every level, including the DEBUG lines EDMC's log leaves out. While the diagnostic log is on the plugin's logger
  is set to DEBUG; a guard on EDMC's own handlers drops the extra lines (those below the level EDMC already used), so EDMC's log reads the same as before.
- Lines written with `log(area, message, **fields)` at the places that matter for troubleshooting: the start, each journal event's name, a button pressed in a window,
  a window opened, a Spansh request (its endpoint, the answer and the time taken), a search or rescan and its result, and Settings being saved.

**What stays out.** The journal events' contents, request bodies, keys and the Raven and Discord secrets are not logged. Each line has the commander's name replaced by
`<commander>`, the home folder by `~` and any Discord webhook link by `<webhook>` (`issue_report.redact`), so the file can be pasted into a report.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import platform
import sys
import threading
import time
from typing import Any, Callable, Iterable, List, Optional

try:
    from config import appname, config
except ImportError:      # unit tests outside EDMC
    appname, config = "EDMarketConnector", None

from . import __version__, issue_report

CONFIG_ENABLED = "wfmt_diag_log_enabled"
FILE_NAME = "wfmt-diagnostics.log"
MAX_BYTES = 1_000_000
BACKUPS = 3
FIELD_CHARS = 200            # one field's value is clipped to this many characters

plugin_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
_plugin_logger = logging.getLogger(f"{appname}.{plugin_name}")
_diag_logger = logging.getLogger(f"{appname}.{plugin_name}.diagnostics")

_lock = threading.RLock()
_enabled = False
_handler: Optional[logging.Handler] = None
_guarded: List[logging.Handler] = []           # EDMC handlers the guard was added to
_prior_level = logging.NOTSET
_names: List[str] = []                         # commander names to hide
_started = time.monotonic()


class _Redacting(logging.Formatter):
    """The log's line format, with the commander's name, the home folder and webhook links taken out."""

    def __init__(self) -> None:
        super().__init__("%(asctime)s.%(msecs)03d | %(levelname)-7s | %(thread)d | %(message)s", "%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        return issue_report.redact(super().format(record), list(_names))


class _KeepOutOfEdmc(logging.Filter):
    """On EDMC's handlers: drops the plugin's records that are below the level EDMC's own log was already at, so switching the diagnostic log on does not add lines to it."""

    def __init__(self, floor: int) -> None:
        super().__init__()
        self.floor = floor

    def filter(self, record: logging.LogRecord) -> bool:
        return not (record.name.startswith(_plugin_logger.name) and record.levelno < self.floor)


_guard: Optional[_KeepOutOfEdmc] = None


def log_path() -> str:
    """Where the diagnostic log is written (the file may not exist yet)."""
    base = ""
    if config is not None:
        try:
            base = str(config.app_dir_path)
        except Exception:
            base = ""
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".wfmt")
    return os.path.join(base, "logs", "WFMT", FILE_NAME)


def enabled() -> bool:
    return _enabled


def saved_setting() -> bool:
    """The tick as saved (off when never set)."""
    try:
        return bool(config.get_bool(CONFIG_ENABLED, default=False)) if config is not None else False
    except Exception:
        return False


def note_commander(name: Any) -> None:
    """Remember a commander name so it is hidden in the log."""
    text = str(name or "").strip()
    if text and text not in _names:
        _names.append(text)


def configure() -> None:
    """Apply the saved tick (at start-up)."""
    set_enabled(saved_setting(), save=False)


def set_enabled(value: bool, save: bool = True, path: Optional[str] = None) -> bool:
    """Switch the diagnostic log on or off (and keep the choice). Returns whether it is on. A file that cannot be opened leaves it off, with the reason in EDMC's log."""
    global _enabled, _handler, _prior_level, _guard
    value = bool(value)
    with _lock:
        if save and config is not None:
            try:
                config.set(CONFIG_ENABLED, value)
            except Exception:
                _plugin_logger.debug("Could not save the diagnostic log setting", exc_info=True)
        if value == _enabled:
            return _enabled
        if value:
            target = path or log_path()
            try:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                handler = logging.handlers.RotatingFileHandler(target, maxBytes=MAX_BYTES, backupCount=BACKUPS, encoding="utf-8")
            except OSError:
                _plugin_logger.warning("The diagnostic log could not be opened at %s", target, exc_info=True)
                return False
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(_Redacting())
            floor = _plugin_logger.getEffectiveLevel()
            _guard = _KeepOutOfEdmc(floor)
            _guarded.clear()
            node = _plugin_logger.parent
            while node is not None:
                for existing in node.handlers:
                    existing.addFilter(_guard)
                    _guarded.append(existing)
                if not node.propagate:
                    break
                node = node.parent
            _prior_level = _plugin_logger.level
            _plugin_logger.setLevel(logging.DEBUG)
            _plugin_logger.addHandler(handler)
            _diag_logger.propagate = False
            _diag_logger.setLevel(logging.DEBUG)
            _diag_logger.addHandler(handler)
            _handler = handler
            _enabled = True
            _write_start()
        else:
            _write("INFO", "diag", "Diagnostic log switched off")
            _enabled = False
            handler, _handler = _handler, None
            for existing in _guarded:
                if _guard is not None:
                    existing.removeFilter(_guard)
            _guarded.clear()
            _guard = None
            _plugin_logger.setLevel(_prior_level)
            if handler is not None:
                _plugin_logger.removeHandler(handler)
                _diag_logger.removeHandler(handler)
                handler.close()
        return _enabled


def _write_start() -> None:
    home = os.path.expanduser("~")
    _write("INFO", "diag", "Diagnostic log switched on",
           wfmt=__version__, python=sys.version.split()[0], system=f"{platform.system()} {platform.release()}", machine=platform.machine(),
           pid=os.getpid(), plugin_dir=os.path.dirname(os.path.abspath(__file__)).replace(home, "~"), log=log_path().replace(home, "~"))


def _text(value: Any) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text if len(text) <= FIELD_CHARS else text[:FIELD_CHARS - 1] + "…"


def _write(level: str, area: str, message: str, **fields: Any) -> None:
    extra = "".join(f" {key}={_text(value)}" for key, value in sorted(fields.items()))
    _diag_logger.log(getattr(logging, level, logging.INFO), "%-9s %s%s", area, message, extra)


def log(area: str, message: str, level: str = "DEBUG", **fields: Any) -> None:
    """One line in the diagnostic log (nothing at all while it is off, and never an error): `area` names the part of WFMT (journal, ui, window, spansh, search, ...),
    `fields` are `key=value` pairs, each clipped to a short length."""
    if not _enabled:
        return
    try:
        _write(level, area, message, **fields)
    except Exception:
        pass


def timed(area: str, message: str, **fields: Any) -> Callable[..., None]:
    """Starts a timer; call the returned function with the outcome fields to log `message` with `ms=<elapsed>` (does nothing while the log is off)."""
    began = time.monotonic()

    def done(**more: Any) -> None:
        if _enabled:
            log(area, message, ms=int((time.monotonic() - began) * 1000), **{**fields, **more})

    return done


def recent(limit: int = 200) -> List[str]:
    """The newest lines of the current diagnostic file (empty when there is none)."""
    try:
        with open(log_path(), encoding="utf-8", errors="replace") as handle:
            return handle.read().splitlines()[-limit:]
    except OSError:
        return []


def uptime_s() -> int:
    return int(time.monotonic() - _started)
