"""Themed message boxes and a one-line prompt, in place of the operating
system's own `tkinter.messagebox` / `tkinter.simpledialog` (those ignore WFMT's
look and differ between Windows and Linux).

    confirm(parent, title, message, yes="Yes", no="No", default_yes=True) -> bool
    choose(parent, title, message, choices, default=0, cancel_value=None) -> Optional[str]
    prompt(parent, title, message, initial="", ok="OK") -> Optional[str]
    info / warning / error(parent, title, message) -> None

Every dialog is modal over `parent` (transient, grab, waits until closed) and
centered over it, or over the screen when `parent` is None. Esc or closing the
window cancels (`confirm` -> False, `choose` -> `cancel_value`, `prompt` ->
None); Enter presses the default button. The text column is capped at
MAX_WIDTH pixels and wraps there, and a very long message scrolls inside a
fixed-size box, so a dialog never grows with its text and never widens the
window it sits over. If Tk cannot create the window, the call returns its
cancel value (False / `cancel_value` / None) instead of raising.

Tests answer without a GUI: `set_test_responder(fn)` makes every call return
`fn(kind, title, message, **kwargs)` at once, without opening a window (`kind`
is "confirm", "choose", "prompt", "info", "warning" or "error"; `kwargs` are the
remaining arguments, never `parent`). `set_test_responder(None)` restores the
real windows. `answers(confirm=True, ...)` builds a responder from fixed
answers (a value, or a callable taking title and message) that raises
`UnansweredDialog` for any kind it was not given, so a test never blocks on a
dialog it did not expect."""
from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Optional, Sequence

from . import palette as P
from . import style
from .widgets import FlatButton, SlimScrollbar, clip

MAX_WIDTH = 480          # hard cap, in pixels, on the message column
_SCROLL_CHARS = 1500     # a longer message scrolls instead of growing the window
_SCROLL_LINES = 22
_SCROLL_HEIGHT = 220     # pixels, the scroll box's fixed height
_MAX_CHARS = 20000       # anything past this is cut with an ellipsis
_BUTTON_CHARS = 18       # longest button caption shown (the full label is still returned)
_ENTRY_CHARS = 44

_MARKERS = {
    "confirm": ("?", "ACCENT"), "choose": ("?", "ACCENT"), "prompt": ("?", "ACCENT"),    # palette token names, read when drawn
    "info": ("i", "INFO"), "warning": ("!", "WARN"), "error": ("x", "DANGER"),
}

_responder: Optional[Callable[..., Any]] = None


class UnansweredDialog(AssertionError):
    """A dialog opened under `answers()` for a kind the test gave no answer for."""


def set_test_responder(fn: Optional[Callable[..., Any]]) -> None:
    """Route every dialog call to `fn(kind, title, message, **kwargs)` (see the module docstring); None restores the real windows."""
    global _responder
    _responder = fn


def answers(**by_kind: Any) -> Callable[..., Any]:
    """A responder from fixed answers per kind; each is a value or a callable taking (title, message)."""
    def respond(kind: str, title: str, message: str, **_kwargs: Any) -> Any:
        if kind not in by_kind:
            raise UnansweredDialog(f"unexpected {kind} dialog {title!r}: {message[:80]!r}")
        value = by_kind[kind]
        return value(title, message) if callable(value) else value
    return respond


def confirm(parent: Optional[tk.Misc], title: str, message: str, yes: str = "Yes", no: str = "No",
            default_yes: bool = True) -> bool:
    if _responder is not None:
        return bool(_responder("confirm", title, message, yes=yes, no=no, default_yes=default_yes))
    return _run(parent, "confirm", title, message, [yes, no], 0 if default_yes else 1, None) == 0


def choose(parent: Optional[tk.Misc], title: str, message: str, choices: Sequence[str], default: int = 0,
           cancel_value: Optional[str] = None) -> Optional[str]:
    if _responder is not None:
        return _responder("choose", title, message, choices=list(choices), default=default, cancel_value=cancel_value)
    picked = _run(parent, "choose", title, message, list(choices), default, None)
    return cancel_value if picked is None else list(choices)[picked]


def prompt(parent: Optional[tk.Misc], title: str, message: str, initial: str = "", ok: str = "OK", show: str = "") -> Optional[str]:
    """`show` hides what is typed ("*") for a key or password."""
    if _responder is not None:
        return _responder("prompt", title, message, initial=initial, ok=ok, show=show)
    typed: list[str] = []
    picked = _run(parent, "prompt", title, message, [ok], 0, initial, typed, show)
    return typed[0] if picked is not None and typed else None


def info(parent: Optional[tk.Misc], title: str, message: str) -> None:
    _simple(parent, "info", title, message)


def warning(parent: Optional[tk.Misc], title: str, message: str) -> None:
    _simple(parent, "warning", title, message)


def error(parent: Optional[tk.Misc], title: str, message: str) -> None:
    _simple(parent, "error", title, message)


def _simple(parent: Optional[tk.Misc], kind: str, title: str, message: str) -> None:
    if _responder is not None:
        _responder(kind, title, message)
        return
    _run(parent, kind, title, message, ["OK"], 0, None)


