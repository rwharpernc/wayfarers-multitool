"""What the Exploration Dashboard shows, worked out from the data the other features already hold. Pure Python: no Tk, no overlay, no EDMC.

The dashboard window (explore_dashboard_window.py) asks this module for plain rows and fields and only draws them, so everything here is tested without a screen. Nothing
is stored or fetched: the inputs are the system survey (`system_survey`), Organic Scanning's view of the body the commander is at (`organic_scan.BodyView`), the newest
Status.json, the running Expedition Log run and the Exploration panel's own readouts. A value that is not known is left out or shown as `-`, never guessed.

Two perspectives, because the questions differ: from **orbit** the system as a whole (every body, what is worth mapping, where the life is), and on the **ground** the
body under the commander (its conditions and materials, the biology on it, the specimens being tracked). `perspective(status)` says which one the commander is in, so the
window can open on the right tab.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Sequence, Tuple

from . import expedition_log, organic_scan
from .system_survey import Body, SystemSurvey, credits_text

ORBIT, GROUND = "orbit", "ground"
FLAG_LANDED = 1 << 1
Fields = List[Tuple[str, str]]                 # (label, value) rows of a details block
DASH = "-"

# Color roles; the window maps them onto its palette.
TEXT, GOOD, WARN, INFO, MUTED, BAD = "text", "good", "warn", "info", "muted", "bad"


@dataclass
class Tile:
    value: str
    caption: str
    role: str = TEXT


@dataclass
class Row:
    key: str
    cells: List[str]
    tag: str = ""


@dataclass
class Table:
    columns: Sequence[Tuple[str, str, int, str]]       # (key, heading, width, anchor)
    rows: List[Row] = field(default_factory=list)
    empty: str = ""


# --- small formatters ---------------------------------------------------------------------------------------------------------

def num(value: Optional[float], digits: int = 0, unit: str = "") -> str:
    if value is None:
        return DASH
    return f"{value:,.{digits}f}{unit}"


def credits(value: Optional[int]) -> str:
    return credits_text(int(value)) if value else DASH


def meters(value: Optional[float]) -> str:
    if value is None:
        return DASH
    return f"{value / 1000:.1f} km" if value >= 1000 else f"{value:.0f} m"


def light_seconds(value: Optional[float]) -> str:
    if value is None:
        return DASH
    return f"{value:,.0f} ls" if value >= 10 else f"{value:.1f} ls"


def percent_text(percent: float) -> str:
    return f"{percent:.0f}%" if percent >= 1 or percent == 0 else f"{percent:.1f}%"


# --- where the commander is ---------------------------------------------------------------------------------------------------

def mode_of(status: Mapping[str, Any]) -> str:
    """"srv", "ship", "foot" or "" from Status.json's flags (organic_scan.scan_mode)."""
    return organic_scan.scan_mode(status.get("Flags"), status.get("Flags2"))


def perspective(status: Mapping[str, Any]) -> str:
    """GROUND when the commander is on a surface (landed, in the SRV or on foot), otherwise ORBIT (in space, in a ship above a planet, or docked)."""
    flags = status.get("Flags")
    if isinstance(flags, int) and flags & FLAG_LANDED:
        return GROUND
    return GROUND if mode_of(status) in ("srv", "foot") else ORBIT


def you_fields(status: Mapping[str, Any], survey: Optional[SystemSurvey] = None) -> Fields:
    """Where the commander is, from the newest Status.json."""
    if not status:
        return [("Status", "waiting for the game's status file")]
    mode = mode_of(status)
    where = {"srv": "In the SRV", "foot": "On foot", "ship": "In the ship"}.get(mode, DASH)
    flags = status.get("Flags")
    if isinstance(flags, int) and flags & FLAG_LANDED:
        where = "Landed" + (" (SRV out)" if mode == "srv" else "")
    rows: Fields = [("Now", where)]
    body = str(status.get("BodyName") or "")
    if body:
        short = survey.find(name=body) if survey is not None else None
        rows.append(("Near", short.short if short is not None and short.short else body))
    if isinstance(status.get("Altitude"), (int, float)) and status.get("Altitude") is not None:
        rows.append(("Altitude", meters(float(status["Altitude"]))))
    if isinstance(status.get("Latitude"), (int, float)) and isinstance(status.get("Longitude"), (int, float)):
        rows.append(("Position", f"{status['Latitude']:.4f}, {status['Longitude']:.4f}"))
    if isinstance(status.get("Heading"), (int, float)):
        rows.append(("Heading", f"{status['Heading']:.0f} degrees"))
    fuel = status.get("Fuel")
    if isinstance(fuel, Mapping) and isinstance(fuel.get("FuelMain"), (int, float)):
        rows.append(("Fuel", f"{fuel['FuelMain']:.1f} t main" + (f", {fuel['FuelReservoir']:.2f} t reserve" if isinstance(fuel.get("FuelReservoir"), (int, float)) else "")))
    return rows


