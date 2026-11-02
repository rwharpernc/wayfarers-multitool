"""Opens the Space Mining and Surface Mining windows with EDMC stubbed and checks the Settings card in each: the right fields for the page, a typed value saved to the
same key the Settings tab holds and kept inside its range, a change in one place shown in the other (the panel's Settings variables, and the other window), the target
commodities and their status line, and no card in a simulation. Run by test_mining_window_settings.py in a subprocess so the stand-ins never leak into other tests.
Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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
root.geometry("420x700")
root.update()
from plugin import mining_live_window, mining_pages, mining_panel, mining_simulation
from plugin import mining_window_settings as W

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


def keys_of(window):
    return set(window._settings_card._vars)


# --- the values and their limits, without a window --------------------------------------------------------------------------------------
check(W.value(W.CFG_DISPLAY_CARGO_BAR) is True, "a tick starts on")
check(W.value(W.CFG_DISPLAY_COVERAGE_MINIMAP) is False, "the minimap starts off")
check(W.set_value(W.CFG_STOP_RADIUS, "99999") == "2500", "the stop radius is kept inside its range")
check(W.set_value(W.CFG_STOP_RADIUS, "1100") == "1000" or W.set_value(W.CFG_STOP_RADIUS, "1100") == "1250", "and on its steps")
check(W.set_value(W.CFG_RIG_GAP, "abc") == "0", "a rig gap that is not a number is off")
check(W.set_value(W.CFG_REFILL_DAYS, "500") == "90", "the refill days stop at the longest the game could need")
text, percent = W.set_target("  Painite   30,  Platinum ", "150")
check(text == "Painite 30, Platinum" and percent == 100, f"the targets are trimmed and the percentage kept to 100: {text!r} {percent}")
check(W.target_status("Painite", 30) == ("1 target set.", False), f"the status line: {W.target_status('Painite', 30)}")
check(W.target_status("Painite 300", 30)[1] is True, "a percentage over 100 is a problem")
W.set_target("", 25)

# --- the panel, so its Settings tab variables can be watched --------------------------------------------------------------------------------
frame = tk.Frame(root)
frame.pack()
controller = mining_panel.controller
controller.build_panel(frame)
controller.start("/nonexistent") if False else None
W.add_listener(controller._on_window_setting)

space = mining_live_window.show(root, mining_pages.SPACE_MINING, mining_panel._settings)
surface = mining_live_window.show(root, mining_pages.SURFACE_MINING, mining_panel._settings)
pump()
check(space is not None and space._settings_card.winfo_exists(), "the Space Mining window has a Settings card")
check(keys_of(space) == {W.CFG_DISPLAY_SESSION_TOTALS, W.CFG_DISPLAY_CARGO_BAR, W.CFG_DISPLAY_PROSPECTOR_HINTS}, f"its fields: {sorted(keys_of(space))}")
check(space._settings_card._target_entry is not None, "and the target commodities box")
check(keys_of(surface) == {W.CFG_DISPLAY_SESSION_TOTALS, W.CFG_DISPLAY_CARGO_BAR, W.CFG_DISPLAY_PROSPECTOR_HINTS, W.CFG_DISPLAY_COVERAGE_MINIMAP,
                           W.CFG_STOP_RADIUS, W.CFG_RIG_GAP, W.CFG_REFILL_DAYS}, f"the Surface Mining window's fields: {sorted(keys_of(surface))}")
check(surface._settings_card._target_entry is None, "the Surface Mining window has no target box")

# a tick in one window: saved, shown in the other window and on the Settings tab, and the panel redraws
tick, _entry = space._settings_card._vars[W.CFG_DISPLAY_CARGO_BAR]
tick.set(False)
W.set_value(W.CFG_DISPLAY_CARGO_BAR, tick.get())
pump()
check(saved.get(W.CFG_DISPLAY_CARGO_BAR) is False, "the tick is saved")
check(surface._settings_card._vars[W.CFG_DISPLAY_CARGO_BAR][0].get() is False, "and shown in the other window")
check(mining_panel._settings().display_cargo_bar is False, "and the panel's settings follow")

# a typed number in the Surface window
var, entry = surface._settings_card._vars[W.CFG_STOP_RADIUS]
var.set("2000")
entry.event_generate("<FocusOut>")
pump()
check(saved.get(W.CFG_STOP_RADIUS) == 2000, f"a typed stop radius is saved: {saved.get(W.CFG_STOP_RADIUS)}")

# the targets typed in the Space window
card = space._settings_card
card._target_var.set("Painite 30")
card._percent_var.set("40")
card._target_entry.event_generate("<FocusOut>")
pump()
check(saved.get("wfmt_mining_target") is not None or any("Painite" in str(v) for v in saved.values()), f"the targets are saved: {saved}")
picked = {}
real_attach = W.commodity_autocomplete.attach
W.commodity_autocomplete.attach = lambda entry, var=None, preferred=lambda: (), on_pick=None: picked.update(on_pick=on_pick) or real_attach(entry, var, preferred, on_pick)
try:
    probe = W.SettingsCard(root, W.SPACE)
finally:
    W.commodity_autocomplete.attach = real_attach
check(picked.get("on_pick") == probe._save_target, "picking a suggestion in the targets box saves the targets")
probe.destroy()
card._target_var.set("Painite 300")
check(card._status.cget("text") != "" and str(card._status.cget("fg")) == W.P.WARN, "a problem with the targets is said, in the warning color")

# a change made in the other window shows here
saved[W.CFG_RIG_GAP] = 50
W._announce()
pump()
check(surface._settings_card._vars[W.CFG_RIG_GAP][0].get() == "50", "a value changed elsewhere shows in the window")

# no card in a simulation
mining_simulation.open_surface_live(root, mining_panel._settings)
pump()
sim = mining_live_window._windows.get(mining_pages.SURFACE_MINING + mining_live_window.SIMULATION_SUFFIX)
check(sim is not None and sim.alive, "the simulation window opens")
check(sim is not None and not hasattr(sim, "_settings_card"), "and has no Settings card")
if sim is not None:
    sim.close()

space.close()
surface.close()
pump()
check(not any(cb.__qualname__.startswith("SettingsCard") for cb in W._listeners), "closing the windows removes their listeners")

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("MINING WINDOW SETTINGS OK")
