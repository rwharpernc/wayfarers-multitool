"""The "Archive" window: the commander's finished construction sites, kept for reference. Opened from the Manage Sites menu of the
Colonization Sites window, where **Archive Finished** moves every completed or failed site here and out of the way of the sites still
being built.

An archived site is the same record as before (colonization_data.py, with `archived` set), so the history figures still count it and it
is part of Back up my data. The window lists each one with how it ended, when it was started and finished and how long it took, and
shows the commodities the build needed under the list. **Restore** puts a site back in the Sites window, **Copy Summary** copies its
facts as text and **Remove Permanently** forgets it (asking first). What the figures are is in colonization_archive.py; the window only draws them.
"""
from __future__ import annotations

import os
import tkinter as tk
from typing import Callable, List, Optional

from config import appname, config

from . import panelkit
from .colonization import Site
from .colonization_archive import site_values, summary_text
from .colonization_data import SiteRepository
from .uikit import dialogs, palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable

CONFIG_GEOMETRY = "wfmt_colonization_archive_window_geometry"
MIN_WIDTH = 760
MIN_HEIGHT = 460
DEFAULT_SIZE = (980, 640)
_NAME_MAX = 60

_SITE_COLUMNS = (
    Column("name", "Site", 220, stretch=True, max_chars=40),
    Column("system", "System", 170, stretch=True, max_chars=32),
    Column("result", "Result", 80, max_chars=10),
    Column("started", "Started", 90, max_chars=10),
    Column("finished", "Finished", 90, max_chars=10),
    Column("took", "Took", 80, anchor="e", max_chars=10),
    Column("tons", "Needed", 90, anchor="e", max_chars=12),
)
_COMMODITY_COLUMNS = (
    Column("label", "Commodity", 240, stretch=True, max_chars=40),
    Column("required", "Required", 90, anchor="e", max_chars=10),
    Column("provided", "Delivered", 90, anchor="e", max_chars=10),
    Column("left", "Left", 90, anchor="e", max_chars=10),
)
_HELP = (
    ("What this is", "Finished construction sites you put away with Archive Finished in the Manage Sites menu, kept so you can look back at them. "
                     "The Colonization Sites window lists only the sites you still work on."),
    ("Delivered", "A site's Delivered figures count every commander's deliveries, as the depot reports them, not only yours. "
                  "Your own are in the history."),
    ("Restore", "Puts the site back in the Colonization Sites window."),
    ("Remove Permanently", "Forgets the site for good. The history keeps what you delivered, but not this list of commodities."),
)

_window: Optional["ArchiveWindow"] = None


def show(parent: tk.Misc, repository: SiteRepository, cmdr: Callable[[], str]) -> None:
    """Open the window, or refresh and raise it if it is open."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return
    _window = ArchiveWindow(parent, repository, cmdr)


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


class ArchiveWindow:
    def __init__(self, parent: tk.Misc, repository: SiteRepository, cmdr: Callable[[], str]) -> None:
        self._repository = repository
        self._cmdr = cmdr
        self._sites: dict = {}
        self._shell = WindowShell(
            parent, "Colonization Archive", "", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Colonization Archive help", _HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Restore", self._on_restore, accent=True)
        self._shell.add_action("Copy Summary", self._on_copy)
        self._shell.add_menu("Manage", [("Remove Permanently", self._on_remove, "danger")])
        self._sites_table = DataTable(self._shell.body, _SITE_COLUMNS, on_select=lambda _iid: self._show_detail(),
                                      empty_text="Nothing is archived yet. Archive Finished in the Manage Sites menu puts finished sites here.")
        self._sites_table.tag_configure("failed", foreground=P.DANGER)
        self._sites_table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._commodities = DataTable(self._shell.body, _COMMODITY_COLUMNS, sortable=False, visible_rows=7,
                                      empty_text="Select a site to see what it needed.")
        self._commodities.pack(fill="x")
        repository.add_listener(self._on_repository_changed)
        self.refresh()

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def _on_repository_changed(self) -> None:
        if self.alive:
            self.refresh()

    def refresh(self) -> None:
        if not self.alive:
            return
        cmdr = (self._cmdr() or "").strip()
        sites = [s for s in self._repository.for_cmdr(cmdr) if s.archived] if cmdr else []
        sites.sort(key=lambda s: s.completed_at or s.updated, reverse=True)
        self._sites = {str(s.market_id): s for s in sites}
        selected = self._sites_table.selection()
        self._sites_table.clear()
        for iid, site in self._sites.items():
            self._sites_table.insert(iid, site_values(site), tag="failed" if site.failed else None)
        if selected and self._sites_table.exists(selected[0]):
            self._sites_table.select(selected[0])
        label = _clip(cmdr, _NAME_MAX) if cmdr else "No commander yet"
        self._shell.set_subtitle(f"{label} - {len(sites)} archived site{'s' if len(sites) != 1 else ''}")
        self._show_detail()

    def _picked(self) -> Optional[Site]:
        picked = self._sites_table.selection()
        return self._sites.get(picked[0]) if picked else None

    def _show_detail(self) -> None:
        self._commodities.clear()
        site = self._picked()
        if site is None:
            return
        for resource in sorted(site.resources, key=lambda r: (r.label or r.key).casefold()):
            self._commodities.insert(resource.key, (resource.label or resource.key, f"{resource.required:,}", f"{resource.provided:,}",
                                                    f"{resource.remaining:,}"))

    def _on_restore(self) -> None:
        site = self._picked()
        if site is None:
            self._shell.set_status("Select a site first.")
            return
        self._repository.set_archived(self._cmdr(), [site.market_id], False)
        self._shell.set_status(f"Restored {_clip(site.display_name(), _NAME_MAX)} to the Colonization Sites window.", ok=True)

    def _on_copy(self) -> None:
        site = self._picked()
        if site is None:
            self._shell.set_status("Select a site first.")
            return
        if panelkit.copy_to_clipboard(self._shell.window, summary_text(site)):
            self._shell.set_status(f"Copied the summary of {_clip(site.display_name(), _NAME_MAX)}.", ok=True)

    def _on_remove(self) -> None:
        site = self._picked()
        if site is None:
            self._shell.set_status("Select a site first.")
            return
        if not dialogs.confirm(self._shell.window, "Remove permanently",
                               f"Forget {_clip(site.display_name(), _NAME_MAX)} for good?\n\nIts list of commodities is lost. "
                               "Your delivery history keeps what you delivered."):
            return
        self._repository.remove(self._cmdr(), site.market_id)
        self._shell.set_status(f"Removed {_clip(site.display_name(), _NAME_MAX)}.")

    def close(self) -> None:
        self._shell.close()
