"""The Carrier Route planner's logic (plugin/carrier_route.py, carrier_route_state.py, carrier_route_spansh.py): the carrier's details from the journal, the request, the answer, and following
the route. No network: Spansh is replaced by a recorded answer (the first, a middle and the last entries of a live Sol to Colonia route, 2026-10-19)."""

import json
import os
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from plugin import carrier_route as CR, carrier_route_spansh, carrier_route_state, spansh_planners  # noqa: E402

RESULT = {"jumps": [
    {"distance": 0, "distance_to_destination": 22000.47, "fuel_in_tank": 1000, "fuel_used": 0, "has_icy_ring": False, "id64": 10477373803, "is_desired_destination": 1,
     "is_system_pristine": False, "must_restock": 1, "name": "Sol", "restock_amount": 3739, "tritium_in_market": 2739, "x": 0, "y": 0, "z": 0},
    {"distance": 499.96, "distance_to_destination": 21503.32, "fuel_in_tank": 1000, "fuel_used": 89, "has_icy_ring": False, "id64": 16061432997473, "is_desired_destination": 0,
     "is_system_pristine": False, "must_restock": 0, "name": "Col 359 Sector MB-A b16-7", "restock_amount": 0, "tritium_in_market": 2650, "x": -198.75, "y": 27.9375, "z": 457.90625},
    {"distance": 500.0, "distance_to_destination": 21003.0, "fuel_in_tank": 1000, "fuel_used": 89, "has_icy_ring": True, "id64": 99, "is_desired_destination": 0,
     "is_system_pristine": True, "must_restock": 0, "name": "IC 1287 Sector DB-X c1-18", "restock_amount": 0, "tritium_in_market": 2561, "x": 1, "y": 2, "z": 3},
    {"distance": 50.6, "distance_to_destination": 0, "fuel_in_tank": 0, "fuel_used": 13, "has_icy_ring": True, "id64": 3238296097059, "is_desired_destination": 1,
     "is_system_pristine": True, "must_restock": 0, "name": "Colonia", "restock_amount": 0, "tritium_in_market": 0, "x": -9530.5, "y": -910.28125, "z": 19808.125},
]}

STATS = {"event": "CarrierStats", "CarrierType": "FleetCarrier", "Callsign": "WLF-LXW", "Name": "ELDER WARDEN", "FuelLevel": 934,
         "SpaceUsage": {"TotalCapacity": 25000, "Crew": 1280, "Cargo": 389, "FreeSpace": 23331}}
HERE = {"event": "CarrierLocation", "CarrierType": "FleetCarrier", "CarrierID": 1, "StarSystem": "Khun", "SystemAddress": 3107241104074}


