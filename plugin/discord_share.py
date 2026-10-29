"""
What the report windows call to share a report with Discord: copy it for pasting, or post it to one of the commander's saved destinations.

Copy for Discord needs no webhook and sends nothing. Post to Discord sends the report's messages to a destination (a named webhook, see discord_webhooks.py), on a
background thread so the window never freezes, only when its button is pressed, and only when the switch on the Discord Settings tab is on and a destination is
saved. With one destination the button posts to it; with several, `post_choosing` shows a small menu of their names first, so nothing goes anywhere unchosen.

A report posted again under the same key to the same destination (for example the BGS report of the same tick) edits the messages it posted before instead of adding
new ones: the ids are remembered for the session only, a message that has been deleted in Discord is simply posted again, and a report that now needs fewer messages
deletes the extra ones. The same report sent to two destinations keeps two sets of ids. Errors come back as the plain sentences discord_client.py words, which never
contain the webhook link.
"""
from __future__ import annotations

import logging
import os
import threading
import time
import tkinter as tk
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from config import appname

from . import discord_client, discord_settings, discord_webhooks, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

NOT_READY = "Turn on Post to Discord and save a webhook link on the Settings, Discord tab first."
_posted: Dict[Tuple[str, str, str], List[str]] = {}      # (commander, report key, destination) -> the ids of the messages posted for it, this session only
_busy = threading.Lock()


def commander() -> str:
    return discord_settings.commander()


def ready() -> bool:
    """Whether Post to Discord can be used now: the switch is on and the current commander has saved a destination."""
    return discord_webhooks.ready(commander())


def copy_for_discord(widget: tk.Misc, messages: Sequence[str]) -> bool:
    """Put the report's messages on the clipboard for pasting into Discord, a blank line between them when there are several (paste each one
    as its own message, since Discord allows 2,000 characters in one). Returns False when the clipboard could not be reached."""
    return panelkit.copy_to_clipboard(widget, "\n\n".join(messages))


def send(cmdr: str, messages: Sequence[str], key: str, destination: str = "", opener: Callable[..., Any] = urllib.request.urlopen,
         sleep: Callable[[float], None] = time.sleep) -> str:
    """Post (or edit the earlier posts of) the report `key` for `cmdr` to the destination named `destination` (the first one when empty) and return a sentence saying
    what happened. Blocking: run it on a worker thread. Raises DiscordError, worded for the commander."""
    target = discord_webhooks.webhooks.find(cmdr, destination)
    if target is None:
        raise discord_client.DiscordError(f"There is no destination called {destination}. Check the Settings, Discord tab." if destination else NOT_READY)
    if not messages:
        raise discord_client.DiscordError("There is nothing to post.")
    link, thread, where = target["url"], target["thread"], target["name"]
    slot = ((cmdr or "").casefold(), key, where.casefold())
    prior = _posted.get(slot, [])
    ids: List[str] = []
    edited = added = 0
    for index, text in enumerate(messages):
        message_id = ""
        if index < len(prior) and prior[index]:
            try:
                message_id = discord_client.edit(link, prior[index], text, thread, opener=opener, sleep=sleep)
                edited += 1
            except discord_client.NotFound:
                message_id = ""
        if not message_id:
            message_id = discord_client.post(link, text, thread, opener=opener, sleep=sleep)
            added += 1
        if message_id:
            ids.append(message_id)
    for old in prior[len(messages):]:
        try:
            discord_client.delete(link, old, thread, opener=opener, sleep=sleep)
        except discord_client.DiscordError:
            pass   # already gone, or not ours to remove: the report no longer needs it either way
    _posted[slot] = ids
    count = len(messages)
    if edited and not added:
        return f"Updated your earlier post in {where}."
    if edited:
        return f"Updated your earlier post in {where} and added {added} more message{'s' if added != 1 else ''}."
    return f"Posted to {where}" + (f" ({count} messages)." if count > 1 else ".")


def post_async(widget: tk.Misc, messages: Sequence[str], key: str, done: Callable[[str, bool], None], destination: str = "",
               opener: Callable[..., Any] = urllib.request.urlopen, sleep: Callable[[float], None] = time.sleep) -> None:
    """Post the report to `destination` on a background thread and call `done(sentence, ok)` back on the window's thread when it finishes (or at once when it
    cannot start). One post at a time: a second press while one is under way says so."""
    cmdr = commander()
    if not discord_webhooks.ready(cmdr):
        done(NOT_READY, False)
        return
    if not _busy.acquire(blocking=False):
        done("A post is already on its way.", False)
        return
    messages = list(messages)

    def finish(text: str, ok: bool) -> None:
        try:
            widget.after(0, lambda: done(text, ok))
        except (tk.TclError, RuntimeError):
            pass   # the window was closed before the answer came

    def worker() -> None:
        try:
            text, ok = send(cmdr, messages, key, destination, opener, sleep), True
        except discord_client.DiscordError as err:
            text, ok = str(err), False
        except Exception as err:
            logger.error("Posting to Discord failed (%s)", type(err).__name__)      # never the text or a traceback: either could hold the link
            text, ok = "Posting failed unexpectedly; see the EDMC log.", False
        finally:
            _busy.release()
        finish(text, ok)

    threading.Thread(target=worker, name="WFMT-discord-post", daemon=True).start()


def _popup(widget: tk.Misc, names: Sequence[str], choose: Callable[[str], None]) -> None:
    """A small menu of the destination names at the mouse pointer; picking one calls `choose(name)`."""
    menu = tk.Menu(widget, tearoff=0)
    for name in names:
        menu.add_command(label=f"Post to {name}", command=lambda name=name: choose(name))
    menu.add_separator()
    menu.add_command(label="Cancel")
    try:
        menu.tk_popup(widget.winfo_pointerx(), widget.winfo_pointery())
    finally:
        menu.grab_release()


def post_choosing(widget: tk.Misc, messages: Sequence[str], key: str, done: Callable[[str, bool], None],
                  popup: Optional[Callable[[tk.Misc, Sequence[str], Callable[[str], None]], None]] = None, **transport: Any) -> None:
    """Post the report: to the commander's only destination, or, when they saved several, to the one they pick from a small menu of names. With none saved (or the
    switch off) `done` says what to set up. `transport` (opener, sleep) is for the tests."""
    cmdr = commander()
    if not discord_webhooks.ready(cmdr):
        done(NOT_READY, False)
        return
    names = [d["name"] for d in discord_webhooks.webhooks.destinations(cmdr)]
    if len(names) == 1:
        post_async(widget, messages, key, done, names[0], **transport)
    else:
        (popup or _popup)(widget, names, lambda name: post_async(widget, messages, key, done, name, **transport))
