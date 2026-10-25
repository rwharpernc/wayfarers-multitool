"""Opens the real Exploration Dashboard with EDMC stubbed (tests/explore_dashboard_smoke.py) and fails if any tab, table or switch misbehaves. Skipped when Tk has no
display. Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ExploreDashboardSmokeTests(unittest.TestCase):
    def test_the_window_opens_and_follows_the_commander(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "explore_dashboard_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EXPLORE DASHBOARD OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
