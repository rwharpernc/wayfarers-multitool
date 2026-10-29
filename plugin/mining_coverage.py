"""
Tracks ground the Rhino's scanner has driven over, per body, for the
Surface Mining page's coverage minimap (mining_coverage_render.py draws
the actual picture - this module is pure geometry/persistence, no PIL,
no tkinter).

"Painted" means driven within scanner range of a point, not scanned -
nothing the journal or Status.json says means a scan happened, so this
can't and doesn't claim to track real surface-scan coverage, only where
the Rhino has been. The design is deliberately simple: paint a disc of
SCAN_RADIUS_M at each recorded point rather than trying to reconstruct
the SRV's exact path.

Fed from mining_panel.py's dashboard_status() (Status.json's live
Latitude/Longitude via mining_live_position.py) whenever
mining_surface.surface_mining_repository.is_active is true - i.e. a
Rhino is actually deployed - and a body radius is known (also read off
mining_surface.py). Not fed from journal events: like
mining_live_position.py itself, this needs Status.json's
once-a-second telemetry, not discrete journal lines.
"""
from __future__ import annotations

import logging
import os
import math
from dataclasses import asdict, dataclass, field
from typing import Optional

try:
    from config import appname
except ImportError:  # pragma: no cover - real EDMC runtime always provides this
    appname = "EDMarketConnector"

from . import commander_data
from . import mining_bearing as bearing

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

COVERAGE_FILENAME = "mining_coverage.json"
"""Not committed to git and not part of any release build - the
commander's own drive history, same reasoning as mining_hotspots.py's
HOTSPOTS_FILENAME. One file, a separate map per commander
(commander_data.py)."""

SCAN_RADIUS_M = 2000.0
"""What the Rhino's scanner sees from wherever it's standing, in
meters - a community figure (Frontier hasn't published one)."""

STAMP_M = 250.0
"""Minimum distance from the last recorded point before a new one is
added - a straight line of stamped discs SCAN_RADIUS_M wide doesn't
need a point every meter driven to look continuous once rendered."""

MAX_POINTS_PER_BODY = 2000
"""Keeps a body's coverage file bounded across a long session's driving
- same "keep history bounded" reasoning as store.py's MAX_HISTORY.
Oldest points are dropped first once this is hit; losing the very
first stamps of a long-since-covered area matters far less than losing
recent ones."""


@dataclass
class CoveragePoint:
    latitude: float
    longitude: float


SAME_SITE_M = 100.0
"""Pressing Mark center within this distance of a marked center moves that center instead of starting another site (the same reasoning as a hotspot saved again at a spot)."""

MAX_SITES_PER_BODY = 12
EDGE_SAMPLES = 72
"""How many points around a marked border are checked against the ground driven, to say how much of the edge has been covered."""


@dataclass
class Site:
    """One mining location (the circle a surface mining signal covers) marked by the commander: the center, and a point on its border once marked. The journal gives neither, so
    both are where the commander stood when pressing Mark center and Mark border, and the radius is the distance between them."""
    center: CoveragePoint
    border: Optional[CoveragePoint] = None

    def radius_m(self, body_radius_m: float) -> Optional[float]:
        if self.border is None:
            return None
        return bearing.distance_m(self.center.latitude, self.center.longitude, self.border.latitude, self.border.longitude, body_radius_m)


def point_at(center: CoveragePoint, bearing_deg: float, distance_m: float, body_radius_m: float) -> CoveragePoint:
    """The latitude and longitude `distance_m` from `center` along `bearing_deg` (great circle)."""
    lat1, lon1, theta, delta = math.radians(center.latitude), math.radians(center.longitude), math.radians(bearing_deg), distance_m / body_radius_m
    lat2 = math.asin(math.sin(lat1) * math.cos(delta) + math.cos(lat1) * math.sin(delta) * math.cos(theta))
    lon2 = lon1 + math.atan2(math.sin(theta) * math.sin(delta) * math.cos(lat1), math.cos(delta) - math.sin(lat1) * math.sin(lat2))
    return CoveragePoint(math.degrees(lat2), (math.degrees(lon2) + 540.0) % 360.0 - 180.0)


