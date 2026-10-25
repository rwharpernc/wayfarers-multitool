"""
Gives a journal event to every feature module, one at a time, without letting one feature's failure stop the others.

load.py hands each journal event to each feature's `handle_event` in turn. A bare loop stops at the first exception, so a bug in one
feature would mean every feature after it never saw that event: for example, an undefined name in System targets raising on EDMC's StartUp
event would keep the BGS, Mining, Trade and ledger features (later in the list) from learning the commander, so their windows would read
as empty. Here each failure is logged with its traceback and the loop carries on.

Pure Python, no tkinter or EDMC; see tests/test_feature_dispatch.py.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, Optional


def dispatch(features: Iterable[Any], entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str],
             state: Dict[str, Any], logger: logging.Logger) -> int:
    """Calls `feature.handle_event(entry, cmdr, system, station, state)` for each feature, in order, and returns how many raised."""
    failed = 0
    for feature in features:
        try:
            feature.handle_event(entry, cmdr, system, station, state)
        except Exception:
            failed += 1
            logger.exception("Feature %s failed on journal event %s; the other features still got it",
                             getattr(feature, "__name__", repr(feature)), entry.get("event"))
    return failed


def replay_ship(features: Iterable[Any], entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any],
                logger: logging.Logger, latest_loadout: Callable[[], Optional[Dict[str, Any]]]) -> int:
    """When EDMC starts with the game already running (`StartUp`), gives every feature the ship's current `Loadout` as well, and returns how many raised.

    The game writes a `Loadout` when you log in and when the ship's fit changes, and EDMC only passes on the events that happen while it runs, so an EDMC started
    mid-session never learned which ship was being flown (the Route Planner said "the ship is not known yet: log in, or change ship", and the fuel, jump range and cargo
    figures that come from the loadout were missing until a relog). The last `Loadout` in the newest journal is exactly what EDMC would have passed on, so replaying it is what
    the features would have seen had EDMC been running; each feature already handles a `Loadout` arriving at any time."""
    if entry.get("event") != "StartUp":
        return 0
    try:
        loadout = latest_loadout()
    except Exception:
        logger.debug("Could not read the current ship from the journals", exc_info=True)
        return 0
    return dispatch(features, loadout, cmdr, system, station, state, logger) if loadout else 0
