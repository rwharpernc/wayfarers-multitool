"""
The Discord Settings tab: the master switch, the commander's webhook (link, nickname, thread id) and a Test button.

Settings-tab-only (no main-panel widget). It also notes which commander is playing, from the journal, because the webhook is saved for each
commander and the reports share to the one in the window. The link is a secret: the box hides it, it is saved only on this computer, left out of
Back up my data, and never logged or shown (discord_client.py, discord_webhooks.py). Nothing is posted from here: Test webhook only asks Discord
whether the link works, and a report is posted only when its Post to Discord button is pressed. See docs/guide/discord.md for the walk-through
that is also summarized on the tab.
"""
from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
from typing import Any, Dict, Optional

import myNotebook as nb
from config import appname, config

from . import discord_client, discord_webhooks

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None   # Settings-tab-only, no main-panel widget

_cmdr = ""
_vars: Dict[str, Any] = {}
_result: Optional[nb.Label] = None


def commander() -> str:
    """The commander the journal last named, or an empty string before login."""
    return _cmdr


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    global _cmdr
    if cmdr:
        _cmdr = cmdr


SETUP_TEXT = (
    "Share your reports to a Discord channel. First make a webhook in Discord: open the channel's settings (the gear beside its name), "
    "then Integrations, Webhooks and New Webhook. Name it, pick the channel and press Copy Webhook URL, then paste the link below. "
    "To post into a thread instead, turn on Developer Mode in Discord (User Settings, Advanced), right-click the thread, choose Copy Thread ID "
    "and paste it into Thread ID. Try it in a private channel of your own first."
)
SECRET_TEXT = (
    "Whoever has the link can post to that channel, so WFMT saves it for {who} only, on this computer, leaves it out of Back up my data and "
    "never shows it or writes it to a log. Nothing is posted until you press Post to Discord on a report. Copy for Discord needs no webhook "
    "and sends nothing anywhere."
)


def build_settings(notebook: nb.Notebook) -> None:
    global _result
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Discord")
    saved = discord_webhooks.webhooks.get(_cmdr)

    nb.Label(frame, text="Discord", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
    nb.Label(frame, text=SETUP_TEXT, wraplength=440, justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 6))

    _vars["enabled"] = tk.BooleanVar(value=discord_webhooks.enabled())
    nb.Checkbutton(frame, text="Allow Post to Discord (reports are still only posted when you press the button)",
                   variable=_vars["enabled"]).grid(row=2, column=0, sticky=tk.W, padx=10, pady=(0, 4))

    for row, (key, label, secret, width) in enumerate((("url", "Webhook link:", True, 34), ("nickname", "Nickname:", False, 24),
                                                       ("thread", "Thread ID (optional):", False, 24)), start=3):
        line = tk.Frame(frame)
        line.grid(row=row, column=0, sticky=tk.W, padx=(30, 10), pady=2)
        nb.Label(line, text=label).pack(side=tk.LEFT)
        _vars[key] = tk.StringVar(value=saved[key])
        entry_options = {"show": "*"} if secret else {}
        nb.EntryMenu(line, textvariable=_vars[key], width=width, **entry_options).pack(side=tk.LEFT, padx=(4, 0))

    test_row = tk.Frame(frame)
    test_row.grid(row=6, column=0, sticky=tk.W, padx=(30, 10), pady=(4, 2))
    tk.Button(test_row, text="Test webhook", command=_test).pack(side=tk.LEFT)
    _result = nb.Label(test_row, text="", wraplength=300, justify=tk.LEFT)
    _result.pack(side=tk.LEFT, padx=(8, 0))

    who = _cmdr or "the current commander"
    nb.Label(frame, text=SECRET_TEXT.format(who=who) + ("" if _cmdr else " Log in to the game first so WFMT knows whose webhook this is."),
             wraplength=440, justify=tk.LEFT).grid(row=7, column=0, sticky=tk.W, padx=10, pady=(6, 4))
    nb.Label(frame, text="Test webhook asks Discord whether the link works and posts nothing. It tests what is typed, before you save.",
             wraplength=440, justify=tk.LEFT).grid(row=8, column=0, sticky=tk.W, padx=10, pady=(0, 10))


def _test() -> None:
    """Ask Discord about the link in the box (a read that posts nothing) and show the answer beside the button."""
    label = _result
    if label is None or "url" not in _vars:
        return
    link = _vars["url"].get().strip()
    if not link:
        label.configure(text="Paste the webhook link first.", foreground="#c07000")
        return
    label.configure(text="Asking Discord…", foreground="")

    def worker() -> None:
        try:
            name = discord_client.check(link)
            outcome, color = f"Works: {name}.", "#2e7d32"
        except discord_client.DiscordError as err:
            outcome, color = str(err), "#c07000"
        except Exception as err:
            logger.error("Discord webhook check failed (%s)", type(err).__name__)      # never the text or a traceback: either could hold the link
            outcome, color = "The check failed unexpectedly; see the EDMC log.", "#c07000"
        try:
            label.after(0, lambda: label.configure(text=outcome, foreground=color))
        except tk.TclError:
            pass   # the Settings dialog was closed before the answer came

    threading.Thread(target=worker, name="WFMT-discord-check", daemon=True).start()


def save_settings() -> None:
    if not _vars:
        return
    config.set(discord_webhooks.CFG_ENABLED, bool(_vars["enabled"].get()))
    if _cmdr:
        discord_webhooks.webhooks.set(_cmdr, _vars["url"].get(), _vars["nickname"].get(), _vars["thread"].get())
