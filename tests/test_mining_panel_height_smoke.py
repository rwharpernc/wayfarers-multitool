"""Checks the Mining panel's Surface page fits its height cap with a Rhino out (tests/mining_panel_height_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningPanelHeightSmokeTests(unittest.TestCase):
    def test_the_buttons_show_without_scrolling_on_the_surface_page(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_panel_height_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING PANEL HEIGHT OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
