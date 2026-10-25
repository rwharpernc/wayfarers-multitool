"""Downloading the dump and installing the index (star_index_download.py, star_index_job.py): progress, resume, conditional requests, the size cap, cancel, disk space, a folder that cannot be
written, and that one job runs at a time. A fake server stands in for Spansh and the dump is a small synthetic file; nothing touches the network."""
from __future__ import annotations

import errno
import os
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from plugin import spansh_courtesy as C            # noqa: E402
from plugin import star_index as SI                # noqa: E402
from plugin import star_index_download as D        # noqa: E402
from plugin import star_index_job as J             # noqa: E402
from fake_dump_server import FakeServer, busy      # noqa: E402
import star_index_fixtures as fx                    # noqa: E402

PLENTY = lambda directory: 10 ** 12                # noqa: E731
LATER = datetime(2027, 6, 1, tzinfo=timezone.utc)      # long after the fake dump's date, so an update downloads the full dump


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = os.path.join(self._tmp.name, "plugin", "star_index")
        SI.forget()
        self.addCleanup(SI.forget)
        self.stars = fx.make_stars(800)
        dump = os.path.join(self._tmp.name, "dump.json.gz")
        fx.write_dump(dump, self.stars, extras=100)
        with open(dump, "rb") as handle:
            self.body = handle.read()

    def courtesy(self, server):
        return C.Courtesy(opener=server, clock=lambda: 0.0, sleep=lambda seconds: None, jitter=lambda: 0.0)

    def job(self, server, free=PLENTY, now=LATER):
        return J.StarIndexJob(self.dir, courtesy=self.courtesy(server), free_space=free, run_inline=True, clock=lambda: now)

    def files(self):
        return sorted(os.listdir(self.dir)) if os.path.isdir(self.dir) else []


