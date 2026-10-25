"""The Route Planner's logic (route_planner.py, fsd_data.py): the ship's numbers from the journal, the request Spansh's exact plotter takes, its route as legs you can follow,
and the Spansh client (spansh_exact.py) with the network replaced. No Tk, no real network; a stand-in config module stops the imports that read it."""
from __future__ import annotations

import os
import sys
import threading
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key, default="": default)
    _stub.user_agent = "WFMT-test"
    _stub.appversion = lambda: "5.13.0"
    sys.modules["config"] = _stub

from plugin import fsd_data, route_planner as NP, spansh_exact  # noqa: E402
from plugin.trade_spansh_client import RouteSearchError  # noqa: E402

SCO_ITEM = "int_hyperdrive_overcharge_size8_class5_overchargebooster_mkii"
LOADOUT = {"event": "Loadout", "Ship": "explorer_nx", "Ship_Localised": "Caspian Explorer", "ShipName": "Stellar Mantis", "ShipIdent": "MA-X7N",
           "UnladenMass": 1532.099976, "MaxJumpRange": 53.4283, "FuelCapacity": {"Main": 224.0, "Reserve": 1.14}, "CargoCapacity": 32,
           "Modules": [{"Slot": "Armour", "Item": "x"},
                       {"Slot": "FrameShiftDrive", "Item": SCO_ITEM, "Engineering": {"Modifiers": [
                           {"Label": "Mass", "Value": 192.0, "OriginalValue": 160.0}, {"Label": "FSDOptimalMass", "Value": 6304.5, "OriginalValue": 4670.0}]}}]}


def loadout(**changes):
    entry = dict(LOADOUT)
    entry.update(changes)
    return entry


def drive_only(item, engineering=None, **changes):
    module = {"Slot": "FrameShiftDrive", "Item": item}
    if engineering:
        module["Engineering"] = engineering
    return loadout(Modules=[module], **changes)


EXACT = {"jumps": [
    {"name": "Sol", "id64": 1, "distance": 0, "distance_to_destination": 400.0, "fuel_in_tank": 224, "fuel_used": 0, "has_neutron": False, "must_refuel": False, "x": 0, "y": 0, "z": 0},
    {"name": "Neutron One", "id64": 2, "distance": 120.5, "distance_to_destination": 279.5, "fuel_in_tank": 218.5, "fuel_used": 5.5, "has_neutron": True, "must_refuel": False,
     "must_inject": 0, "is_scoopable": False, "x": 1.5, "y": 2, "z": 3},
    {"name": "Plain Star", "id": 3, "id64": 3, "distance": 90.0, "distance_to_destination": 189.5, "fuel_in_tank": 213.0, "fuel_used": 5.5, "has_neutron": False, "must_refuel": True,
     "is_scoopable": True},
    {"name": "Neutron Two", "id64": 4, "distance": 110.0, "distance_to_destination": 79.5, "fuel_in_tank": 224.0, "fuel_used": 3.0, "has_neutron": True, "must_inject": 1},
    {"name": "Colonia", "id64": 5, "distance": 79.5, "distance_to_destination": 0, "fuel_in_tank": 220.0, "fuel_used": 4.0, "has_neutron": False},
    {"name": "", "distance": 5}, {"nonsense": True}, "junk"]}


class DriveTableTests(unittest.TestCase):
    def test_every_drive_is_a_real_hyperdrive_item(self):
        self.assertEqual(len(fsd_data.FSD), 66)
        for item, values in fsd_data.FSD.items():
            self.assertTrue(NP._DRIVE.match(item), item)
            self.assertEqual(len(values), 4)
            self.assertTrue(all(v > 0 for v in values), item)

    def test_the_mk_ii_overcharge_drive_is_in_with_its_own_constants(self):
        self.assertEqual(fsd_data.FSD[SCO_ITEM], (4670, 6.8, 0.011, 2.5025))
        self.assertEqual(fsd_data.SUPERCHARGE[SCO_ITEM], 6)

    def test_a_standard_class_5_a_drive(self):
        self.assertEqual(fsd_data.FSD["int_hyperdrive_size5_class5"], (1050, 5, 0.012, 2.45))

    def test_the_guardian_booster_ranges(self):
        self.assertEqual(fsd_data.GUARDIAN_BOOST, {1: 4, 2: 6, 3: 7.75, 4: 9.25, 5: 10.5})


