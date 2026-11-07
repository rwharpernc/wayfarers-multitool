"""
Opens the Ranks section of Operations with EDMC stubbed, and fails if the table does not follow the Rank, Progress and Promotion events, shows
one commander's ranks to another, or gets wide. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class RanksPanelSmokeTests(unittest.TestCase):
    def test_the_table_follows_the_events(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "ranks_panel_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RANKS PANEL OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
