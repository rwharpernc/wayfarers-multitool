"""Looks up a system's Powerplay standing from Spansh's public system API (https://spansh.co.uk/api/system/<id64>), for the Powerplay overlay card's look at the system a
hyperspace jump is heading for. The journal says where you are going when the jump starts (`StartJump`) but not what Powerplay says about it, and the card should have it
by the time you arrive.

One request per destination, through spansh_courtesy.py (paced, retried when Spansh is busy, refused while it keeps failing), on a thread of its own; nothing here touches Tk.
It asks only when the Powerplay card's *Look up the system I am jumping to* tick is on (the caller checks), and sends only the system's id (the journal's SystemAddress).

An answer is one of: found (a `Standing`), none (Spansh knows the system and has no Powerplay state for it, or does not know the system), or failed (the network or Spansh
did not answer). Found and none are kept for `TTL_S` (the standing changes with the weekly cycle), but a found standing's control progress, which moves as players earn merits, is given out only for `PROGRESS_FRESH_S`; a failure is kept for `RETRY_S` so a dead network is not asked again on every
jump of a chain, and the next jump after that asks again.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, Optional, Tuple

from . import http_identity, spansh_courtesy

logger = logging.getLogger(__name__)

SYSTEM_URL = "https://spansh.co.uk/api/system/{id64}"
REQUEST_TIMEOUT_S = 8
TTL_S = 3600.0
PROGRESS_FRESH_S = 600.0      # the control progress moves as players earn merits, so it is shown only while an answer is this young; state and holder hold for the week
RETRY_S = 120.0

FOUND, NONE, FAILED, PENDING, UNKNOWN = "found", "none", "failed", "pending", "unknown"


@dataclass(frozen=True)
class Standing:
    """A system's Powerplay standing: its state (Stronghold, Fortified, Exploited, Unoccupied...), the Power that holds it, every Power active there and the control progress (0-1)."""
    state: str
    controller: str = ""
    powers: Tuple[str, ...] = ()
    progress: Optional[float] = None


def parse(data: Any) -> Optional[Standing]:
    """The standing in a Spansh answer, or None when the system has no Powerplay state (or the answer is not what was expected)."""
    record = data.get("record") if isinstance(data, dict) else None
    if not isinstance(record, dict) or not record.get("power_state"):
        return None
    powers = record.get("power")
    progress = record.get("power_state_control_progress")
    return Standing(
        state=str(record["power_state"]), controller=str(record.get("controlling_power") or ""),
        powers=tuple(str(p) for p in powers) if isinstance(powers, list) else (),
        progress=float(progress) if isinstance(progress, (int, float)) else None,
    )


_lock = threading.Lock()
_cache: Dict[int, Tuple[str, Optional[Standing], float]] = {}     # id64 -> (status, standing, when it was stored)
_pending: set = set()


def _fetch(id64: int) -> Tuple[str, Optional[Standing]]:
    request = urllib.request.Request(SYSTEM_URL.format(id64=id64), headers={"User-Agent": http_identity.user_agent("powerplay-overlay")})
    try:
        standing = parse(json.loads(spansh_courtesy.call(request, REQUEST_TIMEOUT_S).decode("utf-8")))
    except urllib.error.HTTPError as err:
        if err.code == 404:             # Spansh has not heard of the system
            return NONE, None
        logger.debug("Spansh Powerplay lookup failed for id64=%s", id64, exc_info=True)
        return FAILED, None
    except Exception:
        logger.debug("Spansh Powerplay lookup failed for id64=%s", id64, exc_info=True)
        return FAILED, None
    return (FOUND, standing) if standing is not None else (NONE, None)


def peek(id64: int, now: Optional[float] = None) -> Tuple[str, Optional[Standing]]:
    """(status, standing) for `id64` as known now: FOUND with its standing, NONE, FAILED, PENDING (being asked), or UNKNOWN (never asked, or the answer has expired)."""
    now = time.monotonic() if now is None else now
    with _lock:
        if id64 in _pending:
            return PENDING, None
        entry = _cache.get(id64)
    if entry is None:
        return UNKNOWN, None
    status, standing, stored = entry
    if now - stored > (RETRY_S if status == FAILED else TTL_S):
        return UNKNOWN, None
    if standing is not None and standing.progress is not None and now - stored > PROGRESS_FRESH_S:
        standing = replace(standing, progress=None)         # too old to quote: the state and holder are still right, the percentage has moved
    return status, standing


def request(id64: int, on_done: Optional[Callable[[], None]] = None, fetch: Callable[[int], Tuple[str, Optional[Standing]]] = _fetch, now: Callable[[], float] = time.monotonic) -> bool:
    """Asks about `id64` on a background thread unless an answer is already held or on its way; `on_done` is called from that thread when the answer is in. True when a request was started."""
    if peek(id64, now())[0] != UNKNOWN:
        return False
    with _lock:
        if id64 in _pending:
            return False
        _pending.add(id64)

    def worker() -> None:
        try:
            status, standing = fetch(id64)
        except Exception:
            logger.debug("Powerplay lookup crashed for id64=%s", id64, exc_info=True)
            status, standing = FAILED, None
        with _lock:
            _cache[id64] = (status, standing, now())
            _pending.discard(id64)
        if on_done is not None:
            try:
                on_done()
            except Exception:
                logger.debug("Powerplay lookup callback failed", exc_info=True)

    threading.Thread(target=worker, name="WFMT-powerplay-lookup", daemon=True).start()
    return True


def standing_from_journal(entry: Any) -> Optional[Standing]:
    """The standing an arrival event (FSDJump, CarrierJump, Location) carries, or None when it names no Powerplay state."""
    if not isinstance(entry, dict) or not entry.get("PowerplayState"):
        return None
    powers = entry.get("Powers")
    progress = entry.get("PowerplayStateControlProgress")
    return Standing(
        state=str(entry["PowerplayState"]), controller=str(entry.get("ControllingPower") or ""),
        powers=tuple(str(p) for p in powers) if isinstance(powers, list) else (),
        progress=float(progress) if isinstance(progress, (int, float)) else None,
    )


def store(id64: int, standing: Standing, now: Optional[float] = None) -> None:
    """Keeps a standing the journal has just given for a system you arrived in, so a later jump to it needs no request. Only a found standing is stored: a journal entry that
    names no state is not proof the system has none, so it is left to Spansh to say."""
    with _lock:
        _cache[id64] = (FOUND, standing, time.monotonic() if now is None else now)


def clear() -> None:
    """Forget every answer (the tests use this)."""
    with _lock:
        _cache.clear()
        _pending.clear()
