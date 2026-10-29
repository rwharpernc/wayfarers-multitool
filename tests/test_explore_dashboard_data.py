"""The Exploration Dashboard's data layer (explore_dashboard_data.py): the numbers, tables and fields it works out from the survey, the exobiology view, Status.json and
the expedition run. No Tk and no EDMC; a stand-in config module stops the imports that read it."""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default)
    sys.modules["config"] = _stub

from plugin import expedition_log, organic_scan  # noqa: E402
from plugin import explore_dashboard_data as D  # noqa: E402
from plugin.system_survey import Body, SystemSurvey  # noqa: E402


def build_survey() -> SystemSurvey:
    survey = SystemSurvey()
    survey.handle_event({"event": "FSDJump", "StarSystem": "Test Sys", "SystemAddress": 42})
    survey.handle_event({"event": "FSSDiscoveryScan", "BodyCount": 5, "Progress": 0.6})
    survey.handle_event({"event": "Scan", "BodyID": 0, "BodyName": "Test Sys", "StarSystem": "Test Sys", "StarType": "G", "StellarMass": 1.0,
                         "DistanceFromArrivalLS": 0.0, "WasDiscovered": True})
    survey.handle_event({"event": "Scan", "BodyID": 1, "BodyName": "Test Sys 1", "StarSystem": "Test Sys", "PlanetClass": "Earthlike body", "MassEM": 1.0,
                         "TerraformState": "", "Landable": False, "WasDiscovered": False, "WasMapped": False, "DistanceFromArrivalLS": 250.0,
                         "SurfaceGravity": 9.80665, "SurfaceTemperature": 288.0, "SurfacePressure": 101325.0, "Atmosphere": "a thick Oxygen atmosphere",
                         "AtmosphereComposition": [{"Name": "Nitrogen", "Percent": 77.0}, {"Name": "Oxygen", "Percent": 21.0}], "Volcanism": ""})
    survey.handle_event({"event": "Scan", "BodyID": 2, "BodyName": "Test Sys 2", "StarSystem": "Test Sys", "PlanetClass": "Rocky body", "MassEM": 0.05,
                         "Landable": True, "WasDiscovered": True, "WasMapped": True, "WasFootfalled": False, "DistanceFromArrivalLS": 900.0,
                         "SurfaceGravity": 3.0, "SurfaceTemperature": 150.0, "Atmosphere": "", "Volcanism": "minor silicate vapour geysers volcanism",
                         "Materials": [{"Name": "iron", "Percent": 19.2}, {"Name": "nickel", "Percent": 14.5}]})
    survey.handle_event({"event": "FSSBodySignals", "BodyID": 2, "BodyName": "Test Sys 2", "Signals": [{"Type": "$SAA_SignalType_Biological;", "Count": 2},
                                                                                                        {"Type": "$SAA_SignalType_Geological;", "Count": 1}]})
    return survey


class FormatTests(unittest.TestCase):
    def test_unknown_numbers_are_dashes(self):
        self.assertEqual((D.num(None), D.credits(None), D.credits(0), D.meters(None), D.light_seconds(None)), (D.DASH,) * 5)

    def test_units(self):
        self.assertEqual(D.num(1234.5, 1, " ly"), "1,234.5 ly")
        self.assertEqual((D.meters(850), D.meters(2400)), ("850 m", "2.4 km"))
        self.assertEqual((D.light_seconds(250), D.light_seconds(0.4)), ("250 ls", "0.4 ls"))
        self.assertEqual(D.percent_text(60), "60%")


class PerspectiveTests(unittest.TestCase):
    def test_landed_or_out_of_the_ship_is_the_ground(self):
        self.assertEqual(D.perspective({"Flags": 1 << 1}), D.GROUND)                       # landed
        self.assertEqual(D.perspective({"Flags": 0x4000000}), D.GROUND)                    # in the SRV
        self.assertEqual(D.perspective({"Flags": 0, "Flags2": 1}), D.GROUND)               # on foot

    def test_flying_docked_or_unknown_is_orbit(self):
        self.assertEqual(D.perspective({"Flags": 0x1000000}), D.ORBIT)                     # in the main ship
        self.assertEqual(D.perspective({"Flags": 1}), D.ORBIT)                             # docked
        self.assertEqual(D.perspective({}), D.ORBIT)

    def test_you_fields_say_where_you_are(self):
        survey = build_survey()
        rows = dict(D.you_fields({"Flags": 1 << 1 | 0x1000000, "BodyName": "Test Sys 2", "Altitude": 0.0, "Latitude": 12.5, "Longitude": -40.25, "Heading": 90,
                                  "Fuel": {"FuelMain": 12.5, "FuelReservoir": 0.5}}, survey))
        self.assertEqual(rows["Now"], "Landed")
        self.assertEqual(rows["Near"], "2")                      # the short name inside the system
        self.assertEqual(rows["Position"], "12.5000, -40.2500")
        self.assertEqual(rows["Heading"], "90 degrees")
        self.assertIn("12.5 t main", rows["Fuel"])

    def test_no_status_yet(self):
        self.assertEqual(D.you_fields({})[0][0], "Status")


