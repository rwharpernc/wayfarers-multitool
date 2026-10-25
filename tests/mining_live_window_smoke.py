"""Opens the real Mining live windows (plugin/mining_live_window.py) with EDMC stubbed and a Rhino position faked: the Surface window draws a radar, shows the panel's lines, marks a mining location
from its CTR and BRD buttons, moves the radar's reach with the zoom buttons and remembers it, and survives the panel's content frame being destroyed; the Space window shows its lines and only the
lookups switched on in Settings. Run by test_mining_live_window_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
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

from plugin import mining_coverage as coverage, mining_hotspots as hotspots, mining_live_position as LP, mining_live_window as LW  # noqa: E402
from plugin import mining_pages, mining_render as render, mining_surface as surface_mining  # noqa: E402

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


def texts(widget):
    found = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Label):
            found.append(str(child.cget("text")))
        found.extend(texts(child))
    return found


RADIUS = 400_000.0
M_PER_DEG = 3.141592653589793 * RADIUS / 180.0
settings_now = {"hotspots": False, "price": True, "reserve": False}


def settings():
    return render.PanelSettings(True, True, True, settings_now["hotspots"], settings_now["price"], settings_now["reserve"], True)


# a Rhino on a body, on the ground
surface_mining.surface_mining_repository.set_current_cmdr("Smoke Cmdr")
surface_mining.surface_mining_repository.set_current_location("Smoke", "Smoke 1")
surface_mining.surface_mining_repository.record_body_radius("Smoke 1", RADIUS)
coverage.coverage_repository.set_commander("Smoke Cmdr")
LP.set_status({"Flags": LP.FLAGS_HAS_LAT_LONG, "Latitude": 10.0, "Longitude": 20.0, "Heading": 90, "PlanetRadius": RADIUS, "Altitude": 0})
hotspots.hotspot_repository.add_or_merge(hotspots.Hotspot(system="Smoke", body="Smoke 1", material="Painite", rigs=4, latitude=10.0 + 800 / M_PER_DEG, longitude=20.0), RADIUS)

panel_content = tk.Frame(root)
LW.show(panel_content, mining_pages.SURFACE_MINING, settings)
win = LW._windows.get(mining_pages.SURFACE_MINING)
check(win is not None and win.alive, "the surface live window did not open")
for child in panel_content.winfo_children():
    child.destroy()
panel_content.destroy()
pump(0.3)
check(win.alive, "the surface live window was destroyed with the panel's content frame")
check(win._photo is not None, "the radar did not draw with a position")
check(win._radar_label.cget("image"), "the radar picture is not shown")
everything = "\n".join(texts(win._info.body))
check("Nearest saved deposit: Painite" in everything, f"the panel's lines are missing: {everything!r}")
check("Smoke 1" in win._shell._subtitle.cget("text"), f"the subtitle: {win._shell._subtitle.cget('text')!r}")

# the controls
win._mark(False)
body = coverage.coverage_repository.for_body("Smoke", "Smoke 1")
check(body is not None and len(body.sites) == 1, "CTR did not mark a center")
check("Center marked" in win._shell._status.cget("text"), f"CTR said: {win._shell._status.cget('text')!r}")
LP.set_status({"Flags": LP.FLAGS_HAS_LAT_LONG, "Latitude": 10.0 + 1500 / M_PER_DEG, "Longitude": 20.0, "Heading": 0, "PlanetRadius": RADIUS, "Altitude": 0})
win._mark(True)
check(body.sites[0].border is not None and "1.50 km" in win._shell._status.cget("text"), f"BRD said: {win._shell._status.cget('text')!r}")
marked = "\n".join(texts(win._info.body))
check("Nearest marked location: 1.50 km radius, you are" in marked, f"the marked location line is missing: {marked!r}")

# the radar's reach
win._set_range(500.0)
check(saved.get(LW.CONFIG_RANGE) == 500 and win._range_m == 500.0, "the radar range was not set and kept")
check(LW.saved_range() == 500.0, "the kept range is not read back")
saved[LW.CONFIG_RANGE] = 12345
check(LW.saved_range() == 2000.0, "an unknown kept range should fall back to the default")

# no position: the radar says why instead of drawing
LP.set_status({"Flags": 0})
win.refresh()
check(win._photo is None and "Land" in str(win._radar_label.cget("text")), "with no position the radar should explain itself")

# the Space window
LW.show(tk.Frame(root), mining_pages.SPACE_MINING, settings)
space = LW._windows.get(mining_pages.SPACE_MINING)
check(space is not None and space.alive, "the space live window did not open")
pump(0.2)
check(space._radar_label is None, "the space window has no radar")
check(space._lookups_shown == {"hotspot_finder": False, "price_finder": True, "reserve_lookup": False}, f"only the lookups switched on should show: {space._lookups_shown}")
settings_now["reserve"] = True
space.refresh()
check(space._lookups_shown["reserve_lookup"] is True, "a lookup switched on in Settings should appear")
LW.show(tk.Frame(root), mining_pages.SPACE_MINING, settings)         # a second press raises the same window
check(LW._windows[mining_pages.SPACE_MINING] is space, "a second press should raise the open window, not open another")
LW.close()
check(not win.alive and not space.alive, "close() should close both windows")

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("LIVE WINDOW OK")
