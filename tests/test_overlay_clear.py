"""Clearing a line or a circle on the overlay (overlay.OverlayClient.send_vector, send_circle, send_clear and removal_payload).

EDMCModernOverlay rejects a line with no points (and a one-point line with no marker) as having too few points, logging a warning each time, so a clear sent that way never arrived;
and a circle with no color is drawn white, a dot where the circle was. What it accepts as a removal is a payload with an id and a ttl of 0 and nothing to draw. The Bio radar
clears every slot it is not using on each draw (seventeen lines a second), which flooded EDMC's log with thousands of warnings."""
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

from plugin import overlay, overlay_scene  # noqa: E402

POINTS = [{"x": 1, "y": 2}, {"x": 5, "y": 6}]


class ClearTests(unittest.TestCase):
    def setUp(self):
        overlay._hidden = False
        overlay._hidden_groups.clear()
        overlay._last.clear()
        self.sent = []
        patcher = mock.patch.object(overlay.OverlayClient, "_send_raw", lambda _self, payload: self.sent.append(payload))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: (setattr(overlay, "_hidden", False), overlay._hidden_groups.clear(), overlay._last.clear()))
        self.client = overlay.OverlayClient()

    def test_the_removal_is_an_id_and_a_ttl_of_zero_and_nothing_to_draw(self):
        self.assertEqual(overlay.removal_payload("wfmt_x"), {"id": "wfmt_x", "ttl": 0})

    def test_clearing_a_drawn_line_sends_a_removal_not_an_empty_line(self):
        self.client.send_vector("v1", POINTS, "#fff", ttl=4)
        self.sent.clear()
        self.client.send_vector("v1", [], "white", ttl=1)
        self.assertEqual(self.sent, [{"id": "v1", "ttl": 0}])
        self.assertNotIn("v1", overlay._last)

    def test_clearing_a_line_that_is_not_on_the_screen_sends_nothing(self):
        self.client.send_vector("v1", [], "white", ttl=1)
        self.assertEqual(self.sent, [])

    def test_a_clear_is_sent_once(self):
        self.client.send_vector("v1", POINTS, "#fff", ttl=4)
        self.sent.clear()
        for _ in range(5):
            self.client.send_vector("v1", [], "white", ttl=1)
        self.assertEqual(len(self.sent), 1)

    def test_a_radar_clearing_every_unused_slot_each_draw_sends_nothing_when_nothing_is_up(self):
        for _ in range(3):
            for slot in ["ahead", "north"] + [f"point{i}" for i in range(5)] + [f"a{i}" for i in range(10)]:
                self.client.send_vector(f"wfmt_exo_radar_{slot}", [], "white", ttl=1)
        self.assertEqual(self.sent, [])

    def test_only_what_is_drawn_is_removed(self):
        self.client.send_vector("wfmt_exo_radar_ahead", POINTS, "#fff", ttl=4)
        self.sent.clear()
        for slot in ["ahead", "north", "point0", "a0"]:
            self.client.send_vector(f"wfmt_exo_radar_{slot}", [], "white", ttl=1)
        self.assertEqual([p["id"] for p in self.sent], ["wfmt_exo_radar_ahead"])

    def test_a_circle_with_no_color_is_cleared_not_drawn_white(self):
        self.client.send_circle("c1", "#fff", "#000", 5, 6, 7, ttl=4)
        self.sent.clear()
        self.client.send_circle("c1", "", "", 5, 6, 7, ttl=1)
        self.assertEqual(self.sent, [{"id": "c1", "ttl": 0}])
        self.client.send_circle("c1", "", "", 5, 6, 7, ttl=1)
        self.assertEqual(len(self.sent), 1)                         # not on the screen any more: nothing more to send

    def test_a_circle_with_a_color_is_still_drawn(self):
        self.client.send_circle("c1", "#fff", "", 5, 6, 7, ttl=4)
        self.assertEqual(self.sent[-1]["shape"], "circle")

    def test_a_one_point_line_with_a_marker_is_still_drawn(self):
        self.client.send_vector("v1", [{"x": 1, "y": 2, "marker": "cross"}], "#fff", ttl=4)
        self.assertEqual(self.sent[-1]["vector"], [{"x": 1, "y": 2, "marker": "cross"}])

    def test_hiding_everything_removes_lines_and_circles_the_same_way(self):
        self.client.send_vector("v1", POINTS, "#fff", ttl=30)
        self.client.send_circle("c1", "#fff", "#000", 5, 6, 7, ttl=30)
        self.sent.clear()
        overlay.set_all_hidden(True)
        self.assertEqual({p["id"]: p for p in self.sent}, {"v1": {"id": "v1", "ttl": 0}, "c1": {"id": "c1", "ttl": 0}})

    def test_the_built_in_overlay_drops_an_item_for_a_removal(self):
        scene = overlay_scene.Scene()
        scene.apply({"id": "v1", "shape": "vect", "color": "#fff", "ttl": 30, "vector": POINTS})
        scene.apply({"id": "c1", "shape": "circle", "color": "#fff", "x": 1, "y": 2, "radius": 7, "ttl": 30})
        self.assertEqual(len(scene.items()), 2)
        scene.apply(overlay.removal_payload("v1"))
        scene.apply(overlay.removal_payload("c1"))
        self.assertEqual(scene.items(), [])

    def test_no_clear_in_the_plugin_sends_an_empty_line_any_more(self):
        """Every place that clears a line passes an empty list to send_vector, which now turns it into a removal; nothing builds an empty-vector payload itself."""
        root = os.path.join(os.path.dirname(__file__), "..", "plugin")
        for name in sorted(os.listdir(root)):
            if not name.endswith(".py") or name == "overlay.py":
                continue
            with open(os.path.join(root, name), encoding="utf-8") as handle:
                source = handle.read()
            self.assertNotIn('"vector": []', source, name)


if __name__ == "__main__":
    unittest.main()
