"""A wrapped label beside a button wraps to the room left of it, not to the whole frame (panelkit.available_wrap, wrap_label).

With the whole frame width, a long line next to a button made the row wider than the frame, the window grew to fit it, and the next resize handed the label the
larger width again: the main EDMC window crept wider each time such a line changed (the Route Planner's summary was one).
"""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest import mock

panelkit = None


def setUpModule():
    """Import panelkit against stand-ins for EDMC's modules, and take them out again afterwards so nothing leaks into other tests."""
    global panelkit
    config = types.ModuleType("config")
    config.appname = "EDMarketConnector"
    config.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default)
    theme = types.ModuleType("theme")
    theme.theme = mock.MagicMock()
    patcher = mock.patch.dict(sys.modules, {"config": config, "theme": theme, "myNotebook": types.ModuleType("myNotebook")})
    patcher.start()
    for name in [m for m in sys.modules if m == "plugin.panelkit"]:
        sys.modules.pop(name)
    from plugin import panelkit as loaded
    panelkit = loaded
    globals()["_patcher"] = patcher


def tearDownModule():
    globals()["_patcher"].stop()
    sys.modules.pop("plugin.panelkit", None)


class AvailableWrapTests(unittest.TestCase):
    def test_the_room_is_the_frame_less_the_offset_and_a_margin(self):
        self.assertEqual(panelkit.available_wrap(500, 120, 150), 500 - 120 - 6)

    def test_it_is_never_below_the_floor(self):
        self.assertEqual(panelkit.available_wrap(200, 150, 150), 150)

    def test_a_label_at_the_left_edge_gets_the_frame_less_the_margin(self):
        self.assertEqual(panelkit.available_wrap(500, 0, 150), 494)
        self.assertEqual(panelkit.available_wrap(500, -5, 150), 494)


class BesideAButtonTests(unittest.TestCase):
    def test_a_long_label_next_to_a_button_fits_inside_the_frame(self):
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display")
        self.addCleanup(root.destroy)
        frame = tk.Frame(root, width=420, height=60)
        frame.pack()
        frame.pack_propagate(False)
        inner = tk.Frame(frame)
        inner.place(x=0, y=0)
        button = tk.Button(inner, text="PLOT")
        button.grid(row=0, column=0)
        label = panelkit.wrap_label(inner, min_wrap=150, text="Route to Some Far Away Place Name AB-C d1-23: 142 jumps, 31,245 ly, next stop Another Long System Name 45")
        label.grid(row=0, column=1, padx=(8, 0))
        root.update()
        event = types.SimpleNamespace(widget=frame, width=420)
        panelkit.on_frame_configure(event)
        root.update()
        label_left = label.winfo_rootx() - frame.winfo_rootx()
        self.assertLessEqual(label_left + label.winfo_reqwidth(), 420 + 1)


class RowRoomTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display")
        self.addCleanup(self.root.destroy)
        self.tk = tk

    def test_a_label_alone_in_its_row_has_no_row_limit(self):
        frame = self.tk.Frame(self.root)
        frame.pack()
        label = panelkit.wrap_label(frame, text="alone")
        label.grid(row=0, column=0)
        self.assertIsNone(panelkit.row_room(label, 400))

    def test_the_neighbors_width_is_taken_off_even_before_the_label_has_a_position(self):
        frame = self.tk.Frame(self.root)
        frame.pack()
        button = self.tk.Button(frame, text="PLOT")
        button.grid(row=0, column=0)
        label = panelkit.wrap_label(frame, text="beside")
        label.grid(row=0, column=1)                     # no update(): its own position is not known yet
        room = panelkit.row_room(label, 400)
        self.assertEqual(room, 400 - (button.winfo_reqwidth() + panelkit.ROW_GAP) - 6)

    def test_growth_is_logged_with_the_widest_widgets(self):
        frame = self.tk.Frame(self.root)
        frame.pack()
        self.tk.Label(frame, text="a very wide label indeed", width=60).pack()
        self.root.update()
        panelkit._widest_seen = 300
        panelkit._first_seen_at = 0.0                    # long ago: the panel has settled
        with self.assertLogs(panelkit.logger, level="WARNING") as captured:
            panelkit._note_growth(frame, 400)
        self.assertIn("widened from 300 to 400", captured.output[0])
        self.assertIn("a very wide label", captured.output[0])
        self.assertEqual(panelkit._widest_seen, 400)

    def test_growth_while_the_panel_is_still_being_built_is_not_logged(self):
        import time
        frame = self.tk.Frame(self.root)
        self.tk.Label(frame, text="x", width=60).pack()
        frame.pack()
        self.root.update()
        panelkit._widest_seen = 300
        panelkit._first_seen_at = time.monotonic()
        with self.assertNoLogs(panelkit.logger, level="WARNING"):
            panelkit._note_growth(frame, 500)

    def test_small_growth_is_not_logged(self):
        frame = self.tk.Frame(self.root)
        panelkit._widest_seen = 300
        panelkit._first_seen_at = 0.0
        with self.assertNoLogs(panelkit.logger, level="WARNING"):
            panelkit._note_growth(frame, 320)


if __name__ == "__main__":
    unittest.main()
