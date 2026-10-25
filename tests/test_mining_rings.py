"""The Space Mining Book's data (plugin/mining_rings_data.py, mining_rings.py and the ring reading in mining_history.py): rings from the journal's DSS scans and body scans, the tons mined at
them, the notes you write, rings added by hand, and the journals read once more for rings after an update. No network and no EDMC."""

import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from plugin import mining_history as H, mining_rings, mining_rings_data as RD  # noqa: E402

RING = "Col 285 Sector GG-X d1-123 10 A Ring"
DSS = {"timestamp": "2025-07-08T13:46:57Z", "event": "SAASignalsFound", "BodyName": RING, "SystemAddress": 4236758747475, "BodyID": 26,
       "Signals": [{"Type": "Serendibite", "Count": 3}, {"Type": "Alexandrite", "Count": 2}, {"Type": "Benitoite", "Count": 4}, {"Type": "$SAA_SignalType_Thing;", "Count": 9}]}
BODY = {"timestamp": "2025-07-08T13:40:00Z", "event": "Scan", "BodyName": "Col 285 Sector GG-X d1-123 10", "StarSystem": "Col 285 Sector GG-X d1-123", "ReserveLevel": "PristineResources",
        "Rings": [{"Name": RING, "RingClass": "eRingClass_MetalRich"}, {"Name": "Col 285 Sector GG-X d1-123 10 B Ring", "RingClass": "eRingClass_Icy"}]}
JUMP = {"timestamp": "2025-07-08T13:30:00Z", "event": "FSDJump", "StarSystem": "Col 285 Sector GG-X d1-123"}


class ReadingTests(unittest.TestCase):
    def test_a_dss_scan_gives_the_hotspot_counts_and_a_body_scan_the_class_and_reserve(self) -> None:
        found = H.rings_from([JUMP, BODY, DSS])
        record = found[RD.ring_key(RING)]
        self.assertEqual(record["hotspots"], {"Serendibite": 3, "Alexandrite": 2, "Benitoite": 4})     # the journal's own signal types are left out
        self.assertEqual((record["class"], record["reserve"], record["system"]), ("eRingClass_MetalRich", "PristineResources", "Col 285 Sector GG-X d1-123"))
        other = found[RD.ring_key("Col 285 Sector GG-X d1-123 10 B Ring")]
        self.assertEqual((other["class"], other["hotspots"]), ("eRingClass_Icy", {}))

    def test_a_scan_of_something_that_is_not_a_ring_is_ignored(self) -> None:
        body = {"event": "SAASignalsFound", "BodyName": "HIP 1 2", "Signals": [{"Type": "Platinum", "Count": 1}]}
        self.assertEqual(H.rings_from([body, {"event": "Scan", "BodyName": "x", "Rings": [None, {"Name": "not one"}]}]), {})

    def test_the_system_comes_from_the_last_jump_when_the_scan_does_not_say(self) -> None:
        self.assertEqual(H.rings_from([JUMP, DSS])[RD.ring_key(RING)]["system"], "Col 285 Sector GG-X d1-123")


class MergeTests(unittest.TestCase):
    def test_the_newer_scan_wins_and_known_details_are_kept(self) -> None:
        into = {}
        RD.merge(into, {**RD.new_ring(RING, "Sys"), "hotspots": {"Painite": 1}, "scanned": "2025-01-01", "class": "eRingClass_Icy", "seen": "2025-01-01"})
        RD.merge(into, {**RD.new_ring(RING), "hotspots": {"Painite": 2, "Platinum": 1}, "scanned": "2025-02-01"})
        RD.merge(into, {**RD.new_ring(RING), "hotspots": {"Painite": 9}, "scanned": "2024-01-01"})          # an older scan does not replace it
        record = into[RD.ring_key(RING)]
        self.assertEqual((record["hotspots"], record["class"], record["system"]), ({"Painite": 2, "Platinum": 1}, "eRingClass_Icy", "Sys"))


