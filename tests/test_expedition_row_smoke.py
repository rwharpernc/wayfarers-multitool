"""
Opens the Expedition section with the Expedition Log's figures and buttons in it and EDMC stubbed, and fails if the Log still has a section of its own, the lines say the same thing twice, the
buttons do not follow the run or the section widens the panel. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ExpeditionRowSmokeTests(unittest.TestCase):
    def test_one_section_holds_the_plan_and_the_log(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "expedition_row_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EXPEDITION ROW OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
