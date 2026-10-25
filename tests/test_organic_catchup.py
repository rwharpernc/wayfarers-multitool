"""Organic Scanning catches up from the journals for samples taken while EDMC was closed (organic_catchup.py), and the tracker never lowers live progress.

The case that prompted it: Cactoida was logged, sampled and analyzed, the last two scans made with EDMC closed; the survey (rebuilt from the journals) knew it was
analyzed while the Bio status card and the Dashboard still said 2/3.
"""
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

GENUS = "$Codex_Ent_Cactoid_Genus_Name;"
SPECIES = "$Codex_Ent_Cactoid_01_Name;"
ADDRESS = 1676563468920498


def line(**fields):
    return json.dumps(fields)


class Fixture(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType("config")
        config.appname = "EDMarketConnector"
        config.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default, default_journal_dir="")
        patcher = mock.patch.dict(sys.modules, {"config": config, "myNotebook": types.ModuleType("myNotebook")})
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in [m for m in sys.modules if m.startswith("plugin.organic") or m in ("plugin.journal_files", "plugin.panelkit")]:
            sys.modules.pop(name)
        from plugin import organic_catchup, organic_scan
        self.catchup, self.scan = organic_catchup, organic_scan
        self.scan_module = organic_scan
        self.folder = tempfile.mkdtemp()
        self.addCleanup(lambda: [os.remove(os.path.join(self.folder, f)) for f in os.listdir(self.folder)] or os.rmdir(self.folder))

    def journal(self, lines, name="Journal.2026-10-18T090909.01.log"):
        with open(os.path.join(self.folder, name), "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")

    def organic(self, scan_type, body=5, stamp="2026-10-18T15:04:48Z", address=ADDRESS):
        return line(timestamp=stamp, event="ScanOrganic", ScanType=scan_type, Genus=GENUS, Species=SPECIES, Species_Localised="Cactoida Cortexum",
                    Variant_Localised="Cactoida Cortexum - Teal", Body=body, SystemAddress=address)

    def header(self):
        return [line(event="Commander", Name="Test Cmdr"),
                line(event="FSDJump", StarSystem="Myriesly YZ-N c20-6099", SystemAddress=ADDRESS),
                line(event="ApproachBody", Body="Myriesly YZ-N c20-6099 4 a", BodyID=5, StarSystem="Myriesly YZ-N c20-6099", SystemAddress=ADDRESS)]


class ReadTests(Fixture):
    def read(self, cmdr="Test Cmdr"):
        return self.catchup.read_since(cmdr, time.time() - 86400, self.folder).samples

    def test_a_scan_is_given_the_name_of_its_body_from_the_events_that_name_it(self):
        self.journal(self.header() + [self.organic("Log"), self.organic("Sample"), self.organic("Analyse")])
        samples = self.read()
        self.assertEqual([s["scan_type"] for s in samples], ["Log", "Sample", "Analyse"])
        self.assertEqual({(s["system"], s["body"]) for s in samples}, {("Myriesly YZ-N c20-6099", "Myriesly YZ-N c20-6099 4 a")})

    def test_a_scan_of_a_body_that_cannot_be_named_is_skipped(self):
        self.journal(self.header() + [self.organic("Log", body=9)])
        self.assertEqual(self.read(), [])

    def test_only_the_named_commanders_scans_are_read(self):
        self.journal(self.header() + [self.organic("Log")])
        self.assertEqual(self.read("Someone Else"), [])

    def test_a_scan_in_another_system_with_the_same_body_number_is_not_confused(self):
        self.journal(self.header() + [self.organic("Log", address=999)])
        self.assertEqual(self.read(), [])


