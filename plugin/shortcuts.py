"""WFMT's keyboard shortcuts and chat commands: the same actions with the same names on Windows and Linux.

Each action (`shortcut_actions.ACTIONS`) can be started two ways. On Windows, a system-wide key combination, Ctrl+Alt+Shift plus one key (a letter, a digit or F1 to F12), works while
Elite has the focus. On both systems, a chat command typed in Elite's chat (`!wf center`) works: the game writes it to the journal as a `SendText` event and WFMT acts on it. Chat commands
are off until switched on, because everyone in the channel you type into reads them. A Linux desktop gives a program no portable way to hear keys while another window has the focus, so
Linux has the chat commands only.

Settings -> General -> Shortcuts shows both for every action and checks each key combination against Elite's own controls (`elite_keybinds.py`). The pure parts (the action list, the chat
parser, the key names) are in `shortcut_actions.py`.
"""

from __future__ import annotations

import ctypes
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import tkinter as tk

import myNotebook as nb
from config import appname, config

from . import elite_keybinds
from . import overlay
from . import shortcut_actions as actions

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None   # Settings-tab-only, no main-panel widget

_CFG_CHAT = "wfmt_shortcut_chat_enabled"
_CFG_SOUND = "wfmt_shortcut_sound"

MAX_COMMAND_AGE_S = 30.0
"""A chat command older than this in the journal is ignored, so commands from before EDMC started (or replayed while catching up) are never run."""
_OK_PREFIXES = ("Center", "Border marked", "Rig ")


def hotkeys_supported() -> bool:
    return sys.platform == "win32"


def chat_enabled() -> bool:
    return bool(config.get_bool(_CFG_CHAT, False))


def sound_enabled() -> bool:
    return bool(config.get_bool(_CFG_SOUND, True))


def saved_keys() -> Dict[str, str]:
    return {a.id: actions.clean_key(config.get_str(actions.config_key(a.id)), a.default_key) for a in actions.ACTIONS}


# --- running an action --------------------------------------------------------------------------------------------------

_tk_widget: Optional[tk.Misc] = None


def set_tk_widget(widget: tk.Misc) -> None:
    """A widget on EDMC's main window, so an action started on another thread (a hotkey) runs on the Tk thread."""
    global _tk_widget
    _tk_widget = widget


def _on_tk_thread(function: Callable[[], None]) -> None:
    widget = _tk_widget
    if widget is None:
        function()
        return
    try:
        widget.after(0, function)
    except (tk.TclError, RuntimeError):
        logger.debug("Could not hand a shortcut to the Tk thread", exc_info=True)


def run(action_id: str) -> str:
    """Do one action now (on the Tk thread) and say what happened; a sound plays when it worked, if that is on. Never raises."""
    try:
        message, ok = _do(action_id)
    except Exception:
        logger.exception("Shortcut %s failed", action_id)
        return "That did not work: see EDMC's log."
    logger.info("Shortcut %s: %s", action_id, message)
    if ok and sound_enabled():
        try:
            from . import platform_support
            platform_support.play_notification_sound()
        except Exception:
            logger.debug("Could not play the shortcut sound", exc_info=True)
    return message


def _do(action_id: str) -> Tuple[str, bool]:
    if action_id in ("center", "border"):
        from . import mining_live_window
        message = mining_live_window.mark_here(action_id == "border")
        return message, message.startswith(_OK_PREFIXES)
    if action_id == "rig":
        from . import mining_live_window
        message = mining_live_window.place_rig()
        return message, message.startswith(_OK_PREFIXES)
    if action_id == "zoom":
        from . import mining_live_window
        return mining_live_window.cycle_range(), True
    if action_id == "live":
        from . import mining_live_window, mining_pages, mining_panel
        parent = _tk_widget.winfo_toplevel() if _tk_widget is not None else None
        if parent is None:
            return "The Live window needs EDMC's main window.", False
        mining_live_window.show(parent, mining_pages.SURFACE_MINING, mining_panel._settings)
        return "Opened the Surface Mining Live window.", True
    if action_id == "overlays":
        hidden = overlay.toggle_all_hidden()
        return ("Overlays hidden." if hidden else "Overlays shown."), True
    return f"Unknown shortcut {action_id}.", False


