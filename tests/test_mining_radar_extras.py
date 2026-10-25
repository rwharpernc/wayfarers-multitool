"""The live radar's drive rings, stops and target-material line (plugin/mining_drive_rings.py, plugin/mining_coverage_render.py). Pure logic and drawing: no Tk, no EDMC."""

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))

from plugin import mining_coverage as coverage  # noqa: E402
from plugin import mining_coverage_render as render  # noqa: E402
from plugin import mining_drive_rings as rings  # noqa: E402
from plugin import mining_simulation as simulation  # noqa: E402
from plugin import mining_stops as stops  # noqa: E402


class RingRadiiTests(unittest.TestCase):
    def test_a_border_ends_the_rings_on_the_border(self) -> None:
        self.assertEqual(rings.ring_radii(4500.0), [2000.0, 4500.0])
        self.assertEqual(rings.ring_radii(12000.0)[-1], 12000.0)

    def test_each_ring_band_reaches_the_next_with_an_overlap(self) -> None:
        radii = rings.ring_radii(12000.0)
        for inner, outer in zip(radii, radii[1:]):
            self.assertLess(outer - inner, 2 * coverage.SCAN_RADIUS_M, "the bands overlap instead of leaving a seam")
        self.assertGreaterEqual(radii[-1] + coverage.SCAN_RADIUS_M, 12000.0)

    def test_a_small_signal_gets_one_ring_inside_its_border(self) -> None:
        self.assertEqual(rings.ring_radii(1000.0), [1000.0])

    def test_no_border_follows_the_ground_driven(self) -> None:
        self.assertEqual(rings.ring_radii(None), [coverage.SCAN_RADIUS_M], "nothing driven yet: just the first ring")
        self.assertEqual(rings.ring_radii(None, driven_m=3500.0), [2000.0], "driven within the first ring's band")
        far = rings.ring_radii(None, driven_m=7000.0)
        self.assertEqual(far[0], 2000.0)
        self.assertGreaterEqual(far[-1] + coverage.SCAN_RADIUS_M, 7000.0, "the rings reach the ground driven")
        self.assertEqual(rings.ring_radii(None, driven_m=12000.0)[-1] + coverage.SCAN_RADIUS_M >= 12000.0, True)

    def test_a_border_wins_over_the_ground_driven(self) -> None:
        self.assertEqual(rings.ring_radii(4500.0, driven_m=20000.0), [2000.0, 4500.0])

    def test_the_count_is_capped(self) -> None:
        self.assertLessEqual(len(rings.ring_radii(1e9)), rings.MAX_RINGS)


class RadarExtrasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sim = simulation.SurfaceSimulation()
        self.position = self.sim.position()
        self.radius = simulation.PLANET_RADIUS_M
        self.body = self.sim.coverage.for_body(simulation.SYSTEM, simulation.BODY)
        self.saved = self.sim.hotspots.for_body(simulation.SYSTEM, simulation.BODY)
        self.here = coverage.CoveragePoint(self.position.latitude, self.position.longitude)

    def _draw(self, extras=None, range_m=4000.0):
        return render.render_radar(self.body, self.radius, self.here, self.position.heading, self.saved, 480, range_m, extras)

    @staticmethod
    def _has(image, color) -> bool:
        return any(found == color for _count, found in image.getcolors(maxcolors=1 << 24))

    def test_the_drive_rings_are_drawn_only_when_asked_for(self) -> None:
        self.assertFalse(self._has(self._draw(), render._DRIVE_RING_COLOR))
        extras = render.RadarExtras(drive_center=simulation.START, drive_radii_m=rings.ring_radii(simulation.SIGNAL_RADIUS_M))
        self.assertTrue(self._has(self._draw(extras), render._DRIVE_RING_COLOR))

    def test_the_stop_circles_are_drawn(self) -> None:
        best = stops.best_stops(stops.find_stops(self.saved, self.radius, 1250))
        self.assertTrue(best)
        extras = render.RadarExtras(stops=tuple((coverage.CoveragePoint(s.lead.latitude, s.lead.longitude), 1250.0, f"Stop {n}") for n, s in enumerate(best, 1)))
        self.assertFalse(self._has(self._draw(), render._STOP_COLOR))
        self.assertTrue(self._has(self._draw(extras), render._STOP_COLOR))

    def test_the_target_material_gets_the_bright_line(self) -> None:
        self.assertFalse(self._has(self._draw(), render._TARGET_COLOR))
        self.assertTrue(self._has(self._draw(render.RadarExtras(target_material="platinum")), render._TARGET_COLOR), "matching ignores case")
        self.assertFalse(self._has(self._draw(render.RadarExtras(target_material="Tritium")), render._TARGET_COLOR), "nothing saved of it: the plain nearest line is used")

    def test_a_depleted_deposit_is_not_a_target(self) -> None:
        self.assertFalse(self._has(self._draw(render.RadarExtras(target_material="Void Opals")), render._TARGET_COLOR))

    def test_the_image_stays_the_size_asked_for(self) -> None:
        extras = render.RadarExtras(drive_center=simulation.START, drive_radii_m=[2000.0, 1e7], target_material="Painite")
        self.assertEqual(self._draw(extras, 500.0).size, (480, 480))


if __name__ == "__main__":
    unittest.main()
