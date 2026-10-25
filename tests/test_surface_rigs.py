"""The rigs noted on a body (plugin/mining_rigs.py), the spacing bands the radar draws round them and the Rig placed action. Pure logic and drawing: no Tk, no network, no EDMC."""

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
_cfg = sys.modules.setdefault("config", types.ModuleType("config"))
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0")):
    if not hasattr(_cfg, _attr):
        setattr(_cfg, _attr, _default)
if not hasattr(_cfg, "config"):
    _cfg.config = mock.MagicMock()


class _Any(types.ModuleType):
    """A stand-in for an EDMC module: any attribute is a mock."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock()


for _name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "theme", "myNotebook"):
    sys.modules.setdefault(_name, _Any(_name))

from plugin import mining_coverage as coverage  # noqa: E402
from plugin import mining_coverage_render as radar  # noqa: E402
from plugin import mining_rigs as rigs  # noqa: E402
from plugin import mining_simulation as simulation  # noqa: E402

RADIUS = 1_800_000.0
SYSTEM, BODY = "Sys", "Sys 1"
HERE = coverage.CoveragePoint(10.0, 20.0)


def at(bearing_deg: float, meters: float) -> coverage.CoveragePoint:
    return coverage.point_at(HERE, bearing_deg, meters, RADIUS)


class RigBookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.book = rigs.RigBook()

    def add(self, point=HERE, system=SYSTEM, body=BODY, radius=RADIUS) -> str:
        return self.book.add(system, body, point.latitude, point.longitude, radius)

    def test_a_rig_is_noted_and_numbered(self) -> None:
        self.assertEqual(self.add(), "Rig 1 noted here.")
        self.assertEqual(self.add(at(90, 80)), "Rig 2 noted here.")
        self.assertEqual(len(self.book.rigs_for(SYSTEM, BODY)), 2)

    def test_a_second_press_at_the_same_spot_adds_nothing(self) -> None:
        self.add()
        self.assertIn("already noted", self.add(at(0, rigs.SAME_SPOT_M - 1)))
        self.assertEqual(len(self.book.rigs_for(SYSTEM, BODY)), 1)
        self.assertEqual(self.add(at(0, rigs.SAME_SPOT_M + 1)), "Rig 2 noted here.")

    def test_without_a_body_or_its_size_nothing_is_noted(self) -> None:
        for kwargs in ({"system": None}, {"body": ""}, {"radius": None}, {"radius": 0.0}):
            self.assertIn("land first", self.add(**kwargs), kwargs)
        self.assertEqual(self.book.rigs_for(SYSTEM, BODY), [])

    def test_the_rigs_are_for_one_body_and_another_body_starts_a_new_set(self) -> None:
        self.add()
        self.assertEqual(self.book.rigs_for(SYSTEM, "Sys 2"), [])
        self.assertEqual(self.add(system=SYSTEM, body="Sys 2"), "Rig 1 noted here.")
        self.assertEqual(self.book.rigs_for(SYSTEM, BODY), [], "the first body's rigs are gone")
        self.assertEqual(len(self.book.rigs_for(SYSTEM.upper(), "SYS 2")), 1, "names match without regard to case")

    def test_nothing_is_returned_for_no_body_even_with_no_rigs(self) -> None:
        self.assertEqual(self.book.rigs_for(None, None), [])
        self.assertEqual(self.book.rigs_for("", ""), [])

    def test_the_most_rigs_are_capped(self) -> None:
        for number in range(rigs.MAX_RIGS):
            self.add(at(0, 10.0 * number))
        self.assertIn("clear them first", self.add(at(0, 10.0 * rigs.MAX_RIGS)))
        self.assertEqual(len(self.book.rigs_for(SYSTEM, BODY)), rigs.MAX_RIGS)

    def test_clearing_forgets_every_rig_and_says_how_many(self) -> None:
        self.add()
        self.add(at(0, 100))
        self.assertEqual(self.book.clear(), 2)
        self.assertEqual((self.book.rigs_for(SYSTEM, BODY), self.book.clear()), ([], 0))

    def test_spacing_says_how_the_rhino_stands_against_the_nearest_rig(self) -> None:
        self.add()
        self.add(at(90, 200))
        near = self.book.spacing(SYSTEM, BODY, at(90, 40).latitude, at(90, 40).longitude, RADIUS, 80)
        self.assertEqual(near.count, 2)
        self.assertAlmostEqual(near.nearest_m, 40, delta=1)
        self.assertTrue(near.inside)
        clear = self.book.spacing(SYSTEM, BODY, at(0, 100).latitude, at(0, 100).longitude, RADIUS, 80)
        self.assertFalse(clear.inside)
        self.assertFalse(self.book.spacing(SYSTEM, BODY, HERE.latitude, HERE.longitude, RADIUS, 0).inside, "no gap set: never inside")

    def test_spacing_is_none_without_rigs_or_a_known_size(self) -> None:
        self.assertIsNone(self.book.spacing(SYSTEM, BODY, 0.0, 0.0, RADIUS, 80))
        self.add()
        self.assertIsNone(self.book.spacing(SYSTEM, BODY, 0.0, 0.0, None, 80))
        self.assertIsNone(self.book.spacing(SYSTEM, "Other", 0.0, 0.0, RADIUS, 80))


class BandTests(unittest.TestCase):
    def draw(self, rig_points, gap, here=HERE):
        extras = radar.RadarExtras(rigs=tuple(rig_points), rig_gap_m=float(gap))
        return radar.render_radar(None, RADIUS, here, 0.0, [], 480, 500.0, extras)

    @staticmethod
    def has(image, color) -> bool:
        return any(found == color for _count, found in image.getcolors(maxcolors=1 << 24))

    def test_a_clear_rig_gets_an_outline_and_a_close_one_a_filled_band(self) -> None:
        clear = self.draw([at(0, 300)], 80)
        self.assertTrue(self.has(clear, radar._RIG_CLEAR_COLOR))
        self.assertFalse(self.has(clear, radar._RIG_INSIDE_COLOR))
        inside = self.draw([at(0, 40)], 80)
        self.assertTrue(self.has(inside, radar._RIG_INSIDE_COLOR))
        self.assertTrue(self.has(inside, radar._RIG_INSIDE_FILL), "inside the band: filled, so shape as well as color says so")
        self.assertFalse(self.has(clear, radar._RIG_INSIDE_FILL))

    def test_with_no_gap_only_the_dots_are_drawn(self) -> None:
        image = self.draw([at(0, 40)], 0)
        self.assertTrue(self.has(image, radar._RIG_CLEAR_COLOR))
        self.assertFalse(self.has(image, radar._RIG_INSIDE_COLOR))

    def test_no_rigs_draws_nothing_of_them_and_a_far_rig_does_not_crash(self) -> None:
        self.assertFalse(self.has(self.draw([], 80), radar._RIG_CLEAR_COLOR))
        self.assertEqual(self.draw([at(0, 900000)], 80).size, (480, 480))

    def test_the_saved_map_picture_leaves_the_rigs_out(self) -> None:
        extras = radar.RadarExtras(rigs=(at(0, 40),), rig_gap_m=80.0)
        picture = radar.render_radar(None, RADIUS, HERE, 0.0, [], 480, 500.0, extras, center=at(0, 10))
        self.assertFalse(self.has(picture, radar._RIG_INSIDE_COLOR))


class SimulationRigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sim = simulation.SurfaceSimulation(clock=lambda: 1000.0)

    def test_the_simulation_has_its_own_rigs_and_a_gap_to_draw_bands_with(self) -> None:
        sources = self.sim.sources
        self.assertEqual(len(sources.rigs.rigs_for(simulation.SYSTEM, simulation.BODY)), 3)
        self.assertEqual(sources.rig_gap_override, simulation.SIM_RIG_GAP_M)
        self.assertIsNot(sources.rigs, rigs.rig_book)

    def test_placing_a_rig_in_the_simulation_does_not_touch_the_real_ones(self) -> None:
        from plugin import mining_live_window as live
        before = len(rigs.rig_book.rigs_for(simulation.SYSTEM, simulation.BODY))
        message = live.place_rig(self.sim.sources)
        self.assertTrue(message.startswith("Rig "), message)
        self.assertEqual(len(self.sim.sources.rigs.rigs_for(simulation.SYSTEM, simulation.BODY)), 4)
        self.assertEqual(len(rigs.rig_book.rigs_for(simulation.SYSTEM, simulation.BODY)), before)

    def test_placing_a_rig_with_no_position_says_why(self) -> None:
        from plugin import mining_live_window as live
        quiet = self.sim.sources
        quiet.position = lambda: None
        self.assertIn("cannot read your position", live.place_rig(quiet))


if __name__ == "__main__":
    unittest.main()
