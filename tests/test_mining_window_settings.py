"""Opens the Space Mining and Surface Mining windows with EDMC stubbed and fails if the Settings cards do not save, clamp, or stay in step with the Settings tab. Skipped when Tk has no display."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningWindowSettingsSmokeTests(unittest.TestCase):
    def test_the_cards_save_and_stay_in_step(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_window_settings_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING WINDOW SETTINGS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
