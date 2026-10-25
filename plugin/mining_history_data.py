"""What the Mining History window shows, worked out from the saved runs (`mining_history`). Pure Python: no Tk, no EDMC, nothing fetched.

The window (mining_history_window.py) asks for plain rows and fields and only draws them, so everything here is tested without a screen. Figures that cannot be known are left
as `-`, never guessed. "Mining time" is the span from a run's first to its last mining event (a limpet launched, an asteroid prospected, a ton refined or a rock cracked), not the time spent undocked, so travel and
waiting at the station do not dilute the rate; it is the same span the live page's run average is read over (gaps of more than ten minutes between mining events are left out of both). "Earned" is what the `MarketSell` events paid, at whichever station
they were made, for the commodities refined in that run (oldest run first; see `mining_history`); it is not profit (it does not subtract fuel, repairs or ammunition), and what was sold beyond the tons mined
(bought cargo, say) is not counted. Tons mined and not yet sold are left out until they are sold. "After limpets" is "Earned" less what the limpets launched in the run cost, each at the price last paid for
limpets (`BuyDrones`); a limpet launched before any price was known is counted in `limpet_unpriced` and costs nothing here, so the figure is then a little high, and the window says so.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .explore_dashboard_data import DASH, GOOD, INFO, MUTED, TEXT, Fields, Row, Table, Tile, credits, num
from .mining_names import normalize

Run = Dict[str, Any]

SPACE, SURFACE = "space", "surface"
"""The two halves of mining: ring mining from the ship (the Space Mining page) and the Rhino on a body (the Surface Mining page). The window shows one at a time, as the page it was opened from."""


def for_mode(runs: Sequence[Run], mode: Optional[str]) -> List[Run]:
    """The runs as one half of mining sees them (`mode` None keeps every run as it is). A run can hold both (a Rhino run on a trip that also mined a ring), so each is split rather than
    kept or dropped whole: the surface half is what was refined while a Rhino was out, the space half is the rest with the prospecting, cracking and limpets, and the sales after the run are
    matched to the half by the commodity sold. A run with nothing in the half asked for is left out."""
    if mode not in (SPACE, SURFACE):
        return list(runs)
    out: List[Run] = []
    for run in runs:
        srv = {name: count for name, count in (run.get("srv") or {}).items() if count > 0}
        if mode == SURFACE:
            if not srv:
                continue
            half = dict(run, refined=srv, prospected={grade: 0 for grade in run["prospected"]}, motherlode=0, cracked=0, limpets={}, ring="", limpet_cost=0, limpet_unpriced=0)
        else:
            rest = {name: count - srv.get(name, 0) for name, count in run["refined"].items() if count - srv.get(name, 0) > 0}
            if not rest and not run.get("cracked") and not any(run["prospected"].values()):
                continue
            half = dict(run, refined=rest)
        half["sold"] = {name: value for name, value in run["sold"].items() if name in half["refined"]}
        out.append(half)
    return out


def _when(stamp: Any) -> Optional[datetime]:
    try:
        return datetime.strptime(str(stamp), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def refined_tons(run: Run) -> int:
    return sum(run["refined"].values())


def prospected(run: Run) -> int:
    return sum(run["prospected"].values())


def earned(run: Run) -> int:
    return sum(total for _units, total in run["sold"].values())


def limpet_cost(run: Run) -> int:
    return int(run.get("limpet_cost") or 0)


def limpets_unpriced(run: Run) -> int:
    return int(run.get("limpet_unpriced") or 0)


def net(run: Run) -> int:
    """What the run's sales paid less what its limpets cost."""
    return earned(run) - limpet_cost(run)


def signed_credits(value: int) -> str:
    """A credit figure that can be negative (a run whose limpets cost more than it has sold so far)."""
    return DASH if not value else (f"-{credits(-value)}" if value < 0 else credits(value))


def sold_units(run: Run) -> int:
    return sum(units for units, _total in run["sold"].values())


def mining_hours(run: Run) -> float:
    """Hours from the run's first to its last mining event, less the gaps of more than ten minutes between two of them (`idle`, seconds): the live page's mining time."""
    first, last = _when(run.get("first")), _when(run.get("last"))
    if not (first and last):
        return 0.0
    idle = run.get("idle")
    return max(0.0, ((last - first).total_seconds() - (idle if isinstance(idle, (int, float)) else 0)) / 3600.0)


def per_hour(amount: float, hours: float) -> Optional[float]:
    return amount / hours if hours > 0 else None


def minutes_text(hours: float) -> str:
    return f"{hours * 60:,.0f} min" if hours else DASH


