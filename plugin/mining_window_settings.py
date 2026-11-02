"""Mining's display and tuning settings, set in the Space Mining and Surface Mining windows (and nowhere else: the Settings → WFMT → Mining tab says where they went).

The windows build a **Settings** card from `FIELDS` below, each box or
tick saves at once (a box when you press Enter or click away), and the panel and every open window redraw. The panel registers a listener that also updates the Settings tab's
own variables (`add_listener`). The opt-in lookups (the switches that let WFMT ask Spansh or EDSM) stay in Settings only: they are permissions, not display choices.

The config keys live here (the panel imports them), so this module needs nothing from the panel and the live window can use it without a circular import."""
from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Tuple

from config import config

from . import commodity_autocomplete, mining_alerts, mining_depletion as depletion, mining_spansh_client, mining_stops, mining_targets
from . import mining_hotspots as hotspots
from . import mining_pages
from .uikit import palette as P
from .uikit import style
from .uikit.tooltip import add_tooltip

CFG_DISPLAY_SESSION_TOTALS = "wfmt_mining_display_session_totals"
CFG_DISPLAY_CARGO_BAR = "wfmt_mining_display_cargo_bar"
CFG_DISPLAY_PROSPECTOR_HINTS = "wfmt_mining_display_prospector_hints"
CFG_DISPLAY_COVERAGE_MINIMAP = "wfmt_mining_display_coverage_minimap"
CFG_STOP_RADIUS = "wfmt_mining_stop_radius_m"
CFG_RIG_GAP = "wfmt_mining_rig_gap_m"
CFG_REFILL_DAYS = "wfmt_mining_refill_days"

BOTH, SPACE, SURFACE = "both", mining_pages.SPACE_MINING, mining_pages.SURFACE_MINING

# (page it appears on, label, key, kind, default, hover tip). kind: "bool", or "int" (clamped by the function named in _CLAMPS).
FIELDS: Tuple[tuple, ...] = (
    (BOTH, "Show session totals", CFG_DISPLAY_SESSION_TOTALS, "bool", True, "Session totals - the refined totals, the rate and the time to a full hold on the panel and in this window"),
    (BOTH, "Show the cargo bar", CFG_DISPLAY_CARGO_BAR, "bool", True, "Cargo bar - the hold line (used, capacity and what is in it)"),
    (BOTH, "Show prospector hints", CFG_DISPLAY_PROSPECTOR_HINTS, "bool", True, "Prospector hints - the asteroids prospected, the last rock, cores and limpets (Space Mining) and the last DSS scan (Surface Mining)"),
    (SURFACE, "Show coverage minimap", CFG_DISPLAY_COVERAGE_MINIMAP, "bool", False, "Coverage minimap - a small map of the ground the Rhino has driven over on this body, redrawn once a second"),
    (SURFACE, "Stop radius (m, 500 to 2500)", CFG_STOP_RADIUS, "int", mining_stops.DEFAULT_RADIUS_M,
     "Stop radius - deposits within this distance of the one with the most rigs count as one Rhino stop (steps of 250)"),
    (SURFACE, "Too close for another rig (m, 0 = off)", CFG_RIG_GAP, "int", 0,
     "Rig gap - how close the game lets two rigs be; measure it with Mark center and Mark border. 0 turns the check off"),
    (SURFACE, "Deposit refills after (days, 0 = unknown)", CFG_REFILL_DAYS, "int", 0,
     "Refill time - assume a depleted deposit has refilled after this many days; 0 leaves a Depleted mark until you change it"),
)

_listeners: List[Callable[[], None]] = []


def add_listener(callback: Callable[[], None]) -> None:
    """`callback()` runs after any value here changes, from a window (the panel redraws and updates its Settings tab)."""
    if callback not in _listeners:
        _listeners.append(callback)


def _remove_listener(callback: Callable[[], None]) -> None:
    if callback in _listeners:
        _listeners.remove(callback)


def clamp_refill_days(value: object) -> int:
    try:
        return min(depletion.MAX_REGEN_DAYS, max(0, int(round(float(value)))))   # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _clamped(key: str, value: object) -> int:
    if key == CFG_STOP_RADIUS:
        return mining_stops.clamp_radius(value)
    if key == CFG_RIG_GAP:
        return mining_stops.clamp_rig_gap(value)
    return clamp_refill_days(value)


