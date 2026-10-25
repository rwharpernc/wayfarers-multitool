"""Tests for neutron_finder.pick_nearest against canned Spansh responses."""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import neutron_finder, star_index  # noqa: E402
from plugin import star_index_build  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import star_index_fixtures as fixtures  # noqa: E402


def _body(system, distance, region="Inner Orion Spur"):
    return {"system_name": system, "distance": distance, "system_region": region}


class PickNearestTests(unittest.TestCase):
    def test_returns_closest(self):
        found = neutron_finder.pick_nearest({"results": [_body("A", 12.5), _body("B", 20)]}, None)
        self.assertEqual((found.system, found.distance_ly), ("A", 12.5))

    def test_skips_current_system_case_insensitively(self):
        found = neutron_finder.pick_nearest({"results": [_body("PSR J1", 0.0), _body("B", 20)]}, "psr j1")
        self.assertEqual(found.system, "B")

    def test_no_usable_result_raises(self):
        with self.assertRaises(ValueError):
            neutron_finder.pick_nearest({"results": [_body("Here", 0.0)]}, "Here")
        with self.assertRaises(ValueError):
            neutron_finder.pick_nearest({"results": []}, None)
        with self.assertRaises(ValueError):
            neutron_finder.pick_nearest({"error": "x"}, None)

    def test_white_dwarf_subtypes_cover_every_class(self):
        self.assertIn("White Dwarf (DA) Star", neutron_finder.WHITE_DWARF_SUBTYPES)
        self.assertIn("White Dwarf (DQ) Star", neutron_finder.WHITE_DWARF_SUBTYPES)
        self.assertEqual(len(set(neutron_finder.WHITE_DWARF_SUBTYPES)), 14)

    def test_display_name_is_capped(self):
        long_name = "X" * 200
        self.assertEqual(len(neutron_finder.display_name(long_name)), neutron_finder.MAX_NAME_CHARS)
        self.assertEqual(neutron_finder.display_name("Sol"), "Sol")


class LocalIndexTests(unittest.TestCase):
    """The N.S. button uses the local index when there is a usable one and asks Spansh otherwise."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = os.path.join(self._tmp.name, "star_index")
        star_index.forget()
        self.addCleanup(star_index.forget)
        patcher = mock.patch.object(star_index, "default_dir", return_value=self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.stars = fixtures.make_stars(600, spread=1500.0, flat=300.0)
        self.spansh = mock.patch.object(neutron_finder, "find_nearest_primary",
                                        return_value=neutron_finder.NearestStar("From Spansh", 99.0, "Orion Spur"))
        self.asked = self.spansh.start()
        self.addCleanup(self.spansh.stop)

    def install(self):
        dump = os.path.join(self._tmp.name, "d.json.gz")
        fixtures.write_dump(dump, self.stars, extras=50)
        star_index_build.build(dump, self.dir, {})

    def test_with_no_index_spansh_answers_and_says_so(self):
        found = neutron_finder.find_nearest_neutron(10, 20, 30)
        self.assertEqual((found.system, found.source), ("From Spansh", "Spansh"))
        self.asked.assert_called_once()

    def test_with_an_index_it_answers_locally_without_asking_spansh(self):
        self.install()
        star = self.stars[5]
        found = neutron_finder.find_nearest_neutron(star.x + 1, star.y, star.z)
        self.assertEqual((found.system, found.source), (star.name, "local index"))
        self.assertAlmostEqual(found.distance_ly, 1.0, places=5)
        self.assertEqual(found.region, "")
        self.asked.assert_not_called()

    def test_the_commanders_own_system_is_skipped(self):
        self.install()
        near = fixtures.brute_nearest(self.stars, 0, 0, 0, 2)
        by_id = {s.id64: s for s in self.stars}
        first, second = by_id[near[0][1]], by_id[near[1][1]]
        found = neutron_finder.find_nearest_neutron(0, 0, 0, current_system=first.name.upper())
        self.assertEqual(found.system, second.name)
        self.assertAlmostEqual(found.distance_ly, near[1][0], places=5)

    def test_the_switch_turns_the_local_index_off(self):
        self.install()
        with mock.patch.object(star_index, "use_local_index", return_value=False):
            found = neutron_finder.find_nearest_neutron(0, 0, 0)
        self.assertEqual(found.source, "Spansh")
        self.asked.assert_called_once()

    def test_a_damaged_index_falls_back_to_spansh_and_says_why(self):
        self.install()
        with open(star_index.index_path(self.dir), "r+b") as handle:
            handle.truncate(3000)
        star_index.forget()
        found = neutron_finder.find_nearest_neutron(0, 0, 0)
        self.assertEqual(found.system, "From Spansh")
        self.assertIn("not usable", found.source)

    def test_an_index_from_another_format_falls_back_to_spansh(self):
        self.install()
        with open(star_index.index_path(self.dir), "r+b") as handle:
            handle.seek(4)
            handle.write(b"\x63\x00")
        star_index.forget()
        found = neutron_finder.find_nearest_neutron(0, 0, 0)
        self.assertIn("another version", found.source)

    def test_nothing_near_enough_in_the_index_asks_spansh(self):
        self.install()
        found = neutron_finder.find_nearest_neutron(90000, 0, 90000)
        self.assertEqual(found.system, "From Spansh")

    def test_a_failure_while_reading_falls_back_to_spansh(self):
        self.install()
        with mock.patch.object(star_index, "nearest_stars", side_effect=OSError("disk error")):
            found = neutron_finder.find_nearest_neutron(0, 0, 0)
        self.assertEqual(found.system, "From Spansh")

    def test_white_dwarfs_always_ask_spansh(self):
        self.install()
        neutron_finder.find_nearest_white_dwarf(0, 0, 0)
        self.asked.assert_called_once()
        self.assertEqual(self.asked.call_args[0][0], neutron_finder.WHITE_DWARF_SUBTYPES)

    def test_the_local_answer_needs_no_network(self):
        self.install()
        with mock.patch.object(neutron_finder.spansh_courtesy, "call", side_effect=AssertionError("network used")):
            self.assertEqual(neutron_finder.find_nearest_neutron(0, 0, 0).source, "local index")


if __name__ == "__main__":
    unittest.main()
