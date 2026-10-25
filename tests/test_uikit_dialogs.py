"""The themed dialogs (plugin/uikit/dialogs.py): the test responder and its return values for each kind, and a headless smoke test that opens each dialog for real
(tests/uikit_dialogs_smoke.py, skipped when Tk has no display).
Run with: python -m unittest discover -s tests"""
from __future__ import annotations

import os
import subprocess
import sys
import tkinter
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from plugin.uikit import dialogs


class ResponderTests(unittest.TestCase):
    def tearDown(self) -> None:
        dialogs.set_test_responder(None)

    def test_every_call_goes_to_the_responder_with_its_kind_and_arguments(self) -> None:
        seen = []
        dialogs.set_test_responder(lambda kind, title, message, **kw: seen.append((kind, title, message, kw)))
        dialogs.confirm(None, "T1", "m1", yes="Go", no="Stop", default_yes=False)
        dialogs.choose(None, "T2", "m2", ("A", "B"), default=1, cancel_value="x")
        dialogs.prompt(None, "T3", "m3", initial="i", ok="Save")
        dialogs.info(None, "T4", "m4")
        dialogs.warning(None, "T5", "m5")
        dialogs.error(None, "T6", "m6")
        self.assertEqual([s[0] for s in seen], ["confirm", "choose", "prompt", "info", "warning", "error"])
        self.assertEqual(seen[0], ("confirm", "T1", "m1", {"yes": "Go", "no": "Stop", "default_yes": False}))
        self.assertEqual(seen[1][3], {"choices": ["A", "B"], "default": 1, "cancel_value": "x"})
        self.assertEqual(seen[2][3], {"initial": "i", "ok": "Save", "show": ""})
        self.assertEqual(seen[3][3], {})

    def test_return_values(self) -> None:
        dialogs.set_test_responder(dialogs.answers(confirm=True, choose="B", prompt="text", info=None, warning=None, error=None))
        self.assertIs(dialogs.confirm(None, "t", "m"), True)
        self.assertEqual(dialogs.choose(None, "t", "m", ["A", "B"]), "B")
        self.assertEqual(dialogs.prompt(None, "t", "m"), "text")
        self.assertIsNone(dialogs.info(None, "t", "m"))
        self.assertIsNone(dialogs.warning(None, "t", "m"))
        self.assertIsNone(dialogs.error(None, "t", "m"))
        dialogs.set_test_responder(dialogs.answers(confirm=lambda title, message: "Delete" in message, prompt=None, choose=None))
        self.assertIs(dialogs.confirm(None, "t", "Delete this?"), True)
        self.assertIs(dialogs.confirm(None, "t", "Keep this?"), False)
        self.assertIsNone(dialogs.prompt(None, "t", "m"))
        self.assertIsNone(dialogs.choose(None, "t", "m", ["A"]))

    def test_an_unanswered_kind_raises_instead_of_blocking(self) -> None:
        dialogs.set_test_responder(dialogs.answers(confirm=True))
        with self.assertRaises(dialogs.UnansweredDialog):
            dialogs.error(None, "Oops", "not expected")
        with self.assertRaises(dialogs.UnansweredDialog):
            dialogs.prompt(None, "t", "m")

    def test_clearing_the_responder_restores_the_real_windows(self) -> None:
        dialogs.set_test_responder(lambda *a, **k: True)
        self.assertIs(dialogs.confirm(None, "t", "m"), True)
        dialogs.set_test_responder(None)
        # With no Tk root there is nothing to open, so the real path returns its cancel value rather than raising.
        if getattr(tkinter, "_default_root", None) is None:
            self.assertIs(dialogs.confirm(None, "t", "m"), False)
            self.assertIsNone(dialogs.prompt(None, "t", "m"))
            self.assertEqual(dialogs.choose(None, "t", "m", ["A"], cancel_value="c"), "c")


class DialogSmokeTests(unittest.TestCase):
    def test_each_dialog_opens_and_behaves(self) -> None:
        script = os.path.join(os.path.dirname(__file__), "uikit_dialogs_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("UIKIT DIALOGS OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
