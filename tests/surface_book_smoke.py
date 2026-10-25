"""Opens the real Surface Mining Book (plugin/mining_ledger.py) with EDMC stubbed and the journal history faked: the "From your journals" group, the notice while the journals are read, and the
This system button (go to a body you worked in the system you are in, or say you have not worked it). Run by test_surface_book_smoke in a subprocess so the stand-ins never leak into other tests.
Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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

from plugin import mining_history, mining_hotspots, mining_ledger as L, mining_location  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


JOURNAL = {"sys a 3 a": {"body": "Sys A 3 a", "system": "Sys A", "locations": 4, "class": "Rocky body", "tons": 12, "last": ""},
           "sys b 1": {"body": "Sys B 1", "system": "Sys B", "locations": 2, "class": "", "tons": 0, "last": ""}}
history = mining_history.history
history.bodies = lambda: JOURNAL
history.ready = False
history.reading = "Reading your journals for the mining history (30%)"

repo_ = mining_hotspots.hotspot_repository
repo_.load(tempfile.mkdtemp())
repo_.set_commander("Bocheaux")
repo_.add(mining_hotspots.Hotspot("Sys C", "Sys C 2 c", "Painite"))

L.show(root)
book = L._window
root.update()
status = lambda: book._shell._status.cget("text")


def groups():
    return {key: heading for key, (_h, _c, heading) in book._bodies._groups.items()}


check("From your journals" in " ".join(groups().values()), f"the journals' bodies have a group: {groups()}")
check("Reading your journals" in status(), f"the notice says the journals are being read: {status()!r}")
check("30%" in book._shell._subtitle.cget("text") if hasattr(book._shell, "_subtitle") else True, "the subtitle says how far")

mining_location.set_current_system("Sys A")
book._find_here()
root.update()
check(book._body_entry is not None and book._body_entry.body == "Sys A 3 a", f"This system goes to the body worked in the system you are in: {book._body_entry}")
check("Sys A" in status() and "1 body" in status(), f"and says so: {status()!r}")

mining_location.set_current_system("Sys C")
book._find_here()
check(book._body_entry is not None and book._body_entry.body == "Sys C 2 c", "a body with saved hotspots counts as worked")

mining_location.set_current_system("Nowhere")
book._find_here()
check(status() == "You have not worked this system yet.", f"a system with nothing says so: {status()!r}")

history.reading = ""
history.ready = True
book._journal_tick()
check("Finished reading" in status() or "Reading" not in status(), f"the notice is replaced when the read ends: {status()!r}")

book.close()
root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("SURFACE BOOK OK")
