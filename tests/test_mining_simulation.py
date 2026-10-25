"""The Mining simulation shows pretend data and never touches the commander's own."""

import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))

from plugin import commander_data  # noqa: E402
from plugin import mining_coverage as coverage  # noqa: E402
from plugin import mining_hotspots as hotspots  # noqa: E402
from plugin import mining_simulation as simulation  # noqa: E402
from plugin import mining_sources  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402


class _Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class SimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = _Clock()
        self.sim = simulation.SurfaceSimulation(clock=self.clock)

    def test_the_world_has_something_to_look_at(self) -> None:
        sources = self.sim.sources
        self.assertTrue(sources.simulated)
        self.assertEqual(sources.surface.current_body, simulation.BODY)
        saved = sources.hotspots.for_body(simulation.SYSTEM, simulation.BODY)
        self.assertEqual(len(saved), 6)
        self.assertEqual([h.material for h in saved if h.amount == "Depleted"], ["Void Opals"])
        self.assertEqual(len([h for h in saved if not h.has_position()]), 1, "one deposit saved without a position, which the radar cannot place")
        self.assertEqual(len([h for h in saved if h.has_position()]), 5)
        body = sources.coverage.for_body(simulation.SYSTEM, simulation.BODY)
        self.assertEqual(len(body.sites), 2)
        self.assertIsNotNone(body.sites[0].border)
        self.assertIsNone(body.sites[1].border)
        position = self.sim.position()
        inside, _margin = body.inside(body.sites[0], position.latitude, position.longitude, simulation.PLANET_RADIUS_M)
        self.assertTrue(inside, "the Rhino drives inside the marked signal")
        self.assertGreater(len(body.points), 20, "ground already driven when the window opens")

    def test_the_rhino_moves_and_refines(self) -> None:
        first = self.sim.position()
        for _ in range(20):
            self.clock.now += 3.0
            self.sim.tick()
        later = self.sim.position()
        self.assertNotEqual((first.latitude, first.longitude), (later.latitude, later.longitude))
        self.assertIsNotNone(later.heading)
        run = self.sim.surface.current_run()
        self.assertTrue(run.refined)
        self.assertLessEqual(run.cargo, surface_mining.RHINO_CARGO_CAPACITY)

    def test_the_cargo_is_emptied_into_the_ship_when_full(self) -> None:
        for _ in range(200):
            self.clock.now += simulation.REFINE_EVERY_S
            self.sim.tick()
        run = self.sim.surface.current_run()
        self.assertTrue(run.transferred_to_ship)
        self.assertLessEqual(run.cargo, surface_mining.RHINO_CARGO_CAPACITY)

    def test_the_controls_act_on_the_pretend_data_only(self) -> None:
        real_hotspots = list(hotspots.hotspot_repository._hotspots)
        real_coverage = dict(coverage.coverage_repository._by_body)
        from plugin import mining_render as render
        self.assertIn("Center", render.mark_site(False, self.sim.sources))
        self.assertEqual(len(self.sim.sources.coverage.for_body(simulation.SYSTEM, simulation.BODY).sites), 3)
        self.assertEqual(real_hotspots, hotspots.hotspot_repository._hotspots)
        self.assertEqual(real_coverage, coverage.coverage_repository._by_body)

    def test_nothing_can_be_written(self) -> None:
        sources = self.sim.sources
        for repository in (sources.coverage, sources.hotspots):
            self.assertIsNone(repository._plugin_dir)
            self.assertEqual(repository._cmdr, "")
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(commander_data, "write", side_effect=AssertionError("wrote a file")):
            sources.coverage.mark(simulation.SYSTEM, simulation.BODY, 12.0, 40.0, simulation.PLANET_RADIUS_M, False)
            sources.hotspots.add(hotspots.Hotspot(system=simulation.SYSTEM, body=simulation.BODY, material="Painite", latitude=12.0, longitude=40.0))
            for _ in range(5):
                self.clock.now += 5.0
                self.sim.tick()
            self.assertEqual(os.listdir(folder), [])

    def test_it_does_not_share_the_real_repositories(self) -> None:
        real = mining_sources.real()
        sources = self.sim.sources
        for name in ("surface", "coverage", "hotspots", "space"):
            self.assertIsNot(getattr(sources, name), getattr(real, name), name)


if __name__ == "__main__":
    unittest.main()
