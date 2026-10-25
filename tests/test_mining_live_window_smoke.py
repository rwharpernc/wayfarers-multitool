"""Opens the real Mining live windows with EDMC stubbed (tests/mining_live_window_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningLiveWindowSmokeTests(unittest.TestCase):
    def test_the_live_windows_draw_and_mark(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_live_window_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("LIVE WINDOW OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
