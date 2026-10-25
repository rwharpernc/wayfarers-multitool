"""Opens the Mining History window from the Mining panel and redraws the panel (tests/mining_panel_window_smoke.py): the window must stay open. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningPanelWindowSmokeTests(unittest.TestCase):
    def test_the_history_window_survives_the_panel_redrawing(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_panel_window_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING PANEL WINDOW OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