def _run(parent: Optional[tk.Misc], kind: str, title: str, message: str, labels: list[str], default: int,
         initial: Optional[str], typed: Optional[list[str]] = None, show: str = "") -> Optional[int]:
    """Build, show and wait for one dialog. Returns the index of the pressed button, or None when cancelled or when no window could be made.
    A prompt's text is appended to `typed`."""
    try:
        owner = parent if parent is not None else tk._default_root
        if owner is None or not labels:
            return None
        return _show(owner, kind, title, message, labels, default, initial, typed if typed is not None else [], show)
    except tk.TclError:
        return None


def _show(owner: tk.Misc, kind: str, title: str, message: str, labels: list[str], default: int,
          initial: Optional[str], typed: list[str], show: str = "") -> Optional[int]:
    default = default if 0 <= default < len(labels) else 0
    message = str(message)
    if len(message) > _MAX_CHARS:
        message = message[:_MAX_CHARS - 1] + "…"
    top = owner.winfo_toplevel()
    window = tk.Toplevel(owner)
    window.withdraw()            # shown once built and centered, so it never flashes at a corner
    result: list[Optional[int]] = [None]
    try:
        style.skin(window)
        window.title(title)
        window.configure(bg=P.BG)
        window.resizable(False, False)
        entry: Optional[tk.Entry] = None

        def finish(index: Optional[int]) -> None:
            if index is not None and entry is not None:
                typed.append(entry.get())
            result[0] = index
            window.destroy()

        body = tk.Frame(window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD * 2)
        body.pack(fill="x")
        glyph, color_name = _MARKERS[kind]
        color = getattr(P, color_name)
        tk.Label(body, text=glyph, fg=color, bg=P.BG, width=2, anchor="n",
                 font=style.font(P.FONT_TITLE)).pack(side="left", anchor="n", padx=(0, P.PAD))
        text_column = tk.Frame(body, bg=P.BG)
        text_column.pack(side="left", anchor="n")
        if len(message) > _SCROLL_CHARS or message.count("\n") > _SCROLL_LINES:
            _scroll_box(text_column, message)
        else:
            tk.Label(text_column, text=message, fg=P.TEXT, bg=P.BG, justify="left", anchor="w",
                     wraplength=MAX_WIDTH).pack(anchor="w")
        if initial is not None:
            entry = tk.Entry(text_column, width=_ENTRY_CHARS, show=show)
            entry.insert(0, initial)
            entry.pack(anchor="w", fill="x", pady=(P.PAD, 0))

        row = tk.Frame(window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD)
        row.pack(fill="x")
        buttons: dict[int, FlatButton] = {}
        for index in reversed(range(len(labels))):
            if len(labels) == 1:
                what = "close this message"
            elif index == default:
                what = "go ahead"
            else:
                what = "close this without going ahead"
            button = FlatButton(row, clip(labels[index], _BUTTON_CHARS), lambda i=index: finish(i),
                                kind="accent" if index == default else "normal", tip=f"{clip(labels[index], _BUTTON_CHARS)} - {what}")
            button.pack(side="right", padx=(P.PAD_SM, 0))
            buttons[index] = button

        window.bind("<Escape>", lambda _e: finish(None))
        window.bind("<Return>", lambda _e: finish(default))
        window.protocol("WM_DELETE_WINDOW", lambda: finish(None))

        _center(window, top)
        try:
            if top.winfo_viewable():
                window.transient(top)
        except tk.TclError:
            pass
        window.deiconify()
        window.lift()
        style.grab_when_visible(window)
        if entry is not None:
            entry.focus_set()
            entry.select_range(0, "end")
        else:
            buttons[default].focus_set()
    except tk.TclError:
        try:
            window.destroy()
        except tk.TclError:
            pass
        return None
    try:
        window.wait_window()
    except tk.TclError:
        pass
    return result[0]


def _scroll_box(parent: tk.Misc, message: str) -> None:
    """A fixed-size, read-only, scrolling view of a long message (its size is set here, never by the text)."""
    holder = tk.Frame(parent, bg=P.BG, width=MAX_WIDTH, height=_SCROLL_HEIGHT)
    holder.pack(anchor="w")
    holder.pack_propagate(False)
    text = tk.Text(holder, wrap="word", bg=P.BG, fg=P.TEXT, relief="flat", borderwidth=0,
                   highlightthickness=0, width=1, height=1)
    bar = SlimScrollbar(holder, command=text.yview)
    text.configure(yscrollcommand=bar.set)
    bar.pack(side="right", fill="y")
    text.pack(side="left", fill="both", expand=True)
    text.insert("1.0", message)
    text.configure(state="disabled")


def _center(window: tk.Toplevel, top: tk.Misc) -> None:
    """Size the window to its content (never past the screen) and center it over `top`, or over the screen if `top` is not showing."""
    window.update_idletasks()
    screen_w, screen_h = window.winfo_screenwidth(), window.winfo_screenheight()
    width = min(window.winfo_reqwidth(), screen_w - 40)
    height = min(window.winfo_reqheight(), screen_h - 80)
    try:
        showing = bool(top.winfo_viewable())
    except tk.TclError:
        showing = False
    if showing:
        x = top.winfo_rootx() + (top.winfo_width() - width) // 2
        y = top.winfo_rooty() + (top.winfo_height() - height) // 2
    else:
        x, y = (screen_w - width) // 2, (screen_h - height) // 3
    x = max(0, min(x, screen_w - width))
    y = max(0, min(y, screen_h - height))
    window.geometry(f"{width}x{height}+{x}+{y}")
