"""Color and font tokens for WFMT's own window look (spec section 5, option
A: a look independent of EDMC's theme). Every color used by plugin/uikit
comes from here. The colors are module attributes (`P.BG`, `P.TEXT`, ...) set from the
chosen theme by `apply`, so read them when a widget is built, never at import time.

Status colors are never the only carrier of meaning: pills always carry a
text label and map markers differ in shape, so the set stays usable without
telling red from green."""
from __future__ import annotations

import re

# Color tokens, set from the chosen theme. The values here are the Navy theme, which is what every window used before themes.
BG = PANE = CARD = BUTTON = HOVER = SELECT = LINE = STRIPE = ""    # surfaces, darkest to lightest (STRIPE: every other table row)
TEXT = MUTED = FAINT = ""                                          # text
ACCENT = ACCENT_HI = ACCENT_INK = ""                               # primary action: fill, hover fill, text on it
INFO = OK = WARN = DANGER = ""                                     # status
TITLE = HEADING = STATUS = ""                                      # window title, section labels and table headings, footer message (bright, and unlike the accent, the headings and the text)
ROW_OK = ROW_OVER = ROW_HAUL = ""                                   # table row tints for "done", "over" and "being hauled"; dark enough for TEXT to stay readable
MAP_BG = MAP_GRID = MAP_COVERAGE = MAP_HOTSPOT = MAP_DEPLETED = ""

TOKENS = ("BG", "PANE", "CARD", "BUTTON", "HOVER", "SELECT", "LINE", "STRIPE", "TEXT", "MUTED", "FAINT", "ACCENT", "ACCENT_HI", "ACCENT_INK",
          "INFO", "OK", "WARN", "DANGER", "TITLE", "HEADING", "STATUS", "ROW_OK", "ROW_OVER", "ROW_HAUL",
          "MAP_BG", "MAP_GRID", "MAP_COVERAGE", "MAP_HOTSPOT", "MAP_DEPLETED")


def _mix(color: str, other: str, amount: float) -> str:
    """`color` moved `amount` (0 to 1) of the way toward `other`; both "#rrggbb"."""
    a = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def _from_variables(v: dict) -> dict:
    """A theme from the named colors of EDDDT's stylesheet (--bg, --panel, --panel-2, --line, --text, --dim, --label, --cyan, --amber,
    --green, --red, --violet, --hot, --deep, --key-hi, --key-on-hi, --green-dim, --amber-dim, plus --status, the footer message). In EDDDT --cyan is the theme's own
    color (cyan, orange or green), so it becomes the accent and the headings."""
    primary = v["cyan"]
    return {
        "BG": v["bg"], "PANE": v["panel"], "CARD": v["panel-2"], "BUTTON": v["key-hi"], "HOVER": v["hot"], "SELECT": v["key-on-hi"],
        "LINE": v["line"], "STRIPE": _mix(v["panel"], v["panel-2"], 0.5), "TEXT": v["text"], "MUTED": v["dim"], "FAINT": v["label"],
        "ACCENT": primary, "ACCENT_HI": _mix(primary, "#ffffff", 0.3), "ACCENT_INK": v["deep"],
        "INFO": v["violet"], "OK": v["green"], "WARN": v["amber"], "DANGER": v["red"],
        "TITLE": v["amber"], "HEADING": _mix(primary, "#ffffff", 0.12), "STATUS": v["status"],
        "ROW_OK": v["green-dim"], "ROW_OVER": v["amber-dim"], "ROW_HAUL": _mix(v["violet"], v["panel"], 0.62),
        "MAP_BG": v["deep"], "MAP_GRID": v["amber-dim"], "MAP_COVERAGE": v["green-dim"], "MAP_HOTSPOT": v["text"], "MAP_DEPLETED": v["dim"],
    }


def _distinct(tokens: dict) -> dict:
    """`tokens` with no two sharing a color: a repeat is moved one step in its blue channel (not visible), so a color found in an open
    window names exactly one token and can be mapped to the new theme's color for it."""
    seen: set = set()
    result = {}
    for token in TOKENS:
        color = tokens[token].lower()
        while color in seen:
            blue = int(color[5:7], 16)
            color = color[:5] + f"{blue + 1 if blue < 255 else blue - 1:02x}"
        seen.add(color)
        result[token] = color
    return result


