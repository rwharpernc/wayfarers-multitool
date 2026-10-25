"""The mining history told apart by page (plugin/mining_history.py, plugin/mining_history_data.py): what was refined in the Rhino and on which body, the runs as the ring half or the
surface half sees them, the tables and tiles for each, and the one-time re-read of runs saved before the split. No Tk, no network, no EDMC."""
import copy
import json
import os
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


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
        self.folder, self.state = tempfile.mkdtemp(), tempfile.mkdtemp()
        self.addCleanup(self._clean)

    def _clean(self):
        for folder in (self.folder, self.state):
            for name in os.listdir(folder):
                os.remove(os.path.join(folder, name))
            os.rmdir(folder)

    @staticmethod
    def ts(minute, hour=12):
        return f"2026-10-18T{hour:02d}:{minute:02d}:00Z"

    def head(self, who="Test Cmdr", start=0):
        return [line(timestamp=self.ts(start), event="Commander", Name=who), line(timestamp=self.ts(start), event="FSDJump", StarSystem="HIP 1", SystemAddress=1),
                line(timestamp=self.ts(start + 1), event="Undocked")]

    def ring_part(self, start=5, count=2, commodity="Platinum"):
        lines = [line(timestamp=self.ts(start), event="SupercruiseExit", StarSystem="HIP 1", Body="HIP 1 2 A Ring", BodyType="PlanetaryRing"),
                 line(timestamp=self.ts(start + 1), event="LaunchDrone", Type="Prospector"),
                 line(timestamp=self.ts(start + 2), event="ProspectedAsteroid", Content_Localised="Material Content: High")]
        lines += [line(timestamp=self.ts(start + 3), event="MiningRefined", Type_Localised=commodity) for _ in range(count)]
        return lines

    def rhino_part(self, start=20, count=3, commodity="Painite", srv_type="mev_rhino", body="HIP 1 4"):
        lines = [line(timestamp=self.ts(start), event="SupercruiseExit", StarSystem="HIP 1", Body=body, BodyType="Planet"),
                 line(timestamp=self.ts(start + 1), event="LaunchSRV", SRVType=srv_type, ID=1)]
        lines += [line(timestamp=self.ts(start + 2), event="MiningRefined", Type_Localised=commodity) for _ in range(count)]
        lines.append(line(timestamp=self.ts(start + 5), event="DockSRV", SRVType=srv_type, ID=1))
        return lines

    def tail(self, end=40, sells=()):
        lines = [line(timestamp=self.ts(end), event="Docked")]
        for name, count, total in sells:
            lines.append(line(timestamp=self.ts(end + 1), event="MarketSell", Type=name.lower(), Type_Localised=name, Count=count, TotalSale=total))
        return lines

    def runs(self, lines):
        return self.H.runs_from([json.loads(x) for x in lines], "J1.log")


class RunSplitTests(Fixture):
    def test_what_was_refined_in_the_rhino_is_told_apart_and_the_body_is_kept(self):
        run = self.runs(self.head() + self.rhino_part() + self.tail())[0]
        self.assertEqual(run["refined"], {"Painite": 3})
        self.assertEqual(run["srv"], {"Painite": 3})
        self.assertEqual(run["body"], "HIP 1 4")
        self.assertEqual(run["ring"], "")

    def test_a_ring_run_has_no_rhino_refining_and_no_body(self):
        run = self.runs(self.head() + self.ring_part() + self.tail())[0]
        self.assertEqual((run["srv"], run["body"]), ({}, ""))
        self.assertEqual(run["ring"], "HIP 1 2 A Ring")

    def test_a_trip_with_both_splits_its_refining_between_them(self):
        run = self.runs(self.head() + self.ring_part(count=2, commodity="Platinum") + self.rhino_part(count=3, commodity="Painite") + self.tail())[0]
        self.assertEqual(run["refined"], {"Platinum": 2, "Painite": 3})
        self.assertEqual(run["srv"], {"Painite": 3})

    def test_refining_after_the_rhino_is_docked_counts_as_ring_refining_again(self):
        lines = self.head() + self.rhino_part(count=1, commodity="Painite") + [line(timestamp=self.ts(30), event="MiningRefined", Type_Localised="Painite")] + self.tail()
        run = self.runs(lines)[0]
        self.assertEqual((run["refined"], run["srv"]), ({"Painite": 2}, {"Painite": 1}))

    def test_another_kind_of_srv_is_not_the_rhino(self):
        run = self.runs(self.head() + self.rhino_part(srv_type="testbuggy") + self.tail())[0]
        self.assertEqual(run["srv"], {})

    def test_a_destroyed_rhino_or_a_death_ends_the_rhino_refining(self):
        for event in ("SRVDestroyed", "Died"):
            lines = self.head() + self.rhino_part(count=1)[:-1] + [line(timestamp=self.ts(25), event=event),
                                                                    line(timestamp=self.ts(26), event="MiningRefined", Type_Localised="Painite")] + self.tail()
            self.assertEqual(self.runs(lines)[0]["srv"], {"Painite": 1}, event)

    def test_a_jump_forgets_the_rhino_and_the_body(self):
        lines = self.head() + self.rhino_part(count=1)[:-1] + [line(timestamp=self.ts(25), event="FSDJump", StarSystem="HIP 2", SystemAddress=2),
                                                                line(timestamp=self.ts(26), event="MiningRefined", Type_Localised="Painite")] + self.tail()
        run = self.runs(lines)[0]
        self.assertEqual(run["srv"], {"Painite": 1})