class ParamsTests(unittest.TestCase):
    def test_the_engineered_sco_drive_matches_what_spansh_page_sends(self):
        params = NP.params_from_loadout(LOADOUT)
        self.assertEqual((params.optimal_mass, params.max_fuel_per_jump, params.fuel_multiplier, params.fuel_power), (6304.5, 6.8, 0.011, 2.5025))
        self.assertEqual((params.tank_size, params.internal_tank_size), (224.0, 1.14))
        self.assertAlmostEqual(params.base_mass, 1532.099976 + 1.14)
        self.assertEqual((params.supercharge_multiplier, params.injection_multiplier, params.range_boost), (6, 2, None))
        self.assertEqual((params.size, params.rating), (8, "A"))

    def test_an_unengineered_drive_uses_the_base_values(self):
        params = NP.params_from_loadout(drive_only("int_hyperdrive_size5_class5"))
        self.assertEqual((params.optimal_mass, params.max_fuel_per_jump, params.supercharge_multiplier, params.rating), (1050, 5, 4, "A"))

    def test_engineering_modifiers_replace_optimal_mass_and_max_fuel(self):
        mods = {"Modifiers": [{"Label": "FSDOptimalMass", "Value": 1500.5}, {"Label": "MaxFuelPerJump", "Value": 6.25}, {"Label": "Mass", "Value": 99}]}
        params = NP.params_from_loadout(drive_only("int_hyperdrive_size5_class5", mods))
        self.assertEqual((params.optimal_mass, params.max_fuel_per_jump), (1500.5, 6.25))

    def test_a_non_mk_ii_overcharge_drive_supercharges_at_four(self):
        self.assertEqual(NP.params_from_loadout(drive_only("int_hyperdrive_overcharge_size8_class5")).supercharge_multiplier, 4)

    def test_a_guardian_booster_adds_its_range(self):
        modules = [{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_size5_class5"}, {"Slot": "Slot04", "Item": "int_guardianfsdbooster_size4"}]
        self.assertEqual(NP.params_from_loadout(loadout(Modules=modules)).range_boost, 9.25)

    def test_missing_pieces_are_said_not_guessed(self):
        with self.assertRaisesRegex(NP.PlotterError, "no frame shift drive"):
            NP.params_from_loadout(loadout(Modules=[{"Slot": "Armour", "Item": "x"}]))
        with self.assertRaisesRegex(NP.PlotterError, "does not know this frame shift drive"):
            NP.params_from_loadout(drive_only("int_hyperdrive_size9_class9"))
        with self.assertRaisesRegex(NP.PlotterError, "mass and fuel tank"):
            NP.params_from_loadout(drive_only("int_hyperdrive_size5_class5", UnladenMass=None))
        with self.assertRaisesRegex(NP.PlotterError, "mass and fuel tank"):
            NP.params_from_loadout(drive_only("int_hyperdrive_size5_class5", FuelCapacity={"Reserve": 1.0}))
        with self.assertRaises(NP.PlotterError):
            NP.params_from_loadout({"Modules": "nonsense"})

    def test_a_missing_reserve_is_zero(self):
        params = NP.params_from_loadout(drive_only("int_hyperdrive_size5_class5", FuelCapacity={"Main": 32.0}))
        self.assertEqual((params.internal_tank_size, params.base_mass), (0.0, 1532.099976))


class ShipInfoTests(unittest.TestCase):
    def ship(self):
        info = NP.ShipInfo()
        info.apply_loadout(LOADOUT)
        return info

    def test_the_block_reads_like_exploration_buddys_dialog(self):
        rows = dict(self.ship().describe())
        self.assertEqual(rows["Ship"], "Stellar Mantis (MA-X7N)")
        self.assertEqual(rows["Frame shift drive"], "Class 8, Rating A")
        self.assertEqual(rows["FSD booster"], "No")
        self.assertEqual(rows["FSD optimal mass"], "6,304.5 t")
        self.assertEqual(rows["Supercharge"], "Yes (6x)")
        self.assertEqual(rows["Cargo"], "0 t")

    def test_a_booster_is_named_with_its_range(self):
        info = NP.ShipInfo()
        info.apply_loadout(loadout(Modules=[{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_size5_class5"}, {"Item": "int_guardianfsdbooster_size5"}]))
        self.assertEqual(dict(info.describe())["FSD booster"], "Guardian, +10.5 ly")

    def test_a_ship_without_a_custom_name_shows_its_type(self):
        info = NP.ShipInfo()
        info.apply_loadout(loadout(ShipName="", ShipIdent=""))
        self.assertEqual(dict(info.describe())["Ship"], "Caspian Explorer")

    def test_nothing_known_yet(self):
        info = NP.ShipInfo()
        self.assertIn("not known yet", dict(info.describe())["Ship"])
        with self.assertRaisesRegex(NP.PlotterError, "not known yet"):
            info.params()

    def test_a_loadout_the_plotter_cannot_use_shows_the_problem(self):
        info = NP.ShipInfo()
        info.apply_loadout(drive_only("int_hyperdrive_size9_class9"))
        self.assertIn("does not know this frame shift drive", dict(info.describe())["Problem"])

    def test_a_repeat_loadout_changes_nothing(self):
        info = self.ship()
        self.assertFalse(info.apply_loadout(dict(LOADOUT)))
        self.assertTrue(info.apply_loadout(loadout(Ship="anaconda")))

    def test_only_the_cargo_is_read_from_status(self):
        info = self.ship()
        before = info.describe()
        self.assertFalse(info.apply_status({"Fuel": {"FuelMain": 12.0}, "Flags": 5}))      # fuel moves every jump and must change nothing here
        self.assertEqual(info.describe(), before)
        self.assertTrue(info.apply_status({"Cargo": 48}))
        self.assertEqual(dict(info.describe())["Cargo"], "48 t")
        self.assertFalse(info.apply_status({"Cargo": 48}))

    def test_the_block_never_names_a_jump_range(self):
        text = " ".join(f"{a} {b}" for a, b in self.ship().describe()).lower()
        self.assertNotIn("jump range", text)


class FormTests(unittest.TestCase):
    def form(self, options=None, cargo=0.0, params=None):
        return NP.build_form(params or NP.params_from_loadout(LOADOUT), cargo, options or NP.Options(), 271555405828955, 3238296097059)

    def test_the_form_has_the_fields_spansh_page_sends(self):
        form = self.form()
        self.assertEqual(form, {
            "source": "271555405828955", "destination": "3238296097059", "is_supercharged": "0", "use_supercharge": "1", "use_injections": "0",
            "use_injections_when_required": "0", "exclude_secondary": "0", "refuel_every_scoopable": "0", "fuel_power": "2.5025", "fuel_multiplier": "0.011",
            "optimal_mass": "6304.5", "base_mass": "1533.239976", "tank_size": "224", "internal_tank_size": "1.14", "reserve_size": "0", "max_fuel_per_jump": "6.8",
            "max_time": "60", "cargo": "0", "algorithm": "optimistic", "supercharge_multiplier": "6", "injection_multiplier": "2"})

    def test_the_options_are_passed_on(self):
        form = self.form(NP.Options(False, True, True, True, "guided"), cargo=47.6)
        self.assertEqual((form["use_supercharge"], form["use_injections"], form["exclude_secondary"], form["refuel_every_scoopable"], form["algorithm"], form["cargo"]),
                         ("0", "1", "1", "1", "guided", "48"))

    def test_an_unknown_algorithm_falls_back(self):
        self.assertEqual(self.form(NP.Options(algorithm="nonsense"))["algorithm"], "optimistic")

    def test_a_booster_is_sent_and_none_is_left_out(self):
        self.assertNotIn("range_boost", self.form())
        boosted = NP.params_from_loadout(loadout(Modules=[{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_size5_class5"}, {"Item": "int_guardianfsdbooster_size3"}]))
        self.assertEqual(self.form(params=boosted)["range_boost"], "7.75")

    def test_cargo_is_never_negative(self):
        self.assertEqual(self.form(cargo=-5)["cargo"], "0")

    def test_every_algorithm_in_the_list_is_accepted(self):
        for key, _label in NP.ALGORITHMS:
            self.assertEqual(self.form(NP.Options(algorithm=key))["algorithm"], key)


class LegTests(unittest.TestCase):
    def test_every_jump_after_the_start_is_a_leg(self):
        legs = NP.legs_from_result(EXACT)
        self.assertEqual([leg.system for leg in legs], ["Neutron One", "Plain Star", "Neutron Two", "Colonia"])
        self.assertEqual([leg.number for leg in legs], [1, 2, 3, 4])
        self.assertTrue(legs[0].neutron and not legs[1].neutron)
        self.assertEqual((legs[0].distance, legs[0].left, legs[0].fuel_left, legs[0].fuel_used), (120.5, 279.5, 218.5, 5.5))
        self.assertEqual(legs[0].xyz, (1.5, 2.0, 3.0))
        self.assertIsNone(legs[1].xyz)
        self.assertTrue(legs[1].refuel and legs[1].scoopable)
        self.assertTrue(legs[2].inject)

    def test_nothing_usable_gives_no_legs(self):
        for bad in (None, [], {"jumps": "x"}, {"jumps": []}, "text"):
            self.assertEqual(NP.legs_from_result(bad), [])

    def test_notes_say_what_to_do(self):
        legs = NP.legs_from_result(EXACT)
        self.assertEqual(NP.notes_for(legs[0]), "neutron: supercharge")
        self.assertEqual(NP.notes_for(legs[1]), "refuel")
        self.assertEqual(NP.notes_for(legs[2]), "neutron: supercharge, FSD injection")
        self.assertEqual(NP.notes_for(legs[3]), "")


class RouteTests(unittest.TestCase):
    def route(self):
        return NP.Route("Sol", "Colonia", NP.legs_from_result(EXACT))

    def test_totals(self):
        route = self.route()
        self.assertEqual((route.total_jumps, route.neutron_count), (4, 2))
        self.assertAlmostEqual(route.total_distance, 400.0)

    def test_arriving_moves_along_the_route(self):
        route = self.route()
        self.assertEqual(route.next_leg.system, "Neutron One")
        self.assertTrue(route.arrive("neutron one"))                    # case does not matter
        self.assertEqual((route.reached, route.next_leg.system, route.jumps_left), (1, "Plain Star", 3))
        self.assertFalse(route.arrive("Somewhere else"))
        self.assertFalse(route.arrive("Neutron One"))                   # already past it

    def test_skipping_ahead_counts_the_ones_passed(self):
        route = self.route()
        self.assertTrue(route.arrive("Colonia"))
        self.assertEqual((route.reached, route.next_leg, route.jumps_left), (4, None, 0))

    def test_distance_left_is_to_the_end(self):
        route = self.route()
        self.assertAlmostEqual(route.distance_left, 400.0)
        route.arrive("Neutron One")
        self.assertAlmostEqual(route.distance_left, 279.5)

    def test_the_next_supercharge_and_refuel(self):
        route = self.route()
        self.assertEqual(route.next_supercharge()[0], 1)
        self.assertEqual(route.next_refuel()[0], 2)
        route.arrive("Neutron One")
        self.assertEqual(route.next_supercharge()[0], 2)
        self.assertEqual(route.next_refuel()[0], 1)
        route.arrive("Neutron Two")
        self.assertIsNone(route.next_supercharge())
        self.assertIsNone(route.next_refuel())

    def test_the_summary_says_what_is_next(self):
        route = self.route()
        self.assertIn("4 jumps, 400 ly, 2 neutron stars. Next: Neutron One (neutron star), 4 jumps", route.summary())
        route.arrive("Colonia")
        self.assertTrue(route.summary().endswith("You have arrived."))
        self.assertEqual(NP.Route("a", "b").summary(), "No route.")

    def test_copy_all_lists_what_is_left(self):
        route = self.route()
        self.assertEqual(NP.copy_all(route), "Neutron One\nPlain Star\nNeutron Two\nColonia")
        route.arrive("Plain Star")
        self.assertEqual(NP.copy_all(route), "Neutron Two\nColonia")
        route.arrive("Colonia")
        self.assertEqual(NP.copy_all(route), "")


class SpanshClientTests(unittest.TestCase):
    def ship(self):
        info = NP.ShipInfo()
        info.apply_loadout(LOADOUT)
        info.apply_status({"Cargo": 12})
        return info

    def test_lookup_returns_the_id_and_spelling(self):
        reply = mock.MagicMock()
        reply.__enter__.return_value.read.return_value = b'{"min_max":[{"id64":1,"name":"Colonia Sister"},{"id64":3238296097059,"name":"Colonia"}]}'
        with mock.patch.object(spansh_exact.urllib.request, "urlopen", return_value=reply):
            self.assertEqual(spansh_exact.lookup_system("colonia"), (3238296097059, "Colonia"))

    def test_lookup_of_an_unknown_system_says_so(self):
        reply = mock.MagicMock()
        reply.__enter__.return_value.read.return_value = b'{"min_max":[],"values":[]}'
        with mock.patch.object(spansh_exact.urllib.request, "urlopen", return_value=reply):
            with self.assertRaisesRegex(RouteSearchError, "does not know a system called 'Nowhere'"):
                spansh_exact.lookup_system(" Nowhere ")
        with self.assertRaises(RouteSearchError):
            spansh_exact.lookup_system("  ")

    def test_plot_builds_the_form_and_returns_the_route(self):
        seen = {}

        def fake_job(url, form, cancel=None, on_state=None, slow_hint=""):
            seen.update(url=url, form=form)
            return EXACT

        with mock.patch.object(spansh_exact, "lookup_system", return_value=(5, "Colonia")), mock.patch.object(spansh_exact.spansh_planners, "fetch_job", fake_job):
            route = spansh_exact.plot(self.ship(), "Sol", "colonia", NP.Options(algorithm="fuel"), start_id=99)
        self.assertEqual(seen["url"], spansh_exact.ROUTE_URL)
        self.assertEqual((seen["form"]["source"], seen["form"]["destination"], seen["form"]["cargo"], seen["form"]["algorithm"]), ("99", "5", "12", "fuel"))
        self.assertEqual((route.start, route.end, len(route.legs)), ("Sol", "Colonia", 4))

    def test_plot_looks_the_start_up_when_the_game_gave_no_address(self):
        lookups = []

        def fake_lookup(name):
            lookups.append(name)
            return (len(lookups), name.title())

        with mock.patch.object(spansh_exact, "lookup_system", fake_lookup), mock.patch.object(spansh_exact.spansh_planners, "fetch_job", lambda *a, **k: EXACT):
            route = spansh_exact.plot(self.ship(), "sol", "colonia", NP.Options())
        self.assertEqual(lookups, ["sol", "colonia"])
        self.assertEqual((route.start, route.end), ("Sol", "Colonia"))

    def test_a_ship_spansh_cannot_be_told_about_stops_before_any_request(self):
        info = NP.ShipInfo()
        with mock.patch.object(spansh_exact, "lookup_system") as lookup:
            with self.assertRaises(NP.PlotterError):
                spansh_exact.plot(info, "Sol", "Colonia", NP.Options())
        lookup.assert_not_called()

    def test_the_job_is_polled_and_cancel_is_honored(self):
        from plugin import spansh_planners
        answers = iter([{"job": "J1", "status": "queued"}, {"state": "started"}, {"state": "completed", "status": "ok", "result": EXACT}])
        with mock.patch.object(spansh_planners, "_request", side_effect=lambda *a, **k: next(answers)), mock.patch.object(spansh_planners, "POLL_INTERVAL_S", 0):
            self.assertEqual(spansh_planners.fetch_job("u", {"a": "b"}, threading.Event()), EXACT)
        stop = threading.Event()
        stop.set()
        with mock.patch.object(spansh_planners, "_request", return_value={"job": "J2", "status": "queued"}):
            with self.assertRaisesRegex(RouteSearchError, "Cancelled"):
                spansh_planners.fetch_job("u", {}, stop)


class FuelScoopTests(unittest.TestCase):
    def test_a_fitted_scoop_is_found(self):
        ship = NP.ShipInfo()
        self.assertIsNone(ship.has_fuel_scoop())          # no loadout yet: not known
        ship.apply_loadout(loadout(Modules=LOADOUT["Modules"] + [{"Slot": "Slot05", "Item": "int_fuelscoop_size6_class5"}]))
        self.assertTrue(ship.has_fuel_scoop())

    def test_no_scoop_is_reported_in_the_ship_block(self):
        ship = NP.ShipInfo()
        ship.apply_loadout(LOADOUT)
        self.assertFalse(ship.has_fuel_scoop())
        self.assertIn("NONE FITTED", dict(ship.describe())["Fuel scoop"])


class WhiteDwarfTests(unittest.TestCase):
    def test_white_dwarfs_are_marked_from_edsm_star_types(self):
        legs = NP.legs_from_result(EXACT)
        marked = NP.mark_white_dwarfs(legs, {"plain star": "White Dwarf (DA) Star", "neutron one": "White Dwarf (DB) Star", "colonia": "G (White-Yellow) Star"})
        self.assertEqual([leg.white_dwarf for leg in marked], [False, True, False, False])     # the start is not a leg; a neutron star is never also marked
        self.assertEqual(marked[0].boost, True)
        self.assertEqual(NP.notes_for(marked[1]), "white dwarf: supercharge, refuel")

    def test_the_route_counts_and_finds_the_next_boost(self):
        route = NP.Route("Sol", "Colonia", NP.mark_white_dwarfs(NP.legs_from_result(EXACT), {"plain star": "White Dwarf (DA) Star"}), white_dwarf_check="done")
        self.assertEqual(route.white_dwarf_count, 1)
        self.assertIn("1 white dwarfs", route.summary())
        route.reached = 1
        self.assertEqual(route.next_supercharge()[1].system, "Plain Star")

    def test_nothing_is_asked_of_edsm_unless_the_option_is_on(self):
        with mock.patch.object(spansh_exact, "lookup_system", side_effect=[(1, "Sol"), (5, "Colonia")]),                 mock.patch.object(spansh_exact.spansh_planners, "fetch_job", return_value=EXACT):
            ship = NP.ShipInfo()
            ship.apply_loadout(LOADOUT)
            route = spansh_exact.plot(ship, "Sol", "Colonia", NP.Options())
        self.assertEqual(route.white_dwarf_check, "")
        self.assertFalse(any(leg.white_dwarf for leg in route.legs))


if __name__ == "__main__":
    unittest.main()
