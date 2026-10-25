"""Rare-goods locator for Powerplay mode: nearest rare commodities to the
current system.

Rare-good origins never move, so the dataset (`rare_goods.json`: 141 rare
goods with origin system, station, pad size, cost, legality restrictions,
Powerplay eligibility, the station's distance from the arrival star, and baked-in EDSM coordinates / Inara id / Spansh
id64 - see docs/ATTRIBUTIONS.md) ships as a static file rather than being
queried live. Only the origin system's *controlling Power* is looked up
live (`powerplay_control_lookup.py`), because that changes weekly.

Deliberately has no EDMC imports so it can be unit-tested outside EDMC.
"""

from __future__ import annotations

import json
import logging
import math
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

_DATA_PATH = os.path.join(os.path.dirname(__file__), "rare_goods.json")

_cache: Optional[List[Dict[str, Any]]] = None


def _load() -> List[Dict[str, Any]]:
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as fh:
            _cache = json.load(fh)
    except (OSError, ValueError):
        logger.warning("Could not read %s", _DATA_PATH, exc_info=True)
        _cache = []
    return _cache


def dataset_size() -> int:
    return len(_load())


def _distance_ly(a: Sequence[float], b: Dict[str, float]) -> float:
    return math.sqrt((a[0] - b["x"]) ** 2 + (a[1] - b["y"]) ** 2 + (a[2] - b["z"]) ** 2)


def nearest(current_coords: Tuple[float, float, float], limit: int = 10) -> List[Dict[str, Any]]:
    """The `limit` nearest rare goods to `current_coords` (a StarPos-shaped
    (x, y, z) tuple), each entry annotated with `distance_ly`, nearest first."""
    annotated = [
        {**entry, "distance_ly": _distance_ly(current_coords, entry["coords"])} for entry in _load()
    ]
    annotated.sort(key=lambda e: e["distance_ly"])
    return annotated[:max(0, limit)]


def distance_text(distance_ly: float) -> str:
    """A distance for the window's Distance column: one decimal and a thousands separator, e.g. "1,234.5 ly"."""
    return f"{distance_ly:,.1f} ly"


def arrival_text(arrival_ls: Optional[float]) -> str:
    """The arrival-star-to-station distance for the window's Arrival column: whole light seconds with a thousands separator, e.g. "6,395,387 ls"; "—" when not known."""
    return f"{arrival_ls:,.0f} ls" if isinstance(arrival_ls, (int, float)) and not isinstance(arrival_ls, bool) else "—"


LEGAL = "Legal"
RESTRICTED = "Restricted"
ILLEGAL_HERE = "Illegal here"
LEGAL_HERE = "Legal here"


def _norm(text: Any) -> str:
    """A government or allegiance compared without case or spaces, so the journal's "$government_PrisonColony;" (once cleaned) and the table's "Prison Colony" match."""
    return "".join(str(text or "").casefold().split())


def clean_government(raw: Any, localised: Any = None) -> Optional[str]:
    """The journal's `SystemGovernment` ("$government_Democracy;") or its `_Localised` text as a plain government name; None for none or unknown."""
    text = str(localised or "").strip()
    if not text:
        text = str(raw or "").strip()
        if text.startswith("$government_") and text.endswith(";"):
            text = text[len("$government_"):-1]
    return None if not text or _norm(text) == "none" else text


def is_restricted(entry: Dict[str, Any]) -> bool:
    """Whether the table lists any place this rare is illegal."""
    return bool(entry.get("illegalInSuperpowers") or entry.get("illegalInGovs") or entry.get("illegalInSuperpowerGovs"))


def illegal_here(entry: Dict[str, Any], allegiance: Optional[str], government: Optional[str]) -> Optional[bool]:
    """Whether the rare is illegal in a system with this allegiance and government: True or False, or None when the system's details are too thin to say. Any one listed
    restriction (a superpower, a government type, or a superpower with a government type) makes it illegal."""
    a, g = _norm(allegiance), _norm(government)
    powers = [_norm(x) for x in entry.get("illegalInSuperpowers") or []]
    govs = [_norm(x) for x in entry.get("illegalInGovs") or []]
    pairs = [(_norm(x.get("superpower")), _norm(x.get("government"))) for x in entry.get("illegalInSuperpowerGovs") or []]
    if (a and a in powers) or (g and g in govs) or (a and g and (a, g) in pairs):
        return True
    if (powers and not a) or (govs and not g) or (pairs and not (a and g)):
        return None
    return False


def legality_text(entry: Dict[str, Any], allegiance: Optional[str] = None, government: Optional[str] = None) -> str:
    """The Legality column: "Legal" when the table lists no restriction, else "Illegal here" or "Legal here" for the system you are in, or "Restricted" when that is not known."""
    if not is_restricted(entry):
        return LEGAL
    here = illegal_here(entry, allegiance, government)
    return RESTRICTED if here is None else (ILLEGAL_HERE if here else LEGAL_HERE)


def restriction_details(entry: Dict[str, Any]) -> str:
    """Where the rare is illegal, in words, for the detail line beside the controls when a row is selected."""
    if not is_restricted(entry):
        return "no restrictions listed"
    parts: List[str] = []
    powers = list(entry.get("illegalInSuperpowers") or [])
    if powers:
        parts.append("all " + " and ".join(powers) + " space")
    govs = list(entry.get("illegalInGovs") or [])
    if govs:
        parts.append(", ".join(govs) + " systems of any allegiance")
    by_power = {}
    for pair in entry.get("illegalInSuperpowerGovs") or []:
        by_power.setdefault(str(pair.get("superpower")), []).append(str(pair.get("government")))
    for power, kinds in by_power.items():
        parts.append(power + " " + ", ".join(kinds))
    return "illegal in " + "; ".join(parts)


def same_power(a: Any, b: Any) -> bool:
    """Whether two Power names are the same one (ignoring case and spaces); never true for an empty name."""
    return bool(_norm(a)) and _norm(a) == _norm(b)


def candidates(current_coords: Tuple[float, float, float], large_only: bool = False) -> List[Dict[str, Any]]:
    """Every rare good, nearest first, each annotated with `distance_ly`; with `large_only`, only those sold at a large-pad station."""
    found = nearest(current_coords, dataset_size())
    return [entry for entry in found if entry.get("pad") == "L"] if large_only else found


def inara_commodity_url(inara_id: int) -> str:
    """Inara.cz page for the commodity with this numeric id. Inara's own
    name-search for commodities doesn't resolve to a specific item, so the
    ids baked into rare_goods.json (looked up once at authoring time) are
    used to link directly."""
    return f"https://inara.cz/elite/commodity/{inara_id}/"
