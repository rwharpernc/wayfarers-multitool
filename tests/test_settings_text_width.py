"""
Builds a Settings page in a real Tk window and fails if a description stays at its fixed width instead of using the page's, does not follow a resize, or a label that
shares its row is stretched. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class SettingsTextWidthTests(unittest.TestCase):
    def test_descriptions_use_the_whole_page(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "settings_text_width_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SETTINGS TEXT WIDTH OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
