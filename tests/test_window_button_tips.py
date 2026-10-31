"""Every button on a WFMT window has a tooltip: each FlatButton, window action (add_action) and menu button (add_menu) in the plugin is
given a `tip`. Read from the source, because the windows need a display; a button added without one fails here with its file and line.
"""
from __future__ import annotations

import ast
import glob
import os
import unittest

PLUGIN = os.path.join(os.path.dirname(__file__), "..", "plugin")
BUILDERS = {"FlatButton", "MenuButton", "add_action", "add_menu"}


def untipped() -> list:
    found = []
    for path in sorted(glob.glob(os.path.join(PLUGIN, "**", "*.py"), recursive=True)):
        with open(path, encoding="utf-8") as handle:
            tree = ast.parse(handle.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if name in BUILDERS and not any(k.arg == "tip" for k in node.keywords):
                found.append(f"{os.path.relpath(path, PLUGIN)}:{node.lineno} {name}")
    return found


class WindowButtonTipTests(unittest.TestCase):
    def test_every_window_button_has_a_tip(self):
        self.assertEqual(untipped(), [], "buttons without a tip (add tip=\"Name - what it does\")")


if __name__ == "__main__":
    unittest.main()
