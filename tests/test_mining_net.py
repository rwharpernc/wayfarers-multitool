"""What the limpets a run launched cost, and the "after limpets" figures built on it (mining_history.py `BuyDrones` handling, mining_history_data.py): each limpet launched is charged at the
price last paid for limpets, a price carries across journals, a limpet launched before any price was known is counted and left out of the cost, and the window's tiles, sales block and run
table show the net."""
from __future__ import annotations

import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_mining_history import Fixture, line      # noqa: E402


class Journals(Fixture):
    def buy(self, minute, count=10, price=101, **extra):
        fields = dict(event="BuyDrones", Type="Drones", Count=count, BuyPrice=price, TotalCost=count * price)
        fields.update(extra)
        return line(timestamp=self.ts(minute), **fields)

    def trip(self, buys=(), launches=("Prospector", "Collection", "Collection"), sell=400000, start=0):
        """One undock-to-dock trip: `buys` are BuyDrones lines placed before the undocking, `launches` the limpets launched while mining."""
        lines = [line(timestamp=self.ts(start), event="Commander", Name="Test Cmdr")] + list(buys)
        lines += [line(timestamp=self.ts(start + 1), event="Undocked"),
                  line(timestamp=self.ts(start + 5), event="SupercruiseExit", StarSystem="HIP 1", Body="HIP 1 2 A Ring", BodyType="PlanetaryRing")]
        minute = start + 6
        for kind in launches:
            lines.append(line(timestamp=self.ts(minute), event="LaunchDrone", Type=kind))
            minute += 1
        lines += [line(timestamp=self.ts(minute), event="MiningRefined", Type_Localised="Platinum"),
                  line(timestamp=self.ts(minute + 1), event="MiningRefined", Type_Localised="Platinum"),
                  line(timestamp=self.ts(start + 30), event="Docked")]
        if sell:
            lines.append(line(timestamp=self.ts(start + 31), event="MarketSell", Type="platinum", Type_Localised="Platinum", Count=2, TotalSale=sell))
        return lines

    def runs(self, lines, prices=None):
        return self.H.runs_from([json.loads(x) for x in lines], "J1.log", None, None, prices)


class CostTests(Journals):
    def test_each_limpet_launched_costs_the_price_last_paid(self):
        run, = self.runs(self.trip(buys=[self.buy(0, price=101)]))
        self.assertEqual((run["limpet_cost"], run["limpet_unpriced"]), (303, 0))            # three launched at 101

    def test_the_price_changes_with_each_purchase(self):
        lines = [line(timestamp=self.ts(0), event="Commander", Name="Test Cmdr"), self.buy(0, price=101), line(timestamp=self.ts(1), event="Undocked"),
                 line(timestamp=self.ts(6), event="LaunchDrone", Type="Prospector"), self.buy(7, price=120),
                 line(timestamp=self.ts(8), event="LaunchDrone", Type="Collection"), line(timestamp=self.ts(9), event="MiningRefined", Type_Localised="Gold"),
                 line(timestamp=self.ts(30), event="Docked")]
        run, = self.runs(lines)
        self.assertEqual((run["limpet_cost"], run["limpet_unpriced"]), (101 + 120, 0))          # each launch at the price last paid before it

    def test_launches_before_any_price_is_known_are_counted_not_charged(self):
        run, = self.runs(self.trip())
        self.assertEqual((run["limpet_cost"], run["limpet_unpriced"]), (0, 3))

    def test_the_price_carries_into_the_next_journal(self):
        prices = {"unit": 0}
        self.runs(self.trip(buys=[self.buy(0, price=99)], launches=()), prices)
        self.assertEqual(prices["unit"], 99)
        run, = self.runs(self.trip(start=40), prices)
        self.assertEqual((run["limpet_cost"], run["limpet_unpriced"]), (297, 0))

    def test_an_event_with_no_price_changes_nothing(self):
        prices = {"unit": 90}
        self.runs([line(timestamp=self.ts(0), event="BuyDrones", Type="Drones", Count=5)], prices)
        self.assertEqual(prices["unit"], 90)

    def test_a_missing_buy_price_is_worked_out_from_the_total(self):
        self.assertEqual(self.H.limpet_price({"Count": 4, "TotalCost": 404}), 101)
        self.assertEqual(self.H.limpet_price({"BuyPrice": 7, "Count": 4, "TotalCost": 404}), 7)
        self.assertEqual(self.H.limpet_price({"BuyPrice": "x", "Count": 0}), 0)
        self.assertEqual(self.H.limpet_price({"BuyPrice": True}), 0)

    def test_buying_limpets_does_not_start_a_run(self):
        self.assertEqual(self.runs([line(timestamp=self.ts(1), event="Undocked"), self.buy(2), line(timestamp=self.ts(5), event="Docked")]), [])


