"""The bodies the Rhino mined on, read from the journals for the Surface Mining Book (plugin/mining_bodies_data.py, the reading in mining_history.py and the "From your journals" list in
mining_ledger_data.py). No network and no EDMC."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import types  # noqa: E402
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))
from plugin import mining_bodies_data as BD, mining_history as H, mining_ledger_data as LD, mining_hotspots  # noqa: E402

MINING = {"Type": "$PlanetaryMiningLocation_Name;", "Type_Localised": "Planetary Mining Location", "Count": 4}
EVENTS = [
    {"timestamp": "2026-02-01T10:00:00Z", "event": "FSDJump", "StarSystem": "Sys A"},
    {"timestamp": "2026-02-01T10:01:00Z", "event": "SAASignalsFound", "BodyName": "Sys A 3 a", "Signals": [MINING, {"Type": "$SAA_SignalType_Geological;", "Count": 2}]},
    {"timestamp": "2026-02-01T10:02:00Z", "event": "SAASignalsFound", "BodyName": "Sys A 5 b", "Signals": [{**MINING, "Count": 2}]},
    {"timestamp": "2026-02-01T10:02:30Z", "event": "SAASignalsFound", "BodyName": "Sys A 3 A Ring", "Signals": [MINING]},                 # a ring is not a landable body
    {"timestamp": "2026-02-01T10:03:00Z", "event": "Scan", "BodyName": "Sys A 3 a", "Landable": True, "PlanetClass": "Rocky body"},
    {"timestamp": "2026-02-01T10:04:00Z", "event": "ApproachBody", "StarSystem": "Sys A", "Body": "Sys A 3 a"},
    {"timestamp": "2026-02-01T10:05:00Z", "event": "MiningRefined", "Type_Localised": "Osmium"},                                           # a ship refining in space: no Rhino out
    {"timestamp": "2026-02-01T10:06:00Z", "event": "LaunchSRV", "SRVType": "mev_rhino"},
    {"timestamp": "2026-02-01T10:07:00Z", "event": "MiningRefined", "Type_Localised": "Haematite"},
    {"timestamp": "2026-02-01T10:08:00Z", "event": "MiningRefined", "Type_Localised": "Haematite"},
    {"timestamp": "2026-02-01T10:09:00Z", "event": "DockSRV"},
    {"timestamp": "2026-02-01T10:10:00Z", "event": "MiningRefined", "Type_Localised": "Osmium"},                                           # after docking: not counted
    {"timestamp": "2026-02-01T10:11:00Z", "event": "LaunchSRV", "SRVType": "mev_scarab"},
    {"timestamp": "2026-02-01T10:12:00Z", "event": "MiningRefined", "Type_Localised": "Gold"},                                              # not a Rhino
]


class ReadingTests(unittest.TestCase):
    def test_locations_class_and_the_tons_refined_with_the_rhino(self) -> None:
        found = BD.bodies_from(EVENTS)
        self.assertEqual(sorted(r["body"] for r in found.values()), ["Sys A 3 a", "Sys A 5 b"])
        a = found[BD.body_key("Sys A 3 a")]
        self.assertEqual((a["locations"], a["class"], a["tons"], a["last"], a["system"]), (4, "Rocky body", 2, "2026-02-01T10:08:00Z", "Sys A"))
        b = found[BD.body_key("Sys A 5 b")]
        self.assertEqual((b["locations"], b["tons"], b["class"]), (2, 0, ""))

    def test_refining_with_no_body_known_is_not_counted(self) -> None:
        events = [{"event": "LaunchSRV", "SRVType": "mev_rhino"}, {"event": "MiningRefined", "Type_Localised": "Gold"}]
        self.assertEqual(BD.bodies_from(events), {})

    def test_leaving_the_body_stops_the_credit(self) -> None:
        events = [{"event": "ApproachBody", "StarSystem": "S", "Body": "S 1"}, {"event": "LaunchSRV", "SRVType": "mev_rhino"}, {"event": "LeaveBody"},
                  {"event": "MiningRefined", "Type_Localised": "Gold"}]
        self.assertEqual(BD.bodies_from(events), {})

    def test_merge_adds_tons_and_keeps_the_latest_count_and_class(self) -> None:
        into = {}
        BD.merge(into, {**BD.new_body("B", "S"), "locations": 3, "scanned": "2026-01-01", "tons": 5, "last": "2026-01-02"})
        BD.merge(into, {**BD.new_body("B"), "locations": 4, "scanned": "2026-02-01", "tons": 7, "last": "2026-02-02", "class": "Icy body"})
        BD.merge(into, {**BD.new_body("B"), "locations": 9, "scanned": "2025-01-01", "tons": 1})
        record = into[BD.body_key("B")]
        self.assertEqual((record["locations"], record["tons"], record["last"], record["class"], record["system"]), (4, 13, "2026-02-02", "Icy body", "S"))


class HistoryTests(unittest.TestCase):
    def test_every_journal_is_read_for_bodies_and_an_older_file_is_read_again(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            def write(name, lines):
                with open(os.path.join(folder, name), "w", encoding="utf-8") as handle:
                    handle.write("\n".join(json.dumps(x) for x in lines) + "\n")
            owner = {"event": "Commander", "Name": "Bocheaux"}
            write("Journal.2026-02-01T000000.01.log", [owner] + EVENTS)
            write("Journal.2026-02-02T000000.01.log", [owner, {"event": "FSDJump", "StarSystem": "Sys A"}])
            history = H.MiningHistory()
            history.pause = 0
            history.start(tempfile.mkdtemp())
            history.set_commander("Bocheaux")
            history._thread.join()
            history.refresh(folder, wait=True)
            self.assertEqual(history.bodies()[BD.body_key("Sys A 3 a")]["tons"], 2)
            # an older file (saved before the bodies were read) is read again, and tons are not counted twice
            payload = history._payload()
            payload["extras"], payload["bodies"], payload["scan_files"] = 1, {"stale": {"body": "x"}}, ["Journal.2026-02-01T000000.01.log"]
            history._save()
            history.refresh(folder, wait=True)
            self.assertEqual(history.bodies()[BD.body_key("Sys A 3 a")]["tons"], 2)
            self.assertNotIn("stale", history.bodies())


class ListTests(unittest.TestCase):
    JOURNAL = {BD.body_key("Sys A 3 a"): {"body": "Sys A 3 a", "system": "Sys A", "locations": 4, "class": "Rocky body", "tons": 12, "last": ""},
               BD.body_key("Sys B 1"): {"body": "Sys B 1", "system": "Sys B", "locations": 2, "class": "", "tons": 0, "last": ""},
               BD.body_key("Sys C 2 c"): {"body": "Sys C 2 c", "system": "Sys C", "locations": 0, "class": "Icy body", "tons": 30, "last": ""}}

    def test_journal_bodies_not_otherwise_listed_form_their_own_group(self) -> None:
        saved = [mining_hotspots.Hotspot("Sys A", "Sys A 3 a", "Painite")]
        groups = LD.build_body_groups("Elsewhere", [], saved, journal=self.JOURNAL)
        by_key = {key: entries for key, _heading, entries in groups}
        self.assertEqual([e.body for e in by_key["journal"]], ["Sys C 2 c", "Sys B 1"], "most tons first, then most locations; a saved body is not repeated")
        other = by_key["other-systems"][0]
        self.assertEqual((other.body, other.mining_signal_count, other.refined_tons), ("Sys A 3 a", 4, 12), "a saved body gets the journals' count and tons")
        self.assertEqual([h for _k, h, _e in groups if _k == "journal"], [LD.GROUP_JOURNAL])

    def test_a_filter_leaves_the_journal_group_out(self) -> None:
        saved = [mining_hotspots.Hotspot("Sys A", "Sys A 3 a", "Painite")]
        groups = LD.build_body_groups("Elsewhere", [], saved, material="Painite", journal=self.JOURNAL)
        self.assertNotIn("journal", [key for key, _h, _e in groups])

    def test_no_journal_data_changes_nothing(self) -> None:
        self.assertEqual(LD.build_body_groups("S", [], []), [])


if __name__ == "__main__":
    unittest.main()
