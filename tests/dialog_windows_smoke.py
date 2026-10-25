"""Opens the rebuilt dialogs for real with EDMC stubbed: the Add/Edit Hotspot and Ship Build forms (plugin/uikit/form.py), the Import and Export window and the Market Research window. A form fills from
its values, shows an error and stays open on a bad value, saves normalized values and closes; the windows survive the panel's content frame being destroyed; Market Research groups its rows by commodity.
Run by test_dialog_windows_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import time
import types
from datetime import datetime, timedelta, timezone
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil",
          "ttkHyperlinkLabel", "myNotebook", "theme"):
    sys.modules[n] = Any(n)
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

from plugin import mining_ground, mining_hotspot_dialog as HD, mining_hotspot_import_export as IE, mining_hotspots, mining_market_research as research  # noqa: E402
from plugin import mining_market_research_dialog as MR, ship_builds_dialog as SD  # noqa: E402
from plugin.ship_builds_data import ShipBuild  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(seconds=0.0):
    end = time.time() + seconds
    root.update()
    while time.time() < end:
        root.update()
        time.sleep(0.01)


def wait_for(condition, seconds=5.0):
    end = time.time() + seconds
    while time.time() < end:
        pump(0.02)
        if condition():
            return True
    return False


def capture(module):
    """Make `module.FormDialog` remember the form it opened."""
    made = []
    real = module.FormDialog

    class Spy(real):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            made.append(self)

    module.FormDialog = Spy
    return made


# --- the hotspot form ---------------------------------------------------------------------------------------------------
forms = capture(HD)
got = []
panel_content = tk.Frame(root)
HD.open_hotspot_dialog(panel_content, got.append, prefill_system="Sol", prefill_body="Mars 1", prefill_latitude=10.5, prefill_longitude=20.0)
form = forms[-1]
for child in panel_content.winfo_children():
    child.destroy()
panel_content.destroy()
pump(0.2)
check(form.alive, "the hotspot form was destroyed with the panel's content frame")
check(form._vars["system"].get() == "Sol" and form._vars["latitude"].get() == "10.5", "the hotspot form was not filled from the prefill")
form.submit()
check(form.alive and "required" in form._error.cget("text"), f"a missing material should stay open with a message: {form._error.cget('text')!r}")
form._vars["material"].set("painite")
form._vars["rigs"].set("9")
form.submit()
check(form.alive and "Rigs must be 1 to" in form._error.cget("text") and not got, f"a bad rigs value should stay open: {form._error.cget('text')!r}")
form._vars["rigs"].set("4")
form._vars["amount"].set("High")
form.submit()
check(not form.alive, "a good form should close")
check(len(got) == 1 and got[0].material == "Painite" and got[0].rigs == 4 and got[0].amount == "High", f"the saved hotspot: {got}")

old = mining_hotspots.Hotspot(system="Alpha", body="A 1", material="Gold", rigs=3, latitude=1.0, longitude=2.0, mined_tons=40)
HD.open_hotspot_dialog(root, got.append, existing=old)
edit = forms[-1]
check(edit._shell.window.title() == "Edit Hotspot" and edit._vars["material"].get() == "Gold", "the edit form was not filled from the hotspot")
edit._vars["notes"].set("later")
edit.submit()
check(got[-1].mined_tons == 40 and got[-1].notes == "later", f"an edit should keep the mined tons: {got[-1]}")

# --- the ship build form ------------------------------------------------------------------------------------------------
forms = capture(SD)
builds = []
SD.open_ship_build_dialog(root, builds.append, prefill_ship="Anaconda")
ship = forms[-1]
check(ship._vars["ship"].get() == "Anaconda", "the ship build form was not filled with the ship being flown")
ship.submit()
check(ship.alive and "required" in ship._error.cget("text"), "a missing name should stay open")
ship._vars["name"].set("Explorer")
ship._vars["url"].set("edsy.org/x")
ship.submit()
check(ship.alive and "http" in ship._error.cget("text"), f"a link without http should stay open: {ship._error.cget('text')!r}")
ship._vars["url"].set("https://edsy.org/x")
ship.submit()
check(not ship.alive and len(builds) == 1 and builds[0].name == "Explorer", f"the saved build: {builds}")
ship2 = None
SD.open_ship_build_dialog(root, builds.append, existing=ShipBuild(id="abc", ship="Python", name="Trader", site="EDSY", url="https://x"))
ship2 = forms[-1]
check(ship2._shell.window.title() == "Edit Ship Build" and ship2._vars["name"].get() == "Trader", "the ship build edit form was not filled")
ship2.close()

# --- import and export --------------------------------------------------------------------------------------------------
IE.open_import_export_dialog(tk.Frame(root))
window = IE._window
check(window is not None and window.alive, "the import and export window did not open")
check("saved hotspots" in window._subtitle.cget("text"), f"its subtitle: {window._subtitle.cget('text')!r}")
IE.open_import_export_dialog(tk.Frame(root))
check(IE._window is window, "a second press should raise the open window")
window.close()

# --- market research ----------------------------------------------------------------------------------------------------
candidate = research.Candidate("Painite", ("saved here", "your records"))
buyer = research.Buyer(station="Here Port", station_type="Coriolis Starport", is_planetary=False, price=51000, demand=900, updated=datetime.now(timezone.utc),
                       distance_ls=1234.0, large_pads=3, medium_pads=1, small_pads=0)
camp = research.Buyer(station="Dust Camp", station_type="planetary outpost", is_planetary=True, price=50000, demand=10, updated=None, distance_ls=None,
                      large_pads=0, medium_pads=0, small_pads=2)
rows = MR.table_rows([research.CommodityResult(candidate, (buyer, camp)), research.CommodityResult(research.Candidate("Gold", ("typed",)), ())])
check([group for group, _ in rows] == [True, False, False, True, False], f"the market rows are not grouped by commodity: {[g for g, _ in rows]}")
check(rows[1][1][:7] == ("Here Port", "51,000", "900", "Today", "1,234", "Large pads", "Orbital Coriolis Starport"), f"the first market row: {rows[1][1]}")
check(rows[2][1][5:7] == ("Small pads only", "Ground Planetary Outpost"), f"the second market row: {rows[2][1]}")
check("No market in this system buys it" in rows[4][1][0], "a commodity nobody buys should say so")

mining_hotspots.hotspot_repository.add_or_merge(mining_hotspots.Hotspot(system="Sol", body="Mars 1", material="Painite", rigs=4, latitude=1.0, longitude=1.0), 1_000_000.0)
stations = [{"name": "Here Port", "type": "Coriolis Starport", "is_planetary": False, "distance_to_arrival": 1234.0, "large_pads": 3, "market_updated_at": (datetime.now(timezone.utc) - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "market": [{"commodity": "Painite", "sell_price": 51000, "demand": 900}]}]
asked = []


def fake_search(system, days):
    asked.append((system, days))
    return stations, len(stations)


MR.search_stations = fake_search
MR.open_dialog(tk.Frame(root), "Sol", [], mining_ground.OwnRates([], {}))
win = MR._window
check(win is not None and win.alive, "the market research window did not open")
check(wait_for(lambda: len(win._table) >= 2), f"the market research table did not fill: {len(win._table)} rows")
check(asked and asked[0] == ("Sol", 30), f"the search asked for: {asked}")
check("Painite" in win._report and "Here Port" in win._report, "the copyable report is missing the findings")
check(win._table._rows["m1"].values[3] in ("Today", "1 d ago"), f"the Updated column should read from Spansh's stamp: {win._table._rows['m1'].values}")
check("1 market with prices updated" in win._shell._status.cget("text"), f"the status line: {win._shell._status.cget('text')!r}")
win.close()

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("DIALOG WINDOWS OK")
