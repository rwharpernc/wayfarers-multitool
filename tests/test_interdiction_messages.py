"""Which NPC lines raise the interdiction warning (interdiction.py). The keys are real ones from the journal."""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the module under stand-ins for EDMC's own modules, then take everything that import added back out of sys.modules, so the stand-ins
# and the plugin modules bound to them do not reach the other test files (which bring their own).
_before = set(sys.modules)
_stub = types.ModuleType("config")
_stub.appname = "EDMarketConnector"
_stub.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default,
                                     set=lambda key, value: None, default_journal_dir="")
with mock.patch.dict(sys.modules, {"config": _stub, "myNotebook": mock.MagicMock()}):
    from plugin import interdiction as I  # noqa: E402
for _name in set(sys.modules) - _before:
    if _name == "plugin" or _name.startswith("plugin."):
        sys.modules.pop(_name, None)


def npc(key, text="", sender="Someone"):
    return {"event": "ReceiveText", "Channel": "npc", "From": sender, "From_Localised": sender, "Message": key, "Message_Localised": text}


class KeyTests(unittest.TestCase):
    def test_the_keys_that_mean_a_ship_is_after_you(self):
        for key in ("$Pirate_StartInterdiction03;", "$Military_StartInterdiction01;", "$Police_StartInterdiction02;",
                    "$Pirate_HunterHostileSC_Relevant01;", "$Hitman_HunterHostileSC_Relevant02;", "$CargoHunter_HunterHostileSC_RelevantPlayer_03;",
                    "$BountyHunter_HunterHostileSC_Relevant01;", "$HitmanMissionFailure_OnEnemyDetect02;", "$Pirate_OnStartScanCargo01_01;",
                    "$PirateLord_OnStartScanCargo01;"):
            self.assertTrue(I.is_hostile_key(key), key)

    def test_a_key_decides_before_the_words_do(self):
        # No threatening word in the line at all, in any language: the key alone raises the warning.
        self.assertTrue(I.is_threat("$HitmanMissionFailure_OnEnemyDetect02;", "Ich mache es kurz, das ist mein Beruf."))
        # Words that look like a threat, in chatter that is not aimed at you.
        self.assertFalse(I.is_threat("$DistressCallAmbushedPilot_01;", "Pirates ambushed me, please help!"))
        self.assertFalse(I.is_threat("$AmbushedPilot_OnPlayerNear01;", "Pirates, they took my cargo!"))

    def test_a_key_not_known_either_way_falls_back_to_the_words(self):
        self.assertTrue(I.is_threat("$Something_New01;", "Throttle down and submit for a scan."))
        self.assertFalse(I.is_threat("$Something_New01;", "Lovely weather in the system today."))
        self.assertTrue(I.is_threat(None, "Drop your cargo"))


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.snapshots = []
        self.tracker = I.InterdictionTracker(self.snapshots.append)

    def tearDown(self):
        self.tracker._clear_scheduled_clear()

    def test_a_hunter_line_with_no_threatening_words_raises_the_warning(self):
        self.tracker.handle_event(npc("$Hitman_HunterHostileSC_Relevant02;", "Found the ship, tracking it now.", "Britta"))
        self.assertTrue(self.snapshots[-1].active)
        self.assertEqual(self.snapshots[-1].interdictor_name, "Britta")

    def test_chatter_that_is_not_aimed_at_you_does_not(self):
        self.tracker.handle_event(npc("$DistressCallAmbushedPilot_01;", "Pirates ambushed me!"))
        self.assertEqual(self.snapshots, [])

    def test_other_channels_are_ignored(self):
        entry = npc("$Pirate_StartInterdiction03;", "You're mine")
        entry["Channel"] = "starsystem"
        self.tracker.handle_event(entry)
        self.assertEqual(self.snapshots, [])

    def test_an_interdiction_nothing_warned_about_logs_the_lines_before_it(self):
        self.tracker.handle_event(npc("$Strange_Taunt01;", "Nothing the patterns know"))
        with self.assertLogs(I.logger, level="INFO") as logged:
            self.tracker.handle_event({"event": "Interdicted", "Interdictor": "X", "Submitted": False})
        self.assertIn("$Strange_Taunt01;", "\n".join(logged.output))

    def test_lines_before_one_interdiction_are_not_reported_for_the_next(self):
        self.tracker.handle_event(npc("$Strange_Taunt01;", "Nothing the patterns know"))
        with self.assertLogs(I.logger, level="INFO"):
            self.tracker.handle_event({"event": "Interdicted", "Interdictor": "X", "Submitted": False})
        self.tracker._active = False
        with self.assertLogs(I.logger, level="INFO") as logged:
            self.tracker.handle_event({"event": "Interdicted", "Interdictor": "Y", "Submitted": False})
        self.assertNotIn("$Strange_Taunt01;", "\n".join(logged.output))

    def test_a_warned_interdiction_logs_nothing(self):
        self.tracker.handle_event(npc("$Pirate_StartInterdiction03;", "I have you now"))
        with self.assertNoLogs(I.logger, level="INFO"):
            self.tracker.handle_event({"event": "Interdicted", "Interdictor": "X", "Submitted": False})


if __name__ == "__main__":
    unittest.main()
