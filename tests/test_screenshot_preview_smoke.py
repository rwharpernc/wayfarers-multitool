"""
Opens the screenshot preview window with EDMC stubbed, and fails if a very wide or tall image is not scaled into a bounded box inside
the screen, or the window does not re-fit, close or save its place. Skipped when Tk has no display.
Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class ScreenshotPreviewSmokeTests(unittest.TestCase):
    def test_the_preview_window_is_bounded_and_closes(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "screenshot_preview_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PREVIEW OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
