"""Hide every WFMT overlay for a while, and show them again: a click on the line in the WFMT panel, a keyboard shortcut or chat command (Settings -> General -> Shortcuts), or the button in
Settings.

The switch itself is in `overlay.py` (`set_all_hidden`): it clears what is on screen and stops everything being drawn until shown again, then puts back what was up. Nothing
is saved; overlays are shown whenever EDMC starts. This module adds the panel line and the Settings tab; the keyboard shortcut and the chat command that flip the same switch are in
`shortcuts.py` (they were here until the shortcuts moved to one page for every action).
"""

from __future__ import annotations

import os
import logging
from typing import List

import tkinter as tk

import myNotebook as nb
from config import appname

from . import overlay

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None   # Settings-tab-only, no main-panel widget (the panel line is built by `build_panel_line`)


# --- the panel line ----------------------------------------------------------------------------------------------------

def panel_text(hidden: bool) -> str:
    return "Overlays are hidden (click to show)" if hidden else "Overlays shown (click to hide)"


_labels: List[tk.Label] = []


def build_panel_line(parent: tk.Misc, row: int) -> tk.Label:
    """A line in the WFMT panel that says whether the overlays are hidden and flips it when clicked."""
    from . import panelkit
    label = panelkit.wrap_label(parent, anchor="w", cursor="hand2")
    label.grid(row=row, column=0, columnspan=3, sticky=tk.W)
    label.configure(text=panel_text(overlay.all_hidden()))
    label.bind("<Button-1>", lambda _e: overlay.toggle_all_hidden())
    panelkit.add_tooltip(label, "Hides every WFMT overlay until you click again (Settings → General → Shortcuts has a keyboard shortcut and a chat command)")
    _labels.append(label)
    return label


def _on_change(hidden: bool) -> None:
    for label in list(_labels):
        try:
            label.after(0, lambda lab=label: lab.configure(text=panel_text(hidden)))
        except (tk.TclError, RuntimeError):
            _labels.remove(label)


overlay.on_visibility_change(_on_change)


# --- Settings tab ------------------------------------------------------------------------------------------------------

def build_settings(notebook: tk.Misc) -> None:
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Hide overlays")
    nb.Label(
        frame,
        text=("Hides every WFMT overlay at once, for example to take a clean screenshot or to look at the game without cards over it, and shows them again where they "
              "were. Click the Overlays line in the WFMT panel, use the button below, or set a keyboard shortcut or a chat command for it under Settings → General → "
              "Shortcuts. The overlays are always shown when EDMC starts. This hides WFMT's overlays only; another plugin's overlay is unaffected."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 8))
    buttons = tk.Frame(frame)
    buttons.grid(row=1, column=0, sticky=tk.W, padx=10, pady=(6, 10))
    tk.Button(buttons, text="Hide / show now", command=overlay.toggle_all_hidden).pack(side=tk.LEFT)
