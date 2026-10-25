"""
Draws mining_coverage.py's recorded drive history as a small top-down
map: PIL only, no tkinter (mining_render.py/mining_panel.py turn the
result into a tk.PhotoImage for the Surface Mining page - see
to_photo_data() below, which follows screenshot_convert.py's own
thumbnail_photo_data() pattern exactly, including capping *both*
dimensions per the main-window-sizing rule (docs/TECHNICAL.md section 5), even
though MAP_SIZE_PX already makes the canvas an exact fixed square by
construction - the extra thumbnail() call is a deliberate belt-and-
suspenders match to that convention, not dead code).

Flat-earth projection via mining_bearing's own haversine distance/
bearing from the body's recorded center point: accurate enough at the
VIEW_M scale this map shows (a few km), same reasoning
mining_bearing.py itself already uses for the waypoint arrow.

Deliberately small in scope: no lines joining hotspots,
no clustering, no hotkeys to move the map's center (the live window's radar, `render_radar`, is the bigger, zoomable picture). It paints driven
ground, shows recorded hotspots and the current position, north up, at a
fixed size.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFont

from . import mining_bearing as bearing
from . import mining_coverage as coverage
from . import mining_hotspots as hotspots

MAP_SIZE_PX = 220
"""Both dimensions - a fixed square, never derived from source data, so
this can never be the widget that widens EDMC's main window (see
docs/TECHNICAL.md section 5)."""

VIEW_M = 6000.0
"""Half-width of what the map shows around its center - 12 km across
total."""

GRID_M = 1000.0

_BG_COLOR = (40, 40, 40)
_GRID_COLOR = (64, 64, 64)
_COVERAGE_COLOR = (46, 92, 58)
_HOTSPOT_COLOR = (238, 232, 190)
_DEPLETED_COLOR = (150, 150, 150)
_SITE_COLOR = (255, 196, 64)
_POSITION_COLOR = (70, 170, 255)
_POSITION_OUTLINE = (255, 255, 255)
_POSITION_RADIUS_PX = 4
# Colors chosen to stay distinguishable without telling red from green
# (deliberately): a live hotspot is a pale
# filled dot, a depleted one a hollow gray ring - shape, not hue, carries
# the state - and the position marker is blue with a white outline (it
# used to be red on green coverage).


def _project(center: coverage.CoveragePoint, latitude: float, longitude: float,
             radius_m: float, scale_px_per_m: float) -> tuple[float, float]:
    """A lat/lon point -> (x, y) pixel offset from the map's center,
    north up (smaller y = further north)."""
    distance = bearing.distance_m(center.latitude, center.longitude, latitude, longitude, radius_m)
    initial_bearing = math.radians(bearing.initial_bearing_deg(
        center.latitude, center.longitude, latitude, longitude))
    east_m = distance * math.sin(initial_bearing)
    north_m = distance * math.cos(initial_bearing)
    half = MAP_SIZE_PX / 2
    return half + east_m * scale_px_per_m, half - north_m * scale_px_per_m


def render(body_coverage: Optional[coverage.BodyCoverage], radius_m: Optional[float],
          current: Optional[coverage.CoveragePoint],
          known_hotspots: list[hotspots.Hotspot]) -> Optional[Image.Image]:
    """None when there's nothing to draw yet - no coverage recorded for
    this body and no live position either - so the caller can show
    nothing rather than a blank gray square."""
    center = body_coverage.center if body_coverage else None
    if center is None and body_coverage and body_coverage.sites:
        center = body_coverage.sites[0].center
    if center is None:
        center = current
    if center is None or not radius_m:
        return None

    scale = MAP_SIZE_PX / (2 * VIEW_M)
    image = Image.new("RGB", (MAP_SIZE_PX, MAP_SIZE_PX), _BG_COLOR)
    draw = ImageDraw.Draw(image)

    # Grid, pinned to the map's center so it reads as "north up" rather
    # than tied to any single recorded point. Walks outward from the
    # center in both directions at once so it stays symmetric regardless
    # of MAP_SIZE_PX's parity.
    step_px = GRID_M * scale
    half_px = MAP_SIZE_PX / 2
    if step_px >= 4:  # a grid finer than a few px just reads as noise
        offset = 0.0
        while offset <= half_px:
            for coordinate in {half_px + offset, half_px - offset}:
                draw.line([(coordinate, 0), (coordinate, MAP_SIZE_PX)], fill=_GRID_COLOR)
                draw.line([(0, coordinate), (MAP_SIZE_PX, coordinate)], fill=_GRID_COLOR)
            offset += step_px

    # Painted ground: a disc per recorded point.
    scan_radius_px = coverage.SCAN_RADIUS_M * scale
    for point in (body_coverage.points if body_coverage else ()):
        px, py = _project(center, point.latitude, point.longitude, radius_m, scale)
        draw.ellipse([px - scan_radius_px, py - scan_radius_px,
                     px + scan_radius_px, py + scan_radius_px], fill=_COVERAGE_COLOR)

    # The mining locations the commander marked: a cross at the center and, once the border is marked, the circle through it (a ring, so the shape is clear without a color).
    for site in (body_coverage.sites if body_coverage else ()):
        cx, cy = _project(center, site.center.latitude, site.center.longitude, radius_m, scale)
        arm = 4
        draw.line([(cx - arm, cy), (cx + arm, cy)], fill=_SITE_COLOR, width=1)
        draw.line([(cx, cy - arm), (cx, cy + arm)], fill=_SITE_COLOR, width=1)
        site_radius = site.radius_m(radius_m)
        if site_radius:
            reach = site_radius * scale
            draw.ellipse([cx - reach, cy - reach, cx + reach, cy + reach], outline=_SITE_COLOR, width=1)

    # Recorded hotspots on this body, if within view.
    for hotspot in known_hotspots:
        if not hotspot.has_position():
            continue
        px, py = _project(center, hotspot.latitude, hotspot.longitude, radius_m, scale)
        if 0 <= px <= MAP_SIZE_PX and 0 <= py <= MAP_SIZE_PX:
            r = 3
            box = [px - r, py - r, px + r, py + r]
            if hotspot.amount == "Depleted":
                draw.ellipse(box, outline=_DEPLETED_COLOR, width=1)
            else:
                draw.ellipse(box, fill=_HOTSPOT_COLOR)

    # The Rhino's current position, drawn last so it's never hidden
    # under a coverage disc.
    if current is not None:
        px, py = _project(center, current.latitude, current.longitude, radius_m, scale)
        r = _POSITION_RADIUS_PX
        draw.ellipse([px - r, py - r, px + r, py + r], fill=_POSITION_COLOR,
                     outline=_POSITION_OUTLINE)

    return image


RADAR_RANGES_M = (50.0, 250.0, 500.0, 1000.0, 2000.0)
"""The distances from the center to the edge of the radar the live window offers, in meters (its zoom levels)."""
DEFAULT_RADAR_RANGE_M = 2000.0
_RADAR_RINGS = 4

_RADAR_BG = (16, 19, 24)
RADAR_BACKGROUND = _RADAR_BG
"""The radar's plain background color, so the radar card over the game can make exactly it translucent."""
GROUND_DRIVEN_COLOR = _COVERAGE_COLOR
"""The green of the ground driven, translucent on the radar card too: it covers most of the picture and would hide the game."""
_RADAR_RING = (52, 60, 70)
_RADAR_TEXT = (150, 158, 170)
_TRACK_COLOR = (118, 176, 134)
_DRIVE_RING_COLOR = (240, 140, 50)
_STOP_COLOR = (190, 140, 255)
_TARGET_COLOR = (255, 238, 140)
_RIG_CLEAR_COLOR = (90, 220, 200)
_RIG_INSIDE_COLOR = (255, 120, 90)
_RIG_INSIDE_FILL = (74, 36, 32)


