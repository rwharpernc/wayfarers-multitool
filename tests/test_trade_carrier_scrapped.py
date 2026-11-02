"""A decommissioned carrier goes when the game scraps it: its record is dropped, a canceled decommission keeps it, and a `CarrierStats` that only says
"pending" (no date) is trusted for the game's seven days. No EDMC runtime and no network needed."""
from __future__ import annotations

import calendar
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import trade_carrier as carrier  # noqa: E402
from plugin import trade_carrier_ops as ops  # noqa: E402

FLEET = carrier.FLEET


def epoch(stamp: str) -> int:
    return calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ"))


def feed(tracker: carrier.CarrierTracker, **entry) -> None:
    tracker.feed(entry)


def tracker_with_carrier(pending: bool = False, stamp: str = "2026-10-09T10:00:00Z") -> carrier.CarrierTracker:
    tracker = carrier.CarrierTracker()
    feed(tracker, event="Commander", Name="Bocheaux")
    feed(tracker, event="CarrierBuy", CarrierType=FLEET, CarrierID=111, timestamp=stamp, Callsign="ABC-123")
    feed(tracker, event="CarrierStats", CarrierType=FLEET, CarrierID=111, Callsign="ABC-123", Name="ELDER", FuelLevel=500,
         PendingDecommission=pending, timestamp=stamp,
         SpaceUsage={"TotalCapacity": 25000, "Crew": 100, "Cargo": 50, "CargoSpaceReserved": 0, "ShipPacks": 0, "ModulePacks": 0, "FreeSpace": 24850})
    return tracker


