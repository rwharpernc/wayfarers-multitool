"""Draws the real Space Mining page with EDMC stubbed (tests/mining_page_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningPageSmokeTests(unittest.TestCase):
    def test_the_page_shows_the_rock_the_core_the_limpets_and_the_mission_needs(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_page_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING PAGE OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
