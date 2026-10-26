"""Best single systems for a shopping list: the systems where most (ideally all) of what a site still needs can be bought, so a
commander who parks a fleet carrier in one system only hops between its stations.

Find all (colonization_sources.py) answers per commodity with the nearest few stations, and a station is a stop of its own, so a
system whose stations together stock the whole list never shows up as one place. This module closes that gap in two steps:

1. `candidate_systems` groups the Find all answers by system and keeps the few that look best (the most commodities, then the most
   tons), plus the system searched around, which is always worth checking.
2. `find_best_systems` asks Spansh for every station in each candidate (`search_system_stations`: one request per system, each
   station with its whole market), adds up what the system's stations stock and picks the fewest stations that supply the most
   (the same greedy choice as the suggested route, `colonization_sources.plan_route`, limited to that system).

A system that covers every commodity comes first, then by the share of the tons covered, the nearer, and the cheaper basket.
Nothing here touches Tk, and the network call is passed in, so the grouping, ranking and shortfalls are tested without a
connection. Fleet carriers are left out of the verification (they move and their markets go stale); only stations whose market
was updated in the last `sources.MAX_AGE_DAYS` days count, which `search_system_stations` already enforces.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from . import colonization_sources as sources
from .mining_spansh_client import SYSTEM_STATIONS_PAGE, StationPrice, _normalize_commodity_name, search_system_stations

CANDIDATES = 6                 # systems checked with Spansh after a Find all (one request each)
MIN_COMMODITIES = 2            # a system found for fewer commodities than this is not worth a request (when the list is longer than one)
SYSTEM_PAUSE = 0.4             # seconds between two requests to Spansh
MAX_STATIONS_PER_SYSTEM = 12   # a system's plan never has more stops than this

FetchFn = Callable[..., Tuple[List[Dict[str, Any]], int]]   # search_system_stations(system, market_days_old=...) -> (stations, count)


@dataclass(frozen=True)
class SystemStop:
    """One station of a system's plan: what to buy there."""
    station: str
    kind: str
    is_planetary: bool
    pad: str
    arrival_ls: float
    buys: Tuple[sources.Purchase, ...]

    @property
    def tons(self) -> int:
        return sum(b.tons for b in self.buys)


@dataclass(frozen=True)
class SystemPlan:
    system: str
    distance_ly: float                 # from the system searched around
    stops: Tuple[SystemStop, ...]
    needed: int                        # tons the list still needs in all
    covered: int                       # of that, how many tons this system's stations can supply
    uncovered: Tuple[Tuple[str, int], ...]   # (commodity, tons short) the system cannot supply
    cost: int                          # cr for everything the plan buys
    stations_with_market: int          # stations of the system that were considered (a market updated recently)
    more_stations: bool = False        # the system has more stations than Spansh sent in one answer

    @property
    def complete(self) -> bool:
        return not self.uncovered and self.needed > 0

    @property
    def share(self) -> float:
        return self.covered / self.needed if self.needed else 0.0

    def lines(self) -> List[str]:
        """The plan as plain lines: a summary, then one line per station in the order to visit, then what is short."""
        head = f"{self.system}: {self.covered:,} of {self.needed:,} t covered ({self.share:.0%})"
        if self.cost:
            head += f", about {self.cost:,} cr"
        if self.distance_ly:
            head += f", {self.distance_ly:,.1f} ly away"
        out = [head]
        for number, stop in enumerate(self.stops, 1):
            buys = ", ".join(f"{b.commodity} {b.tons:,} t" for b in stop.buys)
            out.append(f"{number}. {stop.station}: {buys}")
        if self.uncovered:
            out.append("Short: " + ", ".join(f"{label} {tons:,} t" for label, tons in self.uncovered))
        return out


@dataclass
class SystemsResult:
    plans: List[SystemPlan] = field(default_factory=list)       # best first
    failed: List[Tuple[str, str]] = field(default_factory=list)  # (system, why)
    stopped: bool = False


# --- step 1: which systems are worth checking ----------------------------------------------------------------------------


def candidate_systems(found: Sequence[Tuple[str, "sources.SearchResult"]], needs: Dict[str, int], always: Sequence[str] = (),
                      limit: int = CANDIDATES) -> List[Tuple[str, float]]:
    """(system, distance in ly) of the systems to check, best first. Systems named in `always` (the one searched around) come
    first, then the systems the Find all answers found the most of the list in, by commodities and then tons. Fleet carriers
    are ignored: their systems change as they move."""
    wanted = {label for label, tons in needs.items() if tons and tons > 0}
    per_system: Dict[str, Dict[str, int]] = {}
    nearest: Dict[str, float] = {}
    for label, result in found:
        if label not in wanted:
            continue
        for source in result.stations:
            if source.supply <= 0:
                continue
            key = source.system
            per_system.setdefault(key, {})
            per_system[key][label] = per_system[key].get(label, 0) + source.supply
            nearest[key] = min(nearest.get(key, source.distance_ly), source.distance_ly)
    minimum = MIN_COMMODITIES if len(wanted) >= MIN_COMMODITIES else 1

    def score(system: str) -> Tuple[int, int]:
        stock = per_system[system]
        return len(stock), sum(min(stock[label], needs[label]) for label in stock)

    ranked = [s for s in per_system if len(per_system[s]) >= minimum]
    ranked.sort(key=lambda s: (-score(s)[0], -score(s)[1], nearest[s], s.casefold()))
    chosen: List[Tuple[str, float]] = []
    seen = set()
    for system in [*[a for a in always if a and a.strip()], *ranked]:
        key = system.strip().casefold()
        if key in seen:
            continue
        seen.add(key)
        chosen.append((system.strip(), nearest.get(system, 0.0)))
        if len(chosen) >= limit:
            break
    return chosen