# --- the system ---------------------------------------------------------------------------------------------------------------

def _planets(survey: SystemSurvey) -> List[Body]:
    return [b for b in survey.bodies.values() if b.kind == "planet"]


def totals(survey: SystemSurvey) -> Mapping[str, int]:
    """The system's sums, each over the bodies the commander (or EDSM) has described."""
    described = [b for b in survey.bodies.values() if b.scanned or b.known]
    planets = [b for b in _planets(survey) if b.scanned or b.known]
    return {
        "scan_value": sum(b.scan_value() for b in described),
        "mapped_value": sum(b.mapped_value() for b in planets),
        "unmapped_extra": sum(max(0, b.mapped_value() - b.scan_value()) for b in planets if not b.mapped),
        "first_discoveries": sum(1 for b in described if b.was_discovered is False),
        "first_footfalls": sum(1 for b in described if b.first_footfall),
        "landable": sum(1 for b in described if b.landable),
        "terraformable": sum(1 for b in described if b.terraformable),
        "bio_bodies": sum(1 for b in survey.bodies.values() if b.bio > 0),
        "geo_bodies": sum(1 for b in survey.bodies.values() if b.geo > 0),
    }


def overview_tiles(survey: SystemSurvey, threshold: int, basis: str, run: Optional[expedition_log.Run] = None) -> List[Tile]:
    """The numbers across the top of the dashboard."""
    if not survey.name:
        return [Tile(DASH, "No system yet", MUTED)]
    sums = totals(survey)
    scanned, total = survey.scanned_count(), survey.body_count
    analyzed, signals = survey.bio_totals()
    to_map = survey.to_map(threshold, basis)
    tiles = [
        Tile(f"{scanned}/{total}" if total else str(scanned), "bodies scanned", GOOD if total and scanned >= total else TEXT),
        Tile(str(survey.mapped_count()), "planets mapped", INFO),
        Tile(str(len(to_map)), f"worth mapping (over {credits_text(threshold)})" if threshold else "scanned, not mapped", WARN if to_map else MUTED),
        Tile(f"{analyzed}/{signals}" if signals else "0", "biological signals analyzed", GOOD if signals and analyzed >= signals else (WARN if signals else MUTED)),
        Tile(credits(sums["scan_value"]), "scan value (estimate)"),
        Tile(credits(sums["unmapped_extra"]), "more from mapping (estimate)", INFO),
        Tile(str(sums["first_discoveries"]), "first discoveries here", GOOD if sums["first_discoveries"] else MUTED),
    ]
    if run is not None:
        tiles.append(Tile(expedition_log.short_credits(run.totals.earned), "earned this expedition", GOOD))
    return tiles


