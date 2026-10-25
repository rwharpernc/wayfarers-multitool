"""The "Get EDMCModernOverlay" link at the top of each overlay feature's Settings page.

Every overlay page used to carry it, which is noise on Windows once WFMT's built-in overlay is chosen (EDMCModernOverlay is then needed only
for other plugins' overlays). It now shows only while EDMCModernOverlay is the overlay in use: on Linux, or when it is chosen on Settings →
Overlays → Overlay Connection, which keeps the link always.

When EDMCModernOverlay is the overlay in use and it is not installed, the page also says so, because nothing can appear on screen until it is (on Linux
WFMT's own overlay is not available yet). The settings stay usable: they are saved and take effect once the overlay is installed.
"""
from __future__ import annotations

import os
import tkinter as tk

import myNotebook as nb
from ttkHyperlinkLabel import HyperlinkLabel

URL = "https://github.com/SweetJonnySauce/EDMCModernOverlay"
TEXT = "Get EDMCModernOverlay (needed on Linux, and for other plugins' overlays)"


NOT_FOUND = ("EDMCModernOverlay was not found. WFMT draws its on-screen displays through it, and its own overlay is Windows only for now, "
             "so on Linux nothing appears on screen until it is installed. These settings are kept and take effect once it is.")


def modern_overlay_found(plugin_dir: str) -> bool:
    """Whether EDMCModernOverlay is installed: its plugin API can be imported, or its folder sits beside WFMT's in EDMC's plugins folder."""
    try:
        from overlay_plugin.overlay_api import define_plugin_group  # type: ignore[import-not-found]  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        beside = os.path.dirname(os.path.abspath(plugin_dir))
        return any(os.path.isdir(os.path.join(beside, name)) and "modernoverlay" in name.lower() for name in os.listdir(beside))
    except OSError:
        return False


def missing() -> bool:
    """Whether EDMCModernOverlay is the overlay in use and is not installed."""
    return wanted() and not modern_overlay_found(os.path.dirname(os.path.abspath(__file__)))


def wanted() -> bool:
    """Whether the built-in overlay is not the one drawing (so the link is of use)."""
    from . import overlay_native
    return overlay_native.selected() != overlay_native.BUILTIN


def add_notice(frame: tk.Misc, row: int, column: int = 0, columnspan: int = 1) -> bool:
    """Put the "not found" message on `frame` at `row` when EDMCModernOverlay is in use and missing. Returns whether it was added."""
    if not missing():
        return False
    nb.Label(frame, text=NOT_FOUND, wraplength=440, justify=tk.LEFT, foreground="#c07000").grid(
        row=row, column=column, columnspan=columnspan, sticky=tk.W, padx=10, pady=(0, 6))
    return True


def add(frame: tk.Misc, row: int = 1) -> bool:
    """Put the link on `frame` at `row` when it is wanted, with the "not found" message above it when EDMCModernOverlay is missing.
    Returns whether the link was added."""
    if not wanted():
        return False
    box = nb.Frame(frame)
    box.grid(row=row, column=0, sticky=tk.W)
    if missing():
        nb.Label(box, text=NOT_FOUND, wraplength=440, justify=tk.LEFT, foreground="#c07000").grid(row=0, column=0, sticky=tk.W, padx=10, pady=(0, 4))
    HyperlinkLabel(box, text=TEXT, background=nb.Label().cget("background"), url=URL, underline=True).grid(
        row=1, column=0, sticky=tk.W, padx=10, pady=(0, 8))
    return True
