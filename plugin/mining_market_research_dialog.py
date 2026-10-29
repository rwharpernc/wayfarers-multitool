"""
The Market Research window: which markets in a system buy what you could surface-mine there.

Opened from the Surface Mining Book. The commodities come from the commander's own records (mining_market_research.plan); the markets come from one Spansh request for the system
(mining_spansh_client.search_system_stations). Opt-in: it uses the "Enable Spansh best price finder" setting, since it asks the same service for the same kind of data, and it sends only the
system's name. The results are a table grouped by commodity (why it was looked for in the group's row, then the markets that buy it, best price first, with price, demand, how old the price
is, the distance from the star, the pads and the kind of station); **Copy report** puts the same findings on the clipboard as text. The request runs on a worker thread and is picked up by an
after() poll, so no widget is touched off the main thread. Built on the shared window kit (plugin/uikit). `search_stations` is a module-level name so tests can replace it.
"""
import logging
import os
import queue
import threading
import tkinter as tk
from typing import Any, Dict, List, Optional, Sequence, Tuple

from config import appname, config

from . import mining_ground
from . import mining_hotspots as hotspots
from . import mining_market_research as research
from . import mining_spansh_client as spansh_client
from . import spansh_courtesy
from . import panelkit
from .mining_body_survey import SurveyedBody
from .mining_names import normalize
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import FlatButton, clip

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_ENABLED = "wfmt_mining_spansh_price_finder_enabled"
"""The same switch as the price finder (Settings > Mining)."""

_BUYERS_SHOWN = 4
_MARKET_DAYS = 30
CONFIG_GEOMETRY = "wfmt_mining_market_research_geometry"
DEFAULT_SIZE = (1080, 640)
MIN_SIZE = (860, 440)
POLL_MS = 200

search_stations = spansh_client.search_system_stations

_COLUMNS = (
    Column("name", "Commodity or station", 330, stretch=True, max_chars=64),
    Column("price", "Price (cr)", 100, anchor="e"),
    Column("demand", "Demand", 90, anchor="e"),
    Column("updated", "Updated", 120),
    Column("arrival", "Arrival (ls)", 100, anchor="e"),
    Column("pads", "Pads", 120),
    Column("kind", "Kind", 200, stretch=True, max_chars=44),
)


def enabled() -> bool:
    return config.get_bool(CONFIG_ENABLED, default=False)


def format_report(system: str, results: Sequence[research.CommodityResult], plan: research.Plan,
                  station_count: int, counted: int) -> str:
    """The text the window shows (and Copy copies)."""
    lines = [f"{system}: {station_count} market{'s' if station_count != 1 else ''} with prices updated in the last "
             f"{_MARKET_DAYS} days (fleet carriers left out)."]
    if counted > spansh_client.SYSTEM_STATIONS_PAGE:
        lines.append(f"Spansh counts {counted} stations here and only the first {spansh_client.SYSTEM_STATIONS_PAGE} were asked for, "
                     "so some markets may be missing.")
    lines.append("")
    if not results:
        lines.append("Nothing to look for yet. Save a hotspot in this system, record deposits on its scanned bodies, or add "
                     "commodities in the box above.")
    for result in results:
        lines.append(f"{result.candidate.name}  ({'; '.join(result.candidate.reasons)})")
        if not result.buyers:
            lines.append("    No market in this system buys it right now.")
        for buyer in result.buyers[:_BUYERS_SHOWN]:
            bits = [f"{buyer.price:,} cr", f"demand {buyer.demand:,}"]
            age = buyer.days_old()
            if age is not None:
                bits.append("updated today" if age == 0 else f"updated {age} d ago")
            if buyer.distance_ls is not None:
                bits.append(f"{buyer.distance_ls:,.0f} ls")
            pads = research.pad_text(buyer)
            if pads:
                bits.append(pads)
            lines.append(f"    {buyer.station} ({buyer.station_type}): " + ", ".join(bits))
        if len(result.buyers) > _BUYERS_SHOWN:
            lines.append(f"    and {len(result.buyers) - _BUYERS_SHOWN} more")
        lines.append("")
    if plan.skipped:
        lines.append("Not a commodity Spansh knows, so left out: " + ", ".join(plan.skipped))
    lines.append("Built from what you have saved, not from what the bodies hold: the game does not say which commodities a "
                 "body carries. Prices are the last ones players uploaded.")
    return "\n".join(lines)


def table_rows(results: Sequence[research.CommodityResult]) -> List[Tuple[bool, Tuple[str, ...]]]:
    """The table's rows in order, as (is a commodity heading, the cells): a heading row per commodity (with why it was looked for), then a row per market that buys it (best price first, at most
    `_BUYERS_SHOWN`, then a row saying how many more), or one row saying no market buys it. Every word of a station kind is capitalized the same way."""
    rows: List[Tuple[bool, Tuple[str, ...]]] = []
    for result in results:
        rows.append((True, (clip(result.candidate.name, 64), "", "", "", "", "", clip("; ".join(result.candidate.reasons), 44))))
        if not result.buyers:
            rows.append((False, ("No market in this system buys it right now.", "", "", "", "", "", "")))
        for buyer in result.buyers[:_BUYERS_SHOWN]:
            age = buyer.days_old()
            updated = "" if age is None else ("Today" if age == 0 else f"{age} d ago")
            pads = research.pad_text(buyer)
            rows.append((False, (clip(buyer.station, 64), f"{buyer.price:,}", f"{buyer.demand:,}", updated, "" if buyer.distance_ls is None else f"{buyer.distance_ls:,.0f}",
                                 pads[:1].upper() + pads[1:], clip(normalize(f"{'ground' if buyer.is_planetary else 'orbital'} {buyer.station_type}"), 44))))
        if len(result.buyers) > _BUYERS_SHOWN:
            rows.append((False, (f"and {len(result.buyers) - _BUYERS_SHOWN} more", "", "", "", "", "", "")))
    return rows


