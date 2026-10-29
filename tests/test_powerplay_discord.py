"""
Powerplay progress for Discord (powerplay_discord.py) and the rows it shares with Copy Progress (powerplay_clipboard.progress_rows): the order of
the systems, the merits and estimated CP, the wording, the escaping and the split into messages.
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

from plugin import discord_format as fmt, powerplay_clipboard as C, powerplay_discord as D  # noqa: E402
from plugin.formulas import ACTIVITIES, NO_CP_ACTIVITIES  # noqa: E402

RATIOS = {activity: 2.5 for activity in ACTIVITIES}
CP_ACTIVITY = next(activity for activity in ACTIVITIES if activity not in NO_CP_ACTIVITIES)


def session(**systems):
    """A session with `name=(merits, last_seen_at)` for each system, all earned in one CP-bearing activity."""
    return {"started_at": "2026-10-29T09:00:00Z", "by_system": {
        name.replace("_", " "): {"totals": {CP_ACTIVITY: merits}, "events": {CP_ACTIVITY: 1}, "last_seen_at": seen}
        for name, (merits, seen) in systems.items()}}


class Rows(unittest.TestCase):
    def test_the_current_system_leads_then_most_recent_first(self):
        sess = session(Nervi=(100, "2026-10-29T10:00:00Z"), Sol=(50, "2026-10-29T12:00:00Z"), Alioth=(25, "2026-10-29T11:00:00Z"))
        rows = C.progress_rows(sess, "Nervi", "Exploited", RATIOS.get)
        self.assertEqual([r.system for r in rows], ["Nervi", "Sol", "Alioth"])
        self.assertEqual(rows[0].state, "Exploited")
        self.assertEqual(rows[1].state, "—")

    def test_a_current_system_with_no_merits_yet_still_leads(self):
        rows = C.progress_rows(session(Sol=(50, "2026-10-29T12:00:00Z")), "Nervi", "", RATIOS.get)
        self.assertEqual([(r.system, r.merits, r.state) for r in rows], [("Nervi", 0, "—"), ("Sol", 50, "—")])

    def test_merits_and_estimated_cp(self):
        rows = C.progress_rows(session(Nervi=(500, "2026-10-29T10:00:00Z")), "", "", RATIOS.get)
        self.assertEqual((rows[0].merits, rows[0].cp), (500, 200.0))

    def test_nothing_earned_and_nowhere_gives_no_rows(self):
        self.assertEqual(C.progress_rows({"by_system": {}}, "", "", RATIOS.get), [])

    def test_the_plain_line_is_unchanged(self):
        row = C.progress_rows(session(Nervi=(120, "2026-10-29T10:00:00Z")), "Nervi", "Exploited", RATIOS.get)[0]
        line = C.format_system_line(C.DEFAULT_TEMPLATE, system=row.system, merits=f"{row.merits:,}", cp=f"{row.cp:,.1f}", state=row.state)
        self.assertEqual(line, "[Nervi](https://inara.cz/elite/starsystem/?search=Nervi) - 120 merits (~48.0 CP) - Exploited")


class Discord(unittest.TestCase):
    def rows(self):
        return [C.ProgressRow("Nervi", 120, 48.0, "Exploited"), C.ProgressRow("Sol", 1234, 493.6, "—")]

    def test_a_row_line(self):
        self.assertEqual(D.row_line(self.rows()[0]), "- [Nervi](<https://inara.cz/elite/starsystem/?search=Nervi>) — 120 merits (~48.0 CP) — Exploited")
        self.assertEqual(D.row_line(self.rows()[1]), "- [Sol](<https://inara.cz/elite/starsystem/?search=Sol>) — 1,234 merits (~493.6 CP)")

    def test_the_report(self):
        (message,) = D.progress_messages(self.rows(), "Aisling Duval", "CYCLE 12 TOTAL — 3,400 merits · est. 1,360.0 CP · 5 systems worked")
        lines = message.split("\n")
        self.assertEqual(lines[0], "**WFMT Powerplay progress** — Aisling Duval")
        self.assertEqual(lines[1], "*This session. CP is an estimate \(\~\).*")
        self.assertTrue(lines[2].startswith("- [Nervi]"))
        self.assertEqual(lines[-2], "**Cycle**")
        self.assertIn("CYCLE 12 TOTAL — 3,400 merits · est. 1,360.0 CP", lines[-1])

    def test_without_a_power_or_a_cycle(self):
        (message,) = D.progress_messages(self.rows())
        self.assertTrue(message.startswith("**WFMT Powerplay progress**\n"))
        self.assertNotIn("Cycle", message)

    def test_nothing_to_share_gives_no_messages(self):
        self.assertEqual(D.progress_messages([]), [])

    def test_names_cannot_format_or_ping(self):
        (message,) = D.progress_messages([C.ProgressRow("A*B @everyone", 1, 0.4, "Fortified_*")], "@here")
        self.assertNotIn("@everyone", message)
        self.assertNotIn("@here", message)
        self.assertIn("Fortified\\_\\*", message)

    def test_a_long_report_is_split_between_rows(self):
        rows = [C.ProgressRow(f"Some Long System Name {i}", i, i / 2.5, "Exploited") for i in range(60)]
        messages = D.progress_messages(rows, "Aisling Duval", "CYCLE 1 TOTAL")
        self.assertTrue(len(messages) > 1)
        self.assertTrue(all(len(m) <= fmt.MESSAGE_LIMIT for m in messages))
        self.assertTrue(all(line.startswith(("-", "**", "*", "CYCLE")) for m in messages for line in m.split("\n")))

    def test_standard_options_give_the_layout_the_posts_always_had(self):
        from plugin import discord_templates as T
        standard = T.preset(T.POWERPLAY, "Standard").options
        args = (self.rows(), "Aisling Duval", "CYCLE 12 TOTAL — 3,400 merits")
        self.assertEqual(D.progress_messages(*args, options=standard), D.progress_messages(*args))
        self.assertEqual(D.row_line(self.rows()[0], standard), D.row_line(self.rows()[0]))

    def test_each_part_can_be_left_out(self):
        row = C.ProgressRow("Nervi", 120, 48.0, "Exploited", (("Acquisition", 80), ("Reinforcement", 40)))
        self.assertNotIn("CP", D.row_line(row, {"cp": False}))
        self.assertNotIn("Exploited", D.row_line(row, {"state": False}))
        self.assertNotIn("inara", D.row_line(row, {"links": False}))
        self.assertTrue(D.row_line(row, {"links": False}).startswith("- Nervi — 120 merits"))
        self.assertNotIn("Acquisition", D.row_line(row))
        self.assertIn("Acquisition 80, Reinforcement 40", D.row_line(row, {"activities": True}))
        (message,) = D.progress_messages([row], "Aisling Duval", "CYCLE 12 TOTAL", {"heading": False, "cycle": False})
        self.assertEqual(message, D.row_line(row))
        (message,) = D.progress_messages([row], "Aisling Duval", "CYCLE 12 TOTAL", {"power": False, "cp": False})
        self.assertNotIn("Aisling", message)
        self.assertIn("*This session.*", message)

    def test_plain_has_no_marks_and_escapes_names(self):
        row = C.ProgressRow("A*B @everyone", 5, 2.0, "Fortified_*")
        (message,) = D.progress_messages([row], "@here", "CYCLE 12 TOTAL", {"plain": True})
        self.assertNotIn("**", message.replace("\\*", ""))
        self.assertNotIn("@everyone", message)
        self.assertIn("• ", message)
        self.assertIn("<https://inara.cz", message)
        self.assertNotIn("](", message)

    def test_every_option_combination_still_fits(self):
        import itertools
        rows = [C.ProgressRow(f"Some Long System Name {i}", i, i / 2.5, "Exploited", (("Acquisition", i), ("Reinforcement", i))) for i in range(60)]
        keys = ["heading", "power", "links", "cp", "state", "activities", "cycle", "plain"]
        for values in itertools.product([False, True], repeat=len(keys)):
            messages = D.progress_messages(rows, "Aisling Duval", "CYCLE 1 TOTAL", dict(zip(keys, values)))
            self.assertTrue(all(len(m) <= fmt.MESSAGE_LIMIT for m in messages))

    def test_the_rows_carry_the_merits_for_each_activity(self):
        sess = {"started_at": "x", "by_system": {"Nervi": {"totals": {"acquisition": 80, "reinforcement": 20}, "events": {}, "last_seen_at": "2026-10-29T10:00:00Z"}}}
        from plugin.formulas import ACTIVITIES, ACTIVITY_LABELS
        sess["by_system"]["Nervi"]["totals"] = {ACTIVITIES[0]: 80, ACTIVITIES[1]: 20}
        (row,) = C.progress_rows(sess, "", "", RATIOS.get)
        self.assertEqual(row.by_activity, ((ACTIVITY_LABELS[ACTIVITIES[0]], 80), (ACTIVITY_LABELS[ACTIVITIES[1]], 20)))

    def test_the_sample_rows_make_a_post(self):
        messages = D.progress_messages(D.sample_rows(), D.SAMPLE_POWER, D.SAMPLE_CYCLE_LINE)
        self.assertTrue(messages and "Example System" in messages[0])

    def test_the_key_names_the_session(self):
        self.assertEqual(D.report_key({"started_at": "2026-10-29T09:00:00Z"}), "powerplay:2026-10-29T09:00:00Z")
        self.assertEqual(D.report_key({}), "powerplay:session")


if __name__ == "__main__":
    unittest.main()
