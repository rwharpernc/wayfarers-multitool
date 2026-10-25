"""A pretend Rhino for trying the Mining Live window without the game.

Settings → Mining → Simulation opens the Surface Live window on made-up data: a Rhino that drives a ring round the middle of a made-up mining location, leaving a trail, with
saved deposits and marked locations to find, refining ore as it goes. The sizes follow real work: a mining signal is several kilometers across and the scanner reaches 2 km, so the
Rhino drives a ring 3.75 km out from the middle of a signal 4.5 km in radius. It exists so the radar, the info lines and the CTR, BRD and +H.S. buttons can be checked the same way
on Windows and on Linux (and by anyone without Elite running).

Nothing here touches the commander's data. The simulation builds its own repositories (never the real singletons) and never gives them a plugin folder or a commander, so none of
them can write a file; `tests/test_mining_simulation.py` checks that. Buttons pressed in the window act on the pretend data only, and it is gone when the window closes.
"""

from __future__ import annotations

import math
import time
from typing import Callable, Optional

from . import mining_coverage as coverage
from . import mining_hotspots as hotspots
from . import mining_live_position as live_position
from . import mining_rigs
from . import mining_sources
from . import mining_space as space_mining
from . import mining_surface as surface_mining

SYSTEM = "Simulated System"
BODY = "Simulated System 1 a"
PLANET_RADIUS_M = 1_800_000.0
START = coverage.CoveragePoint(12.0, 40.0)
"""The middle of the made-up mining location."""
SIGNAL_RADIUS_M = 4500.0
LOOP_RADIUS_M = 3750.0
"""The Rhino drives a ring this far from the middle, inside the signal."""
SPEED_MPS = 90.0
"""About 4.5 minutes a lap: the Rhino at a fast driving speed, so the radar visibly moves at the default 2 km range."""
SIM_RIG_GAP_M = 80
"""The rig gap the simulation draws its bands with, so they show even when no gap is set in Settings; a real gap is the commander's own measurement."""
REFINE_EVERY_S = 4.0
CARGO_PER_REFINE = 2
COMMODITIES = ("Painite", "Platinum", "Low Temperature Diamonds")
TRAIL_SECONDS = 600
"""How much driving is already behind the Rhino when the simulation opens, so the radar shows ground driven at once."""


