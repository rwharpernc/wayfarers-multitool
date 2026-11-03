"""Refresh from Raven: every open site's Raven Colonial figures in one pass (rcc_client.refresh_figures) and how they are worded
(colonization_view.raven_cell, raven_note, raven_summary). No connection: the reads are stood in for."""
from __future__ import annotations

import os
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import colonization, colonization_view as view, rcc_client as R  # noqa: E402


def plan(*sites, id64=1):
    return R.RccSystem("Sol", "", None, list(sites), id64=id64)


def planned(market_id, build_id="b-%d"):
    return R.RccSite("Depot", "build", "no_truss", 1, market_id, build_id=build_id % market_id if "%" in build_id else build_id)


class Fakes:
    def __init__(self, plans=None, projects=None, by_market=None):
        self.plans, self.projects, self.by_market_answers = plans or {}, projects or {}, by_market or {}
        self.plan_calls, self.project_calls, self.market_calls, self.pauses = [], [], [], []

    def fetch_plan(self, system):
        self.plan_calls.append(system)
        answer = self.plans.get(system)
        if isinstance(answer, Exception):
            raise answer
        return answer if answer is not None else plan()

    def project_for(self, build_id):
        self.project_calls.append(build_id)
        answer = self.projects.get(build_id)
        if isinstance(answer, Exception):
            raise answer
        return answer or R.RccProject(build_id, 0, 0, False, {})

    def by_market(self, address, market_id):
        self.market_calls.append((address, market_id))
        return self.by_market_answers.get(market_id)

    def run(self, asks, **kw):
        return R.refresh_figures(asks, self.fetch_plan, self.project_for, self.by_market, pause=self.pauses.append, **kw)


class RefreshFiguresTests(unittest.TestCase):
    def test_a_site_with_a_project_gets_raven_s_figures(self):
        f = Fakes({"Sol": plan(planned(7))}, {"b-7": R.RccProject("b-7", 120, 500, False, {})})
        got = f.run([R.SiteAsk(7, "Sol", "Depot")])
        self.assertEqual(got[7], R.SiteFigure(R.FIGURE_OK, 120, 500, False))

    def test_a_site_raven_has_no_project_for_says_so_and_asks_nothing_more(self):
        f = Fakes({"Sol": plan(R.RccSite("Depot", "plan", "no_truss", 1, 7))})
        self.assertEqual(f.run([R.SiteAsk(7, "Sol", "Depot")])[7].state, R.FIGURE_NONE)
        self.assertEqual(f.project_calls, [])

    def test_the_market_id_finds_a_project_the_plan_does_not_name(self):
        view_ = R.RccProjectView("b-9", "Primary port", "Sol", "x", 9, 10, 20, False, {})
        f = Fakes({"Sol": plan(id64=555)}, {"b-9": R.RccProject("b-9", 10, 20, False, {})}, {9: view_})
        got = f.run([R.SiteAsk(9, "Sol", "Orbital Construction Site: X")])
        self.assertEqual(got[9].state, R.FIGURE_OK)
        self.assertEqual(f.market_calls, [(555, 9)])

    def test_a_complete_project_is_marked_complete(self):
        f = Fakes({"Sol": plan(planned(7))}, {"b-7": R.RccProject("b-7", 0, 500, True, {})})
        self.assertTrue(f.run([R.SiteAsk(7, "Sol", "Depot")])[7].complete)

    def test_one_failure_is_kept_against_its_site_and_the_rest_are_still_asked(self):
        f = Fakes({"Sol": plan(planned(7), planned(8))}, {"b-7": R.RccError("Raven Colonial answered with an error (500). Try again later."),
                                                         "b-8": R.RccProject("b-8", 5, 9, False, {})})
        got = f.run([R.SiteAsk(7, "Sol", "Depot"), R.SiteAsk(8, "Sol", "Depot")])
        self.assertEqual((got[7].state, got[8].state), (R.FIGURE_ERROR, R.FIGURE_OK))
        self.assertIn("500", got[7].note)

    def test_a_surprise_in_one_answer_does_not_lose_the_others(self):
        f = Fakes({"Sol": plan(planned(7), planned(8))}, {"b-7": ValueError("odd"), "b-8": R.RccProject("b-8", 5, 9, False, {})})
        got = f.run([R.SiteAsk(7, "Sol", "Depot"), R.SiteAsk(8, "Sol", "Depot")])
        self.assertEqual((got[7].state, got[8].state), (R.FIGURE_ERROR, R.FIGURE_OK))

    def test_it_stops_after_three_failures_in_a_row_and_says_which_were_not_asked(self):
        down = R.RccError("Could not reach Raven Colonial. Check your connection and try again.")
        f = Fakes({f"S{i}": down for i in range(6)})
        got = f.run([R.SiteAsk(i, f"S{i}", "Depot") for i in range(6)])
        self.assertEqual([got[i].state for i in range(6)], [R.FIGURE_ERROR] * 3 + [R.FIGURE_SKIPPED] * 3)
        self.assertEqual(len(f.plan_calls), 3)

    def test_a_success_resets_the_failure_count(self):
        down = R.RccError("down")
        f = Fakes({"A": down, "B": down, "C": plan(planned(3)), "D": down, "E": down, "F": plan(planned(6))},
                  {"b-3": R.RccProject("b-3", 1, 1, False, {}), "b-6": R.RccProject("b-6", 1, 1, False, {})})
        got = f.run([R.SiteAsk(i, name, "Depot") for i, name in enumerate("ABCDEF")])
        self.assertNotIn(R.FIGURE_SKIPPED, {x.state for x in got.values()})

    def test_the_window_closing_stops_the_pass(self):
        f = Fakes({"Sol": plan(planned(7), planned(8))})
        got = f.run([R.SiteAsk(7, "Sol", "Depot"), R.SiteAsk(8, "Sol", "Depot")], stop=lambda: True)
        self.assertEqual({x.state for x in got.values()}, {R.FIGURE_SKIPPED})
        self.assertEqual(f.plan_calls, [])

    def test_no_more_than_the_cap_are_asked_and_the_rest_say_so(self):
        n = R.MAX_REFRESH_SITES + 3
        f = Fakes({"Sol": plan(*[planned(i) for i in range(n)])})
        got = f.run([R.SiteAsk(i, "Sol", "Depot") for i in range(n)])
        self.assertEqual(len(got), n)
        self.assertEqual(sum(1 for x in got.values() if x.state == R.FIGURE_SKIPPED), 3)
        self.assertEqual(len(f.project_calls), R.MAX_REFRESH_SITES)

    def test_requests_are_spaced_out_but_not_before_the_first(self):
        f = Fakes({"Sol": plan(planned(7), planned(8), planned(9))})
        f.run([R.SiteAsk(i, "Sol", "Depot") for i in (7, 8, 9)])
        self.assertEqual(f.pauses, [R.REFRESH_PAUSE_S] * 2)

    def test_nothing_to_ask_is_an_empty_answer(self):
        self.assertEqual(Fakes().run([]), {})


