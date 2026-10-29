"""
Unit tests for plugin/mining_coverage.py.

Pure logic tests - no EDMC runtime needed. Run with:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))

from plugin import mining_coverage as coverage  # noqa: E402

_EARTH_RADIUS_M = 6_371_000.0


class BodyCoverageTests(unittest.TestCase):
    def test_first_point_sets_center_and_is_recorded(self) -> None:
        body = coverage.BodyCoverage()
        added = body.record(10.0, 20.0, _EARTH_RADIUS_M)
        self.assertTrue(added)
        self.assertEqual(body.center, coverage.CoveragePoint(10.0, 20.0))
        self.assertEqual(len(body.points), 1)

    def test_point_too_close_to_last_is_rejected(self) -> None:
        body = coverage.BodyCoverage()
        body.record(10.0, 20.0, _EARTH_RADIUS_M)
        # ~11m north - well under STAMP_M (250m).
        added = body.record(10.0001, 20.0, _EARTH_RADIUS_M)
        self.assertFalse(added)
        self.assertEqual(len(body.points), 1)

    def test_point_far_enough_is_recorded(self) -> None:
        body = coverage.BodyCoverage()
        body.record(10.0, 20.0, _EARTH_RADIUS_M)
        # ~1.1km north - comfortably over STAMP_M.
        added = body.record(10.01, 20.0, _EARTH_RADIUS_M)
        self.assertTrue(added)
        self.assertEqual(len(body.points), 2)

    def test_points_capped_at_max(self) -> None:
        body = coverage.BodyCoverage()
        original_max = coverage.MAX_POINTS_PER_BODY
        coverage.MAX_POINTS_PER_BODY = 3
        try:
            lat = 10.0
            for _ in range(5):
                body.record(lat, 20.0, _EARTH_RADIUS_M)
                lat += 0.01  # each step is well over STAMP_M
            self.assertEqual(len(body.points), 3)
            # The oldest points were dropped, not the newest.
            self.assertAlmostEqual(body.points[-1].latitude, lat - 0.01, places=6)
        finally:
            coverage.MAX_POINTS_PER_BODY = original_max


class CoverageRepositoryTests(unittest.TestCase):
    def test_record_and_for_body_round_trip(self) -> None:
        repo = coverage.CoverageRepository()
        with tempfile.TemporaryDirectory() as plugin_dir:
            repo.load(plugin_dir)
            repo.record("Sol", "Earth", 10.0, 20.0, _EARTH_RADIUS_M)
            found = repo.for_body("Sol", "Earth")
            self.assertIsNotNone(found)
            self.assertEqual(len(found.points), 1)

    def test_for_body_is_case_insensitive(self) -> None:
        repo = coverage.CoverageRepository()
        with tempfile.TemporaryDirectory() as plugin_dir:
            repo.load(plugin_dir)
            repo.record("Sol", "Earth", 10.0, 20.0, _EARTH_RADIUS_M)
            self.assertIsNotNone(repo.for_body("sol", "earth"))

    def test_unknown_body_returns_none(self) -> None:
        repo = coverage.CoverageRepository()
        self.assertIsNone(repo.for_body("Sol", "Earth"))
        self.assertIsNone(repo.for_body(None, None))

    def test_persists_across_reload(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_dir:
            repo = coverage.CoverageRepository()
            repo.load(plugin_dir)
            repo.set_commander("Alice")
            repo.record("Sol", "Earth", 10.0, 20.0, _EARTH_RADIUS_M)
            repo.record("Sol", "Earth", 10.01, 20.0, _EARTH_RADIUS_M)

            reloaded = coverage.CoverageRepository()
            reloaded.load(plugin_dir)
            reloaded.set_commander("ALICE")   # the journal may write the name in another case
            found = reloaded.for_body("Sol", "Earth")
            self.assertIsNotNone(found)
            self.assertEqual(len(found.points), 2)
            self.assertEqual(found.center, coverage.CoveragePoint(10.0, 20.0))

    def test_clear_body_removes_it(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_dir:
            repo = coverage.CoverageRepository()
            repo.load(plugin_dir)
            repo.record("Sol", "Earth", 10.0, 20.0, _EARTH_RADIUS_M)
            repo.clear_body("Sol", "Earth")
            self.assertIsNone(repo.for_body("Sol", "Earth"))

    def test_missing_file_loads_as_empty(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_dir:
            repo = coverage.CoverageRepository()
            repo.load(plugin_dir)  # no mining_coverage.json exists yet
            self.assertIsNone(repo.for_body("Sol", "Earth"))


class SiteMarkTests(unittest.TestCase):
    R = 400_000.0                       # a body 400 km in radius
    M_PER_DEG = 3.14159265358979 * 400_000.0 / 180.0

    def north(self, meters: float) -> float:
        return meters / self.M_PER_DEG

    def test_center_then_border_gives_the_radius(self) -> None:
        body = coverage.BodyCoverage()
        self.assertIn("press Mark border", body.mark_center(10.0, 20.0, self.R))
        message = body.mark_border(10.0 + self.north(1500), 20.0, self.R)
        self.assertIn("1.50 km", message)
        self.assertAlmostEqual(body.sites[0].radius_m(self.R), 1500.0, delta=2.0)

    def test_center_again_nearby_moves_it_and_far_away_starts_another_site(self) -> None:
        body = coverage.BodyCoverage()
        body.mark_center(10.0, 20.0, self.R)
        self.assertEqual(body.mark_center(10.0 + self.north(50), 20.0, self.R), "Center moved.")
        self.assertEqual(len(body.sites), 1)
        body.mark_center(10.0 + self.north(5000), 20.0, self.R)
        self.assertEqual(len(body.sites), 2)

    def test_border_needs_a_center_and_a_distance_from_it(self) -> None:
        body = coverage.BodyCoverage()
        self.assertIn("press Mark center first", body.mark_border(10.0, 20.0, self.R))
        body.mark_center(10.0, 20.0, self.R)
        self.assertIn("only", body.mark_border(10.0 + self.north(20), 20.0, self.R))
        self.assertIsNone(body.sites[0].border)

    def test_border_goes_to_the_nearest_site(self) -> None:
        body = coverage.BodyCoverage()
        body.mark_center(10.0, 20.0, self.R)
        body.mark_center(10.0 + self.north(8000), 20.0, self.R)
        body.mark_border(10.0 + self.north(8000 + 1200), 20.0, self.R)
        self.assertIsNone(body.sites[0].border)
        self.assertAlmostEqual(body.sites[1].radius_m(self.R), 1200.0, delta=2.0)

    def test_inside_says_whether_you_are_within_the_marked_circle(self) -> None:
        body = coverage.BodyCoverage()
        body.mark_center(10.0, 20.0, self.R)
        site = body.sites[0]
        self.assertIsNone(body.inside(site, 10.0, 20.0, self.R), "no border yet")
        body.mark_border(10.0 + self.north(1500), 20.0, self.R)
        inside, margin = body.inside(site, 10.0 + self.north(1000), 20.0, self.R)
        self.assertTrue(inside)
        self.assertAlmostEqual(margin, 500.0, delta=2.0)
        inside, margin = body.inside(site, 10.0 + self.north(1800), 20.0, self.R)
        self.assertFalse(inside)
        self.assertAlmostEqual(margin, 300.0, delta=2.0)

    def test_edge_covered_counts_the_border_within_reach_of_ground_driven(self) -> None:
        body = coverage.BodyCoverage()
        body.mark_center(10.0, 20.0, self.R)
        site = body.sites[0]
        self.assertIsNone(body.edge_covered(site, self.R), "no border yet")
        body.mark_border(10.0 + self.north(3000), 20.0, self.R)
        self.assertEqual(body.edge_covered(site, self.R), 0.0)
        body.points.append(coverage.CoveragePoint(10.0, 20.0))          # driven only at the center: 3 km from the edge, out of the 2 km reach
        self.assertEqual(body.edge_covered(site, self.R), 0.0)
        for bearing_deg in range(0, 360, 10):                         # driven all the way round
            body.points.append(coverage.point_at(site.center, bearing_deg, 3000.0, self.R))
        self.assertEqual(body.edge_covered(site, self.R), 1.0)

    def test_the_minimap_draws_a_marked_location_even_before_any_driving(self) -> None:
        from plugin import mining_coverage_render as render
        body = coverage.BodyCoverage()
        body.mark_center(10.0, 20.0, self.R)
        body.mark_border(10.0 + self.north(1500), 20.0, self.R)
        image = render.render(body, self.R, None, [])
        self.assertIsNotNone(image)
        colors = {image.getpixel((x, y)) for x in range(image.width) for y in range(image.height)}
        self.assertIn(render._SITE_COLOR, colors)

    def test_the_radar_is_centered_on_you_and_draws_what_is_around_you(self) -> None:
        from plugin import mining_coverage_render as render
        from plugin import mining_hotspots as hotspots
        body = coverage.BodyCoverage()
        body.mark_center(10.0 + self.north(300), 20.0, self.R)
        body.mark_border(10.0 + self.north(900), 20.0, self.R)
        spot = hotspots.Hotspot(system="S", body="B", material="Painite", rigs=4, latitude=10.0 + self.north(500), longitude=20.0)
        here = coverage.CoveragePoint(10.0, 20.0)
        image = render.render_radar(body, self.R, here, 90.0, [spot], 400, 1000.0)
        self.assertEqual(image.size, (400, 400), "a fixed square of the size asked for")
        colors = {image.getpixel((x, y)) for x in range(0, 400) for y in range(0, 400)}
        for name in ("_SITE_COLOR", "_HOTSPOT_COLOR", "_POSITION_COLOR"):
            self.assertIn(getattr(render, name), colors, f"{name} is not on the radar")
        self.assertIsNone(render.render_radar(body, self.R, None, 90.0, [], 400), "no position, no radar")
        self.assertIsNone(render.render_radar(body, None, here, 90.0, [], 400), "no body radius, no radar")
        self.assertEqual(render.render_radar(body, self.R, here, None, [], 99999).size, (1600, 1600), "the size is capped")
        self.assertEqual(render.render_radar(body, self.R, here, None, [], 10).size, (160, 160), "and has a floor")
        self.assertEqual((render.range_text(500.0), render.range_text(2000.0), render.range_text(1500.0)), ("500 m", "2 km", "1.5 km"))

    def test_the_radar_places_a_deposit_by_its_distance_and_direction(self) -> None:
        from plugin import mining_coverage_render as render
        from plugin import mining_hotspots as hotspots
        here = coverage.CoveragePoint(10.0, 20.0)
        north = hotspots.Hotspot(system="S", body="B", material="Painite", rigs=4, latitude=10.0 + self.north(500), longitude=20.0)
        image = render.render_radar(None, self.R, here, None, [north], 400, 1000.0)
        spot_pixels = [(x, y) for x in range(400) for y in range(400) if image.getpixel((x, y)) == render._HOTSPOT_COLOR]
        xs, ys = [p[0] for p in spot_pixels], [p[1] for p in spot_pixels]
        self.assertTrue(190 <= min(xs) and max(xs) <= 210, "due north is straight above the center")
        self.assertTrue(90 <= min(ys) <= 110, f"500 m of a 1 km radar is half way out (100 px above the center): {min(ys)}")

    def test_marks_are_saved_per_commander_and_reloaded(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_dir:
            repo = coverage.CoverageRepository()
            repo.load(plugin_dir)
            repo.set_commander("Alice")
            repo.mark("Sol", "Earth", 10.0, 20.0, self.R, border=False)
            repo.mark("Sol", "Earth", 10.0 + self.north(900), 20.0, self.R, border=True)
            self.assertIn("land first", repo.mark("", "", 1.0, 1.0, self.R, border=False))

            reloaded = coverage.CoverageRepository()
            reloaded.load(plugin_dir)
            reloaded.set_commander("Bob")
            self.assertIsNone(reloaded.for_body("Sol", "Earth"), "another commander has no marks")
            reloaded.set_commander("Alice")
            site = reloaded.for_body("Sol", "Earth").sites[0]
            self.assertAlmostEqual(site.radius_m(self.R), 900.0, delta=2.0)


if __name__ == "__main__":
    unittest.main()