class TextTests(unittest.TestCase):
    def test_names(self) -> None:
        self.assertEqual((RD.class_text("eRingClass_MetalRich"), RD.class_text("eRingClass_Metalic"), RD.class_text("eRingClass_Icy"), RD.class_text("")), ("Metal rich", "Metallic", "Icy", ""))
        self.assertEqual((RD.reserve_text("PristineResources"), RD.reserve_text("LowResources"), RD.reserve_text(None)), ("Pristine", "Low", ""))
        self.assertEqual(RD.hotspot_text({"Painite": 3, "Platinum": 2, "Alexandrite": 3}), "Alexandrite 3, Painite 3, Platinum 2")
        self.assertTrue(RD.hotspot_text({str(i): i + 1 for i in range(8)}).endswith("+2 more"))

    def test_parse_hotspots(self) -> None:
        self.assertEqual(RD.parse_hotspots("Painite 3, Low Temperature Diamonds 2; Platinum"), {"Painite": 3, "Low Temperature Diamonds": 2, "Platinum": 1})
        self.assertEqual(RD.parse_hotspots(""), {})
        self.assertIsNone(RD.parse_hotspots("3"))
        self.assertIsNone(RD.parse_hotspots("Painite 0"))


class RowTests(unittest.TestCase):
    RINGS = {RD.ring_key(RING): {**RD.new_ring(RING, "Sys A"), "hotspots": {"Painite": 3}, "class": "eRingClass_Icy", "reserve": "MajorResources", "seen": "2025-07-08"},
             RD.ring_key("Quiet 1 A Ring"): {**RD.new_ring("Quiet 1 A Ring", "Sys B"), "hotspots": {"Platinum": 1}}}
    RUNS = [{"ring": RING, "system": "Sys A", "start": "2025-07-09T10:00:00Z", "refined": {"Painite": 40, "Osmium": 10}},
            {"ring": RING.lower(), "start": "2025-08-01T10:00:00Z", "refined": {"Painite": 5}},
            {"ring": "Unscanned 9 B Ring", "system": "Sys C", "start": "2025-06-01T10:00:00Z", "refined": {"Gold": 7}}, {"ring": "", "refined": {"Gold": 99}}]

    def test_rows_join_scans_mining_and_notes(self) -> None:
        user = {RD.ring_key("Quiet 1 A Ring"): {"favorite": True, "note": "good for lasers"}, RD.ring_key("By Hand 1 A Ring"): {"manual": {**RD.new_ring("By Hand 1 A Ring", "Sys D"), "hotspots": {"Gold": 2}}}}
        rows = {row.ring: row for row in RD.build_rows(self.RINGS, self.RUNS, user)}
        self.assertEqual(set(rows), {RING, "Quiet 1 A Ring", "Unscanned 9 B Ring", "By Hand 1 A Ring"})
        main = rows[RING]
        self.assertEqual((main.tons, main.runs, main.last_mined[:10], main.ring_class, main.reserve), (55, 2, "2025-08-01", "Icy", "Major"))
        self.assertEqual((rows["Unscanned 9 B Ring"].tons, rows["Unscanned 9 B Ring"].system, rows["Unscanned 9 B Ring"].hotspots), (7, "Sys C", {}))
        self.assertTrue(rows["By Hand 1 A Ring"].manual and not rows[RING].manual)
        self.assertEqual((rows["Quiet 1 A Ring"].favorite, rows["Quiet 1 A Ring"].note), (True, "good for lasers"))
        self.assertEqual(RD.build_rows(self.RINGS, self.RUNS, user)[0].ring, "Quiet 1 A Ring", "favorites come first")

    def test_a_ring_only_seen_as_part_of_a_scanned_planet_is_left_out(self) -> None:
        rings = {**self.RINGS, RD.ring_key("Plain 1 A Ring"): {**RD.new_ring("Plain 1 A Ring", "Sys E"), "class": "eRingClass_Rocky", "reserve": "CommonResources"},
                 RD.ring_key("Noted 1 A Ring"): {**RD.new_ring("Noted 1 A Ring", "Sys F"), "class": "eRingClass_Icy"}}
        names = {row.ring for row in RD.build_rows(rings, self.RUNS, {RD.ring_key("Noted 1 A Ring"): {"note": "look again"}})}
        self.assertNotIn("Plain 1 A Ring", names)
        self.assertIn("Noted 1 A Ring", names, "a note keeps a ring")
        self.assertTrue({RING, "Quiet 1 A Ring", "Unscanned 9 B Ring"} <= names, "hotspots or a mining run keep a ring")

    def test_filtering(self) -> None:
        rows = RD.build_rows(self.RINGS, self.RUNS, {RD.ring_key("Quiet 1 A Ring"): {"favorite": True, "note": "Lasers"}})
        self.assertEqual([r.ring for r in RD.filter_rows(rows, "painite")], [RING])
        self.assertEqual([r.ring for r in RD.filter_rows(rows, "sys b")], ["Quiet 1 A Ring"])
        self.assertEqual([r.ring for r in RD.filter_rows(rows, "lasers")], ["Quiet 1 A Ring"])
        self.assertEqual([r.ring for r in RD.filter_rows(rows, "", favorites_only=True)], ["Quiet 1 A Ring"])
        self.assertEqual(len(RD.filter_rows(rows, "")), 3)