class ModeTests(Fixture):
    def setUp(self):
        super().setUp()
        self.ring_run = self.runs(self.head() + self.ring_part(count=2, commodity="Platinum") + self.tail(sells=[("Platinum", 2, 400000)]))[0]
        self.rhino_run = self.runs(self.head(start=60) + self.rhino_part(start=80, count=3) + self.tail(end=100, sells=[("Painite", 3, 900000)]))[0]
        self.mixed_run = self.runs(self.head(start=120) + self.ring_part(start=125, count=2, commodity="Platinum") + self.rhino_part(start=140, count=4)
                                   + self.tail(end=160, sells=[("Platinum", 2, 300000), ("Painite", 4, 800000)]))[0]
        self.all = [self.ring_run, self.rhino_run, self.mixed_run]

    def test_no_mode_keeps_every_run_as_it_is(self):
        self.assertEqual(self.D.for_mode(self.all, None), self.all)
        self.assertEqual(self.D.for_mode(self.all, "anything else"), self.all)

    def test_the_surface_half_is_the_runs_with_the_rhino_out(self):
        surface = self.D.for_mode(self.all, self.D.SURFACE)
        self.assertEqual(len(surface), 2)
        self.assertEqual([self.D.refined_tons(r) for r in surface], [3, 4])
        for run in surface:
            self.assertEqual(run["ring"], "")
            self.assertEqual((run["cracked"], run["motherlode"], run["limpets"], sum(run["prospected"].values())), (0, 0, {}, 0))

    def test_the_space_half_is_the_ring_runs_and_the_ring_part_of_a_mixed_one(self):
        space = self.D.for_mode(self.all, self.D.SPACE)
        self.assertEqual(len(space), 2)
        self.assertEqual([self.D.refined_tons(r) for r in space], [2, 2])
        self.assertEqual(space[1]["refined"], {"Platinum": 2})
        self.assertEqual(sum(space[1]["prospected"].values()), 1, "the prospecting stays with the ring half")

    def test_sales_follow_the_commodity_into_the_half_that_mined_it(self):
        surface = self.D.for_mode(self.all, self.D.SURFACE)
        space = self.D.for_mode(self.all, self.D.SPACE)
        self.assertEqual([self.D.earned(r) for r in surface], [900000, 800000])
        self.assertEqual([self.D.earned(r) for r in space], [400000, 300000])

    def test_a_run_with_nothing_in_a_half_is_left_out_of_it_and_the_originals_are_not_changed(self):
        before = copy.deepcopy(self.all)
        self.D.for_mode(self.all, self.D.SURFACE)
        self.D.for_mode(self.all, self.D.SPACE)
        self.assertEqual(self.all, before)
        self.assertEqual(self.D.for_mode([self.rhino_run], self.D.SPACE), [])
        self.assertEqual(self.D.for_mode([self.ring_run], self.D.SURFACE), [])

    def test_a_run_with_no_rhino_record_is_a_ring_run(self):
        old = copy.deepcopy(self.ring_run)
        del old["srv"], old["body"]
        self.assertEqual(len(self.D.for_mode([old], self.D.SPACE)), 1)
        self.assertEqual(self.D.for_mode([old], self.D.SURFACE), [])