THEMES: dict = {
    "Navy": {
        "BG": "#0f1a2e", "PANE": "#142340", "CARD": "#1c3054", "BUTTON": "#2c4a7a", "HOVER": "#243d66", "SELECT": "#2f5a96",
        "LINE": "#2a4470", "STRIPE": "#18294a", "TEXT": "#e6e9ee", "MUTED": "#9db3d4", "FAINT": "#6b82a6",
        "ACCENT": "#f0a23b", "ACCENT_HI": "#ffb957", "ACCENT_INK": "#1a1306",
        "INFO": "#4aa8ff", "OK": "#52d6a0", "WARN": "#f2c94c", "DANGER": "#ff7a7a",
        "TITLE": "#ffc15e", "HEADING": "#5fd3f3", "STATUS": "#ffe27a",
        "ROW_OK": "#1d5a45", "ROW_OVER": "#6e4414", "ROW_HAUL": "#244c77",
        "MAP_BG": "#0b1424", "MAP_GRID": "#2b2a1c", "MAP_COVERAGE": "#2e5c3a", "MAP_HOTSPOT": "#eee8be", "MAP_DEPLETED": "#969696",
    },
    # The three themes of EDDDT (its mfd.css), as the same tokens.
    "Cyan": _from_variables({
        "bg": "#04080b", "panel": "#091218", "panel-2": "#0d1b23", "line": "#14343f", "text": "#c4eaf3", "dim": "#6a909c", "label": "#3d6574",
        "cyan": "#38e1ff", "amber": "#ffb347", "green": "#5dff9a", "red": "#ff5b6b", "violet": "#b48cff", "hot": "#0f2f3a",
        "deep": "#02060a", "key-hi": "#27363e", "key-on-hi": "#1f5a6b", "green-dim": "#1c5a37", "amber-dim": "#5a4217",
        "status": "#ffee55"}),
    "Amber": _from_variables({
        "bg": "#0a0703", "panel": "#140e06", "panel-2": "#1c1409", "line": "#3a2a12", "text": "#ffe3b8", "dim": "#a8855a", "label": "#8a6a3c",
        "cyan": "#ff9a1f", "amber": "#ffe14a", "green": "#9be15d", "red": "#ff5b4a", "violet": "#ffb0e0", "hot": "#3a2608",
        "deep": "#060402", "key-hi": "#3a3024", "key-on-hi": "#7a4a0e", "green-dim": "#3a5a1c", "amber-dim": "#6b5a14",
        "status": "#7df0ff"}),
    "Green": _from_variables({
        "bg": "#030a05", "panel": "#07140b", "panel-2": "#0b1d10", "line": "#123a1d", "text": "#c7f5d2", "dim": "#5f9a70", "label": "#3d7a4f",
        "cyan": "#4dff88", "amber": "#ffd24a", "green": "#b6ff5d", "red": "#ff6b5b", "violet": "#9bd0ff", "hot": "#0f3a1c",
        "deep": "#020603", "key-hi": "#243a2a", "key-on-hi": "#1f6b36", "green-dim": "#2a6b20", "amber-dim": "#5a4a17",
        "status": "#fff27a"}),
}
THEMES = {name: _distinct(tokens) for name, tokens in THEMES.items()}
DEFAULT_THEME = "Navy"
_current = ""


def current() -> str:
    return _current


def apply(name: str) -> dict:
    """Makes `name` the theme (an unknown name is Navy). Returns {old color: new color} for the tokens that changed, in lower case, so
    windows that are already open can be recolored (see style.set_theme)."""
    global _current
    name = name if name in THEMES else DEFAULT_THEME
    old = {token: globals()[token] for token in TOKENS if globals()[token]}
    globals().update(THEMES[name])
    _current = name
    changes: dict = {}
    for token, before in old.items():
        after = globals()[token]
        if before.lower() != after.lower():
            changes.setdefault(before.lower(), after)      # two tokens that shared a color: the first one decides
    return changes


apply(DEFAULT_THEME)

PAD = 10
PAD_SM = 5

# (size delta from the system default font, weight)
FONT_BODY = (0, "normal")
FONT_SMALL = (-1, "normal")
FONT_BOLD = (0, "bold")
FONT_SMALL_BOLD = (-1, "bold")
FONT_TITLE = (4, "bold")
FONT_SECTION = (1, "bold")
FONT_STAT = (8, "bold")
