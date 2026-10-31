"""The window kit's tooltips really appear when a button is hovered (tests/uikit_tooltip_smoke.py, skipped when Tk has no display).
Run with: python -m unittest discover -s tests"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest


class UikitTooltipSmokeTests(unittest.TestCase):
    def test_hovering_a_button_shows_its_tooltip(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "uikit_tooltip_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("UIKIT TOOLTIPS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
