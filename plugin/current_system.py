"""The system the commander is in now, for features that must know it on demand (the Missions window's "From where I am", Source commodities).

A feature that follows journal events live only knows the system once it has seen a jump, a login or a carrier jump *since EDMC started*. If EDMC was started
after the game, or the plugin was reloaded, that is nothing until the next jump. So this asks in turn: what the caller has tracked, EDMC's own state (which EDMC
rebuilds from the whole journal at start-up), and the newest journal itself. Nothing is stored or sent."""
from __future__ import annotations

import logging
from typing import Optional

from . import journal_files

logger = logging.getLogger(__name__)

NEWEST_FILES = 3
NEWEST_FILES_FOR_COMMANDER = 40
_PLACE = journal_files.event_pattern("FSDJump", "Location", "CarrierJump")
_PLACE_AND_COMMANDER = journal_files.event_pattern("FSDJump", "Location", "CarrierJump", "Commander", "LoadGame")


def from_monitor() -> str:
    """EDMC's idea of the current system, or "" (not running under EDMC, or it does not know yet)."""
    try:
        from monitor import monitor  # EDMC's own module; absent in unit tests
        state = getattr(monitor, "state", None) or {}
        return str(state.get("SystemName") or "").strip()
    except Exception:
        return ""


def last_place(folder: Optional[str] = None, cmdr: str = "") -> dict:
    """The last jump, login location or carrier jump event (it carries `StarSystem`, `StarPos`, and the system's allegiance and government), or {}.
    With `cmdr`, only journals of that commander count (a journal names its commander in its `Commander` or `LoadGame` event), looking back through
    `NEWEST_FILES_FOR_COMMANDER` files; without it, the newest journal that has a location."""
    try:
        files = journal_files.files_modified_since(0.0, folder)
        for path in reversed(files[-(NEWEST_FILES_FOR_COMMANDER if cmdr else NEWEST_FILES):]):
            last: dict = {}
            playing = ""
            for entry in journal_files.read_events(path, _PLACE_AND_COMMANDER):
                kind = entry.get("event")
                if kind == "Commander":
                    playing = str(entry.get("Name") or "")
                elif kind == "LoadGame":
                    playing = str(entry.get("Commander") or playing)
                elif str(entry.get("StarSystem") or "").strip():
                    last = entry
            if cmdr and playing.casefold() != cmdr.casefold():
                continue
            if last:
                return last
    except Exception:
        logger.debug("Could not read the current system from the journals", exc_info=True)
    return {}


def edmc_commander() -> str:
    """The commander EDMC is following, or "" (not running under EDMC, or it does not know one yet)."""
    try:
        from monitor import monitor  # EDMC's own module; absent in unit tests
        cmdr = getattr(monitor, "cmdr", "")
        return cmdr.strip() if isinstance(cmdr, str) else ""
    except Exception:
        return ""


def from_journal(folder: Optional[str] = None, cmdr: Optional[str] = None) -> str:
    """The star system of the last jump, login location or carrier jump in the journals, or "". It is the commander's own last place (EDMC's commander
    unless `cmdr` says otherwise), so another commander's journals never answer for them; with no commander known, the newest journal that has one."""
    who = edmc_commander() if cmdr is None else cmdr
    return str(last_place(folder, cmdr=who).get("StarSystem") or "").strip()


def find(tracked: str = "") -> str:
    """The current system: `tracked` if the caller has one, else EDMC's, else the journal's, else ""."""
    return (tracked or "").strip() or from_monitor() or from_journal()
