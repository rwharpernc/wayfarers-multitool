"""Real systems near a position that nobody has scanned, for the Boxel Survey Random button.

Random used to guess a procedural name inside a nearby boxel and test it against EDSM. A guess that EDSM has
never heard of is usually a name that does not exist, so nearly everything it returned was invalid. This
module asks Spansh for the systems that do exist around the commander, nearest first, and keeps those
with no scan data on record. The caller then confirms each pick with EDSM before showing it.

Spansh's `body_count` is None (or 0) for a system whose bodies nobody has submitted. That is the best
available proxy for "undiscovered": the system exists and is listed, but no scan reached the databases.
It is not proof that nobody has visited, since a visit without a scan leaves no body data.

The call goes through `spansh_courtesy`. Raises on network or parse failure (an OSError while WFMT is holding off Spansh); run it off the Tk main thread and catch the exception.
"""

from __future__ import annotations

import json
import math
import random
import threading
import time
import urllib.request
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from . import http_identity, spansh_courtesy

SEARCH_URL = "https://spansh.co.uk/api/systems/search"
REQUEST_TIMEOUT_S = 20
_USER_AGENT = http_identity.user_agent("boxel-random")

# Systems requested per call, nearest first. Most systems nearby have no scans, so a
# page this size nearly always holds enough candidates without a second request.
PAGE_SIZE = 25
# The pick is random among this many of the nearest candidates, so repeated clicks vary but stay close.
POOL_SIZE = 8
# How long a fetched list stays usable, and how far from the fetch position it stays usable.
CACHE_TTL_S = 600.0
CACHE_RADIUS_LY = 5.0


def fetch_nearby(x: float, y: float, z: float, size: int = PAGE_SIZE) -> List[Dict[str, Any]]:
    """Systems nearest to (x, y, z), nearest first, as Spansh returns them."""
    body = json.dumps({
        "filters": {},
        "sort": [{"distance": {"direction": "asc"}}],
        "size": size,
        "page": 0,
        "reference_coords": {"x": x, "y": y, "z": z},
    }).encode("utf-8")
    request = urllib.request.Request(
        SEARCH_URL, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": _USER_AGENT},
    )
    data = json.loads(spansh_courtesy.call(request, REQUEST_TIMEOUT_S).decode("utf-8"))
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        raise ValueError(f"Unexpected Spansh systems-search response shape: {type(data)!r}")
    return [entry for entry in results if isinstance(entry, dict)]


def unscanned(entries: List[Dict[str, Any]], visited: FrozenSet[str], here: Optional[str] = None) -> List[Dict[str, Any]]:
    """The entries with no scan data on record, minus systems the commander already visited."""
    out = []
    for entry in entries:
        name = entry.get("name")
        if not name or name in visited or name == here:
            continue
        if entry.get("body_count"):
            continue
        out.append(entry)
    return out


def distance_from(entry: Dict[str, Any], pos: Tuple[float, float, float]) -> float:
    """Light-years from `pos` to the entry; falls back to Spansh's own figure when coordinates are missing."""
    try:
        return math.dist(pos, (float(entry["x"]), float(entry["y"]), float(entry["z"])))
    except (KeyError, TypeError, ValueError):
        return float(entry.get("distance") or 0.0)


def pick_order(candidates: List[Dict[str, Any]], pool: int = POOL_SIZE) -> List[Dict[str, Any]]:
    """The nearest `pool` candidates in random order, then the rest nearest first, so a failed
    EDSM confirmation falls through to the next candidate."""
    head = list(candidates[:pool])
    random.shuffle(head)
    return head + list(candidates[pool:])


class NearbyCache:
    """Keeps the last Spansh list in memory so repeated Random clicks in one place skip the slow search.

    The list is reused while it is younger than `ttl` seconds, was fetched within `radius` light-years of the
    asking position, and was requested at the same size. Names already offered, or found scanned on EDSM, are
    remembered as used so the next click moves on. Nothing is saved to disk. The EDSM check still runs on every
    click, so a system scanned after the list was fetched is caught there.
    """

    def __init__(self, ttl: float = CACHE_TTL_S, radius: float = CACHE_RADIUS_LY, clock=time.monotonic) -> None:
        self._ttl, self._radius, self._clock = ttl, radius, clock
        self._lock = threading.Lock()
        self._entries: List[Dict[str, Any]] = []
        self._pos: Optional[Tuple[float, float, float]] = None
        self._size = 0
        self._fetched_at = 0.0
        self._used: Set[str] = set()

    def get(self, x: float, y: float, z: float, size: int) -> Optional[List[Dict[str, Any]]]:
        """The cached entries still usable for this position and size, or None."""
        with self._lock:
            if self._pos is None or size != self._size or self._clock() - self._fetched_at > self._ttl:
                return None
            if math.dist(self._pos, (x, y, z)) > self._radius:
                return None
            return [e for e in self._entries if e.get("name") not in self._used]

    def put(self, x: float, y: float, z: float, size: int, entries: List[Dict[str, Any]]) -> None:
        with self._lock:
            self._entries, self._pos, self._size = list(entries), (x, y, z), size
            self._fetched_at, self._used = self._clock(), set()

    def mark_used(self, name: str) -> None:
        with self._lock:
            self._used.add(name)

    def clear(self) -> None:
        with self._lock:
            self._pos = None
            self._entries = []
            self._used = set()
