"""The commit-msg hook (.githooks/commit-msg): a message that breaks the project's rules is rejected, so it has to be changed before the commit is accepted.

The rules: no co-author or generated-with line; a subject of at most 72 characters that starts with a capital and does not end in a period; a blank line after it; body lines wrapped at 80 or fewer; no
echo of who asked for the change and no chatty asides. The hook is a POSIX shell script, so the test runs it with `sh` (Git for Windows ships one) and is skipped when none is found."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
HOOK = os.path.join(ROOT, ".githooks", "commit-msg")


def find_sh():
    found = shutil.which("sh")
    if found:
        return found
    git = shutil.which("git")
    if git:       # Git for Windows keeps its sh next to the git it installs
        for relative in (("..", "bin", "sh.exe"), ("..", "..", "bin", "sh.exe"), ("..", "..", "usr", "bin", "sh.exe")):
            candidate = os.path.normpath(os.path.join(os.path.dirname(git), *relative))
            if os.path.exists(candidate):
                return candidate
    return None


SH = find_sh()
GOOD_BODY = "Rebuild from the journals when the history says the commander scanned there."


@unittest.skipUnless(SH, "no POSIX shell to run the hook with")
class CommitMessageHookTests(unittest.TestCase):
    def run_hook(self, message):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8", newline="\n") as handle:
            handle.write(message if message.endswith("\n") else message + "\n")
            path = handle.name
        self.addCleanup(os.remove, path)
        result = subprocess.run([SH, HOOK, path], capture_output=True, text=True, encoding="utf-8")
        return result.returncode, result.stderr

    def accepted(self, message):
        code, errors = self.run_hook(message)
        self.assertEqual(code, 0, errors)

    def rejected(self, message, fragment):
        code, errors = self.run_hook(message)
        self.assertNotEqual(code, 0, "accepted: " + message[:60])
        self.assertIn(fragment, errors)

    def test_a_good_message_is_accepted(self):
        self.accepted("Rebuild surveys after a relog\n\n" + GOOD_BODY)
        self.accepted("Fix the survey rebuild")                                  # a subject alone is fine

    def test_a_subject_of_72_characters_is_the_most(self):
        self.accepted("A" * 72 + "\n\n" + GOOD_BODY)
        self.rejected("A" * 73 + "\n\n" + GOOD_BODY, "73 characters")

    def test_the_subject_must_start_with_a_capital_and_not_end_in_a_period(self):
        self.rejected("fix the thing", "capital letter")
        self.rejected("Fix the thing.", "period")
        self.accepted("1.0.1 release notes")

    def test_a_blank_line_separates_the_subject_from_the_body(self):
        self.rejected("Fix the thing\n" + GOOD_BODY, "blank line")

    def test_body_lines_are_wrapped_but_indented_lines_and_urls_may_run_long(self):
        self.accepted("Fix the thing\n\n" + "x" * 80)
        self.rejected("Fix the thing\n\n" + "x" * 81, "81 characters")
        self.accepted("Fix the thing\n\n    " + "x" * 120)
        self.accepted("Fix the thing\n\nSee https://example.org/" + "x" * 120)

    def test_non_ascii_characters_count_once(self):
        self.accepted("Show an arrow → in the list\n\n" + "→ " * 38)

    def test_who_asked_for_the_change_is_not_part_of_the_message(self):
        for phrase in ("as requested", "per your request", "you asked", "user asked", "per feedback", "as discussed"):
            self.rejected(f"Remove the card {phrase}", phrase)
            self.rejected("Remove the card\n\nDone " + phrase + " earlier.", phrase)

    def test_chatty_asides_and_exclamations_are_not(self):
        self.rejected("Fix the card\n\nOops, wrong file.", "oops")
        self.rejected("Fix the card!", "exclamation")

    def test_echo_phrases_match_whole_words_only(self):
        self.accepted("Fix the loops in the route list\n\nThe troops and loops views share one list.")
        self.rejected("Fix the card\n\nOops, wrong file.", "oops")
        self.rejected("Fix the oops card", "oops")

    def test_credit_lines_are_rejected(self):
        self.rejected("Fix it\n\nCo-Authored-By: Someone <someone@example.com>", "co-author")
        self.rejected("Fix it\n\nGenerated with a tool", "generated-with")

    def test_merge_revert_and_fixup_messages_are_left_alone(self):
        self.accepted("Merge pull request #2 from someone/" + "very-long-branch-name-" * 5)
        self.accepted("Revert \"" + "A very long original subject " * 4 + "\"")
        self.accepted("fixup! Fix the thing")

    def test_comment_lines_git_adds_are_ignored(self):
        self.accepted("Fix the thing\n\n" + GOOD_BODY + "\n# Please enter the commit message for your changes. Lines starting with '#' will be ignored, and an empty message aborts the commit.")

    def test_every_rule_reports_all_its_problems_at_once(self):
        code, errors = self.run_hook("fix the thing.\nbody right after, as requested!")
        self.assertNotEqual(code, 0)
        for fragment in ("capital letter", "period", "blank line", "as requested", "exclamation"):
            self.assertIn(fragment, errors)


if __name__ == "__main__":
    unittest.main()
