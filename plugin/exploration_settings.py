"""Exploration settings that belong to a window of their own, set in that window (the Settings → WFMT → Exploration tabs say where they went).

Three small groups:

- the **Expedition** window: *Copy the next stop's system name to the clipboard every time I arrive anywhere* (also the Copy on arrival tick on the panel) and *Start the Expedition Log
  when I start an expedition*;
- the **Prediction review** window: *Keep a record of what I find, to check the prediction*, with how much is recorded and **Clear the record...**;
- the **My Codex** window: *Track codex entries*.

`TickStrip` draws a group as a strip of ticks. The panels register a listener (`add_listener`) that updates what depends on a change (the expedition panel's Copy on arrival tick, the codex panel).
What stays in Settings: Auto-Honk (it presses the fire button for you), the Boxel Survey and Region Sweep options and Exploration Value (panel sections, several of them lookups of EDSM or
Spansh), the Canonn site filters, and the Nearest place to land switch, which is already in its own window.

The config keys live here so the windows can use them without importing the panels, which import the windows."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Sequence, Tuple

from config import config

from .uikit import palette as P
from .uikit import style
from .uikit.tooltip import add_tooltip

EXPEDITION_AUTOCOPY = "wfmt_expedition_autocopy"
EXPEDITION_START_LOG = "wfmt_expedition_start_log"
EXO_OBSERVE = "wfmt_exo_observations_enabled"
CODEX_TRACK = "wfmt_codex_completionist_enabled"

DEFAULTS: Dict[str, bool] = {EXPEDITION_AUTOCOPY: False, EXPEDITION_START_LOG: True, EXO_OBSERVE: True, CODEX_TRACK: True}

# (key, label, hover tip) for each window's ticks.
EXPEDITION_FIELDS: Tuple[Tuple[str, str, str], ...] = (
    (EXPEDITION_AUTOCOPY, "Copy the next stop on every arrival",
     "Copy on arrival - copy the next stop's system name to the clipboard whenever you arrive in a system (the same tick as on the Exploration panel)"),
    (EXPEDITION_START_LOG, "Start the Expedition Log with an expedition",
     "Start the log - the expedition and its Expedition Log run start, pause and stop together"),
)
EXO_FIELDS: Tuple[Tuple[str, str, str], ...] = (
    (EXO_OBSERVE, "Keep a record of what I find, to check the prediction",
     "Keep a record - keep each sample that names a species, with the body's conditions, so the prediction can be checked here"),
)
CODEX_FIELDS: Tuple[Tuple[str, str, str], ...] = (
    (CODEX_TRACK, "Track codex entries",
     "Track codex entries - keep a personal tally of every codex entry you find, from your own journal (local, nothing is sent)"),
)

_listeners: List[Callable[[], None]] = []


def add_listener(callback: Callable[[], None]) -> None:
    if callback not in _listeners:
        _listeners.append(callback)


def remove_listener(callback: Callable[[], None]) -> None:
    if callback in _listeners:
        _listeners.remove(callback)


def announce() -> None:
    for callback in list(_listeners):
        try:
            callback()
        except Exception:        # one listener failing must not stop the others
            pass


def value(key: str) -> bool:
    return config.get_bool(key, default=DEFAULTS[key])


def set_value(key: str, on: bool) -> bool:
    """Save a tick the way Settings does and tell the listeners. Returns what is now saved."""
    if key in DEFAULTS:
        config.set(key, bool(on))
        announce()
    return value(key) if key in DEFAULTS else bool(on)


class TickStrip(tk.Frame):
    """A strip of ticks across the top of a window. `body` is a frame below them for anything extra (a count, a button)."""

    def __init__(self, parent: tk.Misc, title: str, fields: Sequence[Tuple[str, str, str]], note: str = "", inline: bool = False) -> None:
        """`inline` puts the title and the ticks on one line (for a wide window that has no height to spare); otherwise they stack."""
        super().__init__(parent, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        self._vars: Dict[str, tk.BooleanVar] = {}
        side = "left" if inline else "top"
        tk.Label(self, text=title, fg=P.HEADING, bg=P.CARD, font=style.font(P.FONT_BOLD)).pack(side=side, anchor="w", padx=(0, P.PAD) if inline else 0)
        for key, label, tip in fields:
            var = tk.BooleanVar(value=value(key))
            box = tk.Checkbutton(self, text=label, variable=var, bg=P.CARD, fg=P.TEXT, activebackground=P.CARD, activeforeground=P.TEXT, selectcolor=P.BUTTON,
                                 highlightthickness=0, anchor="w", command=lambda k=key, v=var: set_value(k, v.get()))
            box.pack(side=side, anchor="w", padx=(0, P.PAD) if inline else 0)
            add_tooltip(box, tip)
            self._vars[key] = var
        if note:
            hint = tk.Label(self, text=note, fg=P.FAINT, bg=P.CARD, font=style.font(P.FONT_SMALL), anchor="w", justify="left", wraplength=300)
            hint.pack(anchor="w", pady=(2, 0))
            self.bind("<Configure>", lambda e: hint.configure(wraplength=max(200, e.width - 2 * P.PAD - 4)), add="+")      # wraps to the strip, whatever the window's width
        self.body = tk.Frame(self, bg=P.CARD)
        self.body.pack(fill="x")
        add_listener(self.sync)
        self.bind("<Destroy>", lambda _e: remove_listener(self.sync), add="+")

    def sync(self) -> None:
        """Show what is saved (the Settings tab may have changed it)."""
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        for key, var in self._vars.items():
            held = value(key)
            if var.get() != held:
                var.set(held)
