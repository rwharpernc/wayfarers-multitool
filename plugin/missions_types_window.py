"""The Mission types window: Missions mode's category pages (Massacre, Settlement Raids, Combat, Trade & Mining, Passenger, Covert / On-Foot
Ops, Other, and Community Goals), one at a time, in a window of their own. They used to be paged through with ◀ ▶ on the main panel, which now shows
only the count for each type.

The page itself is drawn by the panel's own code (`missions_ui.MissionsUI.render_category`: the kill-stacking cards, the mission cards, the Community
Goal page), here with this window's colors and width. A list of the types, each with its count, picks the page. Built on the window kit
(plugin/uikit); module-level show / refresh / close follow trade_watch_window.py."""
from __future__ import annotations

import tkinter as tk
from typing import Any, Dict, Optional

from config import config

from . import missions_display_settings as display_settings
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.widgets import FlatButton, ScrollFrame

CONFIG_GEOMETRY = "wfmt_missions_types_window_geometry"
CONFIG_CATEGORY = "wfmt_missions_types_window_category"
DEFAULT_SIZE = (780, 720)
MIN_SIZE = (560, 480)
_WIDTH_STEP = 40       # the page is drawn again when the window's width changes by more than this

_window: Optional["MissionTypesWindow"] = None


def show(parent: tk.Misc, ui: Any, category: Optional[str] = None) -> None:
    """Open the window, or bring it forward, on `category` if one is given."""
    global _window
    if _window is not None and _window.alive:
        if category:
            _window.pick(category)
        else:
            _window.refresh()
        _window.lift()
        return
    _window = MissionTypesWindow(parent, ui, category)


def refresh() -> None:
    if _window is not None and _window.alive:
        _window.refresh()


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


class MissionTypesWindow:
    def __init__(self, parent: tk.Misc, ui: Any, category: Optional[str]) -> None:
        self._ui = ui
        saved = config.get_str(CONFIG_CATEGORY) or ""
        order = ui.category_order()
        self._category = category if category in order else saved if saved in order else order[0]
        self._drawn_width = 0
        self._buttons: Dict[str, FlatButton] = {}

        self._shell = WindowShell(
            parent, "Mission types", "Your missions by type", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)

        body = self._shell.body
        body.columnconfigure(1, weight=1)
        body.rowconfigure(1, weight=1)
        self._display = display_settings.DisplayCard(body)
        self._display.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, P.PAD_SM))
        self._list = tk.Frame(body, bg=P.BG)
        self._list.grid(row=1, column=0, sticky="ns", padx=(0, P.PAD))
        self._scroll = ScrollFrame(body, bg=P.PANE)
        self._scroll.grid(row=1, column=1, sticky="nsew")
        self._scroll.body.columnconfigure(0, weight=1)
        self._scroll.bind("<Configure>", self._on_resize)
        self.refresh()

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._shell.close()

    @property
    def category(self) -> str:
        return self._category

    def pick(self, category: str) -> None:
        if category not in self._ui.category_order():
            return
        self._category = category
        config.set(CONFIG_CATEGORY, category)
        self.refresh()

    def refresh(self) -> None:
        if not self.alive:
            return
        self._display.sync()
        counts = self._ui.category_counts()
        self._fill_list(counts)
        self._draw_page()

    def _on_resize(self, event: tk.Event) -> None:
        if abs(event.width - self._drawn_width) > _WIDTH_STEP:
            self._draw_page()

    # --- the list of types ----------------------------------------------------------------------------------------------

    def _fill_list(self, counts: Dict[str, int]) -> None:
        """One button for each type with its count; the chosen one is lit. Rebuilt on every refresh (they are few)."""
        for child in self._list.winfo_children():
            child.destroy()
        self._buttons = {}
        for key in self._ui.category_order():
            label = f"{self._ui.category_label(key)} ({counts.get(key, 0)})"
            button = FlatButton(self._list, label, lambda k=key: self.pick(k),
                                kind="accent" if key == self._category else "normal",
                                tip=f"{self._ui.category_label(key)} - show the missions of this type")
            button.pack(fill="x", pady=(0, 4))
            if not counts.get(key, 0) and key != self._category:
                button.set_enabled(True)       # an empty type can still be opened; it says so on its page
            self._buttons[key] = button

    # --- the page ---------------------------------------------------------------------------------------------------

    def _draw_page(self) -> None:
        width = self._scroll.winfo_width()
        self._drawn_width = width
        self._scroll.clear()
        self._ui.render_category(self._scroll.body, self._category, max(width, 300))
