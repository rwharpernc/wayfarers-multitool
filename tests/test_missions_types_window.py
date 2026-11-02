"""Opens the Mission types window with EDMC stubbed and fails if the list, the pages or the real panel drawing misbehave. Skipped when Tk has no display."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class MissionTypesWindowSmokeTests(unittest.TestCase):
    def test_the_window_lists_and_draws_the_types(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "missions_types_window_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MISSION TYPES OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
