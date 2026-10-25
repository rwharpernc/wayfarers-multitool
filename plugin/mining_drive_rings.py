"""Where to drive round a marked mining location so the scanner covers all of it.

The scanner reaches `coverage.SCAN_RADIUS_M` (2 km, the community figure; Frontier has not published one) to each side of the Rhino, so a ring driven at radius r covers the band from
r - reach to r + reach. These are the rings that tile a location from its middle out to its border with a little overlap. They are a guide worked out from that one number, not a
measurement of where deposits are: if the real reach is different the rings are too. Nothing here needs Tk or EDMC.
"""

from __future__ import annotations

import math
from typing import List, Optional

from . import mining_coverage as coverage

OVERLAP = 0.9
"""Each ring is placed 90% of a scanner diameter beyond the last, so the bands overlap a little instead of leaving a seam."""
MAX_RINGS = 12


def ring_radii(border_m: Optional[float], reach_m: float = coverage.SCAN_RADIUS_M, driven_m: float = 0.0) -> List[float]:
    """Radii in meters, inside out, of the rings to drive round a location's middle.

    The first sits one reach out, so its band starts at the middle, and each next one a little under a scanner diameter further. How far out they go depends on what is known: with the
    border marked, far enough that a band reaches it, the last ring placed on the border itself; without one, far enough to cover the ground already driven (`driven_m`, the farthest
    point of the track from the middle), so a location with nothing driven yet shows just the first ring."""
    if reach_m <= 0:
        return []
    step = 2 * reach_m * OVERLAP
    has_border = border_m is not None and border_m > 0
    first = min(reach_m, border_m) if has_border else reach_m
    cover_to = border_m if has_border else max(driven_m, 0.0)
    more = math.ceil((cover_to - reach_m - first) / step) if cover_to > first + reach_m else 0
    radii = [first + number * step for number in range(min(1 + more, MAX_RINGS))]
    if has_border:
        radii[-1] = min(radii[-1], border_m)
    return radii
