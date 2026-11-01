"""Where to buy a colonization commodity: the closest stations (and, if asked, fleet carriers) that have it in stock,
found with Spansh's station search (`mining_spansh_client.search_best_price_stations`, shared with the mining Price
Finder and Trade). Nothing here touches Tk, and the network call is passed in, so the shaping, filtering and ordering
are tested without a connection.

The landing-pad choice is deliberate: a commander may swap to a smaller cargo ship when a commodity isn't sold at a
large-pad station, so the default is ANY size. "Medium or larger" and "Large only" ask Spansh for stations with at
least one pad of that size. Fleet carriers are a separate, opt-in search (their stock and prices are volatile and they
can move), and are listed after the stations."""

from __future__ import annotations

import itertools
import json
import math
import time
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from . import trade_prices
from .mining_spansh_client import StationPrice, search_best_price_stations, search_stations_selling_all

PAD_ANY = "any"
PAD_MEDIUM = "medium"
PAD_LARGE = "large"
PAD_LARGE_FIRST = "large_then_medium"   # Large pads first; Medium or larger only when no Large-pad station has the commodity
PAD_CHOICES = ((PAD_LARGE_FIRST, "Large, then Medium"), (PAD_LARGE, "Large only"), (PAD_MEDIUM, "Medium or larger"), (PAD_ANY, "Any size"))
MEDIUM_NOTE = "No Large-pad station in range had it, so these have a Medium pad or larger."

SORT_DISTANCE = "distance"
SORT_PRICE = "price"

DEFAULT_RADIUS_LY = 50
ARRIVAL_CHOICES = (500, 1000, 2500, 5000, 10000, 25000)   # light seconds from the arrival star; "no limit" is None
RADIUS_CHOICES = (25, 50, 100, 200, 500)   # light years; "no limit" is None
MAX_AGE_DAYS = 7          # market data older than this is ignored: it is probably out of date
STATION_RESULTS = 25
CARRIER_RESULTS = 10

WHOLE_LIST_STATIONS = 5     # stations shown per commodity when the whole list is searched at once
WHOLE_LIST_CARRIERS = 2     # fleet carriers shown per commodity then (only when carriers were asked for)
ONE_STOP_RESULTS = 5        # stations asked for that sell the whole list in one place
WHOLE_LIST_PAUSE = 0.4      # seconds between two requests to Spansh, so a long list is not sent as a burst

CACHE_SECONDS = 120   # the same search asked again within this long is answered from memory, not Spansh

SearchFn = Callable[..., List[StationPrice]]
OneStopFn = Callable[..., List[Tuple[StationPrice, Dict[str, Tuple[int, int]]]]]
_cache: Dict[tuple, Tuple[float, "SearchResult"]] = {}


@dataclass(frozen=True)
class Source:
    station: str
    system: str
    kind: str            # Spansh's station type, e.g. "Coriolis Starport"
    is_carrier: bool
    is_planetary: bool
    pad: str             # the largest pad the station has: "Large" / "Medium" / "Small" / "?" when unknown
    distance_ly: float
    arrival_ls: float
    price: int           # cr per ton
    supply: int          # tons in stock
    has_shipyard: bool = False
    position: Optional[Tuple[float, float, float]] = None   # the system's galactic (x, y, z), when Spansh gave it (for the legs of a route)


@dataclass(frozen=True)
class SearchResult:
    stations: List[Source]
    carriers: List[Source]     # empty unless carriers were asked for
    local: bool = False        # answered from the commander's own system, so nothing from outside is added to it
    note: str = ""             # what the commander should know about how the answer was reached (the Medium-pad fall-back)


def largest_pad(item: StationPrice) -> str:
    """The biggest landing pad the station has, from Spansh's pad counts."""
    if item.large_pads:
        return "Large"
    if item.medium_pads:
        return "Medium"
    if item.small_pads:
        return "Small"
    return "?"


def _fits(item: StationPrice, min_pad: str) -> bool:
    """Whether a station has a pad of the wanted size. A station Spansh gave no pad figures for is kept: leaving a
    possible source out is worse than showing one the commander has to check."""
    if min_pad == PAD_ANY or (item.small_pads is None and item.medium_pads is None and item.large_pads is None):
        return True
    if min_pad == PAD_LARGE:
        return bool(item.large_pads)
    return bool(item.large_pads or item.medium_pads)


