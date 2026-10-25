"""What pays: the commodities you could surface-mine, ranked by the best price Spansh shows for them.

Two pure steps, with the Spansh calls (`mining_spansh_client.search_best_price_stations`) and the window (`mining_what_pays_dialog.py`) kept apart from them:

1. `candidates` names the commodities worth pricing, each with the reason, from the commander's own records only: the target commodity set in Settings, every material in the
   saved deposits (any system), what the commander has recorded on the same kind of ground as the scanned bodies of the system they are in (`mining_ground.OwnRates`), and any
   the commander types. There is deliberately no table of which commodity sits on which planet type: the game does not publish one, and community testing says planet class is only a
   screening lead, not a rule. So this ranks what pays, not what a body holds.
2. `rank` takes the best station Spansh found for each and orders them, best price first, with the commodities no station priced last.

No tkinter and no network; see tests/test_mining_what_pays.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

from . import current_cargo, mining_ground
from . import mining_hotspots as hotspots
from . import mining_market_research as research
from . import trade_commodities, trade_prices

MAX_MINIMUM = 1_000_000
"""The most a minimum demand or supply can be asked for: more than any market holds."""

hold = current_cargo.held
"""The hold by commodity (EDMC's cargo state, lower-case names to tons); a module-level name so tests can replace it. Empty when EDMC has not given one."""

NO_CARRIERS: Dict[str, Any] = {"station_types": trade_prices.station_types(True), "exclude_carriers": True}
"""What keeps fleet carriers out of a search: ask for the kinds of station only (so carriers cannot fill the page ahead of real stations) and drop any carrier that is returned anyway.
The kinds are `trade_prices.station_types`; a kind of station Spansh adds that is not in that list is not found until it is."""

MAX_CANDIDATES = 16
"""The most commodities priced at once: one request each, so the wait and the load on Spansh stay small."""


def _norm(text: str) -> str:
    return text.strip().casefold()


def _same_commodity(a: str, b: str) -> bool:
    def key(name: str) -> str:
        return trade_commodities.resolve(name) or "".join(ch for ch in str(name).casefold() if ch.isalnum())
    return bool(key(a)) and key(a) == key(b)


def tons_in_hold(commodity: str) -> int:
    """The tons of `commodity` in the hold, matched whatever the spelling (`lowtemperaturediamond`, `Low Temperature Diamonds`); 0 when it is not there or the hold is not known."""
    try:
        return sum(int(tons) for name, tons in hold().items() if isinstance(tons, (int, float)) and tons > 0 and _same_commodity(name, commodity))
    except Exception:
        return 0


def minimum_for(commodity: str) -> int:
    """The default demand floor for `commodity`: the tons of it in the hold (a station that cannot take them all is a poor answer), at least 1."""
    return min(MAX_MINIMUM, max(1, tons_in_hold(commodity)))


def parse_minimum(text: str) -> Optional[int]:
    """The minimum typed into the box as a whole number of tons from 1 to MAX_MINIMUM (commas allowed, empty means 1); None when it is not one."""
    cleaned = text.strip().replace(",", "")
    if not cleaned:
        return 1
    if not cleaned.isascii() or not cleaned.isdigit():
        return None
    number = int(cleaned)
    return number if 1 <= number <= MAX_MINIMUM else None


@dataclass(frozen=True)
class Offer:
    """The best station found for one commodity (a sell search: what a station pays you)."""
    station: str
    system: str
    price: int
    demand: int
    distance_ly: float
    arrival_ls: float
    pads: str


@dataclass(frozen=True)
class Row:
    name: str
    reasons: tuple[str, ...]
    offer: Optional[Offer]


def candidates(saved: Sequence[hotspots.Hotspot], grounds: Sequence[str], rates: mining_ground.OwnRates, target: str = "", extra: Sequence[str] = (),
               limit: int = MAX_CANDIDATES) -> research.Plan:
    """The commodities to price. `saved` is all of the commander's hotspots, `grounds` the ground keys of the landable bodies scanned in the system they are in, `rates` their own
    rates, `target` the target commodity from Settings (empty for none) and `extra` names typed by hand. The same name from two sources is one commodity with both reasons."""
    order: list[str] = []
    reasons: dict[str, list[str]] = {}
    skipped: list[str] = []

    def add(raw: str, reason: str) -> None:
        name = trade_commodities.resolve(raw)
        if name is None:
            if raw.strip() and raw.strip() not in skipped:
                skipped.append(raw.strip())
            return
        if name not in reasons:
            order.append(name)
            reasons[name] = []
        if reason not in reasons[name]:
            reasons[name].append(reason)

    if target.strip():
        add(target, "your target commodity")

    counts: dict[str, int] = {}
    bodies: dict[str, set[str]] = {}
    labels: dict[str, str] = {}
    for spot in saved:
        if not spot.material.strip():
            continue
        key = _norm(spot.material)
        counts[key] = counts.get(key, 0) + 1
        bodies.setdefault(key, set()).add(f"{_norm(spot.system)}|{_norm(spot.body)}")
        labels.setdefault(key, spot.material.strip())
    for key in sorted(counts, key=lambda k: (-counts[k], k)):
        count, places = counts[key], len(bodies[key])
        add(labels[key], f"{count} saved deposit{'s' if count != 1 else ''} on {places} bod{'ies' if places != 1 else 'y'}")

    ranked: list[tuple[float, str, str]] = []
    for ground in dict.fromkeys(grounds):
        size = rates.sample_size(ground)
        for rate in rates.rates(ground):
            ranked.append((rate.pct, rate.material,
                           f"{rate.pct:.0f}% of your {size} recorded deposit{'s' if size != 1 else ''} on this kind of ground ({mining_ground.label(ground).lower()})"))
    for _pct, material, reason in sorted(ranked, key=lambda r: (-r[0], r[1].casefold())):
        add(material, reason)

    for raw in extra:
        add(raw, "added by you")

    chosen = tuple(research.Candidate(name, tuple(reasons[name])) for name in order[:limit])
    return research.Plan(chosen, tuple(skipped))


def rank(rows: Sequence[Row]) -> list[Row]:
    """Best price first; a commodity no station priced goes last, then by name."""
    return sorted(rows, key=lambda r: (r.offer is None, -(r.offer.price if r.offer else 0), r.name.casefold()))


def offer_from(station_price) -> Offer:
    """An `Offer` from a `mining_spansh_client.StationPrice`."""
    pads = [f"{count} {size}" for size, count in (("small", station_price.small_pads), ("medium", station_price.medium_pads), ("large", station_price.large_pads)) if count]
    return Offer(station_price.station, station_price.system, int(station_price.price), int(station_price.quantity), float(station_price.distance_ly),
                 float(station_price.distance_to_arrival_ls), ", ".join(pads))


def format_report(origin: str, where: str, rows: Sequence[Row], skipped: Sequence[str] = ()) -> str:
    """The text the window copies: what pays best, one line per commodity, and the caveat."""
    lines = [f"What pays, {where.lower()} of {origin}:"]
    if not rows:
        lines.append("Nothing to price yet. Save a deposit, set a target commodity in Settings, or add commodities in the box above.")
    for number, row in enumerate(rank(rows), 1):
        why = "; ".join(row.reasons)
        if row.offer is None:
            lines.append(f"{number}. {row.name}: no station found paying for it ({why})")
            continue
        o = row.offer
        extras = [f"demand {o.demand:,}", f"{o.distance_ly:,.1f} ly", f"{o.arrival_ls:,.0f} ls"] + ([o.pads] if o.pads else [])
        lines.append(f"{number}. {row.name}: {o.price:,} cr at {o.station}, {o.system} ({', '.join(extras)}). Why: {why}")
    if skipped:
        lines.append("Not a commodity Spansh knows, so left out: " + ", ".join(skipped))
    lines.append("This ranks what pays, from your own records: the game does not say which commodities a body carries. Prices are the last ones players uploaded.")
    return "\n".join(lines)