class SurfaceSimulation:
    """The pretend Rhino's world. `sources` is what the Live window reads in place of WFMT's own state."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._started = clock()
        self._last_refine = 0.0
        self.surface = surface_mining.SurfaceMiningRepository()
        self.coverage = coverage.CoverageRepository()
        self.hotspots = hotspots.HotspotRepository()
        self.space = space_mining.SpaceMiningRepository()
        self.rigs = mining_rigs.RigBook()
        self._build_world()
        self.sources = mining_sources.Sources(surface=self.surface, coverage=self.coverage, hotspots=self.hotspots, space=self.space,
                                              position=self.position, tick=self.tick, simulated=True, rigs=self.rigs, rig_gap_override=SIM_RIG_GAP_M)

    # --- the world ----------------------------------------------------------------------------------------------------

    def _build_world(self) -> None:
        self.surface.set_current_cmdr("Simulated commander")
        self.surface.start_run(1)
        self.surface.record_body_radius(BODY, PLANET_RADIUS_M)
        self.surface.set_current_location(SYSTEM, BODY)
        self.surface.record_mining_location_signal(BODY, 3)
        for seconds in range(0, TRAIL_SECONDS + 1, 5):
            self._record_ground(float(seconds))
        for material, bearing_deg, distance_m, rigs in (("Painite", 20.0, 3900.0, 4), ("Platinum", 130.0, 3400.0, 6), ("Low Temperature Diamonds", 250.0, 4300.0, 3),
                                                        ("Platinum", 100.0, 1200.0, 5)):
            spot = coverage.point_at(START, bearing_deg, distance_m, PLANET_RADIUS_M)
            self.hotspots.add(hotspots.Hotspot(system=SYSTEM, body=BODY, material=material, latitude=spot.latitude, longitude=spot.longitude, rigs=rigs))
        # a depleted deposit (a hollow ring on the radar) and one saved without a position (listed in the lines, never on the radar)
        spent = coverage.point_at(START, 300.0, 2600.0, PLANET_RADIUS_M)
        self.hotspots.add(hotspots.Hotspot(system=SYSTEM, body=BODY, material="Void Opals", latitude=spent.latitude, longitude=spent.longitude, rigs=4, amount="Depleted"))
        self.hotspots.add(hotspots.Hotspot(system=SYSTEM, body=BODY, material="Bromellite", notes="no position saved", rigs=2))
        self.coverage.mark(SYSTEM, BODY, START.latitude, START.longitude, PLANET_RADIUS_M, False)
        edge = coverage.point_at(START, 90.0, SIGNAL_RADIUS_M, PLANET_RADIUS_M)
        self.coverage.mark(SYSTEM, BODY, edge.latitude, edge.longitude, PLANET_RADIUS_M, True)
        unfinished = coverage.point_at(START, 200.0, 9000.0, PLANET_RADIUS_M)
        self.coverage.mark(SYSTEM, BODY, unfinished.latitude, unfinished.longitude, PLANET_RADIUS_M, False)
        for seconds in (5.0, 6.0, 12.0):          # three rigs on the Rhino's way, two just over the gap apart: it drives through their bands
            spot = self._position_at(TRAIL_SECONDS + seconds)
            self.rigs.add(SYSTEM, BODY, spot.latitude, spot.longitude, PLANET_RADIUS_M)
        self.coverage.last_message = "Simulation: nothing here is real, and nothing you press is saved."

    # --- the Rhino ----------------------------------------------------------------------------------------------------

    def _position_at(self, seconds: float) -> live_position.LivePosition:
        angle = (seconds * SPEED_MPS / LOOP_RADIUS_M) % (2 * math.pi)
        point = coverage.point_at(START, math.degrees(angle), LOOP_RADIUS_M, PLANET_RADIUS_M)
        heading = (math.degrees(angle) + 90.0) % 360.0         # clockwise round the circle: the way it faces is a quarter turn ahead of where it is
        return live_position.LivePosition(latitude=point.latitude, longitude=point.longitude, heading=heading, planet_radius=PLANET_RADIUS_M, altitude=0.0)

    def position(self) -> Optional[live_position.LivePosition]:
        return self._position_at(self._clock() - self._started + TRAIL_SECONDS)

    def _record_ground(self, seconds: float) -> None:
        here = self._position_at(seconds)
        self.coverage.record(SYSTEM, BODY, here.latitude, here.longitude, PLANET_RADIUS_M)

    def tick(self) -> None:
        """Called before each redraw: leave a point of trail and, every few seconds, refine a unit of ore (emptying the cargo into the ship when the Rhino is full)."""
        elapsed = self._clock() - self._started
        self._record_ground(elapsed + TRAIL_SECONDS)
        if elapsed - self._last_refine < REFINE_EVERY_S:
            return
        self._last_refine = elapsed
        run = self.surface.current_run()
        if run is None:
            return
        if run.cargo + CARGO_PER_REFINE > surface_mining.RHINO_CARGO_CAPACITY:
            self.surface.record_transfer_to_ship(COMMODITIES[0], run.cargo)
            self.surface.update_cargo(0)
            return
        self.surface.record_refined(COMMODITIES[int(elapsed // REFINE_EVERY_S) % len(COMMODITIES)])
        self.surface.update_cargo(run.cargo + CARGO_PER_REFINE)


def open_surface_live(parent, settings_factory) -> None:
    """Open the Surface Live window on a new pretend Rhino (Settings → Mining → Simulation). If a simulation window is already open it is raised instead."""
    from . import mining_live_window, mining_pages

    # EDMC's Settings window holds a modal grab, so while it is open no other window receives a click, the simulation's close button included. Let it go for as long as the
    # simulation is open, and give it back when the simulation closes.
    holder = parent.grab_current()
    window = mining_live_window.show(parent, mining_pages.SURFACE_MINING, settings_factory, SurfaceSimulation().sources)
    if holder is None or window is None:
        return
    holder.grab_release()
    top = window.toplevel

    def give_back(event) -> None:
        if event.widget is not top:
            return
        try:
            if holder.winfo_exists():
                holder.grab_set()
        except Exception:  # noqa: BLE001 - the Settings window went first, or Tk refused the grab: nothing to give back
            pass

    top.bind("<Destroy>", give_back, add="+")