def to_source(item: StationPrice) -> Source:
    carrier = trade_prices.is_carrier(item.station_type)
    return Source(
        station=item.station, system=item.system, kind=item.station_type, is_carrier=carrier,
        is_planetary=item.is_planetary, pad=largest_pad(item), distance_ly=item.distance_ly, arrival_ls=item.distance_to_arrival_ls,
        price=item.price, supply=item.quantity, has_shipyard=item.has_shipyard, position=item.position)


def order(sources: Sequence[Source], sort: str = SORT_DISTANCE) -> List[Source]:
    """Closest first (then by price), or cheapest first (then by distance)."""
    if sort == SORT_PRICE:
        return sorted(sources, key=lambda s: (s.price, s.distance_ly, s.arrival_ls))
    return sorted(sources, key=lambda s: (s.distance_ly, s.price, s.arrival_ls))


@dataclass(frozen=True)
class LocalFilter:
    """The exclusions the commander has set (surface ports, arrival distance, shipyard, enough stock), so that a station in their own system that
    they would not use does not count as the system having the commodity."""
    no_surface: bool = False
    max_arrival_ls: Optional[int] = None
    shipyard_only: bool = False
    enough_stock: bool = False


def _wanted(source: "Source", filters: LocalFilter, needed_t: int) -> bool:
    """Whether a source passes the exclusions; `needed_t` is the tons still to get, used when enough stock is asked for."""
    if filters.no_surface and source.is_planetary:
        return False
    if filters.shipyard_only and not source.has_shipyard:
        return False
    if filters.max_arrival_ls and source.arrival_ls and source.arrival_ls > filters.max_arrival_ls:
        return False
    return not (filters.enough_stock and needed_t and source.supply < needed_t)


def _pad_stages(pad: str) -> List[str]:
    """The pad sizes to try, in order: Large then Medium for the "Large, then Medium" choice, else just the one asked for."""
    return [PAD_LARGE, PAD_MEDIUM] if pad == PAD_LARGE_FIRST else [pad]


def _cache_key(reference_system: str, commodity: str, radius_ly: Optional[float], pad: str, include_carriers: bool,
               sort: str, search: SearchFn, orbital_only: bool = False, here: str = "", filters: Optional[LocalFilter] = None,
               needed_t: int = 0) -> tuple:
    stock = needed_t if filters is not None and filters.enough_stock else 0
    return (reference_system.strip().casefold(), commodity.casefold(), radius_ly, pad, include_carriers, sort, search, orbital_only,
            here.strip().casefold(), filters, stock)


def is_cached(reference_system: str, commodity: str, *, radius_ly: Optional[float] = DEFAULT_RADIUS_LY,
              pad: str = PAD_ANY, include_carriers: bool = False, sort: str = SORT_DISTANCE,
              search: SearchFn = search_best_price_stations, now: Callable[[], float] = time.monotonic,
              orbital_only: bool = False, here: str = "", filters: Optional[LocalFilter] = None, needed_t: int = 0) -> bool:
    """Whether `find` with these arguments would be answered from memory (so it sends no request)."""
    cached = _cache.get(_cache_key(reference_system, commodity, radius_ly, pad, include_carriers, sort, search, orbital_only, here, filters, needed_t))
    return cached is not None and now() - cached[0] < CACHE_SECONDS


def clear_cache() -> None:
    _cache.clear()


