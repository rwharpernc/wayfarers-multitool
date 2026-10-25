"""The Carrier Route planner's owner: it follows the journal for the commander's carrier and keeps the plotted carrier route (one per commander, saved in `carrier_route.json`).

The window (`carrier_route_window`) asks it for the carrier's details and the route, and tells it when a route is plotted or cleared. It is fed the journal events by
`route_planner_panel` (the same events the Route Planner reads), so it follows the commander and moves the route along when the carrier reaches a system on it. No Tk here.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Callable, List, Mapping, Optional

from config import appname

from . import carrier_route as CR
from . import carrier_route_state, commander_data

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

RECOVER_DAYS = 30                 # the journals this recent are read for the carrier's stats and place when the window is first opened


class CarrierRoutePlanner:
    def __init__(self) -> None:
        self._store = carrier_route_state.RouteStore()
        self.cmdr = ""
        self.route: Optional[CR.CarrierRoute] = None
        self._recovered: set = set()
        self._listeners: List[Callable[[], None]] = []

    def start(self, plugin_dir: str) -> None:
        self._store.load(plugin_dir)

    def add_listener(self, listener: Callable[[], None]) -> None:
        self._listeners.append(listener)

    def _notify(self) -> None:
        for listener in tuple(self._listeners):
            try:
                listener()
            except Exception:
                logger.exception("Carrier route listener failed")

    def follow_commander(self, cmdr: str) -> bool:
        """Switch to `cmdr`'s route when the commander changes. True when it changed."""
        key = commander_data.key_for(cmdr)
        if not key or key == commander_data.key_for(self.cmdr):
            return False
        self.cmdr = cmdr
        self.route = self._store.get(cmdr)
        return True

    def handle_event(self, entry: Mapping[str, Any], cmdr: str) -> None:
        changed = self.follow_commander(cmdr)
        if entry.get("event") in CR.EVENTS and CR.tracker.handle_event(entry, cmdr):
            changed = True
            if self.route is not None:
                system = CR.tracker.info(self.cmdr, self.route.kind).system
                if system and self.route.arrive(system):
                    self._store.put(self.cmdr, self.route)
        if changed:
            self._notify()

    def recover_once(self) -> None:
        """Read the carrier's details from the recent journals, once per commander per run (the events may have been written before EDMC started)."""
        key = commander_data.key_for(self.cmdr)
        if not key or key in self._recovered:
            return
        self._recovered.add(key)
        try:
            if CR.tracker.recover(self.cmdr, time.time() - RECOVER_DAYS * 86400):
                self._notify()
        except Exception:
            logger.debug("Could not read the carrier from the journals", exc_info=True)

    def info(self, kind: str = CR.FLEET) -> CR.CarrierInfo:
        return CR.tracker.info(self.cmdr, kind)

    def kinds(self) -> List[str]:
        return CR.tracker.kinds(self.cmdr)

    def set_route(self, route: Optional[CR.CarrierRoute]) -> None:
        self.route = route
        if route is not None:
            system = CR.tracker.info(self.cmdr, route.kind).system
            if system:
                route.arrive(system)           # the carrier may already be on the route
        self._store.put(self.cmdr, route)
        self._notify()

    def clear_route(self) -> bool:
        had = self.route is not None
        self.set_route(None)
        return had

    def mark_reached(self) -> bool:
        """Move the route on by one by hand (the carrier jumped while WFMT could not see it)."""
        route = self.route
        if route is None or route.next_leg is None:
            return False
        route.reached += 1
        self._store.put(self.cmdr, route)
        self._notify()
        return True


planner = CarrierRoutePlanner()


def start(plugin_dir: str) -> None:
    planner.start(plugin_dir)


def handle_event(entry: Mapping[str, Any], cmdr: str) -> None:
    planner.handle_event(entry, cmdr)
