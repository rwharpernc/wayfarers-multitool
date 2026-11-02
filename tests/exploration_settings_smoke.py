"""Checks the Exploration settings that live in windows (the Expedition ticks, the Prediction review record switch, Track codex entries) with EDMC stubbed: each is saved to the key the
Settings tab holds, the panels and the Settings tabs follow a change made in a window, a change made elsewhere shows on the strip, and closing a window removes its listener. Run by
test_exploration_settings.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ".")
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
nb = Any("myNotebook")
nb.Frame, nb.Label, nb.Button, nb.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nb
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
saved = {}


class Cfg:
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
cfgmod.user_agent = "t"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.geometry("900x500")
root.update()
import tempfile
from unittest import mock as _mock
from plugin import codex_completionist_panel, exploration_settings as X, organic_scan_panel, expedition_panel
from plugin import codex_completionist_window as CW, exo_observations, exo_review_window as ER
from plugin.codex_completionist import CodexTally

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


# --- the values -------------------------------------------------------------------------------------------------------------------------------
check(X.value(X.EXPEDITION_AUTOCOPY) is False and X.value(X.EXPEDITION_START_LOG) is True and X.value(X.EXO_OBSERVE) is True and X.value(X.CODEX_TRACK) is True,
      "the ticks start as Settings starts them")
check(X.set_value(X.EXPEDITION_AUTOCOPY, True) is True and saved.get(X.EXPEDITION_AUTOCOPY) is True, "a tick is saved")
X.set_value(X.EXPEDITION_AUTOCOPY, False)
check(X.set_value("wfmt_something_else", True) is True and "wfmt_something_else" not in saved, "an unknown key is not written")
check(expedition_panel.autocopy_enabled() is False and expedition_panel.start_log_enabled() is True, "the panel reads the same values")

# --- the panel's own tick follows a window --------------------------------------------------------------------------------------------------
exp = expedition_panel.controller
exp._autocopy_var = tk.BooleanVar(value=False)
X.set_value(X.EXPEDITION_AUTOCOPY, True)
check(exp._autocopy_var.get() is True, "the panel's Copy on arrival tick follows a change made in the Expedition window")
X.set_value(X.EXPEDITION_AUTOCOPY, False)
check(exp._autocopy_var.get() is False, "and turning it off")
check(organic_scan_panel.observing() is True and codex_completionist_panel.enabled() is True, "the other two read the same saved values")
X.set_value(X.EXO_OBSERVE, False)
X.set_value(X.CODEX_TRACK, False)
check(organic_scan_panel.observing() is False and codex_completionist_panel.enabled() is False, "and follow a change made in their windows")
X.set_value(X.EXO_OBSERVE, True)
X.set_value(X.CODEX_TRACK, True)

# --- the strip --------------------------------------------------------------------------------------------------------------------------------
frame = tk.Frame(root)
frame.pack(fill="x")
strip = X.TickStrip(frame, "Settings", X.EXPEDITION_FIELDS, note="x")
strip.pack(fill="x")
pump()
check(set(strip._vars) == {X.EXPEDITION_AUTOCOPY, X.EXPEDITION_START_LOG}, "the strip has one tick for each field")
strip._vars[X.EXPEDITION_AUTOCOPY].set(True)
X.set_value(X.EXPEDITION_AUTOCOPY, strip._vars[X.EXPEDITION_AUTOCOPY].get())
saved[X.EXPEDITION_START_LOG] = False                                  # changed elsewhere
X.announce()
pump()
check(strip._vars[X.EXPEDITION_START_LOG].get() is False, "a change made elsewhere shows on the strip")
frame.destroy()
pump()
check(strip.sync not in X._listeners, "closing the window removes the strip listener")
X.set_value(X.EXPEDITION_AUTOCOPY, False)
X.set_value(X.EXPEDITION_START_LOG, True)

# --- the Prediction review window: the switch, the count and clearing -----------------------------------------------------------------------
from plugin import organic_scan as scan

BACTERIUM = "$Codex_Ent_Bacterial_Genus_Name;"
AURASUS = "$Codex_Ent_Bacterial_01_Name;"
book = exo_observations.ObservationBook()
book.load(tempfile.mkdtemp())
ER.show(root, book)
win = ER._window
pump()
check(win is not None and X.EXO_OBSERVE in win._settings_strip._vars, "the review window has the record switch")
check("0 finds on 0 bodies" in win._recorded.cget("text"), f"and how much is recorded: {win._recorded.cget('text')!r}")
with _mock.patch.object(ER.dialogs, "confirm", lambda *a, **k: True):
    win._clear_record()                                                 # nothing to clear: no question asked, nothing changes
check(book.count() == 0, "clearing an empty record does nothing")
here = scan.BodyConditions(body_name="Sol 3", planet_class="Rocky body", atmosphere="CarbonDioxide", gravity_g=0.2, temperature_k=180.0, pressure_atm=0.05,
                           volcanism="", star_type="K", system_name="Sol", system_body_types=("Rocky body",))
book.record(here, [BACTERIUM], BACTERIUM, AURASUS, "Bacterium Aurasus", "Teal", exo_observations.predicted_keys(BACTERIUM, here), when="2026-10-17T10:00:00Z")
win.refresh()
pump()
check("1 find on 1 body" in win._recorded.cget("text"), f"a find is counted: {win._recorded.cget('text')!r}")
with _mock.patch.object(ER.dialogs, "confirm", lambda *a, **k: False):
    win._clear_record()
check(book.count() == 1, "saying no to the question keeps the record")
with _mock.patch.object(ER.dialogs, "confirm", lambda *a, **k: True):
    win._clear_record()
pump()
check(book.count() == 0 and "0 finds on 0 bodies" in win._recorded.cget("text"), "saying yes clears it and the count follows")
win.close()
pump()
check(win._show_recorded not in X._listeners, "closing the review window removes its listener")

# --- the My Codex window -----------------------------------------------------------------------------------------------------------------------
cwin = CW.CodexCompletionistWindow(root, CodexTally(), tempfile.mkdtemp())
pump()
check(X.CODEX_TRACK in cwin._settings_strip._vars, "the My Codex window has Track codex entries")
cwin._settings_strip._vars[X.CODEX_TRACK].set(False)
X.set_value(X.CODEX_TRACK, False)
pump()
check(codex_completionist_panel.enabled() is False, "and it turns the tracking off")
X.set_value(X.CODEX_TRACK, True)
cwin.close()
pump()

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("EXPLORATION SETTINGS OK")
