"""Hiding one group of overlay displays on its own (overlay.set_group_hidden): the Exploration Dashboard's two switches."""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_config = types.ModuleType("config")
_config.appname = "EDMarketConnector"
_config.config = types.SimpleNamespace(get_str=lambda key: "", set=lambda *a, **k: None)
sys.modules.setdefault("config", _config)
sys.modules.setdefault("myNotebook", types.ModuleType("myNotebook"))

from plugin import overlay  # noqa: E402

EXPLORATION = ("wfmt_route_", "wfmt_targets_")
EXOBIOLOGY = ("wfmt_exo_status_", "wfmt_exo_radar_")


class GroupHideTests(unittest.TestCase):
    def setUp(self):
        self._reset()
        self.sent = []
        patcher = mock.patch.object(overlay.OverlayClient, "_send_raw", lambda _self, payload: self.sent.append(payload))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._reset)
        self.client = overlay.OverlayClient()

    @staticmethod
    def _reset():
        overlay._hidden = False
        overlay._hidden_groups.clear()
        overlay._group_hidden_since.clear()
        overlay._last.clear()

    def draw(self):
        self.client.send_message("wfmt_route_line1", "route", "#fff", 1, 2, ttl=30)
        self.client.send_message("wfmt_targets_row1", "target", "#fff", 1, 2, ttl=30)
        self.client.send_message("wfmt_exo_status_title", "bio", "#fff", 1, 2, ttl=30)
        self.client.send_message("wfmt_flight_card", "fuel", "#fff", 1, 2, ttl=30)
        self.sent.clear()

    def test_hiding_a_group_clears_only_its_displays(self):
        self.draw()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        self.assertEqual({p["id"] for p in self.sent}, {"wfmt_route_line1", "wfmt_targets_row1"})
        self.assertTrue(all(p == {"id": p["id"], "ttl": 0} for p in self.sent))      # a removal, not a replacement that lingers
        self.assertTrue(overlay.group_hidden("exploration"))
        self.assertFalse(overlay.group_hidden("exobiology"))

    def test_showing_a_group_puts_back_what_lapsed_while_it_was_off(self):
        self.draw()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        payload, when = overlay._last["wfmt_targets_row1"]
        overlay._last["wfmt_targets_row1"] = (dict(payload, ttl=4), when - 120)         # a short-lived card, last drawn when it was switched off two minutes ago
        overlay._group_hidden_since["exploration"] -= 120
        self.sent.clear()
        overlay.set_group_hidden("exploration", EXPLORATION, False)
        self.assertEqual({p["id"]: p["ttl"] for p in self.sent}["wfmt_targets_row1"], 4)

    def test_a_hidden_group_is_not_drawn_but_the_others_are(self):
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        self.client.send_message("wfmt_route_line1", "route", "#fff", 1, 2, ttl=30)
        self.client.send_message("wfmt_exo_status_title", "bio", "#fff", 1, 2, ttl=30)
        self.assertEqual([p["id"] for p in self.sent], ["wfmt_exo_status_title"])

    def test_showing_puts_back_what_was_up_including_what_was_drawn_while_hidden(self):
        self.draw()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        self.client.send_message("wfmt_route_line2", "later", "#fff", 1, 2, ttl=30)
        self.sent.clear()
        overlay.set_group_hidden("exploration", EXPLORATION, False)
        self.assertEqual({p["id"] for p in self.sent}, {"wfmt_route_line1", "wfmt_route_line2", "wfmt_targets_row1"})
        self.assertTrue(all(p["ttl"] > 1 for p in self.sent))
        self.assertFalse(overlay.group_hidden("exploration"))

    def test_switching_to_the_same_state_does_nothing(self):
        self.draw()
        overlay.set_group_hidden("exploration", EXPLORATION, False)
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        self.sent.clear()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        self.assertEqual(self.sent, [])

    def test_two_groups_are_independent(self):
        self.draw()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        overlay.set_group_hidden("exobiology", EXOBIOLOGY, True)
        self.sent.clear()
        overlay.set_group_hidden("exploration", EXPLORATION, False)
        self.assertEqual({p["id"] for p in self.sent}, {"wfmt_route_line1", "wfmt_targets_row1"})       # the exobiology card stays down

    def test_showing_everything_leaves_a_hidden_group_hidden(self):
        self.draw()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        overlay.set_all_hidden(True)
        self.sent.clear()
        overlay.set_all_hidden(False)
        self.assertEqual({p["id"] for p in self.sent}, {"wfmt_exo_status_title", "wfmt_flight_card"})
        self.assertTrue(overlay.group_hidden("exploration"))

    def test_hiding_a_group_while_everything_is_hidden_only_records_it(self):
        self.draw()
        overlay.set_all_hidden(True)
        self.sent.clear()
        overlay.set_group_hidden("exploration", EXPLORATION, True)
        self.assertEqual(self.sent, [])
        overlay.set_all_hidden(False)
        self.assertEqual({p["id"] for p in self.sent}, {"wfmt_exo_status_title", "wfmt_flight_card"})

    def test_listeners_hear_about_each_change(self):
        heard = []
        overlay.on_group_visibility_change(lambda name, hidden: heard.append((name, hidden)))
        self.addCleanup(lambda: overlay._group_listeners.clear())
        overlay.set_group_hidden("exobiology", EXOBIOLOGY, True)
        overlay.set_group_hidden("exobiology", EXOBIOLOGY, False)
        self.assertEqual(heard, [("exobiology", True), ("exobiology", False)])

    def test_the_real_cards_use_these_prefixes(self):
        """The dashboard hides by id prefix, so the prefixes it lists must be the ones the cards are named with."""
        import re
        root = os.path.join(os.path.dirname(__file__), "..", "plugin")
        for module, prefix in (("route_overlay", "wfmt_route_"), ("targets_overlay", "wfmt_targets_"), ("body_info_overlay", "wfmt_body_info_"),
                               ("expedition_log_overlay", "wfmt_expedition_log_"), ("surface_compass", "wfmt_compass_"),
                               ("discovery", "wfmt_discovery_"), ("notable", "wfmt_notable_")):
            with open(os.path.join(root, module + ".py"), encoding="utf-8") as handle:
                self.assertRegex(handle.read(), r'GROUP_PREFIX = "%s"' % re.escape(prefix), module)


    def test_the_dashboards_groups_list_exactly_those_prefixes(self):
        """explore_dashboard.GROUPS is what the header buttons hide; every prefix in it must be a real card prefix and every exploration or exobiology card must be in it."""
        import re
        root = os.path.join(os.path.dirname(__file__), "..", "plugin")
        with open(os.path.join(root, "explore_dashboard.py"), encoding="utf-8") as handle:
            source = handle.read()
        block = source[source.index("GROUPS: Dict"):source.index("def summary_text")]
        listed = set(re.findall(r'"(wfmt_[a-z_]+_)"', block))
        with open(os.path.join(root, "exobiology_overlay.py"), encoding="utf-8") as handle:
            exo = set(re.findall(r'"(wfmt_exo_[a-z]+_)"', handle.read()))
        expected = {"wfmt_route_", "wfmt_targets_", "wfmt_body_info_", "wfmt_expedition_log_", "wfmt_compass_", "wfmt_discovery_", "wfmt_notable_"} | exo
        self.assertEqual(listed, expected)
        self.assertEqual(len(exo), 4)


if __name__ == "__main__":
    unittest.main()
