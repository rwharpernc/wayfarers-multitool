"""Opens the real Route Planner with EDMC stubbed and Spansh faked (tests/route_planner_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class NeutronPlotterSmokeTests(unittest.TestCase):
    def test_the_plotter_plots_and_follows_the_route(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "route_planner_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ROUTE PLANNER OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
