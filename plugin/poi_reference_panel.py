"""POI Reference: one Exploration section that looks up the nearest point of interest from both edastro's GEC
(gec_poi_panel.py) and Canonn's Thargoid and Guardian site lists (canonn_poi_panel.py).

The two used to be separate sections, each with its own FIND button, so finding "something worth visiting near me"
meant pressing two buttons and comparing two lines. Here one FIND starts both lookups at once, each source keeps its
own result line and link, and the system name of whichever result is nearer goes to the clipboard to paste into the
galaxy map. UPDATE re-downloads Canonn's lists (edastro's list is cached for six hours by its own module) and then searches.

The lookups stay manual: nothing is requested until a button is pressed. Each source keeps its own Settings (GEC
needs none; Canonn has the site kinds and the skip-logged switch), shown together under Settings → Exploration →
POI Reference.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Mapping, Optional, Set, Tuple

import tkinter as tk

import myNotebook as nb
from config import appname

from . import canonn_poi_panel, gec_poi_panel, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "exploration"


class Collector:
    """Tracks which lookups of one FIND are still running and which result is nearest. No Tk, so it can be tested."""

    def __init__(self) -> None:
        self._pending: Set[str] = set()
        self._best: Optional[Tuple[str, float]] = None

    @property
    def busy(self) -> bool:
        return bool(self._pending)

    def begin(self, names: Set[str]) -> None:
        self._pending = set(names)
        self._best = None

    def report(self, name: str, system: Optional[str], distance: Optional[float]) -> Optional[str]:
        """Records that `name` finished. Returns None while others are still running; once the last one finishes,
        returns the nearest system found ('' when none was found) so the caller can copy it."""
        self._pending.discard(name)
        if system and distance is not None and (self._best is None or distance < self._best[1]):
            self._best = (system, distance)
        if self._pending:
            return None
        return self._best[0] if self._best else ""


class PoiReferenceController:
    def __init__(self) -> None:
        self._gec = gec_poi_panel.controller
        self._canonn = canonn_poi_panel.controller
        self._collector = Collector()
        self._parent: Optional[tk.Frame] = None
        self._buttons: Tuple[tk.Button, ...] = ()
        self._gec.on_done = lambda system, distance: self._finished("gec", system, distance)
        self._canonn.on_done = lambda system, distance: self._finished("canonn", system, distance)

    def handle_event(self, entry: Mapping[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        self._gec.handle_event(entry, cmdr, system, station, state)
        self._canonn.handle_event(entry, cmdr, system, station, state)

    # --- lookup -------------------------------------------------------------

    def _on_find(self, force_refresh: bool = False) -> None:
        if self._collector.busy:
            return
        started = {
            name for name, controller in (("gec", self._gec), ("canonn", self._canonn))
            if controller.start_lookup(force_refresh)
        }
        if not started:
            return
        self._collector.begin(started)
        self._set_buttons(tk.DISABLED)

    def _finished(self, name: str, system: Optional[str], distance: Optional[float]) -> None:
        nearest = self._collector.report(name, system, distance)
        if nearest is None:
            return
        self._set_buttons(tk.NORMAL)
        if nearest and self._parent is not None:
            panelkit.copy_to_clipboard(self._parent, nearest)           # paste it into the galaxy map

    def _set_buttons(self, state: str) -> None:
        for button in self._buttons:
            button.config(state=state)

    # --- main-panel widgets -------------------------------------------------

    def build_panel(self, parent: tk.Frame) -> None:
        self._parent = parent
        body = panelkit.collapsible_section(parent, "POI Reference", "wfmt_poi_reference_collapsed")
        row = self._gec.build_rows(body, 1)
        row = self._canonn.build_rows(body, row)
        button_row = tk.Frame(body)
        button_row.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(4, 0))
        find = tk.Button(button_row, text="Find POI", command=self._on_find)
        panelkit.add_tooltip(find, "Find POI - find the nearest point of interest from edastro's GEC and from Canonn; the nearer one's system is copied")
        find.pack(side=tk.LEFT)
        refresh = tk.Button(button_row, text="Update POI", command=lambda: self._on_find(force_refresh=True))
        panelkit.add_tooltip(refresh, "Update POI - refresh POI data: re-download the Canonn site list, then search again")
        refresh.pack(side=tk.LEFT, padx=(6, 0))
        self._buttons = (find, refresh)

    # --- Settings tab -------------------------------------------------------

    def build_settings(self, notebook: nb.Notebook) -> None:
        self._gec.build_settings(notebook)
        self._canonn.build_settings(notebook)

    def save_settings(self) -> None:
        self._gec.save_settings()
        self._canonn.save_settings()


controller = PoiReferenceController()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)


def build_settings(notebook: nb.Notebook) -> None:
    controller.build_settings(notebook)


def save_settings() -> None:
    controller.save_settings()
