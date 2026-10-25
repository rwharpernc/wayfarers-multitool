"""Hiding every overlay for a while (overlay.py's switch and overlay_visibility.py's panel line)."""
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
from plugin import overlay_visibility as V  # noqa: E402


class HideTests(unittest.TestCase):
    def setUp(self):
        overlay._hidden = False
        overlay._last.clear()
        self.sent = []
        patcher = mock.patch.object(overlay.OverlayClient, "_send_raw", lambda _self, payload: self.sent.append(payload))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: (setattr(overlay, "_hidden", False), setattr(overlay, "_hidden_since", 0.0), overlay._last.clear()))
        self.client = overlay.OverlayClient()

    def draw(self):
        self.client.send_message("t1", "hello", "#fff", 10, 20, ttl=4)
        self.client.send_shape("r1", "rect", "#000", "#111", 1, 2, 30, 40, ttl=4)
        self.client.send_circle("c1", "#fff", "#000", 5, 6, 7, ttl=4)
        self.client.send_vector("v1", [{"x": 1, "y": 2}, {"x": 3, "y": 4}], "#fff", ttl=4)

    def test_hiding_clears_everything_drawn_and_stops_new_drawing(self):
        self.draw()
        self.sent.clear()
        overlay.set_all_hidden(True)
        by_id = {p["id"]: p for p in self.sent}
        self.assertEqual(set(by_id), {"t1", "r1", "c1", "v1"})
        for ident in ("t1", "r1", "c1", "v1"):                             # every kind of item is removed by id (see tests/test_overlay_clear.py)
            self.assertEqual(by_id[ident], {"id": ident, "ttl": 0}, ident)
        self.sent.clear()
        self.client.send_message("t2", "later", "#fff", 0, 0, ttl=4)
        self.assertEqual(self.sent, [])                      # not drawn while hidden
        self.assertTrue(overlay.all_hidden())

    def test_showing_puts_back_what_was_up_including_what_was_drawn_while_hidden(self):
        self.draw()
        overlay.set_all_hidden(True)
        self.client.send_message("t2", "later", "#fff", 0, 0, ttl=4)
        self.sent.clear()
        overlay.set_all_hidden(False)
        self.assertEqual({p["id"] for p in self.sent}, {"t1", "r1", "c1", "v1", "t2"})
        self.assertTrue(all(p["ttl"] >= 1 for p in self.sent))
        self.assertEqual({p["id"]: p["text"] for p in self.sent if "text" in p}["t1"], "hello")

    def test_something_that_ran_out_is_not_put_back_and_a_clear_forgets_the_id(self):
        self.client.send_message("old", "gone", "#fff", 0, 0, ttl=4)
        self.client.send_message("cleared", "x", "#fff", 0, 0, ttl=4)
        self.client.send_message("cleared", "", "white", 0, 0, ttl=1)
        overlay._last["old"] = (overlay._last["old"][0], overlay._last["old"][1] - 100)         # drawn long ago
        overlay.set_all_hidden(True)
        self.sent.clear()
        overlay.set_all_hidden(False)
        self.assertEqual(self.sent, [])

    def test_a_display_that_lapsed_while_hidden_comes_back_with_its_full_ttl(self):
        self.client.send_message("card_text", "hello", "#fff", 0, 0, ttl=4)
        self.client.send_shape("card", "rect", "#000", "#111", 0, 0, 10, 10, ttl=8)
        overlay.set_all_hidden(True)
        overlay._hidden_since -= 60                                            # a minute ago it was switched off, and the cards were last drawn then
        for ident in ("card_text", "card"):
            payload, when = overlay._last[ident]
            overlay._last[ident] = (payload, when - 60)
        self.sent.clear()
        overlay.set_all_hidden(False)
        self.assertEqual({p["id"]: p["ttl"] for p in self.sent}, {"card_text": 4, "card": 8})

    def test_hiding_removes_only_what_is_on_the_screen(self):
        self.client.send_message("showing", "x", "#fff", 0, 0, ttl=4)
        self.client.send_message("lapsed", "y", "#fff", 0, 0, ttl=4)
        overlay._last["lapsed"] = (overlay._last["lapsed"][0], overlay._last["lapsed"][1] - 100)
        self.sent.clear()
        overlay.set_all_hidden(True)
        self.assertEqual([p["id"] for p in self.sent], ["showing"])

    def test_the_old_clear_forms_become_removals_and_only_for_what_is_on_the_screen(self):
        self.client.send_message("t", "hello", "#fff", 0, 0, ttl=4)
        self.client.send_shape("r", "rect", "#000", "#111", 0, 0, 10, 10, ttl=8)
        self.sent.clear()
        self.client.send_message("t", "", "white", 0, 0, ttl=1)
        self.client.send_shape("r", "rect", "", "", 0, 0, 0, 0, ttl=1)
        self.assertEqual(self.sent, [{"id": "t", "ttl": 0}, {"id": "r", "ttl": 0}])
        self.sent.clear()
        self.client.send_message("never_drawn", "", "white", 0, 0, ttl=1)           # nothing to remove: nothing sent
        self.client.send_shape("never_drawn_r", "rect", "", "", 0, 0, 0, 0, ttl=1)
        self.assertEqual(self.sent, [])

    def test_is_clear_form_does_not_catch_real_drawings(self):
        self.assertTrue(overlay.is_clear_form({"id": "a", "text": "", "ttl": 1}))
        self.assertTrue(overlay.is_clear_form({"id": "a", "shape": "rect", "color": "", "fill": "", "w": 0, "h": 0, "ttl": 1}))
        self.assertFalse(overlay.is_clear_form({"id": "a", "text": "hi", "ttl": 1}))
        self.assertFalse(overlay.is_clear_form({"id": "a", "text": "", "ttl": 4}))
        self.assertFalse(overlay.is_clear_form({"id": "a", "shape": "rect", "color": "#fff", "fill": "", "w": 10, "h": 10, "ttl": 1}))

    def test_a_long_lasting_display_comes_back_with_the_time_it_had_left(self):
        self.client.send_shape("card", "rect", "#000", "#111", 0, 0, 10, 10, ttl=3600)
        overlay.set_all_hidden(True)
        self.sent.clear()
        overlay.set_all_hidden(False)
        self.assertEqual(len(self.sent), 1)
        self.assertGreater(self.sent[0]["ttl"], 3000)

    def test_listeners_hear_each_change_and_a_repeat_changes_nothing(self):
        heard = []
        overlay.on_visibility_change(heard.append)
        self.addCleanup(lambda: overlay._listeners.remove(heard.append))
        overlay.set_all_hidden(True)
        overlay.set_all_hidden(True)
        self.assertTrue(overlay.toggle_all_hidden() is False)
        self.assertEqual(heard, [True, False])


class PanelLineTests(unittest.TestCase):
    def test_the_panel_line_says_which_state_it_is_in(self):
        self.assertIn("hidden", V.panel_text(True))
        self.assertIn("shown", V.panel_text(False))


if __name__ == "__main__":
    unittest.main()
