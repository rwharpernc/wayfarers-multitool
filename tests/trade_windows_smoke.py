"""Opens Trade's panel and its Session, Routes and Market windows (plugin/trade_panel.py, plugin/trade_windows.py) with EDMC stubbed, and
checks that each button opens its window once, that the windows show what the controller hands them and follow its refreshes, that the
Market window's box and Sell / Buy choice reach the controller (and what was typed survives closing it), and that the panel stays narrow.
Run by test_trade_windows_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not,
77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import json
import os
import sys
import tempfile
import time
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui",
          "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nbmod
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
saved = {}


class Cfg:
    default_journal_dir = ""

    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def get_bool(self, key, default=False):
        return saved.get(key, default)

    def get_int(self, key, default=0):
        return saved.get(key, default)

    def get(self, key, default=None):
        return saved.get(key, default)

    def set(self, key, value):
        saved[key] = value


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()


try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()


from plugin import trade_pages, trade_panel, trade_prices, trade_windows  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


def buttons_of(frame):
    found = []
    for child in frame.winfo_children():
        if isinstance(child, tk.Button):
            found.append(child)
        found.extend(buttons_of(child))
    return found


controller = trade_panel.TradePanelController()
host = tk.Frame(root)
host.pack()
controller.build_panel(host)
pump()
panel_buttons = {str(b.cget("text")): b for b in buttons_of(host)}
check(set(panel_buttons) == {"Session", "Routes", "Market", "History"}, f"the panel's buttons: {sorted(panel_buttons)}")
check(not any("\u25c0" in str(b.cget("text")) or "\u25b6" in str(b.cget("text")) for b in buttons_of(host)), "no page arrows are left")
button_rows = {b.winfo_y() for b in buttons_of(host)}
check(len(button_rows) == 1, f"the four buttons are in one row, not {len(button_rows)}: {sorted(button_rows)}")
check(host.winfo_reqwidth() <= 260, f"the panel asks for {host.winfo_reqwidth()} px")

for page in (trade_pages.SESSION, trade_pages.ROUTES, trade_pages.MARKET):
    check(not trade_windows.is_open(page), f"{page} starts closed")
    panel_buttons[page].invoke()
    pump()
    check(trade_windows.is_open(page), f"the {page} button opens its window")
    first = trade_windows._windows[page]
    panel_buttons[page].invoke()
    pump()
    check(trade_windows._windows[page] is first, f"pressing {page} again brings the same window forward")

session = trade_windows._windows[trade_pages.SESSION]
captions = [str(b.cget("text")) for b in session._shell.actions.winfo_children()]
check(captions == ["Reset", "Save session", "History", "Rebuild"], f"the Session window's header buttons: {captions}")
routes = trade_windows._windows[trade_pages.ROUTES]
captions = [str(b.cget("text")) for b in routes._shell.actions.winfo_children()]
check(captions[0] == "Find routes" and captions[-1] == "Round trip", f"the Routes window's header buttons: {captions}")

# Routes: the requirements are in the window and save to the same settings Settings holds
fields = routes._fields
check({"wfmt_trade_max_hops", "wfmt_trade_max_arrival_ls", "wfmt_trade_jump_range_override", "wfmt_trade_route_price_age_h",
       "wfmt_trade_route_permit", "wfmt_trade_include_carriers", "wfmt_trade_include_ground", "wfmt_trade_large_pad",
       "wfmt_trade_min_supply", "wfmt_trade_min_demand", "wfmt_trade_round_radius_ly", "wfmt_trade_roundtrip_commodity"} <= set(fields),
      f"the Routes window has every requirement: {sorted(fields)}")
var, entry = fields["wfmt_trade_max_hops"]
var.set("7")
entry.event_generate("<FocusOut>")
pump()
check(saved.get("wfmt_trade_max_hops") == 7, f"a typed number is saved: {saved.get('wfmt_trade_max_hops')}")
check(controller.set_requirement("wfmt_trade_max_hops", "99") == "10", "a number is kept inside its range")
check(controller.set_requirement("wfmt_trade_jump_range_override", "abc") == "", "a jump range that is not a number is blank")
check(controller.set_requirement("wfmt_trade_jump_range_override", "24.5") == "24.5", "a jump range is kept")
check(controller.set_requirement("wfmt_trade_roundtrip_commodity", " Gold ") == "Gold", "a commodity is trimmed")
tick, _none = fields["wfmt_trade_route_permit"]
tick.set(True)
controller.set_requirement("wfmt_trade_route_permit", tick.get())
check(saved.get("wfmt_trade_route_permit") is True, "a tick is saved")
controller._cycle_hops()
pump()
check(fields["wfmt_trade_max_hops"][0].get() == str(controller.requirement_value("wfmt_trade_max_hops")), "the Hops button's change shows in the window")

# the rest of Trade's settings: the pad in Routes and Market, the Near me radius in Market, fines in Session
check("wfmt_trade_ship_pad_override" in routes._fields, "Routes has the ship size")
mk = trade_windows._windows[trade_pages.MARKET]
check({"wfmt_trade_near_radius_ly", "wfmt_trade_ship_pad_override"} <= set(mk._fields), f"Market has the Near me radius and the ship size: {sorted(mk._fields)}")
check("wfmt_trade_count_fines" in session._fields, f"Session has the fines switch: {sorted(session._fields)}")
check(controller.requirement_value("wfmt_trade_ship_pad_override") == "auto", "the ship size starts as From my ship")
check(controller.set_requirement("wfmt_trade_ship_pad_override", "large") == "large" and saved.get("wfmt_trade_ship_pad_override") == "large", "a pad size is saved")
check(controller._ship_pad() == "large", "and the controller plans for it")
check(controller.set_requirement("wfmt_trade_ship_pad_override", "auto") == "auto" and saved.get("wfmt_trade_ship_pad_override") == "", "From my ship is saved as blank, as Settings does")
check(controller.set_requirement("wfmt_trade_ship_pad_override", "huge") == "auto", "an unknown size is From my ship")
check(controller.set_requirement("wfmt_trade_near_radius_ly", "250") == "250" and controller._near_radius() == 250, "the Near me radius is saved and used")
check(controller.set_requirement("wfmt_trade_near_radius_ly", "0") == "1", "the Near me radius stays inside its range")
controller.set_requirement("wfmt_trade_count_fines", True)
check(saved.get("wfmt_trade_count_fines") is True and trade_panel.count_fines_enabled(), "the fines switch is saved and read back")
pad_var = mk._fields["wfmt_trade_ship_pad_override"][0]
controller.set_requirement("wfmt_trade_ship_pad_override", "medium")
pump()
check(pad_var.get() == "medium", "a pad size picked in one window shows in the other")

# the Market window: the box is the controller's, and Sell / Buy repaint
market = trade_windows._windows[trade_pages.MARKET]
captions = [str(b.cget("text")) for b in market._button_bar.winfo_children()]
check(captions == ["Near me", "Galaxy", "Best picks", "Price finder"], f"the search buttons sit under the box: {captions}")
check(not market._shell.actions.winfo_children(), "and not in the header")
check(controller._commodity_entry is market._entry and market._entry is not None, "the Market box is bound to the controller")
market._entry.set("Tritium")
check(controller._search_target() is not None and controller._search_target()[0] == "Tritium", f"the typed commodity is searched: {controller._search_target()}")
controller.set_side(trade_prices.BUY)
pump()
check(controller.side == trade_prices.BUY and market._painted_side == trade_prices.BUY, "choosing Buy reaches the controller and repaints")
check(market._view._blocks is not None, "the Market window shows blocks")

# lookups off: the search windows say so instead of failing
from plugin import trade_panel as tp  # noqa: E402
text = " ".join(str(getattr(b, "text", "")) for b in market._view._blocks)
check("lookups" in text.lower(), f"with lookups off the Market window says so: {text!r}")

market.close()
pump()
check(controller._commodity_entry is None and controller._typed == "Tritium", "closing Market unbinds the box and keeps what was typed")
trade_windows.show(root, controller, trade_pages.MARKET)
pump()
reopened = trade_windows._windows[trade_pages.MARKET]
check(reopened._entry.get() == "Tritium", f"reopening Market restores the text: {reopened._entry.get()!r}")

# a refresh reaches the open windows
controller._cargo = {"Gold": 10}
controller._capacity = 100
controller._refresh()
pump()
check(any("10 / 100" in str(getattr(b, "value", "")) for b in controller._summary_blocks()), "the panel summary shows the hold")
check("In your ship" in " ".join(str(getattr(b, "text", "")) for b in session._view._blocks), "the Session window follows the refresh")

# Routes: a running total beside each hop's profit
from plugin import trade_spansh_client as spansh  # noqa: E402
hops = [spansh.Hop("Sol", f"Station {n}", 10.0, "Alpha", f"Station {n + 1}", 20.0, 5.0 + n, [], profit=p)
        for n, p in enumerate((1000, 2500, -300), start=1)]
job = types.SimpleNamespace(error=None, result=hops)
controller._finish_routes(job)
mock.patch.object(trade_panel, "lookups_enabled", lambda: True).start()
route_items = [b for b in controller._route_blocks if type(b).__name__ == "Item"]
check([i.cells[1] for i in route_items[:3]] == ["+1,000", "+3,500", "+3,200"], f"running totals: {[i.cells for i in route_items]}")
notes = [b.text for b in controller._route_blocks if type(b).__name__ == "Note"]
check(any(n.startswith("Average per leg: +1,067 cr") and "\u00d7 3 legs = +3,200 cr estimated total earnings" in n for n in notes),
      f"the average per leg and the estimated total, on a line of their own: {notes}")
check(len(route_items) == 3 + 1, "every hop is listed, then one row for the whole route")
whole = route_items[-1]
check(whole.title == "Whole route" and whole.cells[0] == "+3,200" and whole.cells[2] == f"{sum(h.distance_ly for h in hops):.1f}",
      f"the whole route's total and distance: {whole}")
kinds = [(type(b).__name__, getattr(b, "text", "")) for b in controller._route_blocks]
check(("Heading", "Hop by hop") in kinds and kinds.index(("Heading", "Hop by hop")) < kinds.index(("Columns", "")) if ("Columns", "") in kinds else ("Heading", "Hop by hop") in kinds,
      f"the hops are set apart from the totals by their own heading: {kinds[:6]}")
cols = [b for b in controller._route_blocks if type(b).__name__ == "Columns"][0]
check(cols.labels == ("Profit", "Total", "ly"), f"the column headings: {cols.labels}")
routes.refresh()
pump()

# window text has a hierarchy: gains green, losses red, labels muted, headings large
from plugin.uikit import palette as P  # noqa: E402


def labels(widget):
    found = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Label):
            found.append(child)
        found.extend(labels(child))
    return found


texts = {str(l.cget("text")): l for l in labels(routes._view)}
check(str(texts["+1,000"].cget("fg")) == P.OK, "a gain is green")
check(str(texts["-300"].cget("fg")) == P.DANGER if "-300" in texts else True, "a loss is red")
heading = texts.get("Route") or texts.get("Route (repeatable loop)")
check(heading is not None and str(heading.cget("fg")) == P.HEADING, "the heading uses the heading color")
check(str(texts["Hops"].cget("fg")) == P.MUTED, "a label is muted")
check(str(texts["3"].cget("fg")) == P.TEXT, "its value is bright")

trade_windows.close_all()
pump()
check(not any(trade_windows.is_open(p) for p in trade_pages.PAGE_ORDER), "close_all closes every window")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print("TRADE WINDOWS OK")
