"""The tooltip every WFMT button uses, on the main panel and in the windows: a small popup next to the widget after the pointer rests on it.
It needs only Tk, so the window kit can use it without the EDMC modules the main panel imports (`panelkit` re-exports it)."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Union

TOOLTIP_DELAY_MS = 500
TOOLTIP_WRAP = 280


def add_tooltip(widget: tk.Widget, text: Union[str, Callable[[], str]]) -> None:
    """Shows `text` in a small popup next to `widget` after the pointer rests on
    it for TOOLTIP_DELAY_MS, and hides it on leave/click. The popup is its own
    borderless top-level window, so it never affects the size of EDMC's main
    window; fixed light colors keep it legible under every EDMC theme. `text` may be a
    function returning the text, read each time the popup opens, for a button whose
    meaning changes with its label."""
    state = {"after": None, "tip": None}
    widget._has_tooltip = True      # read by the window-fit test, which fails a window button that has none

    def hide(_event: object = None) -> None:
        if state["after"] is not None:
            widget.after_cancel(state["after"])
            state["after"] = None
        if state["tip"] is not None:
            state["tip"].destroy()
            state["tip"] = None

    def show() -> None:
        state["after"] = None
        try:
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.wm_geometry(f"+{widget.winfo_rootx() + 8}+{widget.winfo_rooty() + widget.winfo_height() + 4}")
            shown = text() if callable(text) else text
            if not shown:
                tip.destroy()
                return
            tk.Label(
                tip, text=shown, justify=tk.LEFT, wraplength=TOOLTIP_WRAP, background="#ffffe0",
                foreground="#000000", relief=tk.SOLID, borderwidth=1, padx=4, pady=2,
            ).pack()
            state["tip"] = tip
        except tk.TclError:
            state["tip"] = None

    def schedule(_event: object = None) -> None:
        hide()
        state["after"] = widget.after(TOOLTIP_DELAY_MS, show)

    widget.bind("<Enter>", schedule, add="+")
    widget.bind("<Leave>", hide, add="+")
    widget.bind("<ButtonPress>", hide, add="+")
    widget.bind("<Destroy>", hide, add="+")
