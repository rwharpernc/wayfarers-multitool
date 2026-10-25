"""A Location inside a planetary ring sets the current ring (tests/mining_panel_location_smoke.py). Skipped when Tk is unavailable.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningPanelLocationTests(unittest.TestCase):
    def test_a_location_in_a_ring_sets_the_ring(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_panel_location_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk is unavailable here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING PANEL LOCATION OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
