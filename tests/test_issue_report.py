"""
Unit tests for plugin/issue_report.py: the prefilled GitHub issue address.

Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import __version__  # noqa: E402
from plugin import issue_report  # noqa: E402

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", ".github", "ISSUE_TEMPLATE", "bug_report.yml")


class BuildUrlTests(unittest.TestCase):
    def test_points_at_the_new_issue_form_with_the_template(self) -> None:
        url = issue_report.build_url("- OS: test")
        parts = urlparse(url)
        self.assertEqual(f"{parts.scheme}://{parts.netloc}{parts.path}", issue_report.NEW_ISSUE_URL)
        query = parse_qs(parts.query)
        self.assertEqual(["bug_report.yml"], query["template"])
        self.assertEqual(["bug"], query["labels"])
        self.assertEqual(["- OS: test"], query["environment"])
        self.assertIn(__version__, query["title"][0])

    def test_environment_names_the_versions_and_os_and_nothing_personal(self) -> None:
        text = issue_report.environment_text(edmc="5.13.0", system="TestOS 1")
        self.assertIn(f"WFMT: {__version__}", text)
        self.assertIn("EDMC: 5.13.0", text)
        self.assertIn("Python: ", text)
        self.assertIn("OS: TestOS 1", text)
        self.assertEqual(4, len(text.splitlines()))

    def test_default_url_is_short(self) -> None:
        self.assertLess(len(issue_report.build_url()), issue_report.MAX_URL_LENGTH)

    def test_oversized_prefill_falls_back_to_the_plain_form(self) -> None:
        url = issue_report.build_url("x" * 5000)
        self.assertNotIn("environment", url)
        self.assertIn("template=bug_report.yml", url)

    def test_open_report_opens_the_built_address(self) -> None:
        with mock.patch.object(issue_report.webbrowser, "open") as opened:
            issue_report.open_report()
        opened.assert_called_once()
        self.assertTrue(opened.call_args[0][0].startswith(issue_report.NEW_ISSUE_URL))


LOG = r"""2026-10-14 14:56:50.352 UTC - INFO - 1:2:3 <plugins>.WFMT.inventory_panel.Panel.run:808: Docked as Silas Kade in C:\Users\bob\x
2026-10-14 14:56:51.000 UTC - INFO - 1:2:3 <plugins>.OtherPlugin.mod.f:1: not ours
2026-10-14 14:56:52.000 UTC - ERROR - 1:2:3 <plugins>.WFMT.load.journal_entry:9: failed
Traceback (most recent call last):
  File "x.py", line 1, in f
