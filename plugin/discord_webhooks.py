"""
The Discord webhooks of each commander, kept in `discord_webhooks.json` (one list for each commander, never shared: commander_data.py).

A webhook belongs to one Discord channel (or a thread of it), not to a game commander, so a commander can save several: one for each channel or server they
share to. Each destination has a name the commander chooses (such as "Squadron BGS" or "Friends"), the webhook link and an optional thread id. The name is what the
Post to Discord choice and the messages show, so the link never appears on screen. The two commanders can save the same link, and Settings can copy one commander's
list to another.

A webhook link is a secret, because whoever has it can post to that channel. It is never logged, never put in a message shown to the commander (discord_client.py
words its errors without it), left out of Back up my data (data_backup.LEFT_OUT) and kept off the diagnostics text. The file sits in the plugin folder beside the
other saved data and is kept by the updater. A file from the first version, which held one link with a nickname for each commander, is read as a list of one.

The master switch `wfmt_discord_enabled` is off until the commander turns it on. Posting still needs a button press every time.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional

from . import commander_data

try:
    from config import config
except ImportError:  # unit tests outside EDMC
    config = None

STATE_FILENAME = "discord_webhooks.json"
CFG_ENABLED = "wfmt_discord_enabled"    # the master switch for posting to Discord; off unless the commander turns it on
URL_MAX = 300
NAME_MAX = 40
THREAD_MAX = 25
MAX_DESTINATIONS = 10
DEFAULT_NAME = "Discord"

Destination = Dict[str, str]     # {"name", "url", "thread"}


def _empty() -> Dict[str, Any]:
    return {"destinations": []}


def _is_legacy(_raw: Any) -> bool:
    return False


def clean(items: Iterable[Any]) -> List[Destination]:
    """The destinations as they are kept: an entry with no link is dropped, a missing name becomes "Discord", names are one line and unique (a repeat gets " 2",
    " 3"...), each value is clipped, and there are at most MAX_DESTINATIONS."""
    result: List[Destination] = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        link = str(item.get("url") or "").strip()[:URL_MAX]
        if not link:
            continue
        name = " ".join(str(item.get("name") or item.get("nickname") or "").split())[:NAME_MAX] or DEFAULT_NAME
        base, number = name, 2
        while name.casefold() in seen:
            suffix = f" {number}"
            name, number = base[:NAME_MAX - len(suffix)] + suffix, number + 1
        seen.add(name.casefold())
        result.append({"name": name, "url": link, "thread": str(item.get("thread") or "").strip()[:THREAD_MAX]})
        if len(result) >= MAX_DESTINATIONS:
            break
    return result


class DiscordWebhooks:
    def __init__(self, plugin_dir: Optional[str] = None) -> None:
        self._plugin_dir = plugin_dir or os.path.dirname(os.path.abspath(__file__))
        self._store = commander_data.read(os.path.join(self._plugin_dir, STATE_FILENAME), _is_legacy)

    def destinations(self, cmdr: str) -> List[Destination]:
        """This commander's saved destinations, in the order they were saved (empty when none)."""
        if not commander_data.known(self._store, cmdr):
            return []
        saved = commander_data.payload_for(self._store, cmdr, _empty)
        if not isinstance(saved, dict):
            return []
        if "destinations" in saved:
            return clean(saved["destinations"] or [])
        return clean([saved])      # the first version's shape: {"url", "nickname", "thread"}

    def find(self, cmdr: str, name: str = "") -> Optional[Destination]:
        """The destination called `name` (any case), or the first one when `name` is empty. None when there is no such destination."""
        found = self.destinations(cmdr)
        if not name:
            return found[0] if found else None
        return next((d for d in found if d["name"].casefold() == name.strip().casefold()), None)

    def set_destinations(self, cmdr: str, items: Iterable[Any]) -> List[Destination]:
        """Save this commander's destinations (see `clean`); an empty list forgets them all. Returns what was kept."""
        if not commander_data.key_for(cmdr):
            return []
        kept = clean(items)
        commander_data.put(self._store, cmdr, {"destinations": kept})
        commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)
        return kept

    def other_commanders(self, cmdr: str) -> List[str]:
        """The names of the other commanders who have destinations saved, for the Settings tab's copy choice."""
        mine = commander_data.key_for(cmdr)
        names = []
        for key, entry in sorted(self._store.get("commanders", {}).items()):
            if key != mine and self.destinations(str(entry.get("name") or key)):
                names.append(str(entry.get("name") or key))
        return names


webhooks = DiscordWebhooks()


def enabled() -> bool:
    """The master switch: whether WFMT may post to Discord at all. Off by default; turning it off stops posting at once and keeps the saved links."""
    try:
        return bool(config is not None and config.get_bool(CFG_ENABLED, default=False))
    except Exception:
        return False


def ready(cmdr: str) -> bool:
    """Whether Post to Discord can be used for this commander: the switch is on and at least one destination is saved."""
    return enabled() and bool(webhooks.destinations(cmdr))
