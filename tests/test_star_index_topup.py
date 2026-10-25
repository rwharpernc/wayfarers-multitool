"""Bringing the local star index up to date from Spansh's small update files (star_index_build.build with `topup_from`, star_index.StarIndex.records, star_index_download.choose_update and
the job's top-up with its fall back to the full dump). A fake server stands in for Spansh and the files are small synthetic ones; nothing touches the network."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from plugin import spansh_courtesy as C            # noqa: E402
from plugin import star_index as SI                # noqa: E402
from plugin import star_index_build as B           # noqa: E402
from plugin import star_index_download as D        # noqa: E402
from plugin import star_index_job as J             # noqa: E402
from fake_dump_server import FakeServer            # noqa: E402
import star_index_fixtures as fx                    # noqa: E402

PLENTY = lambda directory: 10 ** 12                # noqa: E731
FULL_MODIFIED = "Wed, 21 Oct 2026 06:26:22 GMT"
NEXT_MODIFIED = "Thu, 22 Oct 2026 06:26:22 GMT"
CURRENT_TO = "2026-10-21T06:26:22Z"
NOW = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)


def units(value: float) -> int:
    return round(value * 32)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = os.path.join(self._tmp.name, "star_index")
        SI.forget()
        self.addCleanup(SI.forget)
        self.stars = fx.make_stars(600)

    def path(self, name):
        return os.path.join(self._tmp.name, name)

    def build_full(self, stars=None, **info):
        dump = self.path("full.json.gz")
        fx.write_dump(dump, stars if stars is not None else self.stars, extras=60)
        source = {"url": D.DUMP_URL, "etag": '"v1"', "last_modified": FULL_MODIFIED, "full_etag": '"v1"', "full_modified": FULL_MODIFIED, "topups": 0}
        source.update(info)
        return B.build(dump, self.dir, source)

    def changes(self):
        """A day's changes: five stars moved, five renamed, five gone (now black holes), thirty new."""
        moved = [s._replace(x=s.x + 1.5, y=s.y - 2.25) for s in self.stars[10:15]]
        renamed = [s._replace(name=f"Renamed Sector AB-C d{i}-{i}") for i, s in enumerate(self.stars[20:25])]
        gone = self.stars[30:35]
        new = fx.make_stars(30, seed=77)
        return moved, renamed, gone, new

    def expected(self):
        moved, renamed, gone, new = self.changes()
        by_id = {s.id64: s for s in self.stars}
        for star in moved + renamed:
            by_id[star.id64] = star
        for star in gone:
            del by_id[star.id64]
        for star in new:
            by_id[star.id64] = star
        return by_id

    def write_update(self, name="day.json.gz", **kw):
        moved, renamed, gone, new = self.changes()
        path = self.path(name)
        fx.write_update(path, neutron=moved + renamed + new, no_longer_neutron=gone, others=40, **kw)
        return path

    def index_records(self):
        return {id64: (name, x, y, z) for id64, name, x, y, z in SI.StarIndex(SI.index_path(self.dir)).records()}


class RecordTests(Base):
    def test_records_returns_every_star_with_its_name_and_position(self):
        self.build_full()
        found = self.index_records()
        self.assertEqual(len(found), len(self.stars))
        for star in self.stars:
            name, x, y, z = found[star.id64]
            self.assertEqual((name, x, y, z), (star.name, units(star.x), units(star.y), units(star.z)))

    def test_records_matches_the_header_count_with_many_odd_names(self):
        stars = fx.make_stars(2000, seed=4, odd_every=3)
        self.build_full(stars)
        self.assertEqual(len(self.index_records()), 2000)

    def test_records_agrees_with_the_query_names(self):
        self.build_full()
        index = SI.StarIndex(SI.index_path(self.dir))
        star = self.stars[7]
        hit = index.nearest(star.x, star.y, star.z)[0]
        self.assertEqual(self.index_records()[hit.id64][0], hit.name)


