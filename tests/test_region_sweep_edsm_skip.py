"""Unit tests for plugin/region_sweep_edsm_skip.py (no network, no Tk). Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin.region_sweep_edsm_skip import KnownSystemCache, skip_known_candidates  # noqa: E402


def _sequence(names):
    it = iter(names)
    return lambda: next(it, None)


class SkipKnownTests(unittest.TestCase):
    def test_unknown_candidate_is_kept(self):
        r = skip_known_candidates("A 1", _sequence(["A 2"]), lambda n: False, KnownSystemCache())
        self.assertEqual((r.candidate, r.skipped, r.gave_up, r.lookup_failed), ("A 1", 0, False, False))

    def test_steps_past_known_systems(self):
        known = {"A 1", "A 2"}
        r = skip_known_candidates("A 1", _sequence(["A 2", "A 3"]), lambda n: n in known, KnownSystemCache())
        self.assertEqual((r.candidate, r.skipped, r.lookup_failed), ("A 3", 2, False))

    def test_failed_lookup_skips_nothing(self):
        r = skip_known_candidates("A 1", _sequence(["A 2"]), lambda n: None, KnownSystemCache())
        self.assertEqual((r.candidate, r.skipped, r.lookup_failed), ("A 1", 0, True))

    def test_failure_after_skips_keeps_the_current_candidate(self):
        answers = {"A 1": True, "A 2": None}
        r = skip_known_candidates("A 1", _sequence(["A 2"]), lambda n: answers[n], KnownSystemCache())
        self.assertEqual((r.candidate, r.skipped, r.lookup_failed), ("A 2", 1, True))

    def test_failed_lookup_is_not_cached(self):
        cache = KnownSystemCache()
        skip_known_candidates("A 1", _sequence([]), lambda n: None, cache)
        self.assertEqual(len(cache), 0)

    def test_cap_stops_the_walk(self):
        names = [f"A {i}" for i in range(2, 50)]
        calls = []

        def lookup(n):
            calls.append(n)
            return True

        r = skip_known_candidates("A 1", _sequence(names), lookup, KnownSystemCache(), max_attempts=3)
        self.assertTrue(r.gave_up)
        self.assertEqual((r.candidate, r.skipped), ("A 4", 3))
        self.assertEqual(len(calls), 4)

    def test_cache_avoids_repeat_lookups_case_insensitively(self):
        cache = KnownSystemCache()
        calls = []

        def lookup(n):
            calls.append(n)
            return False

        skip_known_candidates("Foo AB-C d1-2", _sequence([]), lookup, cache)
        skip_known_candidates("FOO ab-c D1-2", _sequence([]), lookup, cache)
        self.assertEqual(len(calls), 1)

    def test_no_next_candidate_returns_last(self):
        r = skip_known_candidates("A 1", _sequence([]), lambda n: True, KnownSystemCache())
        self.assertEqual((r.candidate, r.skipped, r.gave_up), ("A 1", 0, False))

    def test_none_candidate(self):
        r = skip_known_candidates(None, _sequence([]), lambda n: True, KnownSystemCache())
        self.assertIsNone(r.candidate)


class CacheTests(unittest.TestCase):
    def test_bounded(self):
        cache = KnownSystemCache(max_entries=3)
        for i in range(10):
            cache.put(f"S{i}", True)
        self.assertEqual(len(cache), 3)
        self.assertIsNone(cache.get("S0"))
        self.assertTrue(cache.get("S9"))

    def test_clear(self):
        cache = KnownSystemCache()
        cache.put("X", False)
        cache.clear()
        self.assertIsNone(cache.get("X"))


if __name__ == "__main__":
    unittest.main()
