"""The Ranks section of Operations: every Pilots Federation and navy rank the commander holds, by the game's own name, and the percent toward the next.

The names and the arithmetic are `ranks.py`'s. This module is the feature's seam with the rest of WFMT: it takes the journal's `Rank` (where the commander stands),
`Progress` (the percent toward the next rank) and `Promotion` (a new rank) events, falls back on EDMC's own state when EDMC started after the login, and redraws
the table. Nothing is saved: the game sends `Rank` and `Progress` at every login, and a different commander starts empty so their figures never show on another's.

Operations only (`PANEL_PLACEMENT = "fieldops"`). There is no Settings tab: nothing here has a choice to make.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import tkinter as tk

from config import appname

from . import panelkit, ranks

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "fieldops"

HEADER = ("", "Rank", "To next")
_WAITING_TEXT = "(waiting for the game's rank report: it is sent at login)"
_NO_CMDR_TEXT = "(waiting for commander login)"
_NAME_WRAP_PX = 85         # a long rank name (Lieutenant Commander, Chief Petty Officer) breaks onto a second line instead of widening the panel


class RanksController:
    def __init__(self) -> None:
        self._book = ranks.RankBook()
        self._note_var: Optional[tk.StringVar] = None
        self._note: Optional[tk.Label] = None
        self._rows: Optional[panelkit.StatRows] = None

    # --- journal dispatch ----------------------------------------------------------------------------------------------------------------------
    def handle_event(self, entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        try:
            if self._book.take(entry, cmdr, state):
                self.refresh()
        except Exception:
            logger.warning("The Ranks section could not take an event", exc_info=True)

    # --- the panel ---------------------------------------------------------------------------------------------------------------------------------
    def refresh(self) -> None:
        if self._note_var is None or self._note is None or self._rows is None:
            return
        rows = self._book.rows()
        if not rows:
            self._note_var.set(_WAITING_TEXT if self._book.cmdr else _NO_CMDR_TEXT)
            self._note.grid()
            self._rows.show(None, [])
            return
        self._note.grid_remove()
        self._rows.show(HEADER, rows, wrap={1: _NAME_WRAP_PX})

    def build_panel(self, parent: tk.Frame) -> None:
        self._note_var = tk.StringVar(value=_NO_CMDR_TEXT)
        body = panelkit.collapsible_section(parent, "Ranks", "wfmt_ranks_collapsed")
        self._note = panelkit.wrap_label(body, textvariable=self._note_var, anchor="w")
        self._note.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        self._rows = panelkit.StatRows(body)
        self._rows.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        self.refresh()


controller = RanksController()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)
