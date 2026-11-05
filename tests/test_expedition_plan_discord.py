"""
Expedition plan for Discord (expedition_plan_discord.py): the wording, the options and presets, the short list, the escaping and the split into messages.
"""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
for name in ("myNotebook", "ttkHyperlinkLabel", "theme", "monitor", "plug", "l10n", "requests"):
    sys.modules.setdefault(name, mock.MagicMock())
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = mock.MagicMock()
    sys.modules["config"] = _stub

from plugin import discord_format as fmt, discord_templates as T, expedition_plan_discord as D  # noqa: E402
from plugin.expedition import Expedition, Stop  # noqa: E402


def preset(name):
    return T.preset(T.ANNOUNCEMENT, name).options


def many(count, visited=0):
    stops = [Stop(id=str(i), system=f"System {i + 1}", visited="2026-11-01T10:00:00Z" if i < visited else "") for i in range(count)]
    return Expedition(id="e1", name="Long Haul", status="active", jumps=5, light_years=120.0, stops=stops)


class Plan(unittest.TestCase):
    def test_nothing_to_announce_without_stops(self):
        self.assertEqual(D.summary_messages(None), [])
        self.assertEqual(D.summary_messages(Expedition(id="x", name="Empty")), [])

    def test_standard_has_heading_progress_route_next_and_stops(self):
        text = "\n".join(D.summary_messages(D.sample_expedition()))
        self.assertIn("**WFMT Expedition plan — Example Expedition**", text)
        self.assertIn("1 of 4 stops reached, 12 jumps, 840 ly", text)
        self.assertIn("From Example System to Test Cluster", text)
        self.assertIn("**Next stop** Sample Reach / Sample Reach A 1", text)
        self.assertIn("**Next 3 stops**" + chr(10) + "2. Sample Reach / Sample Reach A 1", text)
        self.assertNotIn("✓", text)                         # the short list leaves out the stops already reached
        self.assertNotIn("Check the ring", text)           # notes are for Detailed

    def test_the_short_list_shows_the_next_ten_unvisited_stops(self):
        text = "\n".join(D.summary_messages(many(30, visited=3)))
        self.assertIn("Next 10 stops", text)
        self.assertIn("4. System 4", text)
        self.assertIn("13. System 13", text)
        self.assertNotIn("14. System 14", text)
        self.assertNotIn("1. ✓", text)

    def test_detailed_lists_every_stop_with_notes(self):
        text = "\n".join(D.summary_messages(D.sample_expedition(), preset(T.DETAILED)))
        self.assertIn("**Stops**", text)
        self.assertIn("Check the ring", text)
        self.assertIn("1. ✓ Example System", text)
        self.assertIn("4. Test Cluster", text)

    def test_compact_has_no_stop_list_or_route(self):
        text = "\n".join(D.summary_messages(D.sample_expedition(), preset(T.COMPACT)))
        self.assertIn("Next stop", text)
        self.assertNotIn("1. ", text)
        self.assertNotIn("From ", text)

    def test_plain_has_no_bold_or_italic_marks(self):
        text = "\n".join(D.summary_messages(D.sample_expedition(), preset(T.PLAIN)))
        self.assertNotIn("**", text)
        self.assertIn("WFMT Expedition plan", text)

    def test_all_stops_reached(self):
        self.assertIn("All stops reached.", "\n".join(D.summary_messages(many(3, visited=3))))

    def test_bodies_can_be_left_out(self):
        self.assertNotIn("Sample Reach A 1", "\n".join(D.summary_messages(D.sample_expedition(), {"bodies": False})))

    def test_a_name_can_never_format_or_ping(self):
        e = many(2)
        e.name, e.stops[0].system, e.stops[1].note = "*@everyone*", "<@123> [x](http://evil)", "@here"
        text = "\n".join(D.summary_messages(e, preset(T.DETAILED)))
        self.assertNotIn("@everyone", text)
        self.assertNotIn("<@", text)
        self.assertNotIn("](http", text)
        self.assertNotIn("@here", text)

    def test_a_long_route_splits_under_the_limit(self):
        messages = D.summary_messages(many(400), {"short": False})
        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(m) <= fmt.MESSAGE_LIMIT for m in messages))

    def test_the_report_key_follows_the_expedition(self):
        self.assertEqual(D.report_key(many(1)), "plan:e1")


class Templates(unittest.TestCase):
    def test_the_report_is_known_to_the_dialog(self):
        self.assertIn(T.ANNOUNCEMENT, T.REPORTS)
        self.assertEqual(T.REPORT_LABELS[T.ANNOUNCEMENT], "Expedition plan")
        self.assertEqual(preset(T.STANDARD), T.DEFAULTS[T.ANNOUNCEMENT])


if __name__ == "__main__":
    unittest.main()
