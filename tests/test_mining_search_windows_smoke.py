"""Opens the real Find Best Price, Check Ring Reserve Level and Find Nearby Hotspots windows with EDMC stubbed (tests/mining_search_windows_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningSearchWindowsSmokeTests(unittest.TestCase):
    def test_the_price_reserve_and_hotspot_windows_fill_their_tables(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_search_windows_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SEARCH WINDOWS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