class BodyRecoveryTests(Fixture):
    def body_scan(self, **extra):
        return line(timestamp="2026-10-18T15:00:00Z", event="Scan", BodyName="Myriesly YZ-N c20-6099 4 a", BodyID=5, SystemAddress=ADDRESS,
                    PlanetClass="Rocky body", AtmosphereType="CarbonDioxide", SurfaceGravity=4.9, SurfaceTemperature=190.0, SurfacePressure=10132.5,
                    Volcanism="", WasFootfalled=False, Materials=[{"Name": "iron", "Percent": 20.0}], **extra)

    def read_all(self):
        return self.catchup.read_since("Test Cmdr", time.time() - 86400, self.folder)

    def test_conditions_footfall_and_genus_hints_are_recovered_for_a_body_scanned_with_edmc_closed(self):
        star = line(timestamp="2026-10-18T14:59:00Z", event="Scan", BodyName="Myriesly YZ-N c20-6099", BodyID=0, SystemAddress=ADDRESS, StarType="G")
        signals = line(timestamp="2026-10-18T15:01:00Z", event="SAASignalsFound", BodyName="Myriesly YZ-N c20-6099 4 a", BodyID=5, SystemAddress=ADDRESS,
                       Genuses=[{"Genus": GENUS}])
        jump = line(event="FSDJump", StarSystem="Myriesly YZ-N c20-6099", SystemAddress=ADDRESS, StarPos=[1.0, 2.0, 3.0])
        self.journal([line(event="Commander", Name="Test Cmdr"), jump, star, self.body_scan(), signals])
        found = self.read_all().bodies["Myriesly YZ-N c20-6099|Myriesly YZ-N c20-6099 4 a"]
        self.assertEqual(found["genus_hints"], [GENUS])
        self.assertTrue(found["first_footfall"])                                   # nobody had been there
        conditions = found["conditions"]
        self.assertEqual((conditions["planet_class"], conditions["atmosphere"], conditions["star_type"]), ("Rocky body", "CarbonDioxide", "G"))
        self.assertEqual(tuple(conditions["galactic_position"]), (1.0, 2.0, 3.0))
        self.assertNotIn("system_body_types", conditions)

    def test_a_star_is_not_a_body_with_conditions(self):
        star = line(timestamp="2026-10-18T14:59:00Z", event="Scan", BodyName="Star", BodyID=0, SystemAddress=ADDRESS, StarType="G")
        self.journal([line(event="Commander", Name="Test Cmdr"), line(event="FSDJump", StarSystem="S", SystemAddress=ADDRESS), star])
        self.assertEqual(self.read_all().bodies, {})

    def test_merge_bodies_adds_only_what_is_missing_and_never_overwrites_the_live_save(self):
        persisted = {"S|B": {"conditions": {"planet_class": "Live"}}}
        bodies = {"S|B": {"conditions": {"planet_class": "Journal"}, "genus_hints": [GENUS], "first_footfall": True}, "S|C": {"genus_hints": [GENUS]}}
        changed = self.catchup.merge_bodies(persisted, bodies)
        self.assertEqual(changed, {"S|B", "S|C"})
        self.assertEqual(persisted["S|B"]["conditions"], {"planet_class": "Live"})
        self.assertEqual((persisted["S|B"]["genus_hints"], persisted["S|B"]["first_footfall"]), ([GENUS], True))
        self.assertEqual(self.catchup.merge_bodies(persisted, bodies), set())             # a second pass adds nothing

    def test_the_live_and_journal_conditions_builders_agree(self):
        entry = json.loads(self.body_scan())
        cond = self.scan_module.conditions_from_scan(entry, "G", "Myriesly YZ-N c20-6099", (1.0, 2.0, 3.0))
        self.assertEqual((cond.planet_class, cond.star_type, cond.system_name), ("Rocky body", "G", "Myriesly YZ-N c20-6099"))
        self.assertAlmostEqual(cond.gravity_g, 4.9 / 9.80665, places=3)
        self.assertEqual(cond.materials, ("iron",))
        self.assertIsNone(self.scan_module.conditions_from_scan({"BodyName": "x"}, None, None, None))


class MergeTests(Fixture):
    def sample(self, scan_type):
        return {"system": "Sys", "body": "Sys 1", "genus": GENUS, "species": SPECIES, "species_name": "Cactoida Cortexum", "variant": "Cactoida Cortexum - Teal",
                "scan_type": scan_type, "timestamp": None}

    def test_a_missed_analyse_completes_the_species_and_keeps_the_saved_positions(self):
        persisted = {"Sys|Sys 1": {"organisms": {GENUS: {"species_key": SPECIES, "species_name": "Cactoida Cortexum", "value": 1, "stage": 2,
                                                         "last_lat": 1.0, "last_lon": 2.0, "variant_name": None, "positions": [[1.0, 2.0], [1.1, 2.1]]}}}}
        changed = self.catchup.merge(persisted, [self.sample("Log"), self.sample("Sample"), self.sample("Analyse")])
        saved = persisted["Sys|Sys 1"]["organisms"][GENUS]
        self.assertEqual(changed, {"Sys|Sys 1"})
        self.assertEqual((saved["stage"], saved["positions"], saved["variant_name"]), (3, [[1.0, 2.0], [1.1, 2.1]], "Cactoida Cortexum - Teal"))
        self.assertGreater(saved["value"], 1)                              # the value comes from the species data

    def test_it_never_lowers_a_stage_and_a_second_pass_changes_nothing(self):
        persisted = {}
        self.catchup.merge(persisted, [self.sample("Analyse")])
        self.assertEqual(self.catchup.merge(persisted, [self.sample("Log"), self.sample("Sample"), self.sample("Analyse")]), set())
        self.assertEqual(persisted["Sys|Sys 1"]["organisms"][GENUS]["stage"], 3)

    def test_a_body_not_saved_before_is_added(self):
        persisted = {}
        self.assertEqual(self.catchup.merge(persisted, [self.sample("Log")]), {"Sys|Sys 1"})
        self.assertEqual(persisted["Sys|Sys 1"]["organisms"][GENUS]["stage"], 1)


class TrackerTests(Fixture):
    def test_restoring_an_older_saved_stage_does_not_undo_live_progress(self):
        tracker = self.scan.OrganicTracker()
        tracker.record_scan(GENUS, SPECIES, "Cactoida Cortexum", "Analyse", None, None)
        tracker.restore_organism(GENUS, SPECIES, "Cactoida Cortexum", 1, 2, None, None)
        self.assertEqual(tracker.organisms[0].stage if hasattr(tracker, "organisms") else tracker._organisms[GENUS].stage, 3)

    def test_restoring_over_a_detected_only_genus_still_applies(self):
        tracker = self.scan.OrganicTracker()
        tracker.note_genus_detected(GENUS)
        tracker.restore_organism(GENUS, SPECIES, "Cactoida Cortexum", 1, 2, None, None)
        self.assertEqual(tracker._organisms[GENUS].stage, 2)


if __name__ == "__main__":
    unittest.main()
