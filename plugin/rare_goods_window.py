"""Rare Goods Finder window for Powerplay mode: nearest rare commodities to
the current system, with each origin system's live controlling Power.

Built on the shared window kit (plugin/uikit: WindowShell + DataTable - see
docs/WINDOW_FRAMEWORK_SPEC.md); module-level show/refresh/close and saved
geometry as in powerplay_window.py.
"""

from __future__ import annotations

import logging
import os
import tkinter as tk
import webbrowser
from typing import Any, Callable, Dict, List, Optional, Tuple

from config import appname, config

from . import powerplay_control_lookup, rare_goods
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import FlatButton, NoteLabel

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_rares_window_geometry"
CONFIG_LIMIT = "wfmt_rares_limit"
CONFIG_LARGE_ONLY = "wfmt_rares_large_only"
CONFIG_MY_POWER = "wfmt_rares_my_power"

MIN_WIDTH = 1250
MIN_HEIGHT = 420
DEFAULT_SIZE = (1270, 560)
DEFAULT_LIMIT = 10
POWER_BATCH = 10                 # with the My Power filter, Spansh is asked about this many origin systems at a time, nearest first, until enough match

_window: Optional["RareGoodsWindow"] = None

Coords = Tuple[float, float, float]

# Widths sized to the bundled dataset's longest values per column (e.g.
# "Ultra-Compact Processor Prototypes", "Stefanyshyn-Piper Station").
_COLUMNS = (
    Column("rare", "Rare Good", 290, stretch=True),
    Column("system", "Origin System", 150),
    Column("distance", "Distance", 100, anchor="e"),
    Column("station", "Station", 220),
    Column("arrival", "Arrival", 100, anchor="e"),
    Column("pad", "Pad", 60, anchor="center"),
    Column("legality", "Legality", 110),
    Column("power", "Controlling Power", 170),
)


def _max_limit() -> int:
    return max(1, rare_goods.dataset_size())


def _saved_limit() -> int:
    raw = config.get_str(CONFIG_LIMIT)
    try:
        value = int(raw) if raw else DEFAULT_LIMIT
    except ValueError:
        value = DEFAULT_LIMIT
    return max(1, min(value, _max_limit()))


def show(parent: tk.Misc, current_system: Optional[str], current_coords: Optional[Coords],
         allegiance: Optional[str] = None, government: Optional[str] = None, my_power: Optional[str] = None, locate: Optional[Callable[[], Any]] = None) -> None:
    """Open the Rare Goods window, or raise it if already open. `allegiance` and `government` are the current system's, for the Legality column; `my_power` is the
    commander's pledged Power, for the My Power filter. `locate` answers *Use last known location*: (system, coordinates, allegiance, government) from the journals, or None."""
    global _window

    if _window is not None and _window.alive:
        _window.refresh(current_system, current_coords, allegiance, government, my_power)
        _window.lift()
        return

    _window = RareGoodsWindow(parent, current_system, current_coords, allegiance, government, my_power, locate)


def refresh(current_system: Optional[str], current_coords: Optional[Coords],
            allegiance: Optional[str] = None, government: Optional[str] = None, my_power: Optional[str] = None) -> None:
    if _window is not None and _window.alive:
        _window.refresh(current_system, current_coords, allegiance, government, my_power)


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