@dataclass
class BodyCoverage:
    """One body's drive history. `center` is the first point ever
    recorded for this body - fixed for the body's lifetime so the map
    doesn't re-anchor (and silently discard the visual relationship
    between old and new points) every time coverage is rendered."""
    center: Optional[CoveragePoint] = None
    points: list[CoveragePoint] = field(default_factory=list)
    sites: list[Site] = field(default_factory=list)

    def nearest_site(self, latitude: float, longitude: float, radius_m: float) -> Optional[tuple[Site, float]]:
        """The marked site whose center is nearest, with that distance in meters."""
        best: Optional[tuple[Site, float]] = None
        for site in self.sites:
            distance = bearing.distance_m(site.center.latitude, site.center.longitude, latitude, longitude, radius_m)
            if best is None or distance < best[1]:
                best = (site, distance)
        return best

    def mark_center(self, latitude: float, longitude: float, radius_m: float) -> str:
        """Mark center: a new site centered here, or the nearby site's center moved here. Returns what was done, for the panel to say."""
        near = self.nearest_site(latitude, longitude, radius_m)
        if near is not None and near[1] <= SAME_SITE_M:
            near[0].center = CoveragePoint(latitude, longitude)
            return "Center moved."
        self.sites.append(Site(CoveragePoint(latitude, longitude)))
        if len(self.sites) > MAX_SITES_PER_BODY:
            del self.sites[: len(self.sites) - MAX_SITES_PER_BODY]
        return "Center marked. Drive to the edge of the signal and press Mark border."

    def mark_border(self, latitude: float, longitude: float, radius_m: float) -> str:
        """Mark border: the border of the nearest site, whose radius is then the distance to it."""
        near = self.nearest_site(latitude, longitude, radius_m)
        if near is None:
            return "No center marked on this body yet: stand at the middle of the signal and press Mark center first."
        site, distance = near
        if distance < SAME_SITE_M:
            return f"You are only {distance:,.0f} m from the center. Drive to the edge of the signal and press Mark border there."
        site.border = CoveragePoint(latitude, longitude)
        return f"Border marked: the signal is {distance / 1000:.2f} km in radius."

    def inside(self, site: Site, latitude: float, longitude: float, body_radius_m: float) -> Optional[tuple[bool, float]]:
        """Whether the point is inside the site's marked circle and by how many meters from its edge (to the edge from inside, past it from outside); None until the border is marked."""
        radius = site.radius_m(body_radius_m)
        if radius is None:
            return None
        distance = bearing.distance_m(site.center.latitude, site.center.longitude, latitude, longitude, body_radius_m)
        return distance <= radius, abs(radius - distance)

    def edge_covered(self, site: Site, body_radius_m: float, reach_m: float = SCAN_RADIUS_M) -> Optional[float]:
        """The share (0 to 1) of the site's border circle within `reach_m` of ground driven; None until the border is marked."""
        radius = site.radius_m(body_radius_m)
        if radius is None or not radius:
            return None
        if not self.points:
            return 0.0
        covered = 0
        for step in range(EDGE_SAMPLES):
            spot = point_at(site.center, step * 360.0 / EDGE_SAMPLES, radius, body_radius_m)
            if any(bearing.distance_m(p.latitude, p.longitude, spot.latitude, spot.longitude, body_radius_m) <= reach_m for p in self.points):
                covered += 1
        return covered / EDGE_SAMPLES

    def record(self, latitude: float, longitude: float, radius_m: float) -> bool:
        """Adds a point if it's at least STAMP_M from the last one
        recorded (or if this is the first point for the body, which
        also sets `center`). Returns whether a point was actually
        added, so the caller only re-renders/saves on real change."""
        if self.center is None:
            self.center = CoveragePoint(latitude, longitude)
            self.points.append(CoveragePoint(latitude, longitude))
            return True
        if self.points:
            last = self.points[-1]
            if bearing.distance_m(last.latitude, last.longitude, latitude, longitude, radius_m) < STAMP_M:
                return False
        self.points.append(CoveragePoint(latitude, longitude))
        if len(self.points) > MAX_POINTS_PER_BODY:
            del self.points[: len(self.points) - MAX_POINTS_PER_BODY]
        return True


