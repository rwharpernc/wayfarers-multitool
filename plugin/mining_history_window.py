"""The Mining History window: the DASHBOARD button in Mining mode.

What the Mining pages cannot show: every mining run found in the commander's journals, added up. There is one window for each half of mining and the button opens the one for the page it
is on: from the Space Mining page the ring runs (**Overview** with totals, prospecting, limpets, sales and the best runs; **Commodities**; **Rings**; **Runs**), from the Surface Mining
page the Rhino's (**Overview** with totals, the bodies mined on, sales and the best runs; **Commodities**; **Bodies**; **Runs**). Every table is sortable. The runs come from `mining_history` (read from the journals in the background, saved per commander) and the
numbers from `mining_history_data`; this module only draws them. It re-reads the newest journal every few seconds while it is open, so a run in progress is included, and the
first time it opens it shows how far the one-time read of the older journals has got.

It reuses the Exploration Dashboard's table and block widgets (`explore_dashboard_window`) so the two windows look and sort alike.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import Any, Dict, List, Optional, Tuple

from config import appname, config

from . import mining_history_data as D
from .explore_dashboard_data import GOOD, INFO, MUTED, TEXT
from .explore_dashboard_window import FieldBlock, TableBox
from .mining_history import history
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.widgets import ScrollFrame, StatTile, Tabs, TileRow

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = {D.SPACE: "wfmt_mining_history_geometry", D.SURFACE: "wfmt_mining_history_surface_geometry"}
TITLES = {D.SPACE: "Space Mining History", D.SURFACE: "Surface Mining History"}
DEFAULT_SIZE = (1120, 740)
MIN_SIZE = (820, 520)
POLL_MS = 700
REFRESH_EVERY_MS = 15000          # re-read the newest journal this often while the window is open

_ROLE_COLORS = {TEXT: "TEXT", GOOD: "OK", INFO: "INFO", MUTED: "MUTED"}   # palette token names, read when drawn

_windows: Dict[str, "MiningHistoryWindow"] = {}


_HELP = (
    ("Mining time", "Runs from a run's first to its last mining event."),
    ("Earned", "What selling the tons a run mined paid, at any station, oldest run first. Tons you did not mine (bought cargo) are not counted, and tons not sold yet are listed under Sales. It is not profit."),
    ("After limpets", "Earned less what the limpets launched in the run cost, each at the price you last paid for limpets. Fuel, repairs and ammunition are not taken off. A ~ means some limpets were launched before WFMT knew a price (they were bought before the journals it has), so the figure is a little high. A run with nothing sold yet shows -."),
)
_HELP_SPACE = (
    ("This window", "The ring mining in your journals: what you prospected, cracked and refined from the ship. Open DASHBOARD on the Surface Mining page for the Rhino's."),
)
_HELP_SURFACE = (
    ("This window", "The Rhino's mining in your journals: the tons refined while a Rhino was out, by body. Open DASHBOARD on the Space Mining page for ring mining."),
    ("Sales", "Matched to each half by the commodity sold, so a commodity mined both ways counts its sales in both."),
)


def show(parent: tk.Misc, mode: str = D.SPACE) -> None:
    """Open the history for `mode` (`D.SPACE` rings, `D.SURFACE` the Rhino), or raise it if it is open. Parented on the main window's toplevel, not on `parent`: the Mining panel destroys
    and rebuilds everything inside its content frame every second, and a window parented there is destroyed with it a moment after it opens."""
    mode = mode if mode in CONFIG_GEOMETRY else D.SPACE
    held = _windows.get(mode)
    if held is not None and held.alive:
        held.refresh_now()
        held.lift()
        return
    _windows[mode] = MiningHistoryWindow(parent.winfo_toplevel(), mode)


def close() -> None:
    for held in list(_windows.values()):
        if held.alive:
            held.close()
    _windows.clear()


class MiningHistoryWindow:
    def __init__(self, parent: tk.Misc, mode: str = D.SPACE) -> None:
        self._mode = mode
        self._signature: Optional[Tuple[Any, ...]] = None
        self._tiles_signature: Optional[tuple] = None
        self._since_refresh = 0
        surface = mode == D.SURFACE
        self._shell = WindowShell(
            parent, TITLES[mode], "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY[mode]) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY[mode], geometry))
        self._shell.add_help(f"{TITLES[mode]} help", _HELP + (_HELP_SURFACE if surface else _HELP_SPACE))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Refresh", self.refresh_now)
        self._shell.add_action("Rebuild from journals", self._rebuild)

        self._tabs = Tabs(self._shell.body)
        self._tabs.pack(fill="both", expand=True)
        self._build_overview(self._tabs.add("Overview"))
        self._commodities = TableBox(self._tabs.add("Commodities"), "What you refined and sold, by commodity (click a heading to sort)", D.commodity_table([]))
        self._commodities.pack(fill="both", expand=True)
        if surface:
            self._places = TableBox(self._tabs.add("Bodies"), "The bodies the Rhino mined on (click a heading to sort)", D.body_table([]))
        else:
            self._places = TableBox(self._tabs.add("Rings"), "Where you mined (click a heading to sort)", D.ring_table([]))
        self._places.pack(fill="both", expand=True)
        self._runs = TableBox(self._tabs.add("Runs"), "Every run from undocking to docking (click a heading to sort)" if not surface else "Every run with the Rhino out (click a heading to sort)",
                              D.run_table([], mode))
        self._runs.pack(fill="both", expand=True)
        self._tabs.select(0)
        history.refresh()
        self._draw()
        self._shell.window.after(POLL_MS, self._poll)

    # --- layout ---------------------------------------------------------------------------------------------------
    def _build_overview(self, tab: tk.Frame) -> None:
        scroll = ScrollFrame(tab)
        scroll.pack(fill="both", expand=True)
        body = scroll.body
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        self._tile_row = TileRow(body)
        self._tile_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=P.PAD, pady=(P.PAD, 0))
        if self._mode == D.SURFACE:
            self._prospecting = None
            self._limpets = FieldBlock(body, "The Rhino's bodies", label_width=26)
            self._limpets.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=P.PAD, pady=P.PAD)
        else:
            self._prospecting = FieldBlock(body, "Prospecting", label_width=26)
            self._prospecting.grid(row=1, column=0, sticky="nsew", padx=(P.PAD, P.PAD_SM), pady=P.PAD)
            self._limpets = FieldBlock(body, "Limpets", label_width=26)
            self._limpets.grid(row=1, column=1, sticky="nsew", padx=(P.PAD_SM, P.PAD), pady=P.PAD)
        self._sales = FieldBlock(body, "Sales", label_width=26)
        self._sales.grid(row=2, column=0, sticky="nsew", padx=(P.PAD, P.PAD_SM), pady=(0, P.PAD))
        self._best = FieldBlock(body, "Best runs by tons refined", label_width=14)
        self._best.grid(row=2, column=1, sticky="nsew", padx=(P.PAD_SM, P.PAD), pady=(0, P.PAD))

    # --- the window -----------------------------------------------------------------------------------------------
    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._shell.close()

    def refresh_now(self) -> None:
        history.refresh()
        self._since_refresh = 0
        self._draw()

    def _rebuild(self) -> None:
        history.clear()
        history.refresh()
        self._draw()

    def _poll(self) -> None:
        if not self.alive:
            return
        self._since_refresh += POLL_MS
        if self._since_refresh >= REFRESH_EVERY_MS:
            self._since_refresh = 0
            history.refresh()
        self._draw()
        self._shell.window.after(POLL_MS, self._poll)

    # --- drawing --------------------------------------------------------------------------------------------------
    def _draw(self) -> None:
        if not self.alive:
            return
        runs: List[D.Run] = D.for_mode(history.runs(), self._mode)
        reading = history.reading
        unsold = history.unsold()
        signature = (len(runs), sum(D.refined_tons(r) for r in runs), sum(D.earned(r) for r in runs), D.waiting_tons(runs, unsold), reading, history.ready, history.commander)
        if signature == self._signature:
            return
        self._signature = signature
        try:
            self._draw_tiles(runs)
            if self._mode == D.SURFACE:
                self._limpets.set(D.surface_fields(runs))
                self._places.fill(D.body_table(runs))
            else:
                self._prospecting.set(D.prospecting_fields(runs))
                self._limpets.set(D.limpet_fields(runs))
                self._places.fill(D.ring_table(runs))
            self._sales.set(D.sales_fields(runs, unsold))
            self._best.set(D.best_runs_fields(runs))
            self._commodities.fill(D.commodity_table(runs))
            self._runs.fill(D.run_table(runs, self._mode))
            self._shell.set_subtitle(D.subtitle(history.commander, runs, reading, self._mode))
            if reading:
                self._shell.set_status(reading)
            elif not history.commander:
                self._shell.set_status("Waiting for your commander: log in or play first.")
            else:
                self._shell.set_status("")
        except Exception:
            logger.warning("The Mining History window could not redraw", exc_info=True)

    def _draw_tiles(self, runs: List[D.Run]) -> None:
        tiles = D.overview_tiles(runs, self._mode)
        signature = tuple((t.value, t.caption, t.role) for t in tiles)
        if signature == self._tiles_signature:
            return
        self._tiles_signature = signature
        for child in self._tile_row.winfo_children():
            child.destroy()
        for tile in tiles:
            StatTile(self._tile_row, tile.value, tile.caption, getattr(P, _ROLE_COLORS.get(tile.role, "TEXT")))
        self._tile_row.arrange(force=True)