def find(reference_system: str, commodity: str, *, radius_ly: Optional[float] = DEFAULT_RADIUS_LY,
         pad: str = PAD_ANY, include_carriers: bool = False, sort: str = SORT_DISTANCE,
         search: SearchFn = search_best_price_stations, now: Callable[[], float] = time.monotonic,
         orbital_only: bool = False, here: str = "", filters: Optional[LocalFilter] = None, needed_t: int = 0) -> SearchResult:
    """Stations (and optionally fleet carriers) near `reference_system` with `commodity` in stock. With `here` (the system the commander is in),
    that system is searched first: if a station in it has the commodity in stock (and passes `filters`, the exclusions the commander has set, with
    `needed_t` the tons still to get), those are the answer and nothing outside is searched; only when none does, the search goes out around `reference_system`, ordered by `sort` (closest first by default). `search` is the
    Spansh call; it raises on a network or parse failure, which the caller reports. Stations are asked for apart from
    carriers so the volatile carrier prices cannot crowd the real stations out of the first page. `orbital_only` asks
    for orbital stations alone (no surface ports), so a commodity whose nearest sellers are all on planets still shows
    the orbital ports that have it."""
    if not reference_system.strip():
        raise ValueError("Enter a system to search around.")
    key = _cache_key(reference_system, commodity, radius_ly, pad, include_carriers, sort, search, orbital_only, here, filters, needed_t)
    cached = _cache.get(key)
    if cached is not None and now() - cached[0] < CACHE_SECONDS:
        return cached[1]
    stages = _pad_stages(pad)
    spansh_sort = SORT_DISTANCE if sort == SORT_DISTANCE else SORT_PRICE
    result = SearchResult([], [])
    for stage in stages:   # one pad size at a time: your own system first, then outside, before the next size is tried
        note = "" if stage == stages[0] else MEDIUM_NOTE
        if here.strip():
            local = _in_system(here.strip(), commodity, stage, include_carriers, orbital_only, sort, search)
            if any(filters is None or _wanted(source, filters, needed_t) for source in [*local.stations, *local.carriers]):
                result = SearchResult(local.stations, local.carriers, local=True, note=note)
                break
        required = None if stage == PAD_ANY else stage
        stations = search(reference_system.strip(), commodity, "Buy", radius_ly, max_results=STATION_RESULTS,
                          market_days_old=MAX_AGE_DAYS, station_types=trade_prices.station_types(not orbital_only),
                          sort_by=spansh_sort, required_pad=required)
        carriers: List[StationPrice] = []
        if include_carriers:
            carriers = search(reference_system.strip(), commodity, "Buy", radius_ly, max_results=CARRIER_RESULTS,
                              market_days_old=MAX_AGE_DAYS, station_types=trade_prices.CARRIER_TYPES,
                              sort_by=spansh_sort, required_pad=required)
        result = SearchResult(
            stations=order([to_source(i) for i in stations if _fits(i, stage)], sort),
            carriers=order([to_source(i) for i in carriers if _fits(i, stage)], sort))
        if result.stations or result.carriers:
            result = SearchResult(result.stations, result.carriers, note=note)   # the note says what these are, so an empty answer has none
            break
    _cache[key] = (now(), result)   # a failed search raised above, so a failure is never remembered
    return result


def _in_system(here: str, commodity: str, pad: str, include_carriers: bool, orbital_only: bool, sort: str,
               search: SearchFn) -> SearchResult:
    """The stations (and carriers, if asked) in the system `here` that have `commodity` in stock. Spansh is asked for that system alone, so a
    price-sorted search elsewhere cannot push it off the page."""
    def ask(types: List[str], count: int) -> List[Source]:
        found = search(here, commodity, "Buy", None, max_results=count, market_days_old=MAX_AGE_DAYS, station_types=types,
                       sort_by=SORT_DISTANCE, required_pad=None if pad == PAD_ANY else pad, this_system_only=True)
        return [to_source(i) for i in found if _fits(i, pad) and i.system.strip().casefold() == here.casefold()]

    stations = ask(trade_prices.station_types(not orbital_only), STATION_RESULTS)
    carriers = ask(trade_prices.CARRIER_TYPES, CARRIER_RESULTS) if include_carriers else []
    return SearchResult(stations=order(stations, sort), carriers=order(carriers, sort))


# --- the whole list at once ----------------------------------------------------------------------------------------


@dataclass
class WholeListResult:
    """What searching every outstanding commodity found: per commodity, in the order asked, plus the ones that failed."""
    found: List[Tuple[str, SearchResult]] = field(default_factory=list)   # (commodity label, its sources)
    failed: List[Tuple[str, str]] = field(default_factory=list)           # (commodity label, why)
    stopped: bool = False                                                 # the commander stopped it part-way

    def without_sources(self) -> List[str]:
        """Commodities the search ran for but found no station (or carrier) for."""
        return [label for label, result in self.found if not result.stations and not result.carriers]


