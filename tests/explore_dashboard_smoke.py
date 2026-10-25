"""Opens the real Exploration Dashboard (plugin/explore_dashboard.py, explore_dashboard_window.py) with EDMC stubbed, feeds the system survey and Status.json, and checks
the panel row, the four tabs, the tables, landing and lifting off, the two overlay switches and a refresh with nothing changed. Run by test_explore_dashboard_smoke in a
subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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

from plugin import explore_dashboard as DASH, explore_dashboard_window as WIN, overlay, system_survey  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(times=4):
    for _ in range(times):
        root.update()


def texts(widget):
    """Every label text under a widget."""
    found = []
    if isinstance(widget, tk.Label):
        found.append(str(widget.cget("text")))
    for child in widget.winfo_children():
        found.extend(texts(child))
    return found


def all_buttons_text(widget):
    """The text of every button under a widget (the section builds into a folding body frame)."""
    found = [str(widget.cget("text"))] if isinstance(widget, tk.Button) else []
    for child in widget.winfo_children():
        found.extend(all_buttons_text(child))
    return found


def all_text(widget):
    return "\n".join(texts(widget))


def table_rows(box):
    return len(box.table)


# --- the system ---------------------------------------------------------------------------------------------------------------
survey = system_survey.survey
survey.reset("Smoke Sys", 7)
survey.playing, survey.in_transit, survey.docked = True, False, False
survey.handle_event({"event": "FSSDiscoveryScan", "BodyCount": 4, "Progress": 0.5})
survey.handle_event({"event": "Scan", "BodyID": 0, "BodyName": "Smoke Sys", "StarSystem": "Smoke Sys", "StarType": "K", "StellarMass": 0.8, "DistanceFromArrivalLS": 0.0})
survey.handle_event({"event": "Scan", "BodyID": 1, "BodyName": "Smoke Sys 1", "StarSystem": "Smoke Sys", "PlanetClass": "Water world", "MassEM": 1.1, "WasDiscovered": False,
                     "WasMapped": False, "DistanceFromArrivalLS": 320.0, "SurfaceGravity": 11.0, "SurfaceTemperature": 300.0, "Atmosphere": "a thick Oxygen atmosphere",
                     "AtmosphereComposition": [{"Name": "Oxygen", "Percent": 99.0}]})
survey.handle_event({"event": "Scan", "BodyID": 2, "BodyName": "Smoke Sys 2", "StarSystem": "Smoke Sys", "PlanetClass": "Rocky body", "MassEM": 0.04, "Landable": True,
                     "WasFootfalled": False, "DistanceFromArrivalLS": 800.0, "SurfaceGravity": 2.0, "Materials": [{"Name": "iron", "Percent": 20.0}]})
survey.handle_event({"event": "FSSBodySignals", "BodyID": 2, "BodyName": "Smoke Sys 2", "Signals": [{"Type": "$SAA_SignalType_Biological;", "Count": 2}]})

# --- the panel row ------------------------------------------------------------------------------------------------------------
frame = tk.Frame(root)
frame.pack()
DASH.start(repo)
DASH.build_panel(frame)
pump()
from plugin import exploration_value as EV  # noqa: E402
check(EV._NO_SCAN_TEXT in all_text(frame), "the Exploration Value lines are drawn inside the Dashboard section")
check("Exploration Value" not in all_text(frame), "there is no section of its own called Exploration Value")
check("DASHBOARD" in all_buttons_text(frame), "the panel has a DASHBOARD button")
DASH.handle_event({"event": "Scan"}, "CMDR A", "Smoke Sys", None, {})
root.after(400, root.quit)
root.mainloop()
check("Smoke Sys" in all_text(frame), "the panel line names the system after an event")

# --- open the window in space --------------------------------------------------------------------------------------------------
space = {"Flags": 0x1000000, "BodyName": "Smoke Sys 1"}
DASH.dashboard_status(space)
DASH.controller._open()
pump(8)
check(WIN.is_open(), "the window opened")
window = WIN._window
check(window._tabs.selected == WIN.TAB_ORBIT, "in space the window opens on Orbit (got %s)" % window._tabs.selected)
overview = all_text(window._tabs._tabs[WIN.TAB_OVERVIEW][2])
check("Smoke Sys" in overview and "bodies scanned" in overview, "the overview names the system and counts bodies")
check("first discoveries here" in overview, "the overview counts first discoveries")
check(table_rows(window._bodies) == 3, "the Orbit table lists the three scanned bodies (got %s)" % table_rows(window._bodies))
check(table_rows(window._map_box) >= 1, "worth-mapping lists the water world")
check(table_rows(window._life_box) == 1, "the life list has the body with biology")
window._select_body("2")
pump()
check("iron" in all_text(window._detail_body), "selecting a body shows its materials")

# --- landing switches to the Surface tab, lifting off back -----------------------------------------------------------------------
DASH.dashboard_status({"Flags": 1 << 1 | 0x1000000, "BodyName": "Smoke Sys 2", "Latitude": 10.0, "Longitude": 20.0, "Heading": 45, "Altitude": 0.0})
WIN.refresh_position()
pump()
check(window._tabs.selected == WIN.TAB_SURFACE, "landing switches to Surface (got %s)" % window._tabs.selected)
check("Landed" in all_text(window._tabs._tabs[WIN.TAB_SURFACE][2]), "the Surface tab says Landed")
check("iron" in all_text(window._tabs._tabs[WIN.TAB_SURFACE][2]), "the Surface tab shows the body's materials")
window._tabs.select(WIN.TAB_EXPLORATION)
DASH.controller._status = {"Flags": 0x1000000}
window._perspective = WIN.D.GROUND
window.refresh()
check(window._tabs.selected == WIN.TAB_EXPLORATION, "a tab chosen by hand is left alone when the view does not change")
check("none running" in all_text(window._tabs._tabs[WIN.TAB_EXPLORATION][2]), "the Exploration tab says no expedition is running")

# --- the overlay switches --------------------------------------------------------------------------------------------------------
sent = []
with mock.patch.object(overlay.OverlayClient, "_send_raw", lambda _self, payload: sent.append(payload)):
    client = overlay.OverlayClient()
    client.send_message("wfmt_route_x", "route", "#fff", 0, 0, ttl=60)
    client.send_message("wfmt_exo_status_x", "bio", "#fff", 0, 0, ttl=60)
    sent.clear()
    check("ON" in window._exploration_button.cget("text"), "the exploration button starts ON")
    window._toggle("exploration")
    pump()
    check([p["id"] for p in sent] == ["wfmt_route_x"], "hiding exploration clears only its cards (sent %s)" % [p["id"] for p in sent])
    check("OFF" in window._exploration_button.cget("text") and "ON" in window._exobiology_button.cget("text"), "the buttons show each group's state")
    window._toggle("exobiology")
    check(overlay.group_hidden("exobiology"), "exobiology is hidden")
    sent.clear()
    window._toggle("exploration")
    window._toggle("exobiology")
    check({p["id"] for p in sent} == {"wfmt_route_x", "wfmt_exo_status_x"}, "showing both puts the cards back")
    check(not overlay.group_hidden("exploration") and not overlay.group_hidden("exobiology"), "both groups are shown again")

# --- a refresh with nothing new changes nothing, and close ---------------------------------------------------------------------------
before = all_text(window._tabs._tabs[WIN.TAB_OVERVIEW][2])
window.refresh()
check(all_text(window._tabs._tabs[WIN.TAB_OVERVIEW][2]) == before, "an unchanged refresh leaves the overview as it was")
window.close()
pump()
check(not WIN.is_open(), "the window closed")
check("wfmt_explore_dashboard_geometry" in saved, "the window remembered its size")

if problems:
    print("PROBLEMS:")
    for problem in problems:
        print(" -", problem)
    sys.exit(1)
print("EXPLORE DASHBOARD OK")
