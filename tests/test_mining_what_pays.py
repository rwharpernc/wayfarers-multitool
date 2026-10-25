"""What pays (plugin/mining_what_pays.py): which commodities are priced and why, the ranking and the report. Pure logic: no Tk, no network, no EDMC."""

import json
import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))

from plugin import mining_ground  # noqa: E402
from plugin import mining_hotspots as hotspots  # noqa: E402
from plugin import mining_spansh_client as spansh  # noqa: E402
from plugin import mining_what_pays as pays  # noqa: E402


def _spot(system: str, body: str, material: str, ground: str = "") -> hotspots.Hotspot:
    return hotspots.Hotspot(system=system, body=body, material=material, ground=ground or None)


def _names(plan) -> list[str]:
    return [c.name for c in plan.candidates]


class CandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rates = mining_ground.OwnRates([])

    def test_nothing_recorded_gives_nothing_to_price(self) -> None:
        plan = pays.candidates([], [], self.rates)
        self.assertEqual(plan.candidates, ())
        self.assertEqual(plan.skipped, ())

    def test_saved_materials_come_from_every_system_most_common_first(self) -> None:
        saved = [_spot("A", "A 1", "Painite"), _spot("B", "B 2", "Platinum"), _spot("B", "B 3", "Platinum"), _spot("C", "C 1", "Painite"), _spot("C", "C 2", "Painite")]
        plan = pays.candidates(saved, [], self.rates)
        self.assertEqual(_names(plan), ["Painite", "Platinum"])
        self.assertEqual(plan.candidates[0].reasons, ("3 saved deposits on 3 bodies",))
        self.assertEqual(plan.candidates[1].reasons, ("2 saved deposits on 2 bodies",))

    def test_one_deposit_on_one_body_reads_in_the_singular(self) -> None:
        self.assertEqual(pays.candidates([_spot("A", "A 1", "Painite")], [], self.rates).candidates[0].reasons, ("1 saved deposit on 1 body",))

    def test_the_target_commodity_comes_first_and_shares_a_commodity_with_the_records(self) -> None:
        plan = pays.candidates([_spot("A", "A 1", "Painite"), _spot("A", "A 2", "Platinum")], [], self.rates, target="platinum")
        self.assertEqual(_names(plan), ["Platinum", "Painite"])
        self.assertEqual(plan.candidates[0].reasons, ("your target commodity", "1 saved deposit on 1 body"))

    def test_your_rates_on_the_grounds_here_are_added(self) -> None:
        saved = [_spot("A", "A 1", "Bromellite", "icy"), _spot("A", "A 2", "Bromellite", "icy"), _spot("A", "A 3", "Painite", "icy")]
        plan = pays.candidates([], ["icy"], mining_ground.OwnRates(saved))
        self.assertEqual(_names(plan), ["Bromellite", "Painite"])
        self.assertIn("67% of your 3 recorded deposits on this kind of ground (icy body)", plan.candidates[0].reasons[0])
        self.assertEqual(pays.candidates([], ["rocky"], mining_ground.OwnRates(saved)).candidates, (), "another ground has no records")

    def test_added_names_count_and_unknown_names_are_reported_not_priced(self) -> None:
        plan = pays.candidates([], [], self.rates, extra=["painite", "Nonsense Ore", " "])
        self.assertEqual(_names(plan), ["Painite"])
        self.assertEqual(plan.candidates[0].reasons, ("added by you",))
        self.assertEqual(plan.skipped, ("Nonsense Ore",))

    def test_the_list_is_capped(self) -> None:
        names = ["Painite", "Platinum", "Bromellite", "Grandidierite", "Monazite", "Alexandrite", "Benitoite", "Musgravite", "Serendibite", "Rhodplumsite",
                 "Gold", "Silver", "Palladium", "Osmium", "Samarium", "Praseodymium", "Cobalt", "Lithium"]
        plan = pays.candidates([_spot("A", "A 1", n) for n in names], [], self.rates)
        self.assertEqual(len(plan.candidates), pays.MAX_CANDIDATES)
        self.assertEqual(len(pays.candidates([_spot("A", "A 1", n) for n in names], [], self.rates, limit=3).candidates), 3)

    def test_a_blank_material_is_ignored(self) -> None:
        self.assertEqual(pays.candidates([_spot("A", "A 1", "  ")], [], self.rates).candidates, ())


