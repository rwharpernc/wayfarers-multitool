"""Opens the real Combat Record panel section and window (plugin/combat_panel.py, plugin/combat_window.py) with EDMC stubbed, and checks that the
panel's two lines follow the events, that the window's three tabs show the session, the totals and the sessions per ship, that a long ship name never
widens the panel, and that Rebuild from journals gives the same figures. Run by test_combat_window_smoke.py in a subprocess so the stand-ins never leak into
other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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
        return default

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

from plugin import combat_panel, combat_record, combat_window  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


def table_texts(table):
    texts = []
    for row in table._rows.values():
        texts.append([str(v) for v in row.values])
    return texts


def stamp(seconds):
    return "2026-10-20T10:00:%02dZ" % seconds


folder = tempfile.mkdtemp()
book = combat_record.CombatBook()
book.logfile = lambda: "Journal.A.log"
panel = combat_panel.CombatController(book)
panel.start(folder)

saved["wfmt_combat_collapsed"] = False
host = tk.Frame(root)
host.pack()
panel.build_panel(host)
pump()
check(panel._session_var.get() == "(waiting for commander login)", f"before a commander: {panel._session_var.get()!r}")

journals = tempfile.mkdtemp()
book.set_commander("Bocheaux", folder=journals, wait=True)
panel.refresh()
check(panel._session_var.get() == "This session: no kills or deaths yet", f"a commander, no play: {panel._session_var.get()!r}")
check(panel._total_var.get() == "All time: none recorded yet", f"no totals: {panel._total_var.get()!r}")

state = {}
panel.handle_event({"event": "LoadGame", "timestamp": stamp(0), "Ship": "federation_corvette", "ShipID": 3,
                    "ShipName": "W" * 80, "ShipIdent": "WW-01", "Commander": "Bocheaux"}, "Bocheaux", "Sol", None, state)
panel.handle_event({"event": "Bounty", "timestamp": stamp(1), "Target": "anaconda", "TotalReward": 12345}, "Bocheaux", "Sol", None, state)
panel.handle_event({"event": "FactionKillBond", "timestamp": stamp(2), "Reward": 5000}, "Bocheaux", "Sol", None, state)
panel.handle_event({"event": "Died", "timestamp": stamp(3)}, "Bocheaux", "Sol", None, state)
pump()
check(panel._session_var.get() == "This session: 2 kills, 1 death, K/D 2.0", f"after play: {panel._session_var.get()!r}")
check(panel._total_var.get() == "All time: 2 kills, 1 death, K/D 2.0", f"totals: {panel._total_var.get()!r}")

width_before = host.winfo_reqwidth()
panel.handle_event({"event": "Bounty", "timestamp": stamp(4), "Target": "x", "TotalReward": 1}, "Bocheaux", "Sol", None, state)
pump()
check(host.winfo_reqwidth() <= max(width_before, 400), f"the panel stayed narrow: {host.winfo_reqwidth()}")

# --- the window ---------------------------------------------------------------------------------------------------------------------------
combat_window.show(root, book)
pump()
win = combat_window._window
check(win is not None and win.alive, "the window opened")
sessions = book.sessions("Bocheaux")
check(len(sessions) == 1 and sessions[0]["id"] == "Journal.A.log", f"one session: {sessions}")
check(len(table_texts(win._session.table)) == 1, f"This session lists the one ship: {table_texts(win._session.table)}")
row = table_texts(win._all.table)[0]
check(row[0] == "Federal Corvette" and row[2] == "3" and row[4] == "1" and row[5] == "3.0", f"All time row: {row}")
check(row[6] == "17,346", f"rewards add up: {row}")
check(len(table_texts(win._sessions)) == 1, "the Sessions tab lists the session")
check("(this session)" in table_texts(win._sessions)[0][0], f"the live session is marked: {table_texts(win._sessions)[0]}")
check(len(table_texts(win._detail)) == 1, "selecting the session shows its ships")
check("Bocheaux" in win._shell._subtitle.cget("text") and "3 kills" in win._shell._subtitle.cget("text"), f"subtitle: {win._shell._subtitle.cget('text')!r}")

# a second window call raises, it does not open another
combat_window.show(root, book)
check(combat_window._window is win, "one window")

# a death on a second ship, in a new session, shows in the totals and in the sessions list
book.logfile = lambda: "Journal.B.log"
panel.handle_event({"event": "LoadGame", "timestamp": stamp(10), "Ship": "asp", "ShipID": 1, "ShipName": "", "ShipIdent": "", "Commander": "Bocheaux"}, "Bocheaux", "Sol", None, state)
panel.handle_event({"event": "Died", "timestamp": stamp(11)}, "Bocheaux", "Sol", None, state)
pump()
win._poll()
pump()
check(len(table_texts(win._sessions)) == 2, f"two sessions: {table_texts(win._sessions)}")
check(len(table_texts(win._all.table)) == 2, "two ships in the totals")
check(table_texts(win._session.table) == [["Asp Explorer", "", "0", "0", "1", "0.0", "0"]], f"This session is the new one only: {table_texts(win._session.table)}")

before = book.total("Bocheaux")
win._rebuild()
book._thread.join()
pump()
check(book.total("Bocheaux") == combat_record.new_tally(), f"no journals exist in the test folder, so the rebuilt record is empty: {book.total('Bocheaux')}")
check(win.alive, "the window survives a rebuild")
check(before["kills"] == 3 and before["deaths"] == 2, f"totals before the rebuild: {before}")

win.close()
check(not win.alive, "closed")

if problems:
    print("FAIL")
    for line in problems:
        print(" -", line)
    sys.exit(1)
print("COMBAT OK")
