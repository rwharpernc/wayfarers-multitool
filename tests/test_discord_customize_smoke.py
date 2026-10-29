"""
Opens the Customize Discord posts dialog (EDMC stubbed) and fails if its preview, its templates (Save, Save as, Rename, Delete, choosing) or its report choice misbehave.
Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class DiscordCustomizeSmokeTests(unittest.TestCase):
    def test_the_dialog_builds_and_the_templates_work(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "discord_customize_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DISCORD CUSTOMIZE OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
