"""Micro-resource names (inventory_names.py): the names the game's journal and the community list give for consumables and Powerplay items, shown when the
event carries no localised name."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import inventory_names as N  # noqa: E402


class MicroResourceNameTests(unittest.TestCase):
    def test_consumables_have_their_game_names(self):
        for internal, shown in (("healthpack", "Medkit"), ("energycell", "Energy Cell"), ("amm_grenade_frag", "Frag Grenade"), ("amm_grenade_emp", "Shield Disruptor"),
                                ("amm_grenade_shield", "Shield Projector"), ("bypass", "E-Breach")):
            self.assertEqual(N.display_name(internal), shown)

    def test_powerplay_items_and_the_seed_have_their_game_names(self):
        self.assertEqual(N.display_name("powermiscindust"), "Industrial Machinery")
        self.assertEqual(N.display_name("PowerResearchData"), "Power Research Data")
        self.assertEqual(N.display_name("nm_seed"), "Unica Seed")

    def test_the_games_own_name_still_wins(self):
        self.assertEqual(N.display_name("healthpack", "Renamed Kit"), "Renamed Kit")

    def test_every_hand_written_key_is_canonical(self):
        for key in N.DISPLAY_NAMES:
            self.assertEqual(key, N.canonicalize(key), key)


if __name__ == "__main__":
    unittest.main()