# --- chat commands (Windows and Linux) -----------------------------------------------------------------------------------

def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    """`!wf <word>` sent in chat, once chat commands are switched on, runs that action. Old journal lines are ignored."""
    if entry.get("event") != "SendText" or not chat_enabled():
        return
    chosen = actions.parse_chat(entry.get("Message"))
    if chosen is None or not actions.is_recent(entry.get("timestamp"), datetime.now(timezone.utc), MAX_COMMAND_AGE_S):
        return
    _on_tk_thread(lambda: run(chosen.id))


# --- the global key combinations (Windows) -------------------------------------------------------------------------------

_thread: Optional[threading.Thread] = None
_thread_id = 0
WM_HOTKEY, WM_QUIT = 0x0312, 0x0012


def _listen(registrations: List[Tuple[int, int, int]], ready: threading.Event, outcome: Dict[str, Any]) -> None:
    """Hold each (id, modifiers, key) until WM_QUIT; `outcome["failed"]` lists the ids another program already holds."""
    import ctypes.wintypes
    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    outcome["thread_id"] = kernel32.GetCurrentThreadId()
    held, failed = [], []
    for index, mods, key in registrations:
        (held if user32.RegisterHotKey(None, index, mods | 0x4000, key) else failed).append(index)      # 0x4000 is MOD_NOREPEAT
    outcome["failed"] = failed
    ready.set()
    msg = ctypes.wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and 1 <= int(msg.wParam) <= len(actions.ACTIONS):
                chosen = actions.ACTIONS[int(msg.wParam) - 1]
                _on_tk_thread(lambda action_id=chosen.id: run(action_id))
    finally:
        for index in held:
            user32.UnregisterHotKey(None, index)


def stop_hotkeys() -> None:
    global _thread, _thread_id
    if _thread is not None and _thread_id:
        try:
            ctypes.windll.user32.PostThreadMessageW(_thread_id, WM_QUIT, 0, 0)
        except Exception:
            logger.debug("Could not stop the shortcut thread", exc_info=True)
        _thread.join(timeout=1.0)
    _thread, _thread_id = None, 0


