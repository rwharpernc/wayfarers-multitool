"""Builds Settings -> General -> Shortcuts (plugin/shortcuts.py) in a real Tk window, changes a key, saves, and checks what was kept and what the page said about a clash. Run by
test_shortcuts_settings_smoke in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
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
sys.modules["myNotebook"] = nbmod
saved = {}


class Cfg:
    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def get_bool(self, key, default=False):
        return saved.get(key, default)

    def get_int(self, key, default=0):
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


try:
    from plugin import elite_keybinds, shortcut_actions as actions, shortcuts

    with mock.patch.object(elite_keybinds, "load", return_value=elite_keybinds.parse(
            '<Root><Dummy><Primary Device="Keyboard" Key="Key_Q"><Modifier Device="Keyboard" Key="Key_LeftControl"/><Modifier Device="Keyboard" Key="Key_LeftAlt"/>'
            '<Modifier Device="Keyboard" Key="Key_LeftShift"/></Primary></Dummy></Root>')), \
            mock.patch.object(shortcuts, "start_hotkeys", return_value={}) as started:
        notebook = ttk.Notebook(root)
        shortcuts.build_settings(notebook)
        root.update()
        check(len(notebook.tabs()) == 1 and notebook.tab(notebook.tabs()[0], "text") == "Shortcuts", "the Shortcuts tab is added")
        check(set(shortcuts._key_vars) == {a.id for a in actions.ACTIONS}, "every action has a key choice")
        check(all(var.get() == "" for var in shortcuts._status_vars.values()), "nothing is flagged with the default keys")
        shortcuts._key_vars["center"].set("Q")
        shortcuts._refresh_status()
        check("Dummy" in shortcuts._status_vars["center"].get(), "a key Elite already uses on that combination is flagged by name")
        shortcuts._key_vars["border"].set("Q")
        shortcuts._refresh_status()
        check("Mark the center" in shortcuts._status_vars["border"].get(), "two WFMT actions on one key are flagged")
        shortcuts._key_vars["center"].set("F9")
        shortcuts._key_vars["border"].set("Off")
        shortcuts._chat_var.set(True)
        shortcuts.save_settings()
        check(saved.get(actions.config_key("center")) == "F9", "the chosen key is saved")
        check(saved.get(actions.config_key("border")) == "Off", "Off is saved")
        check(saved.get("wfmt_shortcut_chat_enabled") is True, "chat commands switched on are saved")
        check(shortcuts.saved_keys()["center"] == "F9" and shortcuts.saved_keys()["border"] == "Off", "the saved keys are read back")
        check(started.called or not shortcuts.hotkeys_supported(), "the key combinations are registered again after saving (Windows)")
except Exception as exc:  # noqa: BLE001
    import traceback
    problems.append("raised: " + "".join(traceback.format_exception(exc)))

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("SHORTCUTS SETTINGS OK")
