"""BGS's display and tuning settings, set in the BGS Report window (the Settings → WFMT → BGS tab keeps tick detection and says where the rest went). The window builds a **Settings** card (`SettingsCard`): the switch that
shows faction states and activity, and how many days of closed ticks to keep. `bgs_panel` registers a listener (`add_listener`) that applies a change (prunes the archive,
saves, redraws) and updates the Settings tab's own variables. Tick detection, the one network call BGS makes, stays in Settings only: it is a permission.

The config keys and their readers live here so `bgs_window` can use them without importing `bgs_panel`, which imports the window."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional

from config import config

from .uikit import palette as P
from .uikit import style
from .uikit.tooltip import add_tooltip

CFG_ENABLED = "wfmt_bgs_enabled"
CFG_TICK_ENABLED = "wfmt_bgs_tick_enabled"
CFG_ARCHIVE_DAYS = "wfmt_bgs_archive_days"
DEFAULT_ARCHIVE_DAYS = 7
MAX_ARCHIVE_DAYS = 90

_listeners: List[Callable[[], None]] = []


def add_listener(callback: Callable[[], None]) -> None:
    if callback not in _listeners:
        _listeners.append(callback)


def _remove_listener(callback: Callable[[], None]) -> None:
    if callback in _listeners:
        _listeners.remove(callback)


def enabled() -> bool:
    # On by default - pure journal parsing, no network calls.
    return config.get_bool(CFG_ENABLED, default=True)


def tick_enabled() -> bool:
    """Gates the one network call this mode makes (the tick-time poll), separate from `enabled()` so faction-state tracking can stay fully local."""
    return config.get_bool(CFG_TICK_ENABLED, default=True)


def archive_days() -> int:
    """How many days of closed ticks to keep (Settings), clamped to 1-90."""
    try:
        value = int(config.get_str(CFG_ARCHIVE_DAYS) or DEFAULT_ARCHIVE_DAYS)
    except ValueError:
        value = DEFAULT_ARCHIVE_DAYS
    return max(1, min(MAX_ARCHIVE_DAYS, value))


def _announce() -> None:
    for callback in list(_listeners):
        try:
            callback()
        except Exception:        # one listener failing must not stop the others
            pass


def set_enabled(new: bool) -> bool:
    config.set(CFG_ENABLED, bool(new))
    _announce()
    return enabled()


def set_archive_days(text: object) -> str:
    """Save the days to keep (kept inside 1 to 90; anything unreadable is the default) and return what is now held, as the box shows it."""
    try:
        days = int(str(text).strip())
    except ValueError:
        days = DEFAULT_ARCHIVE_DAYS
    config.set(CFG_ARCHIVE_DAYS, str(max(1, min(MAX_ARCHIVE_DAYS, days))))
    _announce()
    return str(archive_days())


class SettingsCard(tk.Frame):
    """The Settings card of the BGS Report window."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        tk.Label(self, text="Settings", fg=P.HEADING, bg=P.CARD, font=style.font(P.FONT_BOLD)).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))
        self._shown = tk.BooleanVar(value=enabled())
        box = tk.Checkbutton(self, text="Show BGS faction states and activity", variable=self._shown, bg=P.CARD, fg=P.TEXT, activebackground=P.CARD,
                             activeforeground=P.TEXT, selectcolor=P.BUTTON, highlightthickness=0, command=lambda: set_enabled(self._shown.get()))
        box.grid(row=1, column=0, columnspan=2, sticky="w", padx=(0, P.PAD))
        add_tooltip(box, "Show BGS states and activity - the BGS panel and this report; off, BGS tracks nothing")
        tk.Label(self, text=f"Keep previous ticks for (days, 1 to {MAX_ARCHIVE_DAYS})", fg=P.MUTED, bg=P.CARD).grid(row=1, column=2, sticky="w", padx=(P.PAD, P.PAD_SM))
        self._days = tk.StringVar(value=str(archive_days()))
        self._entry = tk.Entry(self, textvariable=self._days, width=5)
        self._entry.grid(row=1, column=3, sticky="w")
        add_tooltip(self._entry, "Keep previous ticks - how many days of closed ticks the report keeps (1 to 90)")
        for event in ("<Return>", "<FocusOut>"):
            self._entry.bind(event, lambda _e: self._days.set(set_archive_days(self._days.get())), add="+")
        tk.Label(self, text="Tick detection (the one lookup BGS makes) is switched on or off in Settings → WFMT → BGS.", fg=P.FAINT, bg=P.CARD,
                 font=style.font(P.FONT_SMALL), anchor="w").grid(row=2, column=0, columnspan=4, sticky="w", pady=(4, 0))
        add_listener(self.sync)
        self.bind("<Destroy>", lambda _e: _remove_listener(self.sync), add="+")

    def sync(self) -> None:
        """Show what is saved (the Settings tab may have changed it), leaving the box alone while it is being typed in."""
        try:
            if not self.winfo_exists():
                return
            focused = self.focus_get()
        except (tk.TclError, KeyError):
            focused = None
        if self._shown.get() != enabled():
            self._shown.set(enabled())
        if focused is not self._entry and self._days.get() != str(archive_days()):
            self._days.set(str(archive_days()))
