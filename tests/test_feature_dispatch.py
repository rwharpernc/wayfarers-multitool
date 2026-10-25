"""
feature_dispatch: one feature raising on a journal event must not stop the others getting it (plugin/feature_dispatch.py), and no plugin module may
use a name it never defines (for example, a call to a function an edit had deleted would raise on EDMC's
StartUp event, so every feature after it would never learn the commander).

Pure Python - no EDMC runtime needed. Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import glob
import io
import logging
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import feature_dispatch  # noqa: E402

LOG = logging.getLogger("test.feature_dispatch")


def _feature(name: str, seen: list, fail: bool = False) -> types.SimpleNamespace:
    def handle_event(entry, cmdr, system, station, state):
        seen.append((name, entry["event"], cmdr))
        if fail:
            raise NameError(f"{name} is broken")
    return types.SimpleNamespace(__name__=name, handle_event=handle_event)


class DispatchTests(unittest.TestCase):
    def test_every_feature_gets_the_event_in_order(self) -> None:
        seen: list = []
        failed = feature_dispatch.dispatch([_feature("a", seen), _feature("b", seen)], {"event": "StartUp"}, "CMDR", "Sol", None, {}, LOG)
        self.assertEqual((failed, seen), (0, [("a", "StartUp", "CMDR"), ("b", "StartUp", "CMDR")]))

    def test_a_feature_that_raises_does_not_starve_the_ones_after_it(self) -> None:
        seen: list = []
        features = [_feature("a", seen), _feature("broken", seen, fail=True), _feature("bgs", seen)]
        with self.assertLogs(LOG, level="ERROR") as logged:
            failed = feature_dispatch.dispatch(features, {"event": "StartUp"}, "SILAS KADE", None, None, {}, LOG)
        self.assertEqual(failed, 1)
        self.assertEqual([name for name, _event, _cmdr in seen], ["a", "broken", "bgs"])
        self.assertIn("broken", logged.output[0])
        self.assertIn("StartUp", logged.output[0])

    def test_every_failure_is_counted_and_logged(self) -> None:
        seen: list = []
        features = [_feature("x", seen, fail=True), _feature("y", seen, fail=True)]
        with self.assertLogs(LOG, level="ERROR") as logged:
            self.assertEqual(feature_dispatch.dispatch(features, {"event": "FSSDiscoveryScan"}, "", None, None, {}, LOG), 2)
        self.assertEqual(len(logged.output), 2)

    def test_no_features_is_fine(self) -> None:
        self.assertEqual(feature_dispatch.dispatch([], {"event": "x"}, "", None, None, {}, LOG), 0)


class NoUndefinedNamesTests(unittest.TestCase):
    def test_no_plugin_module_uses_a_name_it_never_defines(self) -> None:
        try:
            from pyflakes import api, reporter
        except ImportError:
            self.skipTest("pyflakes is not installed")
        problems = []
        for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "plugin", "*.py"))):
            out, err = io.StringIO(), io.StringIO()
            with open(path, encoding="utf-8") as handle:
                api.check(handle.read(), path, reporter.Reporter(out, err))
            problems += [f"{os.path.basename(path)}: {line}" for line in out.getvalue().splitlines() if "undefined name" in line]
        self.assertEqual(problems, [])


class ReplayShipTests(unittest.TestCase):
    LOADOUT = {"event": "Loadout", "Ship": "krait_mkii", "ShipName": "Test", "Modules": []}

    def test_start_up_gives_every_feature_the_current_loadout_after_the_start_up_event(self) -> None:
        seen: list = []
        failed = feature_dispatch.replay_ship([_feature("a", seen), _feature("b", seen)], {"event": "StartUp"}, "CMDR", "Sol", None, {}, LOG, lambda: self.LOADOUT)
        self.assertEqual((failed, seen), (0, [("a", "Loadout", "CMDR"), ("b", "Loadout", "CMDR")]))

    def test_any_other_event_replays_nothing(self) -> None:
        seen: list = []
        for event in ("FSDJump", "Loadout", "LoadGame"):
            self.assertEqual(feature_dispatch.replay_ship([_feature("a", seen)], {"event": event}, "CMDR", None, None, {}, LOG, lambda: self.LOADOUT), 0)
        self.assertEqual(seen, [])

    def test_no_loadout_in_the_journals_replays_nothing_and_a_failing_reader_does_not_raise(self) -> None:
        seen: list = []
        self.assertEqual(feature_dispatch.replay_ship([_feature("a", seen)], {"event": "StartUp"}, "CMDR", None, None, {}, LOG, lambda: None), 0)

        def broken():
            raise OSError("journal folder gone")
        self.assertEqual(feature_dispatch.replay_ship([_feature("a", seen)], {"event": "StartUp"}, "CMDR", None, None, {}, LOG, broken), 0)
        self.assertEqual(seen, [])

    def test_a_feature_that_raises_on_the_replayed_loadout_does_not_starve_the_others(self) -> None:
        seen: list = []
        failed = feature_dispatch.replay_ship([_feature("a", seen, fail=True), _feature("b", seen)], {"event": "StartUp"}, "CMDR", None, None, {}, LOG, lambda: self.LOADOUT)
        self.assertEqual((failed, [name for name, _e, _c in seen]), (1, ["a", "b"]))


if __name__ == "__main__":
    unittest.main()
