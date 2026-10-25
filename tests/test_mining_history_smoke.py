"""Opens the real Mining History window with EDMC stubbed (tests/mining_history_smoke.py) and fails if reading the journals, the tiles, the tables or the refresh misbehave.
Skipped when Tk has no display. Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningHistorySmokeTests(unittest.TestCase):
    def test_the_window_reads_the_journals_and_fills_every_tab(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_history_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING HISTORY OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
