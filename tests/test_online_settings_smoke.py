"""
Builds the Online page of Settings with EDMC stubbed and fails if a lookup has no checkbox, Turn all off or Reset to defaults do not set the boxes, saving does not
write every switch, or a change hook runs when its switch did not change. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class OnlineSettingsSmokeTests(unittest.TestCase):
    def test_the_page_builds_and_its_controls_work(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "online_settings_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ONLINE SETTINGS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