def percent(part: float, whole: float) -> str:
    return f"{part / whole:.0%}" if whole else DASH


def date_text(stamp: Any) -> str:
    when = _when(stamp)
    return when.strftime("%Y-%m-%d %H:%M") if when else DASH


def where_text(run: Run) -> str:
    ring = str(run.get("ring") or "")
    system = str(run.get("system") or "")
    if ring:
        return ring
    return str(run.get("body") or "") or system or DASH


class Totals:
    """Everything the overview adds up across runs."""

    def __init__(self, runs: Sequence[Run]) -> None:
        self.runs = len(runs)
        self.hours = sum(mining_hours(r) for r in runs)
        self.refined = sum(refined_tons(r) for r in runs)
        self.earned = sum(earned(r) for r in runs)
        self.sold = sum(sold_units(r) for r in runs)
        self.prospected = sum(prospected(r) for r in runs)
        self.grades = {grade: sum(r["prospected"].get(grade, 0) for r in runs) for grade in ("Low", "Medium", "High")}
        self.motherlodes = sum(r.get("motherlode", 0) for r in runs)
        self.cracked = sum(r.get("cracked", 0) for r in runs)
        self.limpets: Dict[str, int] = {}
        for r in runs:
            for kind, count in r["limpets"].items():
                self.limpets[kind] = self.limpets.get(kind, 0) + count
        self.limpet_cost = sum(limpet_cost(r) for r in runs)
        self.unpriced = sum(limpets_unpriced(r) for r in runs)
        self.net = self.earned - self.limpet_cost
        self.rate = per_hour(self.refined, self.hours)
        self.credit_rate = per_hour(self.earned, self.hours)
        self.net_rate = per_hour(self.net, self.hours)


def overview_tiles(runs: Sequence[Run], mode: Optional[str] = None) -> List[Tile]:
    t = Totals(runs)
    if not runs:
        return [Tile("0", "mining runs found", MUTED)]
    tiles = [
        Tile(f"{t.runs:,}", "mining runs", TEXT),
        Tile(num(t.hours, 1), "hours mining", TEXT),
        Tile(f"{t.refined:,}", "tons refined", GOOD),
        Tile(num(t.rate, 0) if t.rate else DASH, "tons per hour", GOOD),
        Tile(credits(t.earned), "credits from sales", INFO),
        Tile(signed_credits(t.net), "credits after limpets", INFO),
        Tile(credits(int(t.credit_rate)) if t.credit_rate else DASH, "credits per hour", INFO),
        Tile(percent(t.grades["High"], t.prospected), "asteroids rated High", TEXT),
    ]
    if mode == SURFACE:                                   # a Rhino prospects no asteroids and launches no limpets
        return [tile for tile in tiles if tile.caption not in ("asteroids rated High", "credits after limpets")]
    return tiles


def prospecting_fields(runs: Sequence[Run]) -> Fields:
    t = Totals(runs)
    return [
        ("Asteroids prospected", f"{t.prospected:,}"),
        ("Low content", f"{t.grades['Low']:,} ({percent(t.grades['Low'], t.prospected)})"),
        ("Medium content", f"{t.grades['Medium']:,} ({percent(t.grades['Medium'], t.prospected)})"),
        ("High content", f"{t.grades['High']:,} ({percent(t.grades['High'], t.prospected)})"),
        ("Motherlodes", f"{t.motherlodes:,}"),
        ("Asteroids cracked", f"{t.cracked:,}"),
        ("Tons per asteroid prospected", num(t.refined / t.prospected, 1) if t.prospected else DASH),
    ]


def limpet_fields(runs: Sequence[Run]) -> Fields:
    t = Totals(runs)
    fields: Fields = [(f"{kind} limpets launched", f"{count:,}") for kind, count in sorted(t.limpets.items(), key=lambda kv: -kv[1])]
    prospectors = t.limpets.get("Prospector", 0)
    collectors = t.limpets.get("Collection", 0)
    if t.prospected and prospectors:
        fields.append(("Prospectors per asteroid prospected", num(prospectors / t.prospected, 2)))
    if t.refined and collectors:
        fields.append(("Collectors per ton refined", num(collectors / t.refined, 2)))
    return fields or [("No limpets launched", "")]


def surface_fields(runs: Sequence[Run]) -> Fields:
    """What the Rhino's runs add up to by body: how many bodies were mined on and where the most tons came from."""
    tons: Dict[str, int] = {}
    for run in runs:
        name = str(run.get("body") or "") or "(no body recorded)"
        tons[name] = tons.get(name, 0) + refined_tons(run)
    if not tons:
        return [("No Rhino mining yet", "")]
    best = max(tons.items(), key=lambda kv: kv[1])
    return [("Bodies mined on", f"{len(tons):,}"), ("Most tons on one body", f"{best[1]:,} t on {best[0]}"),
            ("Tons per body on average", num(sum(tons.values()) / len(tons), 1))]


