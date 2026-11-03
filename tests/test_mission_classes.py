"""Mission names the journals write, and the page each lands on. Pure logic."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import mission_types as mt  # noqa: E402


class SupportMissionTests(unittest.TestCase):
    def test_donations_and_rescues_have_a_page_of_their_own(self) -> None:
        for name in ("Mission_AltruismCredits", "Mission_Altruism", "Mission_AltruismCredits_CivilUnrest",
                     "Mission_AltruismCredits_Outbreak", "Mission_AltruismCredits_Bust", "Mission_AltruismCredits_Famine",
                     "Mission_Rescue", "Mission_Rescue_Planet", "Mission_Rescue_Planet_Expansion", "Mission_Rescue_Agricultural"):
            self.assertEqual(mt.classify({"Name": name}), mt.SUPPORT, name)

    def test_the_page_is_labelled_and_ordered(self) -> None:
        self.assertEqual(mt.CATEGORY_LABELS[mt.SUPPORT], "Donation & Rescue")
        self.assertIn(mt.SUPPORT, mt.CATEGORY_ORDER)
        self.assertEqual(mt.CATEGORY_ORDER[-1], mt.OTHER)
        self.assertEqual(set(mt.CATEGORY_ORDER), set(mt.CATEGORY_LABELS))

    def test_scan_missions_are_combat(self) -> None:
        self.assertEqual(mt.classify({"Name": "MISSION_Scan"}), mt.COMBAT)

    def test_earlier_rules_are_not_changed(self) -> None:
        self.assertEqual(mt.classify({"Name": "Mission_Delivery"}), mt.TRADE)
        self.assertEqual(mt.classify({"Name": "Mission_Massacre"}), mt.MASSACRE_SPACE)
        self.assertEqual(mt.classify({"Name": "Mission_TheDead"}), mt.OTHER)


if __name__ == "__main__":
    unittest.main()
