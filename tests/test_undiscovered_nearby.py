"""RND's source of systems (undiscovered_nearby.py): real systems from Spansh, filtered to those with no scans on record.

No test touches a live service. RND used to guess names inside a boxel; these tests pin the replacement's contract: only
systems Spansh listed are ever offered, a scanned system or one the commander already visited is dropped, and the request
is a nearest-first search around the given position.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def entry(name, body_count=None, distance=10.0):
    return {"name": name, "id64": 1, "distance": distance, "body_count": body_count}


class UndiscoveredNearbyTests(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType("config")
        config.appname = "EDMarketConnector"
        config.user_agent = "EDMarketConnector/6.1.2"
        config.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
        patcher = mock.patch.dict(sys.modules, {"config": config})
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in [m for m in sys.modules if m in ("plugin.undiscovered_nearby", "plugin.http_identity")]:
            sys.modules.pop(name)
        self.module = importlib.import_module("plugin.undiscovered_nearby")

    def fetch(self, data):
        with mock.patch.object(self.module.spansh_courtesy, "call", return_value=json.dumps(data).encode("utf-8")) as opened:
            return self.module.fetch_nearby(1.0, 2.0, 3.0), opened

    def test_the_request_is_a_nearest_first_search_around_the_position(self):
        _, opened = self.fetch({"results": []})
        request = opened.call_args[0][0]
        sent = json.loads(request.data.decode("utf-8"))
        self.assertEqual(sent["reference_coords"], {"x": 1.0, "y": 2.0, "z": 3.0})
        self.assertEqual(sent["sort"], [{"distance": {"direction": "asc"}}])
        self.assertIn("WFMT", request.get_header("User-agent"))
        self.assertEqual(opened.call_args[0][1], self.module.REQUEST_TIMEOUT_S)

    def test_a_busy_spansh_raises_an_oserror_for_the_caller_to_report(self):
        busy = self.module.spansh_courtesy.SpanshBusy("Spansh has not been answering.")
        with mock.patch.object(self.module.spansh_courtesy, "call", side_effect=busy):
            with self.assertRaises(OSError):
                self.module.fetch_nearby(1.0, 2.0, 3.0)

    def test_results_come_back_in_the_order_spansh_gave_them(self):
        results, _ = self.fetch({"results": [entry("A b1-1"), "junk", entry("A b1-2")]})
        self.assertEqual([r["name"] for r in results], ["A b1-1", "A b1-2"])

    def test_a_surprising_shape_raises_instead_of_looking_like_no_systems(self):
        with self.assertRaises(ValueError):
            self.fetch(["not", "a", "dict"])

    def test_only_systems_without_scans_are_kept(self):
        entries = [entry("Scanned a1-1", body_count=22), entry("Blank a1-2"), entry("Zero a1-3", body_count=0)]
        kept = self.module.unscanned(entries, frozenset())
        self.assertEqual([e["name"] for e in kept], ["Blank a1-2", "Zero a1-3"])

    def test_visited_systems_and_the_current_one_are_dropped(self):
        entries = [entry("Been a1-1"), entry("Here a1-2"), entry("New a1-3")]
        kept = self.module.unscanned(entries, frozenset({"Been a1-1"}), here="Here a1-2")
        self.assertEqual([e["name"] for e in kept], ["New a1-3"])

    def test_pick_order_keeps_every_candidate_and_leads_with_the_nearest_pool(self):
        candidates = [entry(f"S a1-{i}", distance=float(i)) for i in range(30)]
        ordered = self.module.pick_order(candidates, pool=5)
        self.assertEqual(len(ordered), 30)
        self.assertEqual({e["name"] for e in ordered[:5]}, {e["name"] for e in candidates[:5]})
        self.assertEqual(ordered[5:], candidates[5:])


class NearbyCacheTests(unittest.TestCase):
    def setUp(self):
        UndiscoveredNearbyTests.setUp(self)
        self.now = [0.0]
        self.cache = self.module.NearbyCache(ttl=600.0, radius=5.0, clock=lambda: self.now[0])
        self.entries = [entry("A a1-1"), entry("A a1-2")]

    def test_nothing_is_cached_until_a_list_is_put(self):
        self.assertIsNone(self.cache.get(0, 0, 0, 25))

    def test_the_list_is_reused_near_the_fetch_position_and_size(self):
        self.cache.put(0, 0, 0, 25, self.entries)
        self.assertEqual(len(self.cache.get(3, 0, 0, 25)), 2)
        self.assertIsNone(self.cache.get(6, 0, 0, 25))     # moved past the radius
        self.assertIsNone(self.cache.get(0, 0, 0, 50))     # the setting changed

    def test_the_list_expires(self):
        self.cache.put(0, 0, 0, 25, self.entries)
        self.now[0] = 599.0
        self.assertIsNotNone(self.cache.get(0, 0, 0, 25))
        self.now[0] = 601.0
        self.assertIsNone(self.cache.get(0, 0, 0, 25))

    def test_used_names_are_not_offered_again_and_a_new_fetch_resets_them(self):
        self.cache.put(0, 0, 0, 25, self.entries)
        self.cache.mark_used("A a1-1")
        self.assertEqual([e["name"] for e in self.cache.get(0, 0, 0, 25)], ["A a1-2"])
        self.cache.put(0, 0, 0, 25, self.entries)
        self.assertEqual(len(self.cache.get(0, 0, 0, 25)), 2)

    def test_distance_comes_from_the_entry_coordinates_when_present(self):
        module = self.module
        self.assertAlmostEqual(module.distance_from({"x": 3, "y": 4, "z": 0}, (0, 0, 0)), 5.0)
        self.assertEqual(module.distance_from({"distance": 7.5}, (0, 0, 0)), 7.5)


if __name__ == "__main__":
    unittest.main()
