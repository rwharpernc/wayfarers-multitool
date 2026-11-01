"""The "Source commodities" window of the Mission mode: for each commodity your Collect, Mining and Delivery missions still need, the closest place that has it in stock,
the best nearby, the cheapest anywhere and a recommended one (see `source_picks.py`). Opened from the "Commodities needed" list.

Nothing is looked up until you press **Find sources**, and only when Trade's online-lookups switch is on (it is off by default): that is the only thing here
that goes online, a few Spansh searches per commodity. Pick a row and **Copy system** puts its system name on the clipboard for the galaxy map."""
from __future__ import annotations

import logging
import threading
import tkinter as tk
from typing import Callable, Dict, List, Optional

from . import mission_sources, panelkit, ship_current, source_picks, trade_ship
from .uikit import dialogs
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox

try:
    from config import appname, config
except ImportError:  # unit tests outside EDMC
    appname, config = "EDMarketConnector", None

logger = logging.getLogger(f"{appname}.wfmt.mission_sources")

_CFG_LOOKUPS = "wfmt_trade_lookups_enabled"          # Trade's own switch for every Spansh lookup (trade_panel.py)
_CFG_NEAR_RADIUS = "wfmt_trade_near_radius_ly"
_CFG_CARRIERS = "wfmt_trade_include_carriers"
_CFG_GROUND = "wfmt_trade_include_ground"
_CFG_SHIP_PAD = "wfmt_trade_ship_pad_override"
_CFG_GEOMETRY = "wfmt_mission_sources_geometry"
_DEFAULT_RADIUS = 100
_MODES = {"From where I am": mission_sources.HERE, "From the turn-in system": mission_sources.TURN_IN}
_POLL_MS = 400
_COLUMNS = (
    Column("commodity", "Commodity", 150, max_chars=28),
    Column("need", "Need", 70, anchor="e"),
    Column("pick", "Pick", 130),
    Column("station", "Station", 210, stretch=True, max_chars=40),
    Column("system", "System", 170, max_chars=60),
    Column("pad", "Largest pad", 90),
    Column("ly", "ly", 70, anchor="e"),
    Column("price", "cr/t", 80, anchor="e"),
    Column("note", "Note", 190, max_chars=60),
)


def lookups_enabled() -> bool:
    return bool(config and config.get_bool(_CFG_LOOKUPS, default=False))


def _radius() -> float:
    try:
        raw = config.get_str(_CFG_NEAR_RADIUS) if config else ""
        return float(max(1, min(100_000, int(raw)))) if raw else float(_DEFAULT_RADIUS)
    except (ValueError, TypeError):
        return float(_DEFAULT_RADIUS)


def read_options() -> mission_sources.Options:
    """The Trade settings the picks follow: the Near me radius, carriers, ground facilities and the landing pad (the Settings override, else the ship you are in)."""
    pad = ((config.get_str(_CFG_SHIP_PAD) if config else "") or "").strip().lower()
    if pad not in (trade_ship.SMALL, trade_ship.MEDIUM, trade_ship.LARGE):
        loadout = ship_current.latest_loadout() or {}
        pad = trade_ship.pad_size(loadout.get("Ship")) or ""
    return mission_sources.Options(
        radius_ly=_radius(), ship_pad=pad or None,
        include_carriers=bool(config.get_bool(_CFG_CARRIERS, default=True)) if config else True,
        include_ground=bool(config.get_bool(_CFG_GROUND, default=True)) if config else True)


def rows_for(need: mission_sources.Need, picks: Optional[source_picks.Picks]) -> List[List[str]]:
    """The table rows for one commodity: its name and need on the first, then one row per pick found (or why there is none). Each row is
    the nine cells followed by the system name to copy (not shown)."""
    first = [need.commodity, f"{need.tons:,} t"]
    if need.pickup is not None:
        # Delivery cargo the faction supplies: it is collected at the station that gave the mission, so there is nothing to buy.
        return [first + ["Pick up at", need.pickup or "the station that gave you the mission", "", need.pickup_pad, "", "", "Free mission cargo, no purchase", ""]]
    if picks is None:
        return [first + ["", "", "", "", "", "", "", ""]]
    rows: List[List[str]] = []
    for kind in source_picks.KINDS:
        pick = picks.picks.get(kind)
        if pick is None:
            continue
        offer = pick.offer
        lead = first if not rows else ["", ""]
        rows.append(lead + [picks.label(kind), offer.station, offer.system, offer.largest_pad or "?", f"{offer.distance_ly:.0f}", f"{offer.price:,}", pick.note, offer.system])
    if not rows:
        rows.append(first + ["", picks.notes[0] if picks.notes else "Nothing found", "", "", "", "", "", ""])
    elif picks.notes:
        rows.append(["", "", "", picks.notes[0], "", "", "", "", "", ""])
    return rows


