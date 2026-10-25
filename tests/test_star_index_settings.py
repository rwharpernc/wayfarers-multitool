"""The text and buttons of the "Local star index" group (star_index_settings.py): what the status line says for each state, which buttons can be pressed, and that the page tells the user what is
downloaded, from where and how large. The functions are pure, so no window is needed; EDMC's own modules are replaced while the module is imported."""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

stand_ins = {"myNotebook": types.ModuleType("myNotebook"), "config": types.ModuleType("config")}
stand_ins["config"].config = mock.MagicMock()
with mock.patch.dict(sys.modules, stand_ins):
    from plugin import star_index_settings as S      # noqa: E402

from plugin import star_index as SI                 # noqa: E402
from plugin import star_index_job as J              # noqa: E402

OK = SI.IndexStatus("ok", "installed", count=5_053_184, size_bytes=112 * 1024 * 1024, built="2026-10-21T09:00:00Z", source_modified="Wed, 21 Oct 2026 06:26:22 GMT", etag='"x"')
IDLE = J.JobState()


class StatusTextTests(unittest.TestCase):
    def test_not_installed(self):
        text = S.status_text(SI.IndexStatus("missing", "not installed"), IDLE)
        self.assertIn("Not installed", text)
        self.assertIn("asks Spansh", text)

    def test_installed_gives_the_count_size_and_dates(self):
        text = S.status_text(OK, IDLE)
        self.assertIn("5,053,184 neutron stars", text)
        self.assertIn("112.0 MB", text)
        self.assertIn("built 2026-10-21", text)
        self.assertIn("Spansh's file of 2026-10-21", text)

    def test_a_damaged_index_says_it_is_ignored_and_what_to_do(self):
        text = S.status_text(SI.IndexStatus("damaged", "the index is incomplete (it ends early)"), IDLE)
        self.assertIn("cannot be used", text)
        self.assertIn("asks Spansh", text)
        self.assertIn("Delete it", text)

    def test_an_old_index_says_to_build_a_new_one(self):
        text = S.status_text(SI.IndexStatus("old", "the index is format 0; this WFMT reads format 1"), IDLE)
        self.assertIn("another version", text)
        self.assertIn("Download and build", text)

    def test_while_downloading_the_progress_is_shown(self):
        text = S.status_text(OK, J.JobState(J.DOWNLOADING, 0.25, "Downloading: 43.4 MB of 173.4 MB"))
        self.assertEqual(text, "Downloading: 43.4 MB of 173.4 MB (25%)")

    def test_while_building_the_step_is_shown(self):
        text = S.status_text(OK, J.JobState(J.BUILDING, 0.5, "Reading the dump: 2,000,000 neutron stars so far"))
        self.assertIn("Reading the dump", text)
        self.assertIn("50%", text)

    def test_how_the_last_job_ended_follows_the_status(self):
        text = S.status_text(SI.IndexStatus("missing", "not installed"), J.JobState(J.FAILED, 0.0, "Not enough free disk space: ..."))
        self.assertTrue(text.startswith("Not installed"))
        self.assertTrue(text.endswith("Not enough free disk space: ..."))
        cancelled = S.status_text(OK, J.JobState(J.CANCELLED, 0.0, "Cancelled. The index that was installed before is unchanged."))
        self.assertIn("Installed:", cancelled)
        self.assertIn("Cancelled.", cancelled)

    def test_dates_read_both_forms_and_leave_others_alone(self):
        self.assertEqual(S.date_text("2026-10-21T09:00:00Z"), "2026-10-21")
        self.assertEqual(S.date_text("Wed, 21 Oct 2026 06:26:22 GMT"), "2026-10-21")
        self.assertEqual(S.date_text("last week"), "last week")


class ButtonTests(unittest.TestCase):
    def test_nothing_installed_only_download_works(self):
        self.assertEqual(S.button_states(SI.IndexStatus("missing", ""), IDLE), {"download": True, "update": False, "cancel": False, "delete": False})

    def test_installed_update_and_delete_work(self):
        self.assertEqual(S.button_states(OK, IDLE), {"download": False, "update": True, "cancel": False, "delete": True})

    def test_a_damaged_index_can_be_replaced_or_deleted(self):
        self.assertEqual(S.button_states(SI.IndexStatus("damaged", "x"), IDLE), {"download": True, "update": False, "cancel": False, "delete": True})

    def test_while_a_job_runs_only_cancel_works(self):
        for state in (J.DOWNLOADING, J.BUILDING):
            self.assertEqual(S.button_states(OK, J.JobState(state, 0.1, "x")), {"download": False, "update": False, "cancel": True, "delete": False})


class DescriptionTests(unittest.TestCase):
    def test_it_says_what_where_how_large_and_that_nothing_is_automatic(self):
        text = S.DESCRIPTION
        for needed in ("downloads.spansh.co.uk", "173.4 MB", "110 MB", "Nothing is downloaded unless you press", "main star", "secondary star", "not part of Back up my data"):
            self.assertIn(needed, text)

    def test_the_settings_page_lists_the_download_among_the_button_only_lookups(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "plugin", "settings_online.py"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("Local star index", source)
        self.assertIn("build_group", source)


if __name__ == "__main__":
    unittest.main()
