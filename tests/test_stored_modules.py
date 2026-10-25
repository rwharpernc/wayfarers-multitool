"""Stored modules: the Module Storage events kept as a per-commander list (stored_modules.py) and the tab that shows it (ship_modules_tab.py).

The events here are synthetic, with the field shapes the game writes. Run with: python -m unittest discover -s tests
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import stored_modules as S  # noqa: E402

CMDR = "Test Pilot"


def item(name, slot=1, system="Alpha", market=100, cost=100, seconds=60, hot=False, **extra):
    entry = {"Name": f"${name}_name;", "Name_Localised": name.replace("_", " ").title(), "StorageSlot": slot, "StarSystem": system, "MarketID": market,
             "TransferCost": cost, "TransferTime": seconds, "BuyPrice": 0, "Hot": hot}
    entry.update(extra)
    return entry


def snapshot(items, stamp="2026-10-20T10:00:00Z", market=100, station="Test Dock", system="Alpha"):
    return {"timestamp": stamp, "event": "StoredModules", "MarketID": market, "StationName": station, "StarSystem": system, "Items": items}


def store(name, stamp, market=100, hot=False, **extra):
    entry = {"timestamp": stamp, "event": "ModuleStore", "MarketID": market, "Slot": "Slot01_Size3", "StoredItem": f"${name}_name;",
             "StoredItem_Localised": name.title(), "Ship": "asp", "ShipID": 1, "Hot": hot}
    entry.update(extra)
    return entry


def retrieve(name, stamp, market=100, **extra):
    entry = {"timestamp": stamp, "event": "ModuleRetrieve", "MarketID": market, "Slot": "Slot01_Size3", "RetrievedItem": f"${name}_name;",
             "RetrievedItem_Localised": name.title(), "Ship": "asp", "ShipID": 1, "Hot": False}
    entry.update(extra)
    return entry


def new_book(folder=None):
    book = S.ModuleBook()
    book.load(folder or tempfile.mkdtemp())
    book._cmdr, book._catching = CMDR, False        # no journals to read: the book is live from the start
    return book


class NameTests(unittest.TestCase):
    def test_token_names_become_journal_items(self) -> None:
        self.assertEqual(S.normalize_item("$int_engine_size3_class5_name;"), "int_engine_size3_class5")
        self.assertEqual(S.normalize_item("$HPT_BeamLaser_Fixed_Small_Name;"), "hpt_beamlaser_fixed_small")
        self.assertEqual(S.normalize_item("int_engine_size3_class5"), "int_engine_size3_class5")
        self.assertEqual(S.normalize_item(None), "")

    def test_readable_name_falls_back_in_order(self) -> None:
        self.assertEqual(S.display_name("int_hyperdrive_overcharge_size4_class5", "FSD (SCO)"), "FSD (SCO)")
        self.assertEqual(S.display_name("int_engine_size3_class5"), "Thrusters")
        self.assertEqual(S.display_name("int_unknownthing_size1_class1"), "Int Unknownthing Size1 Class1")

    def test_rating_and_engineering_text(self) -> None:
        self.assertEqual(S.rating("int_engine_size3_class5"), "3A")
        self.assertEqual(S.rating("int_cargorack_size5_class1"), "5E")
        self.assertEqual(S.rating("hpt_beamlaser_gimbal_huge"), "Huge gimbal")
        self.assertEqual(S.rating("explorer_nx_armour_grade1_default"), "")
        self.assertEqual(S.engineering_text("int_hyperdrive_size5_class1", "FSD_LongRange", 5), "Increased FSD Range G5")
        self.assertEqual(S.engineering_text("int_cargorack_size5_class1", "", 0), "-")
        self.assertEqual(S.engineering_text("zzz", "Made_UpBlueprint", 2), "Up Blueprint G2")

    def test_transfer_time(self) -> None:
        self.assertEqual(S.transfer_time(232927), "2d 16h")
        self.assertEqual(S.transfer_time(12000), "3h 20m")
        self.assertEqual(S.transfer_time(2510), "41m")
        self.assertEqual(S.transfer_time(None), "-")


class SnapshotTests(unittest.TestCase):
    def test_snapshot_reads_engineered_in_transit_and_hot(self) -> None:
        items, asof = S.parse_snapshot(snapshot([
            item("int_cargorack_size5_class1", EngineerModifications="CargoRack_IncreasedCapacity", Level=5, Quality=1.0, hot=True),
            {"Name": "$int_hyperdrive_size5_class1_name;", "Name_Localised": "FSD", "StorageSlot": 600, "BuyPrice": 0, "Hot": False, "InTransit": True},
        ]))
        self.assertEqual([m["i"] for m in items], ["int_cargorack_size5_class1", "int_hyperdrive_size5_class1"])
        self.assertEqual((items[0]["e"], items[0]["l"], items[0]["h"], items[0]["c"], items[0]["t"], items[0]["m"]),
                         ("CargoRack_IncreasedCapacity", 5, True, 100, 60, 100))
        self.assertTrue(items[1]["x"])
        self.assertEqual((items[1]["s"], items[1]["m"], items[1]["c"]), ("", None, None))
        self.assertEqual(asof, {"t": "2026-10-20T10:00:00Z", "station": "Test Dock", "system": "Alpha", "market": 100})

    def test_second_snapshot_replaces_the_first(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5"), item("int_powerplant_size4_class5")]))
        book.handle(snapshot([item("int_sensors_size2_class1")], stamp="2026-10-21T10:00:00Z"))
        self.assertEqual([m["i"] for m in book.modules(CMDR)], ["int_sensors_size2_class1"])
        self.assertEqual(book.asof(CMDR)["t"], "2026-10-21T10:00:00Z")

    def test_cap_on_stored_items(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5", slot=n) for n in range(S.MAX_ITEMS + 500)]))
        self.assertEqual(len(book.modules(CMDR)), S.MAX_ITEMS)
        for number in range(5):
            book.handle(store("int_sensors_size2_class1", f"2026-10-20T10:00:0{number + 1}Z"))
        self.assertEqual(len(book.modules(CMDR)), S.MAX_ITEMS)

    def test_text_is_bounded(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5", system="S" * 500, Name_Localised="N" * 500, EngineerModifications="E" * 500, Level=1)],
                             station="T" * 500))
        module = book.modules(CMDR)[0]
        self.assertLessEqual(max(len(module["n"]), len(module["s"]), len(module["e"])), S.TEXT_CAP)
        self.assertLessEqual(len(book.asof(CMDR)["station"]), S.STATION_CAP)


class StoreRetrieveTests(unittest.TestCase):
    def test_module_store_adds_at_the_docked_station(self) -> None:
        book = new_book()
        book.handle({"event": "Docked", "timestamp": "2026-10-20T10:00:00Z", "MarketID": 200, "StationName": "Other Port", "StarSystem": "Beta"})
        book.handle(snapshot([item("int_engine_size3_class5")], stamp="2026-10-20T10:00:01Z"))
        book.handle(store("int_sensors_size2_class1", "2026-10-20T10:05:00Z", market=200, hot=True, EngineerModifications="Sensor_LightWeight", Level=3))
        added = [m for m in book.modules(CMDR) if m["i"] == "int_sensors_size2_class1"][0]
        self.assertEqual((added["s"], added["m"], added["h"], added["e"], added["l"]), ("Beta", 200, True, "Sensor_LightWeight", 3))
        self.assertEqual(book.where(CMDR, added), "Other Port (Beta)")

    def test_mass_module_store_adds_every_item(self) -> None:
        book = new_book()
        book.handle(snapshot([]))
        book.handle({"event": "MassModuleStore", "timestamp": "2026-10-20T10:05:00Z", "MarketID": 100, "Ship": "mandalay", "ShipID": 3, "Items": [
            {"Slot": "MediumHardpoint1", "Name": "$hpt_multicannon_turret_medium_name;", "Name_Localised": "Multi-Cannon", "Hot": False},
            {"Slot": "MediumHardpoint2", "Name": "$hpt_multicannon_turret_medium_name;", "Name_Localised": "Multi-Cannon", "Hot": False,
             "EngineerModifications": "Weapon_LongRange", "Level": 1, "Quality": 1.0}]})
        modules = book.modules(CMDR)
        self.assertEqual([(m["i"], m["e"], m["s"]) for m in modules],
                         [("hpt_multicannon_turret_medium", "", "Alpha"), ("hpt_multicannon_turret_medium", "Weapon_LongRange", "Alpha")])

    def test_retrieve_removes_the_matching_module_only(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5", slot=1, market=100), item("int_engine_size3_class5", slot=2, market=300, system="Gamma"),
                              item("int_engine_size3_class5", slot=3, market=100, EngineerModifications="Engine_Dirty", Level=2)]))
        book.handle(retrieve("int_engine_size3_class5", "2026-10-20T10:05:00Z", market=100, EngineerModifications="Engine_Dirty", Level=2))
        self.assertEqual([(m["m"], m["e"]) for m in book.modules(CMDR)], [(100, ""), (300, "")])
        book.handle(retrieve("int_engine_size3_class5", "2026-10-20T10:06:00Z", market=100))
        self.assertEqual([m["m"] for m in book.modules(CMDR)], [300])
        book.handle(retrieve("int_engine_size3_class5", "2026-10-20T10:07:00Z", market=100))     # one whose transfer has arrived
        self.assertEqual(book.modules(CMDR), [])

    def test_swapped_out_module_goes_into_storage_with_unknown_engineering(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5")]))
        book.handle(retrieve("int_engine_size3_class5", "2026-10-20T10:05:00Z", SwapOutItem="$int_sensors_size2_class1_name;", SwapOutItem_Localised="Sensors"))
        modules = book.modules(CMDR)
        self.assertEqual([m["i"] for m in modules], ["int_sensors_size2_class1"])
        self.assertEqual(S.engineering_of(modules[0]), "?")

    def test_events_before_any_snapshot_are_ignored(self) -> None:
        book = new_book()
        book.handle(store("int_sensors_size2_class1", "2026-10-20T10:05:00Z"))
        self.assertEqual(book.modules(CMDR), [])
        self.assertIn("Open Module Storage", book.freshness(CMDR))

    def test_an_event_applied_twice_counts_once(self) -> None:
        book = new_book()
        book.handle(snapshot([]))
        event = store("int_sensors_size2_class1", "2026-10-20T10:05:00Z")
        book.handle(event)
        book.handle(dict(event))
        book.handle(store("int_sensors_size2_class1", "2026-10-20T10:04:00Z"))                 # older than what was applied
        book.handle(store("int_sensors_size2_class1", "2026-10-20T10:05:00Z", Slot="Slot02"))  # same second, a different event
        self.assertEqual(len(book.modules(CMDR)), 2)


class StationNameTests(unittest.TestCase):
    def test_known_station_unknown_station_and_transit(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5", market=100), item("int_engine_size3_class5", system="Far Away", market=555),
                              {"Name": "$int_sensors_size2_class1_name;", "InTransit": True, "Hot": False}]))
        near, far, transit = book.modules(CMDR)
        self.assertEqual(book.where(CMDR, near), "Test Dock (Alpha)")
        self.assertEqual(book.where(CMDR, far), "Far Away (market 555)")
        self.assertEqual(book.where(CMDR, transit), "In transit")

    def test_station_names_are_bounded(self) -> None:
        book = new_book()
        for number in range(S.MAX_STATIONS + 50):
            stamp = f"2026-10-20T10:{number // 60:02d}:{number % 60:02d}Z"
            book.handle({"event": "Docked", "timestamp": stamp, "MarketID": number, "StationName": f"Port {number}", "StarSystem": "X"})
        self.assertEqual(len(book._payload(CMDR)["stations"]), S.MAX_STATIONS)


class FilterAndRowsTests(unittest.TestCase):
    def test_filter_matches_every_word_across_columns(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_hyperdrive_size5_class5", EngineerModifications="FSD_LongRange", Level=5, hot=True),
                              item("int_engine_size3_class5", system="Beta", market=7)]))
        self.assertEqual(book.rows(CMDR)[1], 2)
        self.assertEqual(book.rows(CMDR, "hyperdrive")[1], 1)
        self.assertEqual(book.rows(CMDR, "range g5 hot")[1], 1)
        self.assertEqual(book.rows(CMDR, "beta market")[1], 1)
        self.assertEqual(book.rows(CMDR, "zzz")[1], 0)
        self.assertEqual(book.rows(CMDR, "hyperdrive")[0][0],
                         ("Int Hyperdrive Size5 Class5", "5A", "Increased FSD Range G5", "Test Dock (Alpha)", "100 cr, 1m", "Hot"))

    def test_rows_are_limited_but_the_total_is_counted(self) -> None:
        book = new_book()
        book.handle(snapshot([item("int_engine_size3_class5", slot=n) for n in range(30)]))
        rows, total = book.rows(CMDR, limit=10)
        self.assertEqual((len(rows), total), (10, 30))


class PersistenceTests(unittest.TestCase):
    def test_round_trip_and_missing_file(self) -> None:
        folder = tempfile.mkdtemp()
        self.assertFalse(os.path.exists(os.path.join(folder, S.STATE_FILENAME)))
        book = new_book(folder)
        self.assertEqual(book.modules(CMDR), [])
        book.handle(snapshot([item("int_engine_size3_class5", EngineerModifications="Engine_Dirty", Level=4)]))
        with open(os.path.join(folder, S.STATE_FILENAME), encoding="utf-8") as handle:
            raw = handle.read()
        self.assertNotIn("\n", raw)                                   # compact
        self.assertFalse(os.path.exists(os.path.join(folder, S.STATE_FILENAME + ".tmp")))
        again = S.ModuleBook()
        again.load(folder)
        self.assertEqual(again.modules(CMDR), book.modules(CMDR))
        self.assertEqual(again.asof(CMDR), book.asof(CMDR))
        self.assertEqual(json.loads(raw)["version"], 2)

    def test_commanders_stay_separate(self) -> None:
        folder = tempfile.mkdtemp()
        book = new_book(folder)
        book.handle(snapshot([item("int_engine_size3_class5")]))
        book._cmdr = "Other Pilot"
        self.assertEqual(book.modules("Other Pilot"), [])
        self.assertIn("Open Module Storage", book.freshness("Other Pilot"))
        book.handle(snapshot([item("int_sensors_size2_class1"), item("int_sensors_size2_class1", slot=2)], stamp="2026-10-20T11:00:00Z"))
        again = S.ModuleBook()
        again.load(folder)
        self.assertEqual([m["i"] for m in again.modules(CMDR)], ["int_engine_size3_class5"])
        self.assertEqual(len(again.modules("OTHER PILOT")), 2)           # the name is matched without regard to case


class CatchUpTests(unittest.TestCase):
    @staticmethod
    def _journal(folder, name, lines, mtime):
        path = os.path.join(folder, name)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            for line in lines:
                handle.write(json.dumps(line) + "\n")
        os.utime(path, (mtime, mtime))

    def test_newest_snapshot_and_the_events_after_it(self) -> None:
        journals, data = tempfile.mkdtemp(), tempfile.mkdtemp()
        load = {"timestamp": "2026-10-01T10:00:00Z", "event": "LoadGame", "Commander": CMDR}
        self._journal(journals, "Journal.2026-10-01T100000.01.log", [load, snapshot([item("int_powerplant_size4_class5")], stamp="2026-10-01T10:01:00Z")], 1000)
        self._journal(journals, "Journal.2026-10-02T100000.01.log", [
            load, snapshot([item("int_engine_size3_class5"), item("int_engine_size3_class5", slot=2)], stamp="2026-10-02T10:01:00Z"),
            store("int_sensors_size2_class1", "2026-10-02T10:02:00Z"), retrieve("int_engine_size3_class5", "2026-10-02T10:03:00Z")], 2000)
        self._journal(journals, "Journal.2026-10-03T100000.01.log", [
            {"timestamp": "2026-10-03T10:00:00Z", "event": "LoadGame", "Commander": "Someone Else"},
            snapshot([item("int_lifesupport_size1_class1")], stamp="2026-10-03T10:01:00Z")], 3000)
        book = S.ModuleBook()
        book.load(data)
        book.set_commander(CMDR, journals, wait=True)
        self.assertEqual(sorted(m["i"] for m in book.modules(CMDR)), ["int_engine_size3_class5", "int_sensors_size2_class1"])
        # a later start reads what is new, and an event that the journal and EDMC both report counts once
        again = S.ModuleBook()
        again.load(data)
        again.set_commander(CMDR, journals, wait=True)
        again.handle(retrieve("int_engine_size3_class5", "2026-10-02T10:03:00Z"))
        self.assertEqual(sorted(m["i"] for m in again.modules(CMDR)), ["int_engine_size3_class5", "int_sensors_size2_class1"])

    def test_live_events_wait_for_the_catch_up(self) -> None:
        book = S.ModuleBook()
        book.load(tempfile.mkdtemp())
        book._cmdr, book._catching = CMDR, True
        book.handle(snapshot([item("int_engine_size3_class5")]))
        self.assertEqual(book.modules(CMDR), [])
        book._catch_up(CMDR, tempfile.mkdtemp())
        self.assertEqual(len(book.modules(CMDR)), 1)


def planned(item, blueprint, level=5):
    from plugin import ship_plan
    return ship_plan.plan_module({"Slot": "S", "Item": item, "Engineering": {"BlueprintName": blueprint, "Level": level, "Quality": 1.0, "EngineerID": 300000}})


def held(item, blueprint="", level=0, partial=False):
    return S._module(item, "", False, blueprint, level, "Alpha", 100, partial=partial)


class PlanMatchTests(unittest.TestCase):
    FSD = "int_hyperdrive_size5_class5"

    def test_the_same_blueprint_at_the_level_or_above_is_a_full_match(self):
        found = S.match_plan([planned(self.FSD, "FSD_LongRange", 5)], [held(self.FSD, "FSD_LongRange", 5)], lambda m: "Test Dock")
        self.assertEqual((found[0].kind, found[0].short), (S.FULL, "Yes"))
        self.assertIn("Test Dock", found[0].detail)

    def test_other_engineering_is_a_partial_match_and_says_what_the_build_has(self):
        for stored in (held(self.FSD), held(self.FSD, "FSD_FastBoot", 5), held(self.FSD, "FSD_LongRange", 3), held(self.FSD, partial=True)):
            found = S.match_plan([planned(self.FSD, "FSD_LongRange", 5)], [stored])
            self.assertEqual((found[0].kind, found[0].short), (S.PARTIAL, "Partly"), stored)
            self.assertIn("the build has", found[0].detail)

    def test_a_different_module_does_not_match(self):
        found = S.match_plan([planned(self.FSD, "FSD_LongRange", 5)], [held("int_hyperdrive_size4_class5", "FSD_LongRange", 5)])
        self.assertEqual(found, [S.NO_MATCH])

    def test_one_stored_module_serves_one_planned_module_and_full_matches_go_first(self):
        wanted = [planned(self.FSD, "FSD_LongRange", 5), planned(self.FSD, "FSD_LongRange", 5)]
        found = S.match_plan(wanted, [held(self.FSD, "FSD_LongRange", 5)])
        self.assertEqual([m.kind for m in found], [S.FULL, ""])
        found = S.match_plan(wanted, [held(self.FSD), held(self.FSD, "FSD_LongRange", 5)])
        self.assertEqual([m.kind for m in found], [S.FULL, S.PARTIAL])

    def test_a_lower_level_of_the_same_blueprint_is_offered_before_none(self):
        found = S.match_plan([planned(self.FSD, "FSD_LongRange", 5)], [held(self.FSD), held(self.FSD, "FSD_LongRange", 2)])
        self.assertIn("G2", found[0].detail)


class TabSmokeTests(unittest.TestCase):
    def test_tab_shows_the_list_and_the_explanation(self) -> None:
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stored_modules_tab_smoke.py")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
        if result.returncode == 77:
            self.skipTest("Tk has no display here")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("STORED MODULES TAB OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