def find_whole_list(reference_system: str, commodities: Sequence[str], *, radius_ly: Optional[float] = DEFAULT_RADIUS_LY,
                    pad: str = PAD_ANY, include_carriers: bool = False, sort: str = SORT_DISTANCE,
                    search: SearchFn = search_best_price_stations, now: Callable[[], float] = time.monotonic,
                    sleep: Callable[[float], None] = time.sleep, pause: float = WHOLE_LIST_PAUSE,
                    progress: Optional[Callable[[int, int, str], None]] = None,
                    cancelled: Optional[Callable[[], bool]] = None, one_stop: Optional[OneStopFn] = None,
                    needs: Optional[Dict[str, int]] = None, here: str = "", filters: Optional[LocalFilter] = None) -> WholeListResult:
    """`find` for each commodity in turn, one request each (Spansh has no multi-commodity search), pausing between
    requests that really went out. A commodity whose search fails is recorded and the rest carry on, so one bad answer
    does not lose the others; a blank system is refused outright. `progress(done, total, label)` is called before each
    commodity, and `cancelled()` is checked between them.

    With `one_stop` (Spansh's "has all of these" search, which returns each station's whole market) one more request asks
    for stations that sell every commodity in the list; any it finds are added to each commodity's sources, so the route can
    use a station that is not among the nearest few for any one commodity. That request is a bonus: if it fails, nothing is
    lost. Given `needs` as well (tons still to get, by label), it goes first, and a commodity that one of those stations
    can supply in full is not searched on its own (fewer requests); then, if the route built from the answers still leaves
    two or more commodities uncovered, one more request asks for stations that sell all of those, and their whole markets
    (every listed commodity they have in stock) are added too.

    With `here` (the system the commander is in) each commodity is looked for in that system first, as `find` does: one that a station there
    has in stock is answered from there alone, so the one-stop stations and the orbital check add nothing outside to it, and a one-stop station
    outside `here` does not stand in for that commodity's own search. `filters` (the commander's exclusions, with `needs` as the tons wanted) decide
    whether a station in `here` counts as having the commodity at all."""
    if not reference_system.strip():
        raise ValueError("Enter a system to search around.")
    out = WholeListResult()
    stop_pad = PAD_LARGE if pad == PAD_LARGE_FIRST else pad   # the one-stop stations are asked for with a Large pad: a Medium fall-back is per commodity
    options = dict(radius_ly=radius_ly, pad=pad, include_carriers=include_carriers, sort=sort, search=search, now=now, here=here, filters=filters)

    def wanted_t(label: str) -> int:
        return (needs or {}).get(label, 0)
    sent_any = False
    pre_hits: List[Tuple[StationPrice, Dict[str, Tuple[int, int]]]] = []
    satisfied: Dict[str, SearchResult] = {}
    if one_stop is not None and needs and len(commodities) >= 2 and not (cancelled is not None and cancelled()):
        try:
            pre_hits = _one_stop_hits(one_stop, reference_system, list(commodities), radius_ly, stop_pad, include_carriers)
        except Exception:   # an extra; the per-commodity searches then run for everything
            pre_hits = []
        sent_any = True
        pre_hits = [(item, offers) for item, offers in pre_hits if _fits(item, stop_pad)]
        for label in commodities:
            need = needs.get(label, 0)
            if need <= 0:
                continue
            here_stock = [_hit_source(item, offers[label]) for item, offers in pre_hits
                          if label in offers and offers[label][1] >= need and _is_here(item, here)]
            here_stock = [source for source in here_stock if filters is None or _wanted(source, filters, need)]
            if here_stock:   # the one-stop answer already has the whole amount in the commander's system: that is this commodity's answer
                satisfied[label] = SearchResult(order([s for s in here_stock if not s.is_carrier], sort), order([s for s in here_stock if s.is_carrier], sort), local=True)
    for index, label in enumerate(commodities):
        if cancelled is not None and cancelled():
            out.stopped = True
            break
        if progress is not None:
            progress(index, len(commodities), label)
        if label in satisfied:
            out.found.append((label, satisfied[label]))
            continue
        cached = is_cached(reference_system, label, needed_t=wanted_t(label), **options)
        if sent_any and not cached and pause > 0:
            sleep(pause)
        try:
            out.found.append((label, find(reference_system, label, needed_t=wanted_t(label), **options)))
            sent_any = sent_any or not cached
        except Exception as exc:   # a network or parse failure for this commodity only
            out.failed.append((label, str(exc) or exc.__class__.__name__))
            sent_any = True
    if out.stopped:
        return out
    if pre_hits:
        _merge_hits(out, pre_hits, stop_pad, sort)
    elif one_stop is not None and not needs and len(out.found) >= 2 and not out.failed:
        try:
            hits = _one_stop_hits(one_stop, reference_system, [label for label, _ in out.found], radius_ly, stop_pad, include_carriers)
            _merge_hits(out, hits, stop_pad, sort)
        except Exception:   # an extra; the per-commodity answers stand without it
            pass
    if one_stop is not None and needs and not out.failed:
        _cover_leftovers(out, reference_system, one_stop, needs, radius_ly, stop_pad, include_carriers, sort, sleep, pause)
    if not (cancelled is not None and cancelled()):
        _check_orbital(out, reference_system, options, needs, sleep, pause, cancelled)
    return out


def _is_here(item: StationPrice, here: str) -> bool:
    """Whether a station is in the commander's system (always true when no system is given, so the rule is off)."""
    return not here.strip() or item.system.strip().casefold() == here.strip().casefold()