def waiting_tons(runs: Sequence[Run], unsold: Optional[Dict[str, Dict[str, int]]]) -> int:
    """The tons these runs mined that are still waiting to be sold. `unsold` is `mining_history`'s list by run key (the same `file|start` as below) and commodity; a half of a run counts the
    commodities it refined."""
    if not unsold:
        return 0
    return sum(tons for run in runs for name, tons in unsold.get(f"{run.get('file')}|{run.get('start')}", {}).items() if name in run["refined"])


def sales_fields(runs: Sequence[Run], unsold: Optional[Dict[str, Dict[str, int]]] = None) -> Fields:
    t = Totals(runs)
    fields: Fields = [("Credits from sales", credits(t.earned))]
    if t.limpet_cost or t.unpriced:
        spent = credits(t.limpet_cost) + (f" (and {t.unpriced:,} launched with no price known)" if t.unpriced else "")
        fields += [("Limpets launched cost", spent), ("Credits after limpets", signed_credits(t.net))]
    fields += [
        ("Tons sold", f"{t.sold:,}"),
        ("Average price per ton", credits(int(t.earned / t.sold)) if t.sold else DASH),
        ("Credits per mining hour", credits(int(t.credit_rate)) if t.credit_rate else DASH),
    ]
    if t.limpet_cost and t.net_rate:
        fields.append(("After limpets per mining hour", signed_credits(int(t.net_rate))))
    waiting = waiting_tons(runs, unsold)
    if waiting:
        fields.append(("Mined, not sold yet", f"{waiting:,} t"))
    fields.append(("Note", "Sales count at any station, for the tons you mined. Only limpets are taken off; fuel, repairs and ammunition are not, and tons not sold yet earn nothing yet."))
    return fields


def best_runs_fields(runs: Sequence[Run], limit: int = 3) -> Fields:
    """The best runs by tons refined, with the rate for each."""
    ranked = sorted((r for r in runs if refined_tons(r)), key=lambda r: -refined_tons(r))[:limit]
    fields: Fields = []
    for r in ranked:
        rate = per_hour(refined_tons(r), mining_hours(r))
        fields.append((date_text(r.get("start"))[:10], f"{refined_tons(r):,} t at {where_text(r)}" + (f" ({rate:,.0f} t/h)" if rate else "")))
    return fields or [("No runs yet", "")]


COMMODITY_COLUMNS = (("name", "Commodity", 240, "w"), ("refined", "Refined (t)", 100, "e"), ("sold", "Sold (t)", 90, "e"), ("earned", "Earned", 140, "e"),
                     ("avg", "Average per ton", 130, "e"), ("share", "Share of refined", 120, "e"))
RING_COLUMNS = (("name", "Ring", 340, "w"), ("system", "System", 240, "w"), ("runs", "Runs", 70, "e"), ("refined", "Refined (t)", 100, "e"),
                ("prospected", "Prospected", 100, "e"), ("high", "High", 80, "e"), ("last", "Last visit", 140, "w"))
BODY_COLUMNS = (("name", "Body", 340, "w"), ("system", "System", 240, "w"), ("runs", "Runs", 70, "e"), ("refined", "Refined (t)", 100, "e"),
                ("rate", "t / hour", 90, "e"), ("last", "Last visit", 140, "w"))
SURFACE_RUN_COLUMNS = (("when", "Started (UTC)", 130, "w"), ("where", "Where", 300, "w"), ("minutes", "Mining time", 100, "e"), ("refined", "Refined (t)", 100, "e"),
                       ("rate", "t / hour", 80, "e"), ("earned", "Earned", 130, "e"))
RUN_COLUMNS = (("when", "Started (UTC)", 130, "w"), ("where", "Where", 300, "w"), ("minutes", "Mining time", 100, "e"), ("refined", "Refined (t)", 100, "e"),
               ("rate", "t / hour", 80, "e"), ("prospected", "Prospected", 90, "e"), ("high", "High", 70, "e"), ("limpets", "Limpets P / C", 100, "e"),
               ("earned", "Earned", 130, "e"), ("net", "After limpets", 120, "e"))


