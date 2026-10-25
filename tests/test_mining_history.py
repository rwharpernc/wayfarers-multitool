"""The mining history (mining_history.py) and what the Mining History window shows (mining_history_data.py).

Both are pure: a journal walk that turns events into runs, a per-commander saved record that is built in the background, and the rows and tiles worked out from the runs.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def line(**fields):
    return json.dumps(fields)


class Fixture(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType("config")
        config.appname = "EDMarketConnector"
        config.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default, default_journal_dir="")
        patcher = mock.patch.dict(sys.modules, {"config": config, "myNotebook": types.ModuleType("myNotebook")})
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in [m for m in sys.modules if m.startswith("plugin.mining_history") or m in ("plugin.journal_files", "plugin.explore_dashboard_data")]:
            sys.modules.pop(name)
        from plugin import mining_history, mining_history_data
        self.H, self.D = mining_history, mining_history_data
        self.folder = tempfile.mkdtemp()
        self.state = tempfile.mkdtemp()
        self.addCleanup(self._clean)

    def _clean(self):
        for folder in (self.folder, self.state):
            for name in os.listdir(folder):
                os.remove(os.path.join(folder, name))
            os.rmdir(folder)

    def journal(self, name, lines):
        path = os.path.join(self.folder, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return path

    @staticmethod
    def ts(minute, hour=12):
        return f"2026-10-18T{hour:02d}:{minute:02d}:00Z"

    def mining_trip(self, who="Test Cmdr", sell=True, start=0):
        lines = [line(timestamp=self.ts(start), event="Commander", Name=who),
                 line(timestamp=self.ts(start), event="FSDJump", StarSystem="HIP 1", SystemAddress=1),
                 line(timestamp=self.ts(start + 1), event="Undocked"),
                 line(timestamp=self.ts(start + 5), event="SupercruiseExit", StarSystem="HIP 1", Body="HIP 1 2 A Ring", BodyType="PlanetaryRing"),
                 line(timestamp=self.ts(start + 6), event="LaunchDrone", Type="Prospector"),
                 line(timestamp=self.ts(start + 7), event="ProspectedAsteroid", Content="$AsteroidMaterialContent_High;", Content_Localised="Material Content: High",
                      MotherlodeMaterial="Painite"),
                 line(timestamp=self.ts(start + 8), event="ProspectedAsteroid", Content_Localised="Material Content: Low"),
                 line(timestamp=self.ts(start + 9), event="LaunchDrone", Type="Collection"),
                 line(timestamp=self.ts(start + 10), event="MiningRefined", Type="$platinum_name;", Type_Localised="Platinum"),
                 line(timestamp=self.ts(start + 11), event="MiningRefined", Type="$platinum_name;", Type_Localised="Platinum"),
                 line(timestamp=self.ts(start + 12), event="MiningRefined", Type="$osmium_name;"),
                 line(timestamp=self.ts(start + 13), event="AsteroidCracked", Body="HIP 1 2 A Ring"),
                 line(timestamp=self.ts(start + 30), event="Docked")]
        if sell:
            lines += [line(timestamp=self.ts(start + 31), event="MarketSell", Type="platinum", Type_Localised="Platinum", Count=2, TotalSale=400000),
                      line(timestamp=self.ts(start + 32), event="MarketSell", Type="osmium", Count=1, TotalSale=100000)]
        return lines


class WalkTests(Fixture):
    def runs(self, lines):
        return self.H.runs_from([json.loads(x) for x in lines], "J1.log")

    def test_a_trip_becomes_one_run_with_its_prospecting_refining_limpets_and_sales(self):
        run, = self.runs(self.mining_trip())
        self.assertEqual((run["system"], run["ring"]), ("HIP 1", "HIP 1 2 A Ring"))
        self.assertEqual(run["prospected"], {"Low": 1, "Medium": 0, "High": 1})
        self.assertEqual((run["motherlode"], run["cracked"]), (1, 1))
        self.assertEqual(run["refined"], {"Platinum": 2, "Osmium": 1})          # a commodity with no localized name is read from its raw name
        self.assertEqual(run["limpets"], {"Prospector": 1, "Collection": 1})
        self.assertEqual(run["sold"], {"Platinum": [2, 400000], "Osmium": [1, 100000]})
        self.assertEqual((run["first"], run["last"], run["end"]), (self.ts(6), self.ts(13), self.ts(30)))

    def test_a_sale_of_something_never_mined_is_ignored(self):
        lines = self.mining_trip(sell=False) + [line(timestamp=self.ts(40), event="Undocked"), line(timestamp=self.ts(41), event="MarketSell", Type="x", Count=1, TotalSale=5)]
        run, = self.runs(lines)
        self.assertEqual(run["sold"], {})

    def test_a_trip_with_no_mining_is_not_a_run(self):
        self.assertEqual(self.runs([line(timestamp=self.ts(1), event="Undocked"), line(timestamp=self.ts(5), event="Docked")]), [])

    def test_mining_with_no_undocking_before_it_starts_a_run_of_its_own(self):
        run, = self.runs([line(timestamp=self.ts(2), event="MiningRefined", Type_Localised="Gold"), line(timestamp=self.ts(9), event="MiningRefined", Type_Localised="Gold")])
        self.assertEqual((run["refined"], run["end"]), ({"Gold": 2}, self.ts(9)))          # a run still going at the end of the file ends at its last mining event

    def test_a_ring_is_cleared_when_you_leave_supercruise_somewhere_else(self):
        lines = [line(timestamp=self.ts(1), event="Undocked"),
                 line(timestamp=self.ts(2), event="SupercruiseExit", StarSystem="S", Body="S 1 A Ring", BodyType="PlanetaryRing"),
                 line(timestamp=self.ts(3), event="SupercruiseExit", StarSystem="S", Body="Station", BodyType="Station"),
                 line(timestamp=self.ts(4), event="MiningRefined", Type_Localised="Gold")]
        run, = self.runs(lines)
        self.assertEqual(run["ring"], "")

    def test_a_rock_prospected_again_is_counted_once_as_on_the_panel(self):
        rock = dict(event="ProspectedAsteroid", Materials=[{"Name": "painite", "Proportion": 34.4}], Content_Localised="Material Content: High", MotherlodeMaterial="Painite")
        other = dict(event="ProspectedAsteroid", Materials=[{"Name": "iron", "Proportion": 5.0}], Content_Localised="Material Content: Low")
        lines = [line(timestamp=self.ts(1), event="Undocked"), line(timestamp=self.ts(2), **rock), line(timestamp=self.ts(3), **rock),
                 line(timestamp=self.ts(4), **other), line(timestamp=self.ts(5), **rock),
                 line(timestamp=self.ts(6), event="Docked"), line(timestamp=self.ts(7), event="Undocked"), line(timestamp=self.ts(8), **rock)]
        first, second = self.runs(lines)
        self.assertEqual(first["prospected"], {"Low": 1, "Medium": 0, "High": 1})
        self.assertEqual(first["motherlode"], 1)
        self.assertEqual(second["prospected"]["High"], 1, "the next run counts the rock again")

    def test_a_rock_with_no_materials_is_never_a_repeat(self):
        bare = dict(event="ProspectedAsteroid", Materials=[], Content_Localised="Material Content: Medium")
        run, = self.runs([line(timestamp=self.ts(1), event="Undocked"), line(timestamp=self.ts(2), **bare), line(timestamp=self.ts(3), **bare)])
        self.assertEqual(run["prospected"]["Medium"], 2)

    def test_an_unreadable_grade_is_unknown_not_low(self):
        alto = dict(event="ProspectedAsteroid", Materials=[{"Name": "iron", "Proportion": 5.0}], Content="$AsteroidMaterialContent_Alto;", Content_Localised="Contenido: Alto")
        run, = self.runs([line(timestamp=self.ts(1), event="Undocked"), line(timestamp=self.ts(2), **alto)])
        self.assertEqual(run["prospected"], {"Low": 0, "Medium": 0, "High": 0})
        self.assertEqual(run["ungraded"], 1)
        self.assertTrue(self.H.has_mining(run))

    def test_owner_is_read_from_the_commander_or_loadgame_line(self):
        self.assertEqual(self.H.owner_of([json.loads(line(event="Commander", Name="Test Cmdr"))]), "test cmdr")
        self.assertEqual(self.H.owner_of([json.loads(line(event="LoadGame", Commander="Other"))]), "other")
        self.assertEqual(self.H.owner_of([]), "")


class SalesElsewhereTests(Fixture):
    """Sales are matched to the tons mined, at any station, oldest run first."""

    def sell(self, minute, count, total, name="Platinum"):
        return line(timestamp=self.ts(minute), event="MarketSell", Type=name.lower(), Type_Localised=name, Count=count, TotalSale=total)

    def walk(self, lines):
        return self.H.runs_from([json.loads(x) for x in lines], "J1.log")

    def elsewhere(self):
        """Mine two tons of platinum and one of osmium, dock at the ring station and sell nothing, fly to another station."""
        return (self.mining_trip(sell=False)
                + [line(timestamp=self.ts(40), event="Undocked"), line(timestamp=self.ts(50), event="Docked", StationName="Better Port")])

    def gold_trip(self, start, tons):
        return ([line(timestamp=self.ts(start), event="Undocked")]
                + [line(timestamp=self.ts(start + 1), event="MiningRefined", Type_Localised="Gold")] * tons
                + [line(timestamp=self.ts(start + 5), event="Docked")])

    def test_a_sale_at_another_station_is_credited_to_the_run_that_mined_it(self):
        run, = self.walk(self.elsewhere() + [self.sell(51, 2, 500000), self.sell(52, 1, 90000, "Osmium")])
        self.assertEqual(run["sold"], {"Platinum": [2, 500000], "Osmium": [1, 90000]})
        self.assertEqual(self.D.earned(run), 590000)

    def test_the_commodity_table_and_totals_include_it(self):
        runs = self.walk(self.elsewhere() + [self.sell(51, 2, 500000)])
        row = self.D.commodity_table(runs).rows[0].cells
        self.assertEqual((row[0], row[1], row[2]), ("Platinum", "2", "2"))
        t = self.D.Totals(runs)
        self.assertEqual((t.earned, t.sold), (500000, 2))
        self.assertIsNotNone(t.credit_rate)

    def test_selling_less_than_was_mined_leaves_the_rest_waiting(self):
        carry = {}
        run, = self.H.runs_from([json.loads(x) for x in self.elsewhere() + [self.sell(51, 1, 250000)]], "J1.log", carry, {})
        self.assertEqual(run["sold"], {"Platinum": [1, 250000]})
        self.assertEqual({name: [tons for _key, tons in queue] for name, queue in carry.items()}, {"Platinum": [1], "Osmium": [1]})

    def test_a_later_sale_takes_what_was_left(self):
        run, = self.walk(self.elsewhere() + [self.sell(51, 1, 250000), self.sell(55, 1, 260000)])
        self.assertEqual(run["sold"]["Platinum"], [2, 510000])

    def test_tons_sold_beyond_what_was_mined_earn_nothing(self):
        run, = self.walk(self.elsewhere() + [self.sell(51, 10, 1000000)])
        self.assertEqual(run["sold"]["Platinum"], [2, 200000])          # two of the ten tons, at their unit price

    def test_a_commodity_never_mined_is_ignored(self):
        run, = self.walk(self.elsewhere() + [self.sell(51, 5, 900000, "Gold")])
        self.assertNotIn("Gold", run["sold"])

    def test_the_oldest_run_is_credited_first(self):
        first, second = self.walk(self.gold_trip(0, 3) + self.gold_trip(10, 4) + [self.sell(30, 5, 500000, "Gold")])
        self.assertEqual(first["sold"]["Gold"], [3, 300000])
        self.assertEqual(second["sold"]["Gold"], [2, 200000])
        self.assertEqual(self.D.Totals([first, second]).earned, 500000)

    def test_the_shares_of_a_split_sale_add_up_to_the_whole(self):
        first, second = self.walk(self.gold_trip(0, 1) + self.gold_trip(10, 2) + [self.sell(30, 3, 100, "Gold")])
        self.assertEqual(first["sold"]["Gold"][1] + second["sold"]["Gold"][1], 100)

    def test_the_walk_carries_across_journals(self):
        carry, known = {}, {}
        first = self.H.runs_from([json.loads(x) for x in self.mining_trip(sell=False)], "J1.log", carry, known)
        self.H.runs_from([json.loads(self.sell(5, 2, 300000))], "J2.log", carry, known)
        self.assertEqual(first[0]["sold"]["Platinum"], [2, 300000])
        self.assertNotIn("Platinum", carry)

    def test_a_stored_unsold_list_that_is_not_readable_counts_as_empty(self):
        self.assertEqual(self.H._clean_unsold(None), {})
        self.assertEqual(self.H._clean_unsold({"Gold": [["a|b", 2], ["c", "x"], "junk", ["d", 0]], "Tin": "no"}), {"Gold": [["a|b", 2]]})


class SalesElsewhereHistoryTests(Fixture):
    def history(self):
        history = self.H.MiningHistory()
        history.pause = 0
        history.start(self.state)
        history._cmdr = "Test Cmdr"
        return history

    def journals(self):
        """Mining in one journal, a sale at another station in the next, and one more sale in the newest (still growing) one."""
        sale = dict(event="MarketSell", Type="platinum", Type_Localised="Platinum", Count=1)
        self.journal("Journal.2026-10-16T100000.01.log", self.mining_trip(sell=False) + [line(timestamp=self.ts(40), event="Undocked")])
        self.journal("Journal.2026-10-17T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr"), line(timestamp=self.ts(5), event="Docked"),
                                                           line(timestamp=self.ts(6), TotalSale=200000, **sale)])
        newest = self.journal("Journal.2026-10-18T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr"),
                                                                    line(timestamp=self.ts(6), TotalSale=210000, **sale)])
        os.utime(newest, (time.time(), time.time() + 5))

    def test_a_sale_in_a_later_journal_updates_the_saved_run(self):
        self.journals()
        history = self.history()
        history.refresh(self.folder, wait=True)
        run, = history.runs()
        self.assertEqual(run["sold"]["Platinum"], [2, 410000])           # one ton in the saved journal, the last in the newest
        saved, = history._payload()["runs"]
        self.assertEqual(saved["sold"]["Platinum"], [1, 200000], "the newest journal's sale is not written into the saved run")

    def test_reading_the_newest_journal_again_does_not_count_its_sale_twice(self):
        self.journals()
        history = self.history()
        for _ in range(3):
            history.refresh(self.folder, wait=True)
        run, = history.runs()
        self.assertEqual(run["sold"]["Platinum"], [2, 410000])
        self.assertEqual(history.unsold()[self.H.run_key(run)], {"Osmium": 1})

    def test_rebuilding_gives_the_same_numbers_as_live_play(self):
        self.journals()
        history = self.history()
        history.refresh(self.folder, wait=True)
        before = (history.runs(), history.unsold())
        history.clear()
        history.refresh(self.folder, wait=True)
        self.assertEqual((history.runs(), history.unsold()), before)

    def test_the_unsold_list_is_saved_and_survives_a_restart(self):
        self.journals()
        history = self.history()
        history.refresh(self.folder, wait=True)
        os.remove(os.path.join(self.folder, "Journal.2026-10-18T100000.01.log"))
        newest = self.journal("Journal.2026-10-19T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr")])
        os.utime(newest, (time.time(), time.time() + 5))
        later = self.history()
        later.refresh(self.folder, wait=True)
        run, = later.runs()
        self.assertEqual(run["sold"]["Platinum"], [1, 200000])
        self.assertEqual(later.unsold()[self.H.run_key(run)], {"Platinum": 1, "Osmium": 1})

    def test_a_file_saved_before_the_unsold_list_loads_with_nothing_waiting(self):
        self.journals()
        history = self.history()
        history.refresh(self.folder, wait=True)
        del history._payload()["unsold"]
        self.assertEqual(history._payload()["unsold"], {})

    def test_the_window_notes_what_is_still_waiting(self):
        run = self.H.new_run(self.ts(1), "J.log", "S", "")
        run["refined"] = {"Gold": 3}
        fields = dict(self.D.sales_fields([run], {self.H.run_key(run): {"Gold": 2}}))
        self.assertEqual(fields["Mined, not sold yet"], "2 t")
        self.assertNotIn("Mined, not sold yet", dict(self.D.sales_fields([run])))


class HistoryTests(Fixture):
    def history(self, who="Test Cmdr"):
        history = self.H.MiningHistory()
        history.pause = 0
        history.start(self.state)
        history._cmdr = who
        return history

    def test_finished_journals_are_saved_and_the_newest_is_kept_live(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.mining_trip())
        newest = self.journal("Journal.2026-10-18T100000.01.log", self.mining_trip(start=40))
        os.utime(newest, (time.time(), time.time() + 5))
        history = self.history()
        history.refresh(self.folder, wait=True)
        self.assertEqual(len(history.runs()), 2)
        self.assertEqual(len(history._payload()["runs"]), 1)                  # only the finished journal is saved
        self.assertEqual(history._payload()["files"], ["Journal.2026-10-17T100000.01.log"])

    def test_refreshing_again_counts_nothing_twice(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.mining_trip())
        newest = self.journal("Journal.2026-10-18T100000.01.log", self.mining_trip(start=40))
        os.utime(newest, (time.time(), time.time() + 5))
        history = self.history()
        for _ in range(3):
            history.refresh(self.folder, wait=True)
        self.assertEqual(len(history.runs()), 2)

    def test_another_commanders_journal_is_skipped(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.mining_trip(who="Someone Else"))
        self.journal("Journal.2026-10-18T100000.01.log", self.mining_trip(start=40))
        history = self.history()
        history.refresh(self.folder, wait=True)
        self.assertEqual(len(history.runs()), 1)

    def test_the_saved_runs_survive_a_restart_and_are_not_read_again(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.mining_trip())
        self.journal("Journal.2026-10-18T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr")])
        first = self.history()
        first.refresh(self.folder, wait=True)
        os.remove(os.path.join(self.folder, "Journal.2026-10-17T100000.01.log"))          # the journal is gone, the saved run stays
        second = self.history()
        self.assertEqual(len(second.runs()), 1)

    def test_clear_forgets_the_saved_runs_so_the_next_refresh_reads_every_journal_again(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.mining_trip())
        self.journal("Journal.2026-10-18T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr")])
        history = self.history()
        history.refresh(self.folder, wait=True)
        history.clear()
        self.assertEqual(history.runs(), [])
        history.refresh(self.folder, wait=True)
        self.assertEqual(len(history.runs()), 1)

    def test_each_commander_has_their_own_record(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.mining_trip(who="Test Cmdr"))
        self.journal("Journal.2026-10-18T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr")])
        history = self.history("Test Cmdr")
        history.refresh(self.folder, wait=True)
        history._cmdr = "Another"
        self.assertEqual(history.runs(), [])


class DataTests(Fixture):
    def runs(self):
        return self.H.runs_from([json.loads(x) for x in self.mining_trip()], "J1.log") + self.H.runs_from([json.loads(x) for x in self.mining_trip(start=40)], "J2.log")

    def test_the_totals_add_up_across_runs(self):
        t = self.D.Totals(self.runs())
        self.assertEqual((t.runs, t.refined, t.earned, t.sold, t.prospected), (2, 6, 1_000_000, 6, 4))
        self.assertEqual((t.grades["High"], t.motherlodes, t.cracked), (2, 2, 2))
        self.assertAlmostEqual(t.hours, 2 * 7 / 60, places=3)             # each run runs from its first limpet to its last mining event, seven minutes

    def test_the_tiles_say_what_they_count_and_an_empty_history_says_so(self):
        tiles = {t.caption: t.value for t in self.D.overview_tiles(self.runs())}
        self.assertEqual(tiles["mining runs"], "2")
        self.assertEqual(tiles["tons refined"], "6")
        self.assertEqual(tiles["asteroids rated High"], "50%")
        self.assertEqual([t.caption for t in self.D.overview_tiles([])], ["mining runs found"])

    def test_commodities_are_ranked_by_tons_with_the_average_price_per_ton_sold(self):
        table = self.D.commodity_table(self.runs())
        self.assertEqual(table.rows[0].cells[0], "Platinum")
        self.assertEqual(table.rows[0].cells[1:3], ["4", "4"])
        self.assertEqual(table.rows[0].cells[5], "67%")                      # four of six tons

    def test_rings_group_the_runs_and_runs_are_newest_first(self):
        runs = self.runs()
        ring = self.D.ring_table(runs).rows[0].cells
        self.assertEqual((ring[0], ring[2], ring[3]), ("HIP 1 2 A Ring", "2", "6"))
        rows = self.D.run_table(runs).rows
        self.assertTrue(rows[0].cells[0] > rows[1].cells[0])

    def test_a_rate_is_blank_when_there_is_no_mining_time(self):
        run = self.H.new_run(self.ts(1), "J.log", "S", "")
        run["refined"] = {"Gold": 3}
        self.assertEqual(self.D.run_table([run]).rows[0].cells[4], "-")

    def test_the_subtitle_names_the_commander_and_the_first_run(self):
        self.assertIn("CMDR Test Cmdr", self.D.subtitle("Test Cmdr", self.runs()))
        self.assertIn("2026-10-18", self.D.subtitle("Test Cmdr", self.runs()))
        self.assertIn("Reading", self.D.subtitle("Test Cmdr", [], "Reading your journals (40%)"))


if __name__ == "__main__":
    unittest.main()
