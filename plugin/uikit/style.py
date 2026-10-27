"""Fonts and per-window skinning for WFMT windows.

Deliberately touches NOTHING global: ttk themes and ttk styles are
application-wide, so `theme_use()` or restyling "TButton"/"Treeview" here
would recolor EDMC's own main window and every other plugin. Instead the
kit uses classic tk widgets (plus the few custom ones in widgets.py -
FlatButton, Combobox, SlimScrollbar) and `skin()` colors a window's classic
widgets through Tk's option database, scoped by that window's own unique
name."""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from typing import Callable

from . import palette as P

_fonts: dict[tuple, tkfont.Font] = {}
_fixed_fonts: dict[tuple, tkfont.Font] = {}   # fonts that ignore the text size setting

# How many points larger (or smaller) every WFMT window's text is than the system default; one setting for all of them. The window
# headers (A- and A+) and Settings -> General -> Window change it.
TEXT_DELTA_MIN = -2
TEXT_DELTA_MAX = 6
_text_delta = 0
_text_listeners: list[Callable[[], None]] = []


def _size_for(spec: tuple[int, str], scaled: bool = True) -> int:
    base = tkfont.nametofont("TkDefaultFont")
    size = base.cget("size")
    step = spec[0] + (_text_delta if scaled else 0)
    if size > 0:
        return max(6, size + step)
    return -max(8, -size + step)   # negative = pixels


def font(spec: tuple[int, str] = P.FONT_BODY, scaled: bool = True) -> tkfont.Font:
    """(size delta, weight) -> a cached Font based on TkDefaultFont, grown or shrunk by the text size setting. `scaled=False` gives a
    font that ignores the setting, for small boxes (the stat tiles, the status chips) that must stay the same size."""
    cache = _fonts if scaled else _fixed_fonts
    if spec not in cache:
        base = tkfont.nametofont("TkDefaultFont")
        cache[spec] = tkfont.Font(family=base.cget("family"), size=_size_for(spec, scaled), weight=spec[1])
    return cache[spec]


def text_delta() -> int:
    return _text_delta


def set_text_delta(delta: int) -> None:
    """Sets the text size of every WFMT window at once. The cached fonts are resized in place, so open windows follow, and the
    listeners (tables, which must measure their columns again) are told."""
    global _text_delta
    delta = max(TEXT_DELTA_MIN, min(TEXT_DELTA_MAX, int(delta)))
    if delta == _text_delta:
        return
    _text_delta = delta
    for spec, face in list(_fonts.items()):
        try:
            face.configure(size=_size_for(spec))
        except tk.TclError:
            del _fonts[spec]       # its Tk application is gone (only a test makes a second one)
    for listener in list(_text_listeners):
        listener()


def add_text_listener(listener: Callable[[], None]) -> Callable[[], None]:
    """Calls `listener` whenever the text size changes; returns the function that stops it."""
    _text_listeners.append(listener)

    def remove() -> None:
        if listener in _text_listeners:
            _text_listeners.remove(listener)
    return remove


def dpi_factor(widget: tk.Misc) -> float:
    """How much bigger than the 96-dpi baseline text is on this display
    (Tk's pixels-per-point scaling over 96/72), never below 1. Window default
    and minimum sizes are written in baseline pixels and multiplied by this,
    so a 150%/200% display doesn't clip a layout that fits at 100%."""
    try:
        return max(1.0, float(widget.tk.call("tk", "scaling")) / (96 / 72))
    except (tk.TclError, ValueError):
        return 1.0


def _skin_options() -> dict[str, dict[str, object]]:
    """The option-database values for each classic widget class, from the theme in use now."""
    return {
        "Frame": {"background": P.PANE},
        "Label": {"background": P.PANE, "foreground": P.TEXT},
        "Message": {"background": P.PANE, "foreground": P.TEXT},
        "Button": {"background": P.BUTTON, "foreground": P.TEXT, "activebackground": P.HOVER,
                   "activeforeground": P.TEXT, "relief": "flat", "borderwidth": 0,
                   "highlightthickness": 0, "padx": 12, "pady": 5, "cursor": "hand2"},
        "Entry": {"background": P.CARD, "foreground": P.TEXT, "insertBackground": P.TEXT,
                  "relief": "flat", "highlightThickness": 1, "highlightBackground": P.LINE,
                  "highlightColor": P.ACCENT, "selectBackground": P.SELECT, "selectForeground": P.TEXT,
                  "disabledBackground": P.PANE, "disabledForeground": P.FAINT,
                  "readonlyBackground": P.CARD},
        "Text": {"background": P.CARD, "foreground": P.TEXT, "insertBackground": P.TEXT,
                 "relief": "flat", "highlightThickness": 1, "highlightBackground": P.LINE,
                 "highlightColor": P.ACCENT, "selectBackground": P.SELECT, "selectForeground": P.TEXT},
        "Listbox": {"background": P.CARD, "foreground": P.TEXT, "selectBackground": P.SELECT,
                    "selectForeground": P.TEXT, "relief": "flat", "highlightThickness": 1,
                    "highlightBackground": P.LINE, "highlightColor": P.ACCENT, "activestyle": "none"},
        "Checkbutton": {"background": P.PANE, "foreground": P.TEXT, "activebackground": P.PANE,
                        "activeforeground": P.TEXT, "selectColor": P.CARD, "highlightThickness": 0},
        "Radiobutton": {"background": P.PANE, "foreground": P.TEXT, "activebackground": P.PANE,
                        "activeforeground": P.TEXT, "selectColor": P.CARD, "highlightThickness": 0},
        "Canvas": {"background": P.PANE, "highlightThickness": 0},
    }


