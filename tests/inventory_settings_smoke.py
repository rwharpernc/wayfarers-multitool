"""Checks the Inventory window's Settings tab with EDMC stubbed: the pillage message, the sound, the announce categories and the suit capacities are saved to the keys the
Settings tab holds, a blank or default value restores the default, a bad number leaves the saved one, a change in one place shows in the other, and closing the window removes
its listener. Run by test_inventory_settings.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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
import json
from plugin import inventory_settings as S, inventory_suit as suit, inventory_panel
from plugin.inventory import TRACKED_CATEGORIES
from plugin.inventory_settings_tab import SettingsTab

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


CMDR = "Bocheaux"
check(S.message_format() == S.DEFAULT_MESSAGE_FORMAT, "the message starts as the default")
check(S.set_message_format("  Got {item}: {total}  ") == "Got {item}: {total}" and saved.get(S.CFG_MESSAGE_FORMAT) == "Got {item}: {total}", "a message is saved, trimmed")
check(S.set_message_format("   ") == S.DEFAULT_MESSAGE_FORMAT, "a blank message is the default")
check(S.announced_categories() == frozenset(TRACKED_CATEGORIES), "every category announces to begin with")
first = TRACKED_CATEGORIES[0]
check(S.set_announced(first, False) is False and first not in S.announced_categories(), "a category can be muted")
check(json.loads(saved[S.CFG_ANNOUNCE_CATEGORIES]) == [c for c in TRACKED_CATEGORIES if c != first], "and is saved as the Settings tab saves it")
check(S.set_announced("Nonsense", True) is False, "an unknown category changes nothing")
S.set_announced(first, True)
check(S.set_sound_enabled(True) is True and S.sound_enabled(), "the sound is saved")
S.set_sound_enabled(False)

suit.record_loadout(CMDR, "7", name="Mining", suit_key="utilitysuit", grade=1, has_capacity_mod=False)
record = suit.known_loadouts_for(CMDR)["7"]
check(S.capacity_text(record, "Item") == "40", "a capacity starts as the suit default")
check(S.set_capacity(CMDR, "7", "Item", "55") == "55" and record["overrides"]["Item"] == 55, "a different number is kept as an override")
check(S.set_capacity(CMDR, "7", "Item", "40") == "40" and "Item" not in record["overrides"], "the default clears the override")
check(S.set_capacity(CMDR, "7", "Item", "55") == "55" and S.set_capacity(CMDR, "7", "Item", "") == "40" and "Item" not in record["overrides"], "blank clears it")
check(S.set_capacity(CMDR, "7", "Item", "abc") == "40" and S.set_capacity(CMDR, "7", "Item", "-5") == "40", "a bad number leaves it")
check(json.loads(saved[suit.CONFIG_SUIT_OVERRIDES]).get(CMDR, {}).get("7") is not None, "the loadouts are saved")

# --- the tab ---------------------------------------------------------------------------------------------------------------------------------
panel = inventory_panel.controller
panel._message_format_var = tk.StringVar(value="")
panel._sound_var = tk.BooleanVar(value=False)
panel._announce_vars = {c: tk.BooleanVar(value=True) for c in TRACKED_CATEGORIES}
panel._override_vars = {("7", "Item"): tk.StringVar(value="40")}
panel._tracker.set_commander(CMDR)
S.add_listener(panel._on_window_setting)
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)
tab = SettingsTab(frame, lambda: CMDR)
pump()
check(("7", "Item") in tab._capacity_vars and ("7", "Data") in tab._capacity_vars, f"a row for each category of the loadout: {sorted(tab._capacity_vars)}")
tab._format.set("Picked {item}")
tab._format_entry.event_generate("<FocusOut>")
pump()
check(panel._message_format_var.get() == "Picked {item}", "a typed message shows on the Settings tab")
tab._announce[first].set(False)
S.set_announced(first, tab._announce[first].get())
pump()
check(panel._announce_vars[first].get() is False, "a muted category shows on the Settings tab")
var = tab._capacity_vars[("7", "Item")]
var.set("65")
tab._capacity_entries[("7", "Item")].event_generate("<FocusOut>")
pump()
check(record["overrides"].get("Item") == 65 and panel._override_vars[("7", "Item")].get() == "65", "a typed capacity is saved and shown on the Settings tab")
saved[S.CFG_MESSAGE_FORMAT] = "From Settings {item}"                         # changed on the Settings tab
S.announce()
pump()
check(tab._format.get() == "From Settings {item}", "a change made elsewhere shows in the tab")
suit.record_loadout(CMDR, "8", name="Fight", suit_key="tacticalsuit", grade=1, has_capacity_mod=True)
tab.sync()
pump()
check(("8", "Item") in tab._capacity_vars, "a suit worn since appears as a new row")
check(tab._capacity_vars[("8", "Item")].get() == "20", "pre-filled with its (modded) default")
frame.destroy()
pump()
check(tab.sync not in S._listeners, "closing the window removes the tab listener")

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("INVENTORY SETTINGS OK")
