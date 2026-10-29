"""The documentation matches the code: scripts/check_docs.py finds nothing stale.

Each check is its own test so a failure names what drifted. To fix a failure, correct the doc (or the comment). Only a name that
legitimately belongs to something other than WFMT goes in docs/doc_terms.txt.
"""
import importlib.util
import os
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("check_docs", os.path.join(_ROOT, "scripts", "check_docs.py"))
check_docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_docs)


class DocsCurrentTest(unittest.TestCase):
    def _run(self, name):
        problems = check_docs.CHECKS[name]()
        self.assertEqual(problems, [], f"{name}: the docs no longer match the code (see docs/DEVELOPMENT.md, Keeping the docs current)\n" + "\n".join(problems))

    def test_links_resolve(self):
        self._run("links")

    def test_screen_labels_exist_in_the_code(self):
        self._run("labels")

    def test_settings_paths_start_with_a_real_tab(self):
        self._run("paths")

    def test_named_files_and_settings_exist(self):
        self._run("files")

    def test_code_comments_name_real_things(self):
        self._run("comments")

    def test_version_is_the_same_everywhere(self):
        self._run("version")


if __name__ == "__main__":
    unittest.main()
