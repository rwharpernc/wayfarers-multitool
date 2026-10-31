"""Builds the real Colony page of the main EDMC window (plugin/colonization_panel.py) with EDMC stubbed, and checks its
sections: the project rows with an active site, and the last five completed sites when none is under construction.
Run by test_colonization_panel_smoke.py in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
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


for n in ("myNotebook", "monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui",
          "win32process", "win32clipboard", "pywintypes", "psutil"):
    sys.modules[n] = Any(n)
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
        return default

    def get_int(self, key, default=0):
        return default

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

from plugin import colonization, colonization_data, colonization_panel as CP

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def make(market_id, name, complete=False, finished=""):
    entry = {"MarketID": market_id, "ConstructionProgress": 0.4, "ConstructionComplete": complete,
             "ResourcesRequired": [
                 {"Name": "$steel_name;", "Name_Localised": "Steel", "RequiredAmount": 500, "ProvidedAmount": 100},
                 {"Name": "$water_name;", "Name_Localised": "Water", "RequiredAmount": 50, "ProvidedAmount": 0}]}
    site = colonization.apply_depot_event(entry, None, name=name, system="Sol")
    if finished:
        site.completed_at = finished
    return site


repo = colonization_data.SiteRepository()
panel = CP.ColonizationController(repo)
panel._cmdr = "Bocheaux"
frame = tk.Frame(root)
panel.build_panel(frame)
root.update()


def shown(name):
    return bool(panel._shown.get(name))


def heading_drawn(key):
    return bool(panel._headings[key].grid_info())


check(panel._vars["project"].get() == CP._NO_CMDR_TEXT or "No active" in panel._vars["project"].get(), "an empty page says there is no active site")
check(not any(shown(n) for n in CP._DONE_ROWS) and not heading_drawn("recent"), "with no finished site the list is not drawn")

# Five and a half finished sites and nothing under construction: the five newest, newest first.
for index in range(6):
    repo.upsert("Bocheaux", make(10 + index, f"Station {index}", complete=True, finished=f"2026-10-0{index + 1}T10:00:00+00:00"))
panel._refresh_summary()
root.update()
lines = [panel._vars[n].get() for n in CP._DONE_ROWS]
check(lines[0] == "Station 5 (Sol) - 2026-10-06" and lines[4] == "Station 1 (Sol) - 2026-10-02", f"the five newest finished sites, newest first: {lines}")
check(all(shown(n) for n in CP._DONE_ROWS) and heading_drawn("recent"), "the list and its heading are drawn")
check(not heading_drawn("have") and not heading_drawn("finish") and not shown("hold"), "the project sections are not drawn without an active site")

# A site under construction brings the project sections back and the list goes.
repo.upsert("Bocheaux", make(1, "Depot One"))
panel._refresh_summary()
root.update()
check(heading_drawn("have") and heading_drawn("finish") and not heading_drawn("recent"), "the project sections replace the finished list")
check(shown("hold") and shown("to_get") and shown("coverage") and shown("trips") and not shown("carrier"), "no carrier row without a carrier")
check(panel._vars["needed"].get().endswith(" t"), f"still needed is a tonnage: {panel._vars['needed'].get()}")
check("next" not in panel._vars, "the Next line is gone")

if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  " + p)
    sys.exit(1)
print("COLONIZATION PANEL OK")