class MissionSourcesWindow:
    def __init__(self, parent: tk.Misc, needs: Callable[[], List[mission_sources.Need]], here: Callable[[], str],
                 title: str = "WFMT - Source commodities", subtitle: str = "Where to get what your missions still need",
                 empty_text: str = "Nothing to source: no active Collect, Mining or Delivery mission still needs cargo.") -> None:
        self._needs, self._here = needs, here
        self._results: Dict[str, source_picks.Picks] = {}
        self._pending: Dict[str, source_picks.Picks] = {}
        self._worker: Optional[threading.Thread] = None
        self._cancel = threading.Event()
        self._error = ""
        self._note = ""
        self._copyable: Dict[str, str] = {}      # table row id -> the system on that row
        self._selected: Optional[str] = None
        self._shell = WindowShell(
            parent, title, subtitle, size=(1100, 520), min_size=(760, 320),
            load_geometry=lambda: (config.get_str(_CFG_GEOMETRY) if config else "") or "",
            save_geometry=lambda value: config.set(_CFG_GEOMETRY, value) if config else None)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._find = self._shell.add_action("Find sources", self._start, accent=True,
                                       tip="Find sources - look up where to get the cargo your active missions need (Spansh); press again to cancel")
        self._shell.add_action("Copy system", self._copy, tip="Copy system - copy the selected row's system for the galaxy map search")

        bar = tk.Frame(self._shell.body, bg=P.BG)
        bar.pack(fill="x", pady=(P.PAD_SM, P.PAD_SM))
        self._mode = tk.StringVar(value=next(iter(_MODES)))
        box = Combobox(bar, textvariable=self._mode, values=list(_MODES), state="readonly", width=26)
        box.pack(side="left")
        box.bind("<<ComboboxSelected>>", lambda _e: self._clear_results())
        self._table = DataTable(self._shell.body, _COLUMNS, on_select=self._select, sortable=False,
                                empty_text=empty_text)
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self.refresh()

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.lift()

    def close(self) -> None:
        self._cancel.set()
        self._shell.close()

    def refresh(self) -> None:
        """Redraw from the current missions and whatever has been found. Safe to call whenever the missions change."""
        if not self.alive:
            return
        needs = self._needs()
        self._table.clear()
        self._copyable, self._selected = {}, None
        count = 0
        for need in needs:
            for row in rows_for(need, self._results.get(need.commodity)):
                iid = f"r{count}"
                count += 1
                self._table.insert(iid, row[:9])
                if row[9:] and row[9]:
                    self._copyable[iid] = row[9]
        buying = [need for need in needs if need.pickup is None]
        if needs and not buying:
            self._shell.set_status("Your Delivery missions' cargo is picked up at the station that gave them, so there is nothing to look up.")
        elif not lookups_enabled():
            self._shell.set_status("Online lookups are off. Turn them on in Settings > Trade to find sources (it asks Spansh, spansh.co.uk).")
        elif self._error:
            self._shell.set_status(self._error)
        elif buying and not self._results and not self._busy():
            self._shell.set_status("Press Find sources. It asks Spansh a few times per commodity, one after another.")

    def _busy(self) -> bool:
        return self._worker is not None and self._worker.is_alive()

    def _clear_results(self) -> None:
        self._results, self._error = {}, ""
        self.refresh()

    def _start(self) -> None:
        if self._busy():
            self._cancel.set()
            return
        needs, here = self._needs(), self._here()
        mode = _MODES.get(self._mode.get(), mission_sources.HERE)
        note = ""
        if not needs:
            self._shell.set_status("None of your active missions needs cargo to be found (Collect and Mining missions do; a Delivery's cargo is picked up at the station that gave it).")
            return
        needs = [need for need in needs if need.pickup is None]
        if not needs:
            self._shell.set_status("Your Delivery missions' cargo is picked up at the station that gave them, so there is nothing to look up.")
            return
        if not lookups_enabled() and not self._offer_lookups():
            self.refresh()
            return
        if mode == mission_sources.HERE and not here:
            # Not even the journal names a system: measure from each commodity's turn-in system instead, and say so.
            if not any(need.turn_in for need in needs):
                self._shell.set_status("WFMT cannot tell which system you are in (no jump or login in the journal yet), and no mission names a turn-in system.")
                return
            mode = mission_sources.TURN_IN
            note = " Your system is not known yet, so this is measured from the turn-in system."
        options = read_options()
        self._cancel = cancel = threading.Event()
        self._results, self._pending, self._error = {}, {}, ""
        self._find.configure(text="Cancel")
        self._note = note
        self._shell.set_status("Asking Spansh..." + note)
        pending = self._pending

        def work() -> None:
            try:
                mission_sources.lookup(needs, mode, here, options, cancelled=cancel.is_set,
                                       on_done=lambda need, picks: pending.__setitem__(need.commodity, picks))
            except Exception:
                logger.exception("Mission source lookup failed")
                self._error = "Lookup failed - check your connection and try again (see the EDMC log)."

        self._worker = threading.Thread(target=work, name="WFMT-mission-sources", daemon=True)
        self._worker.start()
        self._shell.window.after(_POLL_MS, self._poll)

    def _offer_lookups(self) -> bool:
        """Lookups are off by default. Rather than do nothing, ask once whether to turn on the switch Settings > Trade has (the only thing that goes online here)."""
        if config is None:
            return False
        if not dialogs.confirm(self._shell.window, "Turn on online lookups?", "Finding sources asks Spansh (spansh.co.uk) for market prices, a few requests per commodity, "
                                   "only when you press Find sources.\n\nTurn on Trade's online lookups now? (The same switch as Settings > Trade; you can turn it off there.)"):
            return False
        config.set(_CFG_LOOKUPS, True)
        return True

    def _poll(self) -> None:
        if not self.alive:
            return
        self._results.update(self._pending)
        self.refresh()
        if self._busy():
            self._shell.set_status(f"Asking Spansh... {len(self._results)} of {len([n for n in self._needs() if n.pickup is None])} done (press Cancel to stop)." + self._note)
            self._shell.window.after(_POLL_MS, self._poll)
            return
        self._find.configure(text="Find sources")
        self._shell.set_status(self._error or ("Cancelled." if self._cancel.is_set() else
                                               "Done. Pick a row and press Copy system to put its system name on the clipboard.") + self._note)

    def _select(self, iid: str) -> None:
        self._selected = iid

    def _copy(self) -> None:
        system = self._copyable.get(self._selected or "", "")
        if not system:
            self._shell.set_status("Pick a row with a station first.")
        elif panelkit.copy_to_clipboard(self._shell.window, system):
            self._shell.set_status(f"Copied {system}.")


_extra: Optional[MissionSourcesWindow] = None


def show_for(parent: tk.Misc, needs: Callable[[], List[mission_sources.Need]], here: Callable[[], str],
             title: str = "WFMT - Where to buy", subtitle: str = "Where to get what you still need",
             empty_text: str = "Nothing to look up.") -> MissionSourcesWindow:
    """Open this lookup for a list of commodities that does not come from the missions (for example what an engineer asks for), or raise it and give it the new list. It is
    the same window and the same Spansh searches as Source commodities, and the same Trade tick has to be on for it to look anything up. Nothing is looked up until Find sources is pressed."""
    global _extra
    if _extra is not None and _extra.alive:
        _extra._needs, _extra._here = needs, here
        _extra._clear_results()
        _extra.refresh()
        _extra.lift()
        return _extra
    _extra = MissionSourcesWindow(parent, needs, here, title, subtitle, empty_text)
    return _extra