class SystemTests(unittest.TestCase):
    def test_no_system_gives_one_muted_tile(self):
        tiles = D.overview_tiles(SystemSurvey(), 100_000, "scan")
        self.assertEqual((len(tiles), tiles[0].role), (1, D.MUTED))
        self.assertEqual(D.system_fields(SystemSurvey())[0][0], "System")

    def test_tiles_count_the_system(self):
        survey = build_survey()
        tiles = {tile.caption: tile for tile in D.overview_tiles(survey, 0, "scan")}
        self.assertEqual(tiles["bodies scanned"].value, "3/5")
        self.assertEqual(tiles["planets mapped"].value, "0")                                # mapped means mapped by this commander
        self.assertEqual(tiles["first discoveries here"].value, "1")
        self.assertEqual(tiles["biological signals analyzed"].value, "0/2")

    def test_panel_summary_leaves_out_the_scanned_count(self):
        from plugin import explore_dashboard
        text = explore_dashboard.summary_text(build_survey(), 0, "scan")
        self.assertTrue(text.startswith("Test Sys"))
        self.assertNotIn("scanned", text)                  # the Exploration Value readout beneath it already says it

    def test_an_expedition_adds_a_tile(self):
        run = expedition_log.Run(id="r", name="Trip")
        run.totals.explore_earned = 2_000_000
        tiles = D.overview_tiles(build_survey(), 0, "scan", run)
        self.assertEqual(tiles[-1].caption, "earned this expedition")
        self.assertEqual(tiles[-1].value, "2.0M")

    def test_system_fields(self):
        rows = dict(D.system_fields(build_survey(), "System bodies: 3 scanned of 5"))
        self.assertIn("5 bodies, 60% of the system scanned", rows["Honk"])
        self.assertEqual(rows["Biology"], "1 bodies with life signals")
        self.assertEqual(rows["Panel readout"], "System bodies: 3 scanned of 5")
        self.assertIn("1 landable bodies nobody has landed on", rows["First footfall"])

    def test_totals(self):
        sums = D.totals(build_survey())
        self.assertEqual((sums["first_discoveries"], sums["landable"], sums["bio_bodies"], sums["geo_bodies"], sums["first_footfalls"]), (1, 1, 1, 1, 1))
        self.assertGreater(sums["scan_value"], 0)
        self.assertGreaterEqual(sums["mapped_value"], sums["scan_value"] - sum(b.scan_value() for b in build_survey().bodies.values() if b.kind == "star"))