class DownloadTests(Base):
    def download(self, server, **kw):
        kw.setdefault("free_space", PLENTY)
        return D.download(self.dir, courtesy=self.courtesy(server), **kw)

    def test_a_download_is_a_plain_get_that_names_wfmt(self):
        server = FakeServer(self.body)
        seen = []
        result = self.download(server, progress=lambda done, total: seen.append((done, total)))
        sent = server.requests[0]
        self.assertIn("star-index", sent["user-agent"])
        self.assertTrue(sent["user-agent"].startswith("WFMT/"))
        self.assertEqual(sent["accept-encoding"], "identity")
        self.assertNotIn("range", sent)
        self.assertNotIn("if-none-match", sent)
        self.assertEqual(set(sent), {"user-agent", "accept-encoding"})         # nothing about the player
        self.assertEqual(open(result.path, "rb").read(), self.body)
        self.assertEqual((result.etag, result.size), ('"v1"', len(self.body)))
        self.assertEqual(seen[-1], (len(self.body), len(self.body)))
        self.assertEqual(self.files(), [D.DUMP_NAME])              # no part or record file left

    def test_the_url_is_spansh_s_download_server(self):
        self.assertEqual(D.DUMP_URL, "https://downloads.spansh.co.uk/systems_neutron.json.gz")
        self.assertGreater(D.MAX_DOWNLOAD_BYTES, D.EXPECTED_BYTES)
        self.assertLess(D.MAX_DOWNLOAD_BYTES, D.EXPECTED_BYTES * 1.25)

    def test_an_unchanged_file_is_not_downloaded_again(self):
        server = FakeServer(self.body)
        result = self.download(server, known_etag='"v1"', known_modified="Wed, 21 Oct 2026 06:26:22 GMT")
        self.assertTrue(result.not_modified)
        self.assertEqual(server.requests[0]["if-none-match"], '"v1"')
        self.assertEqual(server.requests[0]["if-modified-since"], "Wed, 21 Oct 2026 06:26:22 GMT")
        self.assertEqual(self.files(), [])

    def test_a_changed_file_is_downloaded(self):
        server = FakeServer(self.body, etag='"v2"')
        result = self.download(server, known_etag='"v1"')
        self.assertFalse(result.not_modified)
        self.assertEqual(result.etag, '"v2"')

    def test_a_partial_download_is_continued_with_a_range(self):
        server = FakeServer(self.body, script=[("drop", 5000)] * (C.MAX_RETRIES + 1))
        with self.assertRaises(D.DownloadError):
            self.download(server)
        part = os.path.join(self.dir, D.DUMP_NAME + D.PART_SUFFIX)
        self.assertTrue(os.path.isfile(part))
        held = os.path.getsize(part)
        self.assertGreater(held, 0)
        again = FakeServer(self.body)
        result = self.download(again)
        self.assertEqual(again.requests[0]["range"], f"bytes={held}-")
        self.assertEqual(again.requests[0]["if-range"], '"v1"')
        self.assertTrue(result.resumed)
        self.assertEqual(open(result.path, "rb").read(), self.body)
        self.assertEqual(self.files(), [D.DUMP_NAME])

    def test_cancel_keeps_the_part_and_the_next_press_resumes(self):
        cancel = threading.Event()

        def progress(done, total):
            if done >= 1000:
                cancel.set()

        server = FakeServer(self.body)
        with mock.patch.object(C, "STREAM_CHUNK", 1000), self.assertRaises(C.Cancelled):
            self.download(server, cancel=cancel, progress=progress)
        self.assertEqual(self.files(), sorted([D.DUMP_NAME + D.INFO_SUFFIX, D.DUMP_NAME + D.PART_SUFFIX]))
        again = FakeServer(self.body)
        result = self.download(again)
        self.assertTrue(result.resumed)
        self.assertEqual(open(result.path, "rb").read(), self.body)

    def test_a_part_that_is_already_complete_is_only_renamed(self):
        os.makedirs(self.dir)
        part = os.path.join(self.dir, D.DUMP_NAME + D.PART_SUFFIX)
        with open(part, "wb") as handle:
            handle.write(self.body)
        with open(part.replace(D.PART_SUFFIX, D.INFO_SUFFIX), "w", encoding="utf-8") as handle:
            handle.write('{"url": "%s", "etag": "\\"v1\\"", "total": %d}' % (D.DUMP_URL, len(self.body)))
        silent = FakeServer(self.body)
        result = self.download(silent)
        self.assertEqual(silent.requests, [])
        self.assertEqual(open(result.path, "rb").read(), self.body)
        self.assertEqual(self.files(), [D.DUMP_NAME])

    def test_a_server_that_ignores_range_sends_the_whole_file_again(self):
        first = FakeServer(self.body, script=[("drop", 3000)] * (C.MAX_RETRIES + 1), ranges=False)
        with self.assertRaises(D.DownloadError):
            self.download(first)
        second = FakeServer(self.body, ranges=False)
        result = self.download(second)
        self.assertFalse(result.resumed)
        self.assertEqual(open(result.path, "rb").read(), self.body)

    def test_a_part_the_server_cannot_continue_is_dropped_and_fetched_again(self):
        os.makedirs(self.dir)
        part = os.path.join(self.dir, D.DUMP_NAME + D.PART_SUFFIX)
        with open(part, "wb") as handle:
            handle.write(self.body + b"extra bytes past the end")
        with open(part.replace(D.PART_SUFFIX, D.INFO_SUFFIX), "w", encoding="utf-8") as handle:
            handle.write('{"url": "%s", "etag": "\\"v1\\""}' % D.DUMP_URL)
        server = FakeServer(self.body)
        result = self.download(server)
        self.assertEqual(open(result.path, "rb").read(), self.body)
        self.assertEqual([r.get("range") for r in server.requests], [f"bytes={len(self.body) + 24}-", None])

    def test_a_part_without_a_record_of_its_file_is_not_trusted(self):
        os.makedirs(self.dir)
        with open(os.path.join(self.dir, D.DUMP_NAME + D.PART_SUFFIX), "wb") as handle:
            handle.write(b"unknown origin")
        server = FakeServer(self.body)
        result = self.download(server)
        self.assertNotIn("range", server.requests[0])
        self.assertEqual(open(result.path, "rb").read(), self.body)

    def test_a_file_larger_than_the_cap_is_refused(self):
        server = FakeServer(self.body)
        with mock.patch.object(D, "MAX_DOWNLOAD_BYTES", len(self.body) - 1):
            with self.assertRaises(D.DownloadError) as caught:
                self.download(server)
        self.assertIn("larger", str(caught.exception))
        self.assertEqual(self.files(), [])

    def test_not_enough_disk_space_refuses_before_writing(self):
        server = FakeServer(self.body)
        with self.assertRaises(D.NotEnoughSpace) as caught:
            self.download(server, free_space=lambda directory: 50 * 1024 * 1024)
        self.assertIn("free disk space", str(caught.exception))
        self.assertEqual(self.files(), [])
        self.assertEqual(len(server.requests), 1)

    def test_space_needed_counts_the_download_and_the_build(self):
        need = len(self.body) + D.BUILD_SPACE_BYTES
        with self.assertRaises(D.NotEnoughSpace):
            self.download(FakeServer(self.body), free_space=lambda directory: need - 1)
        self.assertTrue(self.download(FakeServer(self.body), free_space=lambda directory: need).path)

    def test_free_bytes_looks_up_to_a_folder_that_exists(self):
        self.assertGreater(D.free_bytes(os.path.join(self._tmp.name, "a", "b", "c")), 0)

    def test_a_dropped_connection_that_never_recovers_reports_the_size(self):
        server = FakeServer(self.body, script=[("drop", 2000)] * (C.MAX_RETRIES + 1))
        with self.assertRaises(D.DownloadError) as caught:
            self.download(server)
        self.assertIn("continues", str(caught.exception))

    def test_a_server_error_is_reported_with_its_number(self):
        with self.assertRaises(D.DownloadError) as caught:
            self.download(FakeServer(self.body, script=[busy(503)] * (C.MAX_RETRIES + 1)))
        self.assertIn("503", str(caught.exception))

    def test_a_folder_that_cannot_be_written_gives_a_clear_message(self):
        with mock.patch("os.makedirs", side_effect=PermissionError(errno.EACCES, "Permission denied")):
            with self.assertRaises(D.DownloadError) as caught:
                self.download(FakeServer(self.body))
        self.assertIn("writable", str(caught.exception))
        self.assertIn(self.dir, str(caught.exception))

    def test_a_read_only_file_system_gives_the_same_message(self):
        message = D.local_problem(OSError(errno.EROFS, "Read-only file system"), "/x/y")
        self.assertIn("writable", message)
        self.assertEqual(D.local_problem(OSError(errno.ENOSPC, "full"), "/x/y"), "The disk is full.")

    def test_only_one_download_runs_at_a_time(self):
        gate = threading.Event()
        release = threading.Event()

        class Slow(FakeServer):
            def __call__(self, request, timeout=None):
                gate.set()
                release.wait(5)
                return super().__call__(request, timeout)

        outcome = []
        slow = Slow(self.body)
        thread = threading.Thread(target=lambda: outcome.append(self.download(slow)))
        thread.start()
        self.assertTrue(gate.wait(5))
        with self.assertRaises(D.DownloadError) as caught:
            self.download(FakeServer(self.body))
        self.assertIn("already running", str(caught.exception))
        release.set()
        thread.join(10)
        self.assertEqual(len(outcome), 1)


