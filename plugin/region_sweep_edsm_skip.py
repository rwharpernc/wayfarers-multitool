"""Pure logic (no Tk, no EDMC, no network) for Region Sweep's option "Skip systems already visited by anyone (EDSM)".

Given the next candidate target and a way to step to the following one, `skip_known_candidates` asks a lookup whether each candidate is known to EDSM and steps past
the ones that are, up to a fixed cap. The lookup is passed in (the panel passes `edsm_client.system_known`), so this module is tested without a network.

A lookup that cannot tell (it returns None: offline, EDSM down, an odd answer) stops the walk and keeps the candidate in hand. A failure never skips anything.
Answers are kept in a `KnownSystemCache` for the session so a name is asked about once; a failed lookup is not cached, so it is tried again later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

# The most candidates one advance steps past before it stops and shows the last one, so a long run of charted systems cannot become a long run of requests.
MAX_SKIP_ATTEMPTS = 20
# Bounds the session cache: one small entry per system asked about.
MAX_CACHE_ENTRIES = 5000


class KnownSystemCache:
    """Remembers, for this session only, whether EDSM knew each system when it was asked. Names match without regard to case, as EDSM's do."""

    def __init__(self, max_entries: int = MAX_CACHE_ENTRIES) -> None:
        self._max = max_entries
        self._known: Dict[str, bool] = {}

    def get(self, name: str) -> Optional[bool]:
        return self._known.get(name.casefold())

    def put(self, name: str, known: bool) -> None:
        if len(self._known) >= self._max and name.casefold() not in self._known:
            self._known.pop(next(iter(self._known)))  # drop the oldest answer
        self._known[name.casefold()] = known

    def clear(self) -> None:
        self._known.clear()

    def __len__(self) -> int:
        return len(self._known)


@dataclass
class SkipResult:
    candidate: Optional[str]  # the target to offer
    skipped: int  # how many known systems were stepped past
    gave_up: bool  # stopped at MAX_SKIP_ATTEMPTS with `candidate` still known to EDSM
    lookup_failed: bool  # a lookup could not tell, so `candidate` was kept unchecked


def skip_known_candidates(
    candidate: Optional[str],
    advance: Callable[[], Optional[str]],
    lookup: Callable[[str], Optional[bool]],
    cache: KnownSystemCache,
    max_attempts: int = MAX_SKIP_ATTEMPTS,
) -> SkipResult:
    """Step past candidates that EDSM already knows. `advance()` returns the next candidate (None when there is none); `lookup(name)` returns True (known),
    False (not known) or None (could not tell)."""
    skipped = 0
    while candidate is not None:
        known = cache.get(candidate)
        if known is None:
            known = lookup(candidate)
            if known is None:
                return SkipResult(candidate, skipped, False, True)
            cache.put(candidate, known)
        if not known:
            return SkipResult(candidate, skipped, False, False)
        if skipped >= max_attempts:
            return SkipResult(candidate, skipped, True, False)
        following = advance()
        if following is None:
            return SkipResult(candidate, skipped, False, False)
        candidate = following
        skipped += 1
    return SkipResult(None, skipped, False, False)
