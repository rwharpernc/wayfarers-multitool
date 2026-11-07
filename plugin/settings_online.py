"""Settings → Online: every switch that lets WFMT contact another service, in one place, grouped by the service it asks.

WFMT reads your journal and files on your own computer; anything that asks the internet is a switch here and nowhere else (what each one sends is in
docs/guide/internet-and-privacy.md). The page has a checkbox for each, **Turn all off** (every lookup off in one press, and automatic updates and BGS tick
detection with them) and **Reset to defaults** (every switch back to how WFMT ships). Both only set the boxes; **OK** or **Apply** in EDMC's Settings
saves them, like every other setting. The features read the saved settings exactly as before, so nothing else about them changed. Some features need more than
the saved value when a switch changes (the BGS tick poller): they list a function in `HOOKS` that is called when the box was changed. The one other set of
controls on the page is the local star index (`star_index_settings.py`). `tests/test_settings_online.py` fails when an entry names a setting the code does not have.
"""
from __future__ import annotations

import importlib
import logging
import tkinter as tk
from typing import Callable, Dict

import myNotebook as nb
from config import config

from . import star_index_settings
from .online_lookups import BUTTON_ONLY, GROUPS, LOOKUPS, defaults

logger = logging.getLogger(__name__)

# saved setting -> "module.function" called after the box was changed and saved, for a switch that needs more than the saved value (a poller to start or stop).
# The modules are imported when needed, so this page stays light. Filled for the features whose switch used to do more than write the setting.
HOOKS: Dict[str, str] = {
    "wfmt_bgs_tick_enabled": "bgs_panel.online_changed",                    # starts or stops the tick poller and redraws the BGS section
    "wfmt_targets_known": "targets_overlay.online_changed",                  # starts the Spansh lookup at once when you are already in a system
    "wfmt_rcc_enabled": "colonization_settings.online_changed",              # an open Colonization Sites window re-reads the master switch
}

_vars: Dict[str, tk.BooleanVar] = {}


def turn_all_off() -> None:
    """Untick every box. Nothing is saved until Settings is applied."""
    for var in _vars.values():
        var.set(False)


def reset_defaults() -> None:
    """Put every box back to how WFMT ships. Nothing is saved until Settings is applied."""
    for key, var in _vars.items():
        var.set(defaults()[key])


def save_settings() -> None:
    """Write every box that was built, and call the hook of each one that changed."""
    for _what, _service, key, default, _where in LOOKUPS:
        var = _vars.get(key)
        if var is None:
            continue
        wanted = bool(var.get())
        changed = wanted != bool(config.get_bool(key, default=default))
        config.set(key, wanted)
        if changed:
            _call_hook(key)


def _call_hook(key: str) -> None:
    target = HOOKS.get(key)
    if not target:
        return
    module_name, _, function = target.partition(".")
    try:
        hook: Callable[[], None] = getattr(importlib.import_module(f"{__package__}.{module_name}"), function)
        hook()
    except Exception:
        logger.warning("The change to %s could not be applied at once; it takes effect when EDMC restarts", key, exc_info=True)


def build_settings(notebook: nb.Notebook) -> None:
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Online")
    _vars.clear()
    nb.Label(frame, text="Online", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
    nb.Label(
        frame,
        text=("WFMT reads your journal and game files on this computer. Everything that asks another service is a switch on this page and nowhere else, grouped by who is "
              "asked. Each is off unless noted. What each one sends is in the guide under internet and privacy."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 6))
    buttons = tk.Frame(frame)
    buttons.grid(row=2, column=0, sticky=tk.W, padx=10, pady=(0, 4))
    nb.Button(buttons, text="Turn all off", command=turn_all_off).pack(side=tk.LEFT)
    nb.Button(buttons, text="Reset to defaults", command=reset_defaults).pack(side=tk.LEFT, padx=(6, 0))
    row = 3
    for title, services, note in GROUPS:
        entries = [entry for entry in LOOKUPS if entry[1] in services]
        if not entries:
            continue
        nb.Label(frame, text=title, font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=(10, 0))
        nb.Label(frame, text=note, wraplength=440, justify=tk.LEFT, foreground="gray").grid(row=row + 1, column=0, sticky=tk.W, padx=10)
        row += 2
        for what, service, key, default, where in entries:
            var = tk.BooleanVar(value=bool(config.get_bool(key, default=default)))
            _vars[key] = var
            line = tk.Frame(frame)
            line.grid(row=row, column=0, sticky=tk.W, padx=(24, 10))
            nb.Checkbutton(line, text=what, variable=var).pack(side=tk.LEFT)
            used = f"({service}; {where})" if service == "EDSM and Spansh" else f"({where})"      # a lookup that asks two services says so
            nb.Label(line, text=used, foreground="gray").pack(side=tk.LEFT, padx=(6, 0))
            row += 1
    nb.Label(frame, text="Only when you open or press something (no switch):", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=(12, 2))
    row += 1
    for what, service in BUTTON_ONLY:
        nb.Label(frame, text=f"{what} ({service})", wraplength=440, justify=tk.LEFT).grid(row=row, column=0, sticky=tk.W, padx=10)
        row += 1
    star_index_settings.build_group(frame, row)
    nb.Label(frame, text="").grid(row=row + 6, column=0, pady=4)
