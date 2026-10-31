"""
Opens the Engineers tab with EDMC stubbed and fails if the mouse wheel stops scrolling the page once the pointer has been over the engineer table (a scrolling
page of its own inside the tab). Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class EngineerScrollSmokeTests(unittest.TestCase):
    def test_the_wheel_scrolls_the_page_after_the_table(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "engineer_scroll_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ENGINEER SCROLL OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
