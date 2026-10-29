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

    # --- options (discord_templates) -----------------------------------------------------------------------------

    def test_standard_options_give_the_layout_the_posts_always_had(self):
        from plugin import discord_templates as T
        standard = T.preset(T.BGS, "Standard").options
        self.assertEqual(D.report_messages(self.view, "Nervi", [], standard), D.report_messages(self.view, "Nervi", []))
        self.assertEqual(D.system_block(self.view, "Nervi", True, standard), D.system_block(self.view, "Nervi", True))

    def test_each_section_can_be_left_out(self):
        base = D.system_block(self.view, "Nervi", True)
        self.assertNotIn("Pending", D.system_block(self.view, "Nervi", False, {"state_lists": False}))
        self.assertNotIn("You:", D.system_block(self.view, "Nervi", False, {"activity": False}))
        self.assertNotIn("45.2%", D.system_block(self.view, "Nervi", False, {"influence": False}))
        self.assertNotIn("None → Boom", D.system_block(self.view, "Nervi", False, {"states": False}))
        self.assertNotIn("★", D.system_block(self.view, "Nervi", True, {"pinned_star": False}))
        self.assertIn("★", base)
        self.assertNotIn("**Nervi Brotherhood**", D.system_block(self.view, "Nervi", False, {"bold_controller": False}))
        self.assertIn("Nervi Brotherhood", D.system_block(self.view, "Nervi", False, {"bold_controller": False}))
        self.assertNotIn("WFMT BGS report", "\n".join(D.report_messages(self.view, "Nervi", [], {"heading": False})))

    def test_with_no_state_or_influence_a_faction_is_just_its_name(self):
        text = D.system_block(self.view, "Nervi", False, {"states": False, "influence": False})
        self.assertIn("- **Nervi Brotherhood**\n", text + "\n")

    def test_details_add_government_and_allegiance(self):
        v = view([FactionTrack("Sol", "Mother Gaia", now=snap("Sol", "Mother Gaia", "Boom", 0.5, True, government="Democracy", allegiance="Federation"))])
        self.assertIn("Mother Gaia** — Boom, 50.0%, Democracy / Federation", D.system_block(v, "Sol", False, {"details": True}))
        self.assertNotIn("Democracy", D.system_block(v, "Sol", False))

    def test_compact_is_one_line_for_each_system(self):
        text = D.system_block(self.view, "Nervi", False, {"compact": True})
        self.assertEqual(len(text.split("\n")), 1)
        self.assertIn("**Nervi**", text)
        self.assertIn("Nervi Brotherhood", text)
        self.assertIn("You: Nervi Brotherhood 2 mission", text)
        self.assertNotIn("Allied Forces", text)                    # only the controlling faction
        self.assertEqual(D.system_block(self.view, "Sol", False, {"compact": True}), "- **Sol** — *nothing recorded*")
        self.assertNotIn("You:", D.system_block(self.view, "Nervi", False, {"compact": True, "activity": False}))

    def test_plain_has_no_marks_but_names_are_still_escaped(self):
        nasty = [FactionTrack("A*B", "@everyone *Raiders*", now=snap("A*B", "@everyone *Raiders*", "Boom", 0.5, True))]
        messages = D.report_messages(view(nasty), "A*B", [], {"plain": True})
        text = "\n".join(messages)
        self.assertNotIn("**", text.replace("\\*", ""))
        self.assertNotIn("@everyone", text)
        self.assertIn("• ", text)
        self.assertNotIn("\n- ", text)

    def test_only_systems_you_acted_in(self):
        both = [FactionTrack("Nervi", "Nervi Brotherhood", now=snap("Nervi", "Nervi Brotherhood", "Boom", 0.4, True)),
                FactionTrack("Sol", "Mother Gaia", now=snap("Sol", "Mother Gaia", "None", 0.5, True))]
        v = view(both, [FactionActivity("Nervi", "Nervi Brotherhood", missions=1, inf_plus=1)])
        everything = "\n".join(D.report_messages(v, "Sol", []))
        worked = "\n".join(D.report_messages(v, "Sol", [], {"scope": "worked"}))
        self.assertIn("**Sol**", everything)
        self.assertNotIn("Sol", worked)
        self.assertIn("**Nervi**", worked)
        none_worked = D.report_messages(view(both), "Sol", [], {"scope": "worked"})
        self.assertIn("no activity", "\n".join(none_worked))

    def test_every_option_combination_still_fits_and_never_pings(self):
        import itertools
        from plugin import discord_templates as T
        tracks = [FactionTrack(f"System {i}", f"@everyone Faction *{j}*", snap(f"System {i}", f"@everyone Faction *{j}*", "Boom", 0.1, j == 0),
                               snap(f"System {i}", f"@everyone Faction *{j}*", "War", 0.2, j == 0, pending_states=["Famine"] * 3)) for i in range(30) for j in range(5)]
        acts = [FactionActivity(f"System {i}", f"@everyone Faction *{j}*", missions=3, inf_plus=2, exploration_credits=9_000_000) for i in range(30) for j in range(5)]
        big = view(tracks, acts)
        keys = ["heading", "compact", "plain", "activity", "details", "state_lists"]
        for values in itertools.product([False, True], repeat=len(keys)):
            for scope in T.SCOPES:
                messages = D.report_messages(big, None, [], dict(zip(keys, values), scope=scope))
                self.assertTrue(all(len(m) <= fmt.MESSAGE_LIMIT for m in messages))
                self.assertNotIn("@everyone", "\n".join(messages))

    def test_the_sample_view_makes_a_post(self):
        messages = D.report_messages(D.sample_view(), "Example System", [])
        self.assertTrue(messages and "Example Union" in "\n".join(messages))

    def test_the_plain_copy_is_unchanged_and_has_no_discord_marks(self):
        plain = bgs_format.summary_text([self.view], "Nervi", [])
        self.assertTrue(plain.startswith("WFMT BGS Report"))
        self.assertNotIn("**", plain)


if __name__ == "__main__":
    unittest.main()
