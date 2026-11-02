"""What WFMT reports to Raven Colonial, set in the Colonization Sites window.

Two choices sit inside the master switch: *Report my construction progress and deliveries* and *Also report cargo I move to and from my fleet carrier*. They are set only here. The window draws them as a strip (`RavenStrip`) that says plainly what is on.

What stays in Settings: **the master switch** ("Allow WFMT to write to Raven Colonial") and **the key**. The master switch is the consent to send anything to a third-party site,
so it is given only where that is explained in full; the strip's two ticks are grayed out while it is off and cannot turn it on. The key is a secret; the window already asks for it
the first time a write needs it. 
The config keys live here so `colonization_window` can use them without importing `colonization_panel`, which imports the window."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, List

from config import config

from . import rcc_keys
from .uikit import palette as P
from .uikit import style
from .uikit.tooltip import add_tooltip

CFG_RCC_PROGRESS = "wfmt_rcc_share_progress"      # report depot progress and deliveries to Raven Colonial (off by default)
CFG_RCC_CARRIER = "wfmt_rcc_share_carrier"        # report fleet carrier cargo changes to Raven Colonial (off by default)

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


def master_on() -> bool:
    return rcc_keys.enabled()


def progress_chosen() -> bool:
    """The choice as saved, whether or not the master switch is on."""
    return config.get_bool(CFG_RCC_PROGRESS, default=False)


def carrier_chosen() -> bool:
    return config.get_bool(CFG_RCC_CARRIER, default=False)


def set_progress(on: bool) -> bool:
    """Save the choice (only while the master switch is on: the window cannot grant that consent). Returns what is now saved."""
    if master_on():
        config.set(CFG_RCC_PROGRESS, bool(on))
        announce()
    return progress_chosen()


def set_carrier(on: bool) -> bool:
    if master_on():
        config.set(CFG_RCC_CARRIER, bool(on))
        announce()
    return carrier_chosen()


class RavenStrip(tk.Frame):
    """A strip in the Colonization Sites window: what is reported to Raven Colonial, with the two choices as ticks."""

    def __init__(self, parent: tk.Misc, commander: Callable[[], str]) -> None:
        super().__init__(parent, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        self._commander = commander
        tk.Label(self, text="Raven Colonial", fg=P.HEADING, bg=P.CARD, font=style.font(P.FONT_BOLD)).grid(row=0, column=0, sticky="w", padx=(0, P.PAD))
        self._state = tk.Label(self, text="", fg=P.MUTED, bg=P.CARD, anchor="w", justify="left", wraplength=620)
        self._state.grid(row=0, column=1, columnspan=2, sticky="w")
        self._progress = tk.BooleanVar(value=progress_chosen())
        self._carrier = tk.BooleanVar(value=carrier_chosen())
        self._progress_box = self._tick(1, "Report my construction progress and deliveries", self._progress, set_progress,
                                        "Report progress - send the site's depot figures and your deliveries to Raven Colonial as they happen (needs your key)")
        self._carrier_box = self._tick(2, "Also report cargo I move to and from my fleet carrier", self._carrier, set_carrier,
                                       "Report carrier cargo - send cargo moves to and from your fleet carrier to Raven Colonial (needs your key)")
        self.refresh()
        add_listener(self.refresh)
        self.bind("<Destroy>", lambda _e: remove_listener(self.refresh), add="+")

    def _tick(self, row: int, label: str, var: tk.BooleanVar, setter: Callable[[bool], bool], tip: str) -> tk.Checkbutton:
        box = tk.Checkbutton(self, text=label, variable=var, bg=P.CARD, fg=P.TEXT, activebackground=P.CARD, activeforeground=P.TEXT, selectcolor=P.BUTTON,
                             highlightthickness=0, disabledforeground=P.FAINT, anchor="w", command=lambda: var.set(setter(var.get())))
        box.grid(row=row, column=1, columnspan=2, sticky="w")
        add_tooltip(box, tip)
        return box

    def refresh(self) -> None:
        """Show what is saved and say what is on. Called whenever the window refreshes, and when Settings changes."""
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        on = master_on()
        for var, held in ((self._progress, progress_chosen()), (self._carrier, carrier_chosen())):
            if var.get() != held:
                var.set(held)
        for box in (self._progress_box, self._carrier_box):
            box.configure(state=tk.NORMAL if on else tk.DISABLED)
        cmdr = self._commander()
        if not on:
            text = "Nothing is sent to Raven Colonial. Turn on the master switch in Settings → WFMT → Colonization to report."
        else:
            key = "a key is saved for this commander" if cmdr and rcc_keys.keys.get(cmdr) else "no key yet: you are asked for it when a write needs it"
            sent = [name for name, chosen in (("progress and deliveries", progress_chosen()), ("fleet carrier cargo", carrier_chosen())) if chosen]
            text = ("Reporting " + " and ".join(sent) + "; " if sent else "Writes are allowed but nothing is being reported; ") + key + "."
        self._state.configure(text=text)
