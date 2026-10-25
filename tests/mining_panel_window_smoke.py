"""Opens the real Mining History window from the Mining panel's DASHBOARD button (plugin/mining_panel.py) and redraws the panel while it is open: the window must survive,
because the panel's redraw destroys every child of its content frame. Run by test_mining_panel_window_smoke in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is
unavailable."""
import json
import os
import shutil
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

journals = tempfile.mkdtemp()
state = tempfile.mkdtemp()
saved = {}


class Cfg:
    default_journal_dir = journals

    def get_str(self, key, default=""):
        return journals if key == "journaldir" else (saved.get(key, default) or "")

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


def line(**fields):
    return json.dumps(fields)


def trip(start, who="Smoke Cmdr"):
    stamp = lambda minute: f"2026-10-1{start}T12:{minute:02d}:00Z"
    return [line(timestamp=stamp(0), event="Commander", Name=who), line(timestamp=stamp(1), event="FSDJump", StarSystem="Smoke 1", SystemAddress=1),
            line(timestamp=stamp(2), event="Undocked"),
            line(timestamp=stamp(5), event="SupercruiseExit", StarSystem="Smoke 1", Body="Smoke 1 2 A Ring", BodyType="PlanetaryRing"),
            line(timestamp=stamp(6), event="LaunchDrone", Type="Prospector"),
            line(timestamp=stamp(7), event="ProspectedAsteroid", Content_Localised="Material Content: High"),
            line(timestamp=stamp(8), event="MiningRefined", Type_Localised="Platinum"), line(timestamp=stamp(9), event="MiningRefined", Type_Localised="Platinum"),
            line(timestamp=stamp(20), event="Docked"),
            line(timestamp=stamp(21), event="MarketSell", Type="platinum", Type_Localised="Platinum", Count=2, TotalSale=420000)]


def write(name, lines, newer=0):
    path = os.path.join(journals, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    os.utime(path, (time.time() + newer, time.time() + newer))


write("Journal.2026-10-16T100000.01.log", trip(6))

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


try:
    from plugin import mining_history, mining_history_window as WIN, mining_panel
    mining_history.history.start(state)
    mining_history.history.pause = 0
    mining_history.history.set_commander("Smoke Cmdr")
    parent = tk.Frame(root)
    parent.pack()
    root.deiconify()
    controller = mining_panel.MiningPanelController()
    controller.build_panel(parent)
    root.update()
    controller._buttons.history.invoke()
    for _ in range(10):
        root.update()
    window = WIN._windows.get(WIN.D.SPACE)            # the panel opens on the Space page
    check(window is not None and window.alive, "DASHBOARD opens the Mining History window")
    check(window.alive and window._shell.window.master is root, "the window hangs from the main window, not from the panel's content frame")
    for _ in range(3):
        controller._redraw()
        root.update()
    check(window.alive, "the window survives the panel redrawing")
    if window.alive:
        window.close()

    def lines():
        return [w for w in controller._content.winfo_children() if isinstance(w, tk.Label)]

    controller._redraw()
    before = lines()
    check(before, "the panel shows at least one text line")
    controller._redraw()
    after = lines()
    check(len(before) == len(after) and all(a is b for a, b in zip(before, after)), "a redraw with nothing changed keeps the same text lines, so they do not flicker")
    first = before[0]
    widened = controller._wrap + 40                # the width changed: the same line is updated in place
    controller._wrap = widened
    controller._redraw()
    # Compare with the width that was set, not controller._wrap: on Windows the
    # redraw lets a canvas <Configure> event run, which resets _wrap to the real
    # canvas width before this line is checked.
    check(lines()[0] is first and int(first.cget("wraplength")) == widened, "a changed width updates the line in place")
except Exception as exc:  # noqa: BLE001
    import traceback
    problems.append("raised: " + "".join(traceback.format_exception(exc)))
finally:
    shutil.rmtree(journals, ignore_errors=True)
    shutil.rmtree(state, ignore_errors=True)

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("MINING PANEL WINDOW OK")
