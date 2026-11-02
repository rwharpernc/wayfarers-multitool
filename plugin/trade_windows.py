"""Trade's three pages as windows: Session, Routes and Market. Each is its own pop-out (the window kit, plugin/uikit) opened from a button
on the Trade panel, in place of the ◀ ▶ arrows that used to page through them.

The windows hold no trading state. `trade_panel.TradePanelController` owns it all and, for a page, hands over what to show
(`page_content(page)`: the blocks and the header buttons) and, for Market, the search box and the Sell / Buy choice. A window draws that
and asks the controller to refresh them all whenever something changes. Module-level show / refresh_all / close_all follow
trade_watch_window.py."""
from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Tuple

from config import config

from . import trade_pages, trade_prices
from .trade_commodity_entry import CommodityEntry
from .trade_view import BlockView
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.widgets import FlatButton, ScrollFrame

DEFAULT_SIZE = (760, 680)
MIN_SIZE = (520, 420)
_SUBTITLES = {
    trade_pages.SESSION: "What you have traded this session, your hold and your carrier",
    trade_pages.ROUTES: "The best trade routes from where you are (Spansh)",
    trade_pages.MARKET: "Where to sell or buy a commodity (Spansh)",
}

ButtonSpec = Tuple[str, Callable[[], None], bool]      # caption, command, enabled

_windows: Dict[str, "TradePageWindow"] = {}


_GEOMETRY_KEYS = {
    trade_pages.SESSION: "wfmt_trade_window_geometry_session",
    trade_pages.ROUTES: "wfmt_trade_window_geometry_routes",
    trade_pages.MARKET: "wfmt_trade_window_geometry_market",
}


def geometry_key(page: str) -> str:
    return _GEOMETRY_KEYS[page]


def show(parent: tk.Misc, controller: Any, page: str) -> None:
    """Open the window for `page`, or bring it forward if it is already open."""
    window = _windows.get(page)
    if window is not None and window.alive:
        window.refresh()
        window.lift()
        return
    _windows[page] = TradePageWindow(parent, controller, page)


def is_open(page: str) -> bool:
    window = _windows.get(page)
    return window is not None and window.alive


def refresh_all() -> None:
    for window in list(_windows.values()):
        if window.alive:
            window.refresh()


def close_all() -> None:
    for window in list(_windows.values()):
        if window.alive:
            window.close()
    _windows.clear()


class TradePageWindow:
    def __init__(self, parent: tk.Misc, controller: Any, page: str) -> None:
        self._controller = controller
        self._page = page
        self._signature: Optional[tuple] = None
        self._side_row: Optional[tk.Frame] = None
        self._entry: Optional[CommodityEntry] = None

        self._shell = WindowShell(
            parent, page, _SUBTITLES.get(page, ""), size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(geometry_key(page)) or "",
            save_geometry=lambda geometry: config.set(geometry_key(page), geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)

        if page == trade_pages.MARKET:
            self._build_search_bar()

        scroll = ScrollFrame(self._shell.body, bg=P.PANE)
        scroll.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._view = BlockView(scroll.body, themed=False)
        self._view.pack(fill="x", anchor="n", padx=P.PAD, pady=P.PAD)
        self.refresh()

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        if self._entry is not None:
            self._controller.unbind_commodity_entry(self._entry)
            self._entry = None
        self._shell.close()

    def refresh(self) -> None:
        if not self.alive:
            return
        blocks, specs = self._controller.page_content(self._page)
        self._view.show(blocks)
        self._set_buttons(specs)
        if self._side_row is not None:
            self._paint_side()

    # --- the header buttons -------------------------------------------------------------------------------------------

    def _set_buttons(self, specs: List[ButtonSpec]) -> None:
        """Header buttons for the page. They are rebuilt only when a caption or an enabled state changes (the commands are the controller's
        own methods, so an older closure still works)."""
        signature = tuple((text, enabled) for text, _command, enabled in specs)
        if signature == self._signature:
            return
        self._signature = signature
        for child in self._shell.actions.winfo_children():
            child.destroy()
        for number, (text, command, enabled) in enumerate(specs):
            button = self._shell.add_action(text, command, accent=number == 0 and enabled,
                                            tip=self._controller.button_tip(text))
            button.set_enabled(enabled)

    # --- Market: the commodity box and the Sell / Buy choice ------------------------------------------------------------

    def _build_search_bar(self) -> None:
        bar = tk.Frame(self._shell.body, bg=P.BG)
        bar.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(bar, text="Commodity", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._entry = CommodityEntry(bar, self._controller.preferred_commodities,
                                     on_submit=lambda: self._controller.find_prices("near"))
        self._entry.pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._controller.bind_commodity_entry(self._entry)
        self._side_row = tk.Frame(bar, bg=P.BG)
        self._side_row.pack(side="left")
        tk.Label(self._side_row, text="I want to", fg=P.MUTED, bg=P.BG).pack(side="left", padx=(0, P.PAD_SM))
        self._side_buttons: Dict[str, tk.Frame] = {}
        self._painted_side: Optional[str] = None
        self._paint_side()

    def _paint_side(self) -> None:
        """Sell and Buy as two buttons, the chosen one lit. Rebuilt when the choice changes."""
        side = self._controller.side
        if side == self._painted_side:
            return
        self._painted_side = side
        for holder in self._side_buttons.values():
            holder.destroy()
        self._side_buttons = {}
        for value, text in ((trade_prices.SELL, "Sell"), (trade_prices.BUY, "Buy")):
            holder = tk.Frame(self._side_row, bg=P.BG)
            holder.pack(side="left", padx=(0, P.PAD_SM))
            FlatButton(holder, text, lambda v=value: self._controller.set_side(v),
                       kind="accent" if value == side else "normal",
                       tip=self._controller.button_tip(text)).pack()
            self._side_buttons[value] = holder