class TableTests(ModeTests):
    def test_bodies_are_grouped_and_ranked_by_tons(self):
        other = copy.deepcopy(self.rhino_run)
        other["body"], other["refined"], other["srv"] = "HIP 1 5", {"Painite": 10}, {"Painite": 10}
        table = self.D.body_table(self.D.for_mode(self.all + [other], self.D.SURFACE))
        self.assertEqual([row.cells[0] for row in table.rows], ["HIP 1 5", "HIP 1 4"])
        self.assertEqual(table.rows[1].cells[2], "2")
        self.assertEqual(table.rows[1].cells[3], "7")
        self.assertEqual(len(table.columns), len(table.rows[0].cells))

    def test_a_run_with_no_body_is_listed_under_a_plain_label(self):
        nobody = copy.deepcopy(self.rhino_run)
        nobody["body"] = ""
        self.assertEqual(self.D.body_table([nobody]).rows[0].cells[0], "(no body recorded)")

    def test_the_surface_run_table_has_no_prospecting_or_limpet_columns(self):
        table = self.D.run_table(self.D.for_mode(self.all, self.D.SURFACE), self.D.SURFACE)
        self.assertEqual([c[1] for c in table.columns], ["Started (UTC)", "Where", "Mining time", "Refined (t)", "t / hour", "Earned"])
        self.assertTrue(all(len(row.cells) == len(table.columns) for row in table.rows))
        self.assertEqual(table.rows[-1].cells[1], "HIP 1 4", "the surface run says the body, not a ring")
        space = self.D.run_table(self.D.for_mode(self.all, self.D.SPACE), self.D.SPACE)
        self.assertIn("Limpets P / C", [c[1] for c in space.columns])
        self.assertEqual(space.rows[-1].cells[1], "HIP 1 2 A Ring")

    def test_the_ring_table_lists_only_the_ring_half(self):
        names = [row.cells[0] for row in self.D.ring_table(self.D.for_mode(self.all, self.D.SPACE)).rows]
        self.assertEqual(names, ["HIP 1 2 A Ring"])

    def test_the_surface_tiles_leave_out_the_asteroid_grade_and_the_space_tiles_keep_it(self):
        surface = [t.caption for t in self.D.overview_tiles(self.D.for_mode(self.all, self.D.SURFACE), self.D.SURFACE)]
        space = [t.caption for t in self.D.overview_tiles(self.D.for_mode(self.all, self.D.SPACE), self.D.SPACE)]
        self.assertNotIn("asteroids rated High", surface)
        self.assertIn("asteroids rated High", space)
        self.assertIn("credits after limpets", space)
        self.assertNotIn("credits after limpets", surface)
        self.assertEqual(len(space) - len(surface), 2)

    def test_the_commodities_tab_follows_the_half(self):
        surface = [row.cells[0] for row in self.D.commodity_table(self.D.for_mode(self.all, self.D.SURFACE)).rows]
        space = [row.cells[0] for row in self.D.commodity_table(self.D.for_mode(self.all, self.D.SPACE)).rows]
        self.assertEqual(surface, ["Painite"])
        self.assertEqual(space, ["Platinum"])

    def test_the_surface_fields_name_the_best_body(self):
        fields = dict(self.D.surface_fields(self.D.for_mode(self.all, self.D.SURFACE)))
        self.assertEqual(fields["Bodies mined on"], "1")
        self.assertEqual(fields["Most tons on one body"], "7 t on HIP 1 4")
        self.assertEqual(self.D.surface_fields([]), [("No Rhino mining yet", "")])

    def test_the_subtitle_says_which_half_it_is(self):
        surface = self.D.for_mode(self.all, self.D.SURFACE)
        self.assertIn("2 Rhino mining runs since", self.D.subtitle("Test Cmdr", surface, "", self.D.SURFACE))
        self.assertIn("2 ring mining runs since", self.D.subtitle("Test Cmdr", self.D.for_mode(self.all, self.D.SPACE), "", self.D.SPACE))
        self.assertIn("no Rhino mining runs found", self.D.subtitle("Test Cmdr", [], "", self.D.SURFACE))
        self.assertIn("mining runs since", self.D.subtitle("Test Cmdr", self.all))


class MigrationTests(Fixture):
    def history(self):
        history = self.H.MiningHistory()
        history.pause = 0
        history.start(self.state)
        history._cmdr = "Test Cmdr"
        return history

    def journal(self, name, lines):
        path = os.path.join(self.folder, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return path

    def test_runs_saved_before_the_split_are_read_from_the_journals_once_more(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.head() + self.rhino_part() + self.tail())
        self.journal("Journal.2026-10-18T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr")])
        first = self.history()
        first.refresh(self.folder, wait=True)
        self.assertEqual(first.runs()[0]["srv"], {"Painite": 3})
        path = os.path.join(self.state, self.H.STATE_FILENAME)
        with open(path, encoding="utf-8") as handle:
            saved = json.load(handle)
        data = saved["commanders"]["test cmdr"]["data"]
        data.pop("runs_v")
        data["runs"][0].pop("srv")
        data["runs"][0].pop("body")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(saved, handle)
        second = self.history()
        self.assertEqual(second.runs(), [], "the old runs are dropped until the journals are read again")
        second.refresh(self.folder, wait=True)
        self.assertEqual(second.runs()[0]["srv"], {"Painite": 3})
        self.assertEqual(second.runs()[0]["body"], "HIP 1 4")

    def test_runs_saved_at_the_current_version_are_kept(self):
        self.journal("Journal.2026-10-17T100000.01.log", self.head() + self.rhino_part() + self.tail())
        self.journal("Journal.2026-10-18T100000.01.log", [line(timestamp=self.ts(1), event="Commander", Name="Test Cmdr")])
        self.history().refresh(self.folder, wait=True)
        os.remove(os.path.join(self.folder, "Journal.2026-10-17T100000.01.log"))
        self.assertEqual(len(self.history().runs()), 1, "the journal is gone, the saved run stays")


if __name__ == "__main__":
    unittest.main()
