"""Where to get what your Collect, Mining and Delivery missions still need: the list of needs, and the four source picks (source_picks.py) for each.

Pure logic apart from the Spansh search, which is passed in. The window that shows it is `mission_sources_window.py`.

A need is one commodity summed over every active mission that still has to source it (`MissionSummary.needed_commodity` and `needed_commodity_count`: units
still needed, less what a cargo depot already holds). Its **turn-in system** is where most of those missions are handed in. Looking up is one Spansh round of
about four searches per commodity, so it only happens when the commander presses the button, one commodity after another with a pause between."""
from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional

from . import source_picks
from .trade_prices import BUY

TURN_IN, HERE = "turn-in", "here"      # which system the picks are measured from
MAX_NEEDS = 12                         # a full board of 20 missions rarely has more kinds of cargo; a hard cap on the searches one press can start


@dataclass(frozen=True)
class Need:
    commodity: str
    tons: int                 # still to find, summed over the missions
    missions: int
    turn_in: str                # the system most of those missions are handed in at ("" if none says)
    pickup: Optional[str] = None    # None: buy it on a market. Otherwise the station the cargo is picked up at ("" when not known): Delivery missions
    pickup_pad: str = ""            # for a pickup: that station's largest landing pad ("" when not known)


@dataclass(frozen=True)
class Options:
    radius_ly: float
    ship_pad: Optional[str]
    include_carriers: bool
    include_ground: bool


def needs_from(missions: Iterable[Any]) -> List[Need]:
    """The commodities still to source from a market, biggest need first, at most `MAX_NEEDS`, then the Delivery cargo still to be picked up at a station
    (one entry per commodity and station, biggest first). Works on `all_missions.MissionSummary` objects."""
    totals: Dict[str, List[int]] = {}
    places: Dict[str, Counter] = {}
    pickups: Dict[tuple, List[int]] = {}
    pickup_places: Dict[tuple, Counter] = {}
    pickup_pads: Dict[tuple, str] = {}
    missions = list(missions)
    for mission in missions:
        name = getattr(mission, "pickup_commodity", "")
        count = int(getattr(mission, "pickup_count", 0) or 0)
        if name and count > 0:
            key = (name, getattr(mission, "pickup_station", "") or "")
            entry = pickups.setdefault(key, [0, 0])
            if not pickup_pads.get(key):
                pickup_pads[key] = getattr(mission, "pickup_pad", "") or ""
            entry[0] += count
            entry[1] += 1
            place = getattr(mission, "destination_system", "") or ""
            if place:
                pickup_places.setdefault(key, Counter())[place] += 1
    for mission in missions:
        name = getattr(mission, "needed_commodity", "")
        count = int(getattr(mission, "needed_commodity_count", 0) or 0)
        if not name or count <= 0:
            continue
        entry = totals.setdefault(name, [0, 0])
        entry[0] += count
        entry[1] += 1
        place = getattr(mission, "destination_system", "") or ""
        if place:
            places.setdefault(name, Counter())[place] += 1
    ranked = sorted(totals.items(), key=lambda item: (-item[1][0], item[0].casefold()))
    found = [Need(name, tons, count, places[name].most_common(1)[0][0] if name in places else "") for name, (tons, count) in ranked[:MAX_NEEDS]]
    ranked_pickups = sorted(pickups.items(), key=lambda item: (-item[1][0], item[0][0].casefold(), item[0][1].casefold()))
    return found + [Need(name, tons, count, pickup_places[key].most_common(1)[0][0] if key in pickup_places else "", station, pickup_pads.get(key, ""))
                    for key, (tons, count) in ranked_pickups for name, station in [key]]


def reference_for(need: Need, mode: str, here: str) -> str:
    """The system to measure from: where you are, or the need's turn-in system (falling back to where you are if no mission names one)."""
    if mode == TURN_IN and need.turn_in:
        return need.turn_in
    return here


def lookup(needs: List[Need], mode: str, here: str, options: Options, *, search: Optional[Callable[..., Any]] = None,
           pause: Callable[[float], None] = time.sleep, cancelled: Callable[[], bool] = lambda: False,
           on_done: Callable[[Need, source_picks.Picks], None] = lambda need, picks: None) -> Dict[str, source_picks.Picks]:
    """The picks for each need (by commodity name), one after another with a pause between. `on_done` is told as each finishes, so a window can show the
    first while the rest are still being found. A failed search is raised; the commodities done before it have already been passed to `on_done`."""
    results: Dict[str, source_picks.Picks] = {}
    extra = {} if search is None else {"search": search}
    started = False
    for need in needs:
        if cancelled():
            break
        if need.pickup is not None:
            continue                        # picked up at a station, not bought: nothing to look up
        reference = reference_for(need, mode, here)
        if not reference:
            continue
        if started:
            pause(source_picks.PAUSE_S)
        started = True
        picks = source_picks.find(reference, need.commodity, BUY, need.tons, radius_ly=options.radius_ly, ship_pad=options.ship_pad,
                                  include_carriers=options.include_carriers, include_ground=options.include_ground,
                                  pause=pause, cancelled=cancelled, **extra)
        results[need.commodity] = picks
        on_done(need, picks)
    return results
