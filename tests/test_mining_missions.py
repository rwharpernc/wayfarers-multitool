"""What active mining missions still need, against the hold (plugin/mining_missions.py)."""

import os
import sys
import unittest
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from plugin import mining_missions as M  # noqa: E402


@dataclass
class Mission:
    commodity: str
    commodity_key: str
    needed_commodity_count: int


class NeedTests(unittest.TestCase):
    def test_needs_are_summed_per_commodity_and_the_hold_is_applied(self) -> None:
        missions = [Mission("Painite", "painite", 80), Mission("Painite", "painite", 40), Mission("Osmium", "osmium", 25)]
        found = M.needs(missions, {"Painite": 50, "osmium": 100})
        self.assertEqual(found, [M.MiningNeed("Painite", 120, 50, 2), M.MiningNeed("Osmium", 25, 25, 1)])   # a hold over the need counts only the need

    def test_missions_that_are_not_mining_or_are_done_are_left_out(self) -> None:
        missions = [Mission("", "", 0), Mission("Gold", "gold", 0), Mission("Gold", "", 9)]
        self.assertEqual(M.needs(missions, {"gold": 3}), [])

    def test_lines(self) -> None:
        found = [M.MiningNeed("Painite", 120, 50, 2), M.MiningNeed("Osmium", 25, 25, 1)]
        self.assertEqual(M.lines(found), ["Mission needs: Painite 50 of 120 t held (2 missions)", "Mission needs: Osmium 25 of 25 t held"])
        many = [M.MiningNeed(f"C{i}", 10 - i, 0, 1) for i in range(5)]
        self.assertEqual(M.lines(many)[-1], "+2 more commodities")
        self.assertEqual(M.lines([]), [])


if __name__ == "__main__":
    unittest.main()