class MergeTests(Base):
    def test_a_topup_applies_new_moved_renamed_and_removed_stars(self):
        self.build_full()
        before = SI.status(self.dir)
        result = B.build(self.write_update(), self.dir, {"last_modified": NEXT_MODIFIED}, topup_from=CURRENT_TO)
        want = self.expected()
        self.assertEqual(result.count, len(want))
        self.assertEqual(SI.status(self.dir).count, len(want))
        self.assertEqual(result.added, 5 + 5 + 30)
        self.assertEqual(result.changed, 5 + 5 + 5 + 30 + 40 + 1)
        found = self.index_records()
        self.assertEqual(set(found), set(want))
        for id64, star in want.items():
            self.assertEqual(found[id64], (star.name, units(star.x), units(star.y), units(star.z)))
        self.assertNotEqual(SI.status(self.dir).count, before.count)

    def test_queries_after_a_topup_match_a_brute_force_search(self):
        self.build_full()
        B.build(self.write_update(), self.dir, {}, topup_from=CURRENT_TO)
        stars = list(self.expected().values())
        index = SI.StarIndex(SI.index_path(self.dir))
        for probe in stars[::37]:
            hits = index.nearest(probe.x + 0.5, probe.y, probe.z, count=3)
            self.assertEqual([h.id64 for h in hits], [id64 for _d, id64 in fx.brute_nearest(stars, probe.x + 0.5, probe.y, probe.z, 3)])

    def test_a_removed_star_is_no_longer_found(self):
        self.build_full()
        B.build(self.write_update(), self.dir, {}, topup_from=CURRENT_TO)
        gone = self.stars[30]
        hits = SI.StarIndex(SI.index_path(self.dir)).nearest(gone.x, gone.y, gone.z, count=5)
        self.assertNotIn(gone.id64, [h.id64 for h in hits])

    def test_two_topups_in_a_row_still_agree_with_the_data(self):
        self.build_full()
        B.build(self.write_update(), self.dir, {}, topup_from=CURRENT_TO)
        again = fx.make_stars(10, seed=91)
        fx.write_update(self.path("day2.json.gz"), neutron=again)
        B.build(self.path("day2.json.gz"), self.dir, {}, topup_from=CURRENT_TO)
        want = self.expected()
        for star in again:
            want[star.id64] = star
        self.assertEqual(set(self.index_records()), set(want))

    def test_the_header_keeps_the_source_information(self):
        self.build_full()
        info = {"url": D.DAY_URL, "last_modified": NEXT_MODIFIED, "full_modified": FULL_MODIFIED, "topups": 1}
        B.build(self.write_update(), self.dir, info, topup_from=CURRENT_TO)
        status = SI.status(self.dir)
        self.assertEqual((status.source_modified, status.full_modified, status.topups), (NEXT_MODIFIED, FULL_MODIFIED, 1))

    def test_a_file_that_starts_after_the_index_date_is_refused_and_nothing_changes(self):
        self.build_full()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        late = self.write_update(oldest="2026-10-21T08:00:00Z")
        with self.assertRaises(B.TopupGap):
            B.build(late, self.dir, {}, topup_from=CURRENT_TO)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertEqual(sorted(os.listdir(self.dir)), [SI.INDEX_FILENAME])

    def test_a_file_with_no_systems_is_refused(self):
        self.build_full()
        empty = self.path("empty.json.gz")
        fx._write_rows(empty, [])
        with self.assertRaises(B.BuildError):
            B.build(empty, self.dir, {}, topup_from=CURRENT_TO)

    def test_cancel_during_the_merge_keeps_the_old_index(self):
        import threading
        self.build_full()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(B.BuildCancelled):
            B.build(self.write_update(), self.dir, {}, cancel=cancel, topup_from=CURRENT_TO)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_a_topup_needs_an_installed_index(self):
        with self.assertRaises(SI.IndexUnusable):
            B.build(self.write_update(), self.dir, {}, topup_from=CURRENT_TO)


