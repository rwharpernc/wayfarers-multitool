"""Opens the What pays window (plugin/mining_what_pays_dialog.py) with Spansh replaced by a stand-in, and checks the table, the order, a failure part way and the report. Run by
test_mining_what_pays_smoke in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
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


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes",
          "psutil", "ttkHyperlinkLabel", "theme"):
    sys.modules[n] = Any(n)
nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nbmod
saved = {}


class Cfg:
    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def get_bool(self, key, default=False):
        return saved.get(key, default)

    def get_int(self, key, default=0):
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
root.geometry("300x200")
root.update()

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(window, limit=200):
    for _ in range(limit):
        root.update()
        if not window._busy:
            return
        root.after(20)
        root.update()
    problems.append("the search did not finish")


def station(price):
    from plugin import mining_spansh_client as spansh
    return spansh.StationPrice(station=f"Hub {price}", system="Sol", station_type="Orbis", distance_ly=10.0, distance_to_arrival_ls=500.0, is_planetary=False, price=price, quantity=900,
                               small_pads=0, medium_pads=1, large_pads=1)


try:
    from plugin import mining_ground, mining_hotspots as hotspots, mining_what_pays_dialog as dialog

    dialog.PAUSE_S = 0.0
    for material in ("Painite", "Platinum", "Bromellite"):
        hotspots.hotspot_repository.add(hotspots.Hotspot(system="Sol", body=f"Sol {material[0]}", material=material))
    prices = {"Painite": 500000, "Platinum": 150000}
    asked = []
    extras = []

    def fake_search(origin, commodity, transaction, distance, **kwargs):
        extras.append((commodity, kwargs.get("min_quantity"), kwargs.get("exclude_carriers"), kwargs.get("station_types")))
        asked.append((origin, commodity, transaction, distance, kwargs.get("max_results"), kwargs.get("this_system_only")))
        return [station(prices[commodity])] if commodity in prices else []

    with mock.patch.object(dialog, "search_stations", fake_search):
        dialog.open_dialog(root, "Sol", [], mining_ground.OwnRates([]))
        window = dialog._window
        check(window is not None and window.alive, "the window opens")
        pump(window)
        order = [window._table._rows[iid].values[0] for iid in window._table._order]
        check(order == ["Painite", "Platinum", "Bromellite"], f"best price first, unpriced last (got {order})")
        first = window._table._rows[window._table._order[0]].values
        check("500,000" in first[1] and first[2] == "Hub 500000" and first[7] == "1 medium, 1 large", f"the best offer's cells are filled in (got {first})")
        check(window._table._rows[window._table._order[2]].values[1] == "No station found", "a commodity nobody pays for says so")
        check(len(asked) == 3 and all(a[0] == "Sol" and a[2] == "Sell" and a[3] == 100.0 and a[4] == 1 and a[5] is False for a in asked), f"one sell search each, within 100 ly (got {asked})")
        check(all(e[1] == 1 and e[2] is True and e[3] and "Drake-Class Carrier" not in e[3] for e in extras), f"no hold: a floor of 1 t, carriers left out (got {extras})")
        check("What pays, within 100 ly of Sol:" in window._report and "1. Painite: 500,000 cr" in window._report, "the report is the ranking")
        check(window._busy is False, "the search button is free again")

        # what is in the hold sets that commodity's demand floor, and only that commodity's
        del extras[:]
        with mock.patch.object(dialog.pays, "hold", lambda: {"painite": 12, "drones": 4}):
            window.search()
            pump(window)
        check({e[0]: e[1] for e in extras} == {"Painite": 12, "Platinum": 1, "Bromellite": 1}, f"the floor is the tons held (got {extras})")

        # a failure part way keeps what was found and says so
        def failing_search(origin, commodity, transaction, distance, **kwargs):
            if commodity == "Platinum":
                raise OSError("down")
            return [station(prices.get(commodity, 1))]

        with mock.patch.object(dialog, "search_stations", failing_search):
            window.search()
            pump(window)
        check(len(window._rows) == 1 or len(window._rows) == 2, f"rows found before the failure are kept (got {len(window._rows)})")
        check("did not answer" in window._shell._status.cget("text"), "the status says Spansh did not answer")
        window.close()

        # nothing recorded: nothing to price, and the window says what to do
        hotspots.hotspot_repository._hotspots.clear()
        dialog.open_dialog(root, "Sol", [], mining_ground.OwnRates([]))
        empty = dialog._window
        pump(empty)
        check("Nothing to price yet" in empty._shell._status.cget("text"), "with nothing recorded it says what to do")
        check(len(asked) == 6, "and it asks Spansh nothing more")
        empty.close()
except Exception as exc:  # noqa: BLE001
    import traceback
    problems.append("raised: " + "".join(traceback.format_exception(exc)))

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("MINING WHAT PAYS OK")
