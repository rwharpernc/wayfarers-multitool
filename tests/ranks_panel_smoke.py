"""Opens the real Ranks section of Operations (plugin/ranks_panel.py) with EDMC stubbed, and checks that the table follows the Rank, Progress and Promotion
events, that a different commander starts empty, that EDMC's own state fills the table when EDMC started after the login, and that the longest rank names
do not widen the panel. Run by test_ranks_panel_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not,
77 if Tk is unavailable."""
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

from plugin import ranks_panel  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


def grid_rows(frame):
    """The text of a StatRows frame as the user reads it: one list per row, left to right."""
    rows = {}
    for child in frame.winfo_children():
        info = child.grid_info()
        rows.setdefault(int(info["row"]), {})[int(info["column"])] = child.cget("text")
    return [[cells[column] for column in sorted(cells)] for _row, cells in sorted(rows.items())]


RANK = {"event": "Rank", "Combat": 4, "Trade": 13, "Explore": 8, "Soldier": 2, "Exobiologist": 7, "Empire": 12, "Federation": 11, "CQC": 0}
PROGRESS = {"event": "Progress", "Combat": 99, "Trade": 100, "Explore": 98, "Soldier": 94, "Exobiologist": 98, "Empire": 100, "Federation": 100, "CQC": 0}

saved["wfmt_ranks_collapsed"] = False
panel = ranks_panel.RanksController()
root.geometry("480x500")
root.deiconify()
host = tk.Frame(root)
host.columnconfigure(1, weight=1)          # as ui.py builds each feature's frame
host.pack(fill="x")
panel.build_panel(host)
pump()
check(panel._note_var.get() == "(waiting for commander login)" and panel._note.winfo_manager() == "grid", f"before a commander: {panel._note_var.get()!r}")
check(grid_rows(panel._rows) == [], "no rows before a commander")

panel.handle_event({"event": "LoadGame"}, "Bocheaux", "Sol", None, {})
pump()
check("waiting for the game's rank report" in panel._note_var.get(), f"a commander with no rank report yet: {panel._note_var.get()!r}")

panel.handle_event(RANK, "Bocheaux", "Sol", None, {})
panel.handle_event(PROGRESS, "Bocheaux", "Sol", None, {})
pump()
rows = grid_rows(panel._rows)
check(rows[0] == ["Rank", "To next"], f"the heading: {rows[:1]}")
check(rows[1:] == [["Combat", "Expert", "99%"], ["Trade", "Elite V", "max"], ["Exploration", "Elite", "98%"], ["CQC", "Helpless", "0%"],
                   ["Mercenary", "Rookie", "94%"], ["Exobiologist", "Geneticist", "98%"], ["Federation", "Post Captain", "100%"], ["Empire", "Duke", "100%"]],
      f"every ladder, by the game's names: {rows[1:]}")
check(panel._note.winfo_manager() == "", "the waiting note is gone once there are ranks")
pump()
labels = [c for c in panel._rows.winfo_children() if isinstance(c, tk.Label)]
check(all(int(str(c.cget("wraplength"))) == 0 for c in labels), "no rank name is set to wrap")
check(panel._rows.winfo_width() >= host.winfo_width() - 4, f"the table fills the panel: {panel._rows.winfo_width()} px of {host.winfo_width()}")
width = panel._rows.winfo_width()

panel.handle_event({"event": "Rank", "Federation": 9, "Exobiologist": 4, "Soldier": 3, "Empire": 6}, "Bocheaux", "Sol", None, {})
panel.handle_event({"event": "Progress", "Federation": 100}, "Bocheaux", "Sol", None, {})
pump()
pump()
long_names = [c for c in panel._rows.winfo_children() if isinstance(c, tk.Label) and c.cget("text") in ("Lieutenant Commander", "Semi Professional")]
check(len(long_names) == 1 and int(str(long_names[0].cget("wraplength"))) == 0, f"Lieutenant Commander is shown unwrapped: {len(long_names)} found")
panel.handle_event({"event": "Promotion", "Combat": 5}, "Bocheaux", "Sol", None, {})
pump()
check(["Combat", "Master", "0%"] in grid_rows(panel._rows), "a promotion shows at once, at 0%")

panel.handle_event({"event": "LoadGame"}, "Someone Else", "Sol", None, {})
pump()
check(grid_rows(panel._rows) == [] and panel._note.winfo_manager() == "grid", f"another commander starts empty: {grid_rows(panel._rows)}")

late = ranks_panel.RanksController()
late_host = tk.Frame(root)
late_host.pack()
late.build_panel(late_host)
late.handle_event({"event": "FSDJump"}, "Bocheaux", "Sol", None, {"Rank": {"Trade": (5, 40), "Federation": (9, 61)}})
pump()
check(grid_rows(late._rows)[1:] == [["Trade", "Broker", "40%"], ["Federation", "Lieutenant Commander", "61%"]], f"from EDMC's state: {grid_rows(late._rows)}")

root.destroy()
if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"RANKS PANEL OK (table {width} px wide)")
