"""
Unit tests for plugin/sale_merits.py: pairing a sale with the Powerplay merits that follow it, the CSV log, and the journal replay.

The replay needs powerplay.PowerplayTracker, which lives in a module that imports EDMC; it is imported here with stand-ins for those modules
(removed again afterwards). Run with:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import csv
import importlib
import json
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"  # type: ignore[attr-defined]
    _stub.config = types.SimpleNamespace(get_str=lambda *_a, **_k: "")  # type: ignore[attr-defined]
    sys.modules["config"] = _stub


class _Anything(types.ModuleType):
    def __getattr__(self, name: str):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock(name=f"{self.__name__}.{name}")


_EDMC = ("theme", "myNotebook", "monitor", "ttkHyperlinkLabel", "edmc_data", "plug", "companion", "EDMCLogging",
         "l10n", "timeout_session", "protocol", "prefs", "killswitch", "Tooltips", "ttkDefaults", "requests")
with mock.patch.dict(sys.modules, {name: _Anything(name) for name in _EDMC}):
    powerplay = importlib.import_module("plugin.powerplay")

from plugin import sale_merits as S  # noqa: E402

ME = "Pranav Antal"
CTX = S.Context(power=ME, system="Ngurii", state="Fortified", holder=ME, activity="reinforcement")


def at(second: int, minute: int = 0) -> str:
    return f"2026-10-02T12:{minute:02d}:{second:02d}Z"


def sell(second: int, *, name: str = "Silver", count: int = 100, price: int = 5000, paid: int = 3000, minute: int = 0, **extra) -> dict:
    entry = {"timestamp": at(second, minute), "event": "MarketSell", "Type": name.lower(), "Type_Localised": name, "Count": count,
             "SellPrice": price, "AvgPricePaid": paid, "TotalSale": price * count}
    entry.update(extra)
    return entry


def merit(second: int, gained: int, minute: int = 0) -> dict:
    return {"timestamp": at(second, minute), "event": "PowerplayMerits", "Power": ME, "MeritsGained": gained, "TotalMerits": 1000 + gained}


def run(events, context=lambda: CTX, tracker=None):
    """Feed (kind, entry) pairs: kind 'e' for an ordinary event, 'm' for a merit event. Returns the finished sales."""
    tracker = tracker or S.SaleTracker("Bocheaux")
    done = []
    for kind, entry in events:
        done += tracker.feed(entry, context) if kind == "e" else tracker.merit(entry, entry["MeritsGained"])
    return done + tracker.flush()


class PairingTests(unittest.TestCase):
    def test_a_sale_claims_the_merits_that_follow_it(self):
        sales = run([("e", sell(0)), ("m", merit(2, 80))])
        self.assertEqual(len(sales), 1)
        self.assertEqual((sales[0].merits, sales[0].merit_events), (80, 1))

    def test_further_merits_close_together_belong_to_the_same_sale(self):
        sales = run([("e", sell(0)), ("m", merit(2, 40)), ("m", merit(4, 30)), ("m", merit(6, 10))])
        self.assertEqual((sales[0].merits, sales[0].merit_events), (80, 3))

    def test_a_merit_after_the_window_is_not_taken(self):
        sales = run([("e", sell(0)), ("m", merit(7, 50))])
        self.assertEqual((sales[0].merits, sales[0].merit_events), (0, 0))

    def test_a_chain_stops_when_the_gap_is_too_long(self):
        sales = run([("e", sell(0)), ("m", merit(1, 40)), ("m", merit(10, 30))])
        self.assertEqual(sales[0].merits, 40)

    def test_the_next_sale_closes_the_one_before(self):
        sales = run([("e", sell(0, name="Silver")), ("e", sell(1, name="Gold")), ("m", merit(2, 60))])
        self.assertEqual([(s.commodity, s.merits) for s in sales], [("Silver", 0), ("Gold", 60)])

    def test_an_unrelated_event_after_the_window_closes_the_sale_early(self):
        tracker = S.SaleTracker("Bocheaux")
        tracker.feed(sell(0), lambda: CTX)
        done = tracker.feed({"timestamp": at(30), "event": "Docked"}, lambda: CTX)
        self.assertEqual(len(done), 1)

    def test_a_sale_with_no_merits_is_still_recorded(self):
        sales = run([("e", sell(0))])
        self.assertEqual((sales[0].merits, sales[0].merit_events), (0, 0))

    def test_a_merit_claimed_by_a_hand_in_is_not_taken(self):
        tracker = S.SaleTracker("Bocheaux")
        tracker.feed(sell(0), lambda: CTX)
        tracker.merit(merit(1, 500), 500, delivery=True)
        self.assertEqual(tracker.flush()[0].merits, 0)

    def test_not_pledged_or_no_powerplay_state_records_nothing(self):
        self.assertEqual(run([("e", sell(0))], context=lambda: None), [])
        no_state = S.Context(power=ME, system="Ngurii", state="", holder="", activity="unknown")
        self.assertEqual(run([("e", sell(0))], context=lambda: no_state), [])
        no_power = S.Context(power="", system="Ngurii", state="Fortified", holder="", activity="unknown")
        self.assertEqual(run([("e", sell(0))], context=lambda: no_power), [])

    def test_a_sale_of_nothing_is_ignored(self):
        self.assertEqual(run([("e", sell(0, count=0))]), [])

    def test_profit_and_margin(self):
        sale = run([("e", sell(0, count=10, price=1400, paid=1000))])[0]
        self.assertEqual((sale.profit, sale.margin_pct), (4000, 40.0))

    def test_goods_with_no_cost_have_no_margin(self):
        sale = run([("e", sell(0, paid=0))])[0]
        self.assertIsNone(sale.margin_pct)
        self.assertEqual(sale.row()[COLUMN["margin_pct"]], "")

    def test_where_it_was_bought_and_whether_it_was_mined(self):
        bought = {"timestamp": at(0, 0), "event": "MarketBuy", "Type": "silver", "Count": 5}
        refined = {"timestamp": at(1, 0), "event": "MiningRefined", "Type": "$gold_name;"}
        mined_sale = sell(30, name="Gold")
        mined_sale["Type"] = "gold"
        sales = run([("e", bought), ("e", refined), ("e", sell(10)), ("e", mined_sale)])
        self.assertEqual([(s.commodity, s.bought_in, s.mined) for s in sales], [("Silver", "Ngurii", False), ("Gold", "", True)])

    def test_the_station_is_known_while_docked(self):
        docked = {"timestamp": at(0), "event": "Docked", "StationName": "Ngurii Hub"}
        sales = run([("e", docked), ("e", sell(1)), ("e", {"timestamp": at(50), "event": "Undocked"}), ("e", sell(55))])
        self.assertEqual([s.station for s in sales], ["Ngurii Hub", ""])

    def test_black_market_goods_are_marked(self):
        self.assertTrue(run([("e", sell(0, BlackMarket=True))])[0].black_market)

    def test_a_new_file_starts_fresh(self):
        tracker = S.SaleTracker("Bocheaux")
        tracker.feed(sell(0), lambda: CTX)
        done = tracker.feed({"timestamp": at(1), "event": "Fileheader"}, lambda: CTX)
        self.assertEqual(len(done), 1)


COLUMN = {name: index for index, name in enumerate(S.COLUMNS)}


class LogTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, S.LOG_FILENAME)

    def tearDown(self):
        self.dir.cleanup()

    def _sales(self):
        return run([("e", sell(0)), ("m", merit(1, 80)), ("e", sell(20, name="Gold")), ("m", merit(21, 0 + 40))])

    def test_header_and_rows_are_written(self):
        log = S.SaleLog(self.path)
        self.assertEqual(log.add(self._sales()), 2)
        with open(self.path, newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(tuple(rows[0]), S.COLUMNS)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1][COLUMN["merits"]], "80")
        self.assertEqual(rows[1][COLUMN["mined"]], "no")

    def test_a_sale_is_never_written_twice(self):
        log = S.SaleLog(self.path)
        log.add(self._sales())
        self.assertEqual(log.add(self._sales()), 0)
        self.assertEqual(S.SaleLog(self.path).add(self._sales()), 0)          # nor after a restart
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(len(handle.readlines()), 3)

    def test_the_newest_sale_of_each_commander_is_known_even_after_a_restart(self):
        log = S.SaleLog(self.path)
        self.assertEqual(log.latest("Bocheaux"), "")
        log.add(self._sales())
        self.assertEqual(log.latest("BOCHEAUX"), at(20))
        self.assertEqual(S.SaleLog(self.path).latest("bocheaux"), at(20))
        self.assertEqual(S.SaleLog(self.path).latest("Someone Else"), "")

    def test_the_rank_and_cycle_are_in_the_row(self):
        ranked = S.Context(power=ME, system="Ngurii", state="Fortified", holder=ME, activity="reinforcement", rank=12)
        sale = run([("e", sell(0)), ("m", merit(1, 80))], context=lambda: ranked)[0]
        row = sale.row()
        self.assertEqual((row[COLUMN["rank"]], row[COLUMN["cycle"]]), ("12", 101))        # 2026-10-02 is in cycle 101
        unknown = run([("e", sell(0))])[0].row()
        self.assertEqual(unknown[COLUMN["rank"]], S.UNKNOWN_RANK)

    def test_the_cycle_follows_the_thursday_boundary(self):
        self.assertEqual(S.cycle_of("2026-10-01T06:59:59Z"), 100)
        self.assertEqual(S.cycle_of("2026-10-01T07:00:00Z"), 101)
        self.assertEqual(S.cycle_of("2026-10-08T07:00:00Z"), 102)
        self.assertIsNone(S.cycle_of("not a time"))

    def _old_file(self, rank_known=False):
        """A log as the first version wrote it, without the rank and cycle columns."""
        old = [name for name in S.COLUMNS if name not in ("rank", "cycle")]
        sale = self._sales()[0]
        cells = dict(zip(S.COLUMNS, [str(c) for c in sale.row()]))
        with open(self.path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(old)
            writer.writerow([cells[name] for name in old])

    def test_an_older_file_is_rewritten_with_the_new_columns(self):
        self._old_file()
        log = S.SaleLog(self.path)
        self.assertEqual(log.add(self._sales()[1:]), 1)
        with open(self.path, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["cycle"], "101")
        self.assertEqual(rows[0]["rank"], "")                                  # to be filled by a journal read
        self.assertEqual(rows[1]["rank"], S.UNKNOWN_RANK)                       # written now, rank not known
        self.assertEqual(rows[0]["commodity"], "Silver")

    def test_an_older_file_is_migrated_even_when_nothing_new_arrives(self):
        self._old_file()
        S.SaleLog(self.path).add([])
        with open(self.path, newline="", encoding="utf-8") as handle:
            self.assertEqual(tuple(next(csv.reader(handle))), S.COLUMNS)

    def test_a_blank_rank_is_filled_in_by_a_later_read_and_then_left_alone(self):
        self._old_file()
        log = S.SaleLog(self.path)
        self.assertTrue(log.missing_rank("Bocheaux"))
        ranked = S.Context(power=ME, system="Ngurii", state="Fortified", holder=ME, activity="reinforcement", rank=9)
        found = run([("e", sell(0)), ("m", merit(1, 80))], context=lambda: ranked)
        self.assertEqual(log.add(found), 0)                                    # nothing new, one rank filled
        self.assertFalse(log.missing_rank("Bocheaux"))
        with open(self.path, newline="", encoding="utf-8") as handle:
            self.assertEqual(next(csv.DictReader(handle))["rank"], "9")
        self.assertEqual(S.SaleLog(self.path).add(found), 0)

    def test_settling_marks_a_rank_the_journals_never_had_as_unknown(self):
        self._old_file()
        log = S.SaleLog(self.path)
        log.settle_rank("bocheaux")
        self.assertFalse(log.missing_rank("Bocheaux"))
        with open(self.path, newline="", encoding="utf-8") as handle:
            self.assertEqual(next(csv.DictReader(handle))["rank"], S.UNKNOWN_RANK)

    def test_a_file_that_cannot_be_written_is_survived(self):
        log = S.SaleLog(os.path.join(self.dir.name, "missing", S.LOG_FILENAME))
        self.assertEqual(log.add(self._sales()), 0)


class ReplayTests(unittest.TestCase):
    def _journal(self, extra):
        entries = [
            {"timestamp": at(0, 0), "event": "Fileheader"},
            {"timestamp": at(0, 0), "event": "Commander", "Name": "Bocheaux"},
            {"timestamp": at(0, 0), "event": "LoadGame", "Commander": "Bocheaux"},
            {"timestamp": at(0, 0), "event": "Powerplay", "Power": ME, "Rank": 10, "Merits": 5},
            {"timestamp": at(0, 1), "event": "FSDJump", "StarSystem": "Ngurii", "PowerplayState": "Fortified",
             "ControllingPower": ME, "Powers": [ME]},
        ]
        return entries + extra

    def test_a_sale_in_a_powerplay_system_gets_its_merits_and_state(self):
        sales = S.replay_sales(self._journal([sell(0, minute=5), merit(2, 90, minute=5)]), "Bocheaux", powerplay.PowerplayTracker)
        self.assertEqual(len(sales), 1)
        self.assertEqual((sales[0].merits, sales[0].state, sales[0].holder, sales[0].activity, sales[0].system),
                         (90, "Fortified", ME, "reinforcement", "Ngurii"))

    def test_the_rank_comes_from_the_journal(self):
        sales = S.replay_sales(self._journal([sell(0, minute=5)]), "Bocheaux", powerplay.PowerplayTracker)
        self.assertEqual(sales[0].rank, 10)
        later = self._journal([{"timestamp": at(0, 3), "event": "PowerplayRank", "Power": ME, "Rank": 11}, sell(0, minute=5)])
        self.assertEqual(S.replay_sales(later, "Bocheaux", powerplay.PowerplayTracker)[0].rank, 11)

    def test_another_commanders_sales_are_not_included(self):
        entries = self._journal([sell(0, minute=5)])
        self.assertEqual(S.replay_sales(entries, "Someone Else", powerplay.PowerplayTracker), [])

    def test_a_sale_in_a_system_with_no_powerplay_state_is_not_recorded(self):
        entries = self._journal([])
        entries[4] = {"timestamp": at(0, 1), "event": "FSDJump", "StarSystem": "Sol"}
        self.assertEqual(S.replay_sales(entries + [sell(0, minute=5)], "Bocheaux", powerplay.PowerplayTracker), [])

    def test_the_merits_of_a_hand_in_are_not_taken_by_a_sale(self):
        deliver = {"timestamp": at(0, 5), "event": "PowerplayDeliver", "Power": ME, "Type": "markedslaves", "Count": 8}
        sales = S.replay_sales(self._journal([sell(1, minute=5), deliver, merit(2, 3600, minute=5)]), "Bocheaux", powerplay.PowerplayTracker)
        self.assertEqual(sales[0].merits, 0)

    def test_scan_journals_reads_files_oldest_first_and_reports_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            for name, minute in (("Journal.2026-10-02T120000.01.log", 5), ("Journal.2026-10-03T120000.01.log", 7)):
                with open(os.path.join(folder, name), "w", encoding="utf-8") as handle:
                    for entry in self._journal([sell(0, minute=minute), merit(1, 70, minute=minute)]):
                        handle.write(json.dumps(entry) + "\n")
            with open(os.path.join(folder, "notes.txt"), "w", encoding="utf-8") as handle:
                handle.write("not a journal")
            seen = []
            sales = S.scan_journals(folder, "Bocheaux", powerplay.PowerplayTracker, lambda done, total: seen.append((done, total)))
        self.assertEqual([(s.time, s.merits) for s in sales], [(at(0, 5), 70), (at(0, 7), 70)])
        self.assertEqual(seen, [(1, 2), (2, 2)])

    def test_since_skips_journals_last_written_before_it(self):
        from datetime import datetime, timezone
        with tempfile.TemporaryDirectory() as folder:
            for name, minute, age in (("Journal.2026-10-02T120000.01.log", 5, 10 * 86400), ("Journal.2026-10-03T120000.01.log", 7, 0)):
                path = os.path.join(folder, name)
                with open(path, "w", encoding="utf-8") as handle:
                    for entry in self._journal([sell(0, minute=minute), merit(1, 70, minute=minute)]):
                        handle.write(json.dumps(entry) + "\n")
                stamp = datetime.now(timezone.utc).timestamp() - age
                os.utime(path, (stamp, stamp))
            since = datetime.fromtimestamp(datetime.now(timezone.utc).timestamp() - 86400, timezone.utc)
            recent = S.scan_journals(folder, "Bocheaux", powerplay.PowerplayTracker, since=since)
            everything = S.scan_journals(folder, "Bocheaux", powerplay.PowerplayTracker)
        self.assertEqual([s.time for s in recent], [at(0, 7)])
        self.assertEqual(len(everything), 2)

    def test_a_missing_folder_gives_nothing(self):
        self.assertEqual(S.scan_journals("/nonexistent/wfmt-journals", "Bocheaux", powerplay.PowerplayTracker), [])


if __name__ == "__main__":
    unittest.main()
