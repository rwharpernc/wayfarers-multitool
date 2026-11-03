"""The Combat Record section of Operations: this session's kills and deaths, the totals, and a button for the window (`combat_window.py`).

The counting is `combat_record.py`'s. This module is the feature's seam with the rest of WFMT: it takes the journal events, tells the record which commander is
playing, and keeps two summary lines current. The record is also changed by a worker thread (the journals are read at start-up), so the lines are redrawn by a
slow poll of the record's `revision` as well as after each event.

Operations only (`PANEL_PLACEMENT = "fieldops"`). There is no Settings tab: nothing here has a choice to make.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import tkinter as tk

from config import appname

from . import combat_record, combat_window, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "fieldops"

POLL_MS = 2000
_NO_CMDR_TEXT = "(waiting for commander login)"


def session_line(session: Dict[str, int]) -> str:
    return "This session: " + (combat_record.summary_text(session) if not combat_record.is_empty(session) else "no kills or deaths yet")


def total_line(total: Dict[str, int], reading: bool) -> str:
    if reading:
        return "All time: reading your journals..."
    return "All time: " + (combat_record.summary_text(total) if not combat_record.is_empty(total) else "none recorded yet")


class CombatController:
    def __init__(self, book: combat_record.CombatBook) -> None:
        self._book = book
        self._session_var: Optional[tk.StringVar] = None
        self._total_var: Optional[tk.StringVar] = None
        self._parent: Optional[tk.Frame] = None
        self._shown = (-1, "", False)

    # --- lifecycle ---------------------------------------------------------------------------------------------------------------------------
    def start(self, plugin_dir: str) -> None:
        self._book.load(plugin_dir)

    # --- journal dispatch ----------------------------------------------------------------------------------------------------------------------
    def handle_event(self, entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        try:
            if cmdr:
                self._book.set_commander(cmdr)       # does nothing unless the commander changed
            if self._book.handle(entry, cmdr, state):
                self.refresh()
        except Exception:
            logger.warning("The Combat Record could not take an event", exc_info=True)

    # --- the panel ---------------------------------------------------------------------------------------------------------------------------------
    def refresh(self) -> None:
        if self._session_var is None or self._total_var is None:
            return
        book = self._book
        cmdr = book.cmdr
        if not cmdr:
            self._session_var.set(_NO_CMDR_TEXT)
            self._total_var.set("")
            return
        self._shown = (book.revision, cmdr, book.reading)
        self._session_var.set(session_line(book.session_total(cmdr, book.session_id)))
        self._total_var.set(total_line(book.total(cmdr), book.reading))

    def _poll(self) -> None:
        parent = self._parent
        if parent is None:
            return
        try:
            if not parent.winfo_exists():
                return
            if (self._book.revision, self._book.cmdr, self._book.reading) != self._shown:
                self.refresh()
            parent.after(POLL_MS, self._poll)
        except tk.TclError:
            pass          # the window is going away

    def build_panel(self, parent: tk.Frame) -> None:
        self._parent = parent
        self._session_var = tk.StringVar(value=_NO_CMDR_TEXT)
        self._total_var = tk.StringVar(value="")
        body = panelkit.collapsible_section(parent, "Combat Record", "wfmt_combat_collapsed")
        panelkit.wrap_label(body, textvariable=self._session_var, anchor="w").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        panelkit.wrap_label(body, textvariable=self._total_var, anchor="w").grid(row=1, column=0, columnspan=3, sticky=tk.W)
        button = tk.Button(body, text="Combat", command=self._on_open)
        button.grid(row=2, column=0, sticky=tk.W, pady=(4, 0))
        panelkit.add_tooltip(button, "Combat - open your kills and deaths, per ship, for this session and in total")
        self._shown = (-1, "", False)
        self.refresh()
        parent.after(POLL_MS, self._poll)

    def _on_open(self) -> None:
        if self._parent is not None:
            combat_window.show(self._parent, self._book)


controller = CombatController(combat_record.book)


def start(plugin_dir: str) -> None:
    controller.start(plugin_dir)


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)