def _offer(price: int, **kw) -> pays.Offer:
    base = dict(station="Hub", system="Sol", price=price, demand=500, distance_ly=12.5, arrival_ls=800.0, pads="1 large")
    base.update(kw)
    return pays.Offer(**base)


class RankTests(unittest.TestCase):
    def test_best_price_first_and_unpriced_last(self) -> None:
        rows = [pays.Row("Low", ("a",), _offer(100)), pays.Row("None", ("a",), None), pays.Row("High", ("a",), _offer(900)), pays.Row("Mid", ("a",), _offer(500))]
        self.assertEqual([r.name for r in pays.rank(rows)], ["High", "Mid", "Low", "None"])

    def test_equal_prices_and_unpriced_rows_go_by_name(self) -> None:
        rows = [pays.Row("b", (), _offer(5)), pays.Row("A", (), _offer(5)), pays.Row("z", (), None), pays.Row("C", (), None)]
        self.assertEqual([r.name for r in pays.rank(rows)], ["A", "b", "C", "z"])

    def test_ranking_does_not_change_the_list_it_is_given(self) -> None:
        rows = [pays.Row("Low", (), _offer(1)), pays.Row("High", (), _offer(9))]
        pays.rank(rows)
        self.assertEqual([r.name for r in rows], ["Low", "High"])


class OfferTests(unittest.TestCase):
    def test_an_offer_is_built_from_a_spansh_station(self) -> None:
        station = spansh.StationPrice(station="Hub", system="Sol", station_type="Orbis", distance_ly=12.5, distance_to_arrival_ls=800.4, is_planetary=False, price=612345, quantity=4000,
                                      small_pads=2, medium_pads=0, large_pads=1)
        offer = pays.offer_from(station)
        self.assertEqual((offer.station, offer.system, offer.price, offer.demand), ("Hub", "Sol", 612345, 4000))
        self.assertEqual(offer.pads, "2 small, 1 large")
        self.assertAlmostEqual(offer.arrival_ls, 800.4)

    def test_missing_pad_counts_give_no_pad_text(self) -> None:
        station = spansh.StationPrice("Hub", "Sol", "Outpost", 1.0, 2.0, False, 10, 5)
        self.assertEqual(pays.offer_from(station).pads, "")


class ReportTests(unittest.TestCase):
    def test_the_report_lists_the_ranking_and_says_what_it_is(self) -> None:
        rows = [pays.Row("Painite", ("your target commodity",), _offer(500000)), pays.Row("Bromellite", ("1 saved deposit on 1 body",), None)]
        text = pays.format_report("Sol", "Within 100 ly", rows, skipped=["Nonsense"])
        lines = text.splitlines()
        self.assertEqual(lines[0], "What pays, within 100 ly of Sol:")
        self.assertTrue(lines[1].startswith("1. Painite: 500,000 cr at Hub, Sol"))
        self.assertIn("Why: your target commodity", lines[1])
        self.assertTrue(lines[2].startswith("2. Bromellite: no station found paying for it"))
        self.assertIn("Not a commodity Spansh knows, so left out: Nonsense", text)
        self.assertIn("ranks what pays", text)

    def test_an_empty_ranking_says_what_to_do(self) -> None:
        self.assertIn("Nothing to price yet", pays.format_report("Sol", "Within 100 ly", []))


