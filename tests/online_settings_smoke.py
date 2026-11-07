"""Builds Settings -> Online (plugin/settings_online.py) in a real Tk window with EDMC stubbed and checks that every lookup has a checkbox under its service, that
Turn all on, Turn all off and Reset to defaults set the boxes, that saving writes every switch, and that a change hook runs once for a switch that changed and not for one that did not.
Run by test_online_settings_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from tkinter import ttk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes",
          "psutil", "ttkHyperlinkLabel", "theme"):
    sys.modules[n] = Any(n)
nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
nbmod.Notebook = ttk.Notebook
sys.modules["myNotebook"] = nbmod
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

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


from plugin import online_lookups, settings_online, star_index_settings  # noqa: E402

calls = []
hook_module = types.ModuleType("plugin.fakehook")
hook_module.online_changed = lambda: calls.append("changed")
sys.modules["plugin.fakehook"] = hook_module
settings_online.HOOKS["wfmt_bgs_tick_enabled"] = "fakehook.online_changed"

saved["wfmt_trade_lookups_enabled"] = True               # one switch already on before the page is built
notebook = ttk.Notebook(root)
with mock.patch.object(star_index_settings, "build_group", lambda parent, row: None):
    settings_online.build_settings(notebook)
root.update()
page = root.nametowidget(notebook.tabs()[0])
check(notebook.tab(notebook.tabs()[0], "text") == "Online", "the tab is called Online")


def everything(widget):
    for child in widget.winfo_children():
        yield child
        yield from everything(child)


widgets = list(everything(page))
boxes = [w for w in widgets if isinstance(w, tk.Checkbutton)]
texts = [str(w.cget("text")) for w in widgets if isinstance(w, tk.Label)]
buttons = [str(w.cget("text")) for w in widgets if isinstance(w, tk.Button)]
check(len(boxes) == len(online_lookups.LOOKUPS) == 21, f"a checkbox for each lookup: {len(boxes)}")
check({str(b.cget("text")) for b in boxes} == {entry[0] for entry in online_lookups.LOOKUPS}, "each box carries the lookup's own name")
for heading in ("Spansh", "EDSM", "Raven Colonial", "Community tick service", "GitHub"):
    check(heading in texts, f"the {heading} heading is on the page")
check({"Turn all on", "Turn all off", "Reset to defaults"} <= set(buttons), f"the three buttons: {buttons}")
check(settings_online._vars["wfmt_trade_lookups_enabled"].get() is True, "a switch that was on shows on")
check(settings_online._vars["wfmt_bgs_tick_enabled"].get() is True, "tick detection ships on")
check(sum(1 for v in settings_online._vars.values() if v.get()) == 2, "and nothing else is on")

settings_online.turn_all_off()
check(not any(v.get() for v in settings_online._vars.values()), "Turn all off unticks every box, tick detection included")
check(saved.get("wfmt_bgs_tick_enabled") is None, "and saves nothing by itself")
settings_online.save_settings()
check(all(saved[entry[2]] is False for entry in online_lookups.LOOKUPS), "saving writes every switch, all off")
check(calls == ["changed"], f"the hook ran once, for the switch that changed: {calls}")
settings_online.save_settings()
check(calls == ["changed"], f"and not again when nothing changed: {calls}")

settings_online.reset_defaults()
check({k: v.get() for k, v in settings_online._vars.items()} == online_lookups.defaults(), "Reset to defaults puts every box back to how WFMT ships")
settings_online.save_settings()
check(saved["wfmt_bgs_tick_enabled"] is True and saved["wfmt_trade_lookups_enabled"] is False, "and saving keeps tick detection on and the rest off")
check(calls == ["changed", "changed"], f"the hook ran for tick detection coming back on: {calls}")

settings_online.turn_all_on()
check(all(v.get() for v in settings_online._vars.values()), "Turn all on ticks every box, automatic updates included")
check(saved["wfmt_auto_update"] is False, "and saves nothing by itself")
settings_online.save_settings()
check(all(saved[entry[2]] is True for entry in online_lookups.LOOKUPS), "saving writes every switch, all on")
check(calls == ["changed", "changed"], f"tick detection was already on, so its hook did not run again: {calls}")

root.destroy()
if problems:
    print("\n".join(problems))
    sys.exit(1)
print("ONLINE SETTINGS OK")
