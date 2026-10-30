"""Powerplay overlay (powerplay_overlay.py): what the card says in each situation, and that the controller hands it only the system you are in."""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for name in ("myNotebook", "ttkHyperlinkLabel", "theme", "monitor", "plug", "l10n", "requests"):
    sys.modules.setdefault(name, mock.MagicMock())
if "config" not in sys.modules:
    config_stub = types.ModuleType("config")
    config_stub.appname = "EDMarketConnector"
    config_stub.config = mock.MagicMock()
    sys.modules["config"] = config_stub

from plugin import powerplay, powerplay_overlay as O  # noqa: E402
from plugin.formulas import ACQUISITION, DELIVERY, REINFORCEMENT, UNDERMINING, UNKNOWN  # noqa: E402


def rows(card):
    return {left: (right, role) for left, right, role in card.rows}


class BuildCardTests(unittest.TestCase):
    def test_no_info_or_no_state_is_an_empty_card(self):
        self.assertFalse(O.build_card(None))
        self.assertFalse(O.build_card(O.Info("Sol", "")))

    def test_the_sample_card_shows_everything(self):
        card = O.build_card(O.sample_info())
        self.assertEqual(card.title[0], "Sample System")
        self.assertEqual(card.badge, "Rank 12")
        shown = rows(card)
        self.assertEqual(shown["Power"][0], "Aisling Duval")
        self.assertEqual(shown["Total merits"][0], "1,204,500")
        self.assertEqual(shown["Cycle 41 merits"][0], "86,300")
        self.assertEqual(shown["System"][0], "Fortified")
        self.assertEqual(shown["Held by"][0], "Aisling Duval")
        self.assertEqual(shown["Merits here count as"][0], "Reinforcement")
        self.assertEqual(shown["Reinforcement"][0], "4,200 merits · ~1680 CP")

    def test_a_delivery_shows_merits_but_no_control_points(self):
        shown = rows(O.build_card(O.sample_info()))
        self.assertEqual(shown["Delivery/Donation"][0], "1,500 merits")

    def test_not_pledged_leaves_out_the_power_figures_and_the_guess(self):
        shown = rows(O.build_card(O.Info("Sol", "Unoccupied", activity=ACQUISITION)))
        self.assertEqual(shown["Power"][0], "not pledged")
        self.assertNotIn("Total merits", shown)
        self.assertNotIn("Merits here count as", shown)
        self.assertNotIn("Earned here", shown)
        self.assertEqual(O.build_card(O.Info("Sol", "Unoccupied")).badge, "")

    def test_nothing_earned_yet_says_so(self):
        info = O.Info("Sol", "Stronghold", "Li Yong-Rui", "Li Yong-Rui", 3, 100, "Cycle 2", 0, UNDERMINING)
        shown = rows(O.build_card(info))
        self.assertEqual(shown["Earned here"][0], "nothing yet")
        self.assertEqual(shown["Merits here count as"][0], "Undermining")

    def test_an_unheld_system_says_no_one_holds_it(self):
        self.assertEqual(rows(O.build_card(O.Info("Sol", "Unoccupied")))["Held by"][0], "no one")


class ControllerInfoTests(unittest.TestCase):
    def controller(self, system="Nervi", here="Nervi"):
        c = powerplay.PowerplayController()
        c.sessions = mock.MagicMock()
        c.sessions.current = {"by_system": {"Nervi": {"totals": {REINFORCEMENT: 500, DELIVERY: 100}}}}
        c.tracker.my_power, c.tracker.rank, c.tracker.total_merits = "Zachary Hudson", 5, 9000
        c.tracker.system_name, c.tracker.system_state, c.tracker.system_controller = system, "Exploited", "Zachary Hudson"
        c._current_system = here
        return c

    def test_the_figures_come_from_the_tracker_and_the_session(self):
        info = self.controller().overlay_info()
        self.assertEqual((info.system, info.state, info.power, info.rank, info.total_merits), ("Nervi", "Exploited", "Zachary Hudson", 5, 9000))
        self.assertEqual(info.activity, REINFORCEMENT)
        self.assertEqual(dict(info.here), {REINFORCEMENT: 500, DELIVERY: 100})
        self.assertEqual(dict(info.cp), {REINFORCEMENT: 200.0})     # 500 merits at 2.5 per CP; deliveries earn none

    def test_a_context_kept_from_an_earlier_system_is_not_shown(self):
        self.assertIsNone(self.controller(system="Nervi", here="Sol").overlay_info())

    def test_no_powerplay_state_is_nothing_to_show(self):
        c = self.controller()
        c.tracker.system_state = None
        self.assertIsNone(c.overlay_info())

    def test_system_activity_changes_nothing(self):
        c = self.controller()
        c.tracker._delivery_pending = True
        before = dict(vars(c.tracker))
        self.assertEqual(c.tracker.system_activity("Nervi"), REINFORCEMENT)
        self.assertEqual(vars(c.tracker), before)
        c.tracker.system_controller = "Someone Else"
        self.assertEqual(c.tracker.system_activity("Nervi"), UNDERMINING)
        c.tracker.my_power = None
        self.assertEqual(c.tracker.system_activity("Nervi"), UNKNOWN)


if __name__ == "__main__":
    unittest.main()
