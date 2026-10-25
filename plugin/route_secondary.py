"""Which neutron stops of a route may have their neutron star somewhere other than where you arrive.

Spansh's plotter counts a supercharge at any system with a neutron star, and its exclude-secondary option acts on the main-star record in its data, which comes from submitted scans. Where that
record differs from the game a route can send you to a system whose neutron star is a secondary star, thousands of light seconds from the arrival point: the supercharge then needs a long flight, and the jump after it,
planned for the boost, is not one jump. This module reads a system's stars from Spansh (`GET /api/system/<id64>`, by the address the route answer already carries) and says whether the
neutron star looks like a secondary one. It is a warning, not a fact.

The test (`neutron_is_secondary`): the arrival star of a system carries the system's own name (or that name plus " A" in a multiple system). If a star with that name exists and it is not a
neutron star, the neutron star is a secondary star. If the arrival star is the neutron star, it is not. A catalog-named neutron star in a system with no star named for it falls back to
the database's own "main star" flag. No neutron star in the data, or no data, gives no answer. It is a name rule, so it cannot judge a system whose stars are all named by letter.

`SecondaryChecker` asks for a few stops at a time in the background and never blocks the caller; a failed lookup is asked again after a pause and is never read as an answer.
"""
from __future__ import annotations

import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

WINDOW = 12            # neutron stops ahead asked about at once
RETRY_S = 300          # ask again about a lookup that failed after this long
WORKERS = 4

Fetch = Callable[[int], Optional[List[Dict[str, Any]]]]


def _is_neutron(star: Dict[str, Any]) -> bool:
    return star.get("subtype") == "Neutron Star"


def neutron_is_secondary(system: str, stars: List[Dict[str, Any]]) -> Optional[bool]:
    """True when the system's neutron star looks like a secondary star, False when it looks like the arrival star, None when there is nothing to judge from."""
    neutrons = [star for star in stars if _is_neutron(star)]
    if not neutrons:
        return None
    wanted = {" ".join(str(system).split()).casefold(), " ".join(str(system).split()).casefold() + " a"}
    named = [star for star in stars if " ".join(str(star.get("name") or "").split()).casefold() in wanted]
    if named:
        return not any(_is_neutron(star) for star in named)
    return not any(star.get("is_main_star") is True for star in neutrons)


class SecondaryChecker:
    """Asks about neutron stops in the background. `ensure` starts the lookups for stops not yet answered; `drain` hands back the answers that have arrived, once."""

    def __init__(self, fetch: Fetch, now: Callable[[], float] = time.time, background: bool = True) -> None:
        self._fetch = fetch
        self._now = now
        self._background = background
        self._lock = threading.Lock()
        self._done: Set[int] = set()
        self._asked: Set[int] = set()
        self._failed: Dict[int, float] = {}
        self._results: "queue.Queue[Tuple[str, Optional[bool]]]" = queue.Queue()
        self._busy = 0

    def busy(self) -> bool:
        with self._lock:
            return self._busy > 0

    def ensure(self, stops: Iterable[Tuple[int, str]]) -> int:
        """Start asking about the stops `(system address, name)` that have no answer and are not being asked about. Returns how many lookups were started."""
        wanted: List[Tuple[int, str]] = []
        with self._lock:
            for id64, name in stops:
                if id64 in self._done or id64 in self._asked:
                    continue
                failed = self._failed.get(id64)
                if failed is not None and self._now() - failed < RETRY_S:
                    continue
                self._asked.add(id64)
                wanted.append((id64, name))
            self._busy += len(wanted)
        if not wanted:
            return 0
        if self._background:
            threading.Thread(target=self._run, args=(wanted,), name="WFMT-route-stars", daemon=True).start()
        else:
            self._run(wanted)
        return len(wanted)

    def _run(self, wanted: List[Tuple[int, str]]) -> None:
        def one(stop: Tuple[int, str]) -> None:
            id64, name = stop
            answer: Optional[bool] = None
            ok = False
            try:
                stars = self._fetch(id64)
                if stars is not None:
                    answer, ok = neutron_is_secondary(name, stars), True
            except Exception:
                ok = False
            with self._lock:
                self._asked.discard(id64)
                self._busy -= 1
                if ok:
                    self._done.add(id64)
                    self._failed.pop(id64, None)
                else:
                    self._failed[id64] = self._now()
            if ok:
                self._results.put((name.casefold(), answer))
        if len(wanted) == 1 or not self._background:
            for stop in wanted:
                one(stop)
            return
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            list(pool.map(one, wanted))

    def drain(self) -> Dict[str, Optional[bool]]:
        """The answers that have arrived since the last call, by casefolded system name (True: probably a secondary star; False: the arrival star; None: could not judge)."""
        found: Dict[str, Optional[bool]] = {}
        while True:
            try:
                name, answer = self._results.get_nowait()
            except queue.Empty:
                return found
            found[name] = answer
