"""
The commander's projects on Raven Colonial, as the My Projects window lists them: the rows, which of them count toward the totals,
how far along each is, and the shopping list of one. Pure logic with no network and no window (see tests/test_rcc_projects.py); the
reads and writes are in rcc_client.py and the window is colonization_projects_window.py.

"Counted" is the inverse of Raven Colonial's own *hidden* list: a project is counted unless its build id is hidden, so ticking or
unticking one here and saving it changes what the commander's other tools (SrvSurvey's overlay, ravencolonial.com) show too.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import AbstractSet, Iterable, List, Optional, Set, Tuple

from . import build_costs, rcc_client, rcc_create


@dataclass(frozen=True)
class Row:
    view: rcc_client.RccProjectView
    counted: bool       # not on the hidden list
    primary: bool       # the commander's primary project
    tracked: bool       # WFMT also tracks this site from the journal


def rows(views: Iterable[rcc_client.RccProjectView], hidden: AbstractSet[str], primary: str, tracked_markets: AbstractSet[int]) -> List[Row]:
    """The projects by system and then name, each marked as counted, primary and tracked here."""
    built = [Row(v, v.build_id not in hidden, bool(primary) and v.build_id == primary,
                 v.market_id is not None and v.market_id in tracked_markets) for v in views]
    return sorted(built, key=lambda r: (r.view.system.casefold(), r.view.name.casefold(), r.view.build_id))


def unlisted(views: Iterable[rcc_client.RccProjectView], sites: Iterable[Tuple[int, str, str]]) -> List[Tuple[int, str, str]]:
    """The tracked active sites (market id, name, system) that none of the commander's Raven projects is for: a project deleted on Raven leaves its
    site active in WFMT. A project counts as being for a site by its market id, or, when Raven holds none, by the same name and system."""
    views = list(views)
    markets = {v.market_id for v in views if v.market_id is not None}
    named = {(v.name.casefold(), v.system.casefold()) for v in views if v.market_id is None}
    return [s for s in sites if s[0] not in markets and (s[1].casefold(), s[2].casefold()) not in named]


def progress(view: rcc_client.RccProjectView) -> float:
    """How much of the build is delivered, 0 to 1 (1 for one marked complete)."""
    if view.complete:
        return 1.0
    if view.max_need <= 0:
        return 0.0
    return min(1.0, max(0.0, 1.0 - view.sum_need / view.max_need))


def building_label(view: rcc_client.RccProjectView) -> str:
    """The game's name and the build type Raven knows it by, e.g. `Industrial Outpost (vulcan)`; a carrier being loaded says so."""
    if view.build_type.casefold() == rcc_client.FC_LOADING:
        return "Carrier loading"
    choice = rcc_create.choice_for_layout(view.build_type)
    if choice is None:
        return rcc_client.build_type_label(view.build_type) or "Unknown"
    return f"{choice.name} ({view.build_type.casefold()})"


def totals(shown: Iterable[Row], capacity: int) -> Tuple[int, int, int]:
    """(projects counted, tons still needed in them, trips in a ship holding `capacity` t; 0 trips when the capacity is not known)."""
    counted = [r for r in shown if r.counted and not r.view.complete]
    tons = sum(r.view.sum_need for r in counted)
    trips = math.ceil(tons / capacity) if capacity > 0 and tons > 0 else 0
    return len(counted), tons, trips


def toggled(hidden: AbstractSet[str], build_id: str) -> Set[str]:
    """The hidden list with this project's counted state flipped."""
    result = set(hidden)
    if build_id in result:
        result.discard(build_id)
    else:
        result.add(build_id)
    return result


def shopping_list(view: rcc_client.RccProjectView) -> List[Tuple[str, int]]:
    """(commodity name, tons still needed) for the project, the most tons first."""
    ranked = sorted(view.commodities.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(build_costs.commodity_label(key), tons) for key, tons in ranked if tons > 0]


def shopping_text(view: rcc_client.RccProjectView) -> str:
    """The shopping list as lines to copy, like the Colonization Sites window's own."""
    where = f" ({view.system})" if view.system else ""
    lines = [f"{view.name or 'Project'}{where} - still to get:"]
    lines += [f"{tons:,} t  {label}" for label, tons in shopping_list(view)]
    if len(lines) == 1:
        lines.append("(nothing is needed)")
    return "\n".join(lines)


def find(shown: Iterable[Row], build_id: Optional[str]) -> Optional[Row]:
    return next((r for r in shown if r.view.build_id == build_id), None)