# --- step 2: what a system really has -------------------------------------------------------------------------------------


def _pad_of(station: Dict[str, Any]) -> StationPrice:
    """The station as a `StationPrice` (price and quantity unused), which is what the pad filter and `largest_pad` read."""
    def count(value: Any) -> Optional[int]:
        return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
    return StationPrice(
        station=str(station.get("name") or "?"), system=str(station.get("system_name") or "?"),
        station_type=str(station.get("type") or "?"), distance_ly=0.0,
        distance_to_arrival_ls=float(station.get("distance_to_arrival") or 0.0),
        is_planetary=bool(station.get("is_planetary", False)), price=0, quantity=0,
        small_pads=count(station.get("small_pads")), medium_pads=count(station.get("medium_pads")),
        large_pads=count(station.get("large_pads")))


def plan_system(system: str, distance_ly: float, stations: Sequence[Dict[str, Any]], needs: Dict[str, int], *, pad: str = sources.PAD_ANY,
                more_stations: bool = False) -> SystemPlan:
    """What buying `needs` (tons still to get, by label) in `system` looks like, from its stations' whole markets as Spansh
    sends them (`market`: entries with `commodity`, `buy_price` and `supply`). Stations without a pad that fits are left out."""
    wanted = {label: int(tons) for label, tons in needs.items() if tons and tons > 0}
    spansh_names = {_normalize_commodity_name(label).casefold(): label for label in wanted}
    found: Dict[str, List[sources.Source]] = {label: [] for label in wanted}
    details: Dict[str, StationPrice] = {}
    usable = 0
    for station in stations:
        item = _pad_of(station)
        if not sources._fits(item, pad):   # noqa: SLF001 - the same pad rule as the searches
            continue
        usable += 1
        details[item.station] = item
        for entry in station.get("market") or []:
            label = spansh_names.get(str(entry.get("commodity", "")).casefold())
            price, supply = entry.get("buy_price", 0), entry.get("supply", 0)
            if label is None or not isinstance(price, (int, float)) or not isinstance(supply, (int, float)) or price <= 0 or supply <= 0:
                continue
            found[label].append(sources.to_source(StationPrice(
                station=item.station, system=system, station_type=item.station_type, distance_ly=distance_ly,
                distance_to_arrival_ls=item.distance_to_arrival_ls, is_planetary=item.is_planetary, price=int(price),
                quantity=int(supply), small_pads=item.small_pads, medium_pads=item.medium_pads, large_pads=item.large_pads)))
    route = sources.plan_route([(label, sources.SearchResult(stations=offers, carriers=[])) for label, offers in found.items()],
                               wanted, max_stops=MAX_STATIONS_PER_SYSTEM)
    stops = []
    for stop in route.stops:
        item = details[stop.station]
        stops.append(SystemStop(stop.station, stop.kind, item.is_planetary, sources.largest_pad(item), item.distance_to_arrival_ls, stop.buys))
    stops.sort(key=lambda s: (s.arrival_ls, s.station.casefold()))   # the order to visit: nearest the arrival star first
    cost = sum(b.tons * b.price for s in stops for b in s.buys)
    return SystemPlan(system=system, distance_ly=distance_ly, stops=tuple(stops), needed=route.needed, covered=route.covered,
                      uncovered=route.uncovered, cost=cost, stations_with_market=usable, more_stations=more_stations)


def rank(plans: Sequence[SystemPlan]) -> List[SystemPlan]:
    """Systems that cover everything first, then the larger share of the tons, the nearer, the cheaper basket."""
    return sorted(plans, key=lambda p: (not p.complete, -p.share, p.distance_ly, p.cost, p.system.casefold()))


def find_best_systems(found: Sequence[Tuple[str, "sources.SearchResult"]], needs: Dict[str, int], reference_system: str, *,
                      pad: str = sources.PAD_ANY, fetch: FetchFn = search_system_stations, limit: int = CANDIDATES,
                      sleep: Callable[[float], None] = time.sleep, pause: float = SYSTEM_PAUSE,
                      progress: Optional[Callable[[int, int, str], None]] = None,
                      cancelled: Optional[Callable[[], bool]] = None) -> SystemsResult:
    """Check the candidate systems with Spansh and rank them. One request per system; a system whose request fails is recorded and
    the others carry on, and `cancelled()` is checked between systems. A list of a single commodity has no use for this (a plain
    search answers it), so nothing is asked then."""
    out = SystemsResult()
    wanted = {label: tons for label, tons in needs.items() if tons and tons > 0}
    if len(wanted) < 2:
        return out
    candidates = candidate_systems(found, wanted, always=[reference_system], limit=limit)
    for index, (system, distance) in enumerate(candidates):
        if cancelled is not None and cancelled():
            out.stopped = True
            break
        if progress is not None:
            progress(index, len(candidates), system)
        if index and pause > 0:
            sleep(pause)
        try:
            stations, count = fetch(system, market_days_old=sources.MAX_AGE_DAYS)
        except Exception as exc:   # a network or parse failure for this system only
            out.failed.append((system, str(exc) or exc.__class__.__name__))
            continue
        out.plans.append(plan_system(system, distance, stations, wanted, pad=pad, more_stations=count > SYSTEM_STATIONS_PAGE))
    out.plans = rank([p for p in out.plans if p.covered > 0])
    return out