class ScrappedCarrierTests(unittest.TestCase):
    def test_the_event_carries_the_scrap_time_and_the_carrier_goes_after_it(self) -> None:
        tracker = tracker_with_carrier()
        scrap = epoch("2026-10-29T07:00:00Z")
        feed(tracker, event="CarrierDecommission", CarrierType=FLEET, CarrierID=111, ScrapTime=scrap, timestamp="2026-10-24T16:06:17Z")
        record = tracker.records["bocheaux"][FLEET]
        self.assertTrue(record["decommission"])
        self.assertEqual(record["scrap_at"], scrap)
        self.assertFalse(carrier.prune(tracker.records, scrap - 60))             # still here until the scrap time
        self.assertIn(FLEET, tracker.records["bocheaux"])
        self.assertTrue(carrier.prune(tracker.records, scrap))
        self.assertNotIn("bocheaux", tracker.records)                           # and the commander is left with none

    def test_canceling_keeps_the_carrier(self) -> None:
        tracker = tracker_with_carrier()
        scrap = epoch("2026-10-29T07:00:00Z")
        feed(tracker, event="CarrierDecommission", CarrierType=FLEET, CarrierID=111, ScrapTime=scrap, timestamp="2026-10-24T16:06:17Z")
        feed(tracker, event="CarrierCancelDecommission", CarrierType=FLEET, CarrierID=111, timestamp="2026-10-25T09:00:00Z")
        record = tracker.records["bocheaux"][FLEET]
        self.assertFalse(record["decommission"])
        self.assertNotIn("scrap_at", record)
        self.assertFalse(carrier.prune(tracker.records, scrap + 10 * 86400))

    def test_a_stats_report_without_a_date_is_trusted_for_seven_days(self) -> None:
        tracker = tracker_with_carrier(pending=True, stamp="2026-10-25T13:05:26Z")
        start = epoch("2026-10-25T13:05:26Z")
        self.assertFalse(ops.is_scrapped(tracker.records["bocheaux"][FLEET], start + 6 * 86400))
        self.assertTrue(ops.is_scrapped(tracker.records["bocheaux"][FLEET], start + 7 * 86400))

    def test_a_carrier_not_being_scrapped_never_expires(self) -> None:
        tracker = tracker_with_carrier()
        self.assertFalse(carrier.prune(tracker.records, epoch("2030-01-01T00:00:00Z")))

    def test_an_older_decommission_does_not_undo_a_newer_cancel(self) -> None:
        tracker = tracker_with_carrier()
        feed(tracker, event="CarrierCancelDecommission", CarrierType=FLEET, CarrierID=111, timestamp="2026-10-25T09:00:00Z")
        feed(tracker, event="CarrierDecommission", CarrierType=FLEET, CarrierID=111, ScrapTime=epoch("2026-10-29T07:00:00Z"),
             timestamp="2026-10-24T16:06:17Z")                                    # a journal read late
        self.assertFalse(tracker.records["bocheaux"][FLEET]["decommission"])

    def test_a_new_purchase_after_a_scrapped_one_is_a_fresh_record(self) -> None:
        tracker = tracker_with_carrier()
        feed(tracker, event="CarrierDecommission", CarrierType=FLEET, CarrierID=111, ScrapTime=epoch("2026-10-29T07:00:00Z"),
             timestamp="2026-10-24T16:06:17Z")
        carrier.prune(tracker.records, epoch("2026-10-30T00:00:00Z"))
        feed(tracker, event="Commander", Name="Bocheaux")
        feed(tracker, event="CarrierBuy", CarrierType=FLEET, CarrierID=222, timestamp="2026-10-31T10:00:00Z", Callsign="XYZ-999")
        self.assertEqual(tracker.records["bocheaux"][FLEET]["id"], 222)

    def test_a_replay_with_a_new_purchase_replaces_the_scrapped_carrier_without_a_prune(self) -> None:
        tracker = tracker_with_carrier()
        feed(tracker, event="CarrierDecommission", CarrierType=FLEET, CarrierID=111, ScrapTime=epoch("2026-10-29T07:00:00Z"),
             timestamp="2026-10-24T16:06:17Z")
        feed(tracker, event="CarrierBuy", CarrierType=FLEET, CarrierID=222, timestamp="2026-10-31T10:00:00Z", Callsign="XYZ-999")
        self.assertEqual(tracker.records["bocheaux"][FLEET]["id"], 222)
        feed(tracker, event="CarrierDepositFuel", CarrierType=FLEET, CarrierID=222, Total=300, timestamp="2026-10-31T11:00:00Z")
        self.assertEqual(tracker.records["bocheaux"][FLEET].get("fuel"), 300)       # the new carrier's events are kept

    def test_the_same_purchase_read_twice_changes_nothing(self) -> None:
        tracker = tracker_with_carrier()
        before = dict(tracker.records["bocheaux"][FLEET])
        feed(tracker, event="CarrierBuy", CarrierType=FLEET, CarrierID=111, timestamp="2026-10-09T10:00:00Z", Callsign="ABC-123")
        self.assertEqual(tracker.records["bocheaux"][FLEET], before)

    def test_an_event_of_a_new_carrier_replaces_a_scrapped_one_when_the_purchase_was_not_seen(self) -> None:
        tracker = tracker_with_carrier()
        feed(tracker, event="CarrierDecommission", CarrierType=FLEET, CarrierID=111, ScrapTime=epoch("2026-10-29T07:00:00Z"),
             timestamp="2026-10-24T16:06:17Z")
        feed(tracker, event="CarrierLocation", CarrierType=FLEET, CarrierID=222, StarSystem="Sol", SystemAddress=1, timestamp="2026-10-31T11:00:00Z")
        self.assertEqual(tracker.records["bocheaux"][FLEET]["id"], 222)

    def test_an_event_of_another_carrier_keeps_a_carrier_that_is_not_scrapped(self) -> None:
        tracker = tracker_with_carrier()
        feed(tracker, event="CarrierLocation", CarrierType=FLEET, CarrierID=222, StarSystem="Sol", SystemAddress=1, timestamp="2026-10-31T11:00:00Z")
        self.assertEqual(tracker.records["bocheaux"][FLEET]["id"], 111)

    def test_the_journal_lines_are_picked_up(self) -> None:
        for event in ("CarrierDecommission", "CarrierCancelDecommission"):
            self.assertTrue(carrier._WANTED.search(f'{{ "timestamp":"x", "event":"{event}", "CarrierID":1 }}'), event)


if __name__ == "__main__":
    unittest.main()
