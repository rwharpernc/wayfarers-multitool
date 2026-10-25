"""Opens the real Mining History window (plugin/mining_history_window.py) with EDMC stubbed, over a temporary journal folder, and checks that it reads the journals in the
background, fills the tiles and the four tabs, sorts, refreshes without changing anything and rebuilds. Run by test_mining_history_smoke in a subprocess so the stand-ins never
leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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
write("Journal.2026-10-17T100000.01.log", trip(7))
write("Journal.2026-10-18T100000.01.log", trip(8), newer=10)

from plugin import mining_history, mining_history_window as WIN  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(times=6):
    for _ in range(times):
        root.update()


def texts(widget):
    found = []
    if isinstance(widget, tk.Label):
        found.append(str(widget.cget("text")))
    for child in widget.winfo_children():
        found.extend(texts(child))
    return found


def wait_for(predicate, seconds=10.0):
    end = time.time() + seconds
    while time.time() < end:
        pump(2)
        if predicate():
            return True
        time.sleep(0.05)
    return False


try:
    mining_history.history.start(state)
    mining_history.history.pause = 0
    mining_history.history.set_commander("Smoke Cmdr")
    panel_content = tk.Frame(root)               # the Mining panel's content frame, which it empties and rebuilds every second
    WIN.show(panel_content)
    window = WIN._windows.get(WIN.D.SPACE)
    check(window is not None and window.alive, "the window did not open")
    for child in panel_content.winfo_children():
        child.destroy()
    panel_content.destroy()
    pump()
    check(window.alive, "the window was destroyed with the panel's content frame")
    check(wait_for(lambda: mining_history.history.ready and len(mining_history.history.runs()) == 3), f"the journals were not read: {len(mining_history.history.runs())} runs")
    wait_for(lambda: len(window._runs.table) == 3)       # the window redraws on its own poll, which a fast read can beat
    pump()
    everything = "\n".join(texts(window._shell.window))
    check("3 ring mining runs since" in everything, "the subtitle does not count the runs")
    check("tons refined" in everything and "hours mining" in everything, "the overview tiles are missing")
    check(len(window._commodities.table) == 1, "the commodities table did not fill (one commodity, Platinum)")
    check(len(window._runs.table) == 3, f"the runs table has {len(window._runs.table)} rows")
    check(len(window._places.table) == 1, "the rings table did not group the three runs into one ring")
    # a refresh with nothing changed leaves everything as it is
    signature = window._signature
    window.refresh_now()
    wait_for(lambda: mining_history.history.ready)
    pump()
    check(window._signature == signature, "a refresh with nothing new changed the window")
    # the newest journal grows while the window is open: the live run is picked up
    write("Journal.2026-10-18T100000.01.log", trip(8) + trip(9)[2:], newer=20)
    window.refresh_now()
    check(wait_for(lambda: len(mining_history.history.runs()) == 4), "a run added to the newest journal was not picked up")
    window._draw()
    check(len(window._runs.table) == 4, "the runs table did not grow with the new run")
    # rebuilding reads everything again and ends with the same runs
    window._rebuild()
    check(wait_for(lambda: mining_history.history.ready and len(mining_history.history.runs()) == 4), "the rebuild did not read the journals again")
    window.close()
    check(not window.alive, "the window did not close")
    print("MINING HISTORY", "OK" if not problems else "; ".join(problems))
    code = 0 if not problems else 1
except Exception as exc:  # noqa: BLE001
    import traceback
    tb = traceback.extract_tb(exc.__traceback__)[-1]
    print("MINING HISTORY FAILED:", type(exc).__name__, str(exc)[:200], f"(at {tb.filename.split('plugin')[-1]}:{tb.lineno})")
    code = 1
finally:
    for folder in (journals, state):
        shutil.rmtree(folder, ignore_errors=True)
root.destroy()
sys.exit(code)
