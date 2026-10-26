"""
The ship's hold read from the game's Cargo.json (journal_files.read_cargo_file): the current figure even when EDMC's own
cargo state has not followed a purchase, and None whenever the caller should keep what EDMC reports.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import colonization, journal_files  # noqa: E402


class ReadCargoFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, text: str) -> None:
        with open(os.path.join(self.dir.name, "Cargo.json"), "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_reads_the_inventory_by_name(self) -> None:
        self.write(json.dumps({"event": "Cargo", "Vessel": "Ship", "Count": 1265, "Inventory": [
            {"Name": "cmmcomposite", "Name_Localised": "CMM Composite", "Count": 1237, "Stolen": 0},
            {"Name": "polymers", "Count": 28, "Stolen": 0}]}))
        hold = journal_files.read_cargo_file(self.dir.name)
        self.assertEqual(hold, {"cmmcomposite": 1237, "polymers": 28})
        self.assertEqual(colonization.cargo_by_key(hold), {"cmmcomposite": 1237, "polymers": 28})

    def test_an_empty_hold_is_empty_not_unknown(self) -> None:
        self.write('{ "event":"Cargo", "Vessel":"Ship", "Count":0, "Inventory":[  ] }')
        self.assertEqual(journal_files.read_cargo_file(self.dir.name), {})
        self.write('{ "event":"Cargo", "Vessel":"Ship", "Count":0 }')
        self.assertEqual(journal_files.read_cargo_file(self.dir.name), {})

    def test_the_same_commodity_twice_is_added_up(self) -> None:
        self.write(json.dumps({"Vessel": "Ship", "Inventory": [{"Name": "steel", "Count": 10}, {"Name": "steel", "Count": 5, "MissionID": 7}]}))
        self.assertEqual(journal_files.read_cargo_file(self.dir.name), {"steel": 15})

    def test_unusable_files_give_none_so_edmcs_figure_is_kept(self) -> None:
        self.assertIsNone(journal_files.read_cargo_file(self.dir.name))                 # no file
        self.write('{ "event":"Cargo", "Vess')                                           # half-written
        self.assertIsNone(journal_files.read_cargo_file(self.dir.name))
        self.write('[1, 2]')
        self.assertIsNone(journal_files.read_cargo_file(self.dir.name))
        self.write(json.dumps({"Vessel": "SRV", "Inventory": [{"Name": "steel", "Count": 3}]}))
        self.assertIsNone(journal_files.read_cargo_file(self.dir.name))                 # the SRV's hold is not the ship's
        self.assertIsNone(journal_files.read_cargo_file(""))                            # no journal folder known

    def test_bad_entries_are_skipped(self) -> None:
        self.write(json.dumps({"Vessel": "Ship", "Inventory": [
            "junk", {"Count": 4}, {"Name": "water", "Count": "x"}, {"Name": "gold", "Count": 0}, {"Name": "tin", "Count": 2}]}))
        self.assertEqual(journal_files.read_cargo_file(self.dir.name), {"tin": 2})


if __name__ == "__main__":
    unittest.main()
