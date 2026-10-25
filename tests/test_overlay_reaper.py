"""A card's panel goes when its text goes (overlay.orphaned), instead of staying as an empty shell for a few more seconds.

The text of a card lives for `ttl` seconds and its panel for twice that (so a refresh never puts the panel above the text). When a card simply stops being
redrawn the text lapsed first and the empty panel lingered. The sweep removes a panel that has carried live text and has none left.
"""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_config = types.ModuleType("config")
_config.appname = "EDMarketConnector"
_config.config = types.SimpleNamespace(get_str=lambda key: "", set=lambda *a, **k: None)
sys.modules.setdefault("config", _config)
sys.modules.setdefault("myNotebook", types.ModuleType("myNotebook"))

from plugin import overlay  # noqa: E402


def panel(ident="card", x=100, y=100, w=200, h=80, ttl=16, when=0.0):
    return ident, ({"id": ident, "shape": "rect", "x": x, "y": y, "w": w, "h": h, "ttl": ttl}, when)


def text(ident, x=110, y=110, ttl=8, when=0.0, body="Hello"):
    return ident, ({"id": ident, "text": body, "x": x, "y": y, "ttl": ttl}, when)


def circle(ident, x=150, y=130, ttl=16, when=0.0):
    return ident, ({"id": ident, "shape": "circle", "x": x, "y": y, "radius": 5, "ttl": ttl}, when)


class OrphanedPanelTests(unittest.TestCase):
    def test_a_panel_with_live_text_stays_and_is_remembered(self):
        seen = set()
        self.assertEqual(overlay.orphaned([panel(), text("t")], 3.0, seen), [])
        self.assertIn("card", seen)

    def test_the_panel_goes_as_soon_as_its_text_has_lapsed(self):
        seen = set()
        items = [panel(), text("t")]
        overlay.orphaned(items, 3.0, seen)                       # text alive: the panel is noted as having carried text
        self.assertEqual(overlay.orphaned(items, 8.5, seen), ["card"])   # text lapsed at 8, panel would live to 16
        self.assertNotIn("card", seen)

    def test_shapes_drawn_over_the_panel_go_with_it(self):
        seen = {"card"}
        items = [panel(), text("t"), circle("c"), circle("elsewhere", x=900, y=900)]
        self.assertEqual(sorted(overlay.orphaned(items, 9.0, seen)), ["c", "card"])

    def test_a_panel_that_never_had_text_is_left_to_its_own_ttl(self):
        self.assertEqual(overlay.orphaned([panel()], 9.0, set()), [])

    def test_text_elsewhere_does_not_keep_the_panel(self):
        seen = {"card"}
        items = [panel(), text("far", x=900, y=900, ttl=20)]
        self.assertEqual(overlay.orphaned(items, 9.0, seen), ["card"])

    def test_an_empty_string_is_not_live_text(self):
        seen = {"card"}
        items = [panel(), text("blank", body="", ttl=20)]
        self.assertEqual(overlay.orphaned(items, 9.0, seen), ["card"])

    def test_a_panel_already_past_its_own_ttl_is_not_touched(self):
        seen = {"card"}
        self.assertEqual(overlay.orphaned([panel(ttl=16), text("t")], 17.0, seen), [])
        self.assertNotIn("card", seen)

    def test_a_zero_size_rect_is_not_a_panel(self):
        seen = {"gone"}
        self.assertEqual(overlay.orphaned([panel("gone", w=0, h=0), text("t")], 9.0, seen), [])

    def test_a_refreshed_card_keeps_its_panel(self):
        seen = set()
        overlay.orphaned([panel(when=0.0), text("t", when=0.0)], 3.0, seen)
        refreshed = [panel(when=6.0), text("t", when=6.0)]
        self.assertEqual(overlay.orphaned(refreshed, 10.0, seen), [])


if __name__ == "__main__":
    unittest.main()
