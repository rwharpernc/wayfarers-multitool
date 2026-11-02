"""Checks the shared name type-ahead (bodies, ships, comma lists) with EDMC stubbed and fails if a box suggests the wrong names. Skipped when Tk has no display."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class NameSuggestionsSmokeTests(unittest.TestCase):
    def test_the_boxes_suggest_the_right_names(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "name_suggestions_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("NAME SUGGESTIONS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