class ChooseTests(unittest.TestCase):
    def choose(self, current, now=NOW, topups=0, full=FULL_MODIFIED):
        return D.choose_update(current, topups, full, now)

    def test_an_index_from_yesterday_uses_the_one_day_file(self):
        self.assertEqual(self.choose("2026-10-21T06:26:22Z")[0], D.DAY_URL)

    def test_the_one_day_file_reaches_back_to_midnight_the_day_before(self):
        self.assertEqual(self.choose("2026-10-21T00:00:00Z")[0], D.DAY_URL)
        self.assertEqual(self.choose("2026-10-20T23:59:59Z")[0], D.WEEK_URL)

    def test_an_index_from_this_week_uses_the_one_week_file(self):
        self.assertEqual(self.choose("2026-10-17T10:00:00Z")[0], D.WEEK_URL)
        self.assertEqual(self.choose("2026-10-15T00:00:00Z")[0], D.WEEK_URL)

    def test_an_older_index_downloads_the_full_dump(self):
        self.assertIsNone(self.choose("2026-10-14T23:59:59Z"))

    def test_http_dates_are_read(self):
        self.assertEqual(self.choose("Wed, 21 Oct 2026 06:26:22 GMT")[0], D.DAY_URL)

    def test_an_unreadable_date_means_the_full_dump(self):
        self.assertIsNone(self.choose(""))
        self.assertIsNone(self.choose("yesterday"))
        self.assertIsNone(self.choose(CURRENT_TO, full="unknown"))

    def test_many_topups_or_an_old_lineage_means_the_full_dump(self):
        self.assertIsNone(self.choose(CURRENT_TO, topups=D.MAX_TOPUPS))
        self.assertIsNotNone(self.choose(CURRENT_TO, topups=D.MAX_TOPUPS - 1))
        self.assertIsNone(self.choose(CURRENT_TO, now=datetime(2027, 1, 1, tzinfo=timezone.utc), full="Mon, 01 Jun 2026 00:00:00 GMT"))

    def test_the_urls_are_spansh_s_download_server(self):
        self.assertEqual(D.DAY_URL, "https://downloads.spansh.co.uk/systems_1day.json.gz")
        self.assertEqual(D.WEEK_URL, "https://downloads.spansh.co.uk/systems_1week.json.gz")


class Routing:
    """Answers each URL from its own fake server, so the job's choice of file can be seen."""

    def __init__(self, **servers):
        self.servers = servers
        self.log = []

    def __call__(self, request, timeout=None):
        self.log.append(request.full_url)
        return self.servers[request.full_url](request, timeout)


