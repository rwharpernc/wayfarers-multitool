"""The local star index (star_index.py, star_index_build.py): reading a dump, building the index, the nearest-star query against a brute-force search, and what happens with a damaged,
older, cut-short or half-built index. Everything runs on a small synthetic dump in the real record shape (tests/star_index_fixtures.py); nothing is downloaded."""
from __future__ import annotations

import gzip
import json
import os
import random
import struct
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from plugin import star_index as SI            # noqa: E402
from plugin import star_index_build as SB      # noqa: E402
import star_index_fixtures as fx                # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = os.path.join(self._tmp.name, "star_index")
        self.dump = os.path.join(self._tmp.name, "dump.json.gz")
        SI.forget()
        self.addCleanup(SI.forget)

    def make(self, count=3000, extras=400, **options):
        self.stars = fx.make_stars(count, **options)
        fx.write_dump(self.dump, self.stars, extras=extras)
        return self.stars

    def build(self, **kw):
        return SB.build(self.dump, self.dir, {"url": "x", "etag": '"e1"', "last_modified": "Wed, 21 Oct 2026 06:26:22 GMT"}, **kw)

    def open(self):
        return SI.StarIndex(SI.index_path(self.dir))


class ParseTests(unittest.TestCase):
    def test_a_neutron_star_line_is_read(self):
        line = (b'\t{"id64":2000183,"name":"Pyroomoa AA-A h0","mainStar":"Neutron Star","coords":{"x":-11160.1875,"y":2163.90625,"z":24616.40625},'
                b'"updateTime":"2021-09-13T10:50:16Z"},')
        self.assertEqual(SB.parse_line(line), (2000183, "Pyroomoa AA-A h0", -357126, 69245, 787725))

    def test_other_main_stars_and_structure_lines_are_skipped(self):
        black = b'\t{"id64":1,"name":"A","mainStar":"Black Hole","coords":{"x":1,"y":2,"z":3},"updateTime":"x"},'
        self.assertIsNone(SB.parse_line(black))
        for line in (b"[", b"]", b"", b"\t"):
            self.assertIsNone(SB.parse_line(line))

    def test_a_name_with_an_escape_or_another_field_order_is_still_read(self):
        escaped = b'\t{"id64":5,"name":"Odd \\"Quoted\\" \\u00e9","mainStar":"Neutron Star","coords":{"x":1.5,"y":-2,"z":3},"updateTime":"x"},'
        self.assertEqual(SB.parse_line(escaped), (5, 'Odd "Quoted" é', 48, -64, 96))
        reordered = b'\t{"name":"B","id64":6,"coords":{"x":1,"y":2,"z":3},"mainStar":"Neutron Star"}'
        self.assertEqual(SB.parse_line(reordered), (6, "B", 32, 64, 96))

    def test_names_round_trip_through_the_codec(self):
        for name in ("Eol Prou RS-T d3-94", "Pyroomoa AA-A h0", "Col 285 Sector AB-C a12-0"):
            parts = SI.split_name(name)
            self.assertIsNotNone(parts, name)
            self.assertEqual(SI.join_name(*parts), name)
        for name in ("Sol", "HIP 8887", "Odd Name 5", "Eol Prou RS-T d03-94", "X AA-A h007"):
            self.assertIsNone(SI.split_name(name), name)

    def test_varints_round_trip(self):
        for value in (0, 1, 127, 128, 300, 16383, 16384, 2 ** 40):
            out = bytearray()
            SI.put_varint(out, value)
            self.assertEqual(SI.get_varint(bytes(out), 0), (value, len(out)))