class NetTests(Journals):
    def one_run(self, **kw):
        run, = self.runs(self.trip(buys=[self.buy(0, price=101)], **kw))
        return run

    def test_net_is_earned_less_the_limpets(self):
        run = self.one_run()
        self.assertEqual((self.D.earned(run), self.D.limpet_cost(run), self.D.net(run)), (400000, 303, 399697))

    def test_the_overview_gets_a_tile(self):
        tiles = {t.caption: t.value for t in self.D.overview_tiles([self.one_run()])}
        self.assertEqual(tiles["credits from sales"], "400k")
        self.assertEqual(tiles["credits after limpets"], "400k")

    def test_a_run_not_sold_yet_shows_its_cost_as_a_loss_in_the_totals_and_a_dash_in_the_table(self):
        run = self.one_run(sell=0)
        self.assertEqual(self.D.net(run), -303)
        self.assertEqual(self.D.signed_credits(-303), "-303")
        self.assertEqual(self.D.signed_credits(-2_500_000), "-2.5M")
        cells = self.D.run_table([run]).rows[0].cells
        self.assertEqual(cells[-1], self.D.DASH)

    def test_the_run_table_has_the_net_column_and_marks_an_unpriced_run(self):
        table = self.D.run_table([self.one_run()])
        self.assertEqual(table.columns[-1][1], "After limpets")
        self.assertEqual(table.rows[0].cells[-1], "400k")
        unpriced, = self.runs(self.trip())
        self.assertEqual(self.D.run_table([unpriced]).rows[0].cells[-1], "~400k")

    def test_the_sales_block_shows_the_cost_and_the_net(self):
        fields = dict(self.D.sales_fields([self.one_run()]))
        self.assertEqual(fields["Limpets launched cost"], "303")
        self.assertEqual(fields["Credits after limpets"], "400k")
        self.assertIn("After limpets per mining hour", fields)
        self.assertIn("fuel, repairs and ammunition are not", fields["Note"])

    def test_the_sales_block_says_how_many_were_unpriced(self):
        unpriced, = self.runs(self.trip())
        fields = dict(self.D.sales_fields([unpriced]))
        self.assertEqual(fields["Limpets launched cost"], "- (and 3 launched with no price known)")

    def test_a_history_with_no_limpets_has_no_extra_lines(self):
        run, = self.runs(self.trip(launches=()))
        self.assertNotIn("Credits after limpets", dict(self.D.sales_fields([run])))

    def test_the_surface_half_has_no_limpet_cost(self):
        run = self.one_run()
        run["srv"] = {"Platinum": 2}
        half, = self.D.for_mode([run], self.D.SURFACE)
        self.assertEqual((self.D.limpet_cost(half), self.D.limpets_unpriced(half)), (0, 0))
        self.assertNotIn("credits after limpets", [t.caption for t in self.D.overview_tiles([half], self.D.SURFACE)])
        self.assertNotIn("After limpets", [c[1] for c in self.D.run_table([half], self.D.SURFACE).columns])

    def test_the_totals_add_up_across_runs(self):
        a = self.one_run()
        b = self.one_run(sell=100000)
        t = self.D.Totals([a, b])
        self.assertEqual((t.limpet_cost, t.net, t.unpriced), (606, 500000 - 606, 0))

    def test_a_run_saved_before_the_cost_existed_reads_as_no_cost(self):
        run = self.one_run()
        del run["limpet_cost"], run["limpet_unpriced"]
        self.assertEqual((self.D.limpet_cost(run), self.D.net(run)), (0, 400000))


class HistoryTests(Journals):
    def history(self):
        history = self.H.MiningHistory()
        history.pause = 0
        history.start(self.state)
        history._cmdr = "Test Cmdr"
        return history

    def test_the_price_paid_in_one_journal_charges_the_launches_in_the_next_and_is_saved(self):
        self.journal("Journal.2026-10-16T100000.01.log", self.trip(buys=[self.buy(0, price=101)], launches=()))
        self.journal("Journal.2026-10-17T100000.01.log", self.trip())
        newest = self.journal("Journal.2026-10-18T100000.01.log", self.trip(start=40))
        os.utime(newest, (time.time(), time.time() + 5))
        history = self.history()
        history.refresh(self.folder, wait=True)
        costs = [(r["limpet_cost"], r["limpet_unpriced"]) for r in history.runs()]
        self.assertEqual(costs, [(0, 0), (303, 0), (303, 0)])          # the first journal launched none; the saved and the live one are both charged at the price it paid
        self.assertEqual(history._payload()["limpet_price"], 101)

    def test_runs_saved_before_the_cost_existed_are_read_again_once(self):
        self.assertEqual(self.H.RUNS_VERSION, 5)
        self.assertIn("BuyDrones", self.H.EVENTS)
        self.journal("Journal.2026-10-16T100000.01.log", self.trip(buys=[self.buy(0)]))
        newest = self.journal("Journal.2026-10-17T100000.01.log", self.trip(start=40))
        os.utime(newest, (time.time(), time.time() + 5))
        history = self.history()
        history.refresh(self.folder, wait=True)
        payload = history._payload()
        payload["runs_v"], payload["limpet_price"] = 4, 55
        for run in payload["runs"]:
            run.pop("limpet_cost", None)
        later = self.history()
        later._store = history._store
        later.refresh(self.folder, wait=True)
        self.assertEqual(later._payload()["runs_v"], 5)
        self.assertEqual(later._payload()["runs"][0]["limpet_cost"], 303)           # worked out again from the journal, not from the old price


if __name__ == "__main__":
    unittest.main()
