"""Where the Mining pages read their data from.

The panel and the Live window read the live position, the Rhino run, the marked sites, the saved deposits and the ship run. Normally that is WFMT's own state (`real()`).
The Mining simulation (`mining_simulation.py`) hands the same renderers a separate, in-memory set instead, so fake data can be shown without touching anything the
commander has saved. Nothing here needs Tk or EDMC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from . import mining_coverage as coverage
from . import mining_hotspots as hotspots
from . import mining_live_position as live_position
from . import mining_rigs
from . import mining_space as space_mining
from . import mining_surface as surface_mining


@dataclass
class Sources:
    surface: surface_mining.SurfaceMiningRepository
    coverage: coverage.CoverageRepository
    hotspots: hotspots.HotspotRepository
    space: space_mining.SpaceMiningRepository
    position: Callable[[], Optional[live_position.LivePosition]]
    tick: Callable[[], None] = lambda: None
    """Called once before each redraw of a window; the simulation moves its Rhino here. Does nothing for real data."""
    simulated: bool = False
    rigs: mining_rigs.RigBook = field(default_factory=mining_rigs.RigBook)
    """The rigs the commander has noted on this body (`mining_rigs.py`); the real ones are the module's own, a simulation has its own."""
    rig_gap_override: Optional[int] = None
    """A rig gap to draw bands with instead of the Settings one; only the simulation sets it, so its bands show even when the commander has set no gap."""


def real() -> Sources:
    """WFMT's own state. Built on each call so a test that swaps a module's repository is followed."""
    return Sources(surface=surface_mining.surface_mining_repository, coverage=coverage.coverage_repository,
                   hotspots=hotspots.hotspot_repository, space=space_mining.space_mining_repository, rigs=mining_rigs.rig_book,
                   position=live_position.current_position)
