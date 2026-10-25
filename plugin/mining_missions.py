"""What your active mining missions still need, for the Space Mining page: one line per commodity with the tons still to mine, how many you already hold, and how many missions ask for it.
Pure logic over `all_missions.MissionSummary` objects and the hold (`current_cargo.held()`, by commodity key); no Tk, no network.

A mining mission is one whose name says mining (`mission_types.is_mining_mission`, which sets `MissionSummary.commodity`). `needed_commodity_count` is what is still to find: the mission's
count, less what a cargo depot says is already delivered. The hold is spread over the missions the way `mission_progress.compute` does it for the Missions window: the soonest to expire first.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping

from . import mission_progress

MAX_LINES = 3


@dataclass(frozen=True)
class MiningNeed:
    commodity: str
    tons: int         # still to find, over the missions
    held: int           # of that, already in the hold
    missions: int


def needs(missions: Iterable[Any], held: Mapping[str, int]) -> List[MiningNeed]:
    """The mining missions' needs by commodity, the biggest first. `held` is the hold by commodity key (any spelling: it is re-keyed here)."""
    pool = {mission_progress.commodity_key(k): int(v) for k, v in (held or {}).items() if isinstance(v, (int, float))}
    totals: Dict[str, List[int]] = {}
    names: Dict[str, str] = {}
    for mission in missions:
        name, key, count = getattr(mission, "commodity", ""), getattr(mission, "commodity_key", ""), int(getattr(mission, "needed_commodity_count", 0) or 0)
        if not name or not key or count <= 0:
            continue
        entry = totals.setdefault(key, [0, 0])
        entry[0] += count
        entry[1] += 1
        names.setdefault(key, name)
    found = [MiningNeed(names[key], tons, max(0, min(tons, pool.get(key, 0))), count) for key, (tons, count) in totals.items()]
    return sorted(found, key=lambda need: (-need.tons, need.commodity.casefold()))


def lines(found: List[MiningNeed]) -> List[str]:
    """The page's lines: "Mission needs: Painite 45 of 120 t held (2 missions)". Only the first few, then a count of the rest."""
    out = [f"Mission needs: {need.commodity} {need.held} of {need.tons} t held" + (f" ({need.missions} missions)" if need.missions > 1 else "")
           for need in found[:MAX_LINES]]
    if len(found) > MAX_LINES:
        out.append(f"+{len(found) - MAX_LINES} more commodities")
    return out