def _check_orbital(out: WholeListResult, reference_system: str, options: Dict[str, Any], needs: Optional[Dict[str, int]],
                   sleep: Callable[[float], None], pause: float, cancelled: Optional[Callable[[], bool]]) -> None:
    """A commodity whose every source in the answer is a surface port may still be sold at an orbital port: the nearest few sellers can all be
    on planets and push the orbital ones out of the page. For each such commodity (still to get, when `needs` is known) one more request asks for
    orbital stations alone, and any found are added to its sources. A bonus request: a failure loses nothing."""
    for label in sorted(surface_only_labels(out.found), key=str.casefold):
        if needs is not None and needs.get(label, 0) <= 0:
            continue
        if cancelled is not None and cancelled():
            return
        try:
            if pause > 0 and not is_cached(reference_system, label, orbital_only=True, needed_t=(needs or {}).get(label, 0), **options):
                sleep(pause)
            extra = find(reference_system, label, orbital_only=True, needed_t=(needs or {}).get(label, 0), **options)
        except Exception:
            continue
        for index, (name, result) in enumerate(out.found):
            if name != label or result.local:
                continue
            have = {(s.station, s.system) for s in [*result.stations, *result.carriers]}
            stations = list(result.stations) + [s for s in extra.stations if (s.station, s.system) not in have]
            out.found[index] = (name, SearchResult(stations=order(stations, options["sort"]), carriers=list(result.carriers), note=result.note))


def _one_stop_hits(one_stop: OneStopFn, reference_system: str, labels: Sequence[str], radius_ly: Optional[float], pad: str,
                   include_carriers: bool, also: Sequence[str] = ()) -> List[Tuple[StationPrice, Dict[str, Tuple[int, int]]]]:
    types = trade_prices.station_types(True) + (trade_prices.CARRIER_TYPES if include_carriers else [])
    extra = {"also": list(also)} if also else {}
    return one_stop(reference_system.strip(), list(labels), radius_ly, max_results=ONE_STOP_RESULTS, market_days_old=MAX_AGE_DAYS,
                    station_types=types, required_pad=None if pad == PAD_ANY else pad, **extra)


def _hit_source(item: StationPrice, offer: Tuple[int, int]) -> Source:
    """The source for a one-stop station's offer of one commodity: the station with that commodity's price and stock."""
    price, supply = offer
    return to_source(StationPrice(
        station=item.station, system=item.system, station_type=item.station_type, distance_ly=item.distance_ly,
        distance_to_arrival_ls=item.distance_to_arrival_ls, is_planetary=item.is_planetary, price=price,
        quantity=supply, small_pads=item.small_pads, medium_pads=item.medium_pads, large_pads=item.large_pads,
        has_shipyard=item.has_shipyard, position=item.position))


def _merge_hits(out: WholeListResult, hits: Sequence[Tuple[StationPrice, Dict[str, Tuple[int, int]]]], pad: str, sort: str) -> None:
    """Add each hit station to the sources of every commodity it has in stock (see `find_whole_list`), unless already listed."""
    for index, (label, result) in enumerate(out.found):
        if result.local:
            continue
        have = {(s.station, s.system) for s in [*result.stations, *result.carriers]}
        stations, carriers = list(result.stations), list(result.carriers)
        for item, offers in hits:
            if (item.station, item.system) in have or label not in offers or not _fits(item, pad):
                continue
            source = _hit_source(item, offers[label])
            (carriers if source.is_carrier else stations).append(source)
        out.found[index] = (label, SearchResult(stations=order(stations, sort), carriers=order(carriers, sort)))


def _cover_leftovers(out: WholeListResult, reference_system: str, one_stop: OneStopFn, needs: Dict[str, int],
                     radius_ly: Optional[float], pad: str, include_carriers: bool, sort: str,
                     sleep: Callable[[float], None], pause: float) -> None:
    """One more request for what the route built so far cannot supply: stations that sell all of the uncovered commodities
    (their whole markets also cover any other listed commodity they stock). A bonus request: a failure loses nothing."""
    left = [label for label, _tons in plan_route(out.found, needs).uncovered]
    if len(left) < 2:
        return
    try:
        if pause > 0:
            sleep(pause)
        hits = _one_stop_hits(one_stop, reference_system, left, radius_ly, pad, include_carriers,
                              also=[label for label, _ in out.found if label not in left])
        _merge_hits(out, hits, pad, sort)
    except Exception:
        pass


