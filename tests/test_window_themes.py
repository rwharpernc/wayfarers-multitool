"""The color themes of WFMT's own windows (uikit.palette, uikit.style.set_theme) and the boxes that ignore the text size."""
from __future__ import annotations

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin.uikit import palette as P  # noqa: E402
from plugin.uikit import style  # noqa: E402
from plugin.uikit.widgets import FlatButton, Pill, StatTile  # noqa: E402

HEX = re.compile(r"^#[0-9a-f]{6}$")


class PaletteTests(unittest.TestCase):
    def tearDown(self):
        P.apply(P.DEFAULT_THEME)

    def test_every_theme_defines_every_token_as_a_color(self):
        self.assertEqual(list(P.THEMES), ["Navy", "Cyan", "Amber", "Green"])
        for name, tokens in P.THEMES.items():
            self.assertEqual(set(tokens), set(P.TOKENS), name)
            for token, value in tokens.items():
                self.assertRegex(value, HEX, f"{name} {token}")

    def test_no_two_tokens_of_a_theme_share_a_color(self):
        # An open window is recolored by looking each of its colors up, so a color must name exactly one token.
        for name, tokens in P.THEMES.items():
            self.assertEqual(len(set(tokens.values())), len(tokens), name)

    def test_switching_back_to_navy_restores_the_map_colors(self):
        P.apply("Cyan")
        changes = P.apply("Navy")
        self.assertEqual(changes[P.THEMES["Cyan"]["MAP_BG"]], P.THEMES["Navy"]["MAP_BG"])
        self.assertEqual(changes[P.THEMES["Cyan"]["MAP_HOTSPOT"]], P.THEMES["Navy"]["MAP_HOTSPOT"])

    def test_text_stays_readable_on_every_surface(self):
        def luminance(color: str) -> float:
            r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
            channel = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4   # noqa: E731
            return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

        def contrast(a: str, b: str) -> float:
            hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
            return (hi + 0.05) / (lo + 0.05)

        for name, t in P.THEMES.items():
            for surface in ("BG", "PANE", "CARD"):
                for text in ("TEXT", "MUTED", "HEADING", "TITLE", "STATUS"):
                    self.assertGreaterEqual(contrast(t[text], t[surface]), 4.5, f"{name} {text} on {surface}")
            self.assertGreaterEqual(contrast(t["TEXT"], t["BUTTON"]), 4.5, f"{name} TEXT on BUTTON")
            self.assertGreaterEqual(contrast(t["ACCENT_INK"], t["ACCENT"]), 4.5, f"{name} the accent button")
            self.assertGreaterEqual(contrast(t["TEXT"], t["ROW_OK"]), 4.5, f"{name} TEXT on ROW_OK")
            self.assertGreaterEqual(contrast(t["TEXT"], t["ROW_OVER"]), 4.5, f"{name} TEXT on ROW_OVER")

    def test_apply_sets_the_tokens_and_reports_what_changed(self):
        changes = P.apply("Cyan")
        self.assertEqual((P.current(), P.BG), ("Cyan", P.THEMES["Cyan"]["BG"]))
        self.assertEqual(changes[P.THEMES["Navy"]["BG"].lower()], P.THEMES["Cyan"]["BG"])
        self.assertEqual(P.apply("Cyan"), {})                      # nothing changes when the theme is the same
        P.apply("not a theme")
        self.assertEqual(P.current(), "Navy")


class OpenWindowTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display")
        self.addCleanup(self.root.destroy)
        style._fonts.clear()
        style._fixed_fonts.clear()
        style._skinned.clear()
        self.addCleanup(style.set_theme, "Navy")
        self.addCleanup(style.set_text_delta, 0)
        style.set_theme("Navy")
        style.set_text_delta(0)

    def test_an_open_window_is_recolored_where_it_stands(self):
        import tkinter as tk
        window = tk.Toplevel(self.root)
        style.skin(window)
        label = tk.Label(window, text="x", fg=P.HEADING, bg=P.CARD)
        label.pack()
        canvas = tk.Canvas(window, bg=P.PANE)
        canvas.pack()
        item = canvas.create_rectangle(0, 0, 5, 5, fill=P.OK)
        button = FlatButton(window, "Go", lambda: None, kind="accent")
        button.pack()
        style.set_theme("Amber")
        amber = P.THEMES["Amber"]
        self.assertEqual(str(label.cget("fg")), amber["HEADING"])
        self.assertEqual(str(label.cget("bg")), amber["CARD"])
        self.assertEqual(str(canvas.cget("bg")), amber["PANE"])
        self.assertEqual(str(canvas.itemcget(item, "fill")), amber["OK"])
        self.assertEqual((str(button.cget("bg")), button._bg, button._hover), (amber["ACCENT"], amber["ACCENT"], amber["ACCENT_HI"]))
        self.assertEqual(str(window.cget("bg")), amber["PANE"])

    def test_a_widget_made_after_the_change_uses_the_new_theme(self):
        import tkinter as tk
        style.set_theme("Green")
        tile = StatTile(tk.Frame(self.root), "1", "caption")
        self.assertEqual(str(tile.cget("bg")), P.THEMES["Green"]["CARD"])
        self.assertEqual(str(tile._value.cget("fg")), P.THEMES["Green"]["TEXT"])
        self.assertEqual(str(Pill(self.root, "ok").cget("fg")), P.THEMES["Green"]["MUTED"])

    def test_tiles_and_pills_keep_their_size_whatever_the_text_size_is(self):
        import tkinter as tk
        tile, pill = StatTile(tk.Frame(self.root), "1", "caption"), Pill(self.root, "ok")
        label = tk.Label(self.root, text="x", font=style.font(P.FONT_BODY))
        sizes = lambda: (tile._value.cget("font"), abs(int(tile._value.tk.call("font", "actual", tile._value.cget("font"), "-size"))),   # noqa: E731
                         abs(int(pill.tk.call("font", "actual", pill.cget("font"), "-size"))),
                         abs(int(label.tk.call("font", "actual", label.cget("font"), "-size"))))
        before = sizes()
        style.set_text_delta(4)
        after = sizes()
        self.assertEqual(before[1:3], after[1:3])             # the tile's value and the pill did not grow
        self.assertGreater(after[3], before[3])                # ordinary text did


if __name__ == "__main__":
    unittest.main()