def system_fields(survey: SystemSurvey, progress_text: str = "") -> Fields:
    """The system as a whole."""
    if not survey.name:
        return [("System", "no system yet: jump, or log in")]
    sums = totals(survey)
    scan = f"{min(100.0, survey.progress * 100):.0f}% of the system scanned" if survey.honked else "not honked yet"
    rows: Fields = [
        ("System", survey.name + (" (in hyperspace: this is the last system)" if survey.in_transit else " (docked)" if survey.docked else "")),
        ("Honk", (f"{survey.body_count} bodies, {scan}" if survey.body_count else scan)),
        ("All bodies found", "yes" if survey.fss_complete else "no"),
        ("Bodies described", f"{survey.scanned_count()} scanned" + (f", {survey.known_count()} more from EDSM" if survey.known_count() else "")),
        ("Planets", f"{len(_planets(survey))} seen, {survey.mapped_count()} mapped, {sums['landable']} landable"),
        ("Terraformable", str(sums["terraformable"])),
        ("Biology", f"{sums['bio_bodies']} bodies with life signals" if sums["bio_bodies"] else "none found yet"),
        ("Geology", f"{sums['geo_bodies']} bodies with geological signals" if sums["geo_bodies"] else "none found yet"),
        ("First footfall", f"{sums['first_footfalls']} landable bodies nobody has landed on" if sums["first_footfalls"] else "none known"),
    ]
    if survey.sites_status == "looking":
        rows.append(("Others' finds (Spansh)", "looking..."))
    elif survey.sites:
        rows.append(("Others' finds (Spansh)", f"{len(survey.sites)} bodies listed"))
    if progress_text:
        rows.append(("Panel readout", progress_text))
    return rows


# --- the bodies table ---------------------------------------------------------------------------------------------------------

BODY_COLUMNS: Tuple[Tuple[str, str, int, str], ...] = (
    ("name", "Body", 120, "w"), ("type", "Type", 190, "w"), ("tag", "", 48, "w"), ("dist", "Distance", 90, "e"), ("grav", "Gravity", 74, "e"),
    ("land", "Landable", 74, "center"), ("atmo", "Atmosphere", 170, "w"), ("temp", "Temp", 70, "e"), ("scan", "Scan value", 90, "e"),
    ("mapv", "Mapped value", 100, "e"), ("bio", "Bio", 44, "e"), ("geo", "Geo", 44, "e"), ("state", "Status", 190, "w"),
)


def body_type(body: Body) -> str:
    if body.kind == "star":
        return f"Star {body.star_type}".strip()
    return body.planet_class or "Planet"


def body_state(body: Body) -> str:
    """What has been done with the body, as short words."""
    parts: List[str] = []
    if body.scanned:
        parts.append("scanned")
    elif body.known:
        parts.append("known (EDSM)")
    else:
        parts.append("not scanned")
    if body.mapped:
        parts.append("mapped")
    if body.was_discovered is False:
        parts.append("first discovery")
    if body.first_footfall:
        parts.append("first footfall")
    if body.life_done:
        parts.append("life done")
    return ", ".join(parts)


def body_tag(body: Body, threshold: int, basis: str) -> str:
    """The row color: what to do with this body."""
    if body.finished and body.scanned:
        return "done"
    if body.bio > 0 and not body.life_done:
        return "life"
    value = body.mapped_value() if basis == "mapped" else body.scan_value()
    if body.kind == "planet" and not body.mapped and (body.scanned or body.known) and value >= threshold:
        return "map"
    return ""


def body_row(body: Body, threshold: int = 0, basis: str = "scan") -> Row:
    atmosphere = body.atmosphere.replace(" atmosphere", "") if body.atmosphere else DASH
    return Row(str(body.body_id), [
        body.short or body.name, body_type(body), body.tag, light_seconds(body.distance_ls), num(body.gravity_g, 2, " g"),
        "yes" if body.landable else "", atmosphere, num(body.temperature_k, 0, " K"), credits(body.scan_value()), credits(body.mapped_value()),
        str(body.bio) if body.bio else "", str(body.geo) if body.geo else "", body_state(body)], body_tag(body, threshold, basis))


def bodies_table(survey: SystemSurvey, threshold: int = 0, basis: str = "scan") -> Table:
    bodies = sorted(survey.bodies.values(), key=lambda b: (b.distance_ls if b.distance_ls is not None else 1e18, b.body_id))
    return Table(BODY_COLUMNS, [body_row(b, threshold, basis) for b in bodies], "No bodies yet: honk, then scan.")


# --- one body in detail -------------------------------------------------------------------------------------------------------