class NotesTests(unittest.TestCase):
    def test_notes_favorites_and_manual_rings_are_per_commander_and_kept(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            book = mining_rings.RingNotes()
            book.start(folder)
            self.assertFalse(book.set_note("k", "x"), "no commander yet")
            book.set_commander("Bocheaux")
            key = RD.ring_key(RING)
            self.assertTrue(book.set_note(key, "  a   note "))
            self.assertTrue(book.set_favorite(key, True))
            self.assertEqual(book.add_manual("By Hand 1 A Ring", "Sys D", {"Gold": 2}, "Icy", "Low"), RD.ring_key("By Hand 1 A Ring"))
            self.assertIsNone(book.add_manual("  ", "x", {}))
            again = mining_rings.RingNotes()
            again.start(folder)
            again.set_commander("Bocheaux")
            entries = again.entries()
            self.assertEqual((entries[key]["note"], entries[key]["favorite"]), ("a note", True))
            self.assertEqual(entries[RD.ring_key("By Hand 1 A Ring")]["manual"]["hotspots"], {"Gold": 2})
            again.set_commander("Someone Else")
            self.assertEqual(again.entries(), {}, "another commander's notes are not shared")
            again.set_commander("Bocheaux")
            again.set_note(key, "")
            again.set_favorite(key, False)
            self.assertNotIn(key, again.entries(), "an empty entry is dropped")
            self.assertTrue(again.remove_manual(RD.ring_key("By Hand 1 A Ring")))
            self.assertEqual(again.entries(), {})


class HistoryReadingTests(unittest.TestCase):
    def test_every_journal_is_read_for_rings_and_an_old_file_is_read_again(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            def write(name, lines):
                with open(os.path.join(folder, name), "w", encoding="utf-8") as handle:
                    handle.write("\n".join(json.dumps(x) for x in lines) + "\n")
            owner = {"event": "Commander", "Name": "Bocheaux"}
            write("Journal.2026-01-01T000000.01.log", [owner, JUMP, BODY, DSS])
            write("Journal.2026-01-02T000000.01.log", [owner, JUMP, {"timestamp": "2026-01-02T10:00:00Z", "event": "ProspectedAsteroid", "Content": "$AsteroidMaterialContent_High;"}])
            plugin_dir = tempfile.mkdtemp()
            history = H.MiningHistory()
            history.pause = 0
            history.start(plugin_dir)
            history.set_commander("Bocheaux")
            history._thread.join()
            history.refresh(folder, wait=True)
            self.assertEqual(history.rings()[RD.ring_key(RING)]["hotspots"]["Benitoite"], 4)
            # a file saved before the Space Mining Book had no rings: it is read once more, and its runs are not counted twice
            payload = history._payload()
            runs_before = len(payload["runs"])
            payload["rings"], payload["scan_files"] = {}, []
            history._save()
            history.refresh(folder, wait=True)
            self.assertEqual(history.rings()[RD.ring_key(RING)]["class"], "eRingClass_MetalRich")
            self.assertEqual(len(history._payload()["runs"]), runs_before)

    def test_an_older_payload_without_rings_is_upgraded(self) -> None:
        history = H.MiningHistory()
        history.start(tempfile.mkdtemp())
        history._cmdr = "Bocheaux"
        from plugin import commander_data
        commander_data.put(history._store, "Bocheaux", {"files": ["a"], "runs": []})
        payload = history._payload()
        # the rings and bodies are read again, and so are the runs: a payload from before the Rhino's refining was told apart from the rings' has none of that in its runs
        self.assertEqual((payload["rings"], payload["scan_files"], payload["files"], payload["runs"]), ({}, [], [], []))
        self.assertEqual(payload["runs_v"], H.RUNS_VERSION)
        self.assertEqual(history.rings(), {})


if __name__ == "__main__":
    unittest.main()
