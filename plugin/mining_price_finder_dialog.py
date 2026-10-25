"""The Find Best Price window (the PRICE button on both Mining pages, and on the Trade page): the stations Spansh lists as paying the most for a commodity, or selling it the cheapest.

Type a commodity, say whether you are selling or buying, how far to look (or this system only, for goods that have to be sold inside a Powerplay system) and the system to search from (it starts
as the one you are in), then press **Search**. The results fill a table you can sort by any column: the station and its system, the price, the demand (selling) or the supply (buying), the distance
in light years, the distance from the arrival star, the largest landing pad and what kind of station it is. Double-click a row, or press **Copy system** or **Copy station**, to put a name on the
clipboard for the galaxy map. Opt-in through "Enable Spansh best price finder" in Settings; the lookup is `mining_spansh_client.search_best_price_stations`, and the only thing sent is the system
name and the commodity, when you press Search.

Fleet carriers are left out (they move and their markets go stale): the search asks Spansh for stations only, and a carrier that still came back is dropped. Pad size and the market's age are not
filtered, they are shown in the results (the pad column; Spansh is asked for markets updated in the last 30 days). **Minimum demand (t)** (Minimum supply when buying) is the least a station must
show; when selling it starts at the tons of the commodity in your hold if EDMC knows them, else 1, and a figure you type is kept.

Built on the shared window kit (plugin/uikit), like the Material trader window. The lookup runs on a worker thread and the result is picked up by an after() poll, so no widget is touched off the
main thread. `search_stations` is a module-level name so tests can replace it. Opened from either panel (`open_price_finder_dialog`); only one window is open at a time.
"""
from __future__ import annotations

import logging
import os
import queue
import threading
import tkinter as tk
from typing import Any, Dict, List, Optional, Sequence, Tuple

from config import appname, config

from . import mining_location as location
from . import mining_spansh_client as spansh_client
from . import spansh_courtesy
from .mining_names import normalize
from . import commodity_autocomplete, panelkit, system_autocomplete
from . import mining_what_pays as pays
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, FlatButton, NoteLabel, clip

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_mining_price_finder_geometry"
DEFAULT_SIZE = (1080, 600)
MIN_SIZE = (860, 440)
POLL_MS = 200
MAX_RESULTS = 25

THIS_SYSTEM = "This system only"
ANYWHERE = "Anywhere"
DEFAULT_WHERE = "Within 50 ly"
WHERE_CHOICES: Tuple[Tuple[str, Optional[float]], ...] = (
    (THIS_SYSTEM, None), ("Within 10 ly", 10.0), ("Within 25 ly", 25.0), (DEFAULT_WHERE, 50.0), ("Within 100 ly", 100.0), ("Within 250 ly", 250.0),
    ("Within 500 ly", 500.0), ("Within 1,000 ly", 1000.0), (ANYWHERE, None))
SELLING, BUYING = "I am selling", "I am buying"
search_stations = spansh_client.search_best_price_stations

_window: Optional["PriceFinderWindow"] = None

_COLUMNS = (
    Column("station", "Station", 200, stretch=True, max_chars=44),
    Column("system", "System", 170, max_chars=36),
    Column("price", "Price (cr)", 100, anchor="e"),
    Column("amount", "Demand", 90, anchor="e"),
    Column("distance", "Distance (ly)", 110, anchor="e"),
    Column("arrival", "Arrival (ls)", 100, anchor="e"),
    Column("pad", "Pad", 70),
    Column("kind", "Kind", 190, stretch=True, max_chars=44),
)


def open_price_finder_dialog(parent: tk.Misc, suggested_commodities: Optional[List[str]] = None) -> None:
    """Open the window, or raise it if it is open. Parented on the main window's toplevel: the panels rebuild their own content frames, which would take a window parented there with them."""
    global _window
    if _window is not None and _window.alive:
        _window.add_suggestions(suggested_commodities or [])
        _window.lift()
        return
    _window = PriceFinderWindow(parent.winfo_toplevel(), suggested_commodities or [])


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def where_arguments(label: str) -> Tuple[Optional[float], bool]:
    """(the furthest to look in light years, whether to look only in the search system) for a "Within" choice; 50 ly for anything unknown."""
    if label == THIS_SYSTEM:
        return None, True
    return dict(WHERE_CHOICES).get(label, 50.0), False


def largest_pad(station: spansh_client.StationPrice) -> str:
    """`Large`, `Medium` or `Small`: the biggest landing pad Spansh counts at the station; `?` when it gave no counts."""
    if station.large_pads:
        return "Large"
    if station.medium_pads:
        return "Medium"
    if station.small_pads:
        return "Small"
    return "?"