def skin(window: tk.Misc) -> None:
    """Gives a Toplevel (and every classic tk widget later created inside
    it) WFMT's look without touching the code that builds it. Call right
    after creating the Toplevel and before adding widgets; explicit
    fg=/bg= arguments in the building code still win (status colors).

    Option patterns match widget *names* (a full ".!toplevel3" path would be
    read as an application name), so each is scoped by this window's own
    unique name, loosely bound to everything beneath it - nothing outside
    the window, EDMC's main window included, is affected."""
    window.configure(background=P.PANE)
    _skinned.append(window)
    _apply_options(window)


# The windows skinned so far (closed ones are dropped when the theme changes), the colors a widget can carry, and the last theme change.
_skinned: list[tk.Misc] = []
_COLOR_OPTIONS = ("background", "foreground", "activebackground", "activeforeground", "highlightbackground", "highlightcolor",
                  "selectbackground", "selectforeground", "selectcolor", "insertbackground", "disabledbackground", "disabledforeground",
                  "readonlybackground", "troughcolor")
_CANVAS_ITEM_COLORS = ("fill", "outline", "activefill", "activeoutline")
_theme_listeners: list[Callable[[], None]] = []
_last_changes: dict[str, str] = {}


def _apply_options(window: tk.Misc) -> None:
    scope = window.winfo_name()
    body_font = str(font())   # text that names no font of its own follows the text size setting
    for widget_class in ("Label", "Message", "Button", "Entry", "Text", "Listbox", "Checkbutton", "Radiobutton"):
        window.option_add(f"*{scope}*{widget_class}.font", body_font, 60)
    for widget_class, options in _skin_options().items():
        for option, value in options.items():
            window.option_add(f"*{scope}*{widget_class}.{option}", value, 60)


def remap(color: object) -> object:
    """`color` as it is in the theme just chosen (anything that is not a color the last change touched comes back as it was)."""
    if isinstance(color, str):
        return _last_changes.get(color.lower(), color)
    return color


def _recolor(widget: tk.Misc, changes: dict[str, str]) -> None:
    """Gives `widget` and everything under it the new theme's colors: its color options, a canvas's drawn items, a text widget's tags, and
    the color strings the kit's own widgets keep for later (a button's hover fill, a tab bar's background)."""
    try:
        keys = set(widget.keys())
    except tk.TclError:
        return
    for option in _COLOR_OPTIONS:
        if option in keys:
            try:
                new = changes.get(str(widget.cget(option)).lower())
                if new:
                    widget.configure(**{option: new})
            except tk.TclError:
                pass
    if isinstance(widget, tk.Canvas):
        for item in widget.find_all():
            for option in _CANVAS_ITEM_COLORS:
                try:
                    new = changes.get(str(widget.itemcget(item, option)).lower())
                    if new:
                        widget.itemconfigure(item, **{option: new})
                except tk.TclError:
                    pass
    if isinstance(widget, tk.Text):
        for tag in widget.tag_names():
            for option in ("foreground", "background"):
                try:
                    new = changes.get(str(widget.tag_cget(tag, option)).lower())
                    if new:
                        widget.tag_configure(tag, **{option: new})
                except tk.TclError:
                    pass
    for name, value in list(vars(widget).items()):
        if isinstance(value, str):
            new = changes.get(value.lower())
            if new:
                setattr(widget, name, new)
        elif isinstance(value, tuple) and value and all(isinstance(v, str) for v in value):
            setattr(widget, name, tuple(changes.get(v.lower(), v) for v in value))
    for child in widget.winfo_children():
        _recolor(child, changes)


def theme_name() -> str:
    return P.current()


def set_theme(name: str) -> None:
    """Makes `name` the look of every WFMT window: windows built from now on use it, and the open ones are recolored where they stand.
    The listeners (tables, which keep row colors of their own) are told afterwards."""
    global _last_changes
    if name == P.current() or name not in P.THEMES:
        return
    changes = P.apply(name)
    _last_changes = changes
    _skinned[:] = [w for w in _skinned if _alive(w)]
    for window in _skinned:
        try:
            _apply_options(window)
            window.configure(background=P.PANE)
            _recolor(window, changes)
        except tk.TclError:
            pass
    for listener in list(_theme_listeners):
        listener()


def _alive(widget: tk.Misc) -> bool:
    try:
        return bool(widget.winfo_exists())
    except tk.TclError:
        return False


def add_theme_listener(listener: Callable[[], None]) -> Callable[[], None]:
    """Calls `listener` after the theme changes; returns the function that stops it."""
    _theme_listeners.append(listener)

    def remove() -> None:
        if listener in _theme_listeners:
            _theme_listeners.remove(listener)
    return remove


def grab_when_visible(window: tk.Misc, tries: int = 40) -> None:
    """Make a dialog modal (`grab_set`) once it is actually on screen.

    On X11 (Linux) `grab_set()` raises "grab failed: window not viewable" if
    the window hasn't been mapped yet, which is the case right after it is
    created; Windows doesn't care. So try now and, if that fails, retry a few
    times shortly after. A dialog that never becomes viewable simply stays
    non-modal - it still works, which beats failing to open at all."""
    try:
        window.grab_set()
    except tk.TclError:
        if tries <= 0:
            return
        try:
            window.after(50, lambda: grab_when_visible(window, tries - 1))
        except tk.TclError:  # the dialog was closed before it ever appeared
            pass
