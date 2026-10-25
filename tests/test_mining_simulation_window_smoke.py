"""Opens the Surface Live window on the Mining simulation (tests/mining_simulation_window_smoke.py): the radar draws, CTR marks pretend ground and WFMT's own data is left alone.
Skipped when Tk has no display. Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningSimulationWindowSmokeTests(unittest.TestCase):
    def test_the_simulated_live_window_draws_and_leaves_real_data_alone(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_simulation_window_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING SIMULATION WINDOW OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