ValueError: boom
"""


class DiagnosticsTests(unittest.TestCase):
    def test_keeps_only_wfmt_records_with_their_tracebacks(self) -> None:
        lines = issue_report.wfmt_log_lines(LOG, "WFMT")
        self.assertEqual(5, len(lines))
        self.assertFalse(any("OtherPlugin" in line for line in lines))
        self.assertIn("ValueError: boom", lines[-1])

    def test_keeps_only_the_newest_lines(self) -> None:
        lines = issue_report.wfmt_log_lines(LOG, "WFMT", limit=2)
        self.assertEqual(2, len(lines))
        self.assertIn("ValueError: boom", lines[-1])

    def test_redacts_commander_in_any_case_and_the_home_folder(self) -> None:
        text = issue_report.redact(r"Silas Kade / SILAS KADE in C:\Users\bob\x and C:/Users/bob/y",
                                   ["silas kade"], home=r"C:\Users\bob")
        self.assertNotIn("ilas", text)
        self.assertNotIn("bob", text)
        self.assertEqual(r"<commander> / <commander> in ~\x and ~/y", text)

    def test_a_discord_webhook_link_is_redacted(self) -> None:
        link = "https://discord.com/api/webhooks/1234567890/abcDEF-_secret"
        text = issue_report.redact(f"posted to {link}?wait=true failed; also https://discordapp.com/api/v10/webhooks/5/tok", [], home="~")
        self.assertEqual("posted to <webhook> failed; also <webhook>", text)
        self.assertNotIn("secret", text)

    def test_blank_names_redact_nothing(self) -> None:
        self.assertEqual("abc", issue_report.redact("abc", ["", "  "], home="~"))

    def test_spansh_line_counts_this_sessions_requests(self) -> None:
        line = issue_report.spansh_line()
        self.assertTrue(line.startswith("Spansh requests this session: "), line)
        self.assertIn("retried", line)

    def test_diagnostics_text_has_environment_and_redacted_log(self) -> None:
        with mock.patch.object(issue_report, "_plugin_dir", "WFMT"):
            text = issue_report.diagnostics_text(LOG, ["Silas Kade"], home=r"C:\Users\bob")
        self.assertIn(f"WFMT: {__version__}", text)
        self.assertIn("<commander>", text)
        self.assertNotIn("Silas", text)
        self.assertNotIn("OtherPlugin", text)

    def test_no_wfmt_lines_says_so(self) -> None:
        self.assertIn("no WFMT lines", issue_report.diagnostics_text("nothing here\n"))

    def test_read_log_tail_of_a_missing_file_is_empty(self) -> None:
        self.assertEqual("", issue_report.read_log_tail(os.path.join(os.path.dirname(__file__), "nope.log")))

    def test_copy_diagnostics_hands_text_to_the_clipboard(self) -> None:
        with mock.patch.object(issue_report, "log_path", return_value=""), \
                mock.patch.object(issue_report, "commander_names", return_value=[]):
            widget = mock.MagicMock()
            self.assertTrue(issue_report.copy_diagnostics(widget))
        self.assertIn(f"WFMT: {__version__}", widget.clipboard_append.call_args[0][0])


class TemplateTests(unittest.TestCase):
    def test_template_has_the_prefilled_field_id(self) -> None:
        with open(TEMPLATE_PATH, encoding="utf-8") as handle:
            self.assertIn(f"id: {issue_report.ENVIRONMENT_FIELD}", handle.read())


FEEDBACK_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", ".github", "ISSUE_TEMPLATE", issue_report.FEEDBACK_TEMPLATE)


class FeedbackReportTests(unittest.TestCase):
    def test_the_address_names_the_form_the_area_the_subject_and_the_context(self) -> None:
        url = issue_report.build_feedback_url("Engineers", "Marco Qwent", "Standing in WFMT: Known", "- OS: test")
        parts = urlparse(url)
        self.assertEqual(f"{parts.scheme}://{parts.netloc}{parts.path}", issue_report.NEW_ISSUE_URL)
        query = parse_qs(parts.query)
        self.assertEqual(["game_data.yml"], query["template"])
        self.assertEqual(["Engineers"], query["area"])
        self.assertEqual(["Marco Qwent"], query["subject"])
        self.assertEqual(["Standing in WFMT: Known"], query["context"])
        self.assertEqual(["- OS: test"], query["environment"])
        self.assertIn("Game data: Engineers - Marco Qwent", query["title"][0])
        self.assertIn(__version__, query["title"][0])

    def test_with_nothing_given_the_form_opens_blank_apart_from_the_environment(self) -> None:
        url = issue_report.build_feedback_url()
        query = parse_qs(urlparse(url).query)
        self.assertNotIn("area", query)
        self.assertNotIn("subject", query)
        self.assertIn("environment", query)
        self.assertLess(len(url), issue_report.MAX_URL_LENGTH)

    def test_a_huge_input_still_gives_a_working_address(self) -> None:
        url = issue_report.build_feedback_url("x" * 5000, "y" * 5000, environment="- OS: " + "z" * 3000)
        self.assertLessEqual(len(url), issue_report.MAX_URL_LENGTH)
        self.assertEqual(["game_data.yml"], parse_qs(urlparse(url).query)["template"])

    def test_the_form_has_the_prefilled_field_ids(self) -> None:
        with open(FEEDBACK_TEMPLATE_PATH, encoding="utf-8") as handle:
            text = handle.read()
        for field in (issue_report.AREA_FIELD, issue_report.SUBJECT_FIELD, issue_report.CONTEXT_FIELD, issue_report.ENVIRONMENT_FIELD):
            self.assertIn(f"id: {field}", text)

    def test_open_feedback_opens_the_built_address(self) -> None:
        with mock.patch.object(issue_report.webbrowser, "open") as opened:
            issue_report.open_feedback("Engineers", "Marco Qwent")
        self.assertIn("template=game_data.yml", opened.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
