"""The Route Planner's saved route (route_planner_state.py): written per commander, read back whole, and ignored when damaged. No Tk, no network."""
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
    _stub.config = types.SimpleNamespace(get_str=lambda key, default="": default)
    _stub.user_agent = "WFMT-test"
    _stub.appversion = lambda: "5.13.0"
    sys.modules["config"] = _stub

from plugin import route_planner as NP, route_planner_state as S  # noqa: E402


def sample(reached=1):
    legs = NP.legs_from_result({"jumps": [
        {"name": "Sol", "distance": 0, "distance_to_destination": 300.0},
        {"name": "Alpha Neutron", "distance": 120.5, "distance_to_destination": 179.5, "fuel_in_tank": 218.0, "fuel_used": 6.0, "has_neutron": True, "x": 1, "y": 2, "z": 3, "is_scoopable": True},
        {"name": "Beta", "distance": 99.5, "distance_to_destination": 80.0, "fuel_in_tank": 212.0, "fuel_used": 6.0, "must_refuel": True, "must_inject": 1},
        {"name": "Gamma", "distance": 80.0, "distance_to_destination": 0.0, "fuel_in_tank": 206.0, "fuel_used": 6.0, "has_neutron": True}]})
    return NP.Route("Sol", "Colonia", legs, reached, white_dwarf_check="done")


class RoundTripTests(unittest.TestCase):
    def test_a_route_comes_back_whole(self):
        route = sample(reached=2)
        back = S.from_payload(json.loads(json.dumps(S.to_payload(route))))
        self.assertEqual(back.start, "Sol")
        self.assertEqual(back.end, "Colonia")
        self.assertEqual(back.reached, 2)
        self.assertEqual(back.white_dwarf_check, "done")
        self.assertEqual(back.legs, route.legs)                     # every field of every leg, positions included
        self.assertEqual(back.next_leg.system, "Gamma")

    def test_no_route_saves_as_none(self):
        self.assertEqual(S.to_payload(None), {"route": None})
        self.assertEqual(S.to_payload(NP.Route("A", "B", [])), {"route": None})
        self.assertIsNone(S.from_payload({"route": None}))

    def test_damaged_routes_are_dropped(self):
        good = S.to_payload(sample())
        for bad in (None, 5, {}, {"route": 3}, {"route": {"legs": "x"}}, {"route": {"legs": []}}):
            self.assertIsNone(S.from_payload(bad))
        broken = json.loads(json.dumps(good))
        broken["route"]["legs"][1] = {"system": ""}
        self.assertIsNone(S.from_payload(broken), "one bad leg drops the route rather than showing half of it")
        wild = json.loads(json.dumps(good))
        wild["route"]["reached"] = 99
        self.assertEqual(S.from_payload(wild).reached, len(wild["route"]["legs"]))
        wild["route"]["reached"] = "soon"
        self.assertEqual(S.from_payload(wild).reached, 0)

    def test_a_huge_route_is_not_saved(self):
        legs = [NP.Leg(i, f"S{i}", 1, 1.0, 1.0, False) for i in range(S.MAX_LEGS + 1)]
        self.assertEqual(S.to_payload(NP.Route("A", "B", legs)), {"route": None})


class StoreTests(unittest.TestCase):
    def test_each_commander_keeps_their_own_route(self):
        with tempfile.TemporaryDirectory() as folder:
            store = S.RouteStore()
            store.load(folder)
            store.put("Bocheaux", sample(reached=1))
            self.assertIsNone(store.get("Someone Else"), "another commander has no route")
            other = S.RouteStore()
            other.load(folder)                                     # a restart
            self.assertEqual(other.get("BOCHEAUX").reached, 1, "found again, whatever the case of the name")
            other.put("Someone Else", None)
            self.assertIsNotNone(other.get("bocheaux"), "clearing one commander's route leaves the other's")
            other.put("Bocheaux", None)
            self.assertIsNone(other.get("Bocheaux"))

    def test_the_file_never_holds_a_commander_in_its_name(self):
        with tempfile.TemporaryDirectory() as folder:
            store = S.RouteStore()
            store.load(folder)
            store.put("Bocheaux", sample())
            self.assertEqual(os.listdir(folder), [S.STATE_FILENAME])

    def test_a_missing_or_broken_file_is_just_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            store = S.RouteStore()
            store.load(folder)
            self.assertIsNone(store.get("Bocheaux"))
            with open(os.path.join(folder, S.STATE_FILENAME), "w", encoding="utf-8") as handle:
                handle.write("{not json")
            store.load(folder)
            self.assertIsNone(store.get("Bocheaux"))

    def test_nothing_is_written_before_the_commander_is_known(self):
        with tempfile.TemporaryDirectory() as folder:
            store = S.RouteStore()
            store.load(folder)
            store.put("", sample())
            self.assertEqual(os.listdir(folder), [])


if __name__ == "__main__":
    unittest.main()
