"""Where to look for a missing codex entry, and how far along each kind is (codex_hints.py), plus the My Codex window's overview ordering."""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector", config=types.SimpleNamespace()))
sys.modules.setdefault("myNotebook", types.ModuleType("myNotebook"))

from plugin import codex_hints as H  # noqa: E402
from plugin.codex_catalog import CatalogEntry  # noqa: E402


def entry(name, english, kind="Bacterial", category="Biological", entry_id=0):
    return CatalogEntry(name=name, entry_id=entry_id, english_name=english, category=category, sub_class=kind, platform="Odyssey")


class NameTests(unittest.TestCase):
    def test_a_species_and_color_are_split(self):
        self.assertEqual(H.split_name("Bacterium Aurasus - Teal"), ("Bacterium Aurasus", "Teal"))
        self.assertEqual(H.split_name("Common Thargoid Barnacle"), ("Common Thargoid Barnacle", ""))


class HintTests(unittest.TestCase):
    def test_a_known_species_gets_its_conditions_and_color_source(self):
        text = H.hint_for("Bacterium Aurasus - Teal")
        self.assertIn("CarbonDioxide atmosphere", text)
        self.assertIn("Teal: orbiting a class M star", text)

    def test_a_color_that_comes_from_a_material_says_so(self):
        self.assertIn("surface holds Polonium", H.hint_for("Bacterium Nebulus - Gold"))

    def test_other_rulesets_are_counted(self):
        self.assertIn("other set", H.hint_for("Bacterium Nebulus - Gold"))

    def test_an_entry_without_species_data_has_no_hint(self):
        self.assertEqual(H.hint_for("Common Thargoid Barnacle"), "")
        self.assertEqual(H.hint_for("Something Unknown - Red"), "")


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.catalog = [
            entry("$a1;", "Bacterium Aurasus - Teal", entry_id=1),
            entry("$a2;", "Bacterium Aurasus - Red", entry_id=2),
            entry("$a3;", "Bacterium Aurasus - Lime", entry_id=3),
            entry("$t1;", "Tussock Albata - Lime", kind="Tussocks", entry_id=4),
            entry("$g1;", "Some Ruin", kind="Guardian", category="Civilisations", entry_id=5),
        ]

    def test_found_and_total_are_counted_per_type(self):
        rows = H.progress(self.catalog, ["$a1;"], [4])
        self.assertIn(("Biological", "Bacterial", 1, 3), rows)
        self.assertIn(("Biological", "Tussocks", 1, 1), rows)
        self.assertIn(("Civilisations", "Guardian", 0, 1), rows)

    def test_names_match_without_regard_to_case(self):
        self.assertIn(("Biological", "Bacterial", 1, 3), H.progress(self.catalog, ["$A2;"]))

    def test_percent_of_nothing_is_blank(self):
        self.assertEqual(H.percent(1, 4), "25%")
        self.assertEqual(H.percent(0, 0), "")

    def test_closest_to_done_lists_started_unfinished_types_fewest_left_first(self):
        rows = [("B", "A", 9, 10), ("B", "B", 1, 10), ("B", "C", 10, 10), ("B", "D", 0, 5), ("B", "E", 4, 5)]
        self.assertEqual([r[1] for r in H.closest_to_done(rows)], ["A", "E", "B"])


class OverviewSortTests(unittest.TestCase):
    def test_the_overview_sorts_by_what_is_left_or_percent_done(self):
        try:
            from plugin import codex_completionist_window as W
        except Exception as exc:                       # the window module needs Tk and EDMC; the sort is pure but lives beside them
            self.skipTest(f"window module not importable here: {exc}")
        rows = [("B", "A", 9, 10), ("B", "B", 1, 10), ("B", "C", 2, 4)]
        self.assertEqual([r[1] for r in W.sort_overview(rows, "left", False)], ["A", "C", "B"])
        self.assertEqual([r[1] for r in W.sort_overview(rows, "done", True)], ["A", "C", "B"])
        self.assertEqual([r[1] for r in W.sort_overview(rows, "type", False)], ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
