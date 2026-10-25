"""
The What pays window: the commodities you could surface-mine, ranked by the best price Spansh shows for them.

Opened from the Surface Mining Book. The commodities come from the commander's own records (mining_what_pays.candidates); the prices come from one Spansh station search per commodity (the
best sell price within the chosen distance of the chosen system), asked one after another on a worker thread with a short pause between them and stopped at the first failure. Opt-in: it uses
the "Enable Spansh best price finder" setting, since it asks the same service for the same kind of data, and it sends only a commodity's name, the system's name, the distance and a minimum demand (the
tons of that commodity in the hold when EDMC knows them, else 1). Fleet carriers are left out, the same way as in the price finder (`pays.NO_CARRIERS`). The table
fills in as answers arrive and is ordered best price first when it finishes; **Copy report** puts the same ranking on the clipboard. It ranks what pays, not what a body holds: the game does
not say which commodities a body carries. Built on the shared window kit (plugin/uikit). `search_stations` is a module-level name so tests can replace it.
"""
import logging
import os
import queue
import threading
import time
import tkinter as tk
from typing import Any, List, Optional, Sequence, Tuple

from config import appname, config

from . import mining_alerts
from . import mining_ground
from . import mining_hotspots as hotspots
from . import mining_location as location
from . import mining_price_finder_dialog as price_finder
from . import mining_spansh_client as spansh_client
from . import spansh_courtesy
from . import mining_what_pays as pays
from . import panelkit, system_autocomplete
from .mining_body_survey import SurveyedBody
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, FlatButton, clip
from . import mining_market_research as research

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_ENABLED = "wfmt_mining_spansh_price_finder_enabled"
"""The same switch as the price finder and Market research (Settings > Mining)."""
CONFIG_GEOMETRY = "wfmt_mining_what_pays_geometry"
DEFAULT_SIZE = (1180, 620)
MIN_SIZE = (900, 440)
POLL_MS = 200
PAUSE_S = 0.3
"""Between two requests, so the sixteen at most do not hit Spansh in a burst."""
DEFAULT_WHERE = "Within 100 ly"

search_stations = spansh_client.search_best_price_stations

_COLUMNS = (
    Column("name", "Commodity", 190, stretch=True, max_chars=40),
    Column("price", "Best price (cr)", 120, anchor="e"),
    Column("station", "Station", 200, stretch=True, max_chars=44),
    Column("system", "System", 170, max_chars=36),
    Column("distance", "Distance (ly)", 110, anchor="e"),
    Column("demand", "Demand", 90, anchor="e"),
    Column("arrival", "Arrival (ls)", 100, anchor="e"),
    Column("pads", "Pads", 130, max_chars=28),
    Column("why", "Why it is listed", 300, stretch=True, max_chars=80),
)

_HELP = (
    "This lists what you could surface-mine, from your own records, ranked by the best price a station pays for it. The game does not say which commodities a body carries, so it ranks what pays, not what a body holds.",
    ("Where it looks", "Within the distance you choose of the system in the box (your current system by default), or only in that system. Spansh answers with the best sell price among stations updated in the last 30 days. Fleet carriers are left out. Pad size and a market's age within those 30 days are not filtered: the Pads column shows the first, the best station may be one you cannot land at."),
    ("Demand", "A station must show demand of at least the tons of that commodity in your hold when EDMC knows them, otherwise at least 1 t, so a price for a few tons does not top the list."),
    ("Why it is listed", "The target commodity from Settings, a material in your saved deposits, a commodity you have recorded on the same kind of ground as the bodies scanned in your system, or one you added."),
    ("Also check", "Commodities to add, separated by commas."),
    ("Search", "Asks Spansh once for each commodity, one after another. At most 16 are priced; a failure stops the search and keeps what was found."),
    ("Copy report", "Puts the ranking on the clipboard as text."),
)

_window: Optional["WhatPaysWindow"] = None


