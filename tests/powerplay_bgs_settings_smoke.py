"""Checks the Powerplay Sessions window's Settings tab and the BGS Report window's Settings card with EDMC stubbed: a typed value is saved to the same key the Settings tab
holds and kept inside its range, a bad value leaves the saved one, a change in one place shows in the other (the Settings tab's variables, and the window), and closing a window
removes its listeners. Run by test_powerplay_bgs_settings.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is
unavailable."""
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
root.geometry("700x700")
root.update()
from plugin import bgs_panel, bgs_settings as B, bgs_window, powerplay
from plugin.formulas import ACQUISITION, DEFAULT_RATIOS
from plugin.powerplay_settings_tab import SettingsTab

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


# --- Powerplay ------------------------------------------------------------------------------------------------------------------------------
check(powerplay.set_ratio(ACQUISITION, "5") == "5" and saved.get("wfmt_powerplay_ratio_" + ACQUISITION) == "5.0", f"a ratio is saved: {saved}")
check(powerplay.set_ratio(ACQUISITION, "-3") == "5" and powerplay.set_ratio(ACQUISITION, "abc") == "5", "a ratio that is not above 0 leaves the saved one")
check(powerplay.set_backfill_cycles("99") == "12", "the cycles stop at the most the scan can read")
check(powerplay.set_backfill_cycles("0") == "12" and powerplay.set_backfill_cycles("x") == "12", "and an unreadable number leaves them")
check(powerplay.set_backfill_cycles("6") == "6", "the cycles are saved")
check(powerplay.set_clipboard_template("{system}: {merits}") == "{system}: {merits}", "the Copy Progress format is saved")
check(powerplay.set_clipboard_template("   ") == powerplay.DEFAULT_CLIPBOARD_TEMPLATE, "and a blank one restores the default")

check(powerplay.record_sales_enabled() is True, "the sale-merit log starts on")
check(powerplay.set_record_sales(False) is False and saved.get("wfmt_powerplay_record_sales") is False, "turning it off is saved")
check(powerplay.set_record_sales(True) is True, "and on again")

controller = powerplay.controller
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)
tab = SettingsTab(frame)
pump()
var = tab._ratios[ACQUISITION]
check(var.get() == "5", f"the tab shows the saved ratio: {var.get()}")
var.set("7.5")
tab._ratio_entries[ACQUISITION].event_generate("<FocusOut>")
pump()
check(saved.get("wfmt_powerplay_ratio_" + ACQUISITION) == "7.5", "a typed ratio is saved")
tab._cycles.set("3")
tab._cycles_entry.event_generate("<FocusOut>")
pump()
check(saved.get("wfmt_powerplay_backfill_cycles") == "3", "the cycles are saved")
tab._format.set("{system} {merits}")
tab._format_entry.event_generate("<FocusOut>")
pump()
check(powerplay.clipboard_template() == "{system} {merits}", "the format is saved")
saved["wfmt_powerplay_ratio_" + ACQUISITION] = "9.0"                         # changed elsewhere
powerplay._announce_settings()
pump()
check(var.get() == "9", f"a change made elsewhere shows in the tab: {var.get()}")
check(tab._record_sales.get() is True, "the tab shows the sale-merit log as on")
tab._record_sales.set(False)
tab._parent.update()
saved["wfmt_powerplay_record_sales"] = True                                    # changed elsewhere
powerplay._announce_settings()
pump()
check(tab._record_sales.get() is True, "a change of the sale-merit switch made elsewhere shows in the tab")
check(tab.sync in powerplay._settings_listeners, "the tab listens")
frame.destroy()
pump()
check(tab.sync not in powerplay._settings_listeners, "and stops when its window closes")
check(set(DEFAULT_RATIOS) >= {ACQUISITION}, "the ratio activities are the ones with a default")

# --- BGS ------------------------------------------------------------------------------------------------------------------------------------------
check(B.enabled() is True and B.archive_days() == 7, "BGS starts on, keeping 7 days")
check(B.set_archive_days("500") == "90" and B.set_archive_days("0") == "1", "the days to keep stay inside 1 to 90")
check(B.set_archive_days("abc") == "7", "an unreadable number is the default")
heard = []
B.add_listener(lambda: heard.append(1))
bgs_window.show(root, [], None, [], [], bgs_window.TabActions(toggle_pin=lambda s: None, close=lambda s: None, add=lambda s: None))
win = bgs_window._window
pump()
card = win._settings_card
check(card.winfo_exists(), "the BGS Report window has a Settings card")
card._shown.set(False)
B.set_enabled(card._shown.get())
pump()
check(saved.get("wfmt_bgs_enabled") is False and B.enabled() is False, "the switch is saved")
check(heard, "listeners hear of it")
card._days.set("30")
card._entry.event_generate("<FocusOut>")
pump()
check(saved.get("wfmt_bgs_archive_days") == "30" and B.archive_days() == 30, "the days to keep are saved")
saved["wfmt_bgs_archive_days"] = "14"                                       # changed elsewhere
B._announce()
pump()
check(card._days.get() == "14", "a change made elsewhere shows on the card")
check("tick" in " ".join(str(w.cget("text")) for w in card.winfo_children() if isinstance(w, tk.Label)).lower(), "the card says where tick detection is switched")
win.close()
pump()
check(card.sync not in B._listeners, "closing the report removes the card's listener")

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("POWERPLAY BGS SETTINGS OK")
