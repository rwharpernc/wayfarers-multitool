"""Opens the real Space Mining Book with EDMC stubbed (tests/mining_ring_book_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningRingBookSmokeTests(unittest.TestCase):
    def test_the_book_lists_rings_and_keeps_notes(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_ring_book_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RING BOOK OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