class BodiesTests(unittest.TestCase):
    def test_the_table_lists_every_body_nearest_first(self):
        table = D.bodies_table(build_survey(), 0, "scan")
        self.assertEqual([row.cells[0] for row in table.rows], ["Star", "1", "2"])
        self.assertEqual(len(table.rows[0].cells), len(D.BODY_COLUMNS))

    def test_a_row_describes_the_body(self):
        rows = {row.key: row for row in D.bodies_table(build_survey(), 0, "scan").rows}
        earth = rows["1"].cells
        self.assertEqual((earth[1], earth[2]), ("Earthlike body", "ELW"))
        self.assertEqual(earth[3:5], ["250 ls", "1.00 g"])
        self.assertIn("first discovery", earth[-1])
        rock = rows["2"].cells
        self.assertEqual((rock[5], rock[10], rock[11]), ("yes", "2", "1"))
        self.assertIn("first footfall", rock[-1])

    def test_rows_are_tagged_by_what_to_do(self):
        tags = {row.key: row.tag for row in D.bodies_table(build_survey(), 0, "scan").rows}
        self.assertEqual(tags["2"], "life")          # unfinished biology
        self.assertEqual(tags["1"], "map")           # a planet worth mapping at threshold 0
        done = Body(9, "Done", "9", kind="planet", scanned=True, mapped=True)
        self.assertEqual(D.body_tag(done, 0, "scan"), "done")

    def test_sections_for_one_body(self):
        survey = build_survey()
        sections = dict(D.body_sections(survey.bodies[1]))
        self.assertEqual(dict(sections["Body"])["Type"], "Earthlike body")
        gases = dict(sections["Atmosphere and volcanism"])
        self.assertEqual((gases["Nitrogen"], gases["Oxygen"]), ("77.0%", "21.0%"))
        rock = dict(D.body_sections(survey.bodies[2]))
        self.assertEqual(rock["Materials"][0][0], "iron")            # most abundant first
        self.assertIn("2 biological, 1 geological", dict(rock["Value and progress"])["Signals"])

    def test_a_star_has_no_atmosphere_block(self):
        self.assertNotIn("Atmosphere and volcanism", dict(D.body_sections(build_survey().bodies[0])))

    def test_nothing_selected(self):
        self.assertEqual(D.body_sections(None)[0][0], "Body")


class ListTests(unittest.TestCase):
    def test_map_table_lists_unmapped_planets_worth_it(self):
        survey = build_survey()
        names = [row.cells[0] for row in D.map_table(survey, 0, "scan").rows]
        self.assertEqual(names[0], "1")                                     # most valuable first
        self.assertIn("2", names)
        survey.bodies[2].mapped = True                                      # mapped by the commander: off the list
        self.assertEqual([row.cells[0] for row in D.map_table(survey, 0, "scan").rows], ["1"])
        self.assertEqual(D.map_table(survey, 500_000_000, "scan").rows, [])    # nothing is worth that much
        self.assertEqual(D.map_table(SystemSurvey(), 0, "scan").empty, "Scan some bodies first.")

    def test_life_table_lists_unfinished_biology(self):
        table = D.life_table(build_survey())
        self.assertEqual([row.cells[0] for row in table.rows], ["2"])
        self.assertIn("first footfall", table.rows[0].cells[-1])

    def test_sites_table_without_spansh_explains_how(self):
        self.assertIn("Spansh", D.sites_table(build_survey()).empty)


def genus(key="aleoida", stage=0, species=None, value=None, candidates=(("Aleoida Arcus", 7_252_500), ("Aleoida Coronamus", 6_284_600)), distance=None):
    return organic_scan.GenusView(key, key.title(), 150.0, tuple(candidates), species=species, value=value, stage=stage, distance_m=distance)


