"""
The Discord Settings tab: the master switch and the commander's destinations (each a name, a webhook link and an optional thread id), with a Test button for each.

Settings-tab-only (no main-panel widget). It also notes which commander is playing, from the journal, because destinations are saved for each commander and the
reports share to the one in the window. A commander can have several destinations (a webhook belongs to one channel, so one for each channel or server), and
Settings can copy another commander's list. The link is a secret: the box hides it, it is saved only on this computer, left out of Back up my data, and never
logged or shown (discord_client.py, discord_webhooks.py). Nothing is posted from here: Test only asks Discord whether a link works, and a report is posted only
when its Post to Discord button is pressed. See docs/guide/discord.md for the walk-through that is also summarized on the tab.
"""
from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
from typing import Any, Dict, List, Optional

import myNotebook as nb
from config import appname, config

from . import discord_client, discord_customize, discord_templates, discord_webhooks

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None   # Settings-tab-only, no main-panel widget

_cmdr = ""
_pending: Optional[List[Dict[str, str]]] = None      # destinations saved from Settings before any commander was known: written when the journal names one
_vars: Dict[str, Any] = {}
_rows: List[Dict[str, Any]] = []                     # one for each destination on the tab: {"name", "url", "thread"} variables, its frame and its result label
_list_frame: Optional[tk.Frame] = None
_next_grid_row = 0


def commander() -> str:
    """The commander the journal last named, or an empty string before login."""
    return _cmdr


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    global _cmdr, _pending
    if cmdr:
        _cmdr = cmdr
        if _pending is not None:
            items, _pending = _pending, None
            discord_webhooks.webhooks.set_destinations(_cmdr, items)       # typed before login: it belongs to the commander who has just logged in


SETUP_TEXT = (
    "Share your reports to Discord channels. A webhook belongs to one channel, so make one for each channel you want to post to: in Discord open the channel's "
    "settings (the gear beside its name), then Integrations, Webhooks and New Webhook. Name it, pick the channel and press Copy Webhook URL, then add a "
    "destination below and paste the link. To post into a thread instead, turn on Developer Mode in Discord (User Settings, Advanced), right-click the thread, choose "
    "Copy Thread ID and paste it into Thread ID. Try a private channel of your own first."
)
SECRET_TEXT = (
    "Each commander has their own list: these destinations are saved for {who} only, on this computer. Whoever has a link can post to that channel, so WFMT leaves it "
    "out of Back up my data and never shows it or writes it to a log. With more than one destination, Post to Discord asks which one each time. Nothing is posted until "
    "you press it. Copy for Discord needs no webhook and sends nothing anywhere."
)


def _add_row(values: Optional[Dict[str, str]] = None) -> None:
    """A destination on the tab: name and thread id on one line, the link (hidden) on the next, then its Test and Remove buttons."""
    global _next_grid_row
    if _list_frame is None or len(_rows) >= discord_webhooks.MAX_DESTINATIONS:
        return
    values = values or {}
    row: Dict[str, Any] = {"name": tk.StringVar(value=values.get("name", "")), "url": tk.StringVar(value=values.get("url", "")),
                           "thread": tk.StringVar(value=values.get("thread", ""))}
    frame = tk.Frame(_list_frame)
    frame.grid(row=_next_grid_row, column=0, sticky=tk.W, pady=(0, 6))
    _next_grid_row += 1
    first = tk.Frame(frame)
    first.pack(anchor=tk.W)
    nb.Label(first, text="Name:").pack(side=tk.LEFT)
    nb.EntryMenu(first, textvariable=row["name"], width=20).pack(side=tk.LEFT, padx=(4, 10))
    nb.Label(first, text="Thread ID (optional):").pack(side=tk.LEFT)
    nb.EntryMenu(first, textvariable=row["thread"], width=20).pack(side=tk.LEFT, padx=(4, 0))
    second = tk.Frame(frame)
    second.pack(anchor=tk.W, pady=(2, 0))
    nb.Label(second, text="Webhook link:").pack(side=tk.LEFT)
    nb.EntryMenu(second, textvariable=row["url"], width=46, show="*").pack(side=tk.LEFT, padx=(4, 0))
    third = tk.Frame(frame)
    third.pack(anchor=tk.W, pady=(2, 0))
    tk.Button(third, text="Test", command=lambda: _test(row)).pack(side=tk.LEFT)
    tk.Button(third, text="Remove", command=lambda: _remove(row)).pack(side=tk.LEFT, padx=(6, 0))
    row["result"] = nb.Label(third, text="", wraplength=300, justify=tk.LEFT)
    row["result"].pack(side=tk.LEFT, padx=(8, 0))
    row["frame"] = frame
    _rows.append(row)


