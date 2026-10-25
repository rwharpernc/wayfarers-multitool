"""Opens the rebuilt hotspot, ship build, import and export, and market research dialogs with EDMC stubbed (tests/dialog_windows_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class DialogWindowsSmokeTests(unittest.TestCase):
    def test_the_rebuilt_dialogs_open_validate_and_save(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "dialog_windows_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DIALOG WINDOWS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