def value(key: str) -> Any:
    """What a field holds now: a bool, or the number as text."""
    for _page, _label, name, kind, default, _tip in FIELDS:
        if name == key:
            if kind == "bool":
                return config.get_bool(name, default=default)
            return str(_clamped(name, config.get_int(name, default=default)))
    return ""


def set_value(key: str, new: Any) -> Any:
    """Save a field the way Settings does and return what is now held. Listeners hear of it."""
    for _page, _label, name, kind, _default, _tip in FIELDS:
        if name != key:
            continue
        if kind == "bool":
            config.set(name, bool(new))
        else:
            config.set(name, _clamped(name, new))
        if name == CFG_REFILL_DAYS:
            hotspots.hotspot_repository.refill_days = clamp_refill_days(config.get_int(name, default=0))
        _announce()
        return value(name)
    return new


def target_text() -> Tuple[str, int]:
    return mining_alerts.load_target()


def set_target(text: str, percent: object) -> Tuple[str, int]:
    """Save the target commodities and the default percentage (the same two values Settings holds)."""
    config.set(mining_alerts.CFG_TARGET, " ".join(str(text).split()))
    config.set(mining_alerts.CFG_TARGET_PERCENT, str(mining_alerts.clamp(percent, *mining_alerts.TARGET_PERCENT_RANGE, mining_alerts.DEFAULT_TARGET_PERCENT)))
    _announce()
    return mining_alerts.load_target()


def target_status(text: str, percent: object) -> Tuple[str, bool]:
    """(the line under the target box, whether it is a problem): what is wrong with what is typed, else how many targets it holds."""
    clean = mining_alerts.clamp(percent, *mining_alerts.TARGET_PERCENT_RANGE, mining_alerts.DEFAULT_TARGET_PERCENT)
    parsed = mining_targets.parse_targets(text, clean)
    if parsed.problems:
        return " ".join(parsed.problems[:3]), True
    return (f"{len(parsed.targets)} target{'s' if len(parsed.targets) != 1 else ''} set." if parsed.targets else ""), False


def _announce() -> None:
    for callback in list(_listeners):
        try:
            callback()
        except Exception:        # one listener failing must not stop the others
            pass


