"""
Opens the Create Raven Colonial project dialog (EDMC stubbed) for a construction ship, an ordinary site and a locked system, and
fails if it does not appear. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ColonizationCreateDialogSmokeTests(unittest.TestCase):
    def test_the_dialog_appears_and_can_be_closed(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "colonization_create_dialog_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CREATE DIALOG OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
