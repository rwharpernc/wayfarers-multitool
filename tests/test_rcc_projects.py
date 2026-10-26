"""
A commander's projects on Raven Colonial (rcc_projects.py and the reads and writes in rcc_client.py): parsing what Raven answers,
the rows and what counts, the totals and trips, the shopping list, and that the reads send no key.
"""
from __future__ import annotations

import io
import json
import os
import sys
import types
import unittest
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import rcc_client as R, rcc_projects as P  # noqa: E402

LIVE = [
    {"buildId": "b1", "buildName": "Primary port", "systemName": "Synuefe NI-R c21-10", "buildType": "no_truss", "marketId": 3700000001,
     "sumNeed": 500, "maxNeed": 1000, "complete": False, "commodities": {"Steel": 300, "water": 200, "gold": 0}},
    {"buildId": "b2", "buildName": "Alpha Outpost", "systemName": "Alpha", "buildType": "vulcan", "sumNeed": 90, "maxNeed": 90,
     "commodities": {"titanium": 90}},
    {"buildId": "b3", "buildName": "Loading", "systemName": "Alpha", "buildType": "fc_loading", "sumNeed": 10, "maxNeed": 100, "complete": True},
    {"buildName": "no id"}, "junk",
]


class Response:
    def __init__(self, body):
        self._body = io.BytesIO(body if isinstance(body, bytes) else json.dumps(body).encode("utf-8"))

    def read(self, size=-1):
        return self._body.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Opener:
    def __init__(self, *answers):
        self.answers, self.requests = list(answers), []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return Response(answer)


class Parsing(unittest.TestCase):
    def test_projects_are_read_and_the_malformed_skipped(self):
        views = R.parse_project_views(LIVE)
        self.assertEqual([v.build_id for v in views], ["b1", "b2", "b3"])
        first = views[0]
        self.assertEqual((first.name, first.system, first.build_type, first.market_id, first.sum_need, first.max_need),
                         ("Primary port", "Synuefe NI-R c21-10", "no_truss", 3700000001, 500, 1000))
        self.assertEqual(first.commodities, {"steel": 300, "water": 200})      # keys folded, nothing-needed dropped
        self.assertEqual(R.parse_project_views({"a": 1}), [])

    def test_the_list_is_capped(self):
        many = [{"buildId": f"id{i}", "buildName": "x"} for i in range(R.MAX_PROJECTS + 50)]
        self.assertEqual(len(R.parse_project_views(many)), R.MAX_PROJECTS)


class Reading(unittest.TestCase):
    def test_reads_send_no_key_and_use_the_lowercased_name(self):
        opener = Opener(LIVE, ["b2", "x", 5], "b1")
        views = R.fetch_active("Tiber Caelvox", opener)
        self.assertEqual(R.fetch_hidden("Tiber Caelvox", opener), ["b2", "x"])
        self.assertEqual(R.fetch_primary("Tiber Caelvox", opener), "b1")
        self.assertEqual(len(views), 3)
        self.assertEqual([r.full_url.rsplit("/api/", 1)[1] for r in opener.requests],
                         ["Cmdr/tiber%20caelvox/active", "Cmdr/tiber%20caelvox/hiddenIDs", "Cmdr/tiber%20caelvox/primary"])
        for request in opener.requests:
            self.assertNotIn("Rcc-key", request.headers)

    def test_a_commander_raven_does_not_know_has_nothing(self):
        error = urllib.error.HTTPError("u", 404, "nf", {}, None)
        self.assertEqual(R.fetch_active("X", Opener(error)), [])
        self.assertEqual(R.fetch_primary("X", Opener(error)), "")

    def test_failures_are_worded_for_the_commander(self):
        with self.assertRaises(R.RccError):
            R.fetch_active("X", Opener(urllib.error.HTTPError("u", 500, "x", {}, None)))
        with self.assertRaises(R.RccError):
            R.fetch_active("X", Opener(urllib.error.URLError("down")))
        with self.assertRaises(R.RccError):
            R.fetch_active("X", Opener(b"not json"))
        with self.assertRaises(R.RccError):
            R.fetch_active("  ")


class Writing(unittest.TestCase):
    def test_the_hidden_list_is_replaced_and_the_answer_returned(self):
        sent = []
        answer = R.save_hidden("Tiber", ["b1"], "k", lambda m, p, b, key, cmdr="": sent.append((m, p, b, key)) or ["b1", "b9"])
        self.assertEqual(sent, [("POST", "/api/Cmdr/tiber/hiddenIDs", ["b1"], "k")])
        self.assertEqual(answer, ["b1", "b9"])

    def test_a_primary_project_is_set_by_its_build_id(self):
        sent = []
        R.set_primary("Tiber", "b 1", "k", lambda m, p, b, key, cmdr="": sent.append((m, p, b, key)))
        self.assertEqual(sent, [("PUT", "/api/Cmdr/tiber/primary/b%201", None, "k")])