class DumpReadingTests(Base):
    def test_only_neutron_stars_are_kept_and_names_come_back_whole(self):
        stars = self.make(500, extras=300)
        result = self.build()
        self.assertEqual(result.count, 500)
        index = self.open()
        found = {hit.id64: hit for hit in index.nearest(0, 0, 0, 500, max_radius_ly=100000)}
        self.assertEqual(set(found), {s.id64 for s in stars})
        for star in stars:
            hit = found[star.id64]
            self.assertEqual((hit.name, hit.x, hit.y, hit.z), (star.name, star.x, star.y, star.z))

    def test_a_dump_in_several_gzip_members_is_read(self):
        stars = fx.make_stars(200)
        fx.write_dump(self.dump, stars[:100])
        second = os.path.join(self._tmp.name, "second.json.gz")
        fx.write_dump(second, stars[100:])
        with open(self.dump, "ab") as out, open(second, "rb") as more:
            out.write(more.read())
        self.assertEqual(sum(len(chunk) for chunk in SB.dump_lines(self.dump)) > 0, True)
        lines = [line for chunk in SB.dump_lines(self.dump) for line in chunk]
        self.assertEqual(sum(1 for line in lines if SB.parse_line(line)), 200)

    def test_a_file_cut_short_or_not_gzip_is_an_error(self):
        self.make(300)
        with open(self.dump, "rb") as handle:
            data = handle.read()
        with open(self.dump, "wb") as handle:
            handle.write(data[:len(data) // 2])
        with self.assertRaises(SB.BuildError):
            self.build()
        with open(self.dump, "wb") as handle:
            handle.write(b"this is not gzip data at all" * 100)
        with self.assertRaises(SB.BuildError):
            self.build()

    def test_a_dump_without_neutron_stars_is_refused(self):
        fx.write_dump(self.dump, [], extras=50)
        with self.assertRaises(SB.BuildError):
            self.build()
        self.assertFalse(os.path.exists(SI.index_path(self.dir)))


class QueryTests(Base):
    def test_nearest_matches_a_brute_force_search_at_random_points(self):
        stars = self.make(4000, spread=3000.0, flat=500.0)
        self.build()
        index = self.open()
        rng = random.Random(11)
        for _ in range(250):
            x, y, z = rng.uniform(-3300, 3300), rng.uniform(-700, 700), rng.uniform(-3300, 3300)
            want = fx.brute_nearest(stars, x, y, z, 4)
            got = index.nearest(x, y, z, 4, max_radius_ly=100000)
            self.assertEqual([h.id64 for h in got], [id64 for _d, id64 in want])
            for hit, (distance, _id) in zip(got, want):
                self.assertAlmostEqual(hit.distance_ly, distance, places=6)

    def test_points_on_cell_borders_and_corners(self):
        stars = self.make(3000, spread=1500.0, flat=300.0)
        self.build()
        index = self.open()
        for gx in (-512, -256, 0, 256, 512, 1024):
            for gz in (-256, 0, 256, 768):
                for gy in (-256, 0, 256):
                    for nudge in (0.0, 0.03125, -0.03125):
                        x, y, z = gx + nudge, gy, gz - nudge
                        want = fx.brute_nearest(stars, x, y, z, 3)
                        got = index.nearest(x, y, z, 3, max_radius_ly=100000)
                        self.assertEqual([h.id64 for h in got], [i for _d, i in want], (x, y, z))
        self.assertEqual(SI.CELL_LY, 256)

    def test_a_search_with_a_limited_radius_returns_only_what_is_inside_it(self):
        stars = self.make(1500, spread=4000.0, flat=300.0)
        self.build()
        index = self.open()
        x, y, z = 0.0, 0.0, 0.0
        inside = [s for s in stars if ((s.x - x) ** 2 + (s.y - y) ** 2 + (s.z - z) ** 2) ** 0.5 <= 500]
        got = index.nearest(x, y, z, 500, max_radius_ly=500)
        self.assertEqual({h.id64 for h in got}, {s.id64 for s in inside})
        self.assertTrue(all(h.distance_ly <= 500 for h in got))

    def test_empty_areas_return_nothing_or_the_far_star(self):
        self.make(500, spread=500.0, flat=100.0)
        self.build()
        index = self.open()
        self.assertEqual(index.nearest(50000, 0, 50000, 2, max_radius_ly=2000), [])
        far = index.nearest(6000, 0, 6000, 1, max_radius_ly=100000)
        self.assertEqual(len(far), 1)
        self.assertGreater(far[0].distance_ly, 5000)
        self.assertEqual(index.nearest(-1e9, 0, 1e9, 2), [])        # far outside the grid

    def test_results_are_nearest_first_and_count_is_respected(self):
        self.make(2000)
        self.build()
        got = self.open().nearest(100, 10, -100, 7, max_radius_ly=100000)
        self.assertEqual(len(got), 7)
        self.assertEqual([h.distance_ly for h in got], sorted(h.distance_ly for h in got))

    def test_the_star_at_the_query_position_is_found_at_distance_zero(self):
        stars = self.make(800)
        self.build()
        star = stars[17]
        hit = self.open().nearest(star.x, star.y, star.z, 1)[0]
        self.assertEqual((hit.id64, hit.distance_ly), (star.id64, 0.0))

    def test_every_kind_of_name_comes_back(self):
        stars = self.make(1200, odd_every=7)
        self.build()
        index = self.open()
        by_id = {s.id64: s.name for s in stars}
        for hit in index.nearest(0, 0, 0, 1200, max_radius_ly=100000):
            self.assertEqual(hit.name, by_id[hit.id64])
        self.assertTrue(any(name.startswith("Odd Name") for name in by_id.values()))

    def test_sector_numbers_three_bytes_wide_work_too(self):
        """With 65,535 sectors or more the sector number is 3 bytes wide; the limit is lowered here so a small dump takes that path."""
        stars = self.make(400)
        with mock.patch.object(SB, "TWO_BYTE_SECTORS", 3):
            self.build()
        index = self.open()
        self.assertEqual(index.meta["sector_width"], 3)
        by_id = {s.id64: s.name for s in stars}
        got = index.nearest(0, 0, 0, 400, max_radius_ly=100000)
        self.assertEqual({h.id64: h.name for h in got}, by_id)

    def test_the_number_of_temporary_files_does_not_change_the_result(self):
        stars = self.make(300)
        with mock.patch.object(SB, "BUCKETS", 4):
            self.build()
        got = self.open().nearest(0, 0, 0, 300, max_radius_ly=100000)
        self.assertEqual({h.id64: h.name for h in got}, {s.id64: s.name for s in stars})


class StatusAndDamageTests(Base):
    def test_missing_then_installed(self):
        self.assertEqual(SI.status(self.dir).state, "missing")
        self.make(600)
        result = self.build()
        status = SI.status(self.dir)
        self.assertEqual((status.state, status.count, status.etag), ("ok", 600, '"e1"'))
        self.assertEqual(status.source_modified, "Wed, 21 Oct 2026 06:26:22 GMT")
        self.assertEqual(status.size_bytes, result.size_bytes)
        self.assertTrue(status.built.endswith("Z"))

    def test_a_cut_short_index_is_damaged(self):
        self.make(600)
        self.build()
        path = SI.index_path(self.dir)
        with open(path, "rb") as handle:
            data = handle.read()
        with open(path, "wb") as handle:
            handle.write(data[:-5000])
        self.assertEqual(SI.status(self.dir).state, "damaged")
        with self.assertRaises(SI.IndexUnusable) as caught:
            self.open()
        self.assertEqual(caught.exception.kind, "damaged")

    def test_garbage_and_empty_files_are_damaged(self):
        os.makedirs(self.dir)
        path = SI.index_path(self.dir)
        for data in (b"", b"x" * 100, b"not an index " * 1000):
            with open(path, "wb") as handle:
                handle.write(data)
            SI.forget()
            self.assertEqual(SI.status(self.dir).state, "damaged")

    def test_another_format_version_is_old_and_ignored(self):
        self.make(600)
        self.build()
        path = SI.index_path(self.dir)
        with open(path, "r+b") as handle:
            handle.seek(4)
            handle.write(struct.pack("<H", SI.FORMAT_VERSION + 1))
        SI.forget()
        status = SI.status(self.dir)
        self.assertEqual(status.state, "old")
        self.assertIn("format", status.message)
        with self.assertRaises(SI.IndexUnusable) as caught:
            self.open()
        self.assertEqual(caught.exception.kind, "old")

    def test_a_damaged_header_block_is_damaged(self):
        self.make(600)
        self.build()
        with open(SI.index_path(self.dir), "r+b") as handle:
            handle.seek(20)
            handle.write(b"\xff\xfe garbage")
        SI.forget()
        self.assertEqual(SI.status(self.dir).state, "damaged")


class BuildSafetyTests(Base):
    def test_an_error_during_the_build_leaves_the_old_index_intact(self):
        self.make(500)
        self.build()
        path = SI.index_path(self.dir)
        with open(path, "rb") as handle:
            before = handle.read()
        self.make(900, seed=9)
        with mock.patch.object(SB, "put_varint", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                self.build()
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertEqual(sorted(os.listdir(self.dir)), [SI.INDEX_FILENAME])      # no temporary file or folder is left behind
        self.assertEqual(SI.status(self.dir).count, 500)

    def test_a_dump_that_ends_early_leaves_the_old_index_intact(self):
        self.make(400)
        self.build()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        self.make(700, seed=4)
        with open(self.dump, "rb") as handle:
            data = handle.read()
        with open(self.dump, "wb") as handle:
            handle.write(data[:len(data) * 2 // 3])
        with self.assertRaises(SB.BuildError):
            self.build()
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_cancel_stops_the_build_and_keeps_the_old_index(self):
        self.make(500)
        self.build()
        with open(SI.index_path(self.dir), "rb") as handle:
            before = handle.read()
        self.make(900, seed=3)
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(SB.BuildCancelled):
            self.build(cancel=cancel)
        with open(SI.index_path(self.dir), "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertEqual(sorted(os.listdir(self.dir)), [SI.INDEX_FILENAME])

    def test_cancel_during_the_second_pass_also_cleans_up(self):
        self.make(900)
        cancel = threading.Event()
        calls = []

        def progress(fraction, text):
            calls.append(fraction)
            if fraction > 0.82:
                cancel.set()

        with self.assertRaises(SB.BuildCancelled):
            self.build(cancel=cancel, progress=progress)
        self.assertFalse(os.path.exists(SI.index_path(self.dir)))
        self.assertEqual(os.listdir(self.dir), [])

    def test_a_new_build_replaces_the_old_one(self):
        self.make(400)
        self.build()
        self.make(650, seed=5)
        self.build()
        self.assertEqual(SI.status(self.dir).count, 650)
        self.assertEqual(len(self.open().nearest(0, 0, 0, 1000, max_radius_ly=100000)), 650)

    def test_progress_is_reported_from_start_to_finish(self):
        self.make(600)
        seen = []
        self.build(progress=lambda fraction, text: seen.append((fraction, text)))
        self.assertGreaterEqual(len(seen), 3)
        self.assertEqual(seen[-1][0], 1.0)
        self.assertTrue(all(0.0 <= f <= 1.0 for f, _t in seen))
        self.assertEqual([f for f, _t in seen], sorted(f for f, _t in seen))

    def test_a_system_outside_the_grid_is_counted_and_left_out(self):
        stars = fx.make_stars(50)
        far = fx.Star(999, "Far Away AA-A h0", 200000.0, 0.0, 0.0)
        fx.write_dump(self.dump, stars + [far])
        result = self.build()
        self.assertEqual((result.count, result.skipped_outside_grid), (50, 1))


class NoMemoryHoldTests(Base):
    def test_the_index_file_can_be_replaced_and_deleted_after_a_query(self):
        """Nothing keeps the file open between queries, so Windows can replace or delete it."""
        self.make(400)
        self.build()
        self.open().nearest(0, 0, 0, 2)
        self.make(450, seed=8)
        self.build()
        os.remove(SI.index_path(self.dir))
        self.assertEqual(SI.status(self.dir).state, "missing")

    def test_the_header_json_has_the_source_and_fits_its_block(self):
        self.make(300)
        self.build()
        with open(SI.index_path(self.dir), "rb") as handle:
            head = handle.read(SI.HEADER_BYTES)
        meta = json.loads(head[12:].decode("utf-8"))
        self.assertEqual(meta["source"]["etag"], '"e1"')
        self.assertEqual(meta["count"], 300)
        self.assertEqual(len(head), SI.HEADER_BYTES)


if __name__ == "__main__":
    unittest.main()