def kind_text(station: spansh_client.StationPrice) -> str:
    """`Orbital Coriolis Starport` / `Ground Planetary Outpost`: in space or on a surface, and what it is, every word capitalized the same way."""
    return normalize(f"{'ground' if station.is_planetary else 'orbital'} {(station.station_type or 'station').strip()}")


def row_values(station: spansh_client.StationPrice) -> Tuple[str, ...]:
    return (clip(station.station, 44), clip(station.system, 36), f"{station.price:,}", f"{station.quantity:,}", f"{station.distance_ly:,.1f}",
            f"{station.distance_to_arrival_ls:,.0f}", largest_pad(station), clip(kind_text(station), 44))


def heading_text(commodity: str, transaction: str, where: str, reference: str) -> str:
    verb = "pay the most for" if transaction == "Sell" else "sell the cheapest"
    place = f"in {clip(reference, 40)}" if where == THIS_SYSTEM else ("anywhere" if where == ANYWHERE else f"{where.lower()} of {clip(reference, 40)}")
    return f"Stations that {verb} {clip(commodity, 40)}, {place}"


class PriceFinderWindow:
    def __init__(self, parent: tk.Misc, suggested: Sequence[str]) -> None:
        self._busy = False
        self._results: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self._shown: Dict[str, spansh_client.StationPrice] = {}
        self._shell = WindowShell(
            parent, "Find Best Price", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Copy station", lambda: self._copy("station"))
        self._shell.add_action("Copy system", lambda: self._copy("system"))
        body = self._shell.body

        first = tk.Frame(body, bg=P.BG)
        first.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(first, text="Commodity", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._commodity = tk.StringVar()
        self._suggested: List[str] = list(suggested)
        # an entry that suggests commodity names as you type (the refined ones of this run first); Down on an empty box lists them
        self._commodity_box = tk.Entry(first, textvariable=self._commodity, width=14)
        self._commodity_box.pack(side="left", padx=(P.PAD_SM, P.PAD))
        commodity_autocomplete.attach(self._commodity_box, self._commodity, lambda: self._choices(self._suggested))
        self._transaction = tk.StringVar(value=SELLING)
        box = Combobox(first, textvariable=self._transaction, values=[SELLING, BUYING], state="readonly", width=10)
        box.pack(side="left", padx=(0, P.PAD))
        box.bind("<<ComboboxSelected>>", lambda _e: (self._set_amount_heading(), self._fill_minimum()))
        tk.Label(first, text="Where", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._where = tk.StringVar(value=DEFAULT_WHERE)
        Combobox(first, textvariable=self._where, values=[name for name, _ in WHERE_CHOICES], state="readonly", width=16).pack(side="left", padx=(P.PAD_SM, 0))
        self._minimum_label = tk.Label(first, text="Minimum demand (t)", fg=P.MUTED, bg=P.BG)
        self._minimum_label.pack(side="left", padx=(P.PAD, 0))
        self._minimum = tk.StringVar(value="1")
        self._minimum_typed = False        # the commander typed a figure: the hold stops filling it in
        minimum_box = tk.Entry(first, textvariable=self._minimum, width=9, justify="right")
        minimum_box.pack(side="left", padx=(P.PAD_SM, 0))
        minimum_box.bind("<KeyPress>", self._typed_minimum, add="+")
        self._commodity.trace_add("write", lambda *_args: self._fill_minimum())

        second = tk.Frame(body, bg=P.BG)
        second.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(second, text="Search from", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._origin = tk.StringVar(value=location.current_system() or "")
        entry = tk.Entry(second, textvariable=self._origin, width=34)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        system_autocomplete.attach(entry, self._origin)
        entry.bind("<Return>", lambda _e: self._search())
        FlatButton(second, "Here", self._fill_here).pack(side="left")
        self._search_button = FlatButton(second, "Search", self._search, kind="accent")
        self._search_button.pack(side="left", padx=(P.PAD, 0))

        self._heading = NoteLabel(body, fg=P.MUTED, bg=P.BG, font=P.FONT_BOLD, padx=0)
        self._heading.pack(fill="x", pady=(P.PAD_SM, 0))
        self._table = DataTable(body, _COLUMNS, on_activate=lambda _iid: self._copy("system"),
                                empty_text="Type a commodity and press Search.")
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._shell.set_subtitle(f"Near {self._origin.get()}" if self._origin.get() else "Waiting for your current system (jump or log in)")
        self._say("Pressing Search sends Spansh the system name, the commodity and the minimum, nothing else. Fleet carriers are left out. Click a heading to sort; double-click a row to copy its system.")
        self._shell.window.bind("<Return>", lambda _e: self._search())

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

    @staticmethod
    def _choices(suggested: Sequence[str]) -> List[str]:
        """What was refined this run first, then every commodity worth mining; typing one that is in neither is allowed."""
        first = [name for name in dict.fromkeys(suggested) if name]
        rest = [name for name in sorted(spansh_client.KNOWN_MINING_COMMODITIES) if name not in first]
        return first + rest

    def add_suggestions(self, suggested: Sequence[str]) -> None:
        if suggested:
            self._suggested = list(suggested)
        here = location.current_system()
        if here and not self._origin.get():
            self._origin.set(here)

    def _fill_here(self) -> None:
        self._origin.set(location.current_system() or "")

    def _set_amount_heading(self) -> None:
        selling = self._transaction.get() == SELLING
        self._table.set_heading("amount", "Demand" if selling else "Supply")
        self._minimum_label.configure(text="Minimum demand (t)" if selling else "Minimum supply (t)")

    def _typed_minimum(self, _event: Any) -> None:
        self._minimum_typed = True

    def _fill_minimum(self) -> None:
        """Start the minimum at the tons of this commodity in the hold when selling (1 when buying or when the hold is not known), unless a figure was typed."""
        if self._minimum_typed:
            return
        name = " ".join(self._commodity.get().split())
        self._minimum.set(str(pays.minimum_for(name)) if name and self._transaction.get() == SELLING else "1")

    # --- the lookup ---------------------------------------------------------------------------------------------------

    def _search(self) -> None:
        if self._busy:
            return
        commodity = " ".join(self._commodity.get().split())
        origin = " ".join(self._origin.get().split())
        if not commodity:
            self._say("Type a commodity to search for.")
            return
        if not origin:
            self._say("Type the system to search from, or press Here (your system is not known yet).")
            return
        minimum = pays.parse_minimum(self._minimum.get())
        if minimum is None:
            self._say(f"Type the minimum as a whole number of tons, 1 to {pays.MAX_MINIMUM:,}.")
            return
        transaction = "Sell" if self._transaction.get() == SELLING else "Buy"
        where = self._where.get()
        distance, this_system = where_arguments(where)
        self._busy = True
        self._search_button.set_enabled(False)
        self._say(f"Asking Spansh about {clip(commodity, 40)} near {clip(origin, 40)}...")
        threading.Thread(target=self._worker, args=(origin, commodity, transaction, distance, this_system, where, minimum), daemon=True,
                         name="WFMT-mining-spansh-price-search").start()
        self._shell.window.after(POLL_MS, self._poll)

    def _worker(self, origin: str, commodity: str, transaction: str, distance: Optional[float], this_system: bool, where: str, minimum: int = 1) -> None:
        """Runs off the main thread: it must not touch any Tk widget."""
        try:
            found = search_stations(origin, commodity, transaction, distance, max_results=MAX_RESULTS, this_system_only=this_system, min_quantity=minimum, **pays.NO_CARRIERS)
            self._results.put(("ok", (found, origin, commodity, transaction, where)))
        except Exception as exc:
            logger.exception("Spansh price search failed")
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
        self._fill_results(*payload)

    def _fill_results(self, found: List[spansh_client.StationPrice], origin: str, commodity: str, transaction: str, where: str) -> None:
        self._table.clear()
        self._shown = {}
        self._table.set_heading("amount", "Demand" if transaction == "Sell" else "Supply")
        self._heading.configure(text=heading_text(commodity, transaction, where, origin))
        self._shell.set_subtitle(f"Near {origin}")
        for number, station in enumerate(found):
            iid = f"p{number}"
            self._shown[iid] = station
            self._table.insert(iid, row_values(station))
        if found:
            self._say(f"{len(found)} found, best price first. Click a heading to sort; double-click a row to copy its system.")
        elif where == THIS_SYSTEM:
            self._say(f"No station in {clip(origin, 40)} has a recent market that {'buys' if transaction == 'Sell' else 'sells'} it. Try a distance.")
        else:
            self._say("Nothing found there. Try a longer distance, or check the commodity's spelling.")

    def _copy(self, what: str) -> None:
        chosen = self._table.selection()
        station = self._shown.get(chosen[0]) if chosen else None
        if station is None:
            self._say("Select a row first.")
            return
        text = station.system if what == "system" else station.station
        ok = panelkit.copy_to_clipboard(self._shell.window, text)
        self._say(f"Copied {text}." if ok else "Could not reach the clipboard.")