_window: Optional["MarketResearchWindow"] = None


def open_dialog(parent: tk.Misc, system: str, surveyed: Sequence[SurveyedBody], rates: mining_ground.OwnRates) -> None:
    """Opens the window for `system`, or raises it and searches again for the new system. `surveyed` are the landable bodies scanned there this session (empty for another system) and `rates` the
    commander's own rates. Parented on the caller's toplevel."""
    global _window
    if _window is not None and _window.alive:
        _window.start(system, surveyed, rates)
        _window.lift()
        return
    _window = MarketResearchWindow(parent.winfo_toplevel())
    _window.start(system, surveyed, rates)


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


class MarketResearchWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self._busy = False
        self._results: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self._system = ""
        self._surveyed: Sequence[SurveyedBody] = ()
        self._rates: Optional[mining_ground.OwnRates] = None
        self._report = ""
        self._shell = WindowShell(
            parent, "Market Research", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Copy report", self._copy_report, tip="Copy report - copy the findings as text to the clipboard")
        body = self._shell.body
        row = tk.Frame(body, bg=P.BG)
        row.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(row, text="Also check", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._extra = tk.StringVar()
        entry = tk.Entry(row, textvariable=self._extra, width=44)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        entry.bind("<Return>", lambda _e: self.search())
        self._search_button = FlatButton(row, "Search", self.search, kind="accent", tip="Search - find markets that buy what you could mine here (Spansh)")
        self._search_button.pack(side="left")
        tk.Label(row, text="Commodities, separated by commas.", fg=P.MUTED, bg=P.BG).pack(side="left", padx=(P.PAD, 0))
        self._heading = tk.Label(body, text="", fg=P.MUTED, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD))
        self._heading.pack(fill="x")
        self._table = DataTable(body, _COLUMNS, sortable=False, empty_text="Searching...")
        self._table.tag_configure("note", foreground=P.MUTED)
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

    # --- the lookup ---------------------------------------------------------------------------------------------------

    def start(self, system: str, surveyed: Sequence[SurveyedBody], rates: mining_ground.OwnRates) -> None:
        self._system, self._surveyed, self._rates = system, surveyed, rates
        self._heading.configure(text=f"Markets in {clip(system, 40)} that buy what you could mine there")
        self._shell.set_subtitle(system)
        self.search()

    def search(self) -> None:
        if self._busy or not self._system or self._rates is None:
            return
        saved = hotspots.hotspot_repository.all()
        grounds = [g for g in (mining_ground.classify(b.planet_class, b.volcanism) for b in self._surveyed) if g]
        plan = research.plan(self._system, saved, grounds, self._rates, research.split_names(self._extra.get()))
        self._busy = True
        self._search_button.set_enabled(False)
        self._say("Asking Spansh for the markets in this system...")
        threading.Thread(target=self._worker, args=(self._system, plan), daemon=True, name="WFMT-mining-market-research").start()
        self._shell.window.after(POLL_MS, self._poll)

    def _worker(self, system: str, plan: research.Plan) -> None:
        """Runs off the main thread: it must not touch any Tk widget."""
        try:
            stations, counted = search_stations(system, _MARKET_DAYS)
            self._results.put(("ok", (system, plan, stations, counted)))
        except Exception as exc:
            logger.exception("Spansh system market search failed")
            self._results.put(("failed", str(exc) if isinstance(exc, spansh_courtesy.SpanshBusy) else "The search failed. Check your connection and try again (see the EDMC log)."))

    def _poll(self) -> None:
        """Runs on the main thread via after(): safe to touch widgets."""
        try:
            outcome, payload = self._results.get_nowait()
        except queue.Empty:
            if self.alive and self._busy:
                self._shell.window.after(POLL_MS, self._poll)
            return
        self._busy = False
        if not self.alive:
            return
        self._search_button.set_enabled(True)
        if outcome != "ok":
            self._say(str(payload))
            return
        self._fill(*payload)

    def _fill(self, system: str, plan: research.Plan, stations: list, counted: int) -> None:
        results = research.match(plan.candidates, stations)
        self._report = format_report(system, results, plan, len(stations), counted)
        self._table.clear()
        group = ""
        for number, (is_group, cells) in enumerate(table_rows(results)):
            iid = f"m{number}"
            if is_group:
                group = iid
                self._table.insert(iid, cells, group=True)
            else:
                self._table.insert(iid, cells, parent=group or None, tag="note" if not cells[1] else None)
        notes = [f"{len(stations)} market{'s' if len(stations) != 1 else ''} with prices updated in the last {_MARKET_DAYS} days (fleet carriers left out)."]
        if counted > spansh_client.SYSTEM_STATIONS_PAGE:
            notes.append(f"Spansh counts {counted} stations here and only the first {spansh_client.SYSTEM_STATIONS_PAGE} were asked for, so some markets may be missing.")
        if not results:
            notes.append("Nothing to look for yet: save a hotspot in this system, record deposits on its scanned bodies, or type commodities above.")
        if plan.skipped:
            notes.append("Not a commodity Spansh knows, so left out: " + ", ".join(plan.skipped) + ".")
        self._say(" ".join(notes))