class RequestTests(unittest.TestCase):
    """What a mining price search asks Spansh for, with the network replaced by a recorder: no fleet carriers and a demand floor."""

    def _ask(self, results=(), **kwargs) -> dict:
        captured = {}

        def fake_call(request, timeout, cancel=None, retries=None):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return json.dumps({"results": list(results)}).encode("utf-8")

        with mock.patch.object(spansh.spansh_courtesy, "call", fake_call):
            captured["found"] = spansh.search_best_price_stations("Sol", "Gold", "Sell", 100.0, **kwargs)
        return captured

    @staticmethod
    def _station(name: str, kind: str) -> dict:
        return {"name": name, "system_name": "Sol", "type": kind, "distance": 1.0, "distance_to_arrival": 10.0,
                "market": [{"commodity": "Gold", "sell_price": 90000, "demand": 50}]}

    def test_the_request_asks_for_stations_only_never_carriers(self) -> None:
        kinds = self._ask(**pays.NO_CARRIERS)["body"]["filters"]["type"]["value"]
        self.assertTrue(kinds)
        self.assertFalse([k for k in kinds if "carrier" in k.lower()])
        self.assertIn("Coriolis Starport", kinds)

    def test_a_carrier_that_comes_back_anyway_is_dropped(self) -> None:
        sent = self._ask([self._station("Port", "Coriolis Starport"), self._station("Carrier", "Drake-Class Carrier")], **pays.NO_CARRIERS)
        self.assertEqual([s.station for s in sent["found"]], ["Port"])
        both = self._ask([self._station("Port", "Coriolis Starport"), self._station("Carrier", "Drake-Class Carrier")])
        self.assertEqual(len(both["found"]), 2, "other callers still get what they ask for")

    def test_the_demand_floor_is_in_the_request(self) -> None:
        market = self._ask(min_quantity=40, **pays.NO_CARRIERS)["body"]["filters"]["market"][0]
        self.assertEqual(market["demand"], {"value": ["40", "999999999"], "comparison": "<=>"})
        self.assertEqual(self._ask(**pays.NO_CARRIERS)["body"]["filters"]["market"][0]["demand"]["value"][0], "1")


class HoldFloorTests(unittest.TestCase):
    def _hold(self, held):
        patcher = mock.patch.object(pays, "hold", lambda: held)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_the_floor_is_the_tons_of_that_commodity_in_the_hold(self) -> None:
        self._hold({"painite": 12, "drones": 4, "lowtemperaturediamond": 3})
        self.assertEqual(pays.minimum_for("Painite"), 12)
        self.assertEqual(pays.minimum_for("painite"), 12)
        self.assertEqual(pays.minimum_for("Low Temperature Diamonds"), 3)
        self.assertEqual(pays.minimum_for("Platinum"), 1)

    def test_with_no_hold_known_the_floor_is_one(self) -> None:
        self._hold({})
        self.assertEqual(pays.minimum_for("Painite"), 1)

    def test_a_hold_that_cannot_be_read_is_no_hold(self) -> None:
        def broken():
            raise RuntimeError("no state")
        with mock.patch.object(pays, "hold", broken):
            self.assertEqual(pays.minimum_for("Painite"), 1)

    def test_the_default_hold_is_empty_without_a_cargo_state(self) -> None:
        from plugin import current_cargo
        with mock.patch.object(current_cargo, "_held", {}):
            self.assertEqual(pays.minimum_for("Painite"), 1)

    def test_a_typed_minimum_must_be_a_whole_number_of_tons(self) -> None:
        self.assertEqual(pays.parse_minimum("25"), 25)
        self.assertEqual(pays.parse_minimum(" 1,200 "), 1200)
        self.assertEqual(pays.parse_minimum(""), 1)
        for bad in ("0", "-5", "2.5", "abc", "1e3", str(pays.MAX_MINIMUM + 1)):
            self.assertIsNone(pays.parse_minimum(bad), bad)


if __name__ == "__main__":
    unittest.main()
