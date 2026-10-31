"""Colonization Sites window - the commander's construction sites on the left, and the selected site's shopping list on
the right: progress, the totals (still to get, what is on the carrier, the ship's capacity, trips to buy and to haul), filters, and a sortable commodity table with
what the ship and the fleet carrier already cover. The Where to Buy button opens its own window (colonization_buy_window.py)
that finds the closest stations (and, if asked, fleet carriers) with the picked commodity in stock; this window tells it which
commodity is picked, which rows are still to buy and the site's system. Same singleton window + geometry-persistence convention as
the other WFMT windows, built on the shared window kit (plugin/uikit - see docs/WINDOW_FRAMEWORK_SPEC.md). What is
shown and how it adds up lives in colonization_view.py; this file only draws it. "Only what <station> sells" narrows the
list to what the docked station's market has for sale."""

from __future__ import annotations

import logging
import os
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, FrozenSet, List, Mapping, Optional, Tuple

from config import appname, config

from . import colonization, diag_log, colonization_archive_window, colonization_builds_window, colonization_buy_window, colonization_carrier, colonization_catchup, colonization_create_dialog, colonization_projects_window, colonization_view as view, panelkit, rcc_client, rcc_create, rcc_keys
from .colonization_carrier import CarrierCargo
from .colonization import Site
from .colonization_data import SiteRepository
from .uikit import dialogs, palette as P, style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, ProgressBar, StatTile, section_header

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_colonization_window_geometry"
CONFIG_GROUP = "wfmt_colonization_group_by_category"   # the commodity table groups rows under market categories (default on)
_CFG_HIDE_COVERED_LEGACY = "wfmt_colonization_overlay_hide_covered"   # the older tick box (rows the hold plus the carrier cover); read only until CONFIG_SHOW is saved
CONFIG_SHOW = "wfmt_colonization_overlay_show"   # the Show choice ("all", "buy" or "haul"): one setting for this window and the shopping-list overlay card, so the card lists what the window lists
show_listener: Optional[Callable[[], None]] = None   # called after the Show choice changes, so the overlay card redraws at once (the colonization panel sets it)

MIN_WIDTH = 1300
MIN_HEIGHT = 640
DEFAULT_SIZE = (1300, 780)

_SITE_COLUMNS = (
    Column("name", "Site", 190, stretch=True, max_chars=40),
    Column("left", "Left", 70, anchor="e", max_chars=10),
    Column("status", "Status", 80, anchor="e", max_chars=10),
)
_COMMODITY_COLUMNS = (
    Column("label", "Commodity", 200, stretch=True, max_chars=40),
    Column("required", "Required", 80, anchor="e", max_chars=10),
    Column("delivered", "Delivered", 80, anchor="e", max_chars=10),
    Column("remaining", "Acquire", 80, anchor="e", max_chars=10),
    Column("cargo", "In Cargo", 80, anchor="e", max_chars=10),
)
# Shown only for a commander with a fleet carrier: tons moved onto it (colonization_carrier.py), right after what is in
# the ship. Then the two trip counts: loads to gather what is still missing, and loads to haul it all to the site.
_FC_COLUMN = Column("fc", "FC", 70, anchor="e", max_chars=10)
_TRIP_COLUMNS = (
    Column("buy", "Buy Trips", 90, anchor="e", max_chars=10),
    Column("haul", "Haul Trips", 90, anchor="e", max_chars=10),
)
# Without a carrier there is nothing to stage: one load is bought and delivered in one go, so there is one trips column.
_TRIP_COLUMN_ONLY = (Column("haul", "Trips", 80, anchor="e", max_chars=10),)
NOT_AVAILABLE = "  (not available here)"   # after a commodity the docked market does not sell
_SHOW_LABELS = dict(view.SHOW_CHOICES)   # key -> the dropdown text
_POLL_MS = 150
_HOLD_S = 30.0   # how long a pressed button's message stays before the summary line may replace it
_STATION_MAX = 24  # a station name is clipped to this in the "Only what ... sells" label
_NAME_MAX = 60     # a site's name or system is clipped to this in the detail heading
_window: Optional["ColonizationWindow"] = None


def show(parent: tk.Misc, repository: SiteRepository, cmdr: str, cargo: Mapping[str, int],
         carrier: Optional[CarrierCargo] = None, capacity: Optional[Callable[[], int]] = None,
         current_system: Optional[Callable[[], str]] = None,
         market: Optional[Callable[[], Optional[Tuple[str, FrozenSet[str]]]]] = None,
         carrier_id: Optional[Callable[[], Optional[int]]] = None,
         rcc_created: Optional[Callable[[int, str], None]] = None, create_for: Optional[int] = None,
         rescan_history: Optional[Callable[[str], None]] = None) -> None:
    """Open the window for `cmdr`, or raise/refresh it if already open. `capacity` returns the current ship's cargo
    capacity (0 when unknown), for the trips figure; `current_system` the system the commander is in, for the
    "Here" button of the where-to-buy search; `market` the docked station's name and the commodities it has for
    sale, or None when no market has been opened (for the "Only what this station sells" filter); `carrier_id` the market id of the
    commander's own fleet carrier (None when not known), and `rcc_created(market_id, build_id)` is told of a project made on Raven.
    `create_for` is a site's market id: the window selects that site and goes straight to Create Project on Raven for it."""
    global _window
    if _window is not None and _window.alive:
        _window.set_cmdr(cmdr)
        _window.set_cargo(cargo)
        _window.lift()
    else:
        _window = ColonizationWindow(parent, repository, cmdr, cargo, carrier, capacity, current_system, market, carrier_id, rcc_created, rescan_history)
    if create_for is not None:
        _window.create_for(create_for)


def refresh_cargo(cargo: Mapping[str, int]) -> None:
    """Called by the controller whenever the ship's cargo changes; a no-op while the
    window isn't open."""
    if _window is not None and _window.alive:
        _window.set_cargo(cargo)


def refresh_market() -> None:
    """Called by the controller when the docked station's market changes (opened, or left behind)."""
    if _window is not None and _window.alive:
        _window.refresh_market()


