"""Keeps the smoke tests' windows from taking focus while someone is working at the computer. Each smoke script imports this first.

A real Tk window that is mapped takes the foreground on Windows, so a test run interrupts typing. Every Tk and Toplevel is disabled on Windows, which stops it being
given the focus, and focus_force does nothing. The windows may still flash on screen (making them transparent as well made the whole suite more than twice as slow),
but they cannot take the keyboard. Widgets still work: tests drive them with invoke(), update() and events.
"""
from __future__ import annotations

import sys
import tkinter as tk


def _quiet(window: tk.Misc) -> None:
    if sys.platform != "win32":
        return
    try:
        window.attributes("-disabled", True)
    except tk.TclError:
        pass


def _patch(cls: type) -> None:
    original = cls.__init__

    def init(self, *args, **kwargs):
        original(self, *args, **kwargs)
        _quiet(self)

    cls.__init__ = init


_patch(tk.Tk)
_patch(tk.Toplevel)
tk.Misc.focus_force = lambda self: None          # type: ignore[assignment]