class SettingsCard(tk.Frame):
    """The Settings card of a mining window. `page` is SPACE or SURFACE; `on_change()` redraws the window it sits in."""

    def __init__(self, parent: tk.Misc, page: str, on_change: Optional[Callable[[], None]] = None) -> None:
        super().__init__(parent, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        self._page = page
        self._on_change = on_change
        self._vars: Dict[str, Tuple[tk.Variable, Optional[tk.Entry]]] = {}
        self._target_var = tk.StringVar()
        self._percent_var = tk.StringVar()
        self._target_entry: Optional[tk.Entry] = None
        self._status: Optional[tk.Label] = None
        self._build()
        self.sync()
        add_listener(self._changed)
        self.bind("<Destroy>", lambda _e: _remove_listener(self._changed), add="+")

    def _build(self) -> None:
        tk.Label(self, text="Settings", fg=P.HEADING, bg=P.CARD, font=style.font(P.FONT_BOLD)).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))
        ticks = tk.Frame(self, bg=P.CARD)
        ticks.grid(row=1, column=0, columnspan=4, sticky="w")
        row, column = 2, 0
        tick_count = 0
        for page, label, key, kind, _default, tip in FIELDS:
            if page not in (BOTH, self._page):
                continue
            if kind == "bool":
                var = tk.BooleanVar(value=bool(value(key)))
                box = tk.Checkbutton(ticks, text=label, variable=var, bg=P.CARD, fg=P.TEXT, activebackground=P.CARD, activeforeground=P.TEXT,
                                     selectcolor=P.BUTTON, highlightthickness=0, command=lambda k=key, v=var: set_value(k, v.get()))
                box.grid(row=tick_count // 2, column=tick_count % 2, sticky="w", padx=(0, P.PAD))       # two to a line, so the card never gets wider than a narrow window
                tick_count += 1
                add_tooltip(box, tip)
                self._vars[key] = (var, None)
                continue
            text = tk.StringVar(value=str(value(key)))
            tk.Label(self, text=label, fg=P.MUTED, bg=P.CARD).grid(row=row, column=column * 2, sticky="w", padx=(0, P.PAD_SM), pady=2)
            entry = tk.Entry(self, textvariable=text, width=7)
            entry.grid(row=row, column=column * 2 + 1, sticky="w", padx=(0, P.PAD * 2), pady=2)
            add_tooltip(entry, tip)
            for event in ("<Return>", "<FocusOut>"):
                entry.bind(event, lambda _e, k=key, v=text: v.set(set_value(k, v.get())), add="+")
            self._vars[key] = (text, entry)
            column += 1
            if column == 2:
                column, row = 0, row + 1
        if column:
            row += 1
        if self._page == SPACE:
            self._build_targets(row)

    def _build_targets(self, row: int) -> None:
        tk.Label(self, text="Target commodities", fg=P.MUTED, bg=P.CARD).grid(row=row, column=0, sticky="w", padx=(0, P.PAD_SM), pady=(6, 0))
        self._target_entry = tk.Entry(self, textvariable=self._target_var, width=26)
        self._target_entry.grid(row=row, column=1, columnspan=3, sticky="w", pady=(6, 0))
        line = tk.Frame(self, bg=P.CARD)
        line.grid(row=row + 1, column=0, columnspan=4, sticky="w")
        row += 1
        # The type-ahead follows the item being typed (after the last comma) and replaces only that item.
        commodity_autocomplete.attach(self._target_entry, mining_targets.LastItemVar(self._target_var), lambda: mining_spansh_client.KNOWN_MINING_COMMODITIES)
        tk.Label(line, text="worth cracking at", fg=P.MUTED, bg=P.CARD).pack(side="left", padx=(0, P.PAD_SM))
        percent = tk.Entry(line, textvariable=self._percent_var, width=4)
        percent.pack(side="left")
        tk.Label(line, text="% or more", fg=P.MUTED, bg=P.CARD).pack(side="left", padx=(P.PAD_SM, 0))
        add_tooltip(self._target_entry, "Target commodities - name what you mine for (Painite, or Painite 30, Platinum 25); the panel marks a rock that holds at least that much of one")
        add_tooltip(percent, "Worth cracking at - the percentage a name with no number of its own must reach (1 to 100)")
        for widget in (self._target_entry, percent):
            for event in ("<Return>", "<FocusOut>"):
                widget.bind(event, lambda _e: self._save_target(), add="+")
        self._status = tk.Label(self, text="", fg=P.OK, bg=P.CARD, anchor="w", font=style.font(P.FONT_SMALL))
        self._status.grid(row=row + 1, column=0, columnspan=4, sticky="w")
        self._target_var.trace_add("write", lambda *_a: self._show_status())
        self._percent_var.trace_add("write", lambda *_a: self._show_status())

    def _save_target(self) -> None:
        text, percent = set_target(self._target_var.get(), self._percent_var.get())
        self._target_var.set(text)
        self._percent_var.set(str(percent))

    def _show_status(self) -> None:
        if self._status is None:
            return
        text, problem = target_status(self._target_var.get(), self._percent_var.get())
        try:
            self._status.configure(text=text, fg=P.WARN if problem else P.OK)
        except tk.TclError:
            pass

    def sync(self) -> None:
        """Show what is saved (the Settings tab, or another window, may have changed it), leaving a box alone while it is being typed in."""
        try:
            if not self.winfo_exists():
                return
            focused = self.focus_get()
        except (tk.TclError, KeyError):
            focused = None
        for key, (var, entry) in self._vars.items():
            if entry is not None and entry is focused:
                continue
            held = value(key)
            if var.get() != held:
                var.set(held)
        if self._page == SPACE and self._target_entry is not None:
            text, percent = target_text()
            if self._target_entry is not focused and self._target_var.get() != text:
                self._target_var.set(text)
            if str(percent) != self._percent_var.get() and focused is not self._target_entry:
                self._percent_var.set(str(percent))
            self._show_status()

    def _changed(self) -> None:
        """Something changed (here, in another window, or in Settings): show it, and redraw the window this card is in."""
        self.sync()
        if self._on_change is not None:
            try:
                self._on_change()
            except tk.TclError:
                pass
