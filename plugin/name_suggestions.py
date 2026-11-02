"""Type-ahead for the boxes that take a name WFMT can list: the bodies and rings of a system, ships, and commodities typed as a comma-separated list.

Systems have `system_autocomplete` and a single commodity `commodity_autocomplete`; this module is the rest, built on the same list (`system_autocomplete.attach` with a provider), so the
keys are the same everywhere: Down and Up move through the suggestions, Enter or a click takes one, Escape closes the list, and Enter with nothing highlighted goes on to whatever the box
already did. Everything is local: the names come from what WFMT already holds, and nothing is fetched.

- **Bodies and rings** (`attach_bodies`): the bodies scanned in the system you are in, the bodies of the system's saved hotspots, and the bodies an earlier lookup of that system listed.
- **Ships** (`attach_ships`): the ship names the game uses.
- **Commodity lists** (`attach_commodity_list`): a box that takes several commodities separated by commas; the suggestions are for the one being typed.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional, Sequence

from . import commodity_autocomplete, system_autocomplete, trade_ship

MAX_SUGGESTIONS = 16


def match(names: Sequence[str], text: str, limit: int = MAX_SUGGESTIONS) -> List[str]:
    """The names that start with `text` (ignoring case), then those that contain it, each once, A to Z within each group. Nothing typed offers the first `limit` names."""
    clean = " ".join(str(text).split()).casefold()
    seen = set()
    starts: List[str] = []
    contains: List[str] = []
    for name in sorted({str(n).strip() for n in names if str(n).strip()}, key=lambda n: (n.casefold(), n)):      # a tie in case goes to the capitalized name, every time
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        if not clean or key.startswith(clean):
            starts.append(name)
        elif clean in key:
            contains.append(name)
    return (starts + contains)[:limit]


def body_names(system: str) -> List[str]:
    """The bodies and rings WFMT knows in `system`; with no system given, those of the system the survey is on."""
    from . import mining_body_cache, mining_hotspots, system_survey
    survey = system_survey.survey
    wanted = (system or survey.name or "").strip()
    if not wanted:
        return []
    key = wanted.casefold()
    names: List[str] = []
    if survey.name.casefold() == key:
        names += [body.name for body in survey.bodies.values() if body.name]
    names += [hotspot.body for hotspot in mining_hotspots.hotspot_repository.all() if hotspot.system.casefold() == key and hotspot.body]
    try:
        names += [body.name for body in mining_body_cache.cache.bodies_for(wanted)]
    except Exception:        # a damaged cache must not stop the box suggesting what else it has
        pass
    return names


def attach_names(entry: tk.Entry, var: Optional[tk.StringVar], names: Callable[[], Sequence[str]],
                 on_pick: Optional[Callable[[], None]] = None) -> system_autocomplete.Autocomplete:
    """Suggestions from any list of names, asked for each time the list opens, so it can follow data that changed since the box was built."""
    return system_autocomplete.attach(entry, var, on_pick, provider=lambda text: match(list(names()), text))


def attach_bodies(entry: tk.Entry, var: Optional[tk.StringVar], system: Callable[[], str],
                  on_pick: Optional[Callable[[], None]] = None) -> system_autocomplete.Autocomplete:
    """Body and ring names for the system `system()` gives (asked each time, so it follows the system box beside it)."""
    return attach_names(entry, var, lambda: body_names(system()), on_pick)


def attach_ships(entry: tk.Entry, var: Optional[tk.StringVar], on_pick: Optional[Callable[[], None]] = None) -> system_autocomplete.Autocomplete:
    return attach_names(entry, var, trade_ship.known_ships, on_pick)


def attach_commodity_list(entry: tk.Entry, var: tk.StringVar, preferred: Callable[[], Sequence[str]] = lambda: (),
                          on_pick: Optional[Callable[[], None]] = None) -> system_autocomplete.Autocomplete:
    """For a box that takes several commodities separated by commas: the suggestions are for the one being typed, and taking one replaces only that one."""
    from .mining_targets import LastItemVar
    return commodity_autocomplete.attach(entry, LastItemVar(var), preferred, on_pick)  # type: ignore[arg-type]
