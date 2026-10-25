"""
Which missions need cargo bought on a market (Collect and Mining) and which Delivery missions have cargo to pick up at the station that gave the mission
(mission_types, MissionSummary.from_event, mission_sources.needs_from). The journal scan's station note is tested in test_missions_data.py. The events are
shaped like real ones from the journal (2026-10-17).

Pure logic - no EDMC runtime needed. Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))

from plugin import all_missions, mission_cargo, mission_sources, mission_types  # noqa: E402

STATION = "The Empty Share"


def _event(name: str = "Mission_Delivery", commodity: str = "$PersonalWeapons_Name;", count: int = 132, **extra) -> dict:
    event = {"timestamp": "2026-10-17T22:11:12Z", "event": "MissionAccepted", "Faction": "The Brigade", "Name": name,
             "LocalisedName": f"Deliver {count} units of Personal Weapons", "Commodity": commodity,
             "Commodity_Localised": "Personal Weapons", "Count": count, "DestinationSystem": "Pegasi Sector VP-O b6-7",
             "Expiry": "2026-10-18T22:10:25Z", "Wing": False, "Reward": 810462, "MissionID": 1068710723}
    event.update(extra)
    return event


def _at(event: dict, station: str = STATION, pad: str = "Medium") -> dict:
    return {**event, mission_types.ACCEPTED_AT: station, mission_types.ACCEPTED_PAD: pad}


class KindsTests(unittest.TestCase):
    def test_collect_and_mining_are_bought_on_a_market(self) -> None:
        for name in ("Mission_Collect_Industrial", "Mission_Mining", "Mission_Mining_Expansion", "Mission_Collect"):
            self.assertTrue(mission_types.needs_commodity_supply(_event(name)), name)
            self.assertFalse(mission_types.is_pickup_delivery(_event(name)), name)

    def test_a_delivery_is_never_bought_on_a_market(self) -> None:
        for name in ("Mission_Delivery", "Mission_Delivery_War", "Mission_Delivery_Agriculture"):
            self.assertFalse(mission_types.needs_commodity_supply(_event(name)), name)

    def test_deliveries_with_cargo_are_picked_up(self) -> None:
        for name in ("Mission_Delivery", "Mission_Delivery_War", "Mission_Delivery_Agriculture", "Mission_Delivery_Boom"):
            self.assertTrue(mission_types.is_pickup_delivery(_event(name)), name)

    def test_variants_nothing_is_known_about_are_left_out(self) -> None:
        for name in ("Mission_DeliveryWing_War", "Mission_Delivery_RankFed", "Mission_Delivery_Cooperative", "Mission_OnFoot_Delivery_Contact_MB",
                     "Mission_ColonisationDelivery", "Mission_Sightseeing", "Mission_Courier"):
            self.assertFalse(mission_types.is_pickup_delivery(_event(name)), name)

    def test_a_delivery_without_cargo_is_not(self) -> None:
        self.assertFalse(mission_types.is_pickup_delivery({"Name": "Mission_Delivery"}))
        self.assertFalse(mission_types.is_pickup_delivery(_event(count=0)))
        self.assertFalse(mission_types.is_pickup_delivery(_event(Commodity="")))


class PadTests(unittest.TestCase):
    def test_the_largest_pad_from_a_docked_event(self) -> None:
        self.assertEqual(mission_types.largest_pad_of({"Small": 2, "Medium": 1, "Large": 0}), "Medium")    # The Empty Share
        self.assertEqual(mission_types.largest_pad_of({"Small": 14, "Medium": 16, "Large": 8}), "Large")   # Example Station
        self.assertEqual(mission_types.largest_pad_of({"Small": 1, "Medium": 0, "Large": 0}), "Small")

    def test_no_pads_or_junk_is_empty(self) -> None:
        for value in (None, {}, {"Small": 0, "Medium": 0, "Large": 0}, "x", [], {"Large": True}, {"Large": "2"}):
            self.assertEqual(mission_types.largest_pad_of(value), "", value)


class SummaryTests(unittest.TestCase):
    def test_a_delivery_not_yet_collected_is_a_pickup_not_a_purchase(self) -> None:
        summary = all_missions.MissionSummary.from_event(_at(_event()))
        self.assertEqual((summary.pickup_commodity, summary.pickup_count, summary.pickup_station, summary.pickup_pad),
                         ("Personal Weapons", 132, STATION, "Medium"))
        self.assertEqual((summary.needed_commodity, summary.needed_commodity_count), ("", 0))

    def test_collected_cargo_takes_the_pickup_away(self) -> None:
        collected = mission_cargo.CargoProgress(collected=132, delivered=0, total=132)
        summary = all_missions.MissionSummary.from_event(_at(_event()), collected)
        self.assertEqual((summary.pickup_commodity, summary.pickup_count, summary.pickup_station), ("", 0, ""))

    def test_partly_collected_leaves_the_rest(self) -> None:
        summary = all_missions.MissionSummary.from_event(_at(_event()), mission_cargo.CargoProgress(collected=100, delivered=0, total=132))
        self.assertEqual((summary.pickup_commodity, summary.pickup_count), ("Personal Weapons", 32))

    def test_a_mission_without_the_station_still_works(self) -> None:
        self.assertEqual(all_missions.MissionSummary.from_event(_event()).pickup_station, "")

    def test_a_collect_mission_is_still_bought(self) -> None:
        summary = all_missions.MissionSummary.from_event(_event("Mission_Collect_Industrial", "$Gold_Name;", 20))
        self.assertEqual((summary.needed_commodity_count, summary.pickup_commodity), (20, ""))


class NeedsTests(unittest.TestCase):
    def test_pickups_are_listed_after_the_market_needs_and_not_looked_up(self) -> None:
        missions = [all_missions.MissionSummary.from_event(_at(_event())),
                    all_missions.MissionSummary.from_event(_at(_event(count=48, MissionID=2))),
                    all_missions.MissionSummary.from_event(_event("Mission_Collect_Industrial", "$Gold_Name;", 20, MissionID=3, Commodity_Localised="Gold"))]
        needs = mission_sources.needs_from(missions)
        self.assertEqual([(n.commodity, n.tons, n.missions, n.pickup) for n in needs],
                         [("Gold", 20, 1, None), ("Personal Weapons", 180, 2, STATION)])
        self.assertEqual(needs[-1].pickup_pad, "Medium")

    def test_different_stations_are_separate_pickups(self) -> None:
        missions = [all_missions.MissionSummary.from_event(_at(_event(), "Alpha")),
                    all_missions.MissionSummary.from_event(_at(_event(MissionID=2), "Beta"))]
        self.assertEqual(sorted(n.pickup for n in mission_sources.needs_from(missions)), ["Alpha", "Beta"])

    def test_lookup_skips_pickups(self) -> None:
        calls = []
        pick = mission_sources.Need("Personal Weapons", 180, 2, "", STATION)
        mission_sources.lookup([pick], mission_sources.HERE, "Sol", mission_sources.Options(100, None, True, True),
                               search=lambda *a, **k: calls.append(a), pause=lambda _s: None)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
