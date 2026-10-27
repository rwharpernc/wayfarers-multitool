"""Color and font tokens for WFMT's own window look (spec section 5, option
A: a fixed look independent of EDMC's theme). Every color used by plugin/uikit
comes from here, so a light variant later is a one-dict change.

Status colors are never the only carrier of meaning: pills always carry a
text label and map markers differ in shape, so the set stays usable without
telling red from green."""
from __future__ import annotations

# Surfaces, darkest to lightest.
BG = "#0f1a2e"        # window background (deep navy)
PANE = "#142340"      # pane background
CARD = "#1c3054"      # raised card
BUTTON = "#2c4a7a"     # buttons (visible on both PANE and CARD)
HOVER = "#243d66"     # row hover
SELECT = "#2f5a96"    # selected row
LINE = "#2a4470"      # hairlines

# Text.
TEXT = "#e6e9ee"
MUTED = "#9db3d4"
FAINT = "#6b82a6"

# Accents / status.
ACCENT = "#f0a23b"    # amber - primary actions, current selection marker
INFO = "#4aa8ff"      # blue - "you are here"
OK = "#52d6a0"
WARN = "#f2c94c"
DANGER = "#ff7a7a"

# Headings and messages. HEADING colors section labels and table column headers, TITLE the window title, STATUS the
# footer message (OK, WARN and DANGER still color a message that means success, caution or failure).
TITLE = "#ffc15e"     # warm gold
HEADING = "#5fd3f3"   # cyan
STATUS = "#8fc7ff"    # soft blue

# Row tints for a table row that is "done" (green) or "over" (orange); dark enough for TEXT to stay readable.
ROW_OK = "#1d5a45"
ROW_OVER = "#6e4414"

# Map.
MAP_BG = "#0b1424"
MAP_GRID = "#2b2a1c"          # dim yellow: visible over driven ground
MAP_COVERAGE = "#2e5c3a"
MAP_HOTSPOT = "#eee8be"       # pale filled dot
MAP_DEPLETED = "#969696"      # hollow ring

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
