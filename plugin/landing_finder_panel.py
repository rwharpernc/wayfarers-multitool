"""Nearest place to land: the Exploration panel's row for it (what it does and the button that opens the window).

The lookup is `landing_finder.py` and the window `landing_finder_window.py`. This module is the journal hook and the controller: it remembers the position (`StarPos`) and the ship (`Loadout`)
the commander last had, reads them back from the newest journals when EDMC starts in the middle of a session, and opens the window. It does nothing online by itself: the search runs only when
Find is pressed in the window and the lookup is switched on in Settings > Online.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import Any, Dict, Optional, Tuple

import myNotebook as nb
from config import appname

from . import landing_finder, landing_finder_window, online_lookups, panelkit, restore

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "exploration"

_WRAP_PX = 200


class FinderController:
    """Also the `ctx` the window reads the position, system and ship from."""

    def __init__(self) -> None:
        self.tracker = landing_finder.Tracker()
        self._parent: Optional[tk.Misc] = None
        self._summary: Optional[tk.StringVar] = None
        self._notice: Optional[tk.Label] = None

    # --- what the window asks ---------------------------------------------------------------------------------------
    def position(self) -> Optional[Tuple[float, float, float]]:
        return self.tracker.position

    def system(self) -> str:
        return self.tracker.system

    def ship(self) -> str:
        return self.tracker.ship

    # --- journal ----------------------------------------------------------------------------------------------------
    def handle_event(self, entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        if entry.get("event") == restore.RESTORE_EVENT:
            self._restore(system, state)
            return
        if entry.get("event") in (*landing_finder.Tracker.POSITION_EVENTS, "Loadout") and self.tracker.apply(entry):
            self._changed()

    def _restore(self, system: Optional[str] = None, state: Optional[Dict[str, Any]] = None) -> None:
        """EDMC started in the middle of a session: take the position (the commander's own last one) and the ship from the newest journals."""
        if self.tracker.position is None or not self.tracker.ship:
            found = landing_finder.read_from_journals()
            position = (state or {}).get("StarPos")
            if self.tracker.position is None and isinstance(position, (list, tuple)) and len(position) == 3:
                self.tracker.position, self.tracker.system = tuple(float(v) for v in position), system or ""
            elif self.tracker.position is None:
                self.tracker.position, self.tracker.system = found.position, found.system
            if not self.tracker.ship:
                self.tracker.ship = found.ship
            self._changed()

    def _show_notice(self) -> None:
        """The off-switch warning under Find; hidden while the lookup is on."""
        text = online_lookups.needs(landing_finder_window.CONFIG_ALLOWED)
        if self._notice is None:
            return
        if text:
            self._notice.configure(text=text)
            self._notice.grid()
        else:
            self._notice.grid_remove()

    def _changed(self) -> None:
        try:
            self._show_notice()
            if self._summary is not None:
                self._summary.set(summary_text(self.tracker))
        except tk.TclError:
            pass   # the panel is gone
        landing_finder_window.refresh()

    # --- the panel --------------------------------------------------------------------------------------------------
    def build_panel(self, parent: tk.Frame) -> None:
        self._parent = parent
        self._summary = tk.StringVar(value=summary_text(self.tracker))
        body = panelkit.collapsible_section(parent, "Nearest place to land", "wfmt_landing_finder_collapsed")
        panelkit.wrap_label(body, min_wrap=_WRAP_PX, textvariable=self._summary, anchor="w").grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        button = tk.Button(body, text="Find", command=self._open)
        button.grid(row=2, column=0, sticky=tk.W, pady=(4, 0))
        panelkit.add_tooltip(button, "Find the nearest station that can take your ship (repair, refuel, rearm), and fleet carriers open to all. Online, only when you press Find in the window.")
        self._notice = panelkit.wrap_label(body, min_wrap=_WRAP_PX, anchor="w")
        self._notice.grid(row=3, column=0, columnspan=3, sticky=tk.W)
        self._show_notice()

    def _open(self) -> None:
        if self._parent is not None:
            landing_finder_window.show(self._parent, self)

    def stop(self) -> None:
        landing_finder_window.close()

    # --- Settings tab (the lookup's switch lives in Settings > Online) --------------------------------------------------
    def build_settings(self, notebook: nb.Notebook) -> None:
        frame = nb.Frame(notebook)
        frame.columnconfigure(0, weight=1)
        notebook.add(frame, text="Nearest place to land")
        nb.Label(frame, text="Nearest place to land", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
        nb.Label(
            frame,
            text=("Find on the Exploration panel opens a window that finds, from where you are, the nearest stations that can take your ship and the fleet carriers open "
                  "to everyone. It asks Spansh, and only when you press Find in that window."),
            wraplength=440, justify=tk.LEFT,
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 4))
        nb.Label(frame, text="The Spansh lookup is switched in Settings > Online.", wraplength=440, justify=tk.LEFT).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=(0, 10))


def summary_text(tracker: landing_finder.Tracker) -> str:
    """The line under the section's title: where you are and what pad you need, or that neither is known yet."""
    if tracker.position is None:
        return "Needs your position: it comes from your next jump, or from the journal when you log in."
    pad = landing_finder.ship_pad(tracker.ship)
    return f"From {tracker.system or 'your position'}" + (f"; your ship needs a {pad} pad." if pad else ".")


controller = FinderController()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)


def build_settings(notebook: nb.Notebook) -> None:
    controller.build_settings(notebook)


def start(plugin_dir: str) -> None:
    pass


def stop() -> None:
    controller.stop()
