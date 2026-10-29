"""Expedition Log: the controller behind the Expedition window's Log tab and the Exploration panel's Expedition section (which only shows what is running; expeditions are started, paused and stopped in the Expedition window).

The model, the totals and the saving are `expedition_log.py`; the window is `expedition_log_window.py`; the overlay card is `expedition_log_overlay.py`. This module is the
journal hook and the controller they share: it hands every journal event to the log (`book.apply`, which counts it for the expedition that is running), remembers the
system and the ship the commander is in (so a new expedition starts with them), and starts and stops expeditions for the row and the window. Nothing leaves the
computer.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import Any, Dict, Optional

from config import appname

from . import expedition_hub, expedition_log, expedition_log_window, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None
"""The Log has no section of its own: its figures are in the Expedition section (`expedition_panel.py`, which calls `LogController.build_into`), and it is started, paused and stopped in the Expedition window, whose archive is the
Log tab. `build_panel` still builds a section of its own, with buttons, for the tests that open it alone."""

_NAME_SHOWN = 50
_WRAP_PX = 200

book = expedition_log.LogBook()


def summary_text(book_: expedition_log.LogBook, now: Optional[float] = None) -> str:
    """The lines under the row's title: what is running and how it is going, or what to do."""
    if not book_.ready:
        return "Log in to use the Expedition Log."
    run = book_.active()
    if run is None:
        count = len(book_.runs())
        return f"No expedition running ({count} in the archive)." if count else "No expedition yet. Start one in the Expedition window."
    totals = run.totals
    lines = [f"{expedition_log.clip(run.name, _NAME_SHOWN)}: {expedition_log.duration_text(run.elapsed(now))}" + (" (paused)" if run.status == expedition_log.PAUSED else ""),
             f"{len(run.systems):,} systems · {totals.jumps:,} jumps · {totals.light_years:,.0f} ly",
             f"{totals.bodies_scanned:,} bodies · {totals.bio_species:,} species",
             f"Earned {expedition_log.short_credits(totals.earned)} · unsold ~{expedition_log.short_credits(totals.unsold)}"]
    return "\n".join(lines)


def extra_text(book_: expedition_log.LogBook) -> str:
    """The running expedition's figures that the Expedition section's own lines do not carry (they have the name, jumps, light years and time): the systems, bodies, species and credits, and
    `paused` when it is. Empty when nothing is running."""
    run = book_.active()
    if run is None:
        return ""
    totals = run.totals
    first = f"{len(run.systems):,} systems · {totals.bodies_scanned:,} bodies · {totals.bio_species:,} species"
    return ("Paused · " if run.status == expedition_log.PAUSED else "") + first + f"\nEarned {expedition_log.short_credits(totals.earned)} · unsold ~{expedition_log.short_credits(totals.unsold)}"


def title_suffix(book_: expedition_log.LogBook) -> str:
    """The note after the section's title, which stays visible while the section is folded: what is running, or that nothing is (the buttons are inside the section)."""
    run = book_.active()
    if run is None:
        return " - not running" if book_.ready else ""
    return f" - {expedition_log.clip(run.name, 24)}, " + ("paused, " if run.status == expedition_log.PAUSED else "") + f"{expedition_log.short_credits(run.totals.earned)} earned"


