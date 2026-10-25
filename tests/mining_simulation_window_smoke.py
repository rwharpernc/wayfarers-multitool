"""Opens the Surface Live window on the Mining simulation (Settings -> Mining -> Simulation, plugin/mining_simulation.py): the radar must draw, CTR must mark on the pretend ground,
the window must keep running, and WFMT's own repositories must not change. Run by test_mining_simulation_window_smoke in a subprocess. Exits 0 if everything holds, 1 if not, 77 if
Tk is unavailable."""
import os
import sys
import tempfile
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
root.geometry("400x300")
root.update()

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


try:
    from plugin import mining_coverage as coverage, mining_hotspots as hotspots, mining_live_window as live, mining_panel, mining_simulation as simulation, mining_surface as surface

    real_hotspots = list(hotspots.hotspot_repository._hotspots)
    real_coverage = dict(coverage.coverage_repository._by_body)
    real_body = surface.surface_mining_repository.current_body

    modal = tk.Toplevel(root)             # EDMC's Settings window: modal, so nothing else gets clicks while it holds the grab
    modal.geometry("200x100")
    modal.update()
    modal.grab_set()
    check(root.grab_current() is modal, "the pretend Settings window holds the grab")
    simulation.open_surface_live(modal, mining_panel._settings)
    for _ in range(10):
        root.update()
    window = live._windows.get(live.mining_pages.SURFACE_MINING + live.SIMULATION_SUFFIX)
    check(window is not None and window.alive, "the simulation opens a Surface Live window")
    if window is not None and window.alive:
        check(root.grab_current() is None, "the simulation window can be clicked while Settings is open: Settings lets go of the grab")
        check("(simulation)" in window._shell.window.title(), "the window title says it is a simulation")
        check(window._photo is not None, "the radar draws a picture on the pretend ground")
        check(live._windows.get(live.mining_pages.SURFACE_MINING) is None, "the simulation does not take the place of the real Live window")
        rigs = lambda: len(window._src.rigs.rigs_for(simulation.SYSTEM, simulation.BODY))
        before_rigs = rigs()
        window._place_rig()
        root.update()
        check(rigs() == before_rigs + 1, "Rig placed notes a rig on the pretend ground")
        window._clear_rigs()
        root.update()
        check(rigs() == 0, "Clear rigs forgets them")
        sites = len(window._src.coverage.for_body(simulation.SYSTEM, simulation.BODY).sites)
        window._mark(False)
        root.update()
        check(len(window._src.coverage.for_body(simulation.SYSTEM, simulation.BODY).sites) == sites + 1, "CTR marks a site on the pretend ground")
        for meters in live.radar.RADAR_RANGES_M:
            window._set_range(meters)
            root.update()
            check(window._photo is not None, f"the radar still draws at {meters:.0f} m")
        saved_path = os.path.join(tempfile.mkdtemp(), "sim map.png")
        window._choose_path = lambda default_name: saved_path
        window._save_map()
        root.update()
        check(os.path.isfile(saved_path) and os.path.getsize(saved_path) > 5000, "Save map writes a PNG")
        try:
            from PIL import Image
            with Image.open(saved_path) as picture:
                check(picture.format == "PNG" and picture.size[0] == 900, "the saved map is a 900 px wide PNG")
        except Exception as exc:  # noqa: BLE001
            check(False, f"the saved map could not be read back: {exc}")
        window._choose_path = lambda default_name: ""
        window._save_map()                                  # cancelling the dialog does nothing and does not raise
        check(window.alive, "cancelling Save map leaves the window running")

        def lines():
            return [w for w in window._info.body.winfo_children() if isinstance(w, tk.Label)]

        window.refresh()
        before = lines()
        window.refresh()
        after = lines()
        check(before and len(before) == len(after) and all(a is b for a, b in zip(before, after)), "a redraw keeps the same text lines, so the text does not flash")
        for _ in range(3):
            window.refresh()
            root.update()
        check(window.alive, "the window keeps running through redraws")
        handler = window._shell.window.protocol("WM_DELETE_WINDOW")      # what the title bar's close button runs
        window._shell.window.tk.call(handler)
        root.update()
        check(not window.alive, "the title bar's close button closes the window")
        check(root.grab_current() is modal, "the Settings window gets its grab back when the simulation closes")
    check(real_hotspots == hotspots.hotspot_repository._hotspots, "WFMT's own saved deposits did not change")
    check(real_coverage == coverage.coverage_repository._by_body, "WFMT's own marks did not change")
    check(real_body == surface.surface_mining_repository.current_body, "WFMT's own Rhino state did not change")
    from plugin import mining_rigs
    check(mining_rigs.rig_book.rigs_for(simulation.SYSTEM, simulation.BODY) == [], "WFMT's own rigs did not change")
except Exception as exc:  # noqa: BLE001
    import traceback
    problems.append("raised: " + "".join(traceback.format_exception(exc)))

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("MINING SIMULATION WINDOW OK")
