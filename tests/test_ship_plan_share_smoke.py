"""
Builds the Ship planner tab with EDMC stubbed and fails if the Coriolis and EDSY link buttons do not copy or open a link that decodes back to the build, a pasted link is not
read, or a build too long for Coriolis is not refused. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ShipPlanShareSmokeTests(unittest.TestCase):
    def test_the_link_buttons_copy_and_open_the_selected_build(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "ship_plan_share_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SHIP SHARE OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
