"""
Opens the pop-out windows the other window_fit tests do not cover (Space and Surface Mining Books, Mining History, the Mining live windows and search dialogs, Rare Goods, Route Planner, Carrier Route,
the Plan dialog, Watch list, Ship Builds, Inventory, Exobiology review, My Codex, the form dialogs, the screenshot preview, the themed message boxes and the Help windows) (EDMC stubbed, long data)
and fails if text is cut off, a control is pushed outside the window, a label cannot wrap or a table does not fit at the window's minimum size, 640 px wide and 1600 px wide. Skipped when Tk has no
display. The checker is in window_fit_check.py.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class WindowFitMoreTests(unittest.TestCase):
    def test_more_windows_fit_at_narrow_and_wide_sizes(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "window_fit_more_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=240)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WINDOW FIT MORE OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