class JobTests(Base):
    def test_download_and_build_installs_the_index_and_removes_the_dump(self):
        server = FakeServer(self.body)
        job = self.job(server)
        self.assertTrue(job.start())
        state = job.snapshot()
        self.assertEqual(state.state, J.DONE, state.text)
        self.assertIn("800 neutron stars", state.text)
        status = SI.status(self.dir)
        self.assertEqual((status.state, status.count, status.etag), ("ok", 800, '"v1"'))
        self.assertEqual(self.files(), [SI.INDEX_FILENAME])
        hit = SI.StarIndex(SI.index_path(self.dir)).nearest(self.stars[3].x, self.stars[3].y, self.stars[3].z)[0]
        self.assertEqual(hit.id64, self.stars[3].id64)

    def test_update_sends_the_installed_etag_and_stops_on_not_modified(self):
        self.job(FakeServer(self.body)).start()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        server = FakeServer(self.body)
        job = self.job(server)
        job.start(update=True)
        self.assertEqual(server.requests[0]["if-none-match"], '"v1"')
        state = job.snapshot()
        self.assertEqual(state.state, J.DONE)
        self.assertIn("already up to date", state.text)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_update_to_a_newer_file_rebuilds(self):
        self.job(FakeServer(self.body)).start()
        fx.write_dump(os.path.join(self._tmp.name, "newer.json.gz"), fx.make_stars(1000, seed=3))
        with open(os.path.join(self._tmp.name, "newer.json.gz"), "rb") as handle:
            newer = handle.read()
        job = self.job(FakeServer(newer, etag='"v2"'))
        job.start(update=True)
        self.assertEqual(job.snapshot().state, J.DONE)
        self.assertEqual((SI.status(self.dir).count, SI.status(self.dir).etag), (1000, '"v2"'))

    def test_download_and_build_does_not_send_a_conditional_request(self):
        server = FakeServer(self.body)
        self.job(server).start(update=False)
        self.assertNotIn("if-none-match", server.requests[0])

    def test_not_enough_space_fails_cleanly_and_keeps_the_old_index(self):
        self.job(FakeServer(self.body)).start()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        job = self.job(FakeServer(self.body, etag='"v2"'), free=lambda directory: 10 * 1024 * 1024)
        job.start(update=True)
        state = job.snapshot()
        self.assertEqual(state.state, J.FAILED)
        self.assertIn("free disk space", state.text)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_a_dump_that_cannot_be_built_fails_cleanly_and_keeps_the_old_index(self):
        self.job(FakeServer(self.body)).start()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        job = self.job(FakeServer(b"this is not a gzip file" * 50, etag='"v2"'))
        job.start(update=True)
        state = job.snapshot()
        self.assertEqual(state.state, J.FAILED)
        self.assertIn("could not be built", state.text)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertEqual(self.files(), [SI.INDEX_FILENAME])        # the bad download is gone too

    def test_cancel_while_downloading(self):
        job = self.job(FakeServer(self.body))
        original = D.download

        def cancelling(directory, etag, modified, cancel, progress, courtesy, free):
            cancel.set()
            return original(directory, etag, modified, cancel, progress, courtesy, free)

        with mock.patch.object(J.star_index_download, "download", cancelling):
            job.start()
        self.assertEqual(job.snapshot().state, J.CANCELLED)
        self.assertEqual(SI.status(self.dir).state, "missing")

    def test_cancel_while_building_discards_the_dump_and_keeps_the_old_index(self):
        self.job(FakeServer(self.body)).start()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        job = self.job(FakeServer(self.body, etag='"v2"'))

        def building(fraction, text):
            job.cancel()

        real = J.star_index_build.build

        def build(source, directory, info, cancel, progress):
            return real(source, directory, info, cancel, lambda fraction, text: (progress(fraction, text), job.cancel()))

        with mock.patch.object(J.star_index_build, "build", build):
            job.start(update=True)
        self.assertEqual(job.snapshot().state, J.CANCELLED)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertEqual(self.files(), [SI.INDEX_FILENAME])

    def test_a_job_does_not_start_while_another_runs(self):
        job = J.StarIndexJob(self.dir, courtesy=self.courtesy(FakeServer(self.body)), free_space=PLENTY, run_inline=True)
        job._state = J.JobState(J.DOWNLOADING, 0.5, "x")
        self.assertFalse(job.start())

    def test_the_job_runs_on_a_worker_thread_by_default(self):
        release = threading.Event()
        entered = threading.Event()

        class Slow(FakeServer):
            def __call__(self, request, timeout=None):
                entered.set()
                release.wait(5)
                return super().__call__(request, timeout)

        job = J.StarIndexJob(self.dir, courtesy=self.courtesy(Slow(self.body)), free_space=PLENTY)
        self.assertTrue(job.start())                       # returns at once
        self.assertTrue(entered.wait(5))
        self.assertTrue(job.snapshot().active)
        self.assertFalse(job.start())
        release.set()
        job._thread.join(10)
        self.assertEqual(job.snapshot().state, J.DONE)

    def test_an_unexpected_error_is_reported_not_raised(self):
        job = self.job(FakeServer(self.body))
        with mock.patch.object(J.star_index_build, "build", side_effect=RuntimeError("odd")):
            job.start()
        self.assertEqual(job.snapshot().state, J.FAILED)
        self.assertIn("odd", job.snapshot().text)

    def test_a_folder_that_cannot_be_written_is_reported(self):
        job = self.job(FakeServer(self.body))
        with mock.patch("os.makedirs", side_effect=PermissionError(errno.EACCES, "denied")):
            job.start()
        self.assertEqual(job.snapshot().state, J.FAILED)
        self.assertIn("writable", job.snapshot().text)

    def test_delete_removes_the_index_and_any_download(self):
        self.job(FakeServer(self.body)).start()
        with open(os.path.join(self.dir, D.DUMP_NAME + D.PART_SUFFIX), "wb") as handle:
            handle.write(b"x")
        job = self.job(FakeServer(self.body))
        self.assertIn("deleted", job.delete_index())
        self.assertEqual(self.files(), [])
        self.assertEqual(SI.status(self.dir).state, "missing")

    def test_delete_is_refused_while_a_job_runs(self):
        job = self.job(FakeServer(self.body))
        job._state = J.JobState(J.BUILDING, 0.1, "x")
        self.assertIn("Cancel", job.delete_index())


if __name__ == "__main__":
    unittest.main()
