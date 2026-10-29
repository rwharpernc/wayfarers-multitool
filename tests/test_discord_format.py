"""Discord text (plugin/discord_format.py): escaping, mentions, links, code blocks, timestamps and splitting into messages."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import discord_format as D  # noqa: E402

ZW = D.ZERO_WIDTH_SPACE


class Escaping(unittest.TestCase):
    def test_marks_that_would_format_are_escaped(self):
        self.assertEqual(D.escape("a*b_c~d`e|f"), "a\\*b\\_c\\~d\\`e\\|f")
        self.assertEqual(D.escape("[x](y) # > \\"), "\\[x\\]\\(y\\) \\# \\> \\\\")

    def test_a_star_name_stays_readable(self):
        self.assertEqual(D.escape("Sagittarius A*"), "Sagittarius A\\*")

    def test_mentions_and_tags_are_defused(self):
        out = D.escape("@everyone @here <@123> <#456> <:name:789> <t:1:F>")
        for risky in ("@everyone", "@here", "<@", "<#", "<:", "<t:"):
            self.assertNotIn(risky, out)
        self.assertEqual(out.replace(ZW, "").replace("\\", ""), "@everyone @here <@123> <#456> <:name:789> <t:1:F>")

    def test_text_goes_on_one_line(self):
        self.assertEqual(D.escape("a\n  b\r\nc"), "a b c")

    def test_bold_and_italic_skip_empty_text(self):
        self.assertEqual(D.bold("Sol"), "**Sol**")
        self.assertEqual(D.bold("  "), "")
        self.assertEqual(D.italic("est"), "*est*")
        self.assertEqual(D.bold("A*B"), "**A\\*B**")


class Links(unittest.TestCase):
    def test_a_link_does_not_unfurl(self):
        self.assertEqual(D.link("Nervi", "https://inara.cz/x?a=1"), "[Nervi](<https://inara.cz/x?a=1>)")

    def test_label_marks_and_url_brackets_are_made_safe(self):
        self.assertEqual(D.link("[a]", "https://e.com/a b>c"), "[\\[a\\]](<https://e.com/a%20b%3Ec>)")

    def test_a_url_that_is_not_http_leaves_the_label(self):
        self.assertEqual(D.link("Sol", "javascript:alert(1)"), "Sol")
        self.assertEqual(D.link("Sol", ""), "Sol")


class Blocks(unittest.TestCase):
    def test_a_code_block_cannot_be_closed_early(self):
        block = D.code_block(["a", "x```y"])
        self.assertEqual(block.count("```"), 2)
        self.assertTrue(block.startswith("```\n") and block.endswith("\n```"))

    def test_timestamps(self):
        self.assertEqual(D.timestamp(1790000000.9), "<t:1790000000:F>")
        self.assertEqual(D.timestamp(5, "R"), "<t:5:R>")
        self.assertEqual(D.timestamp(5, "x"), "<t:5:F>")


class Splitting(unittest.TestCase):
    def test_short_blocks_join_into_one_message(self):
        self.assertEqual(D.split_message(["one", "two"], 100), ["one\ntwo"])

    def test_empty_blocks_are_skipped(self):
        self.assertEqual(D.split_message(["", "  ", "a\n", "b"], 100), ["a\nb"])
        self.assertEqual(D.split_message([], 100), [])

    def test_blocks_are_kept_whole_and_split_between(self):
        out = D.split_message(["a" * 60, "b" * 60, "c" * 30], 100)
        self.assertEqual(out, ["a" * 60, "b" * 60 + "\n" + "c" * 30])

    def test_every_message_fits(self):
        blocks = [f"system {i}\n" + "\n".join(f"line {i} {j}" for j in range(12)) for i in range(40)]
        out = D.split_message(blocks)
        self.assertTrue(len(out) > 1)
        self.assertTrue(all(len(m) <= D.MESSAGE_LIMIT for m in out))
        self.assertEqual("\n".join(out), "\n".join(blocks))

    def test_a_long_block_is_cut_between_lines(self):
        block = "\n".join(f"row {i:03d} " + "x" * 30 for i in range(30))
        out = D.split_message([block], 200)
        self.assertTrue(len(out) > 1 and all(len(m) <= 200 for m in out))
        self.assertEqual("\n".join(out), block)

    def test_a_cut_code_block_is_closed_and_reopened(self):
        block = D.code_block([f"row {i:03d} " + "x" * 20 for i in range(40)])
        out = D.split_message([block], 300)
        self.assertTrue(len(out) > 1)
        for message in out:
            self.assertLessEqual(len(message), 300)
            self.assertEqual(message.count("```") % 2, 0, message)
        rows = [line for message in out for line in message.split("\n") if line.startswith("row ")]
        self.assertEqual(len(rows), 40)

    def test_a_line_longer_than_a_message_is_cut(self):
        out = D.split_message(["y" * 450], 100)
        self.assertTrue(all(len(m) <= 100 for m in out))
        self.assertEqual("".join(out), "y" * 450)


if __name__ == "__main__":
    unittest.main()
