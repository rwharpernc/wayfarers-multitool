"""Ship names as a player reads them (ship_names.py): the table, the game's own name, and the tidied fallback for a ship the table does not know."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import ship_names as S  # noqa: E402


class ShipNameTests(unittest.TestCase):
    def test_the_games_own_name_wins(self):
        self.assertEqual(S.display_name("anything", "  Shiny   Thing "), "Shiny Thing")

    def test_the_table_ignores_case(self):
        self.assertEqual(S.display_name("AnacondaMkII"), "Anaconda Mk II")
        self.assertEqual(S.display_name("PantherMkII"), "Panther Clipper Mk II")
        self.assertEqual(S.display_name("Python_NX"), "Python Mk II")

    def test_codenames_and_fighters(self):
        self.assertEqual(S.display_name("smallcombat01_nx"), "Kestrel Mk II")
        self.assertEqual(S.display_name("mediumtransport01"), "Lynx Highliner")
        self.assertEqual(S.display_name("lander01"), "Nomad")
        self.assertEqual(S.display_name("empire_fighter"), "GU-97")

    def test_taxis(self):
        self.assertEqual(S.display_name("adder_taxi"), "Adder (Taxi)")
        self.assertEqual(S.display_name("diamondback_taxi"), "Diamondback Scout (Taxi)")

    def test_an_unknown_ship_is_shown_as_words(self):
        self.assertEqual(S.display_name("some_new_ship"), "Some New Ship")
        self.assertEqual(S.display_name("fooMkIV"), "Foo Mk IV")
        for raw in ("some_new_ship", "fooMkIV", "x_nx"):
            shown = S.display_name(raw)
            self.assertNotIn("_", shown)
            self.assertNotEqual(shown, raw)

    def test_the_ship_list_has_no_fighters_or_vehicles(self):
        listed = S.ships()
        self.assertIn("Anaconda Mk II", listed)
        self.assertNotIn("GU-97", listed)
        self.assertNotIn("SRV", listed)
        self.assertEqual(listed, sorted(listed, key=str.casefold))

    def test_no_name_is_empty(self):
        self.assertEqual(S.display_name(""), "")
        self.assertEqual(S.display_name(None), "")

    def test_every_table_name_is_a_readable_name(self):
        for key, name in {**S.NAMES, **S.VEHICLES}.items():
            self.assertEqual(key, key.casefold())
            self.assertNotIn("_", name)
            self.assertTrue(name[0].isupper() or name[0].isdigit(), name)


if __name__ == "__main__":
    unittest.main()