def body_sections(body: Optional[Body]) -> List[Tuple[str, Fields]]:
    """Everything known about one body, in blocks."""
    if body is None:
        return [("Body", [("", "Nothing selected")])]
    physical: Fields = [("Name", body.name), ("Type", body_type(body))]
    if body.kind == "star":
        physical += [("Stellar mass", num(body.stellar_mass, 2, " solar masses")), ("Distance from arrival", light_seconds(body.distance_ls))]
    else:
        physical += [("Distance from arrival", light_seconds(body.distance_ls)), ("Mass", num(body.mass_em, 3, " Earth masses")), ("Gravity", num(body.gravity_g, 2, " g")),
                     ("Surface temperature", num(body.temperature_k, 0, " K")), ("Surface pressure", num(body.pressure_atm, 3, " atm") if body.pressure_atm else DASH),
                     ("Landable", "yes" if body.landable else "no"), ("Terraformable", "yes" if body.terraformable else "no")]
    blocks: List[Tuple[str, Fields]] = [("Body", physical)]
    if body.kind != "star":
        air: Fields = [("Atmosphere", body.atmosphere or "none")]
        air += [(gas, f"{percent:.1f}%") for gas, percent in body.atmosphere_parts]
        air.append(("Volcanism", body.volcanism or "none"))
        blocks.append(("Atmosphere and volcanism", air))
        if body.materials:
            blocks.append(("Materials", [(name, f"{percent:.1f}%") for name, percent in sorted(body.materials, key=lambda m: -m[1])]))
    status: Fields = [("State", body_state(body)), ("Scan value (estimate)", credits(body.scan_value())), ("Mapped value (estimate)", credits(body.mapped_value()))]
    if body.bio or body.geo:
        status.append(("Signals", f"{body.bio} biological, {body.geo} geological"))
    if body.genuses:
        status.append(("Genera", ", ".join(body.genuses)))
    if body.analyzed:
        status.append(("Analyzed", ", ".join(sorted(set(body.analyzed)))))
    if body.sampling:
        status.append(("Sampling now", body.sampling))
    blocks.append(("Value and progress", status))
    return blocks


# --- the to-do lists ----------------------------------------------------------------------------------------------------------

MAP_COLUMNS = (("name", "Body", 120, "w"), ("type", "Type", 190, "w"), ("dist", "Distance", 90, "e"), ("scan", "Scan", 90, "e"), ("mapv", "If mapped", 100, "e"),
               ("note", "Note", 160, "w"))
LIFE_COLUMNS = (("name", "Body", 120, "w"), ("type", "Type", 190, "w"), ("bio", "Signals", 70, "e"), ("done", "Analyzed", 80, "e"), ("genera", "Genera", 260, "w"),
                ("note", "Note", 160, "w"))
SITE_COLUMNS = (("name", "Body", 120, "w"), ("type", "Type", 190, "w"), ("dist", "Distance", 90, "e"), ("bio", "Biology", 100, "e"), ("what", "What is there", 320, "w"))


def map_table(survey: SystemSurvey, threshold: int, basis: str) -> Table:
    rows = []
    for body in survey.to_map(threshold, basis):
        note = "first discovery" if body.was_discovered is False else ("first footfall" if body.first_footfall else "")
        rows.append(Row(str(body.body_id), [body.short or body.name, body_type(body), light_seconds(body.distance_ls), credits(body.scan_value()),
                                            credits(body.mapped_value()), note]))
    empty = "Nothing scanned is worth mapping yet." if survey.scanned_count() else "Scan some bodies first."
    return Table(MAP_COLUMNS, rows, empty)


def life_table(survey: SystemSurvey) -> Table:
    rows = []
    for body in survey.with_life():
        note = "first footfall (5x)" if body.first_footfall else ("sampling " + body.sampling if body.sampling else "")
        rows.append(Row(str(body.body_id), [body.short or body.name, body_type(body), str(body.bio), str(len(set(body.analyzed))),
                                            ", ".join(body.genuses) or "map it to learn the genera", note], "life"))
    return Table(LIFE_COLUMNS, rows, "No unfinished biology found yet.")


