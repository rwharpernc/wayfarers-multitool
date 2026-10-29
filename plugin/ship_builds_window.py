"""Ship Builds management window - list every saved build link for one
commander, with Add/Edit/Delete/Open/Copy - same singleton window +
geometry-persistence convention as the other WFMT windows, built on the
shared window kit (plugin/uikit - see docs/WINDOW_FRAMEWORK_SPEC.md)."""

from __future__ import annotations

import logging
import os
import tkinter as tk
import webbrowser
from typing import Optional

from config import appname, config

from . import panelkit
from .ship_builds_data import ShipBuild, ShipBuildRepository
from . import stored_modules
from .ship_builds_dialog import open_ship_build_dialog
from .ship_modules_tab import StoredModulesTab
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Tabs

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_ship_builds_window_geometry"

MIN_WIDTH = 760
MIN_HEIGHT = 380
DEFAULT_SIZE = (860, 480)

_COLUMNS = (
    Column("name", "Name", 220, stretch=True, max_chars=50),
    Column("ship", "Ship", 130, max_chars=60),
    Column("role", "Role", 110, max_chars=60),
    Column("site", "Site", 120, max_chars=60),
    Column("updated", "Updated", 100, anchor="e"),
)

_window: Optional["ShipBuildsWindow"] = None


BUILDS_STATUS = "Select a build, then use the buttons above. Double-click a row to edit it."
MODULES_STATUS = "Modules you have in storage, from the game's Module Storage events. The buttons above are for saved builds."


def show(parent: tk.Misc, repository: ShipBuildRepository, cmdr: str, prefill_ship: str,
         module_book: Optional[stored_modules.ModuleBook] = None) -> None:
    """Open the management window for `cmdr`, or raise/refresh it if
    already open. `prefill_ship` seeds a new build's Ship field with the
    commander's currently-flown ship (best-effort, see
    ship_builds_panel.py). `module_book` is the stored-modules list the second
    tab shows (the plugin's own unless a test passes another)."""
    global _window
    if _window is not None and _window.alive:
        _window.set_cmdr(cmdr, prefill_ship)
        _window.lift()
        return
    _window = ShipBuildsWindow(parent, repository, cmdr, prefill_ship, module_book or stored_modules.book)


class ShipBuildsWindow:
    def __init__(self, parent: tk.Misc, repository: ShipBuildRepository, cmdr: str, prefill_ship: str, module_book: stored_modules.ModuleBook) -> None:
        self._repository = repository
        self._cmdr = cmdr
        self._prefill_ship = prefill_ship
        self._builds: list[ShipBuild] = []

        self._shell = WindowShell(
            parent, "Ship Builds", "", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._toplevel = self._shell.window

        self._shell.add_action("Add build", self._on_add, accent=True, tip="Add build - record a new ship build with its link")
        self._shell.add_action("Edit build", self._on_edit, tip="Edit build - change the selected build")
        self._shell.add_action("Delete build", self._on_delete, tip="Delete build - remove the selected build from the list")
        self._shell.add_action("Open Link", self._on_open, tip="Open Link - open the selected build's link in your web browser")
        self._shell.add_action("Copy Link", self._on_copy, tip="Copy Link - copy the selected build's link to the clipboard")

        self._tabs = Tabs(self._shell.body)
        self._tabs.pack(fill="both", expand=True)
        builds_tab = self._tabs.add("Builds")
        self._table = DataTable(builds_tab, _COLUMNS, on_activate=lambda _iid: self._on_edit())
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._modules = StoredModulesTab(self._tabs.add("Stored modules"), module_book, lambda: self._cmdr)
        self._tabs.on_select = lambda index: self._shell.set_status(MODULES_STATUS if index == 1 else BUILDS_STATUS)
        self._tabs.select(0)
        self._shell.set_status(BUILDS_STATUS)

        repository.add_listener(self._refresh)
        self._refresh()

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._toplevel.deiconify()
        self._toplevel.lift()

    def set_cmdr(self, cmdr: str, prefill_ship: str) -> None:
        self._cmdr = cmdr
        self._prefill_ship = prefill_ship
        self._refresh()
        self._modules.refresh()

    def _refresh(self) -> None:
        if not self.alive:
            return
        self._builds = sorted(self._repository.for_cmdr(self._cmdr), key=lambda b: b.updated, reverse=True)
        cmdr_label = self._cmdr or "(no commander detected yet)"
        self._shell.set_subtitle(
            f"{cmdr_label} — {len(self._builds)} saved build{'s' if len(self._builds) != 1 else ''}")

        self._table.clear()
        for build in self._builds:
            self._table.insert(build.id, (build.name, build.ship, build.role, build.site, build.updated[:10]))

    def _selected(self) -> Optional[ShipBuild]:
        selection = self._table.selection()
        if not selection:
            return None
        build_id = selection[0]
        return next((b for b in self._builds if b.id == build_id), None)

    def _on_add(self) -> None:
        if not self._cmdr:
            return
        open_ship_build_dialog(
            self._toplevel, on_save=lambda b: self._repository.add(self._cmdr, b),
            prefill_ship=self._prefill_ship,
        )

    def _on_edit(self) -> None:
        build = self._selected()
        if build is None or not self._cmdr:
            return
        open_ship_build_dialog(
            self._toplevel, on_save=lambda b: self._repository.update(self._cmdr, b), existing=build,
        )

    def _on_delete(self) -> None:
        build = self._selected()
        if build is None or not self._cmdr:
            return
        self._repository.remove(self._cmdr, build.id)

    def _on_open(self) -> None:
        build = self._selected()
        if build is None or not build.url.startswith(("http://", "https://")):   # a hand-edited file could hold any scheme
            return
        webbrowser.open(build.url)

    def _on_copy(self) -> None:
        build = self._selected()
        if build is None:
            return
        panelkit.copy_to_clipboard(self._toplevel, build.url)

    def close(self) -> None:
        self._shell.close()
