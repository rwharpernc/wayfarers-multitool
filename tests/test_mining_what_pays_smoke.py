"""Opens the What pays window with Spansh replaced by a stand-in (tests/mining_what_pays_smoke.py): the table is ranked, a failure part way keeps what was found and an empty record
asks nothing. Skipped when Tk has no display. Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MiningWhatPaysSmokeTests(unittest.TestCase):
    def test_the_window_ranks_what_pays_and_survives_a_failure(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "mining_what_pays_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MINING WHAT PAYS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
