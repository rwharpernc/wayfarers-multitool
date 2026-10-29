"""Opens the real Expedition section (plugin/expedition_panel.py) with the Expedition Log's figures in it (and no START, PAUSE or STOP), and EDMC stubbed: one section where there were two, the
planned expedition's lines with the Log's extra figures under them, a Log run with no plan behind it worded as the Log words it, a run started, paused and stopped from the window showing in it, and the section
not widening the panel. Run by test_expedition_row_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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

from plugin import expedition_log_panel as LOGP, expedition_panel as PLAN  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(times=4):
    for _ in range(times):
        root.update()


def texts(widget):
    found = []
    if isinstance(widget, (tk.Label, tk.Button, tk.Checkbutton)):
        found.append(str(widget.cget("text")))
    for child in widget.winfo_children():
        found.extend(texts(child))
    return found


PLAN.book.load(tempfile.mkdtemp())
LOGP.start(tempfile.mkdtemp())
saved["wfmt_expedition_collapsed"] = False                 # open, so its widgets count towards the panel's width
host = tk.Frame(root)
host.pack()
PLAN.controller.build_panel(host)
pump()

# --- one section, which shows what is running and has no START, PAUSE or STOP (those are in the Expedition window) ------------------------------------------------
shown = texts(host)
check(any("Expedition" in t and t != "Expedition" for t in shown), f"there is an Expedition section: {shown}")
check(not any("Expedition Log" in t for t in shown), f"there is no section of its own for the Log: {shown}")
for word in ("Copy Next", "Expedition"):
    check(word in shown, f"the section has {word}")
for word in ("Start", "Pause", "Stop", "Resume", "Log"):
    check(word not in shown, f"the section has no {word} button: expeditions are managed in the Expedition window")
check(not LOGP.controller._buttons, f"no Log buttons are built into the section: {sorted(LOGP.controller._buttons)}")
check(LOGP.PANEL_PLACEMENT is None, "the Log module asks for no section of its own")

# --- before a commander, and with one -------------------------------------------------------------------------------------------------------------
check(PLAN.controller.summary()[0] == "Log in to use expeditions.", f"before a commander: {PLAN.controller.summary()}")
PLAN.controller.handle_event({"event": "LoadGame"}, "CMDR A", "Sol", None, {})
LOGP.controller.handle_event({"event": "LoadGame", "Commander": "CMDR A"}, "CMDR A", "Sol", None, {})
check(PLAN.controller.summary()[0] == "No expedition yet.", f"with a commander and nothing: {PLAN.controller.summary()}")

# --- a Log run started from the Expedition window has no plan behind it: the Log's own words ------------------------------------------------------------------
LOGP.controller.start_expedition()
pump()
check(LOGP.book.active() is not None, "starting from the window starts a Log run")
text, suffix = PLAN.controller.summary()
check("systems" in text and "Earned" in text and " jumps" in text, f"a Log run alone is worded as the Log words it: {text!r}")
check(suffix == " - running", f"and the folded title says what is running: {suffix!r}")
LOGP.controller.toggle_pause()
pump()
check("(paused)" in PLAN.controller.summary()[0], f"pausing it shows in the section: {PLAN.controller.summary()[0]!r}")
LOGP.controller.toggle_pause()
pump()
check("(paused)" not in PLAN.controller.summary()[0], "resuming carries on")
LOGP.controller.stop_expedition()
pump()
check(LOGP.book.active() is None, "stopping ends it")
check(PLAN.controller.summary()[0] == "No expedition yet.", f"nothing is running again: {PLAN.controller.summary()}")

# --- a planned expedition: its lines, then the Log's extra figures ----------------------------------------------------------------------------------------
made = PLAN.book.create("Colonia run")
PLAN.book.add_stop(made.id, "Sol", xyz=(0.0, 0.0, 0.0))
PLAN.book.add_stop(made.id, "Colonia", xyz=(-9530.5, -910.28, 19808.1))
PLAN.link.start(made.id)
pump()
text, suffix = PLAN.controller.summary()
check(PLAN.book.active() is not None and LOGP.book.active() is not None, "starting the expedition starts its Log run")
check("of 2 stops" in text and "Next:" in text, f"the expedition's own lines come first: {text!r}")
check("systems" in text and "bodies" in text and "Earned" in text, f"then the Log's figures: {text!r}")
check(text.count("jumps") == 1, f"the jumps are said once, not twice: {text!r}")
check(suffix.startswith("- ") and "/2" in suffix, f"the folded title shows the stops: {suffix!r}")
check(host.winfo_reqwidth() <= 216, f"the section does not widen the panel: {host.winfo_reqwidth()} px")

if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("EXPEDITION ROW OK")