@dataclass(frozen=True)
class RadarExtras:
    """What the live radar draws beyond the ground, sites and deposits, worked out by the caller."""
    drive_center: Optional[coverage.CoveragePoint] = None
    drive_radii_m: Sequence[float] = ()
    """Rings to drive round `drive_center`, from `mining_drive_rings.ring_radii`."""
    stops: Sequence[tuple[coverage.CoveragePoint, float, str]] = ()
    """(middle, radius in meters, label) of each stop worth parking at (`mining_stops.best_stops`)."""
    target_material: str = ""
    """The material to guide to (Settings > Mining > target commodity); empty means the nearest deposit of any kind."""
    rigs: Sequence[coverage.CoveragePoint] = ()
    """Where the commander noted placing rigs (`mining_rigs.py`)."""
    rig_gap_m: float = 0.0
    """How close two rigs may be (Settings > Mining); a band of this radius is drawn round each rig, none when it is 0."""


def _dotted_line(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], fill, gap_px: float = 6.0) -> None:
    length = math.hypot(end[0] - start[0], end[1] - start[1])
    if length < 1:
        return
    steps = int(length // gap_px)
    for step in range(0, steps + 1, 2):
        a, b = step * gap_px / length, min((step + 1) * gap_px / length, 1.0)
        draw.line([(start[0] + (end[0] - start[0]) * a, start[1] + (end[1] - start[1]) * a),
                   (start[0] + (end[0] - start[0]) * b, start[1] + (end[1] - start[1]) * b)], fill=fill, width=1)


def _dashed_circle(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius_px: float, fill, width: int = 1, view: Optional[tuple[float, float, float]] = None) -> None:
    """A dashed circle: PIL has no dashed outline, so it is drawn as short arcs with gaps. `view` is (x, y, reach in px) of the part of the picture that matters: only the arc that
    can fall inside it is drawn, so a ring many times the size of the picture costs no more than a small one."""
    if radius_px < 3:
        return
    start, end = 0.0, 360.0
    if view is not None:
        vx, vy, reach = view
        distance = math.hypot(vx - cx, vy - cy)
        if abs(distance - radius_px) > reach:
            return                                                  # the ring misses the picture altogether
        if radius_px > reach:
            aim = math.degrees(math.atan2(vy - cy, vx - cx))        # PIL measures clockwise from east with y down, as the radar's y does
            span = math.degrees(math.asin(min(1.0, reach / radius_px))) + 5.0
            start, end = aim - span, aim + span
    box = [cx - radius_px, cy - radius_px, cx + radius_px, cy + radius_px]
    dash = max(4.0, 28.0 / max(radius_px / 40.0, 1.0))
    angle = start
    while angle < end:
        draw.arc(box, angle, min(angle + dash, end), fill=fill, width=width)
        angle += dash * 2


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                       # a Pillow older than 10.1 has one fixed size
        return ImageFont.load_default()


def range_text(meters: float) -> str:
    return f"{meters / 1000:g} km" if meters >= 1000 else f"{meters:g} m"


def render_radar(body_coverage: Optional[coverage.BodyCoverage], radius_m: Optional[float], position: Optional[coverage.CoveragePoint],
                 heading_deg: Optional[float], known_hotspots: list[hotspots.Hotspot], size_px: int = 480,
                 range_m: float = DEFAULT_RADAR_RANGE_M, extras: Optional[RadarExtras] = None, center: Optional[coverage.CoveragePoint] = None) -> Optional[Image.Image]:
    """A radar centered on `position` (the Rhino), north up, `range_m` meters from the center to the edge: range rings, the ground driven, the mining locations the commander marked
    (a cross at the center and the circle through the border), the saved deposits with the first letters of their material (a hollow ring for a depleted one) and an arrow for the way the
    Rhino faces. A line runs to the nearest saved deposit with its distance. None without a position or the body's radius. `size_px` is both width and height: a fixed square, never
    derived from source data. With `center` the picture is centered on that point instead (the saved map picture, `mining_map_picture.py`): the Rhino is drawn where it is, and the lines
    and distances that belong to the Rhino's place are left out."""
    if position is None or not radius_m:
        return None
    anchor = center or position
    map_mode = center is not None
    size = max(160, min(int(size_px), 1600))
    half = size / 2
    scale = half / range_m
    image = Image.new("RGB", (size, size), _RADAR_BG)
    draw = ImageDraw.Draw(image)
    label_font, small_font = _font(max(11, size // 34)), _font(max(10, size // 40))

    def spot(latitude: float, longitude: float) -> tuple[float, float, float]:
        """(x, y, meters away) of a point on the radar."""
        distance = bearing.distance_m(anchor.latitude, anchor.longitude, latitude, longitude, radius_m)
        direction = math.radians(bearing.initial_bearing_deg(anchor.latitude, anchor.longitude, latitude, longitude))
        return half + distance * math.sin(direction) * scale, half - distance * math.cos(direction) * scale, distance

    # ground driven: a disc of scanner reach around each recorded point, then the track itself
    points = body_coverage.points if body_coverage else []
    reach = coverage.SCAN_RADIUS_M * scale
    nearby = [spot(p.latitude, p.longitude) for p in points]
    for x, y, distance in nearby:
        if distance <= range_m + coverage.SCAN_RADIUS_M:
            draw.ellipse([x - reach, y - reach, x + reach, y + reach], fill=_COVERAGE_COLOR)
    for x, y, distance in nearby:
        if distance <= range_m * 1.5:
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=_TRACK_COLOR)

    # range rings and the cross hairs
    draw.line([(half, 0), (half, size)], fill=_RADAR_RING)
    draw.line([(0, half), (size, half)], fill=_RADAR_RING)
    for step in range(1, _RADAR_RINGS + 1):
        ring = half * step / _RADAR_RINGS
        draw.ellipse([half - ring, half - ring, half + ring, half + ring], outline=_RADAR_RING)
        draw.text((half + 4, half - ring + 2), range_text(range_m * step / _RADAR_RINGS), fill=_RADAR_TEXT, font=small_font)
    draw.text((half - 28, 4), "N", fill=_RADAR_TEXT, font=label_font)      # left of the axis: the outer ring's label sits to the right of it

    # the mining locations the commander marked
    for site in (body_coverage.sites if body_coverage else ()):
        cx, cy, _ = spot(site.center.latitude, site.center.longitude)
        draw.line([(cx - 6, cy), (cx + 6, cy)], fill=_SITE_COLOR, width=2)
        draw.line([(cx, cy - 6), (cx, cy + 6)], fill=_SITE_COLOR, width=2)
        site_radius = site.radius_m(radius_m)
        if site_radius:
            reach_px = site_radius * scale
            draw.ellipse([cx - reach_px, cy - reach_px, cx + reach_px, cy + reach_px], outline=_SITE_COLOR, width=2)

    extras = extras or RadarExtras()

    # the rings to drive round a marked location, dashed, each labeled with its radius
    if extras.drive_center is not None:
        ring_x, ring_y, _ = spot(extras.drive_center.latitude, extras.drive_center.longitude)
        for ring_m in extras.drive_radii_m:
            ring_px = ring_m * scale
            _dashed_circle(draw, ring_x, ring_y, ring_px, _DRIVE_RING_COLOR, width=2, view=(half, half, half * 1.5))
            label_x, label_y = ring_x + ring_px * 0.7071, ring_y - ring_px * 0.7071           # on the ring's north-east
            if 0 <= label_x <= size and 0 <= label_y <= size:
                draw.text((label_x + 3, label_y - 12), range_text(ring_m), fill=_DRIVE_RING_COLOR, font=small_font)

    # the rigs noted on this body: a numbered marker at each (1 is the first placed) and, with a rig gap set, a band round it, filled while the Rhino is inside it and an outline once it is
    # clear (shape as well as color says which)
    if not map_mode:
        for number, rig in enumerate(extras.rigs, start=1):
            rig_x, rig_y, rig_distance = spot(rig.latitude, rig.longitude)
            band_px = extras.rig_gap_m * scale
            if band_px >= 3:
                inside = rig_distance < extras.rig_gap_m
                draw.ellipse([rig_x - band_px, rig_y - band_px, rig_x + band_px, rig_y + band_px], fill=_RIG_INSIDE_FILL if inside else None,
                             outline=_RIG_INSIDE_COLOR if inside else _RIG_CLEAR_COLOR, width=2 if inside else 1)
            draw.rectangle([rig_x - 5, rig_y - 5, rig_x + 5, rig_y + 5], fill=_RIG_CLEAR_COLOR, outline=_RADAR_BG)      # a square, so it is not taken for a deposit's dot
            draw.text((rig_x + 8, rig_y - 6), str(number), fill=_RIG_CLEAR_COLOR, font=small_font)

    # the stops worth parking at: one circle round each
    for stop_center, stop_m, stop_label in extras.stops:
        stop_x, stop_y, _ = spot(stop_center.latitude, stop_center.longitude)
        stop_px = stop_m * scale
        draw.ellipse([stop_x - stop_px, stop_y - stop_px, stop_x + stop_px, stop_y + stop_px], outline=_STOP_COLOR, width=2)
        if -8 <= stop_x <= size + 8 and -8 <= stop_y <= size + 8:
            draw.text((stop_x - 14, stop_y - stop_px - 14), stop_label, fill=_STOP_COLOR, font=small_font)

    # saved deposits, and a line to the nearest
    placed = []
    for hotspot in known_hotspots:
        if hotspot.has_position():
            x, y, distance = spot(hotspot.latitude, hotspot.longitude)
            placed.append((distance, x, y, hotspot))
    nearest = min(placed, key=lambda item: item[0]) if placed and not map_mode else None
    wanted = extras.target_material.strip().casefold()
    targets = [item for item in placed if wanted and not map_mode and (item[3].material or "").strip().casefold() == wanted and item[3].amount != "Depleted"]
    target = min(targets, key=lambda item: item[0]) if targets else None
    guide = target or nearest               # the deposit the radar points at: your target material when you have one and it is saved here, else the nearest of any kind
    for _, x, y, hotspot in placed:
        if not (-8 <= x <= size + 8 and -8 <= y <= size + 8):
            continue
        box = [x - 5, y - 5, x + 5, y + 5]
        if hotspot.amount == "Depleted":
            draw.ellipse(box, outline=_DEPLETED_COLOR, width=2)
        else:
            draw.ellipse(box, fill=_HOTSPOT_COLOR)
        label = (hotspot.material or "?")[:3]
        carries = [item for item in (guide, nearest) if item is not None and hotspot is item[3]]
        if carries:
            label += "  " + bearing.format_distance_m(carries[0][0])      # a deposit a line runs to carries its distance, so the line needs no label of its own to clash with this one
        draw.text((x + 8, y - 7), label, fill=_TARGET_COLOR if guide is not None and hotspot is guide[3] and target is not None else (_HOTSPOT_COLOR if carries else _RADAR_TEXT), font=small_font)
    if nearest is not None and (guide is None or nearest[3] is not guide[3]):
        _dotted_line(draw, (half, half), (nearest[1], nearest[2]), _HOTSPOT_COLOR)       # the nearest of any kind, dotted, when the line to your target material is the solid one
    if guide is not None:
        line_color = _TARGET_COLOR if target is not None else _HOTSPOT_COLOR
        draw.line([(half, half), (guide[1], guide[2])], fill=line_color, width=2 if target is not None else 1)
        if not (-8 <= guide[1] <= size + 8 and -8 <= guide[2] <= size + 8):        # the deposit is beyond the radar: say what and how far where the line leaves it
            reach_px = math.hypot(guide[1] - half, guide[2] - half)
            edge = half - 70.0
            if reach_px > 0 and edge > 0:
                draw.text((half + (guide[1] - half) * edge / reach_px - 20, half + (guide[2] - half) * edge / reach_px - 6),
                          f"{(guide[3].material or '?')[:3]}  {bearing.format_distance_m(guide[0])}", fill=line_color, font=small_font)

    # the Rhino, pointing the way it faces (at the middle, or where it is when the picture is centered elsewhere)
    rx, ry, _ = spot(position.latitude, position.longitude)
    if heading_deg is None:
        draw.ellipse([rx - 6, ry - 6, rx + 6, ry + 6], fill=_POSITION_COLOR, outline=_POSITION_OUTLINE)
    else:
        angle = math.radians(heading_deg)
        tip = (rx + 13 * math.sin(angle), ry - 13 * math.cos(angle))
        left = (rx + 8 * math.sin(angle + 2.5), ry - 8 * math.cos(angle + 2.5))
        right = (rx + 8 * math.sin(angle - 2.5), ry - 8 * math.cos(angle - 2.5))
        draw.polygon([tip, left, (rx, ry), right], fill=_POSITION_COLOR, outline=_POSITION_OUTLINE)
    return image


def to_photo_data(image: Image.Image) -> bytes:
    """GIF bytes suitable for tk.PhotoImage(data=...) - see this
    module's docstring for why the thumbnail() call stays even though
    `image` is already exactly MAP_SIZE_PX square."""
    copy = image.copy()
    copy.thumbnail((MAP_SIZE_PX, MAP_SIZE_PX), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    copy.convert("RGB").save(buffer, format="GIF")
    return buffer.getvalue()


def to_window_photo_data(image: Image.Image) -> bytes:
    """PNG bytes for tk.PhotoImage(data=...) at the image's own size. For the live window, a separate window sized by the commander; the panel's picture goes through `to_photo_data`, which
    caps it at MAP_SIZE_PX so it can never widen EDMC's main window."""
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()