class JobTests(Base):
    def make_job(self, opener):
        courtesy = C.Courtesy(opener=opener, clock=lambda: 0.0, sleep=lambda seconds: None, jitter=lambda: 0.0)
        return J.StarIndexJob(self.dir, courtesy=courtesy, free_space=PLENTY, run_inline=True, clock=lambda: NOW)

    def read(self, path):
        with open(path, "rb") as handle:
            return handle.read()

    def installed(self):
        self.build_full()
        self.assertEqual(SI.status(self.dir).topups, 0)

    def test_an_update_downloads_the_small_file_and_merges_it(self):
        self.installed()
        day = FakeServer(self.read(self.write_update()), etag='"d1"', last_modified=NEXT_MODIFIED)
        full = FakeServer(b"never asked")
        job = self.make_job(Routing(**{D.DAY_URL: day, D.DUMP_URL: full}))
        job.start(update=True)
        state = job.snapshot()
        self.assertEqual(state.state, J.DONE, state.text)
        self.assertIn("1-day file", state.text)
        self.assertEqual(full.requests, [])
        self.assertEqual(day.requests[0]["if-modified-since"], FULL_MODIFIED)
        self.assertNotIn("if-none-match", day.requests[0])
        status = SI.status(self.dir)
        want = self.expected()
        self.assertEqual((status.count, status.topups, status.source_modified, status.full_modified, status.etag, status.full_etag),
                         (len(want), 1, NEXT_MODIFIED, FULL_MODIFIED, '"d1"', '"v1"'))
        self.assertEqual(sorted(os.listdir(self.dir)), [SI.INDEX_FILENAME])           # the update file is deleted

    def test_a_second_update_the_same_day_finds_nothing_new(self):
        self.installed()
        day = FakeServer(self.read(self.write_update()), etag='"d1"', last_modified=NEXT_MODIFIED)
        job = self.make_job(Routing(**{D.DAY_URL: day}))
        job.start(update=True)
        after_first = self.read(SI.index_path(self.dir))
        job.start(update=True)
        self.assertEqual(day.requests[1]["if-modified-since"], NEXT_MODIFIED)
        self.assertIn("already up to date", job.snapshot().text)
        self.assertEqual(self.read(SI.index_path(self.dir)), after_first)

    def test_an_index_a_few_days_old_uses_the_week_file(self):
        self.installed()
        job = J.StarIndexJob(self.dir, courtesy=C.Courtesy(opener=Routing(**{D.WEEK_URL: FakeServer(self.read(self.write_update(oldest="2026-10-14T00:00:01Z")),
                                                                                                  last_modified=NEXT_MODIFIED)}),
                                                              clock=lambda: 0.0, sleep=lambda seconds: None, jitter=lambda: 0.0),
                             free_space=PLENTY, run_inline=True, clock=lambda: datetime(2026, 10, 24, 9, 0, tzinfo=timezone.utc))
        job.start(update=True)
        self.assertEqual(job.snapshot().state, J.DONE, job.snapshot().text)
        self.assertIn("1-week file", job.snapshot().text)

    def test_a_file_that_does_not_reach_back_falls_back_to_the_full_dump(self):
        self.installed()
        late = FakeServer(self.read(self.write_update(oldest="2026-10-21T20:00:00Z")), last_modified=NEXT_MODIFIED)
        newer_stars = fx.make_stars(500, seed=12)
        fx.write_dump(self.path("newer.json.gz"), newer_stars, extras=10)
        full = FakeServer(self.read(self.path("newer.json.gz")), etag='"v2"', last_modified=NEXT_MODIFIED)
        opener = Routing(**{D.DAY_URL: late, D.DUMP_URL: full})
        job = self.make_job(opener)
        job.start(update=True)
        state = job.snapshot()
        self.assertEqual(state.state, J.DONE, state.text)
        self.assertEqual(opener.log, [D.DAY_URL, D.DUMP_URL])
        status = SI.status(self.dir)
        self.assertEqual((status.count, status.topups, status.full_etag), (500, 0, '"v2"'))
        self.assertEqual(sorted(os.listdir(self.dir)), [SI.INDEX_FILENAME])

    def test_after_a_topup_a_full_update_is_conditional_on_the_original_dump(self):
        self.installed()
        day = FakeServer(self.read(self.write_update()), etag='"d1"', last_modified=NEXT_MODIFIED)
        self.make_job(Routing(**{D.DAY_URL: day})).start(update=True)
        far = datetime(2027, 6, 1, tzinfo=timezone.utc)
        full = FakeServer(b"unused", etag='"v1"', last_modified=FULL_MODIFIED)
        courtesy = C.Courtesy(opener=Routing(**{D.DUMP_URL: full}), clock=lambda: 0.0, sleep=lambda seconds: None, jitter=lambda: 0.0)
        job = J.StarIndexJob(self.dir, courtesy=courtesy, free_space=PLENTY, run_inline=True, clock=lambda: far)
        job.start(update=True)
        self.assertEqual(full.requests[0]["if-none-match"], '"v1"')
        self.assertIn("already up to date", job.snapshot().text)

    def test_a_cancelled_topup_keeps_the_old_index(self):
        self.installed()
        before = self.read(SI.index_path(self.dir))
        day = FakeServer(self.read(self.write_update()), last_modified=NEXT_MODIFIED)
        job = self.make_job(Routing(**{D.DAY_URL: day}))
        real = J.star_index_build.build

        def build(source, directory, info, cancel, progress, topup_from=""):
            job.cancel()
            return real(source, directory, info, cancel, progress, topup_from=topup_from)

        from unittest import mock
        with mock.patch.object(J.star_index_build, "build", build):
            job.start(update=True)
        self.assertEqual(job.snapshot().state, J.CANCELLED)
        self.assertEqual(self.read(SI.index_path(self.dir)), before)
        self.assertEqual(sorted(os.listdir(self.dir)), [SI.INDEX_FILENAME])


if __name__ == "__main__":
    unittest.main()
