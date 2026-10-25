"""Opens the real Rare Goods Finder with EDMC stubbed (tests/rare_goods_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class RareGoodsSmokeTests(unittest.TestCase):
    def test_the_finder_shows_a_distance_for_each_origin_system(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "rare_goods_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RARE GOODS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
