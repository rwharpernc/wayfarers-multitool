"""Checks the Colonization Sites window's Raven Colonial strip with EDMC stubbed: the two reporting choices are saved to the keys the Settings tab holds only while the master
switch (which stays in Settings) is on, the ticks are grayed out and refused while it is off, the strip says what is reported, a change in one place shows in the other, and
closing the window removes its listener. Run by test_colonization_settings.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not,
77 if Tk is unavailable."""
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
root.geometry("700x300")
root.update()
from plugin import colonization_panel, colonization_settings as C, rcc_keys

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


# --- the values: the window cannot grant the master consent --------------------------------------------------------------------------------
check(C.master_on() is False and C.progress_chosen() is False and C.carrier_chosen() is False, "everything starts off")
check(C.set_progress(True) is False and saved.get(C.CFG_RCC_PROGRESS) is None, "with the master switch off, a tick is refused and nothing is saved")
check(C.set_carrier(True) is False and saved.get(C.CFG_RCC_CARRIER) is None, "for the carrier choice too")
check(rcc_keys.CFG_ENABLED not in saved, "and the window never touches the master switch")

# --- the strip ---------------------------------------------------------------------------------------------------------------------------------
panel = colonization_panel.controller
panel._rcc_progress_var = tk.BooleanVar(value=False)                     # what the Settings tab would hold
panel._rcc_carrier_var = tk.BooleanVar(value=False)
C.add_listener(panel._on_window_setting)
frame = tk.Frame(root)
frame.pack(fill="x")
cmdr = ["Bocheaux"]
strip = C.RavenStrip(frame, lambda: cmdr[0])
strip.pack(fill="x")
pump()
check(str(strip._progress_box.cget("state")) == "disabled" and str(strip._carrier_box.cget("state")) == "disabled", "with the master switch off the ticks are grayed out")
check("Settings" in strip._state.cget("text") and "Nothing is sent" in strip._state.cget("text"), f"and the strip says nothing is sent and where to change it: {strip._state.cget('text')!r}")

saved[rcc_keys.CFG_ENABLED] = True                                          # the master switch turned on in Settings
C.announce()
pump()
check(str(strip._progress_box.cget("state")) == "normal", "turning the master switch on in Settings enables the ticks")
check("nothing is being reported" in strip._state.cget("text"), f"and says nothing is reported yet: {strip._state.cget('text')!r}")
check("no key yet" in strip._state.cget("text"), "and that there is no key yet")

strip._progress.set(True)
check(C.set_progress(True) is True and saved.get(C.CFG_RCC_PROGRESS) is True, "with the master switch on a tick is saved")
pump()
check(panel._rcc_progress_var.get() is True, "and shown on the Settings tab")
check("progress and deliveries" in strip._state.cget("text"), f"the strip says what is reported: {strip._state.cget('text')!r}")
C.set_carrier(True)
pump()
check("fleet carrier cargo" in strip._state.cget("text") and panel._rcc_carrier_var.get() is True, "the carrier choice too")
check(colonization_panel.rcc_share_progress() and colonization_panel.rcc_share_carrier(), "and the panel's reporting reads the same values")

saved[C.CFG_RCC_PROGRESS] = False                                           # changed on the Settings tab
C.announce()
pump()
check(strip._progress.get() is False, "a change made on the Settings tab shows on the strip")

saved[rcc_keys.CFG_ENABLED] = False                                         # the master switch off again: choices kept, reporting stops
C.announce()
pump()
check(colonization_panel.rcc_share_carrier() is False, "with the master switch off nothing is reported, whatever the ticks say")
check(saved.get(C.CFG_RCC_CARRIER) is True, "but the choice is kept for when it is switched on")

frame.destroy()
pump()
check(strip.refresh not in C._listeners, "closing the window removes the strip listener")

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("COLONIZATION SETTINGS OK")