class TrackerTests(unittest.TestCase):
    def test_stats_and_location_fill_in_the_carrier(self) -> None:
        tracker = CR.CarrierTracker()
        self.assertTrue(tracker.handle_event(STATS, "Bocheaux"))
        self.assertTrue(tracker.handle_event(HERE, "Bocheaux"))
        info = tracker.info("Bocheaux")
        self.assertEqual((info.name, info.callsign, info.tritium, info.used_capacity, info.system, info.address), ("ELDER WARDEN", "WLF-LXW", 934, 1669, "Khun", 3107241104074))
        self.assertFalse(tracker.handle_event(HERE, "Bocheaux"), "the same news is not a change")
        self.assertEqual(tracker.kinds("Bocheaux"), [CR.FLEET])
        self.assertEqual(tracker.info("Someone Else").system, "", "another commander's carrier is not shared")

    def test_a_squadron_carrier_is_kept_apart(self) -> None:
        tracker = CR.CarrierTracker()
        tracker.handle_event(HERE, "Bocheaux")
        tracker.handle_event({**HERE, "CarrierType": "SquadronCarrier", "StarSystem": "Sol"}, "Bocheaux")
        self.assertEqual((tracker.info("Bocheaux", CR.FLEET).system, tracker.info("Bocheaux", CR.SQUADRON).system), ("Khun", "Sol"))
        self.assertEqual(tracker.kinds("Bocheaux"), [CR.FLEET, CR.SQUADRON])

    def test_a_jump_moves_our_carrier_but_a_visit_to_another_does_not(self) -> None:
        tracker = CR.CarrierTracker()
        tracker.handle_event(STATS, "Bocheaux")
        tracker.handle_event(HERE, "Bocheaux")
        self.assertTrue(tracker.handle_event({"event": "CarrierJump", "StarSystem": "Sol", "SystemAddress": 10477373803, "StationName": "wlf-lxw"}, "Bocheaux"))
        self.assertEqual(tracker.info("Bocheaux").system, "Sol")
        self.assertFalse(tracker.handle_event({"event": "Location", "StarSystem": "Colonia", "SystemAddress": 5, "StationName": "ABC-123"}, "Bocheaux"))
        self.assertEqual(tracker.info("Bocheaux").system, "Sol")

    def test_events_without_a_commander_are_ignored(self) -> None:
        self.assertFalse(CR.CarrierTracker().handle_event(STATS, ""))

    def test_recover_reads_only_the_commanders_own_stretches(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            lines = [{"event": "LoadGame", "Commander": "Other"}, {**STATS, "Name": "THEIRS"}, {"event": "LoadGame", "Commander": "Bocheaux"}, STATS, HERE]
            with open(os.path.join(folder, "Journal.2026-10-19T000000.01.log"), "w", encoding="utf-8") as handle:
                handle.write("\n".join(json.dumps(line) for line in lines) + "\n")
            tracker = CR.CarrierTracker()
            self.assertTrue(tracker.recover("Bocheaux", time.time() - 3600, folder))
            self.assertEqual((tracker.info("Bocheaux").name, tracker.info("Bocheaux").system), ("ELDER WARDEN", "Khun"))
            self.assertEqual(tracker.info("Other").name, "", "recovering for one commander does not fill in another")
            self.assertFalse(CR.CarrierTracker().recover("Bocheaux", time.time() - 3600, os.path.join(folder, "nowhere")))


class FormTests(unittest.TestCase):
    def test_a_fleet_carrier_form_with_the_fuel_worked_out(self) -> None:
        form = CR.build_form(CR.FLEET, 10477373803, [3238296097059], 5000)
        self.assertEqual(form, {"source": "10477373803", "destinations": ["3238296097059"], "capacity": "25000", "mass": "25000", "capacity_used": "5000", "calculate_starting_fuel": "1"})

    def test_a_squadron_carrier_and_known_tritium(self) -> None:
        form = CR.build_form(CR.SQUADRON, 1, [2, 3], 70000, work_out_fuel=False, tritium_in_tank=1500, tritium_in_market=300)
        self.assertEqual((form["capacity"], form["mass"], form["capacity_used"]), ("60000", "15000", "60000"))     # used space is held to the carrier's capacity
        self.assertEqual((form["calculate_starting_fuel"], form["fuel_loaded"], form["tritium_stored"], form["destinations"]), ("0", "1000", "300", ["2", "3"]))

    def test_restock_stops_must_be_destinations(self) -> None:
        form = CR.build_form(CR.FLEET, 1, [2, 3], 0, restock_ids=[3, 9])
        self.assertEqual(form["refuel_destinations"], ["3"])


class ResultTests(unittest.TestCase):
    def test_legs_leave_out_the_start_and_keep_the_tritium(self) -> None:
        legs = CR.legs_from_result(RESULT)
        self.assertEqual([leg.system for leg in legs], ["Col 359 Sector MB-A b16-7", "IC 1287 Sector DB-X c1-18", "Colonia"])
        self.assertEqual((legs[0].number, legs[0].distance, legs[0].tritium_left, legs[0].tritium_used, legs[0].market), (1, 499.96, 1000.0, 89.0, 2650.0))
        self.assertEqual(CR.notes_for(legs[1]), "icy ring (pristine)")
        self.assertEqual(CR.notes_for(legs[2]), "your stop, icy ring (pristine)")
        self.assertEqual(legs[2].id64, 3238296097059)

    def test_what_is_needed_at_the_start(self) -> None:
        self.assertEqual(CR.start_needs(RESULT), "Have 3,739 t of tritium at the start (1,000 in the tank, 2,739 in the carrier's market).")
        self.assertEqual(CR.start_needs({"jumps": [{"must_restock": 0, "name": "x"}]}), "")
        self.assertEqual(CR.start_needs(None), "")

    def test_damaged_answers_give_no_legs(self) -> None:
        for bad in (None, [], {}, {"jumps": "x"}, {"jumps": [None, {"name": 3}, {"name": " ", "distance": 5}, {"name": "A"}]}):
            self.assertEqual(CR.legs_from_result(bad), [])

    def test_a_mid_route_restock_is_named(self) -> None:
        leg = CR.legs_from_result({"jumps": [{"name": "A", "distance": 400, "must_restock": 1, "restock_amount": 700}]})[0]
        self.assertEqual(CR.notes_for(leg), "restock tritium (700 t)")


class FollowTests(unittest.TestCase):
    def route(self) -> CR.CarrierRoute:
        return CR.CarrierRoute(CR.FLEET, "Sol", "Colonia", CR.legs_from_result(RESULT), 0, CR.start_needs(RESULT))

    def test_arriving_moves_the_route_on_and_skipped_systems_count_as_done(self) -> None:
        route = self.route()
        self.assertEqual(route.next_leg.system, "Col 359 Sector MB-A b16-7")
        self.assertTrue(route.arrive("  ic 1287  sector DB-X c1-18 "))          # case and spacing do not matter; the first is passed over
        self.assertEqual((route.reached, route.next_leg.system, route.jumps_left), (2, "Colonia", 1))
        self.assertFalse(route.arrive("Sol"), "a system behind us changes nothing")
        self.assertFalse(route.arrive(""))
        route.arrive("Colonia")
        self.assertIsNone(route.next_leg)
        self.assertTrue(route.summary().endswith("Arrived."))

    def test_summary_and_copy_all(self) -> None:
        route = self.route()
        self.assertIn("3 jumps", route.summary())
        self.assertIn("Have 3,739 t", route.summary())
        self.assertEqual(route.copy_all().splitlines(), ["Col 359 Sector MB-A b16-7", "IC 1287 Sector DB-X c1-18", "Colonia"])
        route.arrive("Col 359 Sector MB-A b16-7")
        self.assertNotIn("Have 3,739 t", route.summary(), "the start needs are said only before the first jump")
        self.assertEqual(len(route.copy_all().splitlines()), 2)


class StateTests(unittest.TestCase):
    def test_a_route_round_trips_and_a_damaged_one_is_dropped(self) -> None:
        route = CR.CarrierRoute(CR.SQUADRON, "Sol", "Colonia", CR.legs_from_result(RESULT), 2, "x")
        back = carrier_route_state.from_payload(json.loads(json.dumps(carrier_route_state.to_payload(route))))
        self.assertEqual((back.kind, back.start, back.end, back.reached, back.needs, back.legs), (CR.SQUADRON, "Sol", "Colonia", 2, "x", route.legs))
        self.assertEqual(carrier_route_state.to_payload(None), {"route": None})
        payload = carrier_route_state.to_payload(route)
        payload["route"]["legs"][1] = {"system": ""}
        self.assertIsNone(carrier_route_state.from_payload(payload))
        self.assertIsNone(carrier_route_state.from_payload({"route": {"legs": []}}))

    def test_the_store_keeps_one_route_per_commander(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store = carrier_route_state.RouteStore()
            store.load(folder)
            route = CR.CarrierRoute(CR.FLEET, "Sol", "Colonia", CR.legs_from_result(RESULT))
            store.put("Bocheaux", route)
            again = carrier_route_state.RouteStore()
            again.load(folder)
            self.assertEqual(again.get("Bocheaux").legs, route.legs)
            self.assertIsNone(again.get("Someone Else"))
            store.put("Bocheaux", None)
            again.load(folder)
            self.assertIsNone(again.get("Bocheaux"))


class SpanshTests(unittest.TestCase):
    def test_plot_looks_the_systems_up_and_posts_the_form(self) -> None:
        looked = []

        def lookup(name):
            looked.append(name)
            return {"sol": (10477373803, "Sol"), "colonia": (3238296097059, "Colonia")}[name.casefold()]

        sent = {}

        def job(url, form, cancel=None, on_state=None, slow_hint=""):
            sent.update(url=url, form=form)
            return RESULT

        with mock.patch.object(carrier_route_spansh.spansh_exact, "lookup_system", lookup), mock.patch.object(spansh_planners, "fetch_job", job):
            route = carrier_route_spansh.plot(CR.FLEET, "sol", ["colonia"], 5000)
            self.assertEqual(looked, ["sol", "colonia"])
            self.assertEqual(sent["url"], "https://spansh.co.uk/api/fleetcarrier/route")
            self.assertEqual((sent["form"]["source"], sent["form"]["destinations"]), ("10477373803", ["3238296097059"]))
            self.assertEqual((route.start, route.end, len(route.legs), route.needs[:8]), ("Sol", "Colonia", 3, "Have 3,7"))
            looked.clear()
            carrier_route_spansh.plot(CR.FLEET, "Sol", ["Colonia"], 5000, start_id=10477373803)
            self.assertEqual(looked, ["Colonia"], "a known start address saves a lookup")

    def test_plot_needs_a_destination(self) -> None:
        with self.assertRaises(carrier_route_spansh.RouteSearchError):
            carrier_route_spansh.plot(CR.FLEET, "Sol", [" "], 0, start_id=1)
        with self.assertRaises(carrier_route_spansh.RouteSearchError):
            carrier_route_spansh.plot(CR.FLEET, "Sol", ["a"] * 11, 0, start_id=1)

    def test_a_list_in_the_form_is_sent_as_repeated_fields(self) -> None:
        seen = {}
        answers = iter([{"job": "J"}, {"state": "completed", "status": "ok", "result": RESULT}])

        def request(url, data=None, cancel=None):
            if data is not None:
                seen["data"] = data.decode("utf-8")
            return next(answers)

        with mock.patch.object(spansh_planners, "_request", request), mock.patch.object(spansh_planners, "POLL_INTERVAL_S", 0):
            spansh_planners.fetch_job("u", {"source": "1", "destinations": ["2", "3"]})
        self.assertEqual(seen["data"], "source=1&destinations=2&destinations=3")


if __name__ == "__main__":
    unittest.main()
