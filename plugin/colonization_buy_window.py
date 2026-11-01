"""The Where to Buy window - the closest stations (and, if asked, fleet carriers) with a commodity in stock, opened from the Colonization Sites window.

"Find nearest" searches the commodity picked in the Sites window; "Find all" searches every commodity still to be bought for the selected site (as the
Sites table lists them, covered rows left out), one request each, and lists the closest few stations under each, with a
suggested shopping route. The search choices are remembered between sessions. Nothing is asked of Spansh until a Find button is pressed, and only the
commodity name and the system searched around are sent.

What is searched and how the answer adds up lives in colonization_sources.py; this file draws them. The window knows nothing
of the Sites window beyond the `Host` it is given: which commodity is picked, which rows are still to buy, and the site's system.

Built on the shared window kit (plugin/uikit - see docs/WINDOW_FRAMEWORK_SPEC.md); a worker thread does the searches and the Tk thread polls for the answer.
"""

from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from config import appname, config

from . import colonization_sources as sources, colonization_view as view, diag_log, panelkit, system_autocomplete
from .mining_spansh_client import search_stations_selling_all
from .uikit import palette as P, style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, FlatButton

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_colonization_buy_window_geometry"
CONFIG_SEARCH = "wfmt_colonization_search_prefs"   # radius, pad, carriers and sort of the search (the key the Sites window kept it under)

MIN_WIDTH = 960
MIN_HEIGHT = 560
DEFAULT_SIZE = (1060, 640)

_SOURCE_COLUMNS = (
    Column("station", "Station", 120, stretch=True, max_chars=32),
    Column("system", "System", 110, stretch=True, max_chars=30),
    Column("kind", "Type", 100, max_chars=20),
    Column("planetary", "Planetary", 80, anchor="center", max_chars=4),
    Column("pad", "Pad", 60, max_chars=8),
    Column("distance", "Distance", 70, anchor="e", max_chars=12),
    Column("arrival", "Arrival", 80, anchor="e", max_chars=12),
    Column("price", "Price", 70, anchor="e", max_chars=10),
    Column("supply", "Supply", 70, anchor="e", max_chars=10),
)
_PAD_ORDER = {"Large": 0, "Medium": 1, "Small": 2, "?": 3}
_NO_LIMIT = "No limit"
_SORT_CHOICES = (("Closest first", sources.SORT_DISTANCE), ("Cheapest first", sources.SORT_PRICE))
_POLL_MS = 150
_PLAN_ROWS = 8     # the shopping plan block is this many rows tall at most, then it scrolls
_ERROR_MAX = 90   # a failure message from outside is clipped to this
_NAME_MAX = 60     # a system or commodity name is clipped to this in a note
_HINT = "Pick a commodity row in the Sites window, then Find nearest - or Find all to search everything still to buy."
_STEPS = ("Find nearest searches the commodity picked in the Colonization Sites window: click its row there first. "
          "Find all searches every commodity the selected site still needs to buy, as that window lists them (its filters apply).")
_NONE_PICKED = "none picked - click a commodity row in the Sites window"
_window: Optional["BuyWindow"] = None


@dataclass(frozen=True)
class Host:
    """What the window asks of the Sites window that opened it. `wanted` is the commodity picked there (None when none); `to_buy` the rows still to be
    bought for the selected site, after every filter (None when no site is selected); `site_system` the selected site's system; `current_system` the
    system the commander is in now (empty when not known)."""
    wanted: Callable[[], Optional[str]]
    to_buy: Callable[[], Optional[List[view.CommodityRow]]]
    site_system: Callable[[], str]
    current_system: Callable[[], str]


def show(parent: tk.Misc, host: Host) -> None:
    """Open the window, or raise it and bring it up to date with the Sites window if it is already open."""
    global _window
    if _window is not None and _window.alive:
        _window.host = host
        _window.sync()
        _window.lift()
        return
    _window = BuyWindow(parent, host)


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def set_wanted(label: Optional[str]) -> None:
    """The Sites window's picked commodity changed; a no-op while this window is closed."""
    if _window is not None and _window.alive:
        _window.set_wanted(label)


def refresh_needs() -> None:
    """The Sites window's figures changed (a purchase reached the hold or the carrier, or a delivery was made); the route and the lists follow them."""
    if _window is not None and _window.alive:
        _window.refresh_needs()


def follow_site(system: str) -> None:
    """The Sites window's selected site (or its system) changed; the search follows it unless the commander typed their own system."""
    if _window is not None and _window.alive:
        _window.follow_site(system)


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


