"""Best single systems for a shopping list (colonization_systems.py), with Spansh replaced by a stand-in."""
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

from plugin import colonization_sources as src  # noqa: E402
from plugin import colonization_systems as cs  # noqa: E402


def source(station, system, ly, supply, price=100, carrier=False):
    return src.Source(station=station, system=system, kind="Coriolis Starport", is_carrier=carrier, is_planetary=False, pad="Large",
                      distance_ly=ly, arrival_ls=100.0, price=price, supply=supply)


def found_for(table):
    """{commodity: [Source, ...]} -> what Find all returns."""
    return [(label, src.SearchResult(stations=[s for s in sources if not s.is_carrier], carriers=[s for s in sources if s.is_carrier]))
            for label, sources in table.items()]


def station(name, market, ls=100.0, pads=(1, 1, 1), kind="Coriolis Starport", planetary=False):
    """A station as Spansh sends it from a system search: its whole market."""
    return {"name": name, "system_name": "X", "type": kind, "distance_to_arrival": ls, "is_planetary": planetary,
            "small_pads": pads[0], "medium_pads": pads[1], "large_pads": pads[2],
            "market": [{"commodity": c, "buy_price": price, "supply": supply} for c, (price, supply) in market.items()]}


class CandidateTests(unittest.TestCase):
    NEEDS = {"Steel": 500, "Water": 100, "Copper": 50}

    def test_the_system_with_the_most_commodities_comes_first(self):
        found = found_for({
            "Steel": [source("A1", "Alpha", 10, 500), source("B1", "Beta", 5, 500)],
            "Water": [source("A2", "Alpha", 10, 100)],
            "Copper": [source("A3", "Alpha", 10, 50), source("B2", "Beta", 5, 50)]})
        chosen = cs.candidate_systems(found, self.NEEDS)
        self.assertEqual([name for name, _ in chosen], ["Alpha", "Beta"])
        self.assertEqual(dict(chosen), {"Alpha": 10, "Beta": 5})

    def test_the_system_searched_around_is_always_checked_and_comes_first(self):
        found = found_for({"Steel": [source("A1", "Alpha", 10, 500)], "Water": [source("A2", "Alpha", 10, 100)]})
        chosen = cs.candidate_systems(found, self.NEEDS, always=["Home"])
        self.assertEqual([name for name, _ in chosen], ["Home", "Alpha"])
        self.assertEqual(chosen[0][1], 0.0)

    def test_a_system_found_for_one_commodity_only_is_not_worth_a_request(self):
        found = found_for({"Steel": [source("A1", "Alpha", 10, 500)], "Water": [source("B1", "Beta", 5, 100)]})
        self.assertEqual(cs.candidate_systems(found, self.NEEDS), [])

    def test_fleet_carriers_and_empty_stock_are_ignored(self):
        found = found_for({"Steel": [source("FC", "Moving", 1, 500, carrier=True), source("A1", "Alpha", 10, 0)],
                           "Water": [source("FC", "Moving", 1, 100, carrier=True), source("A2", "Alpha", 10, 100)]})
        self.assertEqual(cs.candidate_systems(found, self.NEEDS), [])

    def test_the_limit_and_duplicates(self):
        table = {"Steel": [source(f"S{i}", f"Sys{i}", i, 500) for i in range(10)],
                 "Water": [source(f"W{i}", f"Sys{i}", i, 100) for i in range(10)]}
        chosen = cs.candidate_systems(found_for(table), self.NEEDS, always=["sys0", "Home"], limit=4)
        self.assertEqual(len(chosen), 4)
        self.assertEqual([n.casefold() for n, _ in chosen].count("sys0"), 1)


