"""A map picture of a mining location, to save and share.

The live radar follows the Rhino. This draws the same marks once, centered on the marked location (or on the Rhino when none is marked), sized to fit the ground driven, the border and
the saved deposits, with a title and a legend, so it can be posted without explanation. It holds no commander name and no dates. Pure drawing: no Tk, no EDMC. The live window's
**Save map** button writes it to a file the commander chooses.
"""

from __future__ import annotations

import math
from typing import Optional

from PIL import Image, ImageDraw

from . import mining_bearing as bearing
from . import mining_coverage as coverage
from . import mining_coverage_render as radar
from . import mining_hotspots as hotspots

SIZE_PX = 900
"""The map's side. The whole picture is this wide, so it is a fixed size however the ground is laid out."""
RANGE_STEPS_M = (2000.0, 4000.0, 6000.0, 8000.0, 12000.0, 16000.0)
"""The distances from the middle to the edge a picture can have: the smallest that fits everything, never more than the last."""
FIT_MARGIN = 1.1
TITLE_PX = 78
LEGEND_PX = 150
_BACKGROUND = (16, 19, 24)
_TEXT = (226, 230, 236)
_MUTED = (150, 158, 170)

_LEGEND = (
    ("Ground driven (within 2 km of the track)", "swatch", radar._COVERAGE_COLOR),
    ("Your track", "dot", radar._TRACK_COLOR),
    ("Marked center and border", "cross", radar._SITE_COLOR),
    ("Where to drive to cover it", "dashed", radar._DRIVE_RING_COLOR),
    ("Stop", "ring", radar._STOP_COLOR),
    ("Saved deposit", "dot", radar._HOTSPOT_COLOR),
    ("Depleted deposit", "ring", radar._DEPLETED_COLOR),
    ("Rhino", "dot", radar._POSITION_COLOR),
)


def fit_range_m(center: coverage.CoveragePoint, radius_m: float, body_coverage: Optional[coverage.BodyCoverage], saved: list[hotspots.Hotspot],
                extras: radar.RadarExtras) -> float:
    """The smallest of `RANGE_STEPS_M` that holds the ring or border, the ground driven and the placed deposits round `center`, with a margin."""
    farthest = max(extras.drive_radii_m, default=0.0)
    for point in (body_coverage.points if body_coverage else ()):
        farthest = max(farthest, bearing.distance_m(center.latitude, center.longitude, point.latitude, point.longitude, radius_m))
    for spot in saved:
        if spot.has_position():
            farthest = max(farthest, bearing.distance_m(center.latitude, center.longitude, spot.latitude, spot.longitude, radius_m))
    needed = farthest * FIT_MARGIN
    return next((step for step in RANGE_STEPS_M if step >= needed), RANGE_STEPS_M[-1])


def render(body_coverage: Optional[coverage.BodyCoverage], radius_m: Optional[float], position: Optional[coverage.CoveragePoint], heading_deg: Optional[float],
           saved: list[hotspots.Hotspot], system: str, body: str, extras: Optional[radar.RadarExtras] = None) -> Optional[Image.Image]:
    """The picture, or None without a position or the body's radius (nothing to center on)."""
    if position is None or not radius_m:
        return None
    extras = extras or radar.RadarExtras()
    center = extras.drive_center or position
    range_m = fit_range_m(center, radius_m, body_coverage, saved, extras)
    drawn = radar.RadarExtras(drive_center=extras.drive_center, drive_radii_m=extras.drive_radii_m, stops=extras.stops)       # no target line: it belongs to where the Rhino is
    plot = radar.render_radar(body_coverage, radius_m, position, heading_deg, saved, SIZE_PX, range_m, drawn, center=center)
    if plot is None:
        return None
    image = Image.new("RGB", (SIZE_PX, TITLE_PX + SIZE_PX + LEGEND_PX), _BACKGROUND)
    draw = ImageDraw.Draw(image)
    title_font, text_font, small_font = radar._font(30), radar._font(18), radar._font(15)
    draw.text((16, 12), f"{body}  ·  {system}", fill=_TEXT, font=title_font)
    draw.text((16, 50), f"North is up. Rings every {radar.range_text(range_m / 4)}.", fill=_MUTED, font=small_font)
    image.paste(plot, (0, TITLE_PX))
    top = TITLE_PX + SIZE_PX + 14
    for index, (label, kind, color) in enumerate(_LEGEND):
        x, y = 16 + (index % 2) * (SIZE_PX // 2), top + (index // 2) * 26
        _swatch(draw, kind, color, x, y)
        draw.text((x + 30, y - 2), label, fill=_TEXT, font=text_font)
    draw.text((16, TITLE_PX + SIZE_PX + LEGEND_PX - 24),
              "Ground driven means driven within scanner reach (2 km, a community estimate), not proven scanned.", fill=_MUTED, font=small_font)
    return image


def _swatch(draw: ImageDraw.ImageDraw, kind: str, color: tuple[int, int, int], x: int, y: int) -> None:
    if kind == "swatch":
        draw.rectangle([x, y + 2, x + 20, y + 16], fill=color)
    elif kind == "dot":
        draw.ellipse([x + 5, y + 4, x + 15, y + 14], fill=color)
    elif kind == "ring":
        draw.ellipse([x + 4, y + 3, x + 16, y + 15], outline=color, width=2)
    elif kind == "cross":
        draw.line([(x + 10, y + 1), (x + 10, y + 17)], fill=color, width=2)
        draw.line([(x + 2, y + 9), (x + 18, y + 9)], fill=color, width=2)
    elif kind == "dashed":
        for start in (0, 12):
            draw.line([(x + start, y + 9), (x + start + 7, y + 9)], fill=color, width=2)


def save(image: Image.Image, path: str) -> None:
    """Write the picture as a PNG."""
    image.save(path, format="PNG")
