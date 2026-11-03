"""
Opens the Combat Record panel section and window with EDMC stubbed, and fails if the panel's lines, the window's tabs or a rebuild from the journals
misbehave. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class CombatWindowSmokeTests(unittest.TestCase):
    def test_the_panel_and_the_window_work(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "combat_window_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("COMBAT OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