class Rows(unittest.TestCase):
    def setUp(self):
        self.views = R.parse_project_views(LIVE)

    def test_rows_are_sorted_and_marked(self):
        shown = P.rows(self.views, {"b2"}, "b1", {3700000001})
        self.assertEqual([r.view.build_id for r in shown], ["b2", "b3", "b1"])        # Alpha first, then Synuefe
        by_id = {r.view.build_id: r for r in shown}
        self.assertEqual((by_id["b1"].counted, by_id["b1"].primary, by_id["b1"].tracked), (True, True, True))
        self.assertEqual((by_id["b2"].counted, by_id["b2"].primary, by_id["b2"].tracked), (False, False, False))

    def test_progress(self):
        by_id = {v.build_id: v for v in self.views}
        self.assertEqual(P.progress(by_id["b1"]), 0.5)
        self.assertEqual(P.progress(by_id["b3"]), 1.0)
        self.assertEqual(P.progress(by_id["b2"]), 0.0)
        self.assertEqual(P.progress(R.RccProjectView("x", "", "", "", None, 0, 0, False, {})), 0.0)

    def test_totals_count_only_unhidden_unfinished_projects(self):
        shown = P.rows(self.views, set(), "", set())
        self.assertEqual(P.totals(shown, 100), (2, 590, 6))
        self.assertEqual(P.totals(P.rows(self.views, {"b2"}, "", set()), 100), (1, 500, 5))
        self.assertEqual(P.totals(shown, 0), (2, 590, 0))                              # no known capacity, no trips

    def test_toggling_flips_the_hidden_state_without_changing_the_original(self):
        original = {"a"}
        self.assertEqual(P.toggled(original, "b"), {"a", "b"})
        self.assertEqual(P.toggled(original, "a"), set())
        self.assertEqual(original, {"a"})


class Labels(unittest.TestCase):
    def test_the_building_is_named_with_its_layout(self):
        by_id = {v.build_id: v for v in R.parse_project_views(LIVE)}
        self.assertEqual(P.building_label(by_id["b2"]), "Industrial Outpost (vulcan)")
        self.assertEqual(P.building_label(by_id["b1"]), "Coriolis Starport (no_truss)")
        self.assertEqual(P.building_label(by_id["b3"]), "Carrier loading")
        self.assertEqual(P.building_label(R.RccProjectView("x", "", "", "mystery", None, 0, 0, False, {})), "Mystery")

    def test_the_shopping_list_is_biggest_first(self):
        view = R.parse_project_views(LIVE)[0]
        self.assertEqual(P.shopping_list(view), [("Steel", 300), ("Water", 200)])
        text = P.shopping_text(view)
        self.assertTrue(text.startswith("Primary port (Synuefe NI-R c21-10) - still to get:"))
        self.assertIn("300 t  Steel", text)
        self.assertIn("nothing is needed", P.shopping_text(R.parse_project_views(LIVE)[2]))


class ByMarket(unittest.TestCase):
    VIEW = {"buildId": "b7", "buildName": "Primary port", "systemName": "Sol", "buildType": "no_truss", "marketId": 5, "sumNeed": 1, "maxNeed": 2}

    def test_a_project_is_found_by_the_systems_address_and_the_market_id(self):
        opener = Opener(self.VIEW)
        view = R.fetch_project_by_market(2833168437946, 5, opener)
        self.assertEqual(view.build_id, "b7")
        self.assertTrue(opener.requests[0].full_url.endswith("/api/system/2833168437946/5"))

    def test_no_project_is_none(self):
        self.assertIsNone(R.fetch_project_by_market(1, 5, Opener(urllib.error.HTTPError("u", 404, "nf", {}, None))))

    def test_the_plan_is_tried_first_then_the_market_id(self):
        sites = R.parse_sites([{"id": "x1", "name": "Named", "bodyNum": 1, "buildType": "vulcan", "status": "build", "buildId": "from-plan"}])
        plan = R.RccSystem("Sol", "", None, sites, id64=99)
        never = lambda *a: self.fail("not needed")
        self.assertEqual(R.build_id_for(plan, 5, "Named", by_market=never), "from-plan")
        asked = []
        found = lambda address, market: asked.append((address, market)) or R.parse_project_views([self.VIEW])[0]
        self.assertEqual(R.build_id_for(plan, 5, "Primary port", by_market=found), "b7")
        self.assertEqual(asked, [(99, 5)])
        self.assertEqual(R.build_id_for(R.RccSystem("Sol", "", None, []), 5, by_market=never), "")     # no address: nothing to ask
        self.assertEqual(R.build_id_for(plan, 6, by_market=lambda *a: None), "")


if __name__ == "__main__":
    unittest.main()
