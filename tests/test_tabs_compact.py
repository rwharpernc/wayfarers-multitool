"""A compact Tabs bar (nested inside a pane) is smaller and takes the pane's color, so it does not read as a second page-level tab bar."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin.uikit import palette as P  # noqa: E402
from plugin.uikit.widgets import Tabs  # noqa: E402


class CompactTabsTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display")
        self.addCleanup(self.root.destroy)

    def label_of(self, tabs: Tabs):
        return tabs._tabs[0][0]

    def test_a_compact_bar_is_smaller_and_uses_the_pane_color(self):
        full, compact = Tabs(self.root), Tabs(self.root, compact=True)
        full.add("Worth mapping")
        compact.add("Worth mapping")
        self.assertEqual(str(compact.cget("bg")), P.PANE)
        self.assertEqual(str(self.label_of(compact).cget("bg")), P.PANE)
        self.assertLess(int(str(self.label_of(compact).cget("padx"))), int(str(self.label_of(full).cget("padx"))))
        self.assertLess(int(str(self.label_of(compact).cget("pady"))), int(str(self.label_of(full).cget("pady"))))

    def test_the_selected_underline_is_the_accent_and_the_others_match_the_bar(self):
        tabs = Tabs(self.root, compact=True)
        tabs.add("One")
        tabs.add("Two")
        tabs.select(1)
        self.assertEqual(str(tabs._tabs[1][1].cget("bg")), P.ACCENT)
        self.assertEqual(str(tabs._tabs[0][1].cget("bg")), P.PANE)

    def test_the_default_bar_is_unchanged(self):
        tabs = Tabs(self.root)
        tabs.add("One")
        self.assertEqual(str(tabs.cget("bg")), P.BG)


if __name__ == "__main__":
    unittest.main()