class PlanSystemTests(unittest.TestCase):
    NEEDS = {"Steel": 1000, "Water": 100}

    def test_stock_is_added_up_across_the_systems_stations(self):
        stations = [station("Near", {"Steel": (90, 600), "Water": (50, 100)}, ls=50),
                    station("Far", {"Steel": (80, 300)}, ls=900)]
        plan = cs.plan_system("X", 12.5, stations, self.NEEDS)
        self.assertEqual((plan.needed, plan.covered), (1100, 1000))
        self.assertEqual(plan.uncovered, (("Steel", 100),))
        self.assertFalse(plan.complete)
        self.assertEqual([s.station for s in plan.stops], ["Near", "Far"])         # nearest the arrival star first
        self.assertEqual(plan.cost, 600 * 90 + 100 * 50 + 300 * 80)

    def test_a_system_that_has_everything_is_complete(self):
        stations = [station("A", {"Steel": (90, 5000), "Water": (50, 5000)})]
        plan = cs.plan_system("X", 0.0, stations, self.NEEDS)
        self.assertTrue(plan.complete)
        self.assertEqual((plan.covered, plan.uncovered, len(plan.stops)), (1100, (), 1))
        self.assertEqual(plan.share, 1.0)

    def test_fewest_stations_cover_the_most(self):
        stations = [station("Both", {"Steel": (95, 1000), "Water": (60, 100)}, ls=700),
                    station("OnlySteel", {"Steel": (80, 1000)}, ls=10)]
        plan = cs.plan_system("X", 0.0, stations, self.NEEDS)
        self.assertEqual([s.station for s in plan.stops], ["Both"])

    def test_commodity_names_match_without_regard_to_case_and_unwanted_ones_are_ignored(self):
        stations = [station("A", {"STEEL": (90, 1000), "Water": (50, 100), "Gold": (9000, 10)})]
        plan = cs.plan_system("X", 0.0, stations, self.NEEDS)
        self.assertEqual(plan.covered, 1100)
        self.assertEqual({b.commodity for b in plan.stops[0].buys}, {"Steel", "Water"})

    def test_zero_price_or_stock_does_not_count(self):
        stations = [station("A", {"Steel": (0, 1000), "Water": (50, 0)})]
        plan = cs.plan_system("X", 0.0, stations, self.NEEDS)
        self.assertEqual((plan.covered, plan.stops), (0, ()))

    def test_the_pad_choice_leaves_out_stations_that_cannot_take_the_ship(self):
        stations = [station("Small", {"Steel": (90, 1000), "Water": (50, 100)}, pads=(2, 0, 0)),
                    station("Big", {"Steel": (95, 400)}, pads=(2, 2, 2))]
        plan = cs.plan_system("X", 0.0, stations, self.NEEDS, pad=src.PAD_LARGE)
        self.assertEqual([s.station for s in plan.stops], ["Big"])
        self.assertEqual(plan.stations_with_market, 1)
        self.assertEqual(cs.plan_system("X", 0.0, stations, self.NEEDS).stations_with_market, 2)

    def test_lines_give_a_summary_the_stations_and_the_shortfall(self):
        stations = [station("Near", {"Steel": (90, 600), "Water": (50, 100)}, ls=50)]
        lines = cs.plan_system("X", 12.5, stations, self.NEEDS).lines()
        self.assertEqual(lines[0], "X: 700 of 1,100 t covered (64%), about 59,000 cr, 12.5 ly away")
        self.assertEqual(lines[1], "1. Near: Steel 600 t, Water 100 t")
        self.assertEqual(lines[-1], "Short: Steel 400 t")


class RankTests(unittest.TestCase):
    def plan(self, name, covered, needed=1000, ly=10.0, cost=0):
        return cs.SystemPlan(system=name, distance_ly=ly, stops=(), needed=needed, covered=covered,
                             uncovered=(("Steel", needed - covered),) if covered < needed else (), cost=cost, stations_with_market=1)

    def test_complete_first_then_share_then_nearer_then_cheaper(self):
        order = cs.rank([self.plan("Partial", 900), self.plan("FullFar", 1000, ly=50), self.plan("FullNear", 1000, ly=5, cost=9),
                         self.plan("FullNearCheap", 1000, ly=5, cost=1), self.plan("Half", 500)])
        self.assertEqual([p.system for p in order], ["FullNearCheap", "FullNear", "FullFar", "Partial", "Half"])