def open_site(market_id=7, need=100):
    return colonization.apply_depot_event({"MarketID": market_id, "ConstructionProgress": 0.4, "ResourcesRequired": [
        {"Name": "$steel_name;", "Name_Localised": "Steel", "RequiredAmount": need + 50, "ProvidedAmount": 50}]}, None, name="Depot", system="Sol")


class WordingTests(unittest.TestCase):
    def test_the_cell(self):
        self.assertEqual(view.raven_cell(None), "")
        self.assertEqual(view.raven_cell(R.SiteFigure(R.FIGURE_OK, 1200, 5000)), "1,200 t")
        self.assertEqual(view.raven_cell(R.SiteFigure(R.FIGURE_OK, 0, 5000, True)), "done")
        self.assertEqual(view.raven_cell(R.SiteFigure(R.FIGURE_NONE)), "no project")
        self.assertEqual(view.raven_cell(R.SiteFigure(R.FIGURE_ERROR, note="x")), "error")
        self.assertEqual(view.raven_cell(R.SiteFigure(R.FIGURE_SKIPPED)), "not asked")

    def test_the_note_says_when_and_how_many(self):
        now = datetime(2026, 11, 3, 15, 0, tzinfo=timezone.utc)
        figures = {1: R.SiteFigure(R.FIGURE_OK, 1, 2), 2: R.SiteFigure(R.FIGURE_NONE), 3: R.SiteFigure(R.FIGURE_ERROR)}
        self.assertEqual(view.raven_note(None, {}), view.RAVEN_NOT_ASKED)
        self.assertEqual(view.raven_note(now - timedelta(minutes=28), figures, now), "Raven figures refreshed 14:32: 2 of 3 sites answered.")
        self.assertEqual(view.raven_note(now - timedelta(days=1), figures, now), "Raven figures refreshed 2026-11-02 15:00: 2 of 3 sites answered.")
        self.assertIn("1 of 1 site answered", view.raven_note(now, {1: R.SiteFigure(R.FIGURE_OK, 1, 2)}, now))

    def test_the_summary(self):
        a, b, c, d = open_site(1, 100), open_site(2, 100), open_site(3, 100), open_site(4, 100)
        figures = {1: R.SiteFigure(R.FIGURE_OK, 100, 150), 2: R.SiteFigure(R.FIGURE_OK, 90, 150), 3: R.SiteFigure(R.FIGURE_NONE),
                   4: R.SiteFigure(R.FIGURE_ERROR)}
        self.assertEqual(view.raven_summary([a, b, c, d], figures),
                         "Raven Colonial: 1 agree, 1 differ, 1 with no project on Raven, 1 not read.")
        self.assertEqual(view.raven_summary([a], {1: R.SiteFigure(R.FIGURE_OK, 100, 150)}), "Raven Colonial: 1 agree, 0 differ.")

    def test_a_site_raven_calls_complete_while_wfmt_does_not_differs(self):
        self.assertIn("1 differ", view.raven_summary([open_site(1)], {1: R.SiteFigure(R.FIGURE_OK, 0, 150, True)}))


if __name__ == "__main__":
    unittest.main()
