"""Checks that a settings box saves on Return or leaving only when its text changed. Skipped when Tk has no display."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


class CommitEntrySmokeTests(unittest.TestCase):
    def test_a_box_saves_only_when_its_text_changed(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "commit_entry_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("COMMIT ENTRY OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
