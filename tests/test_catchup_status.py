"""The panel line that says WFMT is catching up from the journals (catchup_status.py): silent unless a read runs long enough to notice."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import catchup_status as C  # noqa: E402


class CatchupStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        C._running.clear()
        self.addCleanup(C._running.clear)

    def test_nothing_running_says_nothing(self) -> None:
        self.assertEqual(C.text(), "")

    def test_a_quick_read_never_shows(self) -> None:
        C._running["Codex"] = 100.0
        self.assertEqual(C.text(now=100.0 + C.SHOW_AFTER_MS / 1000 - 0.1), "")

    def test_a_long_read_is_named(self) -> None:
        C._running["Codex"] = 100.0
        C._running["Powerplay"] = 100.0
        message = C.text(now=100.0 + C.SHOW_AFTER_MS / 1000 + 0.1)
        self.assertIn("Codex", message)
        self.assertIn("Powerplay", message)
        self.assertIn("once", message)

    def test_a_finished_read_goes_away(self) -> None:
        C._running["BGS"] = 100.0
        C.end("BGS")
        self.assertEqual(C.text(now=999.0), "")
        C.end("BGS")   # ending twice is harmless


if __name__ == "__main__":
    unittest.main()
