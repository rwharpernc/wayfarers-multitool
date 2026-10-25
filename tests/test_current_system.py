"""Finding the system the commander is in on demand (current_system.py): what the caller tracked, then EDMC's state, then the newest journal."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import current_system as C  # noqa: E402


def write_journal(folder, name, events, age=0):
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event) + "\n")
    stamp = time.time() - age
    os.utime(path, (stamp, stamp))


class CurrentSystemTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_the_last_jump_in_the_newest_journal(self):
        write_journal(self.dir.name, "Journal.2026-10-14T100000.01.log", [{"event": "FSDJump", "StarSystem": "Old"}], age=5000)
        write_journal(self.dir.name, "Journal.2026-10-15T100000.01.log",
                      [{"event": "Location", "StarSystem": "Sol"}, {"event": "Scan"}, {"event": "FSDJump", "StarSystem": "Lave"}, {"event": "Scan"}])
        self.assertEqual(C.from_journal(self.dir.name, cmdr=""), "Lave")

    def test_a_newest_journal_without_a_location_falls_back_to_the_one_before(self):
        write_journal(self.dir.name, "Journal.2026-10-14T100000.01.log", [{"event": "CarrierJump", "StarSystem": "Carrier Home"}], age=5000)
        write_journal(self.dir.name, "Journal.2026-10-15T100000.01.log", [{"event": "Fileheader"}])
        self.assertEqual(C.from_journal(self.dir.name, cmdr=""), "Carrier Home")

    def test_the_last_place_carries_the_position_and_the_system_details(self):
        write_journal(self.dir.name, "Journal.2026-10-15T100000.01.log", [
            {"event": "FSDJump", "StarSystem": "Sol", "StarPos": [0, 0, 0]},
            {"event": "Location", "StarSystem": "Lave", "StarPos": [75.75, 48.75, 70.59], "SystemAllegiance": "Federation", "SystemGovernment": "$government_Democracy;"},
            {"event": "Scan"}])
        place = C.last_place(self.dir.name)
        self.assertEqual(place["StarSystem"], "Lave")
        self.assertEqual(place["StarPos"], [75.75, 48.75, 70.59])
        self.assertEqual(place["SystemAllegiance"], "Federation")
        self.assertEqual(C.last_place(os.path.join(self.dir.name, "missing")), {})

    def test_the_last_place_of_one_commander_skips_the_journals_of_others(self):
        write_journal(self.dir.name, "Journal.2026-10-14T100000.01.log",
                      [{"event": "Commander", "Name": "ALPHA"}, {"event": "Location", "StarSystem": "Alpha Home", "StarPos": [1, 2, 3]}], age=5000)
        write_journal(self.dir.name, "Journal.2026-10-15T100000.01.log",
                      [{"event": "Commander", "Name": "BRAVO"}, {"event": "LoadGame", "Commander": "BRAVO"}, {"event": "FSDJump", "StarSystem": "Bravo Far", "StarPos": [4, 5, 6]}])
        self.assertEqual(C.last_place(self.dir.name, cmdr="alpha")["StarSystem"], "Alpha Home")
        self.assertEqual(C.last_place(self.dir.name, cmdr="BRAVO")["StarSystem"], "Bravo Far")
        self.assertEqual(C.last_place(self.dir.name, cmdr="NOBODY"), {})
        self.assertEqual(C.last_place(self.dir.name)["StarSystem"], "Bravo Far")

    def test_from_journal_follows_the_commander_edmc_follows(self):
        write_journal(self.dir.name, "Journal.2026-10-14T100000.01.log",
                      [{"event": "Commander", "Name": "ALPHA"}, {"event": "Location", "StarSystem": "Alpha Home"}], age=5000)
        write_journal(self.dir.name, "Journal.2026-10-15T100000.01.log",
                      [{"event": "Commander", "Name": "BRAVO"}, {"event": "FSDJump", "StarSystem": "Bravo Far"}])
        with mock.patch.object(C, "edmc_commander", return_value="ALPHA"):
            self.assertEqual(C.from_journal(self.dir.name), "Alpha Home")
        with mock.patch.object(C, "edmc_commander", return_value="BRAVO"):
            self.assertEqual(C.from_journal(self.dir.name), "Bravo Far")

    def test_no_journals_is_blank(self):
        self.assertEqual(C.from_journal(self.dir.name), "")
        self.assertEqual(C.from_journal(os.path.join(self.dir.name, "missing")), "")

    def test_the_order_of_asking(self):
        with mock.patch.object(C, "from_monitor", return_value="Monitor"), mock.patch.object(C, "from_journal", return_value="Journal"):
            self.assertEqual(C.find("Tracked"), "Tracked")
            self.assertEqual(C.find(""), "Monitor")
        with mock.patch.object(C, "from_monitor", return_value=""), mock.patch.object(C, "from_journal", return_value="Journal"):
            self.assertEqual(C.find("  "), "Journal")

    def test_outside_edmc_the_monitor_knows_nothing(self):
        with mock.patch.dict(sys.modules, {"monitor": None}):
            self.assertEqual(C.from_monitor(), "")


if __name__ == "__main__":
    unittest.main()
