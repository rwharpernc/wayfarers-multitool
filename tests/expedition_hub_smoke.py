"""Opens the real Expedition window (plugin/expedition_hub.py) with the three panels' windows built into its tabs and EDMC stubbed: one window for Plan, Route and Log, each tab
built when first shown, the panels opening their tab in the same window, a tab that is closed being built again, one saved geometry, and the book listeners being removed when the
window closes. Run by test_expedition_hub_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
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

from plugin import expedition_hub as HUB, expedition_log_panel as LOGP, expedition_panel as PLAN, expedition_window, route_planner_panel as ROUTE, route_planner_window  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(times=4):
    for _ in range(times):
        root.update()


def texts(widget):
    found = []
    if isinstance(widget, tk.Label):
        found.append(str(widget.cget("text")))
    for child in widget.winfo_children():
        found.extend(texts(child))
    return found


def toplevels(widget=None):
    """Every Toplevel under the root (the window is a child of the panel row it was opened from)."""
    found = []
    for child in (root if widget is None else widget).winfo_children():
        if isinstance(child, tk.Toplevel):
            found.append(child)
        found.extend(toplevels(child))
    return found


plan_folder, log_folder = tempfile.mkdtemp(), tempfile.mkdtemp()
PLAN.book.load(plan_folder)
LOGP.start(log_folder)
saved["wfmt_expedition_collapsed"] = False
frame = tk.Frame(root)
frame.pack()
for panel in (PLAN.controller, LOGP.controller, ROUTE.controller):
    holder = tk.Frame(frame)
    holder.pack()
    panel.build_panel(holder)
pump()
PLAN.controller.handle_event({"event": "LoadGame"}, "CMDR A", "Sol", None, {})
LOGP.controller.handle_event({"event": "LoadGame", "Commander": "CMDR A"}, "CMDR A", "Sol", None, {})
made = PLAN.book.create("Colonia run")
PLAN.book.add_stop(made.id, "Sol", xyz=(0.0, 0.0, 0.0))
PLAN.book.add_stop(made.id, "Colonia", xyz=(-9530.5, -910.28, 19808.1))
other = PLAN.book.create("Bubble loop")
PLAN.book.add_stop(other.id, "Sol", xyz=(0.0, 0.0, 0.0))

# --- opening from the Expedition panel builds the window on the Plan tab only -----------------------------------------------------------------
check(not HUB.is_open() and not toplevels(), "nothing is open at the start")
PLAN.controller._open_window(select=made.id)
pump()
check(HUB.is_open() and len(toplevels()) == 1, f"one window opened: {len(toplevels())}")
check(HUB.view(HUB.PLAN) is not None and HUB.view(HUB.PLAN)._picked == made.id, "the Plan tab shows the expedition asked for")
check(HUB.view(HUB.ROUTE) is None and HUB.view(HUB.LOG) is None, "the Route and Log tabs are not built until they are shown")
check(toplevels()[0].title() == "Expedition", f"the window is called Expedition: {toplevels()[0].title()!r}")
check(HUB._hub._tabs.selected == 0, "the Plan tab is the one shown")
shown = "\n".join(texts(HUB._hub.window))
check("Start" in shown and "Pause" in shown, "the Plan tab has its Start and Pause buttons")

# --- the other panels open their tabs in the same window ----------------------------------------------------------------------------------------
LOGP.controller._open_window()
pump()
check(len(toplevels()) == 1, f"the Log opened in the same window, not another: {len(toplevels())}")
check(HUB.view(HUB.LOG) is not None and HUB._hub._tabs.selected == 2, "the Log tab is built and shown")
ROUTE.controller.open()
pump()
check(len(toplevels()) == 1 and HUB.view(HUB.ROUTE) is not None and HUB._hub._tabs.selected == 1, "the Route tab is built and shown in the same window")
check(route_planner_window.is_open(), "the Route Planner module sees its window as open")
route_planner_window.announce("Reached Alpha: a test message")
pump()
check("a test message" in "\n".join(texts(HUB._hub.window)), "the planner's announcements reach the Route tab")

# --- going back to a tab and picking another expedition --------------------------------------------------------------------------------------------
PLAN.controller._open_window(select=other.id)
pump()
check(HUB._hub._tabs.selected == 0 and HUB.view(HUB.PLAN)._picked == other.id, "opening the Plan tab again switches to it and picks the expedition asked for")
check(len(toplevels()) == 1, "still one window")

# --- starting from the tab works, and the Log tab follows ---------------------------------------------------------------------------------------------
HUB.view(HUB.PLAN)._start()
pump()
check(PLAN.book.active() is not None and PLAN.book.active().id == other.id, "Start in the Plan tab starts the expedition")
check(LOGP.book.active() is not None, "and the linked Log run is running")

# --- a tab that is closed is built again when asked for --------------------------------------------------------------------------------------------
expedition_window.close()
pump()
check(HUB.is_open() and HUB.view(HUB.PLAN) is None, "closing the Plan window leaves the others in place")
check(HUB.view(HUB.ROUTE) is not None and HUB.view(HUB.LOG) is not None, "the Route and Log tabs are still there")
listeners = len(PLAN.book._listeners)
PLAN.controller._open_window(select=made.id)
pump()
check(HUB.view(HUB.PLAN) is not None and HUB.view(HUB.PLAN)._picked == made.id, "it is built again, on the expedition asked for")
check(len(PLAN.book._listeners) == listeners + 1, "with one listener on the book")

# --- closing the window closes every tab and removes what they listened to -----------------------------------------------------------------------
before_plan, before_log = len(PLAN.book._listeners), len(LOGP.book._listeners)
HUB.close()
pump()
check(not HUB.is_open() and not toplevels(), "closing the window leaves no window")
check(len(PLAN.book._listeners) == before_plan - 1, "the Plan tab stopped listening")
check(len(LOGP.book._listeners) == before_log - 1, "the Log tab stopped listening")
check(bool(saved.get(HUB.CONFIG_GEOMETRY)), "one geometry is saved for the whole window")
own = [key for key in saved if key.endswith("window_geometry") and key != HUB.CONFIG_GEOMETRY and saved.get(key)]
check(not own, f"the tabs saved no geometry of their own: {own}")

# --- and it opens again --------------------------------------------------------------------------------------------------------------------------------
LOGP.controller._open_window()
pump()
check(HUB.is_open() and HUB.view(HUB.LOG) is not None and HUB._hub._tabs.selected == 2, "the window opens again on the Log tab")
HUB.close()
pump()

if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("EXPEDITION HUB OK")
