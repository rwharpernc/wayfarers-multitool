"""No credit for an AI assistant in the repository except on the acknowledgements page: not in any other file, and not as a commit author or co-author (the commit-msg hook rejects co-author lines in messages).

The file scan reads the working tree directly, like test_line_endings.py, so it behaves the same on Windows, on Linux and in the Docker run. The acknowledgements page is the one place the project credits help, so it is skipped. So are the two
machine-local, untracked names (the assistant notes file and its folder), and the files that have to name them to keep them out of the repository.
"""
from __future__ import annotations

import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {".git", ".claude", "dist", "node_modules", "__pycache__"}
SKIP_FILES = {"CLAUDE.md", ".gitignore", os.path.join("docs", "ATTRIBUTIONS.md"), os.path.join("tests", "test_no_ai_credit.py")}
NAMES = ("claude", "anthropic")


def _files():
    for folder, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            path = os.path.join(folder, name)
            if os.path.relpath(path, ROOT) not in SKIP_FILES:
                yield path


class NoAiCreditTests(unittest.TestCase):
    def test_no_file_names_an_assistant(self):
        found = []
        for path in _files():
            try:
                with open(path, encoding="utf-8") as handle:
                    text = handle.read().lower()
            except (UnicodeDecodeError, OSError):
                continue                   # a binary file
            if any(word in text for word in NAMES):
                found.append(os.path.relpath(path, ROOT))
        self.assertEqual(found, [], "the project credits an AI assistant only in docs/ATTRIBUTIONS.md; take the mention out")

    def test_no_commit_has_an_assistant_as_author_or_co_author(self):
        try:
            log = subprocess.run(["git", "log", "--all", "--format=%an%n%ae%n%cn%n%ce%n%(trailers:key=Co-authored-by,valueonly)"], cwd=ROOT, capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("no usable Git history here (not a checkout, or Git refuses this folder)")
        self.assertFalse(any(word in log.stdout.decode("utf-8").lower() for word in NAMES))


if __name__ == "__main__":
    unittest.main()
