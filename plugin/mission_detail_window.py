"""The Mission description window: everything WFMT knows about one mission, opened by clicking a mission's card in the Mission types window.

It joins three sources: the Missions window's `Row` (progress, hand-in place, time left), the mission's summary (cargo and pickup details) and the
journal's own MissionAccepted record (target, influence, reputation, passengers and the rest). Fields the journal wrote that have no label here are
listed under "Other journal fields", so nothing the game said about the mission is hidden. It reads local data only and opens nothing online.
The window stays live: `refresh()` redraws it, and it says so when the mission is handed in or ends."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from . import missions_board, panelkit
from .missions_overlay import time_left
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.widgets import ScrollFrame

try:
    from config import config
except ImportError:  # unit tests outside EDMC
    config = None

_CFG_GEOMETRY = "wfmt_mission_detail_window_geometry"
_TICK_MS = 30_000
_MAX_VALUE = 400     # a journal value longer than this is cut, so one odd field cannot swell the window
_NAME_WIDTH = 190

Section = Tuple[str, List[Tuple[str, str]]]

# Journal keys shown under a label of their own; the rest go under "Other journal fields".
_LABELLED = {
    "event", "timestamp", "MissionID", "Name", "LocalisedName", "Faction", "Reward", "Wing", "Expiry", "DestinationSystem", "DestinationStation",
    "DestinationSettlement", "Commodity", "Commodity_Localised", "Count", "Target", "Target_Localised", "TargetType", "TargetType_Localised",
    "TargetFaction", "KillCount", "PassengerCount", "PassengerType", "PassengerVIPs", "PassengerWanted", "Influence", "Reputation", "Donation",
    "DonationCommodity", "Description", "LocalisedDescription"}


def _text(value: Any) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(v) for v in value)
    if isinstance(value, dict):
        return ", ".join(f"{k}: {_text(v)}" for k, v in value.items())
    text = str(value).strip()
    return text if len(text) <= _MAX_VALUE else text[:_MAX_VALUE - 1] + "…"


def _add(pairs: List[Tuple[str, str]], label: str, value: Any) -> None:
    """Add a pair unless the journal left the field out or empty."""
    if value in (None, "", [], {}):
        return
    pairs.append((label, _text(value)))


def sections(row: missions_board.Row, summary: Any, event: Optional[Mapping[str, Any]], now: datetime) -> List[Section]:
    """The window's content: titled groups of label and value pairs for one mission. `summary` is the `MissionSummary` (or None), `event` the journal's
    MissionAccepted record (or None when it is not known)."""
    event = event or {}
    out: List[Section] = [("Overview", missions_board.detail(row, now))]

    objective: List[Tuple[str, str]] = []
    _add(objective, "Description", event.get("LocalisedDescription") or event.get("Description"))
    target = event.get("Target_Localised") or event.get("Target")
    _add(objective, "Target", target)
    _add(objective, "Target type", event.get("TargetType_Localised") or event.get("TargetType"))
    _add(objective, "Target faction", event.get("TargetFaction"))
    if event.get("KillCount"):
        _add(objective, "Kills required", f"{int(event['KillCount']):,}")
    _add(objective, "Commodity", event.get("Commodity_Localised") or event.get("Commodity"))
    if event.get("Count") and (event.get("Commodity") or event.get("Commodity_Localised")):
        _add(objective, "Units", f"{int(event['Count']):,}")
    if event.get("PassengerCount"):
        _add(objective, "Passengers", f"{int(event['PassengerCount']):,}" + (f" ({event['PassengerType']})" if event.get("PassengerType") else ""))
        _add(objective, "VIPs", event.get("PassengerVIPs"))
        _add(objective, "Wanted", event.get("PassengerWanted"))
    _add(objective, "Destination system", event.get("DestinationSystem"))
    _add(objective, "Destination station", event.get("DestinationStation"))
    _add(objective, "Destination settlement", event.get("DestinationSettlement"))
    if objective:
        out.append(("Objective", objective))

    cargo: List[Tuple[str, str]] = []
    if summary is not None:
        _add(cargo, "Cargo progress", row.cargo_note)
        if summary.pickup_commodity:
            _add(cargo, "Still to pick up", f"{summary.pickup_count:,} t of {summary.pickup_commodity}")
            _add(cargo, "Pick up at", summary.pickup_station)
            _add(cargo, "Largest pad there", summary.pickup_pad)
        if summary.needed_commodity:
            _add(cargo, "Still to find", f"{summary.needed_commodity_count:,} t of {summary.needed_commodity}")
    if cargo:
        out.append(("Cargo", cargo))

    standing: List[Tuple[str, str]] = []
    _add(standing, "Reward", f"{row.reward:,} cr" if row.reward else "")
    _add(standing, "Donation", f"{int(event['Donation']):,} cr" if str(event.get("Donation", "")).isdigit() else event.get("Donation"))
    _add(standing, "Commodity reward", event.get("DonationCommodity"))
    _add(standing, "Influence gained", event.get("Influence"))
    _add(standing, "Reputation gained", event.get("Reputation"))
    if standing:
        out.append(("Reward and standing", standing))

    ids: List[Tuple[str, str]] = []
    _add(ids, "Mission ID", event.get("MissionID") or row.id)
    _add(ids, "Journal name", event.get("Name"))
    if ids:
        out.append(("Journal", ids))

    other = [(key, _text(value)) for key, value in event.items() if key not in _LABELLED and value not in (None, "", [], {})]
    if other:
        out.append(("Other journal fields", sorted(other)))
    return out


class MissionDetailWindow:
    def __init__(self, parent: tk.Misc, mission_id: int, rows: Callable[[], List[missions_board.Row]], lookup: Callable[[int], Tuple[Any, Optional[Mapping[str, Any]]]],
                 on_close: Callable[["MissionDetailWindow"], None] = lambda _w: None) -> None:
        self.mission_id = mission_id
        self._rows, self._lookup, self._on_close = rows, lookup, on_close
        self._signature: Any = None
        self._shell = WindowShell(
            parent, "WFMT - Mission description", "", size=(720, 640), min_size=(480, 360),
            load_geometry=lambda: (config.get_str(_CFG_GEOMETRY) if config else "") or "",
            save_geometry=lambda value: config.set(_CFG_GEOMETRY, value) if config else None)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Copy system", self._copy_system, tip="Copy system - copy the destination system for the galaxy map search")
        self._shell.add_action("Copy details", self._copy_details, tip="Copy details - copy everything shown here as plain text")
        self._scroll = ScrollFrame(self._shell.body, bg=P.PANE)
        self._scroll.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._scroll.body.columnconfigure(0, weight=1)
        self._content: List[Section] = []
        self._row: Optional[missions_board.Row] = None
        self.refresh()
        self._tick()

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()
        self._shell.window.focus_force()

    def close(self) -> None:
        self._shell.close()
        self._on_close(self)

    def _tick(self) -> None:
        if not self.alive:
            return
        self.refresh()
        if self.alive:
            self._shell.window.after(_TICK_MS, self._tick)

    def show(self, mission_id: int) -> None:
        """Switch the window to another mission."""
        self.mission_id = mission_id
        self._signature = None
        self.refresh()

    def refresh(self) -> None:
        if not self.alive:
            return
        now = datetime.now(timezone.utc)
        row = next((r for r in self._rows() if r.id == self.mission_id), None)
        if row is None:
            self._row, self._content = None, []
            self._shell.set_subtitle("This mission is no longer active (handed in, failed or abandoned).")
            if self._signature != "gone":
                self._signature = "gone"
                self._scroll.clear()
            return
        summary, event = self._lookup(self.mission_id)
        self._row, self._content = row, sections(row, summary, event, now)
        self._shell.set_subtitle(f"{row.title} - {time_left(row.expiry, now) or 'no time limit'} left" if row.expiry else row.title)
        if self._signature != self._content:
            self._signature = self._content
            self._draw()

    def _draw(self) -> None:
        where = self._scroll.position()
        self._scroll.clear()
        body, line = self._scroll.body, 0
        for title, pairs in self._content:
            tk.Label(body, text=title, fg=P.TITLE, bg=P.PANE, anchor="w", font=style.font((P.FONT_BODY[0], "bold"))).grid(
                row=line, column=0, sticky="ew", padx=P.PAD, pady=(P.PAD, 2))
            line += 1
            for name, value in pairs:
                entry = tk.Frame(body, bg=P.PANE)
                entry.grid(row=line, column=0, sticky="ew", padx=P.PAD)
                entry.columnconfigure(1, weight=1)
                tk.Label(entry, text=name, fg=P.MUTED, bg=P.PANE, anchor="nw", justify="left", width=0, wraplength=_NAME_WIDTH).grid(
                    row=0, column=0, sticky="nw", padx=(0, P.PAD))
                label = tk.Label(entry, text=value, fg=P.TEXT, bg=P.PANE, anchor="w", justify="left", wraplength=420)
                label.grid(row=0, column=1, sticky="ew")
                entry.bind("<Configure>", lambda e, lab=label: lab.configure(wraplength=max(e.width - _NAME_WIDTH - 3 * P.PAD, 150)))
                line += 1
        self._scroll.restore_position(where)

    def _plain_text(self) -> str:
        lines: List[str] = []
        for title, pairs in self._content:
            lines.append(title.upper())
            lines.extend(f"{name}: {value}" for name, value in pairs)
            lines.append("")
        return "\n".join(lines).strip()

    def _copy_system(self) -> None:
        if self._row is None or not self._row.system:
            self._shell.set_status("This mission has no destination system.")
        elif panelkit.copy_to_clipboard(self._shell.window, self._row.system):
            self._shell.set_status(f"Copied {self._row.system}.", ok=True)

    def _copy_details(self) -> None:
        if self._content and panelkit.copy_to_clipboard(self._shell.window, self._plain_text()):
            self._shell.set_status("Copied the mission details.", ok=True)
