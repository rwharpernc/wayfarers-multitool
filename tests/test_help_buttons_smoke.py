"""Opens real windows that keep their explanation behind a Help button (tests/help_buttons_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class HelpButtonsSmokeTests(unittest.TestCase):
    def test_help_opens_in_windows_that_had_a_paragraph(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "help_buttons_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("HELP BUTTONS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
