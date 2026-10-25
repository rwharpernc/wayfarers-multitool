"""The check for a neutron star that is a secondary star (route_secondary.py): the name rule on real system shapes, and the background checker with the lookup replaced. No Tk, no network."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import route_secondary as RS  # noqa: E402


def star(name, subtype, main=None):
    return {"name": name, "subtype": subtype, "is_main_star": main, "type": "Star"}


# Lalande 25224 as Spansh and EDSM both record it (2026-10-18): the named neutron star is listed as the main star at 0 ls, and the F star bearing the system's name 6,156 ls away.
LALANDE = [star("Lalande 25224", "F (White) Star"), star("PSR J2144-3933", "Neutron Star", True)]


class NameRuleTests(unittest.TestCase):
    def test_a_neutron_star_beside_the_star_named_for_the_system_is_a_secondary_star(self):
        self.assertTrue(RS.neutron_is_secondary("Lalande 25224", LALANDE))

    def test_the_arrival_star_being_the_neutron_star_is_fine(self):
        self.assertFalse(RS.neutron_is_secondary("Jackson's Lighthouse", [star("Jackson's Lighthouse", "Neutron Star", True), star("Jackson's Lighthouse 2", "T (Brown dwarf) Star")]))
        self.assertFalse(RS.neutron_is_secondary("Pru Aescs QN-S b9-1", [star("Pru Aescs QN-S b9-1", "Neutron Star", True)]))

    def test_a_multiple_system_uses_the_a_star(self):
        self.assertFalse(RS.neutron_is_secondary("Pru Aescs QN-S b9-1", [star("Pru Aescs QN-S b9-1 A", "Neutron Star", True), star("Pru Aescs QN-S b9-1 B", "M (Red dwarf) Star")]))
        self.assertTrue(RS.neutron_is_secondary("Pru Aescs QN-S b9-1", [star("Pru Aescs QN-S b9-1 A", "K (Yellow-Orange) Star", True), star("Pru Aescs QN-S b9-1 B", "Neutron Star")]))

    def test_names_compare_without_regard_to_case_or_spacing(self):
        self.assertFalse(RS.neutron_is_secondary("  jackson's   lighthouse ", [star("Jackson's Lighthouse", "Neutron Star", True)]))

    def test_with_no_star_named_for_the_system_the_main_star_flag_decides(self):
        self.assertFalse(RS.neutron_is_secondary("Odd System", [star("PSR J1", "Neutron Star", True), star("Odd 2", "M (Red dwarf) Star")]))
        self.assertTrue(RS.neutron_is_secondary("Odd System", [star("PSR J1", "Neutron Star", False), star("Odd 2", "M (Red dwarf) Star", True)]))
        self.assertTrue(RS.neutron_is_secondary("Odd System", [star("PSR J1", "Neutron Star", None)]))

    def test_no_neutron_star_or_no_data_is_no_answer(self):
        self.assertIsNone(RS.neutron_is_secondary("Sol", [star("Sol", "G (White-Yellow) Star", True)]))
        self.assertIsNone(RS.neutron_is_secondary("Sol", []))


class CheckerTests(unittest.TestCase):
    def make(self, data, now=None):
        self.calls = []

        def fetch(id64):
            self.calls.append(id64)
            value = data[id64]
            if isinstance(value, Exception):
                raise value
            return value
        self.clock = [1000.0]
        return RS.SecondaryChecker(fetch, now=(now or (lambda: self.clock[0])), background=False)

    def test_answers_arrive_once_by_name(self):
        checker = self.make({1: LALANDE, 2: [star("Fine", "Neutron Star", True)]})
        self.assertEqual(checker.ensure([(1, "Lalande 25224"), (2, "Fine")]), 2)
        self.assertEqual(checker.drain(), {"lalande 25224": True, "fine": False})
        self.assertEqual(checker.drain(), {}, "an answer is handed over once")
        self.assertFalse(checker.busy())

    def test_a_stop_is_asked_about_once(self):
        checker = self.make({1: LALANDE})
        checker.ensure([(1, "Lalande 25224")])
        self.assertEqual(checker.ensure([(1, "Lalande 25224")]), 0)
        self.assertEqual(self.calls, [1])

    def test_a_failed_lookup_is_not_an_answer_and_is_retried_later(self):
        data = {1: OSError("no network")}
        checker = self.make(data)
        checker.ensure([(1, "X")])
        self.assertEqual(checker.drain(), {}, "a failure says nothing about the system")
        self.assertEqual(checker.ensure([(1, "X")]), 0, "not again at once")
        self.clock[0] += RS.RETRY_S + 1
        data[1] = [star("X", "Neutron Star", True)]
        self.assertEqual(checker.ensure([(1, "X")]), 1)
        self.assertEqual(checker.drain(), {"x": False})

    def test_a_system_spansh_does_not_know_gives_no_answer_and_is_not_asked_again_at_once(self):
        checker = self.make({1: None})
        checker.ensure([(1, "Unknown")])
        self.assertEqual(checker.drain(), {}, "no data is no answer")
        self.assertEqual(checker.ensure([(1, "Unknown")]), 0)


if __name__ == "__main__":
    unittest.main()