class ExobiologyTests(unittest.TestCase):
    def test_a_named_genus_shows_its_candidates_with_even_odds(self):
        row = D.genus_row(genus())
        self.assertEqual(row.cells[0], "Aleoida")
        self.assertIn("Aleoida Arcus 7.3M (50%)", row.cells[4])
        self.assertEqual(row.cells[2], "Collecting: 0/3")
        self.assertIn(" to ", row.cells[3])

    def test_a_confirmed_species_shows_it_and_its_progress(self):
        row = D.genus_row(genus(stage=2, species="Aleoida Arcus", value=7_252_500, distance=100.0))
        self.assertEqual((row.cells[2], row.cells[4], row.tag), ("Collecting: 2/3", "confirmed", "life"))
        self.assertEqual(row.cells[5], "100 m of 150 m")

    def test_progress_reads_collecting_x_of_three_until_analyzed(self):
        for stage, text in ((0, "Collecting: 0/3"), (1, "Collecting: 1/3"), (2, "Collecting: 2/3")):
            self.assertEqual(D.genus_row(genus(stage=stage)).cells[2], text)
        self.assertEqual(D.genus_row(genus(stage=3, species="Aleoida Arcus", value=7_252_500)).cells[2], "Analyzed: 3/3")

    def test_the_tracked_table_calls_them_specimens(self):
        table = D.waypoint_table(None)
        self.assertEqual(table.columns[0][1], "Specimen")
        self.assertIn("specimens", table.empty)

    def test_analyzed_rows_are_done(self):
        self.assertEqual(D.genus_row(genus(stage=3, species="Aleoida Arcus", value=7_252_500)).tag, "done")

    def test_first_footfall_multiplies_every_figure(self):
        row = D.genus_row(genus(species="Aleoida Arcus", value=1_000_000), multiplier=5)
        self.assertEqual(row.cells[3], "5.0M")

    def test_exobiology_fields(self):
        view = organic_scan.BodyView("Test Sys 2", (genus(stage=1, species="Aleoida Arcus", value=7_252_500, distance=40.0), genus("bacterium", 3, "Bacterium Alcyoneum", 1_658_500)),
                                     first_footfall=True, signal_count=2, active="aleoida")
        rows = dict(D.exo_fields(view))
        self.assertEqual(rows["Analyzed"], "1 of 2")
        self.assertIn("5x", rows["First footfall"])
        self.assertEqual(rows["Next sample"], "walk 110 m further from the last one")
        self.assertIn("Aleoida", rows["Sampling now"])

    def test_no_view_means_no_biology(self):
        self.assertEqual(D.exo_fields(None)[0][0], "Exobiology")
        self.assertIn("No biology", D.genus_table(None).empty)

    def test_bearing_and_direction(self):
        self.assertAlmostEqual(D.bearing_deg(0, 0, 1, 0), 0.0, places=3)           # north
        self.assertAlmostEqual(D.bearing_deg(0, 0, 0, 1), 90.0, places=3)          # east
        self.assertEqual(D.direction_text(5), "ahead")
        self.assertEqual(D.direction_text(180), "behind")
        self.assertEqual(D.direction_text(90), "90 degrees right")
        self.assertEqual(D.direction_text(-45), "45 degrees left")
        self.assertEqual(D.direction_text(350), "ahead")                           # wraps

    def test_waypoints_are_listed_with_distance_and_direction(self):
        point = organic_scan.Waypoint("aleoida", "Aleoida Arcus - Green", 0.0, 0.1, "foot")
        view = organic_scan.BodyView("B", (), here=(0.0, 0.0), heading=90.0, radius_m=1_000_000.0, waypoints=(point,))
        table = D.waypoint_table(view)
        self.assertEqual(len(table.rows), 1)
        self.assertEqual(table.rows[0].cells[2], "ahead")                          # due east while facing east
        self.assertTrue(table.rows[0].cells[1].endswith("km"))

    def test_an_inexact_waypoint_has_a_tilde(self):
        point = organic_scan.Waypoint("aleoida", "A", 0.0, 0.001, "ship")
        view = organic_scan.BodyView("B", (), here=(0.0, 0.0), heading=0.0, radius_m=1_000_000.0, waypoints=(point,))
        self.assertTrue(D.waypoint_table(view).rows[0].cells[1].startswith("~"))

    def test_no_position_no_waypoints(self):
        self.assertEqual(D.waypoint_table(organic_scan.BodyView("B", ())).rows, [])
        self.assertEqual(D.vehicle_fields(None), [])

    def test_vehicles(self):
        view = organic_scan.BodyView("B", (), here=(0.0, 0.0), radius_m=1_000_000.0, ship=(0.0, 0.001), srv=None)
        self.assertEqual([label for label, _ in D.vehicle_fields(view)], ["Ship"])


class ExplorationTests(unittest.TestCase):
    def test_no_expedition(self):
        self.assertIn("none running", D.expedition_fields(None)[0][1])

    def test_a_running_expedition(self):
        run = expedition_log.Run(id="r", name="Colonia run", started="2026-10-18T10:00:00Z", start_system="Sol")
        run.totals.jumps, run.totals.light_years, run.totals.bio_earned, run.totals.explore_earned = 120, 21_500.4, 3_000_000, 1_000_000
        run.systems = ["Sol", "A", "B"]
        rows = dict(D.expedition_fields(run))
        self.assertEqual((rows["Expedition"], rows["Jumps"], rows["Systems"], rows["Distance"]), ("Colonia run", "120", "3", "21,500 ly"))
        self.assertIn("4.0M", rows["Earned"])

    def test_route_and_readouts(self):
        self.assertEqual(D.route_fields([]), [("Route", "no route plotted")])
        self.assertEqual(D.route_fields([("12 jumps left", "title")]), [("", "12 jumps left")])
        self.assertEqual(len(D.readout_fields("a", "b")), 2)
        self.assertEqual(D.readout_fields("", ""), [])


if __name__ == "__main__":
    unittest.main()
