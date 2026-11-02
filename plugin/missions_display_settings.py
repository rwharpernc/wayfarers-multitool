"""Missions' six display switches, set in the Mission types window as well as in Settings → WFMT → Missions.

Both places read and write the same saved values, so a change in either shows in the other: the window builds a **Display** card from `FIELDS`, each tick saves at
once, and the panel and the open window redraw. `missions.py` registers a listener (`add_listener`) that applies the new values to the panel and updates the Settings tab's own
variables. The config keys live here so `missions_types_window` can use them without importing `missions` (which imports the panel, which imports that window)."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

from config import config

from .uikit import palette as P
from .uikit import style
from .uikit.tooltip import add_tooltip

CFG_REMAINING = "wfmt_missions_show_remaining_column"
CFG_PROGRESS = "wfmt_missions_display_progress"
CFG_TOTALS = "wfmt_missions_show_totals_row"
CFG_MISSION_COUNT = "wfmt_missions_show_mission_count"
CFG_SETTLEMENT = "wfmt_missions_display_settlement"
CFG_COMMODITIES_NEEDED = "wfmt_missions_display_commodities_needed"

# (config key, the name the Settings tab keeps its variable under, label, hover tip); every one starts on.
FIELDS: Tuple[Tuple[str, str, str, str], ...] = (
    (CFG_PROGRESS, "display_progress", "Show kill progress", "Kill progress - done/required kills, with a bar, on the massacre and settlement raid pages"),
    (CFG_REMAINING, "show_remaining_column", "Show remaining-kills column", "Remaining kills - how many more kills the biggest stack needs than each other stack"),
    (CFG_TOTALS, "show_totals_row", "Show totals row", "Totals row - the biggest stack with the total reward, when more than one faction has a stack"),
    (CFG_MISSION_COUNT, "show_mission_count", "Show mission count", "Mission count - the Missions: N/20 line at the top of the panel"),
    (CFG_SETTLEMENT, "display_settlement", "Show target settlement (ground missions)", "Target settlement - the ground targets under the settlement raid stacks"),
    (CFG_COMMODITIES_NEEDED, "display_commodities_needed", "Show commodities needed (trade and mining)", "Commodities needed - the total of each commodity your trade and mining missions still need"),
)

_listeners: List[Callable[[], None]] = []


def add_listener(callback: Callable[[], None]) -> None:
    """`callback()` runs after a switch is changed from a window."""
    if callback not in _listeners:
        _listeners.append(callback)


def _remove_listener(callback: Callable[[], None]) -> None:
    if callback in _listeners:
        _listeners.remove(callback)


def value(key: str) -> bool:
    return config.get_bool(key, default=True)


def set_value(key: str, new: bool) -> bool:
    """Save a switch and tell the listeners (the panel redraws, the Settings tab follows). Returns what is now held."""
    config.set(key, bool(new))
    for callback in list(_listeners):
        try:
            callback()
        except Exception:        # one listener failing must not stop the others
            pass
    return value(key)


class DisplayCard(tk.Frame):
    """The Display card of the Mission types window. `on_change()` redraws the window it sits in."""

    def __init__(self, parent: tk.Misc, on_change: Optional[Callable[[], None]] = None) -> None:
        super().__init__(parent, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        self._on_change = on_change
        self._vars: Dict[str, tk.BooleanVar] = {}
        tk.Label(self, text="Display", fg=P.HEADING, bg=P.CARD, font=style.font(P.FONT_BOLD)).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        for number, (key, _name, label, tip) in enumerate(FIELDS):
            var = tk.BooleanVar(value=value(key))
            box = tk.Checkbutton(self, text=label, variable=var, bg=P.CARD, fg=P.TEXT, activebackground=P.CARD, activeforeground=P.TEXT,
                                 selectcolor=P.BUTTON, highlightthickness=0, anchor="w", command=lambda k=key, v=var: set_value(k, v.get()))
            box.grid(row=1 + number // 2, column=number % 2, sticky="w", padx=(0, P.PAD))      # two to a line, so the card never gets wider than a narrow window
            add_tooltip(box, tip)
            self._vars[key] = var
        add_listener(self._changed)
        self.bind("<Destroy>", lambda _e: _remove_listener(self._changed), add="+")

    def sync(self) -> None:
        """Show what is saved (the Settings tab may have changed it)."""
        for key, var in self._vars.items():
            held = value(key)
            if var.get() != held:
                var.set(held)

    def _changed(self) -> None:
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        self.sync()
        if self._on_change is not None:
            try:
                self._on_change()
            except tk.TclError:
                pass