def start_hotkeys(keys: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Register the saved (or given) keys; returns action id -> why it is not on, for each that could not be taken. Empty when all is well, or off Windows."""
    global _thread, _thread_id
    if not hotkeys_supported():
        return {}
    keys = saved_keys() if keys is None else keys
    stop_hotkeys()
    registrations, problems = [], {}
    for index, a in enumerate(actions.ACTIONS, 1):
        combo = actions.win_hotkey(keys.get(a.id, actions.OFF))
        if combo is not None:
            registrations.append((index, combo[0], combo[1]))
    if not registrations:
        return {}
    ready, outcome = threading.Event(), {}
    thread = threading.Thread(target=_listen, args=(registrations, ready, outcome), name="WFMT-shortcuts", daemon=True)
    thread.start()
    ready.wait(2.0)
    _thread, _thread_id = thread, int(outcome.get("thread_id", 0))
    for index in outcome.get("failed", []):
        chosen = actions.ACTIONS[index - 1]
        problems[chosen.id] = f"{actions.combo_text(keys[chosen.id])} could not be taken: another program is using that combination."
    return problems


# --- Settings -> General -> Shortcuts ------------------------------------------------------------------------------------

_key_vars: Dict[str, tk.StringVar] = {}
_status_vars: Dict[str, tk.StringVar] = {}
_chat_var: Optional[tk.BooleanVar] = None
_sound_var: Optional[tk.BooleanVar] = None
_result_var: Optional[tk.StringVar] = None
_bindings: Optional[List[elite_keybinds.Binding]] = None


def _refresh_status() -> None:
    picked = {action_id: var.get() for action_id, var in _key_vars.items()}
    for action_id, var in _status_vars.items():
        var.set(actions.conflict_text(picked[action_id], picked, action_id, _bindings))


def build_settings(notebook: tk.Misc) -> None:
    global _chat_var, _sound_var, _result_var, _bindings
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Shortcuts")
    _bindings = elite_keybinds.load()
    nb.Label(
        frame,
        text=("Start an action without the mouse. Every key combination is Ctrl+Alt+Shift plus one key, a combination Elite's own controls almost never use, and the chat "
              "command is the same on Windows and Linux."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))

    table = tk.Frame(frame)
    table.grid(row=1, column=0, sticky=tk.W, padx=10, pady=(4, 2))
    for column, heading in enumerate(("Action", "Keys (Windows)", "Chat command")):
        nb.Label(table, text=heading).grid(row=0, column=column, sticky=tk.W, padx=(0, 12))
    saved = saved_keys()
    for row, a in enumerate(actions.ACTIONS, 1):
        _key_vars[a.id] = tk.StringVar(value=saved[a.id])
        _status_vars[a.id] = tk.StringVar(value="")
        nb.Label(table, text=a.label).grid(row=row * 2 - 1, column=0, sticky=tk.W, padx=(0, 12), pady=(4, 0))
        keys = tk.Frame(table)
        keys.grid(row=row * 2 - 1, column=1, sticky=tk.W, padx=(0, 12), pady=(4, 0))
        nb.Label(keys, text=actions.MODIFIER_TEXT).pack(side=tk.LEFT)
        menu = tk.OptionMenu(keys, _key_vars[a.id], *actions.KEY_CHOICES, command=lambda _v: _refresh_status())
        menu.pack(side=tk.LEFT)
        if not hotkeys_supported():
            menu.configure(state=tk.DISABLED)
        nb.Label(table, text=f"{actions.CHAT_PREFIX} {a.word}").grid(row=row * 2 - 1, column=2, sticky=tk.W, pady=(4, 0))
        nb.Label(table, textvariable=_status_vars[a.id], wraplength=420, justify=tk.LEFT).grid(row=row * 2, column=0, columnspan=3, sticky=tk.W)

    note = ("The key combinations work while Elite has the focus. If another program already holds one, WFMT says so after you press OK."
            if hotkeys_supported() else
            "The key combinations are for Windows: a Linux desktop gives a program no portable way to hear keys while another window has the focus. Use the chat commands.")
    nb.Label(frame, text=note, wraplength=440, justify=tk.LEFT).grid(row=2, column=0, sticky=tk.W, padx=10, pady=(8, 2))
    if _bindings is None:
        nb.Label(frame, text="Elite's controls file could not be found or read, so the key combinations were not checked against it.", wraplength=440,
                 justify=tk.LEFT).grid(row=3, column=0, sticky=tk.W, padx=10)

    _chat_var = tk.BooleanVar(value=chat_enabled())
    nb.Checkbutton(frame, text="Chat commands (type  !wf <word>  in Elite's chat)", variable=_chat_var).grid(row=4, column=0, sticky=tk.W, padx=10, pady=(10, 0))
    nb.Label(frame, text=("Off until you switch it on, because anyone in the chat channel you type into reads the command. Type it in a channel with nobody else in it, such as a "
                          "private one with no members. The command is read from your journal, so it works the same on Windows and Linux."),
             wraplength=440, justify=tk.LEFT).grid(row=5, column=0, sticky=tk.W, padx=10)
    _sound_var = tk.BooleanVar(value=sound_enabled())
    nb.Checkbutton(frame, text="Play a sound when a shortcut worked", variable=_sound_var).grid(row=6, column=0, sticky=tk.W, padx=10, pady=(8, 0))
    _result_var = tk.StringVar(value="")
    nb.Label(frame, textvariable=_result_var, wraplength=440, justify=tk.LEFT).grid(row=7, column=0, sticky=tk.W, padx=10, pady=(6, 10))
    _refresh_status()


def save_settings() -> None:
    if not _key_vars or _chat_var is None or _sound_var is None:
        return
    for action_id, var in _key_vars.items():
        config.set(actions.config_key(action_id), actions.clean_key(var.get(), actions.action(action_id).default_key))
    config.set(_CFG_CHAT, bool(_chat_var.get()))
    config.set(_CFG_SOUND, bool(_sound_var.get()))
    problems = start_hotkeys() if hotkeys_supported() else {}
    if _result_var is not None:
        _result_var.set("\n".join(problems.values()))
    for text in problems.values():
        logger.warning(text)


def start(plugin_dir: str) -> None:
    for text in start_hotkeys().values():
        logger.info(text)


def stop() -> None:
    stop_hotkeys()