# --- a shopping route from the whole-list answer ----------------------------------------------------------------------

ROUTE_MAX_STOPS = 6   # a suggested route never has more stops than this: past that it is a different trip


@dataclass(frozen=True)
class Purchase:
    commodity: str
    tons: int
    price: int           # cr per ton at this stop
    supply: int = 0      # tons in stock at this stop (0 when not known)


@dataclass(frozen=True)
class Stop:
    station: str
    system: str
    kind: str
    is_carrier: bool
    distance_ly: float
    buys: Tuple[Purchase, ...]
    is_planetary: bool = False    # a surface port (needs a planetary landing)
    pad: str = ""                 # the largest pad ("Large" / "Medium" / "Small" / "?"), blank when not known
    position: Optional[Tuple[float, float, float]] = None   # the system's galactic position, when Spansh gave it
    leg_ly: Optional[float] = None   # the jump distance from the stop before it (from the search's system for the first); None when not known

    @property
    def tons(self) -> int:
        return sum(b.tons for b in self.buys)


@dataclass(frozen=True)
class RoutePlan:
    stops: Tuple[Stop, ...]
    needed: int                       # tons the commodities searched for still need in all
    covered: int                      # of that, how many tons the stops can supply
    uncovered: Tuple[Tuple[str, int], ...]   # (commodity, tons) the stops cannot supply (not in range, or too little stock)
    total_ly: Optional[float] = None         # the whole trip, start to last stop; None when any leg is not known

    def lines(self) -> List[str]:
        """The plan as plain lines: a summary, one line per stop, and what is left over."""
        if not self.stops:
            return []
        out = [f"Suggested shopping route: {len(self.stops)} stop{'s' if len(self.stops) != 1 else ''}, "
               f"{self.covered:,} of {self.needed:,} t covered" + (f", {self.total_ly:,.1f} ly in all" if self.total_ly is not None else "")]
        for number, stop in enumerate(self.stops, 1):
            buys = ", ".join(f"{b.commodity} {b.tons:,} t" for b in stop.buys)
            tag = (" (fleet carrier)" if stop.is_carrier else "") + (" (surface port)" if stop.is_planetary else "")
            out.append(f"{number}. {stop.station} ({stop.system}){tag}, {(stop.leg_ly if stop.leg_ly is not None else stop.distance_ly):,.1f} ly: {buys}")
        if self.uncovered:
            out.append("Not covered: " + ", ".join(f"{label} {tons:,} t" for label, tons in self.uncovered))
        return out


def filter_found(found: Sequence[Tuple[str, "SearchResult"]], *, no_surface: bool = False, max_arrival_ls: Optional[int] = None,
                 needs: Optional[Dict[str, int]] = None, shipyard_only: bool = False) -> List[Tuple[str, "SearchResult"]]:
    """The whole-list answers with the sources the commander does not want taken out: surface ports (`no_surface`), stations farther than
    `max_arrival_ls` from their arrival star (an unknown distance is kept), and, given `needs` (tons still to get by label), stations
    holding less of a commodity than is still needed there, and, with `shipyard_only`, stations without a shipyard (a smaller cargo ship can be kept there)."""
    rule = LocalFilter(no_surface=no_surface, max_arrival_ls=max_arrival_ls, shipyard_only=shipyard_only, enough_stock=needs is not None)

    def keep(label: str, source: Source) -> bool:
        return _wanted(source, rule, needs.get(label, 0) if needs is not None else 0)

    return [(label, SearchResult([s for s in result.stations if keep(label, s)], [c for c in result.carriers if keep(label, c)],
                                 local=result.local, note=result.note))
            for label, result in found]


def surface_only_labels(found: Sequence[Tuple[str, "SearchResult"]]) -> frozenset:
    """The commodities whose every source in `found` (with stock) is a surface port; a commodity with no source at all is not among them."""
    out = set()
    for label, result in found:
        sources = [s for s in [*result.stations, *result.carriers] if s.supply > 0]
        if sources and all(s.is_planetary for s in sources):
            out.add(label)
    return frozenset(out)


