"""The shared text size of WFMT's windows (uikit.style), and how a DataTable fits its columns to the content."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin.uikit import palette as P  # noqa: E402
from plugin.uikit import style  # noqa: E402
from plugin.uikit.table import Column, DataTable  # noqa: E402


class TextSizeTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display")
        self.addCleanup(self.root.destroy)
        style._fonts.clear()      # fonts cached for an earlier test's Tk application are gone
        self.addCleanup(style.set_text_delta, 0)
        style.set_text_delta(0)

    def test_the_cached_fonts_follow_the_setting_in_place(self):
        body = style.font(P.FONT_BODY)
        before = abs(int(body.cget("size")))
        style.set_text_delta(3)
        self.assertEqual(abs(int(body.cget("size"))), before + 3)
        style.set_text_delta(0)
        self.assertEqual(abs(int(body.cget("size"))), before)

    def test_the_setting_is_kept_within_its_limits(self):
        style.set_text_delta(99)
        self.assertEqual(style.text_delta(), style.TEXT_DELTA_MAX)
        style.set_text_delta(-99)
        self.assertEqual(style.text_delta(), style.TEXT_DELTA_MIN)

    def test_listeners_hear_a_change_once_and_can_stop(self):
        heard = []
        stop = style.add_text_listener(lambda: heard.append(style.text_delta()))
        style.set_text_delta(2)
        style.set_text_delta(2)           # no change, no call
        stop()
        style.set_text_delta(4)
        self.assertEqual(heard, [2])

    def test_a_table_measures_its_columns_again_at_a_new_size(self):
        columns = [Column("name", "Name", 40, stretch=False), Column("n", "Tons", 40, anchor="e")]
        table = DataTable(self.root, columns)
        table.pack()
        table.insert("a", ("Steel", "1,000"))
        self.root.update()
        before = table._header.winfo_reqwidth()
        style.set_text_delta(6)
        self.root.update()
        self.assertGreater(table._header.winfo_reqwidth(), before)

    def test_short_columns_stay_narrow_and_long_ones_take_the_spare_width(self):
        columns = [Column("a", "A", 200), Column("b", "Description", 40)]
        table = DataTable(self.root, columns)
        table.pack(fill="x")
        table.insert("r", ("x", "a rather longer piece of text than the first column"))
        self.root.update()
        a_width, b_width = table._header.grid_bbox(0, 0)[2], table._header.grid_bbox(1, 0)[2]
        self.assertLess(a_width, 200)           # the declared width is only a floor for an empty table
        self.assertGreater(b_width, a_width)


if __name__ == "__main__":
    unittest.main()