class CoverageRepository:
    """Constructed empty, `load(plugin_dir)` called once from
    mining_panel.start() - same convention as
    mining_hotspots.HotspotRepository."""

    def __init__(self) -> None:
        self._by_body: dict[str, BodyCoverage] = {}   # the current commander's; empty until one is known
        self._plugin_dir: Optional[str] = None
        self._store = commander_data.new_store()
        self._cmdr = ""
        self.last_message = ""                         # what Mark center or Mark border last did, shown on the Surface page until the next press

    def load(self, plugin_dir: str) -> None:
        """Read the file. Nothing is shown until `set_commander` says whose map to use. A file written before coverage
        was per commander is claimed by the first commander seen."""
        self._plugin_dir = plugin_dir
        path = os.path.join(plugin_dir, COVERAGE_FILENAME)
        try:
            self._store = commander_data.read(path, is_legacy=lambda raw: isinstance(raw, dict))
        except Exception:
            logger.exception("Failed to load %s - starting with no recorded coverage", COVERAGE_FILENAME)
            self._store = commander_data.new_store()

    def set_commander(self, cmdr: str) -> None:
        """Switch to this commander's recorded ground (the previous commander's is already saved)."""
        key = commander_data.key_for(cmdr)
        if not key or key == commander_data.key_for(self._cmdr):
            return
        self._cmdr = str(cmdr).strip()
        claimed = not commander_data.known(self._store, cmdr) and self._store.get("legacy") is not None
        try:
            raw = commander_data.payload_for(self._store, cmdr, dict)
            self._by_body = {
                body_key: BodyCoverage(
                    center=CoveragePoint(**entry["center"]) if entry.get("center") else None,
                    points=[CoveragePoint(**p) for p in entry.get("points", [])],
                    sites=[Site(CoveragePoint(**s["center"]), CoveragePoint(**s["border"]) if s.get("border") else None)
                           for s in entry.get("sites", []) if isinstance(s, dict) and s.get("center")],
                )
                for body_key, entry in raw.items()
            }
        except Exception:
            logger.exception("Failed to read %s's coverage - starting with none", cmdr)
            self._by_body = {}
        if claimed:
            self._save()

    @staticmethod
    def _key(system: str, body: str) -> str:
        return f"{system.strip().casefold()}|{body.strip().casefold()}"

    def for_body(self, system: Optional[str], body: Optional[str]) -> Optional[BodyCoverage]:
        if not system or not body:
            return None
        return self._by_body.get(self._key(system, body))

    def record(self, system: str, body: str, latitude: float, longitude: float, radius_m: float) -> None:
        if not system or not body:
            return
        key = self._key(system, body)
        coverage = self._by_body.setdefault(key, BodyCoverage())
        if coverage.record(latitude, longitude, radius_m):
            self._save()

    def mark(self, system: str, body: str, latitude: float, longitude: float, radius_m: float, border: bool) -> str:
        """Mark center (`border` False) or Mark border (True) at this position; saved. Says what was done, or why not."""
        if not system or not body or not radius_m:
            return "WFMT does not know the body yet: land first."
        coverage = self._by_body.setdefault(self._key(system, body), BodyCoverage())
        message = coverage.mark_border(latitude, longitude, radius_m) if border else coverage.mark_center(latitude, longitude, radius_m)
        self._save()
        self.last_message = message
        return message

    def clear_body(self, system: str, body: str) -> None:
        """Drops all recorded coverage for one body - a safety valve for
        a commander who wants a fresh map (e.g. after driving somewhere
        irrelevant by mistake), cheap to provide given the
        JSON-file-per-repository storage every other WFMT feature already
        uses."""
        if self._by_body.pop(self._key(system, body), None) is not None:
            self._save()

    def _save(self) -> None:
        if self._plugin_dir is None or not self._cmdr:
            return
        try:
            path = os.path.join(self._plugin_dir, COVERAGE_FILENAME)
            payload = {
                key: {
                    "center": asdict(coverage.center) if coverage.center else None,
                    "points": [asdict(p) for p in coverage.points],
                    "sites": [asdict(s) for s in coverage.sites],
                }
                for key, coverage in self._by_body.items()
            }
            commander_data.put(self._store, self._cmdr, payload)
            commander_data.write(path, self._store)
        except Exception:
            logger.exception("Failed to save %s", COVERAGE_FILENAME)


coverage_repository = CoverageRepository()
