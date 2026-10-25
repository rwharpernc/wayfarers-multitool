"""The saved map picture (plugin/mining_map_picture.py): sized to fit, a fixed width, and drawn from the simulation's pretend ground. No Tk, no EDMC."""

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))

from plugin import mining_coverage as coverage  # noqa: E402
from plugin import mining_coverage_render as radar  # noqa: E402
from plugin import mining_drive_rings as rings  # noqa: E402
from plugin import mining_map_picture as picture  # noqa: E402
from plugin import mining_simulation as simulation  # noqa: E402


class MapPictureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sim = simulation.SurfaceSimulation()
        self.position = self.sim.position()
        self.here = coverage.CoveragePoint(self.position.latitude, self.position.longitude)
        self.radius = simulation.PLANET_RADIUS_M
        self.body = self.sim.coverage.for_body(simulation.SYSTEM, simulation.BODY)
        self.saved = self.sim.hotspots.for_body(simulation.SYSTEM, simulation.BODY)
        self.extras = radar.RadarExtras(drive_center=simulation.START, drive_radii_m=rings.ring_radii(simulation.SIGNAL_RADIUS_M))

    def test_the_range_is_the_smallest_step_that_fits(self) -> None:
        wide = picture.fit_range_m(simulation.START, self.radius, self.body, self.saved, self.extras)
        self.assertIn(wide, picture.RANGE_STEPS_M)
        self.assertGreaterEqual(wide, simulation.SIGNAL_RADIUS_M * picture.FIT_MARGIN)
        smaller = [step for step in picture.RANGE_STEPS_M if step < wide]
        self.assertTrue(not smaller or smaller[-1] < simulation.SIGNAL_RADIUS_M * picture.FIT_MARGIN)

    def test_empty_ground_gets_the_smallest_range(self) -> None:
        self.assertEqual(picture.fit_range_m(self.here, self.radius, None, [], radar.RadarExtras()), picture.RANGE_STEPS_M[0])

    def test_the_range_is_capped(self) -> None:
        self.assertEqual(picture.fit_range_m(self.here, self.radius, None, [], radar.RadarExtras(drive_radii_m=[1e9])), picture.RANGE_STEPS_M[-1])

    def test_the_picture_has_a_fixed_width_and_the_expected_height(self) -> None:
        image = picture.render(self.body, self.radius, self.here, self.position.heading, self.saved, simulation.SYSTEM, simulation.BODY, self.extras)
        self.assertEqual(image.size, (picture.SIZE_PX, picture.TITLE_PX + picture.SIZE_PX + picture.LEGEND_PX))

    def test_nothing_to_center_on_gives_no_picture(self) -> None:
        self.assertIsNone(picture.render(self.body, self.radius, None, None, self.saved, "s", "b"))
        self.assertIsNone(picture.render(self.body, None, self.here, None, self.saved, "s", "b"))

    def test_the_rhino_lines_are_left_off_a_map_centered_elsewhere(self) -> None:
        target_extras = radar.RadarExtras(drive_center=simulation.START, drive_radii_m=self.extras.drive_radii_m, target_material="Platinum")
        image = picture.render(self.body, self.radius, self.here, None, self.saved, "s", "b", target_extras)
        self.assertFalse(any(color == radar._TARGET_COLOR for _count, color in image.getcolors(maxcolors=1 << 24)))

    def test_it_writes_a_png(self) -> None:
        import tempfile
        image = picture.render(self.body, self.radius, self.here, None, self.saved, "Sys", "Body", self.extras)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "map.png")
            picture.save(image, path)
            self.assertTrue(open(path, "rb").read(8).startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()
