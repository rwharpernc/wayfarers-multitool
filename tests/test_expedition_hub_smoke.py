"""
Opens the Expedition window with the Plan, Route and Log tabs built into it and EDMC stubbed, and fails if it opens more than one window, builds a tab before it is shown,
leaves a listener behind or saves a geometry for a tab. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ExpeditionHubSmokeTests(unittest.TestCase):
    def test_the_window_holds_the_three_tabs(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "expedition_hub_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EXPEDITION HUB OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
