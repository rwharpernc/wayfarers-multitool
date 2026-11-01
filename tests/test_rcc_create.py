"""
Starting a Raven Colonial project (rcc_create.py): the request bodies, the validation, and the order of the calls with a stand-in
for the network, including that a failed optional step never undoes the project.
"""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import rcc_client, rcc_create as C  # noqa: E402
from plugin.colonization import Resource, Site  # noqa: E402

PLAN = [
    {"id": "x1", "name": "Pennington Claim", "bodyNum": 4, "buildType": "no_truss", "status": "plan"},
    {"id": "x2", "name": "Built Already", "bodyNum": 5, "buildType": "hermes", "status": "complete", "buildId": "b2", "marketId": 9},
    {"id": "x3", "name": "Has Project", "bodyNum": 6, "buildType": "vulcan", "status": "plan", "buildId": "b3"},
]


def site() -> Site:
    return Site(market_id=3700000001, name="$EXT_PANEL_ColonisationShip; Pennington Claim", system="Synuefe NI-R c21-10",
                resources=[Resource("steel", "Steel", 6660, 100, 0), Resource("water", "Water", 741, 0, 0)], progress=0.01)


def request(**changes) -> C.Request:
    fields = dict(site=site(), cmdr="Tiber Caelvox", key="k", system="Synuefe NI-R c21-10", system_address=1234, star_pos=(1.0, 2.0, 3.0),
                  name="Pennington Claim", build_type="no_truss", body_num=4)
    fields.update(changes)
    return C.Request(**fields)


class Recorder:
    def __init__(self, fail=()):
        self.calls, self.fail = [], fail

    def __call__(self, method, path, body, key, cmdr=""):
        self.calls.append((method, path, body))
        for marker in self.fail:
            if marker in path:
                raise rcc_client.RccError("nope")
        return {"buildId": "newbuild"} if path == "/api/project" else None


class PrimaryPort(unittest.TestCase):
    def test_a_built_or_started_station_in_the_plan_means_the_primary_port_exists(self):
        sites = rcc_client.parse_sites(PLAN)
        self.assertIn("2 stations", C.primary_port_note(sites, site()))
        only_planned = rcc_client.parse_sites([PLAN[0]])
        self.assertEqual(C.primary_port_note(only_planned, site()), "")
        self.assertEqual(C.primary_port_note([], site()), "")

    def test_a_project_alone_counts_even_when_its_site_is_still_planned(self):
        self.assertIn("1 station ", C.primary_port_note(rcc_client.parse_sites([PLAN[0], PLAN[2]]), site()))

    def test_the_site_being_created_does_not_count_for_itself(self):
        own = rcc_client.parse_sites([{"id": "x9", "name": "Me", "status": "build", "marketId": 3700000001, "buildId": "b9"}])
        self.assertEqual(C.primary_port_note(own, site()), "")
        self.assertEqual(C.primary_port_note([], site(), [site()]), "")

    def test_other_stations_wfmt_has_seen_in_the_system_count_unless_abandoned(self):
        here = Site(market_id=5, name="Done Station", system="synuefe ni-r c21-10", complete=True)
        elsewhere = Site(market_id=6, name="Far", system="Sol", complete=True)
        failed = Site(market_id=7, name="Gave Up", system="Synuefe NI-R c21-10", failed=True)
        self.assertIn("1 other station ", C.primary_port_note([], site(), [here, elsewhere, failed]))
        self.assertEqual(C.primary_port_note([], site(), [elsewhere, failed]), "")


