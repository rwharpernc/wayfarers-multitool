"""The Where to Buy window - the closest stations (and, if asked, fleet carriers) with a commodity in stock, opened from the Colonization Sites window.

"Find nearest" searches the commodity picked in the Sites window; "Find all" searches every commodity still to be bought for the selected site (as the
Sites table lists them, covered rows left out), one request each, and lists the closest few stations under each, with the best single systems and a
suggested shopping route. The search choices are remembered between sessions. Nothing is asked of Spansh until a Find button is pressed, and only the
commodity name and the system searched around are sent.

What is searched and how the answer adds up lives in colonization_sources.py and colonization_systems.py; this file draws them. The window knows nothing
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

from . import colonization_sources as sources, colonization_systems as systems, colonization_view as view, panelkit, system_autocomplete
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
MIN_HEIGHT = 460
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
_ERROR_MAX = 90    # a failure message from outside is clipped to this
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


def follow_site(system: str) -> None:
    """The Sites window's selected site (or its system) changed; the search follows it unless the commander typed their own system."""
    if _window is not None and _window.alive:
        _window.follow_site(system)


def _credits(amount: int) -> str:
    """A basket's cost short enough for the Price column: 950 cr, 12.5K cr, 22.8M cr, 1.2B cr (blank for none)."""
    if amount <= 0:
        return ""
    for size, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if amount >= size:
            return f"{amount / size:,.1f}{suffix} cr"
    return f"{amount:,} cr"


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
        self._whole_to_get: Dict[str, int] = {}                 # commodity label -> tons still to get, for its heading
        self._plan: Optional[sources.RoutePlan] = None          # the suggested shopping route for the last "Find all"
        self._systems: Optional[systems.SystemsResult] = None   # the best single systems for the last "Find all" (each checked with Spansh)
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
        self._carriers_var = tk.BooleanVar(master=self._toplevel, value=self._prefs.carriers)
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
        FlatButton(first, "Here", self._on_here).pack(side="left", padx=(0, P.PAD))
        tk.Label(first, text="Within", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._radius = Combobox(first, state="readonly", width=9,
                                values=[f"{r} ly" for r in sources.RADIUS_CHOICES] + [_NO_LIMIT])
        self._radius.set(_NO_LIMIT if self._prefs.radius_ly is None else f"{int(self._prefs.radius_ly)} ly")
        self._radius.pack(side="left", padx=(P.PAD_SM, P.PAD))
        tk.Label(first, text="Sort", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._sort = Combobox(first, state="readonly", width=14, values=[label for label, _ in _SORT_CHOICES])
        self._sort.set(next((text for text, key in _SORT_CHOICES if key == self._prefs.sort), _SORT_CHOICES[0][0]))
        self._sort.pack(side="left", padx=(P.PAD_SM, 0))

        second = tk.Frame(options, bg=P.PANE, pady=P.PAD_SM)
        second.pack(fill="x")
        tk.Label(second, text="Landing pad", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._pad = Combobox(second, state="readonly", width=17, values=[label for _, label in sources.PAD_CHOICES])
        self._pad.set(next((text for key, text in sources.PAD_CHOICES if key == self._prefs.pad), sources.PAD_CHOICES[0][1]))
        self._pad.pack(side="left", padx=(P.PAD_SM, P.PAD))
        tk.Checkbutton(second, text="Include fleet carriers", variable=self._carriers_var).pack(side="left")
        self._find_button = FlatButton(second, "Find nearest", self._on_find, kind="accent")
        self._find_button.pack(side="right")
        self._find_all_button = FlatButton(second, "Find all", self._on_find_all)
        self._find_all_button.pack(side="right", padx=(0, 6))
        FlatButton(second, "Copy System", self._on_copy_system).pack(side="right", padx=(0, 6))
        FlatButton(second, "Copy Route", self._on_copy_route).pack(side="right", padx=(0, 6))

        self._sources_note = tk.Label(host, text=_HINT, fg=P.MUTED, bg=P.PANE, anchor="w", justify="left", padx=P.PAD)
        self._sources_note.pack(fill="x")
        host.bind("<Configure>", lambda e: [label.configure(wraplength=max(e.width - 2 * P.PAD, 100)) for label in (self._sources_note, self._picked, self._steps)])
        self._source_table = DataTable(host, _SOURCE_COLUMNS, sortable=False, on_header=self._on_source_sort,
                                       on_select=self._on_source_pick, select_groups=True, empty_text="No search yet.")
        self._source_table.tag_configure("carrier", foreground=P.INFO)
        self._source_table.pack(fill="both", expand=True)

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

    def _pad_choice(self) -> str:
        label = self._pad.get()
        return next((key for key, text in sources.PAD_CHOICES if text == label), sources.PAD_ANY)

    def _sort_choice(self) -> str:
        label = self._sort.get()
        return next((key for text, key in _SORT_CHOICES if text == label), sources.SORT_DISTANCE)

    def _save_prefs(self) -> None:
        config.set(CONFIG_SEARCH, sources.dump_prefs(sources.SearchPrefs(
            radius_ly=self._radius_ly(), pad=self._pad_choice(), carriers=bool(self._carriers_var.get()),
            sort=self._sort_choice())))

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
        carriers, order = bool(self._carriers_var.get()), self._sort_choice()
        self._save_prefs()
        self._search_id += 1
        job: Dict[str, Any] = {"id": self._search_id, "done": False, "result": None, "error": ""}
        self._find_button.set_enabled(False)
        self._say(f"Searching for {commodity} around {_clip(system, _NAME_MAX)}…", busy=True)

        def work() -> None:
            try:
                job["result"] = sources.find(system, commodity, radius_ly=radius, pad=pad,
                                             include_carriers=carriers, sort=order)
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
            self._say(f"The search failed: {_clip(job['error'], _ERROR_MAX)}. Spansh may be busy; try again shortly.")
            return
        self._result, self._result_label, self._whole, self._plan, self._systems = job["result"], commodity, None, None, None
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
        radius, pad, carriers, order = self._radius_ly(), self._pad_choice(), bool(self._carriers_var.get()), self._sort_choice()
        self._save_prefs()
        self._search_id += 1
        job: Dict[str, Any] = {"id": self._search_id, "done": False, "result": None, "error": "", "cancel": False,
                               "progress": (0, len(labels), labels[0])}
        self._whole_job = job
        self._find_button.set_enabled(False)
        self._find_all_button.configure(text="Stop")
        self._say(f"Searching for {len(labels)} commodities around {_clip(system, _NAME_MAX)}…", busy=True)

        def work() -> None:
            try:
                job["result"] = sources.find_whole_list(
                    system, labels, radius_ly=radius, pad=pad, include_carriers=carriers, sort=order,
                    progress=lambda done, total, label: job.__setitem__("progress", (done, total, label)),
                    cancelled=lambda: job["cancel"], one_stop=search_stations_selling_all, needs=to_get)
                if not job["result"].stopped:
                    job["phase"] = "systems"
                    try:   # a bonus on top of the answer above: the systems where most of the list can be bought in one place
                        job["systems"] = systems.find_best_systems(
                            job["result"].found, to_get, system, pad=pad,
                            progress=lambda done, total, label: job.__setitem__("progress", (done, total, label)),
                            cancelled=lambda: job["cancel"])
                    except Exception:
                        logger.exception("Colonization best-systems check failed")
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
            verb = "Checking system" if job.get("phase") == "systems" else "Searching"
            self._say(f"{verb} {done + 1} of {total}: {_clip(label, _NAME_MAX)}…", busy=True)
            self._toplevel.after(_POLL_MS, self._poll_whole, job, system, to_get)
            return
        self._whole_job = None
        self._find_button.set_enabled(True)
        self._find_all_button.configure(text="Find all")
        if job["error"]:
            self._say(f"The search failed: {_clip(job['error'], _ERROR_MAX)}.")
            return
        self._whole, self._whole_to_get, self._result = job["result"], to_get, None
        self._plan = sources.plan_route(job["result"].found, to_get)
        self._systems = job.get("systems")
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

        def add(group: List[sources.Source], prefix: str, tag: Optional[str], parent: Optional[str]) -> None:
            for index, item in enumerate(sorted(group, key=lambda s: self._source_value(s, key), reverse=descending)):
                iid = f"{prefix}{index}"
                self._source_rows[iid] = item.system
                self._source_table.insert(
                    iid, (item.station, item.system, item.kind, "Yes" if item.is_planetary else "No", item.pad,
                          f"{item.distance_ly:,.1f} ly",
                          f"{item.arrival_ls:,.0f} ls" if item.arrival_ls else "", f"{item.price:,}",
                          f"{item.supply:,}"), tag=tag, parent=parent)

        add(result.stations, "s", None, None)
        if result.carriers:
            self._source_table.insert("carriers", (f"Fleet carriers ({len(result.carriers)})", "", "", "", "", "", "", "", ""),
                                      tag="carrier", group=True, open=True)
            add(result.carriers, "c", "carrier", "carriers")
        stations, carriers = len(result.stations), len(result.carriers)
        if not stations and not carriers:
            self._say(f"Nothing found with {self._result_label} in stock. Try a larger radius, any landing pad size, "
                     f"or include fleet carriers.")
            return
        extra = f" and {carriers} fleet carrier{'s' if carriers != 1 else ''}" if carriers else ""
        around = f" around {_clip(system, _NAME_MAX)}" if system else ""
        self._say(f"{self._result_label}: {stations} station{'s' if stations != 1 else ''}{extra}{around}. Price is per "
                 f"ton; the data is from players' own market updates, so confirm on arrival.")

    def _render_whole(self, system: str = "") -> None:
        """The "Find all" answer: a heading per commodity, with its closest few stations (and carriers, if asked) below."""
        whole = self._whole
        if whole is None or not self.alive:
            return
        key, descending = self._source_sort
        self._source_table.clear()
        self._source_table.mark_sorted(key, descending)
        self._source_rows.clear()
        plan = self._plan
        found_systems = self._systems.plans if self._systems is not None else []
        if found_systems:
            # The best single systems first, each with its stations in the order to visit and what to buy at each; only the best is open.
            self._source_table.insert("systems", ("Best single systems", f"{len(found_systems)} checked", "", "", "", "", "", "", ""),
                                      group=True, open=True)
            for rank, found in enumerate(found_systems, 1):
                sid = f"sys{rank}"
                short = sum(tons for _label, tons in found.uncovered)
                self._source_rows[sid] = found.system
                self._source_table.insert(
                    sid, (f"{rank}. {_clip(found.system, _NAME_MAX)}", f"{found.covered:,} of {found.needed:,} t",
                          "everything" if found.complete else f"short {short:,} t", "", "",
                          f"{found.distance_ly:,.1f} ly" if found.distance_ly else "", "", _credits(found.cost), ""),
                    group=True, open=rank == 1, parent="systems")
                for number, stop in enumerate(found.stops, 1):
                    stop_id = f"{sid}s{number}"
                    self._source_rows[stop_id] = found.system
                    self._source_table.insert(
                        stop_id, (f"{number}. {stop.station}", found.system, stop.kind, "Yes" if stop.is_planetary else "No", stop.pad, "",
                                  f"{stop.arrival_ls:,.0f} ls" if stop.arrival_ls else "", "", f"{stop.tons:,} t"),
                        group=True, open=rank == 1, parent=sid)
                    for index, buy in enumerate(stop.buys):
                        self._source_table.insert(f"{stop_id}b{index}", (f"{buy.commodity} x {buy.tons:,} t", "", "", "", "", "", "",
                                                                         f"{buy.price:,}", ""), parent=stop_id)
                for index, (label, tons) in enumerate(found.uncovered):
                    self._source_table.insert(f"{sid}u{index}", (f"Short: {label} x {tons:,} t", "", "", "", "", "", "", "", ""), parent=sid)
        if plan is not None and plan.stops:
            # The suggested shopping route: a stop is a row with what to buy there as rows beneath it.
            self._source_table.insert("route", ("Suggested route", f"{len(plan.stops)} stop{'s' if len(plan.stops) != 1 else ''}",
                                                f"{plan.covered:,} of {plan.needed:,} t", "", "", "", "", "", ""),
                                      group=True, open=True)
            for number, stop in enumerate(plan.stops, 1):
                stop_id = f"route{number}"
                self._source_rows[stop_id] = stop.system
                self._source_table.insert(
                    stop_id, (f"{number}. {stop.station}", stop.system, stop.kind, "", "", f"{stop.distance_ly:,.1f} ly", "", "",
                              f"{stop.tons:,} t"), group=True, open=True, parent="route", tag="carrier" if stop.is_carrier else None)
                for index, buy in enumerate(stop.buys):
                    self._source_table.insert(f"{stop_id}b{index}", (f"{buy.commodity} x {buy.tons:,} t", "", "", "", "", "", "",
                                                                     f"{buy.price:,}", ""), parent=stop_id)
        for g, (label, result) in enumerate(whole.found):
            need = self._whole_to_get.get(label)
            stations = list(result.stations[:sources.WHOLE_LIST_STATIONS])
            carriers = list(result.carriers[:sources.WHOLE_LIST_CARRIERS])
            gid = f"g{g}"
            # The label in the first column and the rest in later ones: a cell is clipped to its column, so one long heading
            # in the first would lose its end.
            self._source_table.insert(
                gid, (label, f"{need:,} t to get" if need else "", "" if stations or carriers else "no source found",
                      "", "", "", "", "", ""), group=True, open=True)
            for prefix, group, tag in (("s", stations, None), ("c", carriers, "carrier")):
                for index, item in enumerate(sorted(group, key=lambda s: self._source_value(s, key), reverse=descending)):
                    iid = f"{gid}{prefix}{index}"
                    self._source_rows[iid] = item.system
                    self._source_table.insert(
                        iid, (item.station, item.system, item.kind, "Yes" if item.is_planetary else "No", item.pad,
                              f"{item.distance_ly:,.1f} ly", f"{item.arrival_ls:,.0f} ls" if item.arrival_ls else "",
                              f"{item.price:,}", f"{item.supply:,}"), tag=tag, parent=gid)
        around = f" around {_clip(system, _NAME_MAX)}" if system else ""
        parts = [f"Searched {len(whole.found)} commodit{'y' if len(whole.found) == 1 else 'ies'}{around}"
                 f"{' (stopped early)' if whole.stopped else ''}."]
        missing = whole.without_sources()
        if missing:
            parts.append(f"No source found for {_clip(', '.join(missing), _ERROR_MAX)}; try a larger radius, any pad size "
                         f"or include fleet carriers.")
        if whole.failed:
            parts.append(f"The search failed for {_clip(', '.join(label for label, _ in whole.failed), _ERROR_MAX)}"
                         f" - Spansh may be busy; press Find all again.")
        if self._systems is not None and self._systems.failed:
            parts.append(f"Could not check {_clip(', '.join(name for name, _ in self._systems.failed), _ERROR_MAX)} with Spansh.")
        if found_systems:
            best = found_systems[0]
            more = " Its station list may be longer than Spansh sent." if best.more_stations else ""
            parts.append((f"{best.system} has everything: {len(best.stops)} station{'s' if len(best.stops) != 1 else ''}."
                          if best.complete else
                          f"No single system covers everything; {best.system} covers the most ({best.share:.0%} of the tons).") + more)
        if plan is not None and plan.stops:
            parts.append(f"A shopping route of {len(plan.stops)} stop{'s' if len(plan.stops) != 1 else ''} covers "
                         f"{plan.covered:,} of {plan.needed:,} t (Copy Route copies it).")
            if plan.uncovered:
                parts.append("Not covered: " + _clip(", ".join(f"{label} {tons:,} t" for label, tons in plan.uncovered), _ERROR_MAX) + ".")
        parts.append(f"The closest {sources.WHOLE_LIST_STATIONS} stations are listed for each; price is per ton.")
        self._say(" ".join(parts))

    def _on_copy_route(self) -> None:
        plan = self._plan
        best = self._systems.plans[0] if self._systems is not None and self._systems.plans else None
        if (plan is None or not plan.stops) and best is None:
            self._say("Press Find all first; the shopping route is worked out from its answer.")
            return
        lines = (["Best single system:"] + best.lines() + [""]) if best is not None else []
        if plan is not None and plan.stops:
            lines += plan.lines()
        if panelkit.copy_to_clipboard(self._toplevel, "\n".join(_clip(line, 240) for line in lines)):
            what = "the best system and the shopping route" if best is not None and plan is not None and plan.stops else (
                "the best system" if best is not None else f"the {len(plan.stops)}-stop shopping route")
            self._say(f"Copied {what} to the clipboard.")

    def _on_source_pick(self, iid: str) -> None:
        """Clicking a result row copies its system, ready to paste into the galaxy map's search. Rows with no system (the
        commodity headings and the route's buy lines) copy nothing."""
        if self._source_rows.get(iid):
            self._on_copy_system()

    def _on_copy_system(self) -> None:
        selection = self._source_table.selection()
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
