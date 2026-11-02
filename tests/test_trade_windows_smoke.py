"""
Opens the Trade panel and its Session, Routes and Market windows with EDMC stubbed, and fails if a button does not open its window,
the windows do not follow the controller, or the panel gets wide. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class TradeWindowsSmokeTests(unittest.TestCase):
    def test_the_buttons_open_the_windows(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "trade_windows_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TRADE WINDOWS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