def refresh_cmdr(cmdr: str) -> None:
    """Called by the controller when the active commander changes, so an open window follows them instead of
    staying on the previous commander's sites."""
    if _window is not None and _window.alive:
        _window.set_cmdr(cmdr)


def default_show() -> str:
    """The Show choice before one is saved, for this window and the overlay card alike. The older tick box decides: ticked (the default) is To buy."""
    return view.SHOW_BUY if config.get_bool(_CFG_HIDE_COVERED_LEGACY, default=True) else view.SHOW_ALL


def _saved_show() -> str:
    """The Show choice kept from last time (see CONFIG_SHOW), or the card's own default (To buy) when none has been chosen yet,
    so the window and the overlay card list the same rows until you pick."""
    saved = config.get_str(CONFIG_SHOW)
    return saved if saved in _SHOW_LABELS else default_show()


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


class ColonizationWindow:
    def __init__(self, parent: tk.Misc, repository: SiteRepository, cmdr: str, cargo: Mapping[str, int],
                 carrier: Optional[CarrierCargo] = None, capacity: Optional[Callable[[], int]] = None,
                 current_system: Optional[Callable[[], str]] = None,
                 market: Optional[Callable[[], Optional[Tuple[str, FrozenSet[str]]]]] = None,
                 carrier_id: Optional[Callable[[], Optional[int]]] = None,
                 rcc_created: Optional[Callable[[int, str], None]] = None,
                 rescan_history: Optional[Callable[[str], None]] = None) -> None:
        self._repository = repository
        self._rescan_history = rescan_history or (lambda _cmdr: None)
        self._carrier_id = carrier_id or (lambda: None)
        self._rcc_created = rcc_created or (lambda _market_id, _build_id: None)
        self._market = market or (lambda: None)
        self._carrier = carrier
        self._capacity = capacity or (lambda: 0)
        self._current_system = current_system or (lambda: "")
        self._with_fc = False
        self._cmdr = cmdr
        self._cargo: Dict[str, int] = dict(cargo)
        self._sites: Dict[int, Site] = {}
        self._selected: Optional[int] = None   # the market id of the site shown on the right
        self._sort_key = "label"
        self._sort_desc = False
        self._row_label: Dict[str, str] = {}     # commodity table row id -> the commodity's name
        self._wanted: Optional[str] = None       # the commodity row picked for the Where to Buy window's search

        self._shell = WindowShell(
            parent, "Colonization Sites", "", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._toplevel = self._shell.window

        self._shell.add_action("Copy Shopping List", self._on_copy, accent=True,
                                tip="Copy Shopping List - copy what the selected site still needs to the clipboard")
        self._shell.add_action("Where to Buy", self._on_where_to_buy,
                                tip="Where to Buy - open the window that finds stations selling the commodities (Spansh, only when you press Find)")
        self._shell.add_action("Rescan Journals", self._on_rescan,
                                tip="Rescan Journals - read your journals again for sites, deliveries and (if you have one) your fleet carrier")
        # Raven Colonial's actions under one heading: the first ones only read, the last three write (each asks first).
        self._shell.add_menu("Raven Colonial", [
            ("My Projects", self._on_projects),
            ("Planned Builds", self._on_builds),
            ("Raven Progress", self._on_raven_progress),
            None,
            ("Open Selected Build on Raven", self._on_open_build_page),
            ("Open This System on Raven", self._on_open_system_page),
            ("Raven Colonial Website", lambda: webbrowser.open(rcc_client.home_page_url())),
            None,
            ("Create Project on Raven…", self._on_create_rcc),
            ("Report Complete to Raven", self._on_report_rcc),
            ("Mark Plan Entry Demolished…", self._on_demolish_rcc)],
            tip="Raven Colonial - view your projects and planned builds, open Raven pages, or create and report projects (Raven)")
        self._shell.add_menu("Manage Sites", [
            ("Archive Finished", self._on_archive_finished),
            ("Show Archive", self._on_show_archive),
            None,
            ("Remove Site", self._on_remove, "danger"),
            ("Remove Finished", self._on_remove_finished, "danger")],
            tip="Manage Sites - archive, show the archive of, or remove colonization sites")

        self._show = tk.StringVar(master=self._toplevel, value=_SHOW_LABELS[_saved_show()])   # the Show dropdown: which stage of the work to list (the overlay card's choice too)
        self._filter_text = tk.StringVar(master=self._toplevel, value="")
        self._station_only = tk.BooleanVar(master=self._toplevel, value=False)
        self._group_by_category = tk.BooleanVar(master=self._toplevel, value=config.get_bool(CONFIG_GROUP, default=True))

        panes = tk.PanedWindow(self._shell.body, orient="horizontal", bg=P.BG, bd=0, sashwidth=6,
                               sashrelief="flat", opaqueresize=True)
        panes.pack(fill="both", expand=True, pady=(0, P.PAD_SM))

        left = tk.Frame(panes, bg=P.PANE)
        section_header(left, "Sites").pack(fill="x")
        self._site_table = DataTable(
            left, _SITE_COLUMNS, sortable=False, on_select=self._on_pick_site,
            empty_text="No construction sites yet - dock at a construction depot to register one.")
        self._site_table.tag_configure("done", foreground=P.MUTED)
        self._site_table.pack(fill="both", expand=True)
        panes.add(left, stretch="never", minsize=260, width=300)

        right = tk.Frame(panes, bg=P.PANE)
        panes.add(right, stretch="always", minsize=760)
        self._build_detail(right)

        self._commodity_table = self._build_commodity_table()
        self._shell.set_status("Select a site on the left. To find where to buy something, click its commodity row, then press Where to Buy above.")

        repository.add_listener(self._refresh)
        if carrier is not None:
            carrier.add_listener(self._refresh)
        self._refresh()

    # --- layout ----------------------------------------------------------

    def _build_detail(self, right: tk.Frame) -> None:
        self._detail = right
        head = tk.Frame(right, bg=P.PANE, padx=P.PAD, pady=P.PAD_SM)
        head.pack(fill="x")
        self._title = tk.Label(head, text="", fg=P.HEADING, bg=P.PANE, anchor="w", font=style.font(P.FONT_SECTION))
        self._title.pack(fill="x")
        self._where = tk.Label(head, text="", fg=P.MUTED, bg=P.PANE, anchor="w")
        self._where.pack(fill="x")
        self._progress = ProgressBar(head, width=200, height=10)
        self._progress.pack(fill="x", pady=(P.PAD_SM, 0))

        tiles = tk.Frame(right, bg=P.PANE, padx=P.PAD, pady=P.PAD_SM)
        tiles.pack(fill="x")
        self._tile_get = StatTile(tiles, "–", "t still to get", P.ACCENT)
        self._tile_carrier = StatTile(tiles, "–", "t on your carrier", P.INFO)
        self._tile_hold = StatTile(tiles, "–", "t already in your ship", P.OK)
        self._tile_ship = StatTile(tiles, "–", "t ship capacity")
        self._tile_buy = StatTile(tiles, "–", "trips to buy", P.ACCENT)
        self._tile_haul = StatTile(tiles, "–", "trips to haul", P.INFO)
        self._arrange_tiles()

        filters = tk.Frame(right, bg=P.PANE, padx=P.PAD, pady=P.PAD_SM)
        filters.pack(fill="x")
        tk.Label(filters, text="Filter", fg=P.MUTED, bg=P.PANE).pack(side="left")
        entry = tk.Entry(filters, textvariable=self._filter_text, width=14)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._filter_text.trace_add("write", lambda *_: self._refresh_detail())
        tk.Label(filters, text="Show", fg=P.MUTED, bg=P.PANE).pack(side="left")
        show_box = Combobox(filters, textvariable=self._show, state="readonly", width=8, values=list(_SHOW_LABELS.values()))
        show_box.pack(side="left", padx=(P.PAD_SM, 0))
        show_box.bind("<<ComboboxSelected>>", lambda _e: self._on_show_changed())
        # What the docked station sells, from its market (Market.json); off and grayed out until a market is opened.
        self._station_check = tk.Checkbutton(filters, text="Only what this station sells", variable=self._station_only,
                                             command=self._refresh_detail)
        self._station_check.pack(side="left", padx=(P.PAD, 0))
        tk.Checkbutton(filters, text="Group by category", variable=self._group_by_category,
                       command=self._on_group_changed).pack(side="left", padx=(P.PAD, 0))

        self._table_host = tk.Frame(right, bg=P.PANE)
        self._table_host.pack(fill="both", expand=True)

    def _arrange_tiles(self) -> None:
        """The figures above the table. A commander without a fleet carrier has no carrier figure and a single trips figure
        (one load is bought and delivered in one go); one with a carrier has trips to buy and trips to haul."""
        for tile in (self._tile_get, self._tile_carrier, self._tile_hold, self._tile_ship, self._tile_buy, self._tile_haul):
            tile.pack_forget()
        shown = [self._tile_get, self._tile_hold, self._tile_ship, self._tile_haul]
        if self._with_fc:
            shown = [self._tile_get, self._tile_carrier, self._tile_hold, self._tile_ship, self._tile_buy, self._tile_haul]
        self._tile_haul.set_caption("trips to haul" if self._with_fc else "trips to finish")
        for tile in shown:
            tile.pack(side="left", padx=(0, P.PAD_SM))

    def _build_commodity_table(self) -> DataTable:
        columns = _COMMODITY_COLUMNS + ((_FC_COLUMN,) if self._with_fc else ()) + (
            _TRIP_COLUMNS if self._with_fc else _TRIP_COLUMN_ONLY)
        table = DataTable(self._table_host, columns, sortable=False, on_header=self._on_sort,
                          on_select=self._on_pick_commodity, empty_text="Nothing left to deliver here.")
        # Whole-row tints: green when the ship plus the fleet carrier covers the need, orange when it is more than needed. Under the To haul filter there is no green
        # (every row would have it): the rows in the ship's hold are tinted instead, in a color of their own (view.row_tag).
        table.tag_configure(view.TAG_UNAVAILABLE, foreground=P.FAINT)    # the docked market does not sell it
        table.tag_configure(view.TAG_HAULING, foreground=P.TEXT, background=P.ROW_HAUL)
        table.tag_configure(view.STATE_ENOUGH, foreground=P.TEXT, background=P.ROW_OK)
        table.tag_configure(view.STATE_OVER, foreground=P.TEXT, background=P.ROW_OVER)
        table.pack(fill="both", expand=True)
        table.mark_sorted(self._sort_key, self._sort_desc)
        return table

    # --- state ------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._toplevel.deiconify()
        self._toplevel.lift()

    def set_cmdr(self, cmdr: str) -> None:
        if cmdr != self._cmdr:
            self._selected = None
            self._wanted = None
            colonization_buy_window.set_wanted(None)
        self._cmdr = cmdr
        self._refresh()

    def refresh_market(self) -> None:
        self._refresh_detail()

    def set_cargo(self, cargo: Mapping[str, int]) -> None:
        self._cargo = dict(cargo)
        self._refresh()

    def _on_pick_site(self, iid: str) -> None:
        try:
            self._selected = int(iid)
        except ValueError:
            return
        self._wanted = None
        colonization_buy_window.set_wanted(None)
        self._refresh_detail()

    def _on_pick_commodity(self, iid: str) -> None:
        self._wanted = self._row_label.get(iid)
        colonization_buy_window.set_wanted(self._wanted)
        if self._wanted:
            self._announce(f"{self._wanted} is picked for Where to Buy: press Where to Buy above if its window is not open, then Find nearest "
                           "there (or Find all for everything the site still needs).")

    def _on_where_to_buy(self) -> None:
        """Open the Where to Buy window (it asks Spansh only when one of its Find buttons is pressed)."""
        colonization_buy_window.show(self._toplevel, colonization_buy_window.Host(
            wanted=lambda: self._wanted, to_buy=self._rows_to_buy,
            site_system=lambda: (self._selected_site().system if self._selected_site() is not None else ""),
            current_system=self._current_system))

    def _rows_to_buy(self) -> Optional[List[view.CommodityRow]]:
        """The rows the table lists for the selected site after every filter (None when no site is selected), for Find all."""
        site = self._selected_site()
        return None if site is None else self._visible_rows(site, self._carrier_tons(), self._capacity())

    def _on_sort(self, key: str) -> None:
        self._sort_desc = (self._sort_key == key) and not self._sort_desc
        self._sort_key = key
        self._refresh_detail()

    def _refresh(self) -> None:
        if not self.alive:
            return
        sites = [s for s in self._repository.for_cmdr(self._cmdr) if not s.archived]   # archived ones are in the Archive window
        self._sites = {s.market_id: s for s in sites}
        active = sum(1 for s in sites if s.active)
        cmdr_label = self._cmdr or "(no commander detected yet)"
        self._shell.set_subtitle(f"{cmdr_label} — {active} active of {len(sites)} site{'s' if len(sites) != 1 else ''}")

        if self._selected not in self._sites:   # nothing picked yet, or the picked site was removed
            first_active = next((s for s in sites if s.active), None)
            self._selected = (first_active or sites[0]).market_id if sites else None

        self._site_table.clear()
        for site in sites:
            self._site_table.insert(
                str(site.market_id), (site.display_name(), f"{site.remaining_total:,} t", view.site_status(site)),
                tag=None if site.active else "done")
        if self._selected is not None:
            self._site_table.select(str(self._selected))
        self._refresh_detail()

    def _show_key(self) -> str:
        """The Show dropdown as its key (view.SHOW_ALL, SHOW_BUY or SHOW_HAUL)."""
        return next((key for key, text in _SHOW_LABELS.items() if text == self._show.get()), view.SHOW_ALL)

    def _on_show_changed(self) -> None:
        """The Show dropdown changed: keep it, so the shopping-list overlay card lists the same rows, and redraw both."""
        key = next((k for k, text in _SHOW_LABELS.items() if text == self._show.get()), view.SHOW_ALL)
        config.set(CONFIG_SHOW, key)
        self._refresh_detail()
        if show_listener is not None:
            show_listener()

    def _on_group_changed(self) -> None:
        config.set(CONFIG_GROUP, self._group_by_category.get())
        self._refresh_detail()

    def _grouped(self) -> bool:
        """Rows sit under category headings (alphabetical inside), while that is switched on and the table is in
        its natural order; sorting by any other column, or the commodity column backwards, shows a plain sorted list instead."""
        return self._group_by_category.get() and self._sort_key == "label" and not self._sort_desc

    def _commodity_value(self, row: view.CommodityRow):
        return {"label": row.label.casefold(), "required": row.required, "delivered": row.delivered,
                "remaining": row.to_get, "cargo": row.in_cargo, "buy": row.to_get, "haul": row.remaining,
                "fc": row.on_carrier}.get(self._sort_key, row.label.casefold())

    def _refresh_detail(self) -> None:
        if not self.alive:
            return
        site = self._sites.get(self._selected) if self._selected is not None else None

        wants_fc = bool(self._carrier and self._cmdr and self._carrier.has_carrier(self._cmdr))
        if wants_fc != self._with_fc:   # the column set changes with the commander: rebuild the table
            self._with_fc = wants_fc
            self._commodity_table.destroy()
            self._commodity_table = self._build_commodity_table()
            self._arrange_tiles()

        self._commodity_table.clear()
        self._row_label.clear()
        if site is None:
            self._title.configure(text="No site selected")
            self._where.configure(text="")
            self._progress.set(0)
            for tile in (self._tile_get, self._tile_carrier, self._tile_hold, self._tile_ship, self._tile_buy,
                         self._tile_haul):
                tile.set("–")
            return

        self._title.configure(text=_clip(site.display_name(), _NAME_MAX))
        self._where.configure(text=_clip(site.system, _NAME_MAX) + f"  ·  {view.site_status(site)}"
                              if site.system else view.site_status(site))
        self._progress.set(100 if site.complete else site.progress * 100, P.OK if site.complete else P.INFO)
        colonization_buy_window.follow_site(site.system)    # the Where to Buy window searches around the site unless the commander chose elsewhere
        on_carrier = self._carrier.tons(self._cmdr) if wants_fc and self._carrier else {}
        capacity = self._capacity()
        totals = view.totals(site, self._cargo, capacity, on_carrier)
        self._tile_get.set(f"{totals.to_get:,}")
        self._tile_carrier.set(f"{totals.on_carrier:,}" if wants_fc else "–")
        self._tile_hold.set(f"{totals.in_hold:,}")
        self._tile_ship.set(f"{capacity:,}" if capacity > 0 else "–")
        self._tile_buy.set(f"{totals.buy_trips:,}" if capacity > 0 else "–")
        self._tile_haul.set(f"{totals.haul_trips:,}" if capacity > 0 else "–")

        colonization_buy_window.refresh_needs()    # a purchase in the hold or on the carrier takes it off the Where to Buy route
        rows = self._visible_rows(site, on_carrier, capacity)
        rows.sort(key=self._commodity_value, reverse=self._sort_desc)
        self._commodity_table.mark_sorted(self._sort_key, self._sort_desc)
        if self._grouped():
            layout = [(category, items) for category, items in view.group_rows(rows)]
        else:
            layout = [("", rows)]
        for category, items in layout:
            parent = None
            if category:
                parent = f"{site.market_id}:cat:{category}"
                self._commodity_table.insert(parent, (category, "", "", f"{sum(r.to_get for r in items):,}", ""), group=True)
            for row in items:
                values = (row.label if row.available or row.covered else row.label + NOT_AVAILABLE,
                          f"{row.required:,}", f"{row.delivered:,}", f"{row.to_get:,}",   # Acquire: still to get, not yet in the ship or on the carrier
                          f"{row.in_cargo:,}" if row.in_cargo else "")
                if wants_fc:
                    values += (f"{row.on_carrier:,}" if row.on_carrier else "",)
                if wants_fc:
                    values += (view.format_trips(row.buy_trips),)
                values += (view.format_trips(row.haul_trips),)
                tag = view.row_tag(row, self._show_key())
                iid = f"{site.market_id}:{row.key}"
                self._row_label[iid] = row.label
                self._commodity_table.insert(iid, values, tag=tag, parent=parent)
        wanted_iid = next((i for i, label in self._row_label.items() if label == self._wanted), None)
        if wanted_iid:
            self._commodity_table.select(wanted_iid)
        if time.monotonic() < self._held_until:
            return   # an action's own message is still being read; a depot update must not wipe it
        if totals.lines and not rows:
            self._shell.set_status("The filters hide every commodity this site still needs.")
        else:
            plural = lambda n: "" if n == 1 else "s"   # noqa: E731
            if capacity <= 0:
                ship = "Your ship's cargo capacity isn't known yet."
            elif wants_fc:
                ship = (f"Your {capacity:,} t ship needs {totals.buy_trips:,} trip{plural(totals.buy_trips)} to buy "
                        f"what is missing and {totals.haul_trips:,} to haul it all to the site.")
            else:   # nothing to stage anywhere: a load is bought and delivered in one go
                ship = f"Your {capacity:,} t ship needs {totals.haul_trips:,} trip{plural(totals.haul_trips)} to finish the build."
            covered_by = "your ship and carrier" if wants_fc else "your ship"
            self._shell.set_status(f"{totals.lines} commodit{'y' if totals.lines == 1 else 'ies'} still needed, "
                                   f"{totals.covered} covered by {covered_by}. {ship}")

    def _station_filter(self) -> Tuple[str, Optional[FrozenSet[str]]]:
        """The docked station's name and what it sells when "Only what this station sells" is on and a market is known;
        otherwise no filter. Also keeps the checkbox's text and state in step with the market."""
        market = self._market()
        if market is None:
            self._station_only.set(False)
            self._station_check.configure(text="Only what this station sells", state="disabled")
            return "", None
        station, keys = market
        self._station_check.configure(text=f"Only what {_clip(station, _STATION_MAX)} sells" if station
                                      else "Only what this station sells", state="normal")
        return station, (keys if self._station_only.get() else None)

    def _visible_rows(self, site: Site, on_carrier: Mapping[str, int], capacity: int) -> List[view.CommodityRow]:
        """The commodity rows after every filter, as the table shows them."""
        _station, only = self._station_filter()
        market = self._market()
        show = self._show_key()
        return view.commodity_rows(site, self._cargo, on_carrier, False, self._filter_text.get(),
                                   capacity, only_keys=only, market_keys=market[1] if market else None, show=show)

    # --- buttons -----------------------------------------------------------

    _held_until = 0.0

    def _announce(self, text: str, ok: bool = False) -> None:
        """Show a message from something the commander just pressed, and keep it up for a while: the construction panel in the game
        sends depot updates every few seconds, and each one redraws the table and its summary line over the status."""
        self._held_until = time.monotonic() + _HOLD_S
        self._shell.set_status(text, ok)

    def _selected_site(self) -> Optional[Site]:
        return self._sites.get(self._selected) if self._selected is not None else None

    def _carrier_tons(self) -> Dict[str, int]:
        """Tons moved onto the commander's fleet carrier, or nothing for a commander without one."""
        if self._carrier and self._cmdr and self._carrier.has_carrier(self._cmdr):
            return self._carrier.tons(self._cmdr)
        return {}

    def _on_copy(self) -> None:
        site = self._selected_site()
        if site is None:
            self._shell.set_status("Select a site on the left first.")
            return
        lines = [f"{site.display_name()}{f' ({site.system})' if site.system else ''} - still to get:"]
        lines += [f"{amount:,} t  {label}" for label, amount in colonization.shopping_list(site, self._cargo, self._carrier_tons())]
        if len(lines) == 1:
            lines.append("(nothing - everything needed is already on your ship, on your carrier or delivered)")
        if panelkit.copy_to_clipboard(self._toplevel, "\n".join(lines)):
            self._shell.set_status(f"Copied the shopping list for {site.display_name()}.")

    def _on_projects(self) -> None:
        """Open My Projects: every active project the commander has on Raven Colonial. Nothing is asked until it opens."""
        colonization_projects_window.show(
            self._toplevel, lambda: self._cmdr, lambda: frozenset(s.market_id for s in self._repository.for_cmdr(self._cmdr)), self._capacity)

    def _on_builds(self) -> None:
        """Open the Planned Builds window (what Raven Colonial has for this site's system). Nothing is asked until this is pressed."""
        site = self._selected_site()
        if site is None:
            self._announce("Select a site on the left first; its system is the one looked up.")
            return
        if not site.system:
            self._announce("This site has no system name yet; dock at it once so WFMT knows where it is.")
            return
        colonization_builds_window.show(
            self._toplevel, site.system,
            lambda: frozenset(s.market_id for s in self._repository.for_cmdr(self._cmdr)))

    def _on_open_system_page(self) -> None:
        """Open Raven Colonial's page for the selected site's system in the browser (nothing is asked of Raven by WFMT)."""
        site = self._selected_site()
        if site is None or not site.system:
            self._announce("Select a site with a known system on the left first.")
            return
        webbrowser.open(rcc_client.system_page_url(site.system))
        self._announce(f"Opened {site.system} on Raven Colonial in your browser.")

    def _on_open_build_page(self) -> None:
        """Open Raven Colonial's page for the selected site's own project. The project is found the way Raven Progress finds it (one
        read of the system's plan); a site Raven has no project for opens its system page instead."""
        site = self._selected_site()
        if site is None:
            self._announce("Select a site on the left first.")
            return
        if not site.system:
            self._announce("This site has no system name yet; dock at it once so WFMT knows where it is.")
            return
        job: Dict[str, Any] = {"done": False, "build_id": "", "error": ""}
        self._announce("Looking up the project on Raven Colonial…")

        def work() -> None:
            try:
                job["build_id"] = rcc_client.build_id_for(rcc_client.fetch_system(site.system), site.market_id, site.name, self._address(site))
            except rcc_client.RccError as err:
                job["error"] = str(err)
            except Exception:
                logger.exception("Raven Colonial project lookup failed")
                job["error"] = "The lookup failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-open-build").start()
        self._poll_open_build(job, site)

    def _poll_open_build(self, job: Dict[str, Any], site: Site) -> None:
        if not self._shell.alive:
            return
        if not job["done"]:
            self._toplevel.after(150, self._poll_open_build, job, site)
            return
        if job["error"]:
            self._announce(job["error"])
        elif job["build_id"]:
            webbrowser.open(rcc_client.build_page_url(job["build_id"]))
            self._announce(f"Opened {site.display_name()} on Raven Colonial in your browser.")
        else:
            webbrowser.open(rcc_client.system_page_url(site.system))
            self._announce("Raven Colonial has no project linked to this site, so its system page was opened instead.")

    def _on_raven_progress(self) -> None:
        """Read Raven Colonial's own figures for the selected site and set them beside WFMT's (a read; nothing is sent but the project's
        id). The site is matched on its market id in Raven's plan for the system."""
        site = self._selected_site()
        if site is None:
            self._announce("Select a site on the left first.")
            return
        if not site.system:
            self._announce("This site has no system name yet; dock at it once so WFMT knows where it is.")
            return
        job: Dict[str, Any] = {"done": False, "project": None, "error": ""}
        self._announce("Asking Raven Colonial…")

        def work() -> None:
            try:
                build_id = rcc_client.build_id_for(rcc_client.fetch_system(site.system), site.market_id, site.name, self._address(site))
                job["project"] = rcc_client.fetch_project(build_id)
            except rcc_client.RccError as err:
                job["error"] = str(err)
            except Exception:
                logger.exception("Raven Colonial progress lookup failed")
                job["error"] = "The lookup failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-progress").start()
        self._poll_progress(job, site)

    def _poll_progress(self, job: Dict[str, Any], site: Site) -> None:
        if not self._shell.alive:
            return
        if not job["done"]:
            self._toplevel.after(150, self._poll_progress, job, site)
            return
        project = job["project"]
        if project is None:
            self._announce(job["error"] or "Raven Colonial has no project linked to this site.")
            return
        ours = site.remaining_total
        verdict = "they agree" if project.sum_need == ours else f"they differ by {abs(project.sum_need - ours):,} t"
        state = " Raven Colonial has it marked complete." if project.complete else ""
        self._announce(f"{site.display_name()}: Raven Colonial says {project.sum_need:,} t still needed of {project.max_need:,}; "
                               f"WFMT says {ours:,} t ({verdict}).{state}")

    def _on_rescan(self) -> None:
        """Read the journals again for everything this window shows: the sites (the last 30 days, folded in by the same newest-only
        rule as at start-up), the delivery history (every journal) and, for a commander with a fleet carrier, the carrier tally (see
        colonization_carrier.scan_journals). The files are read on a worker thread; the results are applied here on the Tk thread."""
        if not self._cmdr:
            self._announce("Rescan Journals needs a commander; WFMT has not seen one yet.")
            return
        cmdr = self._cmdr
        with_carrier = self._carrier is not None and self._carrier.has_carrier(cmdr)
        job: Dict[str, Any] = {"done": False, "events": None, "record": None}
        self._announce("Rescanning the journals…")
        finished = diag_log.timed("rescan", "Rescan Journals", with_carrier=with_carrier)
        job["finished"] = finished

        def work() -> None:
            try:
                since = (datetime.now(timezone.utc) - timedelta(days=colonization_catchup.MAX_DAYS)).timestamp()
                job["events"] = colonization_catchup.read_since(since)
            except Exception:
                logger.exception("Site rescan failed")
            if with_carrier:
                try:
                    job["record"] = colonization_carrier.scan_journals(cmdr)
                except Exception:
                    logger.exception("Carrier rescan failed")
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-colonization-rescan").start()
        self._poll_rescan(job, cmdr, with_carrier)

    def _poll_rescan(self, job: Dict[str, Any], cmdr: str, with_carrier: bool) -> None:
        if not self._shell.alive:
            return
        if not job["done"]:
            self._toplevel.after(150, self._poll_rescan, job, cmdr, with_carrier)
            return
        if cmdr != self._cmdr:
            self._announce("The commander changed; rescan again.")
            return
        parts = []
        if job["events"] is None:
            parts.append("the sites could not be read (see the EDMC log)")
        else:
            changed = colonization_catchup.apply_events(self._repository, job["events"])
            parts.append(f"{changed} site update{'' if changed == 1 else 's'}")
        self._rescan_history(cmdr)
        parts.append("delivery history being rebuilt")
        if with_carrier and self._carrier is not None:
            record = job["record"]
            if record is None:
                parts.append("the carrier could not be read (see the EDMC log)")
            else:
                self._carrier.replace_from_journals(cmdr, record)
                self._carrier.commit()
                tons = self._carrier.tons(cmdr)
                parts.append(f"{sum(tons.values()):,} t on your carrier in {len(tons)} commodit{'y' if len(tons) == 1 else 'ies'} "
                             "(the next Frontier fetch can replace this with its real cargo)")
        job["finished"](outcome="ok", events=len(job["events"]) if job["events"] is not None else "unreadable")
        self._announce(f"Rescanned the journals: {'; '.join(parts)}.")

    def _raven_ready(self, site: Optional[Site]) -> str:
        """The commander's Raven key when a write may go ahead, else "" (with the reason in the status line). Asks for the key when
        none is saved; it is kept only once a write has worked."""
        if not rcc_keys.enabled():
            self._announce("Sending to Raven Colonial is switched off. Turn it on in Settings → Colonization → Raven Colonial.")
            return ""
        if site is None:
            self._announce("Select a site on the left first.")
            return ""
        if not site.system or not self._cmdr:
            self._announce("This site needs a system name and a commander first; dock at it once.")
            return ""
        key = rcc_keys.keys.get(self._cmdr)
        if not key:
            entered = dialogs.prompt(
                self._toplevel, "Raven Colonial key", f"Paste {self._cmdr}'s Raven Colonial key. It is saved for this commander only and sent "
                "only to Raven Colonial.", show="*")
            key = (entered or "").strip()
        return key

    def _address(self, site: Site) -> Optional[int]:
        """The site's system address when the game state knows it (the commander is in that system), else None (Raven's own is then used)."""
        return rcc_create.locate(site.system, None, self._game_state())[0]

    @staticmethod
    def _game_state() -> Mapping[str, Any]:
        try:
            from monitor import monitor   # EDMC's own module; absent in unit tests
            return getattr(monitor, "state", None) or {}
        except Exception:
            return {}

    def create_for(self, market_id: int) -> None:
        """Select the site with this market id and start Create Project on Raven for it (the offer made on the panel)."""
        if market_id not in self._sites:
            self._announce("That site is no longer in the list.")
            return
        self._selected = market_id
        self._site_table.select(str(market_id))
        self._refresh_detail()
        self._toplevel.after(200, self._on_create_rcc)

    def _on_create_rcc(self) -> None:
        """Start a Raven Colonial project for the selected site: read the system's plan, then (after the commander fills in and confirms the
        dialog) create the project and link the commander (see rcc_create.py). Nothing is sent before the dialog is confirmed."""
        site = self._selected_site()
        key = self._raven_ready(site)
        if not key or site is None:
            return
        if not site.active:
            self._announce("This site is already finished; only an active one can start a project.")
            return
        job: Dict[str, Any] = {"done": False, "plan": None, "error": ""}
        self._announce("Looking at the plan on Raven Colonial…")

        def work() -> None:
            try:
                rcc_client.clear_cache()
                job["plan"] = rcc_client.fetch_system(site.system)
            except rcc_client.RccError as err:
                job["error"] = str(err)
            except Exception:
                logger.exception("Raven Colonial plan lookup failed")
                job["error"] = "The lookup failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-plan").start()
        self._poll_plan(job, site, key)

    def _poll_plan(self, job: Dict[str, Any], site: Site, key: str) -> None:
        if not self._shell.alive:
            return
        if not job["done"]:
            self._toplevel.after(_POLL_MS, self._poll_plan, job, site, key)
            return
        plan = job["plan"]
        if plan is None:
            logger.info("Create project: the plan was not read: %s", job["error"])
            self._announce(job["error"] or "Raven Colonial could not be read.")
            return
        try:
            existing = rcc_client.build_id_for(plan, site.market_id, site.name, self._address(site))
        except rcc_client.RccError as err:
            logger.info("Create project: the lookup of an existing project failed: %s", err)
            self._announce(str(err))
            return
        if existing:
            logger.info("Create project: Raven already has build %s for market %s", existing, site.market_id)
            self._rcc_created(site.market_id, existing)
            self._announce(f"Raven Colonial already has a project for {site.display_name()}; progress sharing will use it.")
            return
        address, star_pos = rcc_create.locate(site.system, plan, self._game_state())
        name = rcc_create.suggested_name(site)
        carrier_id = self._carrier_id()
        locked = ""
        if plan.is_open is False and plan.architect and plan.architect.casefold() != self._cmdr.casefold():
            locked = f"This system is locked to its architect, {plan.architect}; Raven Colonial may refuse a project here."
        logger.info("Create project: asking about %r in %s (%d plan sites, %d bodies)", name, site.system, len(plan.sites), len(plan.bodies))
        chosen = colonization_create_dialog.ask(
            self._toplevel, site.system, name, rcc_create.planned_sites(plan.sites), rcc_create.guess_planned(plan.sites, name),
            plan.architect or self._cmdr, can_attach_carrier=isinstance(carrier_id, int), bodies=plan.bodies,
            primary_port=rcc_create.is_construction_ship(site), locked_note=locked)
        if chosen is None:
            logger.info("Create project: the dialog was cancelled or did not open")
            self._announce("Nothing was sent to Raven Colonial.")
            return
        request = rcc_create.Request(
            site=site, cmdr=self._cmdr, key=key, system=site.system, system_address=address, star_pos=star_pos, name=chosen.name,
            build_type=chosen.build_type, body_num=chosen.body_num, body_name=chosen.body_name, planned=chosen.planned,
            architect=chosen.architect, notes=chosen.notes, due=rcc_create.parse_due(chosen.due), primary_port=chosen.primary_port,
            make_primary=chosen.make_primary, fleet_carrier=carrier_id if chosen.fleet_carrier else None)
        problem = rcc_create.validate(request)
        if problem:
            self._announce(problem)
            return
        run: Dict[str, Any] = {"done": False, "result": None, "error": ""}
        self._announce("Creating the project on Raven Colonial…")

        def create() -> None:
            try:
                run["result"] = rcc_create.create(request)
            except rcc_client.RccError as err:
                run["error"] = str(err)
            except Exception:
                logger.exception("Creating the Raven Colonial project failed")
                run["error"] = "Creating the project failed unexpectedly; see the EDMC log."
            run["done"] = True

        threading.Thread(target=create, daemon=True, name="WFMT-rcc-create").start()
        self._poll_create(run, site, key)

    def _poll_create(self, run: Dict[str, Any], site: Site, key: str) -> None:
        if not self._shell.alive:
            return
        if not run["done"]:
            self._toplevel.after(_POLL_MS, self._poll_create, run, site, key)
            return
        result = run["result"]
        if result is None:
            self._announce(_clip(run["error"] or "Raven Colonial did not create the project.", 200))
            return
        rcc_keys.keys.set(self._cmdr, key)     # saved once it has worked, so a wrong key is not kept
        rcc_client.clear_cache()
        self._rcc_created(site.market_id, result.build_id)
        self._announce(_clip(result.summary, 300))

    def _on_demolish_rcc(self) -> None:
        """Mark the selected site's entry in Raven's plan as demolished (Raven's own status; nothing happens in the game). Asks first."""
        site = self._selected_site()
        key = self._raven_ready(site)
        if not key or site is None:
            return
        job: Dict[str, Any] = {"done": False, "message": ""}
        self._announce("Looking at the plan on Raven Colonial…")

        def work() -> None:
            try:
                rcc_client.clear_cache()
                plan = rcc_client.fetch_system(site.system)
                build_id = rcc_client.build_id_for(plan, site.market_id, site.name, self._address(site))
                entry = next((s for s in plan.sites if s.site_id and (s.market_id == site.market_id or (build_id and s.build_id == build_id))), None)
                address, _pos = rcc_create.locate(site.system, plan, self._game_state())
                if entry is None or address is None:
                    job["message"] = "Raven Colonial has no plan entry for this site."
                else:
                    job["entry"], job["address"] = entry, address
            except rcc_client.RccError as err:
                job["message"] = str(err)
            except Exception:
                logger.exception("Raven Colonial plan lookup failed")
                job["message"] = "The lookup failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-demolish-look").start()
        self._poll_demolish(job, site, key)

    def _poll_demolish(self, job: Dict[str, Any], site: Site, key: str) -> None:
        if not self._shell.alive:
            return
        if not job["done"]:
            self._toplevel.after(_POLL_MS, self._poll_demolish, job, site, key)
            return
        entry = job.get("entry")
        if entry is None:
            self._announce(job["message"])
            return
        if not dialogs.confirm(self._toplevel, "Mark demolished on Raven Colonial",
                               f"Mark {entry.name} in {site.system} as demolished in Raven Colonial's plan?\n\nOnly its plan entry changes."):
            return
        address, cmdr, body = job["address"], self._cmdr, rcc_create.demolish_body(entry)
        run: Dict[str, Any] = {"done": False, "error": ""}
        self._announce("Updating Raven Colonial…")

        def work() -> None:
            try:
                rcc_client.send_write("PUT", f"/api/v2/system/{address}/sites", body, key, cmdr=cmdr)
                rcc_client.clear_cache()
                rcc_keys.keys.set(cmdr, key)
            except rcc_client.RccError as err:
                run["error"] = str(err)
            except Exception:
                logger.exception("Marking the plan entry demolished failed")
                run["error"] = "The update failed unexpectedly; see the EDMC log."
            run["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-demolish").start()
        self._poll_report(run, entry.name, "Raven Colonial now has {name} as demolished.")

    def _on_report_rcc(self) -> None:
        """Tell Raven Colonial the selected site is finished. Asks first, and sends only the commander's Raven key to the one
        project's `complete` address (see rcc_client.complete_project); nothing else leaves WFMT."""
        if not rcc_keys.enabled():
            self._announce("Sending to Raven Colonial is switched off. Turn it on in Settings → Colonization → Raven Colonial.")
            return
        site = self._selected_site()
        if site is None:
            self._announce("Select a site on the left first.")
            return
        if not site.complete:
            self._announce("Your journal has not reported this site complete yet, so there is nothing to report.")
            return
        if not site.system or not self._cmdr:
            self._announce("This site needs a system name and a commander before it can be reported.")
            return
        key = rcc_keys.keys.get(self._cmdr)
        if not key:
            entered = dialogs.prompt(
                self._toplevel, "Raven Colonial key", f"Paste {self._cmdr}'s Raven Colonial key. It is saved for this commander only and sent "
                "only to Raven Colonial.", show="*")
            key = (entered or "").strip()
            if not key:
                return
        if not dialogs.confirm(
                self._toplevel, "Report to Raven Colonial",
                f"Tell Raven Colonial that {site.display_name()} in {site.system} is complete?\n\nOnly your Raven key and this "
                "one project's id are sent; none of your deliveries or cargo."):
            return
        market_id, system, cmdr, site_name, address = site.market_id, site.system, self._cmdr, site.name, self._address(site)
        job: Dict[str, Any] = {"done": False, "error": ""}
        self._announce("Reporting to Raven Colonial…")

        def work() -> None:
            try:
                build_id = rcc_client.build_id_for(rcc_client.fetch_system(system), market_id, site_name, address)
                rcc_client.complete_project(build_id, key, cmdr=cmdr)
                rcc_keys.keys.set(cmdr, key)     # saved once it has worked, so a wrong key is not kept
            except rcc_client.RccError as err:
                job["error"] = str(err)
            except Exception:
                logger.exception("Reporting to Raven Colonial failed")
                job["error"] = "Reporting failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-complete").start()
        self._poll_report(job, site.display_name())

    def _poll_report(self, job: Dict[str, Any], name: str, done: str = "Raven Colonial now has {name} as complete.") -> None:
        if not self._shell.alive:
            return
        if not job["done"]:
            self._toplevel.after(150, self._poll_report, job, name, done)
            return
        self._announce(job["error"] or done.format(name=name))

    def _on_remove(self) -> None:
        site = self._selected_site()
        if site is None or not self._cmdr:
            self._announce("Select the site you want to remove on the left first.")
            return
        self._repository.remove(self._cmdr, site.market_id)

    def _on_archive_finished(self) -> None:
        """Moves every completed or failed site to the Archive window, where it stays for reference (and can be brought back)."""
        if not self._cmdr:
            return
        finished = [s.market_id for s in self._sites.values() if not s.active]
        moved = self._repository.set_archived(self._cmdr, finished, True)
        self._announce(f"Archived {moved} finished site{'s' if moved != 1 else ''}." if moved else "There are no finished sites to archive.")

    def _on_show_archive(self) -> None:
        colonization_archive_window.show(self._toplevel, self._repository, lambda: self._cmdr)

    def _on_remove_finished(self) -> None:
        """Clears every completed or failed site at once."""
        if not self._cmdr:
            return
        finished = [s.market_id for s in self._sites.values() if not s.active]
        for market_id in finished:
            self._repository.remove(self._cmdr, market_id)
        self._announce(f"Removed {len(finished)} finished site{'s' if len(finished) != 1 else ''}.")

    def close(self) -> None:
        colonization_builds_window.close()
        colonization_archive_window.close()
        colonization_projects_window.close()
        colonization_buy_window.close()
        self._shell.close()
