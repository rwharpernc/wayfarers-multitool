"""
On-demand lookup against Spansh's (https://spansh.co.uk) body-search API to
find the nearest system whose *primary* (main) star is a neutron star or a
white dwarf - the "Neutron Star" and "White Dwarf" buttons in Exploration mode's panel, next
to Discovery Alerts. Useful for neutron-boost plotting and white-dwarf
visits: a star that is only a secondary companion isn't what you want to jump
to, so the search is restricted to `is_main_star`.

Spansh doesn't publish this endpoint's request shape. The shape below was
worked out from live `POST /api/bodies/search` calls and checked against
real responses (same approach as mining_spansh_client.py): `subtype`
("Neutron Star", or any of the white dwarf subtypes) plus `is_main_star`
true, sorted by distance ascending, with the search origin given as `reference_coords` (the journal's StarPos) -
confirmed to return the same distances as a `reference_system` of "Sol" for
(0, 0, 0). Coordinates rather than a system name so this works from a
system Spansh has never seen. If Spansh changes this endpoint, this is the
one place to fix.

The N.S. button can also answer from the local star index (`star_index.py`) when the user has installed it and left it switched on: no request is made then. `find_nearest_neutron` tries
the index first and falls back to the Spansh search when there is no usable index, it holds no neutron star near enough, or anything goes wrong reading it. `NearestStar.source` says
which answered. The index lists only systems whose *main* star is a neutron star, as the Spansh search above does.

Same raise-on-failure calling convention as mining_spansh_client.py and
gec_poi_edastro.py: a synchronous, blocking network call that callers must
run off the Tk main thread, catching exceptions themselves.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import dataclass, replace
from typing import Optional, Sequence, Tuple

from . import http_identity, spansh_courtesy, star_index

logger = logging.getLogger(__name__)

BODIES_SEARCH_URL = "https://spansh.co.uk/api/bodies/search"
REQUEST_TIMEOUT_S = 20
_USER_AGENT = http_identity.user_agent("neutron-finder")

NEUTRON_SUBTYPES = ("Neutron Star",)
WHITE_DWARF_SUBTYPES = tuple(
    f"White Dwarf ({kind}) Star"
    for kind in ("DA", "DAB", "DAO", "DAZ", "DAV", "DB", "DBZ", "DBV", "DO", "DOV", "DQ", "DC", "DCV", "DX")
)
"""Spansh names each white dwarf class separately ("White Dwarf (DA) Star", ...);
these are the values confirmed against live calls (some, like DAO, currently
match nothing but are harmless to include)."""

_RESULT_COUNT = 2
"""Asked for two so the commander's own system can be skipped when they are
already sitting in a neutron system - the useful answer is then the next one."""

MAX_NAME_CHARS = 40
"""Hard cap on a system name shown in the main panel (see
`display_name`) - names come from an external API, and an EDMC main window
sizes itself to its widest row across every loaded plugin."""


@dataclass(frozen=True)
class NearestStar:
    system: str
    distance_ly: float
    region: str
    source: str = "Spansh"          # which answered: "Spansh" (the search) or "local index"


LOCAL_SOURCE = "local index"


def display_name(name: str) -> str:
    """`name` truncated to MAX_NAME_CHARS for the main panel."""
    if len(name) <= MAX_NAME_CHARS:
        return name
    return name[:MAX_NAME_CHARS - 1] + "…"


def find_nearest_neutron(x: float, y: float, z: float, current_system: Optional[str] = None) -> NearestStar:
    """The nearest system whose primary star is a neutron star - see
    `find_nearest_primary`."""
    local, note = _try_local_index(x, y, z, current_system)
    if local is not None:
        return local
    found = find_nearest_primary(NEUTRON_SUBTYPES, x, y, z, current_system)
    return replace(found, source=f"{found.source}, {note}") if note else found


def find_nearest_neutron_local(x: float, y: float, z: float, current_system: Optional[str] = None) -> Optional[NearestStar]:
    """The nearest neutron-star system from the local star index, skipping `current_system`; None when the index is switched off, not installed, damaged, from another format, or has nothing
    within its search range, so the caller asks Spansh instead."""
    return _try_local_index(x, y, z, current_system)[0]


def _try_local_index(x: float, y: float, z: float, current_system: Optional[str]) -> Tuple[Optional[NearestStar], str]:
    """(the answer or None, a few words on why the index was not used when it is installed but cannot be read)."""
    if not star_index.use_local_index():
        return None, ""
    try:
        hits = star_index.nearest_stars(x, y, z, _RESULT_COUNT)
    except star_index.IndexUnusable as err:
        if err.kind == "missing":
            return None, ""
        logger.warning("The local star index cannot be used (%s); asking Spansh instead", err)
        return None, "local index not usable" if err.kind == "damaged" else "local index is from another version"
    except (OSError, ValueError, KeyError, IndexError, OverflowError):
        logger.warning("Reading the local star index failed; asking Spansh instead", exc_info=True)
        return None, "local index not usable"
    skip = current_system.casefold() if current_system else None
    for hit in hits:
        if skip is not None and hit.name.casefold() == skip:
            continue
        return NearestStar(hit.name, hit.distance_ly, "", LOCAL_SOURCE), ""
    return None, ""


def find_nearest_white_dwarf(x: float, y: float, z: float, current_system: Optional[str] = None) -> NearestStar:
    """The nearest system whose primary star is a white dwarf (any class) - see
    `find_nearest_primary`."""
    return find_nearest_primary(WHITE_DWARF_SUBTYPES, x, y, z, current_system)


def find_nearest_primary(subtypes: Sequence[str], x: float, y: float, z: float,
                         current_system: Optional[str] = None) -> NearestStar:
    """The nearest system whose primary star has one of `subtypes`, measured
    from galactic (x, y, z) in light years, skipping `current_system` (if
    given). Raises on any network/parse failure or when nothing is found."""
    request_body = {
        "filters": {
            "subtype": {"value": list(subtypes)},
            "is_main_star": {"value": True},
        },
        "sort": [{"distance": {"direction": "asc"}}],
        "size": _RESULT_COUNT,
        "page": 0,
        "reference_coords": {"x": x, "y": y, "z": z},
    }
    request = urllib.request.Request(
        BODIES_SEARCH_URL,
        data=json.dumps(request_body).encode("utf8"),
        headers={"User-Agent": _USER_AGENT, "Content-Type": "application/json"},
        method="POST",
    )
    data = json.loads(spansh_courtesy.call(request, REQUEST_TIMEOUT_S).decode("utf-8"))

    return pick_nearest(data, current_system)


def pick_nearest(data: object, current_system: Optional[str]) -> NearestStar:
    """Picks the answer out of a bodies/search response; split from the network
    call so it can be tested against a canned response."""
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        raise ValueError(f"Unexpected Spansh bodies/search response shape: {data!r}")

    skip = current_system.casefold() if current_system else None
    for body in results:
        if not isinstance(body, dict):
            continue
        system = body.get("system_name")
        distance = body.get("distance")
        if not isinstance(system, str) or not isinstance(distance, (int, float)):
            continue
        if skip is not None and system.casefold() == skip:
            continue
        region = body.get("system_region")
        return NearestStar(system, float(distance), region if isinstance(region, str) else "")
    raise ValueError("Spansh returned no matching primary-star systems")
