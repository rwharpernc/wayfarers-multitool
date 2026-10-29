"""The BGS report as Discord messages (bgs_discord.py): the wording, the escaping of names, the split into messages and the key for an edit."""
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

from plugin import bgs_discord as D, bgs_format  # noqa: E402
from plugin import discord_format as fmt  # noqa: E402
from plugin.bgs_ledger import FactionTrack, PeriodView  # noqa: E402
from plugin.bgs_tracker import FactionActivity, FactionSnapshot  # noqa: E402

WHEN = "2026-10-29T09:00:00Z"


def snap(system, faction, state="Boom", influence=0.452, controlling=False, **extra):
    return FactionSnapshot(system, faction, faction_state=state, influence=influence, is_controlling=controlling, updated_at=WHEN, **extra)


def view(tracks=(), activity=(), current=True):
    return PeriodView(tick_start=WHEN, tick_end=None if current else "2026-10-30T09:00:00Z", current=current, activity=list(activity), tracks=list(tracks))


class Report(unittest.TestCase):
    def setUp(self):
        self.nervi = [
            FactionTrack("Nervi", "Nervi Brotherhood", before=snap("Nervi", "Nervi Brotherhood", "None", 0.439, True),
                         now=snap("Nervi", "Nervi Brotherhood", "Boom", 0.452, True, pending_states=["Famine"], active_states=["Boom"])),
            FactionTrack("Nervi", "Allied Forces", now=snap("Nervi", "Allied Forces", "War", 0.3)),
        ]
        self.acts = [FactionActivity("Nervi", "Nervi Brotherhood", missions=2, inf_plus=4, exploration_credits=1_500_000)]
        self.view = view(self.nervi, self.acts)

    def test_a_system_block(self):
        text = D.system_block(self.view, "Nervi")
        self.assertEqual(text.split("\n")[0], "**Nervi**")
        self.assertIn("- **Nervi Brotherhood** — None → Boom, 45.2% \\(+1.3\\)", text)
        self.assertIn("  - Pending: Famine", text)
        self.assertIn("  - Active: Boom", text)
        self.assertIn("  - You: 2 mission\(s\) done, INF +4/-0; 1,500,000 cr exploration data", text)
        self.assertIn("- Allied Forces — War, 30.0%", text)

    def test_the_controlling_faction_comes_first_and_a_pinned_system_is_starred(self):
        text = D.system_block(self.view, "Nervi", pinned=True)
        lines = text.split("\n")
        self.assertEqual(lines[0], "**★ Nervi**")
        self.assertTrue(lines[1].startswith("- **Nervi Brotherhood**"))

    def test_names_cannot_format_or_ping(self):
        nasty = [FactionTrack("A*B_C", "@everyone *Raiders* [x](y)", now=snap("A*B_C", "@everyone *Raiders* [x](y)", "Boom", 0.5, True))]
        text = D.system_block(view(nasty), "A*B_C")
        self.assertNotIn("@everyone", text)
        self.assertIn("A\\*B\\_C", text)
        self.assertNotIn("[x](y)", text)

    def test_an_activity_only_faction_is_listed(self):
        text = D.system_block(view([], [FactionActivity("Sol", "Mother Gaia", missions=1, inf_plus=1)]), "Sol")
        self.assertIn("- Mother Gaia — You:", text)

    def test_a_system_with_nothing_says_so(self):
        self.assertEqual(D.system_block(view(), "Sol"), "**Sol**\n- *nothing recorded*")

    def test_the_report_has_a_heading_and_a_block_for_each_system(self):
        messages = D.report_messages(self.view, "Nervi")
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].startswith("**WFMT BGS report**\n*"))
        self.assertIn(bgs_format.period_label(self.view).split(" ")[0], messages[0])
        self.assertIn("**Nervi**", messages[0])

    def test_no_activity(self):
        self.assertEqual(D.report_messages(view(), None), ["**WFMT BGS report**\n*Current tick — since 2026-10-29 09:00 UTC*\n- *no activity*"])

    def test_a_big_report_is_split_between_systems_under_the_limit(self):
        tracks = [FactionTrack(f"System {i}", f"Faction {j}", now=snap(f"System {i}", f"Faction {j}", "Boom", 0.1, j == 0)) for i in range(40) for j in range(6)]
        messages = D.report_messages(view(tracks), None)
        self.assertTrue(len(messages) > 1)
        self.assertTrue(all(len(m) <= fmt.MESSAGE_LIMIT for m in messages))
        starts = [m.split("\n")[0] for m in messages[1:]]
        self.assertTrue(all(s.startswith("**System ") or s.startswith("**WFMT") for s in starts), starts)

    def test_the_key_names_the_tick(self):
        self.assertEqual(D.report_key(self.view), "bgs:" + WHEN)
        self.assertEqual(D.report_key(PeriodView(None, None, True)), "bgs:current")

    def test_the_plain_copy_is_unchanged_and_has_no_discord_marks(self):
        plain = bgs_format.summary_text([self.view], "Nervi", [])
        self.assertTrue(plain.startswith("WFMT BGS Report"))
        self.assertNotIn("**", plain)


if __name__ == "__main__":
    unittest.main()
