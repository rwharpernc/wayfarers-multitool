"""The journal systems behind the suggestions (system_names.py): a typed start is found by bisection, a name typed in full is known whatever its capitals, and
`system_history.py` hands over only the playing commander's systems."""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"  # type: ignore[attr-defined]
    _stub.config = types.SimpleNamespace(get_bool=lambda key, default=False: False, get_str=lambda *_a, **_k: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import system_history as H  # noqa: E402
from plugin import system_names as N  # noqa: E402


class HistoryHandOverTests(unittest.TestCase):
    def setUp(self):
        N.clear()

    def history_with(self, cmdr, *names):
        history = H.SystemHistory()
        history._cmdr = cmdr
        payload = H.commander_data.payload_for(history._store, cmdr, H._empty)
        for name in names:
            payload["systems"][name.casefold()] = {"name": name, "visits": 1}
        return history

    def test_the_names_are_every_saved_and_live_system_once(self):
        history = self.history_with("Alpha", "Sol", "Colonia")
        history._live = {"sol": {"name": "SOL", "visits": 1}, "beagle point": {"name": "Beagle Point", "visits": 1}}
        self.assertEqual(sorted(history.names()), ["Beagle Point", "Colonia", "Sol"])

    def test_publishing_replaces_the_suggestions_with_the_playing_commanders_systems(self):
        alpha = self.history_with("Alpha", "Sol")
        beta = self.history_with("Beta", "Solitude")
        alpha._publish()
        self.assertEqual(N.visited_matches("so"), ["Sol"])
        beta._publish()
        self.assertEqual(N.visited_matches("so"), ["Solitude"], "nothing of the last commander's stays")

    def test_no_commander_and_no_history_give_no_names(self):
        self.assertEqual(H.SystemHistory().names(), [])
        self.assertEqual(self.history_with("Alpha").names(), [])


class LookupTests(unittest.TestCase):
    def setUp(self):
        N.clear()
        N.set_visited(["Sol", "Solitude", "Colonia", "Beagle Point", "sol", "Wolf 359"])

    def test_a_typed_start_finds_systems_a_to_z_whatever_the_capitals(self):
        self.assertEqual(N.visited_matches("SO"), ["Sol", "Solitude"])
        self.assertEqual(N.visited_matches("col"), ["Colonia"])
        self.assertEqual(N.visited_matches("zzz"), [])
        self.assertEqual(N.visited_matches(""), [])

    def test_the_limit_is_kept(self):
        N.set_visited([f"Sys {n:03d}" for n in range(100)])
        self.assertEqual(len(N.visited_matches("sys", limit=5)), 5)

    def test_a_name_typed_in_full_is_known_in_any_capitals(self):
        self.assertTrue(N.knows("sol"))
        self.assertTrue(N.knows("BEAGLE POINT"))
        self.assertFalse(N.knows("Beagle"))
        self.assertTrue(N.knows("Registered Today") is False)
        N.remember("Registered Today")
        self.assertTrue(N.knows("registered today"))

    def test_local_suggestions_put_the_sessions_systems_first_then_the_journals(self):
        N.remember("Soho")
        self.assertEqual(N.suggest_local("so")[:3], ["Soho", "Sol", "Solitude"])
        self.assertEqual(N.suggest_local("s"), [], "two letters, as in the boxes")

    def test_a_large_history_is_looked_up_without_scanning_it(self):
        N.set_visited([f"Sector {n:06d} AB-C d1-2" for n in range(60000)])
        import time
        start = time.perf_counter()
        for _ in range(200):
            N.visited_matches("sector 0123")
        self.assertLess(time.perf_counter() - start, 1.0, "200 lookups in 60,000 systems")


if __name__ == "__main__":
    unittest.main()