class Planned(unittest.TestCase):
    def test_only_unbuilt_unlinked_sites_are_offered(self):
        sites = rcc_client.parse_sites(PLAN)
        self.assertEqual([s.name for s in C.planned_sites(sites)], ["Pennington Claim"])
        self.assertEqual(C.planned_sites(sites)[0].site_id, "x1")

    def test_the_site_is_matched_by_the_stations_own_name(self):
        sites = rcc_client.parse_sites(PLAN)
        self.assertEqual(C.guess_planned(sites, "pennington claim").site_id, "x1")
        self.assertEqual(C.suggested_name(site()), "Primary port")
        other = Site(market_id=5, name="Orbital Construction Site: Grinning Station")
        self.assertEqual(C.suggested_name(other), "Grinning Station")
        self.assertTrue(C.is_construction_ship(site()))
        self.assertTrue(C.is_construction_ship(Site(market_id=6, name="System Colonization Ship Foo")))
        self.assertFalse(C.is_construction_ship(other))

    def test_the_only_planned_site_is_preselected(self):
        sites = rcc_client.parse_sites(PLAN)
        self.assertEqual(C.guess_planned(sites, "Primary port").site_id, "x1")
        two = rcc_client.parse_sites(PLAN + [{"id": "x4", "name": "Second", "bodyNum": 1, "buildType": "vesta", "status": "plan"}])
        self.assertIsNone(C.guess_planned(two, "Primary port"))


class Parsing(unittest.TestCase):
    def test_due_dates(self):
        self.assertEqual(C.parse_due("2026-12-31"), "2026-12-31T00:00:00Z")
        self.assertIsNone(C.parse_due(" "))
        with self.assertRaises(ValueError):
            C.parse_due("31/12/2026")

    def test_the_location_comes_from_raven_first_then_the_game(self):
        plan = rcc_client.RccSystem("S", "", None, [], id64=5, pos=(1.0, 1.0, 1.0))
        state = {"SystemName": "S", "SystemAddress": 9, "StarPos": [2, 2, 2]}
        self.assertEqual(C.locate("S", plan, state), (5, (1.0, 1.0, 1.0)))
        self.assertEqual(C.locate("s", None, state), (9, (2.0, 2.0, 2.0)))
        self.assertEqual(C.locate("Elsewhere", None, state), (None, None))


class Bodies(unittest.TestCase):
    def test_the_project_body_carries_the_depot_and_what_is_still_needed(self):
        body = C.project_body(request(architect="A", notes="n", due="2026-12-31T00:00:00Z"), "x1")
        self.assertEqual((body["marketId"], body["systemAddress"], body["systemSiteId"], body["buildType"]),
                         (3700000001, 1234, "x1", "no_truss"))
        self.assertEqual(body["commodities"], {"steel": 6560, "water": 741})
        self.assertEqual(body["maxNeed"], 7401)
        self.assertEqual(body["starPos"], [1.0, 2.0, 3.0])
        self.assertEqual((body["architectName"], body["notes"], body["timeDue"], body["bodyNum"]), ("A", "n", "2026-12-31T00:00:00Z", 4))
        depot = body["colonisationConstructionDepot"]
        self.assertEqual(depot["marketID"], 3700000001)
        self.assertEqual(depot["resourcesRequired"][0], {"name": "$steel_name;", "name_Localised": "Steel", "requiredAmount": 6660,
                                                         "providedAmount": 100, "payment": 0})

    def test_unknown_optional_fields_are_left_out(self):
        body = C.project_body(request(star_pos=None, body_num=None), "")
        for name in ("starPos", "bodyNum", "systemSiteId", "architectName", "notes", "timeDue", "bodyName"):
            self.assertNotIn(name, body)

    def test_demolishing_keeps_the_entry_as_it_is(self):
        entry = rcc_client.parse_sites(PLAN)[0]
        update = C.demolish_body(next(s for s in rcc_client.parse_sites(PLAN) if s.site_id == "x2"))["update"][0]
        self.assertEqual((update["status"], update["marketId"], update["buildId"], update["id"]), ("demolish", 9, "b2", "x2"))
        self.assertIsNotNone(entry)


class Validation(unittest.TestCase):
    def test_what_is_missing_is_named(self):
        self.assertIn("key", C.validate(request(key=" ")))
        self.assertIn("name", C.validate(request(name="")))
        self.assertIn("Choose", C.validate(request(build_type="")))
        self.assertIn("address", C.validate(request(system_address=None)))
        self.assertEqual(C.validate(request()), "")

    def test_no_body_is_needed(self):
        self.assertEqual(C.validate(request(body_num=None)), "")