def _remove(row: Dict[str, Any]) -> None:
    if row in _rows:
        _rows.remove(row)
        try:
            row["frame"].destroy()
        except tk.TclError:
            pass


def _copy_from(source: str) -> None:
    """Add the destinations another commander saved (the ones whose link this list does not have yet). Saved with the rest when Settings closes."""
    have = {r["url"].get().strip() for r in _rows}
    for destination in discord_webhooks.webhooks.destinations(source):
        if destination["url"] not in have:
            _add_row(destination)


def build_settings(notebook: nb.Notebook) -> None:
    global _list_frame, _next_grid_row
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Discord")
    _rows.clear()
    _next_grid_row = 0

    nb.Label(frame, text="Discord", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
    nb.Label(frame, text=SETUP_TEXT, wraplength=440, justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 6))

    _vars["enabled"] = tk.BooleanVar(value=discord_webhooks.enabled())
    nb.Checkbutton(frame, text="Allow Post to Discord (reports are still only posted when you press the button)",
                   variable=_vars["enabled"]).grid(row=2, column=0, sticky=tk.W, padx=10, pady=(0, 4))

    nb.Label(frame, text="Destinations", font=("TkDefaultFont", 9, "bold")).grid(row=3, column=0, sticky=tk.W, padx=10, pady=(6, 2))
    _list_frame = tk.Frame(frame)
    _list_frame.grid(row=4, column=0, sticky=tk.W, padx=(30, 10))
    for destination in discord_webhooks.webhooks.destinations(_cmdr):
        _add_row(destination)
    if not _rows:
        _add_row()

    buttons = tk.Frame(frame)
    buttons.grid(row=5, column=0, sticky=tk.W, padx=(30, 10), pady=(2, 2))
    tk.Button(buttons, text="Add destination", command=_add_row).pack(side=tk.LEFT)
    tk.Button(buttons, text="Customize posts…", command=lambda: discord_customize.show(frame, discord_templates.BGS)).pack(side=tk.LEFT, padx=(14, 0))
    others = discord_webhooks.webhooks.other_commanders(_cmdr)
    if others:
        chosen = tk.StringVar(value=others[0])
        tk.OptionMenu(buttons, chosen, *others).pack(side=tk.LEFT, padx=(14, 4))
        tk.Button(buttons, text="Copy their destinations", command=lambda: _copy_from(chosen.get())).pack(side=tk.LEFT)

    who = _cmdr or "the current commander"
    nb.Label(frame, text=SECRET_TEXT.format(who=who) + ("" if _cmdr else " WFMT has not seen you log in yet: what you type here is kept and saved for the commander who logs in next."),
             wraplength=440, justify=tk.LEFT).grid(row=6, column=0, sticky=tk.W, padx=10, pady=(6, 4))
    nb.Label(frame, text="Test asks Discord whether the link works and posts nothing. It tests what is typed, before you save.",
             wraplength=440, justify=tk.LEFT).grid(row=7, column=0, sticky=tk.W, padx=10, pady=(0, 10))


def _test(row: Dict[str, Any]) -> None:
    """Ask Discord about the link in this row (a read that posts nothing) and show the answer beside the button."""
    label = row.get("result")
    if label is None:
        return
    link = row["url"].get().strip()
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
    global _pending
    if "enabled" not in _vars:
        return
    config.set(discord_webhooks.CFG_ENABLED, bool(_vars["enabled"].get()))
    items = [{"name": r["name"].get(), "url": r["url"].get(), "thread": r["thread"].get()} for r in _rows]
    if _cmdr:
        discord_webhooks.webhooks.set_destinations(_cmdr, items)
    else:
        _pending = [item for item in items if item["url"].strip()] or None
