"""Opens the Engineers tab of the real Blueprints window with EDMC stubbed and checks that the mouse wheel scrolls the page when the pointer is over the
details of an engineer (a long guide makes the page taller than the window). Run by test_engineer_scroll_smoke.py in a subprocess. Exits 0 if everything
holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
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

from plugin import blueprints, blueprints_window, material_trader_window, material_traders, materials, materials_panel, materials_window  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def wait_for(condition, seconds=5.0):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        root.update_idletasks()
        root.update()
        if condition():
            return True
        time.sleep(0.02)
    return False


def pump():
    root.update_idletasks()
    root.update()



folder = tempfile.mkdtemp()
materials_panel.wishlist.load(folder)
materials_panel.engineer_book.load(folder)
materials_panel.engineer_book.set_commander("Bocheaux")
blueprints_window.show(root, materials_panel.wishlist, materials_panel.holdings, materials_panel.engineer_book, tab=blueprints_window.ENGINEERS_TAB)
bwin = blueprints_window._window
top = bwin._shell.window
top.geometry("1000x900+50+20")
top.deiconify()
pump()
bwin._engineer_table.select("Chloe Sedesi", notify=True)
pump()
note = bwin._engineer_note


def scroll_frame(widget):
    from plugin.uikit.widgets import ScrollFrame
    if isinstance(widget, ScrollFrame):
        return widget
    for child in widget.winfo_children():
        found = scroll_frame(child)
        if found is not None:
            return found
    return None


# the ScrollFrame that holds the Engineers tab: the nearest one above the details
frame = note
from plugin.uikit.widgets import ScrollFrame  # noqa: E402
while frame is not None and not isinstance(frame, ScrollFrame):
    frame = frame.master
check(frame is not None, "the details sit in a scrolling page")
canvas = frame._canvas
pump()
region = [int(float(v)) for v in canvas.cget("scrollregion").split()]
check(region[3] > canvas.winfo_height(), f"the page is taller than the window: region {region}, window {canvas.winfo_height()}")

# The pointer goes over the engineer table (a page of its own inside this one), then off it onto the page, then the wheel turns.
table = bwin._engineer_table
controls = [w for w in note.master.winfo_children() if w.winfo_y() > table.winfo_y() and w is not note][0]


def point_over(widget, dx, dy):
    return widget.winfo_rootx() - top.winfo_rootx() + dx, widget.winfo_rooty() - top.winfo_rooty() + dy


top.event_generate("<Motion>", warp=True, x=table.winfo_rootx() - top.winfo_rootx() + 60, y=table.winfo_rooty() - top.winfo_rooty() + 40)
pump()
time.sleep(0.2)
pump()
x, y = point_over(controls, controls.winfo_width() - 20, 4)
top.event_generate("<Motion>", warp=True, x=x, y=y)
pump()
time.sleep(0.2)
pump()
check(top.winfo_containing(*top.winfo_pointerxy()) is not None, "the pointer is in the window")
before = canvas.yview()[0]
for _ in range(5):
    controls.event_generate("<MouseWheel>", delta=-120)
    controls.event_generate("<Button-5>")
    pump()
after = canvas.yview()[0]
check(after > before, f"the wheel scrolls the page after the pointer has been over the table: {before} -> {after}")

blueprints_window.close() if hasattr(blueprints_window, "close") else None
if problems:
    print("PROBLEMS:", len(problems))
    for line in problems:
        print(" -", line)
    sys.exit(1)
print("ENGINEER SCROLL OK")
