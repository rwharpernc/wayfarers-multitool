"""Trade shows ships as a player reads them (trade_ship.ship_display_name, known_ships), through ship_names.py."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import trade_ship  # noqa: E402


class TradeShipNameTests(unittest.TestCase):
    def test_names_that_worked_before_are_unchanged(self):
        self.assertEqual(trade_ship.ship_display_name("empire_trader"), "Imperial Clipper")
        self.assertEqual(trade_ship.ship_display_name("Federation_Corvette"), "Federal Corvette")
        self.assertEqual(trade_ship.ship_display_name("independant_trader"), "Keelback")

    def test_ships_that_showed_as_raw_names_are_named(self):
        self.assertEqual(trade_ship.ship_display_name("anacondamkii"), "Anaconda Mk II")
        self.assertEqual(trade_ship.ship_display_name("smallcombat01_nx"), "Kestrel Mk II")
        self.assertEqual(trade_ship.ship_display_name("mediumtransport01"), "Lynx Highliner")
        self.assertEqual(trade_ship.ship_display_name("some_new_ship"), "Some New Ship")
        self.assertEqual(trade_ship.ship_display_name(""), "")

    def test_the_anaconda_and_the_anaconda_mk_ii_need_a_large_pad(self):
        for name in ("anaconda", "Anaconda", "anacondamkii", "AnacondaMkII", "Anaconda Mk II"):
            self.assertEqual(trade_ship.pad_size(name), trade_ship.LARGE, name)

    def test_the_lynx_highliner_needs_a_medium_pad(self):
        for name in ("mediumtransport01", "MediumTransport01", "Lynx Highliner"):
            self.assertEqual(trade_ship.pad_size(name), trade_ship.MEDIUM, name)

    def test_a_pad_is_never_guessed_for_a_ship_not_in_the_pad_table(self):
        self.assertIsNone(trade_ship.pad_size("brand_new_ship"))
        self.assertIsNone(trade_ship.pad_size("lander01"))          # the Nomad launches from a ship; the game gives it no pad requirement

    def test_the_ship_boxes_offer_ships_only(self):
        names = trade_ship.known_ships()
        self.assertIn("Anaconda Mk II", names)
        self.assertIn("Kestrel Mk II", names)
        self.assertNotIn("SRV", names)
        self.assertNotIn("GU-97", names)


if __name__ == "__main__":
    unittest.main()
