"""
Knowing who is playing when EDMC starts without the game running.

EDMC tells plugins the commander only through journal events. When it starts with the game already running it sends a
synthetic `StartUp` event, and every feature picks the commander up from that. When it starts first (the game is not
running yet, or was closed), nothing arrives until the next login, and every per-commander feature sits waiting.

So a short time after start-up, if no live event has arrived, `load.py` calls `dispatch`: it names the commander from the
newest journal (`latest_commander`) and sends every feature one neutral event, `RESTORE_EVENT`. It is deliberately **not**
`StartUp` or `LoadGame`: those say a game is running (Game Mode would read a dead game's journal, Powerplay would try to
recover a pledge, a credits session would start). Features treat the new event as any other unknown event, so the only
effect is the one they all share, learning `cmdr` and loading that commander's saved data. A real `LoadGame` or
`StartUp` later, for the same or another commander, then behaves exactly as before.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from . import journal_files

try:
    from config import appname
except ImportError:  # unit tests outside EDMC
    appname = "EDMarketConnector"

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

RESTORE_EVENT = "WFMTRestoreCommander"
NEWEST_FILES = 3   # the newest journal may be empty (the game just started), so look back a few
_LOGIN_EVENTS = journal_files.event_pattern("Commander", "LoadGame")


def _edmc_commander() -> str:
    try:
        from monitor import monitor  # EDMC's own module; absent in unit tests
        return str(getattr(monitor, "cmdr", "") or "")
    except ImportError:
        return ""


def latest_commander(folder: Optional[str] = None) -> str:
    """The commander EDMC itself is following (it rebuilds that from the journal it reads at start-up), else the one named in the newest journal file
    (its last `LoadGame` / `Commander`), else "". EDMC comes first because the newest file by date can belong to another commander than the one EDMC follows.
    A missing folder or unreadable file gives ""."""
    mine = _edmc_commander()
    if mine:
        return mine
    try:
        files = journal_files.files_modified_since(0.0, folder)
        for path in reversed(files[-NEWEST_FILES:]):
            found = ""
            for entry in journal_files.read_events(path, _LOGIN_EVENTS):
                name = entry.get("Name") if entry.get("event") == "Commander" else entry.get("Commander")
                if name:
                    found = str(name)
            if found:
                return found
    except Exception:
        logger.debug("Could not read the commander from the journals", exc_info=True)
    return ""


def restore_entry() -> Dict[str, Any]:
    return {"event": RESTORE_EVENT, "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def place_for(cmdr: str, folder: Optional[str] = None) -> Dict[str, Any]:
    """The commander's last known place from their own journals (the newest jump, login location or carrier jump), or {}."""
    from . import current_system
    return current_system.last_place(folder, cmdr=cmdr) if cmdr else {}


def place_state(place: Dict[str, Any]) -> Dict[str, Any]:
    """The part of EDMC's own `state` that says where the commander is, in EDMC's key names, for the features that read it."""
    state: Dict[str, Any] = {}
    if place.get("StarSystem"):
        state["SystemName"] = place["StarSystem"]
    if place.get("StarPos"):
        state["StarPos"] = place["StarPos"]
    if place.get("SystemAddress"):
        state["SystemAddress"] = place["SystemAddress"]
    return state


def dispatch(features: Iterable[Any], cmdr: str, place: Optional[Dict[str, Any]] = None) -> int:
    """Send `cmdr`'s restore event to every feature's `handle_event`. One feature failing never stops the others.
    `place` is the commander's last known place; it is passed the way EDMC passes the current system on every event (the `system` argument and the
    `state` dict), so each feature learns where the commander last was without being told about an arrival. Returns how many handled it without error."""
    ok = 0
    entry = restore_entry()
    system = str((place or {}).get("StarSystem") or "").strip() or None
    state = place_state(place or {})
    for feature in features:
        try:
            feature.handle_event(dict(entry), cmdr, system, None, dict(state))
            ok += 1
        except Exception:
            logger.exception("%s failed to restore the commander %s", getattr(feature, "__name__", feature), cmdr)
    return ok
