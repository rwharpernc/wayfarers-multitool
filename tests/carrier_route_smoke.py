"""Opens the real Carrier Route window (plugin/carrier_route_window.py) with EDMC stubbed and Spansh faked: the carrier's details filled in from the journal, a route plotted for a destination,
the table, copying the next system, the route following the carrier through the journal, marking a jump by hand, clearing it, and the route coming back for the commander after a restart.
Run by test_carrier_route_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
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

from plugin import carrier_route as CR, carrier_route_panel, carrier_route_spansh, carrier_route_window as W  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(times=6):
    for _ in range(times):
        root.update()


STATS = {"event": "CarrierStats", "CarrierType": "FleetCarrier", "Callsign": "WLF-LXW", "Name": "ELDER WARDEN", "FuelLevel": 934,
         "SpaceUsage": {"TotalCapacity": 25000, "FreeSpace": 23331}}
HERE = {"event": "CarrierLocation", "CarrierType": "FleetCarrier", "StarSystem": "Khun", "SystemAddress": 3107241104074}
LEGS = [CR.CarrierLeg(1, "Alpha", 499.9, 5000.0, 1000.0, 89.0, 0, False, False, False, (0, 0, 0), 1, 2650.0),
        CR.CarrierLeg(2, "Beta", 500.0, 4500.0, 1000.0, 88.0, 0, True, True, False, (0, 0, 1), 2, 2560.0),
        CR.CarrierLeg(3, "Gamma", 50.0, 0.0, 0.0, 13.0, 0, True, False, True, (0, 0, 2), 3, 0.0)]
ASKED = []


def fake_plot(kind, start, destinations, used, work_out, tank, market, start_id=None, cancel=None, on_state=None):
    ASKED.append((kind, start, list(destinations), used, work_out, tank, market, start_id))
    if on_state is not None:
        on_state("Looking up Gamma")
    return CR.CarrierRoute(kind, start, destinations[-1], list(LEGS), 0, "Have 3,739 t of tritium at the start (1,000 in the tank, 2,739 in the carrier's market).")


folder = tempfile.mkdtemp()
planner = carrier_route_panel.planner
planner.start(folder)
planner.handle_event({"event": "LoadGame", "Commander": "Bocheaux"}, "Bocheaux")
planner.handle_event(STATS, "Bocheaux")
planner.handle_event(HERE, "Bocheaux")

with mock.patch.object(carrier_route_spansh, "plot", fake_plot):
    W.show(root)
    window = W._window
    pump()
    check(window._vars["start"].get() == "Khun" and window._vars["used"].get() == "1669" and window._vars["tank"].get() == "934",
          f"the carrier's place, space used and tritium come from the journal: {[window._vars[k].get() for k in ('start', 'used', 'tank')]}")
    check(str(window._entries["tank"].cget("state")) == "disabled", "the tank and market boxes wait while Spansh is asked to work the fuel out")
    window._work_out.set(False)
    window._fuel_mode()
    check(str(window._entries["tank"].cget("state")) == "normal", "unticking that lets you type them")
    window._work_out.set(True)
    window._fuel_mode()

    window._plot()                                                       # no destination yet
    check(not ASKED and "Give both" in window._shell._status.cget("text"), "no destination: nothing is sent")

    window._vars["end"].set("Gamma")
    window._plot()
    for _ in range(100):
        pump(2)
        time.sleep(0.05)
        if not window._busy:
            break
    check(len(ASKED) == 1 and ASKED[0][:4] == ("fleet", "Khun", ["Gamma"], 1669) and ASKED[0][4] is True and ASKED[0][7] == 3107241104074,
          f"Spansh was asked for the carrier at Khun, its address known: {ASKED}")
    route = planner.route
    check(route is not None and [leg.system for leg in route.legs] == ["Alpha", "Beta", "Gamma"], f"the route is kept: {route}")
    rows = [window._table.table._rows[iid].values for iid in window._table.table._order] if hasattr(window._table.table, "_rows") else []
    texts = window._summary.cget("text")
    check("3 jumps" in texts and "Have 3,739 t" in texts, f"the summary says what is needed at the start: {texts!r}")

    window._copy_next()
    check(root.clipboard_get() == "Alpha", f"Copy next system puts the next system on the clipboard: {root.clipboard_get()!r}")
    window._copy_all()
    check(root.clipboard_get().splitlines() == ["Alpha", "Beta", "Gamma"], "Copy all remaining lists every system left")

    planner.handle_event({"event": "CarrierLocation", "CarrierType": "FleetCarrier", "StarSystem": "Alpha", "SystemAddress": 1}, "Bocheaux")
    pump()
    check(planner.route.reached == 1 and planner.route.next_leg.system == "Beta", "the carrier arriving at the first system moves the route on")
    planner.handle_event({"event": "CarrierJump", "StarSystem": "Beta", "SystemAddress": 2, "StationName": "WLF-LXW"}, "Bocheaux")
    check(planner.route.reached == 2, "a carrier jump you were aboard for does the same")
    planner.handle_event({"event": "CarrierJump", "StarSystem": "Gamma", "SystemAddress": 3, "StationName": "SOMEONE-ELSE"}, "Bocheaux")
    check(planner.route.reached == 2, "another carrier's jump does not")

    window._mark_reached()
    check(planner.route.reached == 3 and planner.route.next_leg is None, "Mark next as reached moves it on by hand")
    window._copy_next()
    check("arrived" in window._shell._status.cget("text"), "nothing is left to copy once it has arrived")

    # a restart: a new owner reads the saved route back for the commander, and another commander sees none
    planner.set_route(CR.CarrierRoute(CR.FLEET, "Khun", "Gamma", list(LEGS)))
    fresh = carrier_route_panel.CarrierRoutePlanner()
    fresh.start(folder)
    fresh.follow_commander("Bocheaux")
    check(fresh.route is not None and fresh.route.end == "Gamma" and len(fresh.route.legs) == 3, "the route comes back for the commander after a restart")
    fresh.follow_commander("Other Commander")
    check(fresh.route is None, "another commander does not see it")

    check(window._planner.clear_route() and planner.route is None, "Clear route lets go of it")
    window.close()
root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("CARRIER ROUTE OK")
