"""
Builds the Colony page of the main EDMC window (EDMC stubbed) and fails if its sections or the finished-sites list misbehave. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ColonizationPanelSmokeTests(unittest.TestCase):
    def test_the_page_shows_its_sections(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "colonization_panel_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("COLONIZATION PANEL OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