class FindBestSystemsTests(unittest.TestCase):
    NEEDS = {"Steel": 1000, "Water": 100}

    def setUp(self):
        self.found = found_for({"Steel": [source("A1", "Alpha", 10, 500), source("B1", "Beta", 20, 500)],
                                "Water": [source("A2", "Alpha", 10, 100), source("B2", "Beta", 20, 100)]})
        self.markets = {
            "Home": [station("H", {"Steel": (90, 200)})],
            "Alpha": [station("A1", {"Steel": (90, 1000), "Water": (50, 100)})],
            "Beta": [station("B1", {"Steel": (90, 500)}), station("B2", {"Water": (50, 100)})]}
        self.calls, self.sleeps = [], []

    def fetch(self, system, market_days_old=7):
        self.calls.append((system, market_days_old))
        return self.markets[system], len(self.markets[system])

    def run_it(self, **kwargs):
        return cs.find_best_systems(self.found, self.NEEDS, "Home", fetch=self.fetch, sleep=self.sleeps.append, **kwargs)

    def test_it_checks_each_candidate_once_and_ranks_the_complete_one_first(self):
        result = self.run_it()
        self.assertEqual([c[0] for c in self.calls], ["Home", "Alpha", "Beta"])
        self.assertEqual({c[1] for c in self.calls}, {src.MAX_AGE_DAYS})
        self.assertEqual([p.system for p in result.plans], ["Alpha", "Beta", "Home"])
        self.assertTrue(result.plans[0].complete)
        self.assertEqual(result.plans[1].uncovered, (("Steel", 500),))
        self.assertEqual(len(self.sleeps), 2)                    # a pause between requests, none before the first

    def test_a_system_that_fails_is_recorded_and_the_others_carry_on(self):
        original = self.fetch

        def flaky(system, market_days_old=7):
            if system == "Alpha":
                raise OSError("down")
            return original(system, market_days_old)
        result = cs.find_best_systems(self.found, self.NEEDS, "Home", fetch=flaky, sleep=lambda _s: None)
        self.assertEqual([system for system, _ in result.failed], ["Alpha"])
        self.assertEqual([p.system for p in result.plans], ["Beta", "Home"])

    def test_cancelling_stops_between_systems(self):
        ticks = iter([False, True])
        result = self.run_it(cancelled=lambda: next(ticks))
        self.assertTrue(result.stopped)
        self.assertEqual([c[0] for c in self.calls], ["Home"])

    def test_progress_is_reported_before_each_system(self):
        seen = []
        self.run_it(progress=lambda done, total, system: seen.append((done, total, system)))
        self.assertEqual(seen, [(0, 3, "Home"), (1, 3, "Alpha"), (2, 3, "Beta")])

    def test_one_commodity_needs_no_system_search(self):
        result = cs.find_best_systems(self.found, {"Steel": 1000}, "Home", fetch=self.fetch, sleep=lambda _s: None)
        self.assertEqual((result.plans, self.calls), ([], []))

    def test_systems_that_supply_nothing_are_left_out(self):
        self.markets["Home"] = [station("H", {"Gold": (9000, 10)})]
        self.assertNotIn("Home", [p.system for p in self.run_it().plans])

    def test_a_system_with_more_stations_than_one_answer_holds_is_flagged(self):
        original = self.fetch
        result = cs.find_best_systems(self.found, self.NEEDS, "Home", sleep=lambda _s: None,
                                      fetch=lambda s, market_days_old=7: (original(s)[0], 150))
        self.assertTrue(all(p.more_stations for p in result.plans))


if __name__ == "__main__":
    unittest.main()
