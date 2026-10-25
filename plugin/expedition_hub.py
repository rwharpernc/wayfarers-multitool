"""The Expedition window: one window with a tab for each part of an expedition, Plan, Route and Log.

Plan is the Expedition window (`expedition_window.py`: the expeditions and their stops), Route is the Route Planner (`route_planner_window.py`) and Log is the Expedition Log
(`expedition_log_window.py`: the archive and totals). Each is the same code that used to run in a window of its own; here it is built into a tab through `uikit.shell.TabShell`,
which has the interface of `WindowShell`, so a window needs only a `host` argument to live in a tab. A tab is built the first time it is shown, and again if it is closed.

The panels (`expedition_panel`, `route_planner_panel`, `expedition_log_panel`) `register` how to build their tab and open it with `show`; this module knows nothing about them, so
it imports no panel. The window's size and position are saved once, for the whole window.
"""
from __future__ import annotations

import functools
import logging
import os
import tkinter as tk
from typing import Any, Callable, Dict, Optional

from config import appname, config

from .uikit.shell import TabShell, WindowShell
from .uikit.widgets import Tabs

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PLAN, ROUTE, LOG = "plan", "route", "log"
TABS = ((PLAN, "Plan"), (ROUTE, "Route"), (LOG, "Log"))
CONFIG_GEOMETRY = "wfmt_expedition_hub_geometry"
DEFAULT_SIZE = (1240, 820)
MIN_SIZE = (1080, 600)

Builder = Callable[..., Any]
_builders: Dict[str, Builder] = {}
_hub: Optional["ExpeditionHub"] = None


def register(tab: str, builder: Builder) -> None:
    """Say how to build `tab`. `builder(parent, host, **options)` builds the tab's window with `host` as its shell, or, when it is already built, applies the options (select an
    expedition, refresh) and returns it. The result has `alive`, `close()`, and is the window object of that module."""
    _builders[tab] = builder


def show(parent: tk.Misc, tab: str, **options: Any) -> None:
    """Open the window on `tab` (building it first if needed), or raise it and switch to the tab."""
    global _hub
    if _hub is None or not _hub.alive:
        _hub = ExpeditionHub(parent)
    _hub.show(tab, **options)


def is_open() -> bool:
    return _hub is not None and _hub.alive


def view(tab: str) -> Any:
    """The window built in `tab`, or None."""
    return _hub.view(tab) if _hub is not None and _hub.alive else None


def close() -> None:
    if _hub is not None and _hub.alive:
        _hub.close()


class ExpeditionHub:
    def __init__(self, parent: tk.Misc) -> None:
        self._views: Dict[str, Any] = {}
        self._shell = WindowShell(
            parent, "Expedition", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._claim_close()
        self._shell.window.bind("<Escape>", lambda _e: self.close())
        self._tabs = Tabs(self._shell.body, wrap=False)
        self._tabs.pack(fill="both", expand=True, pady=(0, 4))
        self._pages = {name: self._tabs.add(title) for name, title in TABS}
        self._tabs.on_select = self._on_select

    # --- the window --------------------------------------------------------------------------------------------------
    @property
    def alive(self) -> bool:
        return self._shell.alive

    @property
    def window(self) -> tk.Toplevel:
        return self._shell.window

    def view(self, tab: str) -> Any:
        found = self._views.get(tab)
        return found if found is not None and found.alive else None

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def _claim_close(self) -> None:
        """A tab's window sets the close handler of the Toplevel it is built in; the host's must be the one that stays."""
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        for tab, found in list(self._views.items()):
            try:
                found.close()
            except Exception:                                  # noqa: BLE001 - a tab that fails to close must not keep the window open
                logger.debug("Could not close the %s tab", tab, exc_info=True)
        self._views.clear()
        self._shell.close()

    # --- the tabs --------------------------------------------------------------------------------------------------------
    def _index(self, tab: str) -> int:
        return [name for name, _title in TABS].index(tab)

    def show(self, tab: str, **options: Any) -> None:
        built = self._ensure(tab, **options)
        self._tabs.select(self._index(tab))
        if not built and self.view(tab) is not None:
            _builders[tab](self._shell.window, self._host(tab), **options)      # already built: pick the expedition, refresh
        self.lift()

    def _on_select(self, index: int) -> None:
        self._ensure(TABS[index][0])

    def _host(self, tab: str) -> Callable[..., TabShell]:
        return functools.partial(TabShell, page=self._pages[tab], on_close=lambda _shell, t=tab: self._views.pop(t, None))

    def _ensure(self, tab: str, **options: Any) -> bool:
        """Build the tab's window if it has none. True when it was built now."""
        if self.view(tab) is not None:
            return False
        builder = _builders.get(tab)
        if builder is None:
            return False
        self._views[tab] = builder(self._shell.window, self._host(tab), **options)
        self._claim_close()
        return True