def sites_table(survey: SystemSurvey) -> Table:
    rows = []
    for site in survey.sites:
        pois = ", ".join(f"{count}x {what}" if count > 1 else what for what, count in site.pois)
        species = ", ".join(name for name, _count, _value in site.species[:4])
        rows.append(Row(site.name, [site.short or site.name, site.subtype or DASH, light_seconds(site.distance_ls), credits(site.bio_value),
                                    "; ".join(part for part in (species, pois) if part) or DASH]))
    return Table(SITE_COLUMNS, rows, "Switch on the Spansh lookup in Settings -> Overlays -> System targets to see what others found.")


# --- exobiology on the ground -------------------------------------------------------------------------------------------------

GENUS_COLUMNS = (("genus", "Genus", 130, "w"), ("species", "Species / color", 230, "w"), ("stage", "Progress", 130, "w"), ("value", "Pays", 130, "e"),
                 ("odds", "Could be", 330, "w"), ("dist", "From last sample", 130, "e"))
WAYPOINT_COLUMNS = (("name", "Specimen", 230, "w"), ("dist", "Distance", 90, "e"), ("dir", "Direction", 150, "w"), ("how", "Seen from", 90, "w"))


def _progress_word(genus: organic_scan.GenusView) -> str:
    """"Collecting: 1/3" while a species is being sampled (the Log, Sample and Analyse scans make three), "Analyzed: 3/3" once it is paid out."""
    needed = organic_scan.REQUIRED_SAMPLES
    done = max(0, min(genus.stage, needed))
    return f"Analyzed: {done}/{needed}" if genus.complete else f"Collecting: {done}/{needed}"


def _value_text(genus: organic_scan.GenusView, multiplier: int) -> str:
    span = genus.value_range
    if span is None:
        return DASH
    low, high = span[0] * multiplier, span[1] * multiplier
    return credits(low) if low == high else f"{credits(low)} to {credits(high)}"


def genus_row(genus: organic_scan.GenusView, multiplier: int = 1) -> Row:
    if genus.species:
        what = genus.species + (f" ({genus.variant})" if genus.variant and genus.variant != genus.species else "")
        odds = "confirmed"
    else:
        what = genus.variant_hint and f"{genus.name} ({genus.variant_hint})" or genus.name
        odds = "; ".join(f"{name} {credits(value * multiplier)} ({share}%)" for name, value, share in genus.odds()) or "no candidates known"
    if genus.distance_m is None:
        far = DASH
    else:
        far = f"{meters(genus.distance_m)} of {meters(genus.min_distance_m)}"
    return Row(genus.key, [genus.name, what, _progress_word(genus), _value_text(genus, multiplier), odds, far],
               "done" if genus.complete else ("life" if genus.stage else ""))


def genus_table(view: Optional[organic_scan.BodyView]) -> Table:
    if view is None:
        return Table(GENUS_COLUMNS, [], "No biology on the body you are at (or it has not been scanned and mapped).")
    return Table(GENUS_COLUMNS, [genus_row(g, view.multiplier) for g in view.genera], "No genera named yet: map the body, or scan a specimen with the Composition Scanner.")


def exo_fields(view: Optional[organic_scan.BodyView]) -> Fields:
    if view is None:
        return [("Exobiology", "no biology on this body")]
    rows: Fields = [("Body", view.body_name), ("Genera", f"{len(view.genera)} named" + (f" of {view.signal_count} signals" if view.signal_count else "")),
                    ("Analyzed", f"{view.analyzed} of {len(view.genera)}"), ("Progress", f"{view.progress * 100:.0f}%")]
    if view.reward_range is not None:
        low, high = view.reward_range[0] * view.multiplier, view.reward_range[1] * view.multiplier
        rows.append(("Could pay", credits(low) if low == high else f"{credits(low)} to {credits(high)}"))
    if view.first_footfall:
        rows.append(("First footfall", f"nobody has landed here: every reward is {view.multiplier}x"))
    if not view.mapped:
        rows.append(("Note", "not mapped: the genera are known only from the signal count"))
    active = view.active_genus
    if active is not None:
        rows.append(("Sampling now", f"{active.title}, {_progress_word(active)}"))
        if active.distance_m is not None and active.distance_m < active.min_distance_m:
            rows.append(("Next sample", f"walk {meters(active.min_distance_m - active.distance_m)} further from the last one"))
        elif active.distance_m is not None:
            rows.append(("Next sample", "far enough from the last one"))
    return rows


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """The initial compass bearing from point 1 to point 2, 0 to 360 degrees."""
    p1, p2, d_lon = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(d_lon) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(d_lon)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def direction_text(relative: float) -> str:
    """A bearing relative to the heading (-180 to 180) as words."""
    r = (relative + 180.0) % 360.0 - 180.0
    if abs(r) <= 15:
        return "ahead"
    if abs(r) >= 165:
        return "behind"
    side = "right" if r > 0 else "left"
    return f"{abs(r):.0f} degrees {side}"


