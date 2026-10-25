"""Builds the Mining panel on the Surface page with the simulation's pretend Rhino (a full set of lines and the button bar) and checks that the button bar is inside the panel's height
cap, so the buttons show without scrolling. Run by test_mining_panel_height_smoke in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ".")
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
nb = Any("myNotebook")
nb.Frame, nb.Label, nb.Button, nb.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nb
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
saved = {}


class Cfg:
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
cfgmod.user_agent = "t"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.geometry("420x700")
from plugin import mining_coverage, mining_hotspots, mining_live_position, mining_pages, mining_panel, mining_simulation, mining_surface

simulation = mining_simulation.SurfaceSimulation(clock=lambda: 1000.0)
# let the panel read the simulation's pretend world, with the Rhino deployed and some ore refined
for repo_module, name, value in ((mining_surface, "surface_mining_repository", simulation.surface), (mining_coverage, "coverage_repository", simulation.coverage),
                                 (mining_hotspots, "hotspot_repository", simulation.hotspots)):
    setattr(repo_module, name, value)
mining_live_position.current_position = simulation.position
for _ in range(60):
    simulation._last_refine = 0
    simulation._clock = lambda t=[1000.0]: t.__setitem__(0, t[0] + 5.0) or t[0]
    simulation.tick()

frame = tk.Frame(root)
frame.pack(fill="x")
controller = mining_panel.MiningPanelController()
controller.build_panel(frame)
problems = []
for page in (mining_pages.SURFACE_MINING, mining_pages.SPACE_MINING):
    controller._current_page = page
    controller._redraw()
    root.update()
    controller._content.update_idletasks()
    bbox = controller._canvas.bbox("all")
    bar = controller._buttons.bar
    bar_bottom = bar.winfo_y() + bar.winfo_height()
    if bar_bottom > mining_panel._MAX_PANEL_HEIGHT:
        problems.append(f"{page}: the button bar ends at {bar_bottom} px, below the {mining_panel._MAX_PANEL_HEIGHT} px cap, so the buttons need scrolling")
    if int(controller._canvas.cget("height")) != min(bbox[3] - bbox[1], mining_panel._MAX_PANEL_HEIGHT):
        problems.append(f"{page}: the panel is not as tall as its content or the cap")
root.destroy()
if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("MINING PANEL HEIGHT OK")