def _jump(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return math.dist(a, b)


def _fly_order(stops: Sequence[Stop]) -> Tuple[List[Stop], Optional[float]]:
    """Put the stops in the order to fly them: the shortest trip that starts from the search's system (each stop knows its own distance from
    it) and visits every stop, each leg measured from the stop before. Every order is tried (a route has six stops at most). When a
    stop's position is not known the legs cannot be measured, so they go nearest the search's system first and carry no leg (total None)."""
    stops = list(stops)
    if not stops:
        return [], 0.0
    if any(s.position is None for s in stops) or len(stops) > 8:
        stops.sort(key=lambda s: (s.distance_ly, s.station.casefold()))
        return stops, None
    best: Optional[Tuple[float, Tuple[str, ...], Tuple[Stop, ...]]] = None
    for perm in itertools.permutations(stops):
        total = perm[0].distance_ly + sum(_jump(a.position, b.position) for a, b in zip(perm, perm[1:]))   # type: ignore[arg-type]
        key = (round(total, 6), tuple(s.station.casefold() for s in perm))
        if best is None or key < (best[0], best[1]):
            best = (key[0], key[1], perm)
    assert best is not None
    perm = best[2]
    legs = [perm[0].distance_ly] + [_jump(a.position, b.position) for a, b in zip(perm, perm[1:])]   # type: ignore[arg-type]
    return [replace(s, leg_ly=leg) for s, leg in zip(perm, legs)], sum(legs)


def plan_route(found: Sequence[Tuple[str, "SearchResult"]], needs: Dict[str, int], max_stops: int = ROUTE_MAX_STOPS) -> RoutePlan:
    """Pick the few stops that between them supply the most of what is still needed, from the per-commodity answers of a
    whole-list search. `needs` is the tons still to get for each commodity (by label).

    It is greedy: take the station that can supply the most tons of what is still outstanding (a station is offered once per
    commodity it sells, so one that sells several wins), take that off the needs, and repeat until nothing is left, nothing more
    can be covered, or `max_stops` is reached. Ties go to the nearer station, then the cheaper one. The stops are then put in
    order of distance from the search's reference system (the nearest first), which is the order to fly them. Only the stations
    the searches returned are considered, so a commodity with none in range is reported as not covered rather than guessed."""
    remaining = {label: int(tons) for label, tons in needs.items() if tons and tons > 0}
    needed = sum(remaining.values())
    # (station, system) -> {commodity: (supply, price)} plus the details of the station
    offers: Dict[Tuple[str, str], Dict[str, Tuple[int, int]]] = {}
    details: Dict[Tuple[str, str], Source] = {}
    for label, result in found:
        if label not in remaining:
            continue
        for source in [*result.stations, *result.carriers]:
            if source.supply <= 0:
                continue
            key = (source.station, source.system)
            offers.setdefault(key, {})[label] = (source.supply, source.price)
            details.setdefault(key, source)

    chosen: List[Stop] = []
    left = dict(remaining)
    candidates = dict(offers)
    while left and candidates and len(chosen) < max_stops:
        def coverage(key: Tuple[str, str]) -> int:
            return sum(min(supply, left.get(label, 0)) for label, (supply, _price) in candidates[key].items())
        best = max(candidates, key=lambda k: (coverage(k), -details[k].distance_ly, -sum(p for _s, p in candidates[k].values())))
        if coverage(best) <= 0:
            break
        buys = []
        for label, (supply, price) in sorted(candidates[best].items(), key=lambda kv: kv[0].casefold()):
            take = min(supply, left.get(label, 0))
            if take > 0:
                buys.append(Purchase(label, take, price, supply))
                left[label] -= take
                if left[label] <= 0:
                    del left[label]
        source = details[best]
        chosen.append(Stop(source.station, source.system, source.kind, source.is_carrier, source.distance_ly, tuple(buys), source.is_planetary,
                           source.pad, source.position))
        del candidates[best]
    ordered, total = _fly_order(chosen)
    uncovered = tuple(sorted(left.items(), key=lambda kv: kv[0].casefold()))
    return RoutePlan(stops=tuple(ordered), needed=needed, covered=needed - sum(left.values()), uncovered=uncovered, total_ly=total)


# --- remembered choices --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Preset:
    """A named combination of the where-to-buy options. Every preset sorts closest first, and the commander's own system is always searched
    first (see `find`); a preset sets the rest. `radius_ly` None leaves the radius as it is."""
    key: str
    label: str
    pad: str = PAD_LARGE_FIRST
    no_carriers: bool = True
    no_surface: bool = False
    max_arrival_ls: Optional[int] = None
    enough_stock: bool = False
    shipyard_only: bool = False
    radius_ly: Optional[float] = None


PRESET_CUSTOM = "custom"
DEFAULT_PRESET = "large_then_medium"
PRESETS = (
    Preset(DEFAULT_PRESET, "Large, then Medium (default)"),
    Preset("large", "Large ship", pad=PAD_LARGE),
    Preset("medium", "Medium ship", pad=PAD_MEDIUM),
    Preset("one_trip", "One trip (enough stock)", pad=PAD_LARGE, enough_stock=True),
    Preset("quick", "Quick top-up (25 ly, orbital)", pad=PAD_LARGE, no_surface=True, max_arrival_ls=2500, radius_ly=25.0),
    Preset("orbital", "Orbital only (near arrival)", no_surface=True, max_arrival_ls=1000),
    Preset("shipyard", "Shipyard stops", shipyard_only=True),
)
PRESET_LABELS = {preset.key: preset.label for preset in PRESETS} | {PRESET_CUSTOM: "Custom"}


def preset_by_key(key: str) -> Optional[Preset]:
    return next((p for p in PRESETS if p.key == key), None)


def preset_for(*, pad: str, sort: str, no_carriers: bool, no_surface: bool, max_arrival_ls: Optional[int], enough_stock: bool,
               shipyard_only: bool, radius_ly: Optional[float]) -> str:
    """The key of the preset the given options match exactly, else PRESET_CUSTOM."""
    for p in PRESETS:
        if (sort == SORT_DISTANCE and pad == p.pad and no_carriers == p.no_carriers and no_surface == p.no_surface
                and max_arrival_ls == p.max_arrival_ls and enough_stock == p.enough_stock and shipyard_only == p.shipyard_only
                and (p.radius_ly is None or radius_ly == p.radius_ly)):
            return p.key
    return PRESET_CUSTOM


@dataclass(frozen=True)
class SearchPrefs:
    """The where-to-buy options the commander last used, kept between sessions. These are window preferences, not
    anything about their play, so they are shared by every commander like the window's size."""
    radius_ly: Optional[float] = DEFAULT_RADIUS_LY   # None = no limit
    pad: str = PAD_LARGE_FIRST
    no_carriers: bool = True     # fleet carriers are left out unless the commander includes them
    sort: str = SORT_DISTANCE
    no_surface: bool = False     # leave surface ports (planetary stations) out (they are included unless asked)
    max_arrival_ls: Optional[int] = None   # leave out stations farther than this from their arrival star (None = no limit)
    enough_stock: bool = False   # leave out stations holding less of a commodity than is still needed
    shipyard_only: bool = False  # only stations with a shipyard
    preset: str = DEFAULT_PRESET # the preset these options matched when saved (PRESET_CUSTOM when none)


def dump_prefs(prefs: SearchPrefs) -> str:
    return json.dumps({"radius": prefs.radius_ly, "pad": prefs.pad, "no_carriers": prefs.no_carriers, "sort": prefs.sort,
                       "no_surface": prefs.no_surface, "arrival": prefs.max_arrival_ls, "enough": prefs.enough_stock,
                       "shipyard": prefs.shipyard_only, "preset": prefs.preset})


def load_prefs(raw: Any) -> SearchPrefs:
    """The saved choices, with anything missing, unreadable or out of range replaced by its default."""
    try:
        data = json.loads(raw) if isinstance(raw, str) and raw.strip() else {}
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    default = SearchPrefs()
    radius = data.get("radius", default.radius_ly)
    if radius is not None and (isinstance(radius, bool) or radius not in RADIUS_CHOICES):
        radius = default.radius_ly
    if data and "preset" not in data:   # saved before presets existed: the new defaults apply (only the radius is kept)
        return SearchPrefs(radius_ly=float(radius) if radius is not None else None)
    pad = data.get("pad")
    sort = data.get("sort")
    no_carriers = data.get("no_carriers")
    no_surface = data.get("no_surface")
    arrival = data.get("arrival")
    enough = data.get("enough")
    shipyard = data.get("shipyard")
    return SearchPrefs(
        radius_ly=float(radius) if radius is not None else None,
        pad=pad if pad in {key for key, _ in PAD_CHOICES} else default.pad,
        no_carriers=no_carriers if isinstance(no_carriers, bool) else default.no_carriers,
        sort=sort if sort in (SORT_DISTANCE, SORT_PRICE) else default.sort,
        no_surface=no_surface if isinstance(no_surface, bool) else default.no_surface,
        max_arrival_ls=arrival if (not isinstance(arrival, bool) and arrival in ARRIVAL_CHOICES) else default.max_arrival_ls,
        enough_stock=enough if isinstance(enough, bool) else default.enough_stock,
        shipyard_only=shipyard if isinstance(shipyard, bool) else default.shipyard_only,
        preset=data["preset"] if isinstance(data.get("preset"), str) and data["preset"] in PRESET_LABELS else default.preset)