def waypoint_table(view: Optional[organic_scan.BodyView]) -> Table:
    rows = []
    if view is not None and view.here is not None and view.radius_m:
        for index, point in enumerate(view.waypoints):
            distance = organic_scan.haversine_distance_m(view.here[0], view.here[1], point.lat, point.lon, view.radius_m)
            heading = view.heading if view.heading is not None else 0.0
            facing = direction_text(bearing_deg(view.here[0], view.here[1], point.lat, point.lon) - heading) if view.heading is not None else DASH
            rows.append(Row(str(index), [point.name, ("~" if not point.exact else "") + meters(distance), facing, point.mode or DASH]))
    return Table(WAYPOINT_COLUMNS, rows, "No specimens being tracked: scan one with the Composition Scanner.")


def vehicle_fields(view: Optional[organic_scan.BodyView]) -> Fields:
    """Where the ship and the SRV are relative to the commander on the ground."""
    rows: Fields = []
    if view is None or view.here is None or not view.radius_m:
        return rows
    for label, spot in (("Ship", view.ship), ("SRV", view.srv)):
        if spot is not None:
            rows.append((label, meters(organic_scan.haversine_distance_m(view.here[0], view.here[1], spot[0], spot[1], view.radius_m)) + " away"))
    return rows


# --- the exploration so far ---------------------------------------------------------------------------------------------------

def expedition_fields(run: Optional[expedition_log.Run], now: Optional[float] = None) -> Fields:
    """The running expedition, or why there is none."""
    if run is None:
        return [("Expedition", "none running: START one in the Expedition Log on the Exploration panel")]
    t = run.totals
    return [
        ("Expedition", run.name), ("Time", expedition_log.duration_text(run.elapsed(now))), ("Started in", run.start_system or DASH),
        ("Systems", f"{len(run.systems):,}"), ("Jumps", f"{t.jumps:,}"), ("Distance", f"{t.light_years:,.0f} ly"), ("Honks", f"{t.honks:,}"),
        ("Bodies scanned", f"{t.bodies_scanned:,} ({t.stars:,} stars, {t.planets:,} planets)"), ("First discoveries", f"{t.first_discoveries:,}"),
        ("Mapped", f"{t.mapped:,} ({t.first_mapped:,} first maps)"),
        ("Notable", f"{t.earth_likes:,} Earth-likes, {t.water_worlds:,} water worlds, {t.ammonia_worlds:,} ammonia worlds, {t.terraformables:,} terraformables"),
        ("Landings", f"{t.landings:,}"), ("Codex entries", f"{t.codex_new:,} new"),
        ("Exobiology", f"{t.bio_samples:,} samples, {t.bio_species:,} species analyzed, {t.bio_first_footfalls:,} first footfalls"),
        ("Earned", f"{expedition_log.short_credits(t.earned)} ({expedition_log.short_credits(t.explore_earned)} exploration, {expedition_log.short_credits(t.bio_earned)} exobiology)"),
        ("Unsold (estimate)", expedition_log.short_credits(t.explore_estimated + t.bio_estimated)),
    ]


def route_fields(lines: Sequence[Tuple[str, str]]) -> Fields:
    """The Route overlay's status lines (fuel, range, jumps left) as fields."""
    if not lines:
        return [("Route", "no route plotted")]
    return [("", text) for text, _role in lines]


def readout_fields(progress_text: str, sales_text: str) -> Fields:
    rows: Fields = []
    if progress_text:
        rows.append(("This system", progress_text))
    if sales_text:
        rows.append(("Sales", sales_text))
    return rows
