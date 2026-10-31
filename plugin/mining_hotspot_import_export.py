"""
Import/export for the known-surface-hotspots list (mining_hotspots.py),
shared between the Settings tab's hotspot section
(mining_hotspot_settings.py) and the Import and Export window (the Import/export
button in the Surface Mining live window) so the file-picker/merge-prompt/
error-handling logic exists in exactly one place.
"""
import logging
import os
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Optional

from config import appname

from . import mining_hotspots as hotspots
from .uikit import dialogs
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.widgets import FlatButton, NoteLabel

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")


def import_hotspots(parent: tk.Misc) -> None:
    """Opens a file picker, asks merge-vs-replace, and imports a file
    exported by WFMT (see export_hotspots). Any listener registered on hotspot_repository (the
    main panel included, via mining_panel.py's add_listener call)
    refreshes on its own once the import succeeds - this function
    doesn't need to know who's displaying the list."""
    path = filedialog.askopenfilename(
        title="Import Hotspots",
        filetypes=[("JSON files", "*.json")])
    if not path:
        return
    merge = dialogs.confirm(
        parent, "Import Hotspots",
        "Merge with the existing list?\n\nYes = add to current list.\nNo = replace it entirely.")
    try:
        count = hotspots.hotspot_repository.import_from_file(path, merge=merge)
    except Exception:
        logger.exception("Failed to import hotspots from %s", path)
        dialogs.error(parent, "Import Hotspots", "Could not read that file - see the log.")
        return
    dialogs.info(parent, "Import Hotspots", f"Imported {count} hotspot(s).")


def export_hotspots(parent: tk.Misc) -> None:
    """Opens a save-file picker and writes the full hotspot list in
    WFMT's own flat JSON shape (see mining_hotspots.py's
    HotspotRepository.export_to_file()) - this is the file another
    commander's import_hotspots() call above can read back in
    directly."""
    path = filedialog.asksaveasfilename(defaultextension=".json",
                                        filetypes=[("JSON files", "*.json")])
    if not path:
        return
    try:
        hotspots.hotspot_repository.export_to_file(path)
    except Exception:
        logger.exception("Failed to export hotspots to %s", path)
        dialogs.error(parent, "Export Hotspots", "Could not write that file - see the log.")


_window: Optional[WindowShell] = None


def open_import_export_dialog(parent: tk.Misc) -> None:
    """The Import and Export window (the Import/export button in the Surface Mining live window): what the list holds, and the two actions, each with a line saying what it does. The Settings tab keeps its own
    Import and Export buttons (`mining_hotspot_settings.py`). Parented on the caller's toplevel, not on a frame the panel rebuilds every second (which would take the window with it)."""
    global _window
    if _window is not None and _window.alive:
        _window.window.deiconify()
        _window.window.lift()
        return
    shell = WindowShell(parent.winfo_toplevel(), "Import and Export Hotspots", f"{len(hotspots.hotspot_repository.all()):,} saved hotspots", size=(560, 340), min_size=(480, 300))
    _window = shell
    shell.window.transient(parent.winfo_toplevel())
    body = shell.body
    for text, action, label, tip in (
            ("Import", lambda: _run(shell, import_hotspots), "Reads a hotspot file exported by WFMT, from you or another commander, and asks whether to add to your list or replace it.",
             "Import - read a hotspot file exported by WFMT and add it to, or replace, your list"),
            ("Export", lambda: _run(shell, export_hotspots), "Writes your saved hotspots to a file you choose, to keep or to give another commander.",
             "Export - write your saved hotspots to a file you choose")):
        row = tk.Frame(body, bg=P.BG)
        row.pack(fill="x", pady=(0, P.PAD))
        FlatButton(row, text, action, kind="accent" if text == "Import" else "normal", tip=tip).pack(side="left", padx=(0, P.PAD))
        NoteLabel(row, label, bg=P.BG, padx=0).pack(side="left", fill="x", expand=True)
    FlatButton(body, "Close", shell.close, tip="Close - close this window").pack(anchor="e", pady=(P.PAD, 0))
    shell.set_status("Hotspots are kept for the commander you are playing; an export holds only that commander's list.")


def _run(shell: WindowShell, action) -> None:
    """Run an import or export from the window, then bring the window back in front of the file picker's aftermath and refresh the count."""
    action(shell.window)
    if shell.alive:
        shell.set_subtitle(f"{len(hotspots.hotspot_repository.all()):,} saved hotspots")
        shell.window.lift()
