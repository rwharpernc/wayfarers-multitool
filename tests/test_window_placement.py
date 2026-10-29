"""uikit/placement.py: a window opens where it was left when that is still on a monitor, otherwise on EDMC's monitor (or always there)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin.uikit import placement as P  # noqa: E402

LEFT = (0, 0, 1920, 1080)
RIGHT = (1920, 0, 2560, 1440)
BOTH = [LEFT, RIGHT]
EDMC_LEFT = (100, 100, 420, 700)         # EDMC's window on the left monitor
EDMC_RIGHT = (2000, 200, 420, 700)


class MonitorTests(unittest.TestCase):
    def test_the_monitor_a_window_mostly_sits_on(self):
        self.assertEqual(P.monitor_of(EDMC_RIGHT, BOTH), RIGHT)
        self.assertEqual(P.monitor_of(EDMC_LEFT, BOTH), LEFT)
        self.assertEqual(P.monitor_of((1800, 100, 400, 400), BOTH), RIGHT)       # 120 px on the left, 280 on the right

    def test_a_window_on_no_monitor_falls_back_to_the_first(self):
        self.assertEqual(P.monitor_of((9000, 9000, 100, 100), BOTH), LEFT)


class OnScreenTests(unittest.TestCase):
    def test_a_position_on_a_monitor(self):
        self.assertTrue(P.on_a_screen((300, 200), (800, 600), BOTH))
        self.assertTrue(P.on_a_screen((2500, 300), (800, 600), BOTH))

    def test_a_position_on_an_unplugged_monitor(self):
        self.assertFalse(P.on_a_screen((4800, 200), (800, 600), BOTH))
        self.assertFalse(P.on_a_screen((-2400, 200), (800, 600), BOTH))

    def test_a_window_with_only_a_sliver_showing_does_not_count(self):
        self.assertFalse(P.on_a_screen((1900, 200), (800, 600), [LEFT]))         # 20 px of it on the monitor


class PlaceTests(unittest.TestCase):
    def test_a_remembered_position_on_a_monitor_is_kept(self):
        self.assertEqual(P.place((800, 600), (2300, 300), EDMC_LEFT, BOTH), (2300, 300))

    def test_no_remembered_position_opens_over_edmc_on_its_monitor(self):
        x, y = P.place((800, 600), None, EDMC_LEFT, BOTH)
        self.assertEqual((x, y), (0, 150))                                      # centered on EDMC (310, 450), kept on the left monitor
        x, y = P.place((800, 600), None, EDMC_RIGHT, BOTH)
        self.assertTrue(RIGHT[0] <= x and x + 800 <= RIGHT[0] + RIGHT[2])

    def test_a_position_on_an_unplugged_monitor_opens_on_edmc_instead(self):
        x, y = P.place((800, 600), (4800, 200), EDMC_RIGHT, BOTH)
        self.assertTrue(RIGHT[0] <= x and x + 800 <= RIGHT[0] + RIGHT[2])

    def test_always_ignores_the_remembered_position(self):
        x, _y = P.place((800, 600), (2300, 300), EDMC_LEFT, BOTH, always_here=True)
        self.assertTrue(LEFT[0] <= x and x + 800 <= LEFT[0] + LEFT[2])

    def test_a_window_larger_than_the_monitor_sits_at_its_top_left(self):
        self.assertEqual(P.place((2500, 1300), None, EDMC_LEFT, BOTH), (0, 0))

    def test_no_monitors_known_changes_nothing(self):
        self.assertEqual(P.place((800, 600), (50, 60), EDMC_LEFT, []), (50, 60))
        self.assertEqual(P.place((800, 600), None, EDMC_LEFT, []), (100, 100))


class SettingTests(unittest.TestCase):
    def test_the_always_switch(self):
        P.set_always(True)
        self.assertTrue(P.always())
        P.set_always(False)
        self.assertFalse(P.always())


if __name__ == "__main__":
    unittest.main()
