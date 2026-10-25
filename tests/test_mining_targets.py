"""Several target commodities (plugin/mining_targets.py, plugin/mining_alerts.py): the box's text, each name's own percentage, which commodity hit, one alert per target per rock,
and the type-ahead's stand-in for the box's variable. No Tk and no EDMC."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from plugin import mining_alerts as M  # noqa: E402
from plugin import mining_targets as T  # noqa: E402


def rock(*materials, remaining=100.0):
    return {"event": "ProspectedAsteroid", "Remaining": remaining, "Content": "$AsteroidMaterialContent_High;", "Content_Localised": "Material Content: High",
            "Materials": [{"Name": name.lower(), "Name_Localised": name, "Proportion": percent} for name, percent in materials]}


class ParseTests(unittest.TestCase):
    def names(self, text, default=20):
        return [(t.name, t.percent) for t in T.parse_targets(text, default).targets]

    def test_several_names_with_their_own_percentages_and_the_default(self) -> None:
        parsed = T.parse_targets("Painite 30, Platinum 25, Void Opals", 20)
        self.assertEqual([(t.name, t.percent) for t in parsed.targets], [("Painite", 30.0), ("Platinum", 25.0), ("Void Opals", 20.0)])
        self.assertEqual(parsed.problems, ())

    def test_semicolons_percent_signs_spaces_and_blank_items(self) -> None:
        self.assertEqual(self.names("  Painite   30% ;; Low Temp. Diamonds 12.5 , "), [("Painite", 30.0), ("Low Temp. Diamonds", 12.5)])

    def test_one_name_behaves_as_before(self) -> None:
        self.assertEqual(self.names("Painite", 35), [("Painite", 35.0)])
        self.assertEqual(self.names("void opals", 20), [("void opals", 20.0)])
        self.assertEqual(self.names("", 20), [])
        self.assertEqual(self.names(None, 20), [])
        self.assertEqual(T.parse_targets("Painite").problems, ())

    def test_a_name_that_is_unknown_is_still_a_target(self) -> None:
        self.assertEqual(self.names("Unobtainium 50"), [("Unobtainium", 50.0)])

    def test_a_bad_percentage_is_reported_and_the_entry_left_out(self) -> None:
        for bad in ("Painite 0", "Painite 101", "Painite 3x", "Painite -5", "Painite 1.2.3"):
            parsed = T.parse_targets(bad + ", Platinum 25", 20)
            self.assertEqual([t.name for t in parsed.targets], ["Platinum"], bad)
            self.assertEqual(len(parsed.problems), 1, bad)
            self.assertIn("percentage must be a number from 1 to 100", parsed.problems[0], bad)
            self.assertIn("Painite", parsed.problems[0], bad)

    def test_a_number_with_no_name_is_reported(self) -> None:
        parsed = T.parse_targets("30, Painite", 20)
        self.assertEqual([t.name for t in parsed.targets], ["Painite"])
        self.assertEqual(len(parsed.problems), 1)

    def test_more_than_the_maximum_are_cut_and_reported(self) -> None:
        text = ", ".join(f"Metal{chr(97 + i)}" for i in range(T.MAX_TARGETS + 3))
        parsed = T.parse_targets(text, 20)
        self.assertEqual(len(parsed.targets), T.MAX_TARGETS)
        self.assertEqual(T.MAX_TARGETS, 8)
        self.assertEqual(parsed.problems, (f"Only the first {T.MAX_TARGETS} targets are used.",))

    def test_a_name_listed_twice_in_two_spellings_is_one_target(self) -> None:
        parsed = T.parse_targets("Void Opals 30, void opal 40, Painite", 20)
        self.assertEqual([(t.name, t.percent) for t in parsed.targets], [("Void Opals", 30.0), ("Painite", 20.0)])
        self.assertEqual(len(parsed.problems), 1)

    def test_a_long_name_is_cut_in_a_message(self) -> None:
        parsed = T.parse_targets("A" * 200 + " 500", 20)
        self.assertEqual(len(parsed.problems), 1)
        self.assertLess(len(parsed.problems[0]), 100)


class FindingTests(unittest.TestCase):
    def test_the_first_hit_is_named_on_the_page_line(self) -> None:
        found = M.rock_finding(rock(("Painite", 34.4), ("Platinum", 12.0)), "Painite 30, Platinum 25", 20)
        self.assertEqual(found.target, ("Painite", 34.4))
        self.assertEqual(found.hits, (("Painite", 34.4),))
        self.assertEqual(M.rock_text(found), "Last rock: Painite 34%, Platinum 12% (High), target: Painite")

    def test_each_name_has_its_own_percentage(self) -> None:
        found = M.rock_finding(rock(("Painite", 34.0), ("Platinum", 12.0)), "Painite 40, Platinum 10", 20)
        self.assertEqual(found.hits, (("Platinum", 12.0),))
        self.assertEqual(M.rock_text(found), "Last rock: Painite 34%, Platinum 12% (High), target: Platinum")

    def test_a_name_with_no_number_uses_the_default(self) -> None:
        found = M.rock_finding(rock(("Painite", 34.0), ("Platinum", 12.0)), "Painite 40, Platinum", 10)
        self.assertEqual(found.hits, (("Platinum", 12.0),))
        self.assertEqual(M.rock_finding(rock(("Platinum", 12.0)), "Platinum", 15).hits, ())

    def test_two_hits_come_richest_first_and_both_are_named(self) -> None:
        found = M.rock_finding(rock(("Platinum", 28.0), ("Painite", 34.0)), "Platinum 25, Painite 30", 20)
        self.assertEqual(found.hits, (("Painite", 34.0), ("Platinum", 28.0)))
        self.assertEqual(found.target, ("Painite", 34.0))
        self.assertTrue(M.rock_text(found).endswith("target: Painite / Platinum"))

    def test_many_hits_are_summarized(self) -> None:
        names = ("A", "B", "C", "D", "E")
        found = M.rock_finding(rock(*((name + "ium", 50.0 - i) for i, name in enumerate(names))), ", ".join(n + "ium 10" for n in names), 20)
        self.assertEqual(len(found.hits), 5)
        self.assertTrue(M.rock_text(found).endswith("target: Aium / Bium / Cium / 2 more"))

    def test_every_spelling_matches_in_a_list(self) -> None:
        opal = rock(("Void Opal", 25.0))
        for typed in ("Painite, Void Opals", "painite; void opals 20", "Painite 30, opal"):
            self.assertEqual(M.rock_finding(opal, typed, 20).hits, (("Void Opal", 25.0),), typed)
        diamonds = rock(("Low Temp. Diamonds", 25.0))
        self.assertEqual(M.rock_finding(diamonds, "Platinum, Low Temperature Diamonds", 20).target, ("Low Temp. Diamonds", 25.0))
        self.assertIsNone(M.rock_finding(opal, "Painite 20, Platinum 20", 20).target)

    def test_the_alert_card_names_the_commodity(self) -> None:
        alerts = M.rock_alerts(M.rock_finding(rock(("Platinum", 28.0), ("Painite", 34.0)), "Platinum 25, Painite 30", 20))
        self.assertEqual([a.lines for a in alerts], [("Rich rock: Painite", "34% of the rock"), ("Rich rock: Platinum", "28% of the rock")])
        self.assertEqual([a.target for a in alerts], ["Painite", "Platinum"])
        self.assertEqual(M.rock_alert(M.rock_finding(rock(("Painite", 34.0)), "Painite", 30)).lines, ("Rich rock: Painite", "34% of the rock"))

    def test_the_cards_for_one_rock_are_capped(self) -> None:
        names = ("A", "B", "C", "D", "E")
        finding = M.rock_finding(rock(*((name + "ium", 50.0 - i) for i, name in enumerate(names))), ", ".join(n + "ium 10" for n in names), 20)
        self.assertEqual(len(M.rock_alerts(finding)), M.MAX_TARGET_CARDS)

    def test_a_core_and_a_target_are_both_announced(self) -> None:
        entry = dict(rock(("Painite", 34.0)), MotherlodeMaterial="Bromellite")
        self.assertEqual([a.kind for a in M.rock_alerts(M.rock_finding(entry, "Painite", 20))], [M.KIND_CORE, M.KIND_TARGET])


class WatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.at = 1000.0
        self.text = "Painite 30, Platinum 25"
        self.watcher = M.MiningWatcher(now=lambda: self.at, target=lambda: (self.text, 20))

    def targets(self):
        return sorted(a.target for a in self.watcher.alerts() if a.kind == M.KIND_TARGET)

    def test_a_rock_rich_in_two_targets_raises_one_alert_for_each(self) -> None:
        self.watcher.handle_event(rock(("Painite", 34.0), ("Platinum", 28.0)))
        self.assertEqual(self.targets(), ["Painite", "Platinum"])

    def test_the_same_rock_again_raises_nothing_new_and_leaves_the_cards_showing(self) -> None:
        entry = rock(("Painite", 34.0), ("Platinum", 28.0))
        self.watcher.handle_event(entry)
        self.watcher.handle_event(entry)
        self.assertEqual(self.targets(), ["Painite", "Platinum"])
        self.at += M.ROCK_ALERT_S + 1
        self.watcher.handle_event(entry)
        self.assertEqual(self.watcher.alerts(), [])

    def test_a_target_added_later_alerts_for_that_target_only(self) -> None:
        entry = rock(("Painite", 34.0), ("Platinum", 28.0))
        self.text = "Painite 30"
        self.watcher.handle_event(entry)
        self.at += M.ROCK_ALERT_S + 1
        self.text = "Painite 30, Platinum 25"
        self.watcher.handle_event(entry)                       # the same composition, but Platinum was never alerted for it
        self.assertEqual(self.targets(), ["Platinum"])
        self.watcher.handle_event(entry)
        self.assertEqual(self.targets(), ["Platinum"])

    def test_a_new_run_alerts_again(self) -> None:
        entry = rock(("Painite", 34.0))
        self.watcher.handle_event(entry)
        self.at += M.ROCK_ALERT_S + 1
        self.watcher.handle_event({"event": "Undocked"})
        self.watcher.handle_event(entry)
        self.assertEqual(self.targets(), ["Painite"])

    def test_a_mostly_used_up_rock_alerts_for_no_target(self) -> None:
        self.watcher.handle_event(rock(("Painite", 34.0), ("Platinum", 28.0), remaining=M.MIN_REMAINING_PERCENT - 1))
        self.assertEqual(self.watcher.alerts(), [])

    def test_the_sound_key_tells_the_targets_apart(self) -> None:
        self.watcher.handle_event(rock(("Painite", 34.0), ("Platinum", 28.0)))
        keys = {(a.kind, a.rock, a.target) for a in self.watcher.alerts()}
        self.assertEqual(len(keys), 2)

    def test_a_single_name_in_the_box_alerts_as_it_always_did(self) -> None:
        self.text = "Painite"
        self.watcher = M.MiningWatcher(now=lambda: self.at, target=lambda: (self.text, 30))
        self.watcher.handle_event(rock(("Painite", 34.0)))
        alert, = self.watcher.alerts()
        self.assertEqual((alert.kind, alert.lines), (M.KIND_TARGET, ("Rich rock: Painite", "34% of the rock")))


class PrimaryTargetTests(unittest.TestCase):
    def test_the_first_name_is_the_one_the_radar_follows(self) -> None:
        from unittest import mock
        with mock.patch.object(M, "load_target", return_value=("Platinum 25, Painite", 20)):
            self.assertEqual(M.primary_target(), "Platinum")
        with mock.patch.object(M, "load_target", return_value=("", 20)):
            self.assertEqual(M.primary_target(), "")
        with mock.patch.object(M, "load_target", return_value=("Painite", 20)):
            self.assertEqual(M.primary_target(), "Painite")


class TypeAheadVarTests(unittest.TestCase):
    class Var:
        def __init__(self, value):
            self.value = value

        def get(self):
            return self.value

        def set(self, value):
            self.value = value

    def test_the_suggestions_are_for_the_last_item(self) -> None:
        var = self.Var("Painite 30, Pla")
        self.assertEqual(T.LastItemVar(var).get(), "Pla")
        self.assertEqual(T.LastItemVar(self.Var("Painite 30; ")).get(), "")
        self.assertEqual(T.LastItemVar(self.Var("Void  Op")).get(), "Void Op")

    def test_taking_a_suggestion_replaces_only_the_last_item(self) -> None:
        var = self.Var("Painite 30, Pla")
        T.LastItemVar(var).set("Platinum")
        self.assertEqual(var.value, "Painite 30, Platinum")
        var = self.Var("Painite; Os")
        T.LastItemVar(var).set("Osmium")
        self.assertEqual(var.value, "Painite; Osmium")

    def test_with_one_name_it_reads_and_writes_the_whole_box(self) -> None:
        var = self.Var("Pain")
        proxy = T.LastItemVar(var)
        self.assertEqual(proxy.get(), "Pain")
        proxy.set("Painite")
        self.assertEqual(var.value, "Painite")


if __name__ == "__main__":
    unittest.main()