class BuyWindow:
    def __init__(self, parent: tk.Misc, host: Host) -> None:
        self.host = host
        self._system_edited = False              # the commander typed their own search system
        self._search_id = 0                      # which search the window waits for; older answers are dropped
        self._result: Optional[sources.SearchResult] = None
        self._result_label = ""
        self._whole: Optional[sources.WholeListResult] = None   # the last "Find all" answer (instead of _result)
        self._whole_to_get: Dict[str, int] = {}                 # commodity label -> tons still to get, for its heading (kept up to date by refresh_needs)
        self._whole_system = ""                                 # the system the last "Find all" searched around
        self._plan: Optional[sources.RoutePlan] = None          # the suggested shopping route for the last "Find all"
        self._whole_job: Optional[Dict[str, Any]] = None        # the "Find all" running now
        self._prefs = sources.load_prefs(config.get_str(CONFIG_SEARCH))
        self._source_sort = ("distance", False)
        self._source_rows: Dict[str, str] = {}   # result row id -> its system name, for Copy System

        self._shell = WindowShell(
            parent, "Where to Buy", "The closest places to buy what a site still needs", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._toplevel = self._shell.window

        self._system_var = tk.StringVar(master=self._toplevel, value="")
        self._no_carriers_var = tk.BooleanVar(master=self._toplevel, value=self._prefs.no_carriers)
        self._no_surface_var = tk.BooleanVar(master=self._toplevel, value=self._prefs.no_surface)
        self._enough_var = tk.BooleanVar(master=self._toplevel, value=self._prefs.enough_stock)
        self._shipyard_var = tk.BooleanVar(master=self._toplevel, value=self._prefs.shipyard_only)
        content = tk.Frame(self._shell.body, bg=P.PANE)    # the note wraps to this frame's width, which the body's side padding does not narrow
        content.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._build(content)
        self.sync()

    # --- layout ----------------------------------------------------------

    def _build(self, host: tk.Misc) -> None:
        """The search: its options, the Find nearest button and the table of results."""
        intro = tk.Frame(host, bg=P.PANE, padx=P.PAD, pady=P.PAD_SM)
        intro.pack(fill="x")
        self._picked = tk.Label(intro, text="", fg=P.HEADING, bg=P.PANE, anchor="w", justify="left", font=style.font(P.FONT_SECTION))
        self._picked.pack(fill="x")
        self._steps = tk.Label(intro, text=_STEPS, fg=P.MUTED, bg=P.PANE, anchor="w", justify="left")
        self._steps.pack(fill="x")
        options = tk.Frame(host, bg=P.PANE, padx=P.PAD, pady=P.PAD_SM)
        options.pack(fill="x")
        first = tk.Frame(options, bg=P.PANE)
        first.pack(fill="x")
        tk.Label(first, text="Around", fg=P.MUTED, bg=P.PANE).pack(side="left")
        entry = tk.Entry(first, textvariable=self._system_var, width=26)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        system_autocomplete.attach(entry, self._system_var, on_pick=lambda: setattr(self, "_system_edited", True))
        entry.bind("<KeyRelease>", lambda _e: setattr(self, "_system_edited", True))
        FlatButton(first, "Here", self._on_here,
                   tip="Here - fill in the system you are in now").pack(side="left", padx=(0, P.PAD))
        tk.Label(first, text="Within", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._radius = Combobox(first, state="readonly", width=9,
                                values=[f"{r} ly" for r in sources.RADIUS_CHOICES] + [_NO_LIMIT])
        self._radius.set(_NO_LIMIT if self._prefs.radius_ly is None else f"{int(self._prefs.radius_ly)} ly")
        self._radius.pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._radius.bind("<<ComboboxSelected>>", lambda _e: self._on_filter_change())
        tk.Label(first, text="Sort", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._sort = Combobox(first, state="readonly", width=14, values=[label for label, _ in _SORT_CHOICES])
        self._sort.set(next((text for text, key in _SORT_CHOICES if key == self._prefs.sort), _SORT_CHOICES[0][0]))
        self._sort.pack(side="left", padx=(P.PAD_SM, 0))
        self._sort.bind("<<ComboboxSelected>>", lambda _e: self._on_filter_change())

        presets = tk.Frame(options, bg=P.PANE, pady=P.PAD_SM)
        presets.pack(fill="x")
        second = tk.Frame(options, bg=P.PANE, pady=P.PAD_SM)
        second.pack(fill="x")
        tk.Label(presets, text="Preset", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._preset = Combobox(presets, state="readonly", width=30, values=[p.label for p in sources.PRESETS] + [sources.PRESET_LABELS[sources.PRESET_CUSTOM]])
        self._preset.set(sources.PRESET_LABELS.get(self._prefs.preset, sources.PRESET_LABELS[sources.DEFAULT_PRESET]))
        self._preset.pack(side="left", padx=(P.PAD_SM, P.PAD))
        tk.Label(presets, text="Your own system is always searched first.", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._preset.bind("<<ComboboxSelected>>", lambda _e: self._on_preset())
        tk.Label(second, text="Landing pad", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._pad = Combobox(second, state="readonly", width=17, values=[label for _, label in sources.PAD_CHOICES])
        self._pad.set(next((text for key, text in sources.PAD_CHOICES if key == self._prefs.pad), sources.PAD_CHOICES[0][1]))
        self._pad.pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._pad.bind("<<ComboboxSelected>>", lambda _e: self._on_filter_change())
        self._find_button = FlatButton(second, "Find nearest", self._on_find, kind="accent",
                                       tip="Find nearest - search for the nearest stations selling the selected commodity (Spansh)")
        self._find_button.pack(side="right")
        self._find_all_button = FlatButton(second, "Find all", self._on_find_all,
                                           tip="Find all - search for every commodity still to buy and plan a route (Spansh); press again to stop")
        self._find_all_button.pack(side="right", padx=(0, 6))
        FlatButton(second, "Copy System", self._on_copy_system,
                   tip="Copy System - copy the selected result's system name to the clipboard").pack(side="right", padx=(0, 6))
        FlatButton(second, "Copy Route", self._on_copy_route,
                   tip="Copy Route - copy the shopping route from the last Find all to the clipboard").pack(side="right", padx=(0, 6))

        third = tk.Frame(options, bg=P.PANE)
        third.pack(fill="x")
        tk.Checkbutton(third, text="Exclude fleet carriers", variable=self._no_carriers_var, command=self._on_filter_change).pack(side="left", padx=(0, P.PAD))
        tk.Checkbutton(third, text="Exclude surface ports", variable=self._no_surface_var, command=self._on_filter_change).pack(side="left", padx=(0, P.PAD))
        fourth = tk.Frame(options, bg=P.PANE)
        fourth.pack(fill="x")
        tk.Checkbutton(fourth, text="Only stations with enough stock", variable=self._enough_var, command=self._on_filter_change).pack(side="left", padx=(0, P.PAD))
        tk.Checkbutton(fourth, text="Only stations with a shipyard", variable=self._shipyard_var, command=self._on_filter_change).pack(side="left", padx=(0, P.PAD))
        tk.Label(fourth, text="Arrival within", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._arrival = Combobox(fourth, state="readonly", width=10, values=[f"{n:,} ls" for n in sources.ARRIVAL_CHOICES] + [_NO_LIMIT])
        self._arrival.set(_NO_LIMIT if self._prefs.max_arrival_ls is None else f"{self._prefs.max_arrival_ls:,} ls")
        self._arrival.pack(side="left", padx=(P.PAD_SM, 0))
        self._arrival.bind("<<ComboboxSelected>>", lambda _e: self._on_filter_change())

        self._sources_note = tk.Label(host, text=_HINT, fg=P.MUTED, bg=P.PANE, anchor="w", justify="left", padx=P.PAD)
        self._sources_note.pack(fill="x")
        host.bind("<Configure>", lambda e: [label.configure(wraplength=max(e.width - 2 * P.PAD, 100)) for label in (self._sources_note, self._picked, self._steps)])
        # The shopping plan (the suggested route) has a block of its own above the per-commodity
        # lists, so it is not lost among them. It is shown only after a Find all that produced one.
        self._plan_frame = tk.Frame(host, bg=P.CARD, padx=P.PAD_SM, pady=P.PAD_SM)
        tk.Label(self._plan_frame, text="Closest way to buy everything", fg=P.ACCENT, bg=P.CARD, anchor="w",
                 font=style.font(P.FONT_SECTION)).pack(fill="x", padx=P.PAD_SM)
        self._plan_table = DataTable(self._plan_frame, _SOURCE_COLUMNS, sortable=False, on_select=self._on_plan_pick,
                                     select_groups=True, visible_rows=_PLAN_ROWS)
        self._plan_table.tag_configure("carrier", foreground=P.INFO)
        self._plan_table.tag_configure("warn", foreground=P.WARN)
        self._plan_table.pack(fill="x")
        self._list_heading = tk.Label(host, text="Closest stations for each commodity", fg=P.HEADING, bg=P.PANE, anchor="w",
                                      font=style.font(P.FONT_SECTION), padx=P.PAD, pady=P.PAD_SM)
        self._source_table = DataTable(host, _SOURCE_COLUMNS, sortable=False, on_header=self._on_source_sort,
                                       on_select=self._on_source_pick, select_groups=True, empty_text="No search yet.")
        self._source_table.tag_configure("carrier", foreground=P.INFO)
        self._source_table.tag_configure("warn", foreground=P.WARN)
        self._source_table.pack(fill="both", expand=True)

    def _show_plan(self, show: bool) -> None:
        """Show or hide the shopping plan block (and the heading that tells the commodity lists apart from it)."""
        if show:
            self._plan_frame.pack(fill="x", padx=P.PAD, pady=(P.PAD_SM, P.PAD_SM), before=self._source_table)
            self._list_heading.pack(fill="x", before=self._source_table)
        else:
            self._plan_frame.pack_forget()
            self._list_heading.pack_forget()

    # --- state ------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._toplevel.deiconify()
        self._toplevel.lift()

    def sync(self) -> None:
        """Bring the window up to date with the Sites window: the picked commodity and the site's system."""
        self.follow_site(self.host.site_system())
        self.set_wanted(self.host.wanted())

    def follow_site(self, system: str) -> None:
        if system and not self._system_edited:   # search around the site unless the commander chose elsewhere
            self._system_var.set(system)

    def set_wanted(self, label: Optional[str]) -> None:
        self._picked.configure(text="Commodity: " + (_clip(label, _NAME_MAX) if label else _NONE_PICKED))
        if label:
            self._say(f"Ready to search for {label}. Press Find nearest.")
        elif self._result is None and self._whole is None:
            self._say(_HINT)

    # --- the search -------------------------------------------------------

    def _on_here(self) -> None:
        here = self.host.current_system()
        if not here:
            self._say("WFMT hasn't seen which system you are in yet.")
            return
        self._system_var.set(here)
        self._system_edited = True

    def _radius_ly(self) -> Optional[float]:
        text = self._radius.get()
        if text == _NO_LIMIT:
            return None
        try:
            return float(text.split()[0])
        except (ValueError, IndexError):
            return float(sources.DEFAULT_RADIUS_LY)

    def _arrival_ls(self) -> Optional[int]:
        text = self._arrival.get()
        if text == _NO_LIMIT:
            return None
        try:
            return int(text.split()[0].replace(",", ""))
        except (ValueError, IndexError):
            return None

    def _pad_choice(self) -> str:
        label = self._pad.get()
        return next((key for key, text in sources.PAD_CHOICES if text == label), sources.PAD_LARGE_FIRST)

    def _sort_choice(self) -> str:
        label = self._sort.get()
        return next((key for text, key in _SORT_CHOICES if text == label), sources.SORT_DISTANCE)

    def _preset_key(self) -> str:
        """The preset the options on screen match, or custom."""
        return sources.preset_for(pad=self._pad_choice(), sort=self._sort_choice(), no_carriers=bool(self._no_carriers_var.get()),
                                  no_surface=bool(self._no_surface_var.get()), max_arrival_ls=self._arrival_ls(),
                                  enough_stock=bool(self._enough_var.get()), shipyard_only=bool(self._shipyard_var.get()),
                                  radius_ly=self._radius_ly())

    def _on_preset(self) -> None:
        """A preset was chosen: set the options to it (Custom changes nothing), then draw again from what was already found."""
        preset = next((p for p in sources.PRESETS if p.label == self._preset.get()), None)
        if preset is not None:
            self._pad.set(next(text for key, text in sources.PAD_CHOICES if key == preset.pad))
            self._sort.set(next(text for text, key in _SORT_CHOICES if key == sources.SORT_DISTANCE))
            self._no_carriers_var.set(preset.no_carriers)
            self._no_surface_var.set(preset.no_surface)
            self._enough_var.set(preset.enough_stock)
            self._shipyard_var.set(preset.shipyard_only)
            self._arrival.set(_NO_LIMIT if preset.max_arrival_ls is None else f"{preset.max_arrival_ls:,} ls")
            if preset.radius_ly is not None:
                self._radius.set(f"{int(preset.radius_ly)} ly")
        self._on_filter_change()

    def _save_prefs(self) -> None:
        key = self._preset_key()
        self._preset.set(sources.PRESET_LABELS[key])
        config.set(CONFIG_SEARCH, sources.dump_prefs(sources.SearchPrefs(
            radius_ly=self._radius_ly(), pad=self._pad_choice(), no_carriers=bool(self._no_carriers_var.get()),
            sort=self._sort_choice(), no_surface=bool(self._no_surface_var.get()), max_arrival_ls=self._arrival_ls(),
            enough_stock=bool(self._enough_var.get()), shipyard_only=bool(self._shipyard_var.get()), preset=key)))

    def _say(self, text: str, busy: bool = False) -> None:
        """The note under the buttons. A search in progress is shown in the status color so it stands out; anything else in the plain text one."""
        self._sources_note.configure(text=text, fg=P.STATUS if busy else P.TEXT)

    def _on_find(self) -> None:
        """Starts the search on a worker thread (Spansh can take seconds) and polls for its answer."""
        wanted = self.host.wanted()
        if not wanted:
            self._say("Pick a commodity row in the Sites window first.")
            return
        system = self._system_var.get().strip()
        if not system:
            self._say("Enter a system to search around, or press Here.")
            return
        commodity, radius, pad = wanted, self._radius_ly(), self._pad_choice()
        carriers, order = not self._no_carriers_var.get(), self._sort_choice()
        here = self.host.current_system()
        self._save_prefs()
        self._search_id += 1
        job: Dict[str, Any] = {"id": self._search_id, "done": False, "result": None, "error": ""}
        self._find_button.set_enabled(False)
        self._say(f"Searching for {commodity} around {_clip(system, _NAME_MAX)}…", busy=True)
        finished = diag_log.timed("search", "Find nearest", commodity=commodity, system=system, radius_ly=radius, pad=pad, carriers=carriers, sort=order)
        job["finished"] = finished

        def work() -> None:
            try:
                job["result"] = sources.find(system, commodity, radius_ly=radius, pad=pad,
                                             include_carriers=carriers, sort=order, here=here)
            except Exception as exc:   # network, parse or bad input: shown, not raised into the main thread
                logger.exception("Colonization where-to-buy search failed")
                job["error"] = str(exc) or exc.__class__.__name__
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-colonization-sources").start()
        self._toplevel.after(_POLL_MS, self._poll_search, job, commodity, system)

    def _poll_search(self, job: Dict[str, Any], commodity: str, system: str) -> None:
        if not self.alive or job["id"] != self._search_id:
            return
        if not job["done"]:
            self._toplevel.after(_POLL_MS, self._poll_search, job, commodity, system)
            return
        self._find_button.set_enabled(True)
        if job["error"]:
            job["finished"](outcome="failed", error=job["error"])
            self._say(f"The search failed: {_clip(job['error'], _ERROR_MAX)}. Spansh may be busy; try again shortly.")
            return
        self._result, self._result_label, self._whole, self._plan = job["result"], commodity, None, None
        job["finished"](outcome="ok", stations=len(job["result"].stations), carriers=len(job["result"].carriers))
        self._render_sources(system)

    def _on_find_all(self) -> None:
        """Searches every commodity still to be bought (as the Sites table lists them, covered rows left out), one request each
        on a worker thread; pressing the button again while it runs stops it, keeping what it has found."""
        if self._whole_job is not None:
            self._whole_job["cancel"] = True
            self._say("Stopping after the search in progress…", busy=True)
            return
        shown = self.host.to_buy()
        system = self._system_var.get().strip()
        if shown is None:
            self._say("Select a site in the Sites window first.")
            return
        if not system:
            self._say("Enter a system to search around, or press Here.")
            return
        rows = [r for r in shown if r.to_get > 0]
        if not rows:
            self._say("Nothing left to buy in the list as it is shown.")
            return
        labels = [r.label for r in rows]
        to_get = {r.label: r.to_get for r in rows}
        radius, pad, carriers, order = self._radius_ly(), self._pad_choice(), not self._no_carriers_var.get(), self._sort_choice()
        here = self.host.current_system()
        self._save_prefs()
        self._search_id += 1
        job: Dict[str, Any] = {"id": self._search_id, "done": False, "result": None, "error": "", "cancel": False,
                               "progress": (0, len(labels), labels[0])}
        self._whole_job = job
        self._find_button.set_enabled(False)
        self._find_all_button.configure(text="Stop")
        self._say(f"Searching for {len(labels)} commodities around {_clip(system, _NAME_MAX)}…", busy=True)
        job["finished"] = diag_log.timed("search", "Find all", commodities=len(labels), system=system, radius_ly=radius, pad=pad, carriers=carriers, sort=order)

        def work() -> None:
            try:
                job["result"] = sources.find_whole_list(
                    system, labels, radius_ly=radius, pad=pad, include_carriers=carriers, sort=order,
                    progress=lambda done, total, label: job.__setitem__("progress", (done, total, label)),
                    cancelled=lambda: job["cancel"], one_stop=search_stations_selling_all, needs=to_get, here=here)
            except Exception as exc:   # bad input or an unexpected failure: shown, not raised into the main thread
                logger.exception("Colonization whole-list search failed")
                job["error"] = str(exc) or exc.__class__.__name__
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-colonization-sources-all").start()
        self._toplevel.after(_POLL_MS, self._poll_whole, job, system, to_get)

    def _poll_whole(self, job: Dict[str, Any], system: str, to_get: Dict[str, int]) -> None:
        if not self.alive or job["id"] != self._search_id:
            return
        if not job["done"]:
            done, total, label = job["progress"]
            self._say(f"Searching {done + 1} of {total}: {_clip(label, _NAME_MAX)}…", busy=True)
            self._toplevel.after(_POLL_MS, self._poll_whole, job, system, to_get)
            return
        self._whole_job = None
        self._find_button.set_enabled(True)
        self._find_all_button.configure(text="Find all")
        if job["error"]:
            job["finished"](outcome="failed", error=job["error"])
            self._say(f"The search failed: {_clip(job['error'], _ERROR_MAX)}.")
            return
        self._whole, self._whole_to_get, self._result, self._whole_system = job["result"], to_get, None, system
        job["finished"](outcome="stopped" if job["result"].stopped else "ok", searched=len(job["result"].found), failed=len(job["result"].failed),
                        without_sources=len(job["result"].without_sources()))
        self._plan = self._make_plan()
        self._render_whole(system)

    def _on_source_sort(self, key: str) -> None:
        descending = self._source_sort[0] == key and not self._source_sort[1]
        self._source_sort = (key, descending)
        if self._whole is not None:
            self._render_whole()
        elif self._result is not None:
            self._render_sources()

    @staticmethod
    def _source_value(source: sources.Source, key: str):
        return {"station": source.station.casefold(), "system": source.system.casefold(), "kind": source.kind.casefold(),
                "planetary": source.is_planetary, "pad": _PAD_ORDER.get(source.pad, 3), "distance": source.distance_ly, "arrival": source.arrival_ls,
                "price": source.price, "supply": source.supply}[key]

    def _render_sources(self, system: str = "") -> None:
        result = self._result
        if result is None or not self.alive:
            return
        key, descending = self._source_sort
        self._source_table.clear()
        self._source_table.mark_sorted(key, descending)
        self._source_rows.clear()
        self._plan_table.clear()
        self._show_plan(False)

        def add(group: List[sources.Source], prefix: str, tag: Optional[str], parent: Optional[str]) -> None:
            for index, item in enumerate(sorted(group, key=lambda s: self._source_value(s, key), reverse=descending)):
                iid = f"{prefix}{index}"
                self._source_rows[iid] = item.system
                self._source_table.insert(
                    iid, (item.station, item.system, item.kind, "Yes" if item.is_planetary else "No", item.pad,
                          f"{item.distance_ly:,.1f} ly",
                          f"{item.arrival_ls:,.0f} ls" if item.arrival_ls else "", f"{item.price:,}",
                          f"{item.supply:,}"), tag=tag, parent=parent)

        (_label, shown), = sources.filter_found([(self._result_label, result)], no_surface=bool(self._no_surface_var.get()),
                                                max_arrival_ls=self._arrival_ls(), needs=self._need_for_single(),
                                                shipyard_only=bool(self._shipyard_var.get()))
        shown_stations, shown_carriers = shown.stations, shown.carriers
        hidden = len(result.stations) + len(result.carriers) - len(shown_stations) - len(shown_carriers)
        add(shown_stations, "s", None, None)
        if shown_carriers:
            self._source_table.insert("carriers", (f"Fleet carriers ({len(shown_carriers)})", "", "", "", "", "", "", "", ""),
                                      tag="carrier", group=True, open=True)
            add(shown_carriers, "c", "carrier", "carriers")
        stations, carriers = len(shown_stations), len(shown_carriers)
        if not stations and not carriers:
            if hidden:
                self._say(f"{self._result_label}: all {hidden} found are left out by the filters (surface ports, arrival distance, stock or shipyard). Loosen them to see them.")
            else:
                self._say(f"Nothing found with {self._result_label} in stock. Try a larger radius, any landing pad size, "
                          f"or untick Exclude fleet carriers.")
            return
        extra = f" and {carriers} fleet carrier{'s' if carriers != 1 else ''}" if carriers else ""
        around = f" around {_clip(system, _NAME_MAX)}" if system else ""
        left_out = f" {hidden} left out by the filters." if hidden else ""
        where = " Your own system was searched first." if result.local else ""
        fallback = f" {result.note}" if result.note else ""
        self._say(f"{self._result_label}: {stations} station{'s' if stations != 1 else ''}{extra}{around}.{left_out}{where}{fallback} Price is per "
                  f"ton; the data is from players' own market updates, so confirm on arrival.")

    def _need_for_single(self) -> Optional[Dict[str, int]]:
        """The tons still to get of the commodity a Find nearest searched, when "Only stations with enough stock" is ticked (else None)."""
        if not self._enough_var.get():
            return None
        rows = self.host.to_buy() or []
        return {r.label: r.to_get for r in rows if r.label == self._result_label and r.to_get > 0}

    def _found_view(self) -> List[Any]:
        """The Find all answers as the commander wants to see them: without the surface ports when they are not included."""
        whole = self._whole
        if whole is None:
            return []
        return sources.filter_found(whole.found, no_surface=bool(self._no_surface_var.get()), max_arrival_ls=self._arrival_ls(),
                                    needs=self._whole_to_get if self._enough_var.get() else None, shipyard_only=bool(self._shipyard_var.get()))

    def _surface_only(self) -> frozenset:
        """The commodities still to get whose every source found is a surface port."""
        if self._whole is None:
            return frozenset()
        return frozenset(label for label in sources.surface_only_labels(self._whole.found) if self._whole_to_get.get(label))

    def _make_plan(self) -> sources.RoutePlan:
        return sources.plan_route(self._found_view(), self._whole_to_get, surface_only=self._surface_only())

    def _on_filter_change(self) -> None:
        """A filter changed (surface ports, stock or arrival distance): the lists and the route are drawn again from what was already found (nothing is asked of Spansh)."""
        try:
            self._save_prefs()
        except tk.TclError:
            return
        if self._whole is not None:
            self._plan = self._make_plan()
            self._render_whole(self._whole_system)
        elif self._result is not None:
            self._render_sources()

    def refresh_needs(self) -> None:
        """Follow what the commander has bought. The tons still to get come from the Sites window again (its Acquire figures, after the ship's
        hold and the fleet carrier), and the route is worked out again from the stations Find all already found: nothing is asked of Spansh. A
        commodity that is covered drops out of the lists and the route; one partly bought shrinks."""
        if self._whole is None or not self.alive or self._whole_job is not None:
            return
        rows = self.host.to_buy()
        if rows is None:
            return
        searched = {label for label, _result in self._whole.found}
        needs = {r.label: r.to_get for r in rows if r.to_get > 0 and r.label in searched}
        if needs == {label: tons for label, tons in self._whole_to_get.items() if tons > 0}:
            return                                  # nothing changed for the commodities searched
        self._whole_to_get = needs
        self._plan = self._make_plan()
        self._render_whole(self._whole_system, quiet=True)
        if not needs:
            self._say("Everything on the list is bought: it is in your hold or on your carrier, or delivered.")

    def _render_whole(self, system: str = "", quiet: bool = False) -> None:
        """The "Find all" answer: a heading per commodity, with its closest few stations (and carriers, if asked) below."""
        whole = self._whole
        if whole is None or not self.alive:
            return
        key, descending = self._source_sort
        self._source_table.clear()
        self._source_table.mark_sorted(key, descending)
        self._source_rows.clear()
        plan = self._plan
        include_surface = not self._no_surface_var.get()
        surface_only = sorted(self._surface_only(), key=str.casefold)
        self._plan_table.clear()
        self._show_plan(bool(plan is not None and plan.stops) or bool(surface_only))
        table = self._plan_table    # the route goes in the plan block, the commodity lists in the table below it
        if surface_only:
            # Said on the route itself: these are sold only at surface ports, none at an orbital port in range. One row each, so no name is clipped.
            table.insert("surfacenote", ("Only at surface ports" if include_surface else "Only at surface ports, so left out of the route",
                                         "", "", "", "", "", "", "", ""), group=True, open=True)
            for index, name in enumerate(surface_only):
                tons = self._whole_to_get.get(name, 0)
                table.insert(f"surfacenote{index}", (f"{name} x {tons:,} t" if tons else name, "", "", "", "", "", "", "", ""),
                             parent="surfacenote", tag="warn")
        if plan is not None and plan.stops:
            # The suggested shopping route: a stop is a row with what to buy there as rows beneath it.
            table.insert("route", ("Suggested route", f"{len(plan.stops)} stop{'s' if len(plan.stops) != 1 else ''}",
                                                f"{plan.covered:,} of {plan.needed:,} t", "", "", "", "", "", ""),
                                      group=True, open=True)
            for number, stop in enumerate(plan.stops, 1):
                stop_id = f"route{number}"
                self._source_rows[stop_id] = stop.system
                table.insert(
                    stop_id, (f"{number}. {stop.station}", stop.system, stop.kind, "Yes" if stop.is_planetary else "No", "", f"{stop.distance_ly:,.1f} ly", "", "",
                              f"{stop.tons:,} t"), group=True, open=True, parent="route", tag="carrier" if stop.is_carrier else None)
                for index, buy in enumerate(stop.buys):
                    table.insert(f"{stop_id}b{index}", (f"{buy.commodity} x {buy.tons:,} t"
                                                        + (" - surface ports only" if buy.surface_only else ""), "", "", "", "", "", "",
                                 f"{buy.price:,}", f"{buy.supply:,}" if buy.supply else ""), parent=stop_id,
                                 tag="warn" if buy.surface_only else None)
        raw_counts = {label: len(result.stations) + len(result.carriers) for label, result in whole.found}
        for g, (label, result) in enumerate(self._found_view()):
            need = self._whole_to_get.get(label)
            if not need:
                continue                            # bought (or delivered) since the search: off the list
            stations = list(result.stations[:sources.WHOLE_LIST_STATIONS])
            carriers = list(result.carriers[:sources.WHOLE_LIST_CARRIERS])
            gid = f"g{g}"
            # The label in the first column and the rest in later ones: a cell is clipped to its column, so one long heading
            # in the first would lose its end.
            self._source_table.insert(
                gid, (label, f"{need:,} t to get" if need else "",
                      "" if stations or carriers else ("surface ports only (left out)" if label in surface_only and not include_surface
                                                       else "left out by the filters" if raw_counts.get(label) else "no source found"),
                      "", "", "", "", "", ""), group=True, open=True)
            for prefix, group, tag in (("s", stations, None), ("c", carriers, "carrier")):
                for index, item in enumerate(sorted(group, key=lambda s: self._source_value(s, key), reverse=descending)):
                    iid = f"{gid}{prefix}{index}"
                    self._source_rows[iid] = item.system
                    self._source_table.insert(
                        iid, (item.station, item.system, item.kind, "Yes" if item.is_planetary else "No", item.pad,
                              f"{item.distance_ly:,.1f} ly", f"{item.arrival_ls:,.0f} ls" if item.arrival_ls else "",
                              f"{item.price:,}", f"{item.supply:,}"), tag=tag, parent=gid)
        if quiet:                                   # a refresh after a purchase leaves the note alone
            return
        around = f" around {_clip(system, _NAME_MAX)}" if system else ""
        parts = [f"Searched {len(whole.found)} commodit{'y' if len(whole.found) == 1 else 'ies'}{around}"
                 f"{' (stopped early)' if whole.stopped else ''}."]
        missing = [label for label in whole.without_sources() if label not in surface_only]
        shown_total = sum(len(result.stations) + len(result.carriers) for _label, result in self._found_view())
        left_out = sum(raw_counts.values()) - shown_total
        if left_out > 0:
            parts.append(f"{left_out} station{'s' if left_out != 1 else ''} left out by the filters.")
        if surface_only:
            parts.append(("Only at surface ports (none at an orbital port in range): " if include_surface
                          else "Only at surface ports (none at an orbital port in range), so left out of the lists and the route; untick Exclude surface ports: ")
                         + _clip(", ".join(surface_only), _ERROR_MAX) + ".")
        if missing:
            parts.append(f"No source found for {_clip(', '.join(missing), _ERROR_MAX)}; try a larger radius, any pad size "
                         f"or untick Exclude fleet carriers.")
        if whole.failed:
            parts.append(f"The search failed for {_clip(', '.join(label for label, _ in whole.failed), _ERROR_MAX)}"
                         f" - Spansh may be busy; press Find all again.")
        if plan is not None and plan.stops:
            parts.append(f"A shopping route of {len(plan.stops)} stop{'s' if len(plan.stops) != 1 else ''} covers "
                         f"{plan.covered:,} of {plan.needed:,} t (Copy Route copies it).")
            if plan.uncovered:
                parts.append("Not covered: " + _clip(", ".join(f"{label} {tons:,} t" for label, tons in plan.uncovered), _ERROR_MAX) + ".")
        parts.append(f"The closest {sources.WHOLE_LIST_STATIONS} stations are listed for each; price is per ton.")
        self._say(" ".join(parts))

    def _on_copy_route(self) -> None:
        plan = self._plan
        if plan is None or not plan.stops:
            self._say("Press Find all first; the shopping route is worked out from its answer.")
            return
        if panelkit.copy_to_clipboard(self._toplevel, "\n".join(_clip(line, 240) for line in plan.lines())):
            self._say(f"Copied the {len(plan.stops)}-stop shopping route to the clipboard.")

    def _on_source_pick(self, iid: str) -> None:
        """Clicking a result row copies its system, ready to paste into the galaxy map's search. Rows with no system (the
        commodity headings and the route's buy lines) copy nothing."""
        self._plan_table.select(None)    # one selection across the two tables
        if self._source_rows.get(iid):
            self._on_copy_system()

    def _on_plan_pick(self, iid: str) -> None:
        self._source_table.select(None)
        if self._source_rows.get(iid):
            self._on_copy_system()

    def _on_copy_system(self) -> None:
        selection = self._plan_table.selection() or self._source_table.selection()
        system = self._source_rows.get(selection[0]) if selection else None
        if not system:
            self._say("Select a result row first.")
            return
        if panelkit.copy_to_clipboard(self._toplevel, system):
            self._say(f"Copied {_clip(system, _NAME_MAX)} to the clipboard.")

    def close(self) -> None:
        if self._whole_job is not None:
            self._whole_job["cancel"] = True   # let the worker stop between commodities instead of running on
        self._search_id += 1   # a search still running has nowhere to show its answer
        try:
            self._save_prefs()
        except tk.TclError:   # the widgets are already gone
            pass
        self._shell.close()
