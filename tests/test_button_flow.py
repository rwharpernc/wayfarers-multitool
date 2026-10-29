"""panelkit.flow_positions: where a row of buttons wraps so it never passes the width EDMC's window is already held at."""
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"  # type: ignore[attr-defined]
    _stub.config = types.SimpleNamespace(get_str=lambda *_a, **_k: "")  # type: ignore[attr-defined]
    sys.modules["config"] = _stub

from plugin import panelkit  # noqa: E402


class FlowPositionsTests(unittest.TestCase):
    def test_a_row_that_fits_stays_on_one_line(self):
        self.assertEqual(panelkit.flow_positions([80, 80, 80], cap=300, gap=4), [(0, 0), (0, 1), (0, 2)])

    def test_the_button_that_would_pass_the_cap_starts_a_new_line(self):
        self.assertEqual(panelkit.flow_positions([100, 100, 100], cap=210, gap=4), [(0, 0), (0, 1), (1, 0)])

    def test_the_gap_counts_toward_the_cap(self):
        self.assertEqual(panelkit.flow_positions([100, 100], cap=203, gap=4), [(0, 0), (1, 0)])
        self.assertEqual(panelkit.flow_positions([100, 100], cap=204, gap=4), [(0, 0), (0, 1)])

    def test_a_button_wider_than_the_cap_sits_alone(self):
        self.assertEqual(panelkit.flow_positions([50, 400, 50], cap=200, gap=4), [(0, 0), (1, 0), (2, 0)])

    def test_no_cap_means_one_line(self):
        self.assertEqual(panelkit.flow_positions([500, 500], cap=0), [(0, 0), (0, 1)])

    def test_no_buttons(self):
        self.assertEqual(panelkit.flow_positions([], cap=100), [])


if __name__ == "__main__":
    unittest.main()
