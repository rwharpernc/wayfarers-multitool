"""The Surface radar's picture, from the Mining data: one recipe for the Live window and for the radar card over the game, so they always show the same thing.

`context` gathers what a radar needs from a `mining_sources.Sources` (the Rhino's position, the body's size, the ground driven, the saved deposits), `extras` works out the drive rings, the stops
and the target material, and `render` draws it with `mining_coverage_render.render_radar`. Pure of Tk and of any overlay; the callers decide where the picture goes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from config import config

from . import mining_alerts
from . import mining_bearing as bearing
from . import mining_coverage as coverage
from . import mining_coverage_render as radar
from . import mining_drive_rings
from . import mining_live_position as live_position
from . import mining_sources
from . import mining_stops

CONFIG_STOP_RADIUS = "wfmt_mining_stop_radius_m"
"""Settings > Mining: also read by the Mining Book."""
CONFIG_RIG_GAP = "wfmt_mining_rig_gap_m"
"""Settings > Mining: how close two rigs may be, which the bands round placed rigs show."""
CONFIG_RANGE = "wfmt_mining_live_radar_range_m"
"""How far the radar reaches (50 m to 2 km), shared by the Live window and the radar card over the game, so one range choice steps both."""


def saved_range() -> float:
    """The radar's range in meters from Settings storage, one of `radar.RADAR_RANGES_M`; the default for anything else."""
    try:
        value = float(config.get_int(CONFIG_RANGE, default=int(radar.DEFAULT_RADAR_RANGE_M)))
    except (TypeError, ValueError):
        return radar.DEFAULT_RADAR_RANGE_M
    return value if value in radar.RADAR_RANGES_M else radar.DEFAULT_RADAR_RANGE_M


@dataclass(frozen=True)
class Context:
    position: live_position.LivePosition
    body_radius_m: float
    system: Optional[str]
    body: Optional[str]
    body_coverage: Optional[coverage.BodyCoverage]
    saved: list
    rigs: tuple = ()
    rig_gap_m: int = 0


def context(src: mining_sources.Sources) -> Optional[Context]:
    """What a radar is drawn from, or None while there is no position or the body's size is not known (the radar then has nothing to show)."""
    repo = src.surface
    position = src.position()
    body_radius = repo.radius_for_current_body() or (position.planet_radius if position else None)
    if position is None or not body_radius:
        return None
    gap = src.rig_gap_override if src.rig_gap_override is not None else mining_stops.clamp_rig_gap(config.get_int(CONFIG_RIG_GAP, default=0))
    return Context(position, body_radius, repo.current_system, repo.current_body, src.coverage.for_body(repo.current_system, repo.current_body),
                   src.hotspots.for_body(repo.current_system, repo.current_body),
                   tuple(coverage.CoveragePoint(r.latitude, r.longitude) for r in src.rigs.rigs_for(repo.current_system, repo.current_body)), int(gap))


def extras(ctx: Context, with_target: bool = True) -> radar.RadarExtras:
    """The rings to drive round the nearest marked location, the stops worth parking at and the material to guide to."""
    drive_center, radii = None, ()
    near = ctx.body_coverage.nearest_site(ctx.position.latitude, ctx.position.longitude, ctx.body_radius_m) if ctx.body_coverage else None
    if near is not None:
        site = near[0]
        driven = max((bearing.distance_m(site.center.latitude, site.center.longitude, p.latitude, p.longitude, ctx.body_radius_m) for p in ctx.body_coverage.points), default=0.0)
        drive_center, radii = site.center, mining_drive_rings.ring_radii(site.radius_m(ctx.body_radius_m), driven_m=driven)
    stop_radius = mining_stops.clamp_radius(config.get_int(CONFIG_STOP_RADIUS, default=mining_stops.DEFAULT_RADIUS_M))
    best = mining_stops.best_stops(mining_stops.find_stops(ctx.saved, ctx.body_radius_m, stop_radius))
    stops = tuple((coverage.CoveragePoint(stop.lead.latitude, stop.lead.longitude), float(stop_radius), f"Stop {number}") for number, stop in enumerate(best, 1))
    return radar.RadarExtras(drive_center=drive_center, drive_radii_m=radii, stops=stops, target_material=mining_alerts.primary_target() if with_target else "",
                             rigs=ctx.rigs, rig_gap_m=float(ctx.rig_gap_m))


def render(src: mining_sources.Sources, size_px: int, range_m: float) -> Optional[Image.Image]:
    """The radar centered on the Rhino, `size_px` square and reaching `range_m` from the middle to the edge; None while there is nothing to draw it from."""
    ctx = context(src)
    if ctx is None:
        return None
    return radar.render_radar(ctx.body_coverage, ctx.body_radius_m, coverage.CoveragePoint(ctx.position.latitude, ctx.position.longitude), ctx.position.heading, ctx.saved,
                              size_px, range_m, extras(ctx))
