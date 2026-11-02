"""Save a settings box when it is left or Return is pressed, but only if its text changed since it was entered.

A box bound straight to Return and FocusOut saved (and redrew every panel and window that listens) each time it was tabbed through, and twice when
Return was followed by leaving the box. `bind_commit` remembers the text the box held when it was entered or last saved, and calls `commit(text)`
only when the text differs. `commit` returns the text now held (a clamped number, say), which is put back into the box.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable


def bind_commit(entry: tk.Entry, var: tk.StringVar, commit: Callable[[str], str]) -> None:
    """Call `commit(var.get())` on Return or leaving `entry`, when the text is not what it held on entering it (or when last committed)."""
    state = {"start": var.get()}

    def entered(_event: object = None) -> None:
        state["start"] = var.get()

    def settle(_event: object = None) -> None:
        text = var.get()
        if text == state["start"]:
            return
        var.set(commit(text))
        state["start"] = var.get()

    entry.bind("<FocusIn>", entered, add="+")
    for event in ("<Return>", "<FocusOut>"):
        entry.bind(event, settle, add="+")
