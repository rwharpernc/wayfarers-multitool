"""Builds the Shortcuts Settings page in a real Tk window and saves a change (tests/shortcuts_settings_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ShortcutsSettingsSmokeTests(unittest.TestCase):
    def test_the_page_builds_flags_clashes_and_saves(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "shortcuts_settings_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SHORTCUTS SETTINGS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
