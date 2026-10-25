"""WFMT uses its own themed dialogs (plugin/uikit/dialogs.py), never the operating system's `tkinter.messagebox` / `tkinter.simpledialog`, which ignore the
look of the windows and differ between Windows and Linux. This fails if any module under plugin/ imports either one.
Run with: python -m unittest discover -s tests"""
from __future__ import annotations

import ast
import os
import unittest

PLUGIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugin"))
NATIVE = {"messagebox", "simpledialog"}


def _native_imports(tree: ast.AST) -> list:
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[:2] in (["tkinter", "messagebox"], ["tkinter", "simpledialog"]) for alias in node.names):
                lines.append(node.lineno)
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")
            if module[:2] in (["tkinter", "messagebox"], ["tkinter", "simpledialog"]):
                lines.append(node.lineno)
            elif module == ["tkinter"] and any(alias.name in NATIVE for alias in node.names):
                lines.append(node.lineno)
    return lines


class NoNativeDialogsTests(unittest.TestCase):
    def test_no_module_imports_the_native_dialogs(self) -> None:
        found = []
        for folder, dirs, names in os.walk(PLUGIN):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in names:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(folder, name)
                with open(path, encoding="utf-8") as handle:
                    tree = ast.parse(handle.read(), path)
                found += [f"{os.path.relpath(path, PLUGIN)}:{line}" for line in _native_imports(tree)]
        self.assertEqual(found, [], "use plugin/uikit/dialogs.py instead of tkinter.messagebox / simpledialog")

    def test_the_check_recognizes_each_import_form(self) -> None:
        for source in ("import tkinter.messagebox", "import tkinter.messagebox as m", "from tkinter import messagebox",
                       "from tkinter import filedialog, simpledialog", "from tkinter.messagebox import askyesno",
                       "from tkinter.simpledialog import askstring"):
            self.assertTrue(_native_imports(ast.parse(source)), source)
        self.assertFalse(_native_imports(ast.parse("from tkinter import filedialog, ttk")))


if __name__ == "__main__":
    unittest.main()