class LogController:
    def __init__(self) -> None:
        self._plugin_dir: Optional[str] = None
        self._system = ""
        self._ship = ""
        self._parent: Optional[tk.Misc] = None
        self._summary_var: Optional[tk.StringVar] = None
        self._body: Optional[tk.Frame] = None
        self._buttons: Dict[str, tk.Button] = {}
        book.add_listener(self._update)

    # --- lifecycle ------------------------------------------------------------------------------------------------
    def start(self, plugin_dir: str) -> None:
        self._plugin_dir = plugin_dir
        book.load(plugin_dir)

    def stop(self) -> None:
        book.flush()

    # --- the journal ----------------------------------------------------------------------------------------------
    def handle_event(self, entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        if cmdr:
            book.set_commander(cmdr)
        event = entry.get("event")
        if system:
            self._system = system
        if event in ("FSDJump", "CarrierJump", "Location") and entry.get("StarSystem"):
            self._system = str(entry["StarSystem"])
        if event == "Loadout":
            self._ship = expedition_log.ship_label(entry) or self._ship
        book.apply(entry)

    # --- what the row and the window do ---------------------------------------------------------------------------
    def system(self) -> str:
        return self._system

    def ship(self) -> str:
        return self._ship

    def commander(self) -> str:
        return book.commander

    def start_expedition(self, name: str = "") -> Optional[expedition_log.Run]:
        """Starts an expedition from here, in the ship the commander is in (stopping the one that is running)."""
        return book.start(name, self._system, self._ship)

    def plan_since_last_sale(self, folder: Optional[str] = None, kind: str = expedition_log.SINCE_ANY) -> Optional[dict]:
        """What an expedition carried on from the data the commander is holding would be (see `expedition_log.plan_since_last_sale`; `kind` picks which sale it follows). Reads files only, so it may run on a worker
        thread; `begin_since_last_sale` then starts it on the main thread."""
        return expedition_log.plan_since_last_sale(book.commander, folder, kind) if book.commander else None

    def begin_since_last_sale(self, plan: dict, name: str = "") -> Optional[expedition_log.Run]:
        """Starts the expedition `plan_since_last_sale` worked out, in the ship the commander is in; it carries on counting live from there."""
        return book.start_at(plan["started"], name or expedition_log.SINCE_NAMES.get(plan.get("kind", ""), expedition_log.SINCE_NAMES[expedition_log.SINCE_ANY]), self._system, self._ship, plan["rebuilt"])

    def stop_expedition(self) -> Optional[expedition_log.Run]:
        """Ends the expedition that is running or paused."""
        return book.stop()

    def toggle_pause(self) -> Optional[expedition_log.Run]:
        """Pauses the running expedition, or resumes the paused one."""
        active = book.active()
        if active is None:
            return None
        return book.resume(active.id) if active.status == expedition_log.PAUSED else book.pause(active.id)

    def rescan_totals(self, run_id: str, folder: Optional[str] = None) -> Optional[expedition_log.Run]:
        """What a run's totals come to when worked out again from the commander's journals between its start and end. Reads files and changes nothing, so it can run on
        a worker thread; `rescan` applies it (on the main thread, since the window listens to the log)."""
        run = book.get(run_id)
        if run is None or not book.commander:
            return None
        return expedition_log.rescan(run, book.commander, folder)

    def rescan(self, run_id: str, folder: Optional[str] = None) -> Optional[expedition_log.Run]:
        rebuilt = self.rescan_totals(run_id, folder)
        return book.replace_totals(run_id, rebuilt) if rebuilt is not None else None

    # --- the panel ------------------------------------------------------------------------------------------------
    def build_panel(self, parent: tk.Frame) -> None:
        """A section of its own (the Log alone, as the tests open it); the panel's Expedition section uses `build_into` instead."""
        self._parent = parent
        self._register_tab()
        self._summary_var = tk.StringVar()
        body = panelkit.collapsible_section(parent, "Expedition Log", "wfmt_expedition_log_collapsed")
        self._body = body
        panelkit.wrap_label(body, min_wrap=_WRAP_PX, textvariable=self._summary_var, anchor="w").grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        self._buttons_into(body, 2, with_log=True)
        self._update()

    def build_into(self, parent: tk.Frame, body: tk.Frame, row: int) -> int:
        """Hook the Expedition section (`body`) up to the Log, which it only shows: there are no buttons here, expeditions are started, paused and stopped in the Expedition window.
        Returns the next free row."""
        self._parent = parent
        self._register_tab()
        self._update()
        return row

    def _buttons_into(self, body: tk.Frame, row: int, with_log: bool) -> None:
        buttons = [("start", "START", self._on_start, "Start a new expedition here, in this ship (stops the one that is running)"),
                   ("pause", "PAUSE", self._on_pause, "Hold the running expedition: nothing is counted and its clock stops, and the card keeps showing it, until you press RESUME"),
                   ("stop", "STOP", self._on_stop, "Stop the expedition (running or paused): it is finished and the card goes back to saying none is running")]
        if with_log:
            buttons.append(("log", "LOG", self._open_window, "Open the Expedition Log: the archive of your expeditions, to name, edit, reset and rescan them"))
        for column, (key, text, command, tip) in enumerate(buttons):
            button = tk.Button(body, text=text, command=command)
            button.grid(row=row, column=column, sticky=tk.W, padx=(0 if column == 0 else 6, 0), pady=(4, 0))
            panelkit.add_tooltip(button, tip)
            self._buttons[key] = button

    def _update(self) -> None:
        try:
            if self._summary_var is not None:
                self._summary_var.set(summary_text(book))
            if self._body is not None:
                self._body.set_title_suffix(title_suffix(book))      # type: ignore[attr-defined]
            if "stop" in self._buttons:
                active = book.active()
                self._buttons["stop"].configure(state=tk.NORMAL if active is not None else tk.DISABLED)
                self._buttons["pause"].configure(state=tk.NORMAL if active is not None else tk.DISABLED,
                                                 text="RESUME" if active is not None and active.status == expedition_log.PAUSED else "PAUSE")
                self._buttons["start"].configure(state=tk.NORMAL if book.ready else tk.DISABLED)
        except tk.TclError:
            pass   # the panel is gone

    def _on_start(self) -> None:
        self.start_expedition()

    def _on_stop(self) -> None:
        self.stop_expedition()

    def _on_pause(self) -> None:
        self.toggle_pause()

    def _register_tab(self) -> None:
        expedition_hub.register(expedition_hub.LOG, lambda window, host: expedition_log_window.show(window, book, self, host))

    def _open_window(self) -> None:
        if self._parent is not None:
            self._register_tab()
            expedition_hub.show(self._parent, expedition_hub.LOG)


controller = LogController()


def start(plugin_dir: str) -> None:
    controller.start(plugin_dir)


def stop() -> None:
    controller.stop()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)
