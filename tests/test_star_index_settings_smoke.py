"""Builds the Local star index group on the Online lookups page in a real Tk window and runs the buttons against a fake server (tests/star_index_settings_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class StarIndexSettingsSmokeTests(unittest.TestCase):
    def test_the_group_builds_and_its_buttons_work(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "star_index_settings_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("STAR INDEX SETTINGS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
