"""
No co-author or "generated with" credit lines outside the Acknowledgements page.

Code comments, docs, changelog entries and commit messages carry no co-author line or "generated with" note; the one place
for acknowledgements is `docs/ATTRIBUTIONS.md`. This scans the working tree for the common phrasings, and checks the
commit-msg hook that stops them in commit messages is in the repo. It reads files directly, so it behaves the same on
Windows and Linux.
"""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {".git", "dist", "node_modules", "__pycache__"}
TEXT_EXTENSIONS = {".py", ".md", ".mjs", ".js", ".json", ".txt", ".toml", ".yml", ".yaml", ".cfg", ".ini"}
# Files that may carry such a line: the acknowledgements, and the files that enforce this rule.
ALLOWED = {
    os.path.join("docs", "ATTRIBUTIONS.md"),
    os.path.join("tests", "test_no_co_author_lines.py"), os.path.join("tests", "test_commit_msg_hook.py"), os.path.join(".githooks", "commit-msg"),
}
CREDIT = re.compile(r"co-authored-by:|generated (?:with|by) (?:an? )?(?:ai|assistant|tool)\b|🤖", re.IGNORECASE)


class NoCoAuthorLineTests(unittest.TestCase):
    def test_no_credit_lines_in_the_working_tree(self):
        found = []
        for folder, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in names:
                if os.path.splitext(name)[1].lower() not in TEXT_EXTENSIONS:
                    continue
                path = os.path.join(folder, name)
                rel = os.path.relpath(path, ROOT)
                if rel in ALLOWED:
                    continue
                with open(path, encoding="utf-8", errors="replace") as handle:
                    for number, line in enumerate(handle, 1):
                        if CREDIT.search(line):
                            found.append(f"{rel}:{number}")
        self.assertEqual(found, [], "credit line outside docs/ATTRIBUTIONS.md: " + ", ".join(found))

    def test_the_commit_message_hook_is_in_the_repo(self):
        hook = os.path.join(ROOT, ".githooks", "commit-msg")
        self.assertTrue(os.path.isfile(hook), "run `git config core.hooksPath .githooks` after adding .githooks/commit-msg")
        with open(hook, encoding="utf-8") as handle:
            self.assertIn("co-authored-by", handle.read().lower())


if __name__ == "__main__":
    unittest.main()
