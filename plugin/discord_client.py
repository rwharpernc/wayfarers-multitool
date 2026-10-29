"""
Posting to a Discord webhook: the link the commander saved in Settings, one message at a time, only when they press Post to Discord.

A webhook link is a secret (whoever has it can post to that channel), so this module never puts it in an error message, a log line or anything
shown to the commander, and drops the underlying error with `from None` so a traceback cannot carry it either. Every message is sent with
`allowed_mentions` empty, so nothing in a report can ping anyone, and with `wait=true` so Discord answers with the message (its id is what lets a
repeat post edit the earlier one). A `thread_id` posts into a thread of the webhook's channel.

The network is reached only through the `opener` argument (urllib's `urlopen` by default), and the wait before a retry through `sleep`, so the
tests run without either. A request that Discord answers with 429 (or a brief server error) is retried once after the wait Discord asks for,
at most `RETRY_WAIT_MAX_S`. See DISCORD_SHARING_RESEARCH.md for what is sent and when.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, Optional, Tuple

from . import http_identity
from .discord_format import MESSAGE_LIMIT

TIMEOUT_S = 15
MAX_BYTES = 100_000                  # a message or webhook answer is a few kilobytes
RETRY_CODES = (429, 502, 503)
RETRY_WAIT_S = 2.0
RETRY_WAIT_MAX_S = 10.0
HOSTS = ("discord.com", "ptb.discord.com", "canary.discord.com", "discordapp.com")

_PATH = re.compile(r"^/api(?:/v\d+)?/webhooks/(\d+)/([A-Za-z0-9_\-]+)/?$")
_ID = re.compile(r"^\d{1,25}$")


class DiscordError(Exception):
    """A problem posting to Discord, worded for the commander. Never contains the webhook link."""


class NotFound(DiscordError):
    """Discord says the webhook, or the message being edited, is not there (deleted). A repeat post falls back to a new message."""


def parse_webhook(url: str) -> Tuple[str, str]:
    """(the webhook's address without any query, the thread id written on the end of it, or ""). Raises DiscordError when `url` is not a Discord
    webhook link, so a pasted web page or a typing slip is caught before anything is sent."""
    try:
        parts = urllib.parse.urlsplit((url or "").strip())
    except ValueError:
        parts = urllib.parse.urlsplit("")
    match = _PATH.match(parts.path or "")
    if parts.scheme != "https" or (parts.hostname or "").lower() not in HOSTS or match is None:
        raise DiscordError("That is not a Discord webhook link. It looks like https://discord.com/api/webhooks/...")
    thread = urllib.parse.parse_qs(parts.query).get("thread_id", [""])[0]
    return f"https://{parts.hostname.lower()}/api/webhooks/{match.group(1)}/{match.group(2)}", thread if _ID.match(thread) else ""


def _address(url: str, thread: str, message_id: str = "", wait: bool = False) -> str:
    base, from_link = parse_webhook(url)
    if message_id:
        if not _ID.match(str(message_id)):
            raise DiscordError("That message cannot be edited.")
        base += f"/messages/{message_id}"
    query = {}
    if wait:
        query["wait"] = "true"
    thread = (thread or from_link or "").strip()
    if thread:
        if not _ID.match(thread):
            raise DiscordError("The thread id must be a number (copy it from Discord with Developer Mode on).")
        query["thread_id"] = thread
    return base + ("?" + urllib.parse.urlencode(query) if query else "")


def _retry_wait(err: urllib.error.HTTPError) -> float:
    """How long Discord asks us to wait: `retry_after` in its answer, else the Retry-After header, else a short default, never above the cap."""
    wait = RETRY_WAIT_S
    try:
        body = json.loads(err.read(MAX_BYTES).decode("utf-8"))
        if isinstance(body, dict) and body.get("retry_after") is not None:
            wait = float(body["retry_after"])
        elif err.headers and err.headers.get("Retry-After"):
            wait = float(err.headers.get("Retry-After"))
    except (ValueError, TypeError, OSError, UnicodeDecodeError, AttributeError):
        try:
            wait = float(err.headers.get("Retry-After", "")) if err.headers else RETRY_WAIT_S
        except (TypeError, ValueError, AttributeError):
            wait = RETRY_WAIT_S
    return max(0.0, min(RETRY_WAIT_MAX_S, wait))


def _send(method: str, address: str, body: Optional[Dict[str, Any]], opener: Callable[..., Any], sleep: Callable[[float], None]) -> bytes:
    headers = {"User-Agent": http_identity.user_agent("discord")}
    data: Optional[bytes] = None
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    for attempt in (1, 2):
        request = urllib.request.Request(address, data=data, method=method, headers=headers)
        try:
            with opener(request, timeout=TIMEOUT_S) as response:
                return response.read(MAX_BYTES)
        except urllib.error.HTTPError as err:
            if err.code in RETRY_CODES and attempt == 1:
                sleep(_retry_wait(err))
                continue
            if err.code == 404:
                raise NotFound("Discord could not find that webhook or message. It may have been deleted.") from None
            if err.code in (401, 403):
                raise DiscordError("Discord did not accept that webhook link. It may have been changed or removed.") from None
            if err.code == 429:
                raise DiscordError("Discord is asking for a pause. Wait a little and try again.") from None
            if err.code == 400:
                raise DiscordError("Discord refused the message (400). It may be too long.") from None
            raise DiscordError(f"Discord answered with an error ({err.code}).") from None
        except (urllib.error.URLError, OSError, TimeoutError):
            raise DiscordError("Could not reach Discord. Check your connection and try again.") from None
    return b""


def _body(content: str) -> Dict[str, Any]:
    if not (content or "").strip():
        raise DiscordError("There is nothing to post.")
    if len(content) > MESSAGE_LIMIT:
        raise DiscordError(f"That message is longer than Discord allows ({MESSAGE_LIMIT:,} characters).")
    return {"content": content, "allowed_mentions": {"parse": []}}


def _message_id(raw: bytes) -> str:
    try:
        data = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    except (ValueError, UnicodeDecodeError):
        return ""
    value = str(data.get("id") or "") if isinstance(data, dict) else ""
    return value if _ID.match(value) else ""


def post(url: str, content: str, thread: str = "", opener: Callable[..., Any] = urllib.request.urlopen,
         sleep: Callable[[float], None] = time.sleep) -> str:
    """Post `content` (at most 2,000 characters) to the webhook, optionally into `thread`. Returns the new message's id ("" if Discord did not say),
    which `edit` needs to change it later."""
    return _message_id(_send("POST", _address(url, thread, wait=True), _body(content), opener, sleep))


def edit(url: str, message_id: str, content: str, thread: str = "", opener: Callable[..., Any] = urllib.request.urlopen,
         sleep: Callable[[float], None] = time.sleep) -> str:
    """Replace the text of a message this webhook posted. Raises NotFound when it has been deleted."""
    return _message_id(_send("PATCH", _address(url, thread, message_id), _body(content), opener, sleep)) or str(message_id)


def delete(url: str, message_id: str, thread: str = "", opener: Callable[..., Any] = urllib.request.urlopen,
           sleep: Callable[[float], None] = time.sleep) -> None:
    """Remove a message this webhook posted (used when a report that was posted in several messages now needs fewer)."""
    _send("DELETE", _address(url, thread, message_id), None, opener, sleep)


def check(url: str, opener: Callable[..., Any] = urllib.request.urlopen, sleep: Callable[[float], None] = time.sleep) -> str:
    """Ask Discord about the webhook without posting anything. Returns its name (or "that webhook"), or raises DiscordError."""
    raw = _send("GET", _address(url, ""), None, opener, sleep)
    try:
        data = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    except (ValueError, UnicodeDecodeError):
        data = {}
    return str(data.get("name") or "that webhook").strip()[:60] if isinstance(data, dict) else "that webhook"