class RareGoodsWindow:
    _STATUS = "Double-click a row to open it on Inara. Select a row to see where that rare is illegal. Help explains the columns and filters."

    _HELP = (
        ("Distance", "Light years from your current system to the origin system. The list starts sorted by it; click a heading to re-sort."),
        ("Arrival", "How far the station is from the arrival star, in light seconds. Approximate."),
        ("Legality", "Community data, not yet checked in the game. “Legal” means none is listed; “Illegal here” and “Legal here” are for the system you are in."),
        ("Large pads only", "Keeps only stations with a large landing pad."),
        ("Only my Power", "Keeps origin systems that your pledged Power controls. Spansh is asked about them, nearest first."),
        ("Power column", "Looked up live from Spansh: “…” while loading, “—” if unclaimed or unreachable."),
        ("Use last known location", "Takes your commander's last position from the journals, for when the game is closed."),
    )

    def __init__(
        self, parent: tk.Misc, current_system: Optional[str], current_coords: Optional[Coords],
        allegiance: Optional[str] = None, government: Optional[str] = None, my_power: Optional[str] = None,
        locate: Optional[Callable[[], Any]] = None,
    ) -> None:
        self._locate = locate
        self._current_system = current_system
        self._current_coords = current_coords
        self._allegiance = allegiance
        self._government = government
        self._my_power = my_power
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._refresh_seq = 0
        self._id64_to_iids: Dict[int, List[str]] = {}

        self._shell = WindowShell(
            parent, "Rare Goods Finder", "", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Copy system", self._copy_selected)
        self._shell.add_action("Refresh", self._refresh_again)
        self._shell.add_action("Use last known location", self._use_last_known)
        self._shell.add_help("Rare Goods Finder help", self._HELP)

        controls = tk.Frame(self._shell.body, bg=P.BG)
        controls.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(controls, text="Show nearest:", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._limit_var = tk.StringVar(value=str(_saved_limit()))
        limit_entry = tk.Entry(controls, textvariable=self._limit_var, width=4)
        limit_entry.pack(side="left", padx=(6, 6))
        limit_entry.bind("<Return>", lambda _e: self._apply_limit())
        FlatButton(controls, "Apply", self._apply_limit).pack(side="left")
        self._large_var = tk.BooleanVar(value=config.get_str(CONFIG_LARGE_ONLY) == "1")
        self._mine_var = tk.BooleanVar(value=config.get_str(CONFIG_MY_POWER) == "1")
        check_look = dict(fg=P.TEXT, bg=P.BG, selectcolor=P.PANE, activebackground=P.BG, activeforeground=P.TEXT)
        tk.Checkbutton(controls, text="Large pads only", variable=self._large_var, command=self._apply_filters, **check_look).pack(side="left", padx=(P.PAD, 0))
        self._mine_check = tk.Checkbutton(controls, text="Only my Power", variable=self._mine_var, command=self._apply_filters, **check_look)
        self._mine_check.pack(side="left", padx=(P.PAD_SM, 0))
        self._detail = NoteLabel(self._shell.body, "Select a row for where that rare is illegal.", bg=P.BG, padx=0)
        self._detail.pack(fill="x", pady=(0, P.PAD_SM))

        self._table = DataTable(self._shell.body, _COLUMNS, on_activate=self._open_selected, on_select=self._show_detail)
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._shell.set_status(self._STATUS)

        self.refresh(current_system, current_coords, allegiance, government, my_power)

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def _limit(self) -> int:
        try:
            value = int(self._limit_var.get())
        except (ValueError, AttributeError):
            return DEFAULT_LIMIT
        return max(1, min(value, _max_limit()))

    def _apply_limit(self) -> None:
        limit = self._limit()
        self._limit_var.set(str(limit))
        config.set(CONFIG_LIMIT, str(limit))
        self._refresh_again()

    def _refresh_again(self) -> None:
        self.refresh(self._current_system, self._current_coords, self._allegiance, self._government, self._my_power)

    def _use_last_known(self) -> None:
        """Take the detected commander's last known place from the journals, for when the game is closed and nothing live says where they are."""
        place = self._locate() if self._locate else None
        if not place:
            self._shell.set_status("No earlier location was found in this commander's journals.")
            return
        system, coords, allegiance, government = place
        self.refresh(system, coords, allegiance, government, self._my_power)
        self._shell.set_subtitle(f"Last known location: {system or '(unknown)'}")
        self._shell.set_status("Using the last location in the journals; it updates when you jump or log in.")

    def _apply_filters(self) -> None:
        config.set(CONFIG_LARGE_ONLY, "1" if self._large_var.get() else "0")
        config.set(CONFIG_MY_POWER, "1" if self._mine_var.get() else "0")
        self._refresh_again()

    def refresh(self, current_system: Optional[str], current_coords: Optional[Coords],
                allegiance: Optional[str] = None, government: Optional[str] = None, my_power: Optional[str] = None) -> None:
        if not self.alive:
            return
        self._current_system = current_system
        self._current_coords = current_coords
        self._allegiance = allegiance
        self._government = government
        self._my_power = my_power
        self._entries = {}
        self._refresh_seq += 1
        seq = self._refresh_seq
        self._id64_to_iids = {}

        self._table.clear()

        if not current_coords:
            self._shell.set_subtitle("Awaiting system data…")
            self._table.insert("waiting", ("(waiting for a system jump or login; or press Use last known location)", "", "", "", "", "", "", ""))
            return

        mine = self._mine_var.get() and bool(my_power)
        self._mine_check.configure(
            text=f"Only my Power ({my_power})" if my_power else "Only my Power (not pledged or not known yet)",
            state="normal" if my_power else "disabled")
        self._shell.set_subtitle(f"Current system: {current_system or '(unknown)'}" + (f"  ·  only {my_power}" if mine else ""))

        found = rare_goods.candidates(current_coords, self._large_var.get())
        if mine:
            self._resolve_my_power(seq, found, self._limit(), str(my_power))
            return
        self._show_rows(seq, found[:self._limit()])

    def _show_rows(self, seq: int, entries: List[Dict[str, Any]]) -> None:
        """Fill the table with `entries` (already filtered, nearest first) and ask Spansh for the Power of any not yet known."""
        if seq != self._refresh_seq or not self.alive:
            return
        self._table.clear()
        self._entries = {}
        self._id64_to_iids = {}
        for entry in entries:
            iid = str(entry["inaraId"])
            self._entries[iid] = entry
            self._table.insert(iid, self._row_values(entry, self._allegiance, self._government))
            id64 = entry.get("spanshId64")
            if id64 is not None:
                self._id64_to_iids.setdefault(id64, []).append(iid)
        if not entries:
            self._table.insert("none", ("(no rare good matches the filters)", "", "", "", "", "", "", "", ""))
        powerplay_control_lookup.fetch_missing(self._id64_to_iids.keys(), self._lookup_callback(seq))

    def _resolve_my_power(self, seq: int, found: List[Dict[str, Any]], limit: int, my_power: str) -> None:
        """Walk `found` nearest first, asking Spansh (POWER_BATCH origin systems at a time) which Power controls each, until `limit` are controlled by `my_power`
        or none are left; then show those. Answers are cached for the session, so a second look costs nothing."""
        matches: List[Dict[str, Any]] = []
        unknown: List[int] = []
        for entry in found:
            id64 = entry.get("spanshId64")
            if id64 is None:
                continue
            known, power = powerplay_control_lookup.cached(id64)
            if known:
                if rare_goods.same_power(power, my_power):
                    matches.append(entry)
                    if len(matches) >= limit:
                        break
            else:
                unknown.append(id64)
                if len(unknown) >= POWER_BATCH:
                    break
        if len(matches) < limit and unknown:
            self._shell.set_status(f"Asking Spansh which Power controls each origin system, nearest first ({len(matches)} of {limit} found for {my_power} so far)…")
            waiting = set(unknown)

            def on_result(id64: int, _power: Optional[str]) -> None:
                try:
                    self._shell.window.after(0, lambda: self._batch_result(seq, waiting, id64, found, limit, my_power))
                except (tk.TclError, RuntimeError):
                    pass
            powerplay_control_lookup.fetch_missing(unknown, on_result)
            return
        self._shell.set_status(self._STATUS)
        self._show_rows(seq, matches)

    def _batch_result(self, seq: int, waiting: set, id64: int, found: List[Dict[str, Any]], limit: int, my_power: str) -> None:
        if seq != self._refresh_seq or not self.alive:
            return
        waiting.discard(id64)
        if not waiting:
            self._resolve_my_power(seq, found, limit, my_power)

    def _lookup_callback(self, seq: int) -> Callable[[int, Optional[str]], None]:
        def on_result(id64: int, power: Optional[str]) -> None:
            # Runs on the lookup's worker thread; hop to the Tk thread. The
            # window can be destroyed while lookups are still finishing, so
            # a dead toplevel is simply ignored.
            try:
                self._shell.window.after(0, lambda: self._apply_power_result(seq, id64, power))
            except (tk.TclError, RuntimeError):
                pass
        return on_result

    def _apply_power_result(self, seq: int, id64: int, power: Optional[str]) -> None:
        if seq != self._refresh_seq or not self.alive:
            return
        for iid in self._id64_to_iids.get(id64, ()):
            if self._table.exists(iid):
                self._table.set(iid, "power", power or "—")

    @staticmethod
    def _row_values(entry: Dict[str, Any], allegiance: Optional[str] = None, government: Optional[str] = None) -> tuple:
        id64 = entry.get("spanshId64")
        found, power = powerplay_control_lookup.cached(id64) if id64 is not None else (True, None)
        return (
            entry["rare"],
            entry["system"],
            rare_goods.distance_text(entry["distance_ly"]),
            entry["station"],
            rare_goods.arrival_text(entry.get("distanceToStarLs")),
            entry["pad"],
            rare_goods.legality_text(entry, allegiance, government),
            (power or "—") if found else "…",
        )

    def _show_detail(self, iid: str) -> None:
        entry = self._entries.get(iid)
        if entry is not None:
            self._detail.configure(text=f"{entry['rare']}: {rare_goods.restriction_details(entry)}.")

    def _copy_selected(self) -> None:
        """Put the selected rare's origin system on the clipboard, to paste into the galaxy map's search."""
        chosen = self._table.selection()
        entry = self._entries.get(chosen[0]) if chosen else None
        if entry is None:
            self._shell.set_status("Select a row first, then press Copy system.")
            return
        try:
            self._shell.window.clipboard_clear()
            self._shell.window.clipboard_append(entry["system"])
        except tk.TclError:
            self._shell.set_status("Could not use the clipboard.")
            return
        self._shell.set_status(f"Copied {entry['system']}. Paste it into the galaxy map's search.")

    def _open_selected(self, iid: str) -> None:
        try:
            inara_id = int(iid)
        except ValueError:
            return
        webbrowser.open(rare_goods.inara_commodity_url(inara_id))

    def close(self) -> None:
        self._shell.close()
