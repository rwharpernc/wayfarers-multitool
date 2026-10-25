"""
Unit tests for plugin/rare_goods.py and plugin/powerplay_control_lookup.py.

No EDMC runtime or network needed - the Spansh call is mocked. Run with:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import powerplay_control_lookup as lookup  # noqa: E402
from plugin import rare_goods  # noqa: E402


class DatasetTests(unittest.TestCase):
    def test_dataset_loads_with_expected_shape(self) -> None:
        self.assertEqual(rare_goods.dataset_size(), 141)
        for entry in rare_goods._load():
            for key in ("rare", "inaraId", "system", "station", "pad", "coords"):
                self.assertIn(key, entry, entry.get("rare"))
            for axis in ("x", "y", "z"):
                self.assertIsInstance(entry["coords"][axis], (int, float))

    def test_inara_ids_are_unique(self) -> None:
        # The window uses the Inara id as the tree row id, so a duplicate
        # would raise on insert.
        ids = [e["inaraId"] for e in rare_goods._load()]
        self.assertEqual(len(ids), len(set(ids)))


class NearestTests(unittest.TestCase):
    def test_sorted_nearest_first_and_limited(self) -> None:
        results = rare_goods.nearest((75.75, 48.75, 70.75), limit=5)  # Lave's own coords
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0]["rare"], "Lavian Brandy")
        self.assertAlmostEqual(results[0]["distance_ly"], 0.0)
        distances = [r["distance_ly"] for r in results]
        self.assertEqual(distances, sorted(distances))

    def test_limit_larger_than_dataset_and_zero(self) -> None:
        self.assertEqual(len(rare_goods.nearest((0, 0, 0), limit=10_000)), rare_goods.dataset_size())
        self.assertEqual(rare_goods.nearest((0, 0, 0), limit=0), [])

    def test_does_not_mutate_cached_dataset(self) -> None:
        rare_goods.nearest((0, 0, 0), limit=3)
        self.assertNotIn("distance_ly", rare_goods._load()[0])

    def test_distance_text(self) -> None:
        self.assertEqual(rare_goods.distance_text(0.0), "0.0 ly")
        self.assertEqual(rare_goods.distance_text(42.26), "42.3 ly")
        self.assertEqual(rare_goods.distance_text(21345.678), "21,345.7 ly")

    def test_arrival_text(self) -> None:
        self.assertEqual(rare_goods.arrival_text(288), "288 ls")
        self.assertEqual(rare_goods.arrival_text(6395387), "6,395,387 ls")
        for unknown in (None, "x", True):
            self.assertEqual(rare_goods.arrival_text(unknown), "—")

    def test_every_rare_has_an_arrival_distance(self) -> None:
        for entry in rare_goods._load():
            self.assertIsInstance(entry["distanceToStarLs"], int, entry["rare"])
            self.assertGreater(entry["distanceToStarLs"], 0, entry["rare"])

    def test_clean_government(self) -> None:
        self.assertEqual(rare_goods.clean_government("$government_PrisonColony;", "Prison colony"), "Prison colony")
        self.assertEqual(rare_goods.clean_government("$government_Democracy;"), "Democracy")
        self.assertEqual(rare_goods.clean_government("Theocracy"), "Theocracy")
        for none in (None, "", "$government_None;"):
            self.assertIsNone(rare_goods.clean_government(none))

    def test_legality_in_a_system(self) -> None:
        by_name = {e["rare"]: e for e in rare_goods._load()}
        brandy, onion, plain = by_name["Lavian Brandy"], by_name["Onionhead"], by_name["Altairian Skin"]
        self.assertEqual(rare_goods.legality_text(plain, "Federation", "Theocracy"), "Legal")
        self.assertEqual(rare_goods.legality_text(brandy), "Restricted")                                  # not known where you are
        self.assertEqual(rare_goods.legality_text(brandy, "Federation", "Theocracy"), "Illegal here")    # a superpower with a government
        self.assertEqual(rare_goods.legality_text(brandy, "Independent", "Prison colony"), "Illegal here")    # a government of any allegiance, any spelling
        self.assertEqual(rare_goods.legality_text(brandy, "Federation", "Democracy"), "Legal here")
        self.assertEqual(rare_goods.legality_text(brandy, "Independent", None), "Restricted")             # a government that could matter is missing
        self.assertEqual(rare_goods.legality_text(onion, "Empire", None), "Illegal here")                 # a whole superpower needs no government
        self.assertEqual(rare_goods.legality_text(onion, "Alliance", "Democracy"), "Illegal here")
        self.assertEqual(rare_goods.legality_text(onion, "Alliance", "Anarchy"), "Legal here")

    def test_restriction_details(self) -> None:
        by_name = {e["rare"]: e for e in rare_goods._load()}
        self.assertEqual(rare_goods.restriction_details(by_name["Altairian Skin"]), "no restrictions listed")
        self.assertIn("Prison Colony", rare_goods.restriction_details(by_name["Lavian Brandy"]))
        self.assertIn("Federation Theocracy", rare_goods.restriction_details(by_name["Lavian Brandy"]))
        self.assertIn("all Federation and Empire space", rare_goods.restriction_details(by_name["Onionhead"]))

    def test_candidates_are_all_the_rares_nearest_first_and_can_be_large_pads_only(self) -> None:
        everything = rare_goods.candidates((0, 0, 0))
        self.assertEqual(len(everything), rare_goods.dataset_size())
        self.assertEqual([e["distance_ly"] for e in everything], sorted(e["distance_ly"] for e in everything))
        large = rare_goods.candidates((0, 0, 0), large_only=True)
        self.assertTrue(large and all(e["pad"] == "L" for e in large))
        self.assertEqual(len(large), sum(1 for e in everything if e["pad"] == "L"))

    def test_same_power(self) -> None:
        self.assertTrue(rare_goods.same_power("Aisling Duval", "aisling  duval"))
        self.assertFalse(rare_goods.same_power("Aisling Duval", "Zemina Torval"))
        self.assertFalse(rare_goods.same_power(None, None))
        self.assertFalse(rare_goods.same_power("", ""))

    def test_inara_url(self) -> None:
        self.assertEqual(rare_goods.inara_commodity_url(10006), "https://inara.cz/elite/commodity/10006/")


def _fake_response(payload: dict) -> bytes:
    return json.dumps(payload).encode("utf-8")


class ControlLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        lookup._cache.clear()

    def test_fetch_one_caches_power_and_unclaimed(self) -> None:
        with mock.patch.object(
            lookup.spansh_courtesy, "call",
            side_effect=[_fake_response({"record": {"controlling_power": "Aisling Duval"}}),
                         _fake_response({"record": {}})],
        ):
            self.assertEqual(lookup._fetch_one(1), "Aisling Duval")
            self.assertIsNone(lookup._fetch_one(2))
        self.assertEqual(lookup.cached(1), (True, "Aisling Duval"))
        self.assertEqual(lookup.cached(2), (True, None))
        self.assertEqual(lookup.cached(3), (False, None))

    def test_failed_lookup_is_cached_as_unresolved_power(self) -> None:
        with mock.patch.object(lookup.spansh_courtesy, "call", side_effect=OSError("down")):
            self.assertIsNone(lookup._fetch_one(9))
        self.assertEqual(lookup.cached(9), (True, None))

    def test_fetch_missing_skips_cached_and_reports_results(self) -> None:
        lookup._cache[1] = "Zachary Hudson"
        got: dict = {}
        done = threading.Event()

        def on_result(id64: int, power) -> None:
            got[id64] = power
            done.set()

        with mock.patch.object(
            lookup.spansh_courtesy, "call",
            return_value=_fake_response({"record": {"controlling_power": "Nakato Kaine"}}),
        ) as urlopen:
            lookup.fetch_missing([1, 2], on_result)
            self.assertTrue(done.wait(5))
        self.assertEqual(got, {2: "Nakato Kaine"})
        self.assertEqual(urlopen.call_count, 1)

    def test_fetch_missing_spawns_nothing_when_all_cached(self) -> None:
        lookup._cache[1] = None
        with mock.patch.object(lookup.threading, "Thread") as thread:
            lookup.fetch_missing([1], lambda *_: None)
        thread.assert_not_called()


if __name__ == "__main__":
    unittest.main()
