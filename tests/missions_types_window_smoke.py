"""Opens the Mission types window (plugin/missions_types_window.py) with EDMC stubbed and a stand-in for the Missions panel's drawing, and checks the
list of types with their counts, that picking one draws that page at the window's width and is remembered, that asking for a type opens on it, and
that the real MissionsUI.render_category draws a page into a frame and leaves the panel's own wrap width and background as they were. Run by
test_missions_types_window.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is
unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import json
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


try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()



try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()


try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()



from plugin import missions_types_window as window, missions_ui  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


class FakeUI:
    ORDER = ["massacre_space", "combat", "community_goal"]
    LABELS = {"massacre_space": "Massacre (Space)", "combat": "Combat", "community_goal": "Community Goals"}

    def __init__(self):
        self.drawn = []
        self.counts = {"massacre_space": 3, "combat": 0, "community_goal": 1}

    def category_order(self):
        return list(self.ORDER)

    def category_label(self, key):
        return self.LABELS[key]

    def category_counts(self):
        return dict(self.counts)

    def render_category(self, frame, category, width):
        self.drawn.append((category, width))
        tk.Label(frame, text=f"page {category}").grid(row=0, column=0)


ui = FakeUI()
window.show(root, ui)
pump()
win = window._window
check(win is not None and win.alive, "the window opens")
check(win.category == "massacre_space", f"it opens on the first type: {win.category}")
captions = [str(b.cget("text")) for b in win._buttons.values()]
check(captions == ["Massacre (Space) (3)", "Combat (0)", "Community Goals (1)"], f"the list of types with counts: {captions}")
check(ui.drawn and ui.drawn[-1][0] == "massacre_space", f"the chosen page is drawn: {ui.drawn}")
check(ui.drawn[-1][1] >= 300, f"at a usable width: {ui.drawn[-1]}")

win.pick("combat")
pump()
check(win.category == "combat" and ui.drawn[-1][0] == "combat", "picking a type draws it")
check(saved.get(window.CONFIG_CATEGORY) == "combat", "and is remembered")

ui.counts["combat"] = 2
window.refresh()
pump()
check("Combat (2)" in [str(b.cget("text")) for b in win._buttons.values()], "a refresh updates the counts")

window.show(root, ui, "community_goal")
pump()
check(window._window is win and win.category == "community_goal", "asking again for a type brings the same window to it")
check(len(window._window._scroll.body.winfo_children()) == 1, "only the chosen page is in the window")

# a redraw of the same type keeps the scroll position; picking another type starts at the top
class TallUI(FakeUI):
    def render_category(self, frame, category, width):
        self.drawn.append((category, width))
        for n in range(80):
            tk.Label(frame, text=f"{category} line {n}").grid(row=n, column=0, sticky="w")


tall = TallUI()
window.show(root, tall, "massacre_space")
pump()
scroll = window._window._scroll
scroll._canvas.yview_moveto(0.5)
pump()
before = scroll.position()
window.refresh()
pump()
check(before > 0.3 and abs(scroll.position() - before) < 0.05, f"a redraw of the same type keeps the scroll position: {before} -> {scroll.position()}")
window._window.pick("combat")
pump()
check(scroll.position() == 0.0, f"another type starts at the top: {scroll.position()}")

# the Display card: the six switches, saved to the keys Settings holds, and in step with a change made elsewhere
from plugin import missions_display_settings as D  # noqa: E402
card = window._window._display
check(set(card._vars) == {key for key, _n, _l, _t in D.FIELDS} and len(card._vars) == 6, f"the six switches: {sorted(card._vars)}")
heard = []
D.add_listener(lambda: heard.append(1))
card._vars[D.CFG_TOTALS].set(False)
D.set_value(D.CFG_TOTALS, card._vars[D.CFG_TOTALS].get())
pump()
check(saved.get(D.CFG_TOTALS) is False and heard, f"a switch is saved and the listeners hear of it: {saved.get(D.CFG_TOTALS)} {heard}")
saved[D.CFG_SETTLEMENT] = False                  # changed on the Settings tab
window.refresh()
pump()
check(card._vars[D.CFG_SETTLEMENT].get() is False, "a change made elsewhere shows on the card")
check(all(D.value(k) for k in (D.CFG_PROGRESS, D.CFG_REMAINING, D.CFG_MISSION_COUNT, D.CFG_COMMODITIES_NEEDED)), "the rest are still on (every switch starts on)")

window.close()
pump()
check(not win.alive, "close closes it")

# the real panel's drawing: into any frame, leaving its own settings alone
before = (missions_ui._content_bg, missions_ui._WRAP, missions_ui._WRAP_NAME)
frame = tk.Frame(root)
frame.pack()
missions_ui.ui.render_category(frame, "community_goal", 640)
pump()
check(len(frame.winfo_children()) > 0, "the Community Goals page draws something")
check((missions_ui._content_bg, missions_ui._WRAP, missions_ui._WRAP_NAME) == before,
      f"the panel's wrap width and background are put back: {before} -> {(missions_ui._content_bg, missions_ui._WRAP, missions_ui._WRAP_NAME)}")
for key in missions_ui.ui.category_order():
    inner = tk.Frame(root)
    missions_ui.ui.render_category(inner, key, 500)       # every type draws, with or without missions
    inner.destroy()

if problems:
    print("\n".join(problems))
    sys.exit(1)
print("MISSION TYPES OK")