class Creating(unittest.TestCase):
    def test_a_project_of_its_own_never_touches_the_plan(self):
        send = Recorder()
        result = C.create(request(fleet_carrier=3700000002), send)
        self.assertEqual([(m, p) for m, p, _b in send.calls], [
            ("PUT", "/api/project"), ("PUT", "/api/project/newbuild/link/tiber%20caelvox"),
            ("PUT", "/api/Cmdr/tiber%20caelvox/primary/newbuild"), ("PUT", "/api/project/newbuild/fc/3700000002")])
        self.assertNotIn("systemSiteId", send.calls[0][2])
        self.assertEqual(result.build_id, "newbuild")
        self.assertEqual(result.warnings, [])

    def test_a_planned_site_is_used_without_touching_the_plan(self):
        planned = C.planned_sites(rcc_client.parse_sites(PLAN))[0]
        send = Recorder()
        C.create(request(planned=planned, make_primary=False), send)
        self.assertEqual([p for _m, p, _b in send.calls], ["/api/project", "/api/project/newbuild/link/tiber%20caelvox"])
        self.assertEqual(send.calls[0][2]["systemSiteId"], "x1")

    def test_a_refused_project_stops_the_run(self):
        send = Recorder(fail=("/api/project",))
        with self.assertRaises(rcc_client.RccError):
            C.create(request(), send)
        self.assertEqual(len(send.calls), 1)

    def test_a_failed_optional_step_is_reported_and_keeps_the_project(self):
        planned = C.planned_sites(rcc_client.parse_sites(PLAN))[0]
        result = C.create(request(planned=planned), Recorder(fail=("/primary/",)))
        self.assertEqual(result.build_id, "newbuild")
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("primary", result.summary)

    def test_an_answer_without_a_build_id_is_an_error(self):
        planned = C.planned_sites(rcc_client.parse_sites(PLAN))[0]
        with self.assertRaises(rcc_client.RccError):
            C.create(request(planned=planned), lambda *a, **k: {})

    def test_an_invalid_request_sends_nothing(self):
        send = Recorder()
        with self.assertRaises(rcc_client.RccError):
            C.create(request(name=""), send)
        self.assertEqual(send.calls, [])


class BuildTypes(unittest.TestCase):
    def test_a_building_lists_the_layouts_raven_knows_it_by(self):
        coriolis = next(c for c in C.build_choices() if c.key == "no_truss")
        self.assertEqual(coriolis.layouts, ("no_truss", "dual_truss", "quad_truss"))
        self.assertEqual(C.choice_label(coriolis), "Tier 2: Coriolis Starport")
        vulcan = next(c for c in C.build_choices() if c.key == "vulcan")
        self.assertEqual((vulcan.name, vulcan.layouts, vulcan.location), ("Industrial Outpost", ("vulcan",), "orbital"))

    def test_the_two_locations_split_the_buildings(self):
        orbital, surface = C.choices_at("orbital"), C.choices_at("surface")
        self.assertTrue(orbital and surface)
        self.assertEqual(len(orbital) + len(surface), len(C.build_choices()))
        self.assertEqual({c.location for c in surface}, {"surface"})

    def test_a_planned_layout_finds_its_building(self):
        self.assertEqual(C.choice_for_layout("Dual_Truss").key, "no_truss")
        self.assertEqual(C.choice_for_layout("vulcan").name, "Industrial Outpost")
        self.assertIsNone(C.choice_for_layout("nonsense"))

    def test_every_layout_is_listed_once(self):
        layouts = [x for c in C.build_choices() for x in c.layouts]
        self.assertEqual(len(layouts), len(set(layouts)))


class Bodies(unittest.TestCase):
    def test_bodies_are_listed_by_number_without_belts(self):
        bodies = rcc_client.parse_bodies([
            {"name": "S B 1", "num": 7, "type": "hmc", "subType": "High metal content world"},
            {"name": "S A", "num": 1, "type": "st", "subType": "K star"},
            {"name": "S A Belt", "num": 100200, "type": "bt"}, {"name": "", "num": 3}, "junk"])
        self.assertEqual([(b.num, b.name) for b in bodies], [(1, "S A"), (7, "S B 1")])
        self.assertEqual(bodies[1].kind, "High metal content world")


if __name__ == "__main__":
    unittest.main()
