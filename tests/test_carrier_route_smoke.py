"""Opens the real Carrier Route window with EDMC stubbed and Spansh faked (tests/carrier_route_smoke.py). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class CarrierRouteSmokeTests(unittest.TestCase):
    def test_the_window_plots_follows_and_restores_a_carrier_route(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "carrier_route_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CARRIER ROUTE OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