def commodity_table(runs: Sequence[Run]) -> Table:
    refined: Dict[str, int] = {}
    sold: Dict[str, List[int]] = {}
    for run in runs:
        for name, count in run["refined"].items():
            name = normalize(name) or name
            refined[name] = refined.get(name, 0) + count
        for name, (units, total) in run["sold"].items():
            row = sold.setdefault(normalize(name) or name, [0, 0])
            row[0] += units
            row[1] += total
    total_refined = sum(refined.values())
    names = sorted(set(refined) | set(sold), key=lambda n: (-refined.get(n, 0), n.casefold()))
    rows = []
    for name in names:
        units, total = sold.get(name, [0, 0])
        rows.append(Row(name.casefold(), [name, f"{refined.get(name, 0):,}", f"{units:,}" if units else DASH, credits(total),
                                          credits(int(total / units)) if units else DASH, percent(refined.get(name, 0), total_refined)]))
    return Table(COMMODITY_COLUMNS, rows, "No mining found in your journals yet.")


def ring_table(runs: Sequence[Run]) -> Table:
    groups: Dict[Tuple[str, str], List[Run]] = {}
    for run in runs:
        groups.setdefault((str(run.get("ring") or "(no ring recorded)"), str(run.get("system") or "")), []).append(run)
    ordered = sorted(groups.items(), key=lambda kv: -sum(refined_tons(r) for r in kv[1]))
    rows = []
    for (ring, system), group in ordered:
        pros = sum(prospected(r) for r in group)
        high = sum(r["prospected"].get("High", 0) for r in group)
        rows.append(Row(f"{ring}|{system}", [ring, system or DASH, f"{len(group):,}", f"{sum(refined_tons(r) for r in group):,}", f"{pros:,}",
                                              percent(high, pros), date_text(max(str(r.get("start") or "") for r in group))]))
    return Table(RING_COLUMNS, rows, "No mining found in your journals yet.")


def body_table(runs: Sequence[Run]) -> Table:
    """The Rhino's runs grouped by the body they were on, most tons first."""
    groups: Dict[Tuple[str, str], List[Run]] = {}
    for run in runs:
        groups.setdefault((str(run.get("body") or "(no body recorded)"), str(run.get("system") or "")), []).append(run)
    ordered = sorted(groups.items(), key=lambda kv: -sum(refined_tons(r) for r in kv[1]))
    rows = []
    for (body, system), group in ordered:
        tons, hours = sum(refined_tons(r) for r in group), sum(mining_hours(r) for r in group)
        rate = per_hour(tons, hours)
        rows.append(Row(f"{body}|{system}", [body, system or DASH, f"{len(group):,}", f"{tons:,}", num(rate, 0) if rate else DASH,
                                              date_text(max(str(r.get("start") or "") for r in group))]))
    return Table(BODY_COLUMNS, rows, "No Rhino mining found in your journals yet.")


def run_table(runs: Sequence[Run], mode: Optional[str] = None) -> Table:
    rows = []
    for run in sorted(runs, key=lambda r: str(r.get("start") or ""), reverse=True):
        hours = mining_hours(run)
        rate = per_hour(refined_tons(run), hours)
        pros = prospected(run)
        if mode == SURFACE:
            rows.append(Row(f"{run.get('file')}:{run.get('start')}", [
                date_text(run.get("start")), where_text(run), minutes_text(hours), f"{refined_tons(run):,}", num(rate, 0) if rate else DASH, credits(earned(run))]))
            continue
        rows.append(Row(f"{run.get('file')}:{run.get('start')}", [
            date_text(run.get("start")), where_text(run), minutes_text(hours), f"{refined_tons(run):,}", num(rate, 0) if rate else DASH,
            f"{pros:,}", percent(run["prospected"].get("High", 0), pros),
            f"{run['limpets'].get('Prospector', 0)} / {run['limpets'].get('Collection', 0)}", credits(earned(run)),
            (("~" if limpets_unpriced(run) else "") + signed_credits(net(run))) if sold_units(run) else DASH]))
    return Table(SURFACE_RUN_COLUMNS if mode == SURFACE else RUN_COLUMNS, rows, "No Rhino mining found in your journals yet." if mode == SURFACE else "No mining found in your journals yet.")


def subtitle(commander: str, runs: Sequence[Run], reading: str = "", mode: Optional[str] = None) -> str:
    who = f"CMDR {commander} - " if commander else ""
    kind = {SURFACE: "Rhino ", SPACE: "ring "}.get(mode or "", "")
    if reading:
        return who + reading
    if not runs:
        return who + f"no {kind}mining runs found"
    first = date_text(min(str(r.get("start") or "") for r in runs))[:10]
    return f"{who}{len(runs):,} {kind}mining runs since {first}"
