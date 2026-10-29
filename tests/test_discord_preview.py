"""The customize dialog's preview (discord_preview.py): how a post's markdown is drawn."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import discord_format as fmt, discord_preview as V  # noqa: E402


def plain(text):
    return "".join(piece for piece, _tags in V.segments(text))


class Preview(unittest.TestCase):
    def test_bold_italic_and_links(self):
        self.assertEqual(V.segments("a **b** *c* [d](<https://e.com>) f"),
                         [("a ", ()), ("b", ("bold",)), (" ", ()), ("c", ("italic",)), (" ", ()), ("d", ("link",)), (" f", ())])

    def test_an_escaped_mark_shows_as_itself(self):
        self.assertEqual(plain("Sagittarius A\\* \\_x\\_ \\(y\\)"), "Sagittarius A* _x_ (y)")
        self.assertEqual(plain(fmt.bold("A*B")), "A*B")

    def test_bullets(self):
        self.assertEqual(plain("- one\n  - two"), "• one\n    • two")
        self.assertEqual(plain("no bullet - here"), "no bullet - here")

    def test_a_real_post_reads_cleanly(self):
        text = "**WFMT BGS report**\n*Current tick*\n**Nervi**\n- **Nervi Brotherhood** — Boom, 45.2% \\(+1.3\\)\n  - You: 2 mission\\(s\\) done"
        self.assertEqual(plain(text), "WFMT BGS report\nCurrent tick\nNervi\n• Nervi Brotherhood — Boom, 45.2% (+1.3)\n    • You: 2 mission(s) done")

    def test_bold_inside_a_link_label_and_nesting(self):
        self.assertEqual(V.segments("**a *b* c**"), [("a ", ("bold",)), ("b", ("bold", "italic")), (" c", ("bold",))])

    def test_empty_and_plain_text(self):
        self.assertEqual(V.segments(""), [])
        self.assertEqual(V.segments("just text"), [("just text", ())])


if __name__ == "__main__":
    unittest.main()
