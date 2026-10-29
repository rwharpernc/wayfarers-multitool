"""
The Discord webhook of each commander, kept in `discord_webhooks.json` (one entry per commander, never shared: commander_data.py).

A webhook link is a secret, because whoever has it can post to that channel. It is never logged, never put in a message shown to the commander
(discord_client.py words its errors without it), left out of Back up my data (data_backup.LEFT_OUT) and kept off the diagnostics text. The file
sits in the plugin folder beside the other saved data and is kept by the updater. Each commander also has a nickname (only a label for them, such as
the server's name, so a message can say which webhook it used without showing the link) and an optional thread id.

The master switch `wfmt_discord_enabled` is off until the commander turns it on. Posting still needs a button press every time.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from . import commander_data

try:
    from config import config
except ImportError:  # unit tests outside EDMC
    config = None

STATE_FILENAME = "discord_webhooks.json"
CFG_ENABLED = "wfmt_discord_enabled"    # the master switch for posting to Discord; off unless the commander turns it on
URL_MAX = 300
NICKNAME_MAX = 40
THREAD_MAX = 25


def _empty() -> Dict[str, Any]:
    return {"url": "", "nickname": "", "thread": ""}


def _is_legacy(_raw: Any) -> bool:
    return False


class DiscordWebhooks:
    def __init__(self, plugin_dir: Optional[str] = None) -> None:
        self._plugin_dir = plugin_dir or os.path.dirname(os.path.abspath(__file__))
        self._store = commander_data.read(os.path.join(self._plugin_dir, STATE_FILENAME), _is_legacy)

    def get(self, cmdr: str) -> Dict[str, str]:
        """This commander's webhook as {"url", "nickname", "thread"}; every value is empty when none is saved."""
        if not commander_data.known(self._store, cmdr):
            return _empty()
        saved = commander_data.payload_for(self._store, cmdr, _empty)
        return {key: str(saved.get(key) or "") for key in ("url", "nickname", "thread")}

    def url(self, cmdr: str) -> str:
        return self.get(cmdr)["url"]

    def set(self, cmdr: str, url: str, nickname: str = "", thread: str = "") -> None:
        """Save (or, given an empty link, forget) this commander's webhook."""
        if not commander_data.key_for(cmdr):
            return
        link = (url or "").strip()[:URL_MAX]
        commander_data.put(self._store, cmdr, {"url": link, "nickname": " ".join((nickname or "").split())[:NICKNAME_MAX] if link else "",
                                               "thread": (thread or "").strip()[:THREAD_MAX] if link else ""})
        commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)


webhooks = DiscordWebhooks()


def enabled() -> bool:
    """The master switch: whether WFMT may post to Discord at all. Off by default; turning it off stops posting at once and keeps the saved link."""
    try:
        return bool(config is not None and config.get_bool(CFG_ENABLED, default=False))
    except Exception:
        return False


def ready(cmdr: str) -> bool:
    """Whether Post to Discord can be used for this commander: the switch is on and a link is saved."""
    return enabled() and bool(webhooks.url(cmdr))
