"""The link between a planned expedition and an Expedition Log run (expedition_link.py): starting both at once, Pause, Stop and Resume agreeing in both directions, the
expedition's time following the run's clock, the setting that leaves the log alone, stopping and starting again, and the link surviving a restart."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import expedition as X  # noqa: E402
from plugin import expedition_link as K  # noqa: E402
from plugin import expedition_log as L  # noqa: E402


def utc(hour, minute):
    return datetime(2026, 10, 20, hour, minute, tzinfo=timezone.utc).timestamp()


class Clock:
    """A time the test sets, as the journal-style text both books stamp their changes with."""

    def __init__(self, hour=10, minute=0):
        self.t = utc(hour, minute)

    def at(self, hour, minute):
        self.t = utc(hour, minute)

    def __call__(self):
        return L.stamp(self.t)


class Setup:
    def __init__(self, folder, clock, enabled=True):
        ids = iter(f"p{i}" for i in range(1, 1000))
        run_ids = iter(f"r{i}" for i in range(1, 1000))
        self.clock = clock
        self.plans = X.ExpeditionBook(now=clock, new_id=lambda: next(ids))
        self.logs = L.LogBook(now=clock, new_id=lambda: next(run_ids))
        self.enabled = enabled
        self.plans.load(folder)
        self.logs.load(folder)
        self.plans.set_commander("Bocheaux")
        self.logs.set_commander("Bocheaux")
        self.link = K.ExpeditionLink(self.plans, self.logs, lambda name: self.logs.start(name, "Sol", "Asp Explorer"), lambda: self.enabled)

    def trip(self, name="Colonia run", systems=("Sol", "Colonia")):
        e = self.plans.create(name)
        for system in systems:
            self.plans.add_stop(e.id, system)
        return e


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.clock = Clock()
        self.s = Setup(self.tmp.name, self.clock)

    def tearDown(self):
        self.tmp.cleanup()


class Starting(Base):
    def test_starting_an_expedition_starts_a_linked_run(self):
        e = self.s.trip()
        started = self.s.link.start(e.id)
        run = self.s.logs.active()
        self.assertEqual((e.status, run.name, run.status, e.log_run_id), (X.ACTIVE, "Colonia run", L.RUNNING, run.id))
        self.assertTrue(started.new_run)
        self.assertEqual(started.log_words(), "Logging in Expedition Log.")
        self.assertEqual((run.start_system, run.ships), ("Sol", ["Asp Explorer"]))

    def test_the_setting_off_leaves_the_log_alone(self):
        self.s.enabled = False
        e = self.s.trip()
        started = self.s.link.start(e.id)
        self.assertEqual((e.status, e.log_run_id, self.s.logs.runs(), started.run, started.log_words()), (X.ACTIVE, "", [], None, ""))
        self.assertEqual(self.s.link.elapsed_text(e), X.elapsed_text(e.started))

    def test_the_setting_off_still_carries_on_a_run_the_expedition_already_has(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        self.s.link.stop(e.id)
        self.s.enabled = False
        self.s.link.start(e.id)
        self.assertEqual((self.s.logs.active().id, e.log_run_id), (e.log_run_id, e.log_run_id))
        self.assertEqual(len(self.s.logs.runs()), 1)

    def test_an_expedition_with_no_stops_cannot_start_and_starts_no_run(self):
        e = self.s.plans.create("Empty")
        with self.assertRaises(X.ExpeditionError):
            self.s.link.start(e.id)
        self.assertEqual((e.status, self.s.logs.runs()), (X.PLANNED, []))

    def test_no_commander_in_the_log_means_no_run_but_the_expedition_still_starts(self):
        e = self.s.trip()
        self.s.logs.set_commander("Someone Else")          # the log has switched commander; the planner has not
        self.s.logs._cmdr = ""
        started = self.s.link.start(e.id)
        self.assertEqual((e.status, started.run, e.log_run_id), (X.ACTIVE, None, ""))

    def test_starting_another_expedition_sets_the_first_aside_and_stops_its_run(self):
        a, b = self.s.trip("A"), self.s.trip("B", ("Sol", "Maia"))
        self.s.link.start(a.id)
        run_a = self.s.logs.get(a.log_run_id)
        self.s.link.start(b.id)
        run_b = self.s.logs.get(b.log_run_id)
        self.assertEqual((a.status, b.status), (X.PAUSED, X.ACTIVE))
        self.assertEqual((run_a.status, run_b.status, self.s.logs.active().id), (L.STOPPED, L.RUNNING, run_b.id))
        self.s.link.start(a.id)                              # and back: the first run is reopened, the second is stopped
        self.assertEqual((a.status, b.status, run_a.status, run_b.status), (X.ACTIVE, X.PAUSED, L.RUNNING, L.STOPPED))
        self.assertEqual(len(self.s.logs.runs()), 2)

    def test_an_expedition_set_aside_by_one_with_no_run_has_its_run_paused(self):
        a, b = self.s.trip("A"), self.s.trip("B", ("Sol", "Maia"))
        self.s.link.start(a.id)
        run_a = self.s.logs.get(a.log_run_id)
        self.s.enabled = False
        self.s.link.start(b.id)
        self.assertEqual((a.status, b.status, b.log_run_id, run_a.status), (X.PAUSED, X.ACTIVE, "", L.PAUSED))
        self.s.link.start(a.id)
        self.assertEqual((a.status, b.status, run_a.status), (X.ACTIVE, X.PAUSED, L.RUNNING))

    def test_starting_twice_changes_nothing(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        again = self.s.link.start(e.id)
        self.assertEqual((len(self.s.logs.runs()), again.new_run), (1, False))


class Pausing(Base):
    def test_pause_on_the_planner_pauses_the_run_and_start_resumes_both(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        run = self.s.logs.get(e.log_run_id)
        self.clock.at(10, 10)
        self.s.link.pause(e.id)
        self.assertEqual((e.status, run.status), (X.PAUSED, L.PAUSED))
        self.clock.at(10, 40)
        self.s.link.start(e.id)
        self.assertEqual((e.status, run.status, run.paused_for, run.paused_at), (X.ACTIVE, L.RUNNING, 1800.0, ""))

    def test_pause_on_the_log_pauses_the_expedition_and_resume_carries_on(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        run = self.s.logs.get(e.log_run_id)
        self.s.logs.pause(run.id)
        self.assertEqual((e.status, self.s.plans.active()), (X.PAUSED, None))
        self.s.logs.resume(run.id)
        self.assertEqual((e.status, self.s.plans.active()), (X.ACTIVE, e))

    def test_stop_on_the_log_stops_the_expedition_running_or_paused(self):
        for pause_first in (False, True):
            e = self.s.trip(f"Trip {pause_first}")
            self.s.link.start(e.id)
            run = self.s.logs.get(e.log_run_id)
            if pause_first:
                self.s.logs.pause(run.id)
            self.s.logs.stop(run.id)
            self.assertEqual((e.status, run.status), (X.DONE, L.STOPPED), f"pause first: {pause_first}")

    def test_a_new_run_started_in_the_log_stops_the_linked_expedition(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        self.s.logs.start("Something else", "Sol", "")
        self.assertEqual((e.status, self.s.plans.active()), (X.DONE, None))

    def test_resuming_a_stopped_run_in_the_log_reopens_its_expedition_and_sets_aside_the_running_one(self):
        a, b = self.s.trip("A"), self.s.trip("B", ("Sol", "Maia"))
        self.s.link.start(a.id)
        self.s.link.stop(a.id)
        self.s.link.start(b.id)
        self.s.logs.resume(a.log_run_id)
        self.assertEqual((a.status, b.status), (X.ACTIVE, X.PAUSED))
        self.assertEqual(self.s.logs.active().id, a.log_run_id)

    def test_pausing_an_expedition_that_is_not_running_pauses_no_run(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        run = self.s.logs.get(e.log_run_id)
        self.s.link.stop(e.id)
        self.s.link.pause(e.id)
        self.assertEqual(run.status, L.STOPPED)

    def test_a_run_deleted_from_the_log_leaves_the_expedition_unlinked_in_effect(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        self.s.logs.delete(e.log_run_id)
        self.assertIsNone(self.s.link.run_of(e))
        self.s.link.pause(e.id)
        self.assertEqual(e.status, X.PAUSED)
        self.s.link.start(e.id)                              # a fresh run, since the old one is gone
        self.assertEqual(self.s.logs.active().id, e.log_run_id)


class Figures(Base):
    def test_a_journal_event_that_changes_figures_only_does_not_scan_the_expeditions(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        with mock.patch.object(self.s.plans, "expeditions", wraps=self.s.plans.expeditions) as scan:
            self.s.logs.apply({"event": "FSDJump", "StarSystem": "Sol", "JumpDist": 5.0, "StarPos": [0, 0, 0], "timestamp": "2026-10-20T10:01:00Z"})
            self.assertEqual(scan.call_count, 0)
            self.s.logs.pause(self.s.logs.active().id)          # a status change is still carried over
            self.assertGreater(scan.call_count, 0)
        self.assertEqual(e.status, X.PAUSED)


class Stopping(Base):
    def test_stop_on_the_planner_stops_the_run_running_or_paused(self):
        for pause_first in (False, True):
            e = self.s.trip(f"Trip {pause_first}")
            self.s.link.start(e.id)
            run = self.s.logs.get(e.log_run_id)
            if pause_first:
                self.s.link.pause(e.id)
            self.s.link.stop(e.id)
            self.assertEqual((e.status, run.status, self.s.logs.active()), (X.DONE, L.STOPPED, None), f"pause first: {pause_first}")

    def test_starting_a_stopped_expedition_reopens_it_and_its_run(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        run = self.s.logs.get(e.log_run_id)
        self.s.link.stop(e.id)
        self.assertEqual(run.ended != "", True)
        self.s.link.start(e.id)
        self.assertEqual((e.status, e.finished, run.status, run.ended, len(self.s.logs.runs())), (X.ACTIVE, "", L.RUNNING, "", 1))

    def test_reset_lets_go_of_the_run_and_stops_it(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        run = self.s.logs.get(e.log_run_id)
        self.s.link.reset(e.id)
        self.assertEqual((e.status, e.log_run_id, run.status), (X.PLANNED, "", L.STOPPED))
        self.s.link.start(e.id)
        self.assertNotEqual(e.log_run_id, run.id)
        self.assertEqual(len(self.s.logs.runs()), 2)


class Time(Base):
    def test_a_linked_expedition_shows_the_runs_time_without_the_time_paused(self):
        e = self.s.trip()
        self.s.link.start(e.id)                              # 10:00
        self.clock.at(10, 20)
        self.s.link.pause(e.id)
        self.clock.at(10, 50)
        self.s.link.start(e.id)
        with mock.patch.object(L.time, "time", return_value=utc(11, 0)):
            self.assertEqual(self.s.link.elapsed_text(e), X.span_text(30 * 60))       # 20 min before the pause and 10 after, not the hour on the wall clock
        self.assertEqual(X.span_text(30 * 60), "30 min")

    def test_the_time_holds_still_while_paused_and_after_a_stop(self):
        e = self.s.trip()
        self.s.link.start(e.id)
        self.clock.at(10, 15)
        self.s.link.pause(e.id)
        with mock.patch.object(L.time, "time", return_value=utc(18, 0)):
            self.assertEqual(self.s.link.elapsed_text(e), "15 min")
        self.s.link.stop(e.id)
        with mock.patch.object(L.time, "time", return_value=utc(18, 0)):
            self.assertEqual(self.s.link.elapsed_text(e), "15 min")

    def test_an_unlinked_expedition_shows_its_dates(self):
        e = self.s.trip()
        self.assertEqual(self.s.link.elapsed_text(e), "")
        self.s.enabled = False
        self.s.link.start(e.id)
        self.s.link.stop(e.id)
        self.assertEqual(self.s.link.elapsed_text(e), X.elapsed_text(e.started, e.finished))


class Restart(unittest.TestCase):
    def test_the_link_survives_a_save_and_a_load(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Setup(folder, Clock())
            e = first.trip()
            first.link.start(e.id)
            run_id = e.log_run_id
            first.plans.flush()
            first.logs.flush()
            second = Setup(folder, Clock())
            again = second.plans.get(e.id)
            self.assertEqual((again.log_run_id, again.status, second.link.run_of(again).id, second.logs.active().id), (run_id, X.ACTIVE, run_id, run_id))
            second.logs.pause(run_id)                          # and the two still follow each other
            self.assertEqual(again.status, X.PAUSED)

    def test_an_old_record_without_a_link_loads_unlinked(self):
        raw = {"id": "old", "name": "Old", "status": "planned", "stops": [{"id": "s", "system": "Sol"}]}
        e = X._expedition_from_raw(raw)
        self.assertEqual(e.log_run_id, "")
        self.assertNotIn("log_run_id", X._expedition_to_raw(e))

    def test_the_link_is_saved_in_the_record(self):
        e = X.Expedition("e", "E", log_run_id="r9")
        self.assertEqual(X._expedition_from_raw(X._expedition_to_raw(e)).log_run_id, "r9")


if __name__ == "__main__":
    unittest.main()
