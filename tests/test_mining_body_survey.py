"""
Unit tests for plugin/mining_body_survey.py.

Pure logic tests - no EDMC runtime needed. Run with:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import mining_body_survey as survey  # noqa: E402


class SystemBodySurveyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.survey = survey.SystemBodySurvey()
        self.survey.on_system_changed("Sol")

    def test_landable_body_is_recorded(self) -> None:
        self.survey.record_scan("Sol", "Sol 1", "High metal content body", "", True)
        bodies = self.survey.landable_bodies()
        self.assertEqual(len(bodies), 1)
        self.assertEqual(bodies[0].name, "Sol 1")
        self.assertEqual(bodies[0].planet_class, "High metal content body")

    def test_non_landable_body_is_ignored(self) -> None:
        self.survey.record_scan("Sol", "Sol", "K (Yellow-Orange) Star", "", False)
        self.assertEqual(self.survey.landable_bodies(), [])

    def test_scan_from_a_different_system_is_ignored(self) -> None:
        self.survey.record_scan("Alioth", "Alioth 1", "Rocky body", "", True)
        self.assertEqual(self.survey.landable_bodies(), [])

    def test_system_change_clears_previous_bodies(self) -> None:
        self.survey.record_scan("Sol", "Sol 1", "Rocky body", "", True)
        self.survey.on_system_changed("Alioth")
        self.assertEqual(self.survey.landable_bodies(), [])
        self.assertEqual(self.survey.current_system, "Alioth")

    def test_same_system_reconfirmation_does_not_clear(self) -> None:
        self.survey.record_scan("Sol", "Sol 1", "Rocky body", "", True)
        self.survey.on_system_changed("Sol")
        self.assertEqual(len(self.survey.landable_bodies()), 1)

    def test_signal_before_scan_is_applied_once_scan_arrives(self) -> None:
        self.survey.record_signal("Sol", "Sol 1", 3)
        self.survey.record_scan("Sol", "Sol 1", "Rocky body", "", True)
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 3)

    def test_signal_after_scan_updates_existing_body(self) -> None:
        self.survey.record_scan("Sol", "Sol 1", "Rocky body", "", True)
        self.survey.record_signal("Sol", "Sol 1", 5)
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 5)

    def test_bodies_with_signals_sort_before_bodies_without(self) -> None:
        self.survey.record_scan("Sol", "A", "Rocky body", "", True)
        self.survey.record_scan("Sol", "B", "Icy body", "", True)
        self.survey.record_signal("Sol", "B", 2)
        names = [b.name for b in self.survey.landable_bodies()]
        self.assertEqual(names, ["B", "A"])

    def test_higher_signal_count_sorts_first(self) -> None:
        self.survey.record_scan("Sol", "A", "Rocky body", "", True)
        self.survey.record_scan("Sol", "B", "Icy body", "", True)
        self.survey.record_signal("Sol", "A", 1)
        self.survey.record_signal("Sol", "B", 4)
        names = [b.name for b in self.survey.landable_bodies()]
        self.assertEqual(names, ["B", "A"])

    def test_grouped_by_class(self) -> None:
        self.survey.record_scan("Sol", "A", "Rocky body", "", True)
        self.survey.record_scan("Sol", "B", "Icy body", "", True)
        self.survey.record_scan("Sol", "C", "Rocky body", "", True)
        groups = self.survey.grouped_by_class()
        self.assertEqual({b.name for b in groups["Rocky body"]}, {"A", "C"})
        self.assertEqual({b.name for b in groups["Icy body"]}, {"B"})

    def test_missing_planet_class_groups_as_unknown(self) -> None:
        self.survey.record_scan("Sol", "A", None, "", True)
        groups = self.survey.grouped_by_class()
        self.assertIn("Unknown", groups)

    def test_an_fss_count_is_kept_until_a_detailed_scan_gives_the_authoritative_one(self) -> None:
        self.survey.record_scan("Sol", "A", "Icy body", "", True)
        self.survey.record_signal("Sol", "A", 12, detailed=False)
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 12)
        self.survey.record_signal("Sol", "A", 11)                      # the detailed scan
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 11)
        self.survey.record_signal("Sol", "A", 12, detailed=False)      # a later FSS line does not replace it
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 11)

    def test_an_fss_count_found_before_the_scan_is_used_when_the_scan_arrives(self) -> None:
        self.survey.record_signal("Sol", "A", 5, detailed=False)
        self.survey.record_scan("Sol", "A", "Icy body", "", True)
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 5)

    def test_an_fss_count_for_another_system_is_ignored(self) -> None:
        self.survey.record_scan("Sol", "A", "Icy body", "", True)
        self.survey.record_signal("Alpha", "A", 9, detailed=False)
        self.assertIsNone(self.survey.landable_bodies()[0].mining_signal_count)

    def test_a_change_of_system_forgets_which_counts_were_detailed(self) -> None:
        self.survey.record_signal("Sol", "A", 2)
        self.survey.on_system_changed("Alpha")
        self.survey.on_system_changed("Sol")
        self.survey.record_scan("Sol", "A", "Icy body", "", True)
        self.survey.record_signal("Sol", "A", 7, detailed=False)
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 7)

    def test_an_outside_count_is_kept_only_when_the_journal_gave_none(self) -> None:
        self.survey.record_scan("Sol", "A", "Icy body", "", True)
        self.assertTrue(self.survey.record_external_count("Sol", "A", 12))
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 12)
        self.assertFalse(self.survey.record_external_count("Sol", "A", 99))
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 12)
        self.survey.record_signal("Sol", "A", 3)                       # the journal's own count replaces an outside one
        self.assertEqual(self.survey.landable_bodies()[0].mining_signal_count, 3)

    def test_an_outside_count_never_replaces_a_journal_count(self) -> None:
        self.survey.record_signal("Sol", "A", 3)
        self.assertFalse(self.survey.record_external_count("Sol", "A", 12))

    def test_an_outside_body_is_added_only_when_the_journal_has_not_given_it(self) -> None:
        self.assertTrue(self.survey.record_external("Sol", "A", "Icy body", None))
        self.assertFalse(self.survey.record_external("Sol", "A", "Rocky body", "x"))
        self.assertEqual(self.survey.landable_bodies()[0].planet_class, "Icy body")


if __name__ == "__main__":
    unittest.main()
