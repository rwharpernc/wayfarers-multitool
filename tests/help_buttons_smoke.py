"""Opens windows that explain themselves behind a Help button (the shell's `add_help`) with EDMC stubbed, and checks that Help opens, is raised rather than duplicated on a
second press, and that each window's Help entries are plain lines or (name, text) pairs. Run by test_help_buttons_smoke in a subprocess so the stand-ins never leak into other
tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "ttkHyperlinkLabel", "theme", "myNotebook"):
    sys.modules[n] = Any(n)
saved = {}


class Cfg:
    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def set(self, key, value):
        saved[key] = value


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import bgs_window, colonization_history_window, ledger_window  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def well_formed(items):
    return bool(items) and all(isinstance(i, str) or (isinstance(i, tuple) and len(i) == 2 and all(isinstance(s, str) for s in i)) for i in items)


def exercise(name, shell, items):
    check(well_formed(items), f"{name}: Help entries are lines or (name, text) pairs")
    shell._show_help()
    first = shell._help_window
    check(first is not None and first.winfo_exists(), f"{name}: Help opens a window")
    shell._show_help()
    check(shell._help_window is first, f"{name}: a second Help press reuses the window")
    first.destroy()


bgs_window.show(root, [], None, [], [], bgs_window.TabActions(toggle_pin=lambda s: None, close=lambda s: None, add=lambda s: None))
exercise("BGS Report", bgs_window._window._shell, bgs_window.HELP)
bgs_window._window.close()

colonization_history_window.show(root, lambda: ("CMDR TEST", [], {}))
exercise("Colonization History", colonization_history_window._window._shell, colonization_history_window.HELP)
colonization_history_window.close()

controller = mock.MagicMock()
controller.record.return_value = {}
controller.cmdr = "CMDR TEST"
controller.status = ""
controller.rebuilding.return_value = False
ledger_window.show(root, controller)
exercise("Credits Ledger", ledger_window._window._shell, ledger_window.HELP)
ledger_window._window._shell.close()

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("HELP BUTTONS OK")
