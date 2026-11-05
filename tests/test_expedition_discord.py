"""
Expedition summary for Discord (expedition_discord.py): the wording, the options and presets, the escaping and the split into messages.
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

from plugin import discord_format as fmt, discord_templates as T, expedition_discord as D  # noqa: E402
from plugin.expedition_log import Run, Totals  # noqa: E402

NOW = 1_793_000_000.0


def preset(name):
    return T.preset(T.EXPEDITION, name).options


def run(**fields):
    base = D.sample_run()
    for key, value in fields.items():
        setattr(base, key, value)
    return base


class Summary(unittest.TestCase):
    def test_nothing_to_share_without_an_expedition(self):
        self.assertEqual(D.summary_messages(None), [])

    def test_standard_has_the_heading_figures_and_sales(self):
        text = "\n".join(D.summary_messages(run(), None, NOW))
        self.assertIn("**WFMT Expedition — Example Expedition**", text)
        self.assertIn("From Example System to Sample Reach", text)
        self.assertIn("42 jumps", text)
        self.assertIn("9 samples, 3 species analyzed", text)
        self.assertIn("**2,450,000 cr**", text)
        self.assertIn("**5,100,000 cr**", text)
        self.assertIn("**7,550,000 cr**", text)
        self.assertIn("~600,000 cr", text)
        self.assertNotIn("Example Explorer", text)       # ships and notes are for Detailed
        self.assertNotIn("A sample note.", text)

    def test_the_figures_are_the_runs_own(self):
        text = "\n".join(D.summary_messages(run(totals=Totals(explore_earned=1000, bio_earned=250, explore_estimated=40, bio_estimated=10))))
        self.assertIn("**1,000 cr**", text)
        self.assertIn("**1,250 cr**", text)
        self.assertIn("~50 cr", text)

    def test_compact_keeps_the_heading_and_the_sales(self):
        text = "\n".join(D.summary_messages(run(), preset(T.COMPACT), NOW))
        self.assertIn("WFMT Expedition", text)
        self.assertIn("Total earned", text)
        self.assertNotIn("jumps", text)
        self.assertNotIn("samples", text)
        self.assertNotIn("Unsold", text)

    def test_detailed_adds_ships_and_notes(self):
        text = "\n".join(D.summary_messages(run(), preset(T.DETAILED), NOW))
        self.assertIn("Example Explorer", text)
        self.assertIn("A sample note.", text)

    def test_plain_has_no_bold_or_italic_marks(self):
        text = "\n".join(D.summary_messages(run(), preset(T.PLAIN), NOW))
        self.assertNotIn("**", text)
        self.assertNotIn("*", text.replace("\\*", ""))
        self.assertIn("2,450,000 cr", text)

    def test_unsold_can_stand_without_the_sales(self):
        text = "\n".join(D.summary_messages(run(), {"sales": False}, NOW))
        self.assertNotIn("Total earned", text)
        self.assertIn("Unsold", text)
        self.assertNotIn("Unsold", "\n".join(D.summary_messages(run(), {"sales": False, "unsold": False}, NOW)))

    def test_no_route_line_when_the_places_are_unknown(self):
        text = "\n".join(D.summary_messages(run(start_system="", end_system=""), None, NOW))
        self.assertNotIn("From", text)

    def test_a_name_can_never_format_or_ping(self):
        text = "\n".join(D.summary_messages(run(name="*@everyone* <@123>", start_system="[x](http://evil)", ships=["`a`"], notes="@here"),
                                             preset(T.DETAILED), NOW))
        self.assertNotIn("@everyone", text)
        self.assertNotIn("<@", text)
        self.assertNotIn("](http", text)
        self.assertNotIn("@here", text)

    def test_a_long_note_splits_under_the_limit(self):
        messages = D.summary_messages(run(notes="word " * 1200), preset(T.DETAILED), NOW)
        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(m) <= fmt.MESSAGE_LIMIT for m in messages))

    def test_unknown_options_are_ignored(self):
        self.assertEqual(D.summary_messages(run(), {"nonsense": True}, NOW), D.summary_messages(run(), None, NOW))

    def test_the_report_key_follows_the_expedition(self):
        self.assertEqual(D.report_key(Run(id="ab12cd34", name="x")), "expedition:ab12cd34")
        self.assertNotEqual(D.report_key(Run(id="a", name="x")), D.report_key(Run(id="b", name="x")))


class Templates(unittest.TestCase):
    def test_the_report_is_known_to_the_dialog(self):
        self.assertIn(T.EXPEDITION, T.REPORTS)
        self.assertEqual(T.REPORT_LABELS[T.EXPEDITION], "Expedition summary")

    def test_standard_is_the_defaults(self):
        self.assertEqual(preset(T.STANDARD), T.DEFAULTS[T.EXPEDITION])


if __name__ == "__main__":
    unittest.main()