def enabled() -> bool:
    return config.get_bool(CONFIG_ENABLED, default=False)


def table_rows(rows: Sequence[pays.Row]) -> List[Tuple[str, ...]]:
    """The table's cells for each row, best price first: a commodity no station priced shows `No station found` in the price column."""
    cells: List[Tuple[str, ...]] = []
    for row in pays.rank(rows):
        why = "; ".join(row.reasons)
        o = row.offer
        if o is None:
            cells.append((row.name, "No station found", "", "", "", "", "", "", why))
        else:
            cells.append((row.name, f"{o.price:,}", o.station, o.system, f"{o.distance_ly:,.1f}", f"{o.demand:,}", f"{o.arrival_ls:,.0f}", o.pads, why))
    return cells


def open_dialog(parent: tk.Misc, system: str, surveyed: Sequence[SurveyedBody], rates: mining_ground.OwnRates) -> None:
    """Opens the window for `system` (a box the commander can change), or raises it if it is open. `surveyed` are the landable bodies scanned in the current system and `rates` the
    commander's own rates. Parented on the caller's toplevel."""
    global _window
    if _window is not None and _window.alive:
        _window.set_inputs(system, surveyed, rates)
        _window.lift()
        return
    _window = WhatPaysWindow(parent.winfo_toplevel())
    _window.set_inputs(system, surveyed, rates)
    _window.search()


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


class WhatPaysWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self._busy = False
        self._events: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self._surveyed: Sequence[SurveyedBody] = ()
        self._rates: Optional[mining_ground.OwnRates] = None
        self._rows: List[pays.Row] = []
        self._skipped: Tuple[str, ...] = ()
        self._report = ""
        self._shell = WindowShell(
            parent, "What pays", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_help("What pays help", _HELP)
        self._shell.add_action("Copy report", self._copy_report)
        body = self._shell.body
        first = tk.Frame(body, bg=P.BG)
        first.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(first, text="Near", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._origin = tk.StringVar()
        entry = tk.Entry(first, textvariable=self._origin, width=30)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD))
        entry.bind("<Return>", lambda _e: self.search())
        system_autocomplete.attach(entry, self._origin)
        self._where = tk.StringVar(value=DEFAULT_WHERE)
        Combobox(first, textvariable=self._where, values=[name for name, _ in price_finder.WHERE_CHOICES], state="readonly", width=16).pack(side="left", padx=(0, P.PAD))
        self._search_button = FlatButton(first, "Search", self.search, kind="accent")
        self._search_button.pack(side="left")
        second = tk.Frame(body, bg=P.BG)
        second.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(second, text="Also check", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._extra = tk.StringVar()
        extra = tk.Entry(second, textvariable=self._extra, width=44)
        extra.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        extra.bind("<Return>", lambda _e: self.search())
        tk.Label(second, text="Commodities, separated by commas.", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._heading = tk.Label(body, text="Your commodities, best price first", fg=P.MUTED, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD))
        self._heading.pack(fill="x")
        self._table = DataTable(body, _COLUMNS, empty_text="Searching...")
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._shell.close()

    def _say(self, text: str) -> None:
        self._shell.set_status(text)

    def _copy_report(self) -> None:
        if not self._report:
            self._say("There is no report yet.")
            return
        ok = panelkit.copy_to_clipboard(self._shell.window, self._report)
        self._say("Copied the report." if ok else "Could not reach the clipboard.")

    def set_inputs(self, system: str, surveyed: Sequence[SurveyedBody], rates: mining_ground.OwnRates) -> None:
        self._surveyed, self._rates = surveyed, rates
        if system and not self._origin.get():
            self._origin.set(system)

    # --- the lookup ---------------------------------------------------------------------------------------------------

    def search(self) -> None:
        if self._busy or self._rates is None:
            return
        origin = self._origin.get().strip() or location.current_system() or ""
        if not origin:
            self._say("Type a system to look near, or jump or log in so WFMT knows yours.")
            return
        saved = hotspots.hotspot_repository.all()
        grounds = [g for g in (mining_ground.classify(b.planet_class, b.volcanism) for b in self._surveyed) if g]
        plan = pays.candidates(saved, grounds, self._rates, mining_alerts.primary_target(), research.split_names(self._extra.get()))
        if not plan.candidates:
            self._table.clear()
            self._report = pays.format_report(origin, self._where.get(), [], plan.skipped)
            self._say("Nothing to price yet: save a deposit, set a target commodity in Settings, or type commodities above."
                      + (f" Not a commodity Spansh knows, so left out: {', '.join(plan.skipped)}." if plan.skipped else ""))
            return
        distance, this_system = price_finder.where_arguments(self._where.get())
        self._busy = True
        self._search_button.set_enabled(False)
        self._rows, self._skipped = [], plan.skipped
        self._table.clear()
        self._shell.set_subtitle(f"Near {origin}")
        self._say(f"Pricing {len(plan.candidates)} commodit{'ies' if len(plan.candidates) != 1 else 'y'} with Spansh...")
        threading.Thread(target=self._worker, args=(origin, plan.candidates, distance, this_system), daemon=True, name="WFMT-mining-what-pays").start()
        self._shell.window.after(POLL_MS, self._poll)

    def _worker(self, origin: str, candidates: Sequence[research.Candidate], distance: Optional[float], this_system: bool) -> None:
        """Runs off the main thread: it must not touch any Tk widget."""
        total = len(candidates)
        for number, candidate in enumerate(candidates, 1):
            try:
                found = search_stations(origin, candidate.name, "Sell", distance, max_results=1, this_system_only=this_system,
                                        min_quantity=pays.minimum_for(candidate.name), **pays.NO_CARRIERS)
            except Exception as exc:
                logger.exception("Spansh price search failed for %s", candidate.name)
                if isinstance(exc, spansh_courtesy.SpanshBusy):
                    self._events.put(("failed", f"{exc} Kept what was found so far."))
                else:
                    self._events.put(("failed", f"Spansh did not answer for {candidate.name}. Check your connection and try again (see the EDMC log). Kept what was found so far."))
                return
            offer = pays.offer_from(found[0]) if found else None
            self._events.put(("row", (number, total, pays.Row(candidate.name, candidate.reasons, offer))))
            if number < total:
                time.sleep(PAUSE_S)
        self._events.put(("done", None))

    def _poll(self) -> None:
        """Runs on the main thread via after(): safe to touch widgets."""
        finished = False
        message = ""
        while True:
            try:
                kind, payload = self._events.get_nowait()
            except queue.Empty:
                break
            if kind == "row":
                number, total, row = payload
                self._rows.append(row)
                self._say(f"Priced {number} of {total}...")
                if self.alive:
                    self._table.insert(f"w{number}", table_rows([row])[0])
            elif kind == "failed":
                finished, message = True, str(payload)
            elif kind == "done":
                finished = True
        if not finished:
            if self.alive and self._busy:
                self._shell.window.after(POLL_MS, self._poll)
            return
        self._busy = False
        if not self.alive:
            return
        self._search_button.set_enabled(True)
        self._show_ranked(message)

    def _show_ranked(self, failure: str) -> None:
        self._table.clear()
        for number, cells in enumerate(table_rows(self._rows)):
            self._table.insert(f"r{number}", cells)
        origin = self._origin.get().strip() or location.current_system() or ""
        self._report = pays.format_report(origin, self._where.get(), self._rows, self._skipped)
        priced = sum(1 for r in self._rows if r.offer is not None)
        notes = [failure or f"Priced {len(self._rows)}; {priced} had a station paying for it."]
        if self._skipped:
            notes.append("Not a commodity Spansh knows, so left out: " + ", ".join(self._skipped) + ".")
        self._say(" ".join(notes))
