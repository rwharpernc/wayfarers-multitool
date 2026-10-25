"""The live rate and the run average (plugin/mining_rate.py), worded the same on the Space page, the Surface page and the HUD (plugin/mining_render.py, plugin/mining_overlay.py),
and the same mining time in Mining History (plugin/mining_history.py, plugin/mining_history_data.py). No Tk window and no EDMC."""

import os
import sys
import time
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_config = types.ModuleType("config")
_config.appname = "EDMarketConnector"
_config.user_agent = "WFMT-test"
_config.appversion = lambda: "5.13.0"
_config.config = mock.MagicMock()


class _Any(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock()


sys.modules.setdefault("config", _config)
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0")):
    if not hasattr(sys.modules["config"], _attr):
        setattr(sys.modules["config"], _attr, _default)
if not hasattr(sys.modules["config"], "config"):
    sys.modules["config"].config = mock.MagicMock()
for _name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes",
              "psutil", "ttkHyperlinkLabel", "theme", "myNotebook"):
    sys.modules.setdefault(_name, _Any(_name))

from plugin import mining_history, mining_history_data, mining_pages, mining_rate as R  # noqa: E402
from plugin import mining_render as render  # noqa: E402
from plugin import mining_space as space_mining  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402


class RateNowTests(unittest.TestCase):
    def test_it_is_the_tons_of_the_last_minute_scaled_to_an_hour(self) -> None:
        stamps = [100.0 + i for i in range(7)]            # seven tons in the last seven seconds of a minute
        self.assertEqual(R.current_rate(stamps, now=160.0), 7 * 3600 / 60)

    def test_a_young_run_divides_by_its_age_not_a_full_window(self) -> None:
        stamps = [100.0, 101.0, 102.0]
        self.assertEqual(R.current_rate(stamps, now=102.0), 3 * 3600 / R.MIN_RATE_SPAN_SECONDS)   # never by less than the floor
        stamps = [100.0 + i * 5 for i in range(5)]
        self.assertEqual(R.current_rate(stamps, now=130.0), 5 * 3600 / 30)

    def test_it_falls_to_zero_after_a_lull_and_the_list_is_pruned_in_place(self) -> None:
        stamps = [100.0, 110.0, 150.0]
        self.assertGreater(R.current_rate(stamps, now=155.0), 0)
        self.assertEqual(R.current_rate(stamps, now=170.0), 2 * 3600 / 60)        # the first has left the window
        self.assertEqual(stamps, [110.0, 150.0])
        self.assertEqual(R.current_rate(stamps, now=500.0), 0.0)
        self.assertEqual(stamps, [])

    def test_record_tick_uses_the_time_it_is_given(self) -> None:
        stamps: list = []
        R.record_tick(stamps, 42.0)
        self.assertEqual(stamps, [42.0])


class ClockTests(unittest.TestCase):
    def test_no_events(self) -> None:
        clock = R.MiningClock()
        self.assertEqual((clock.first, clock.last, clock.mined_seconds), (None, None, 0.0))
        self.assertIsNone(clock.average_per_hour(10))

    def test_a_single_event_has_no_time_yet(self) -> None:
        clock = R.MiningClock()
        clock.note(1000.0)
        self.assertEqual((clock.first, clock.last, clock.mined_seconds), (1000.0, 1000.0, 0.0))
        self.assertIsNone(clock.average_per_hour(1))

    def test_the_average_is_tons_over_the_mining_time(self) -> None:
        clock = R.MiningClock()
        for at in (0.0, 30.0, 90.0, 1800.0):
            clock.note(at)
        self.assertEqual(clock.mined_seconds, 90.0)                   # the last gap (1710 s) is over ten minutes
        self.assertEqual(clock.average_per_hour(6), 6 * 3600 / 90.0)

    def test_a_gap_of_more_than_ten_minutes_is_left_out_but_ten_exactly_is_not(self) -> None:
        clock = R.MiningClock()
        first_gap_end = 60.0 + R.MAX_GAP_SECONDS
        for at in (0.0, 60.0, first_gap_end, first_gap_end + R.MAX_GAP_SECONDS + 1, first_gap_end + R.MAX_GAP_SECONDS + 41):
            clock.note(at)
        self.assertEqual(clock.mined_seconds, 60.0 + R.MAX_GAP_SECONDS + 40.0)
        self.assertEqual((clock.first, clock.last), (0.0, first_gap_end + R.MAX_GAP_SECONDS + 41))

    def test_an_event_stamped_earlier_adds_nothing(self) -> None:
        clock = R.MiningClock()
        clock.note(100.0)
        clock.note(200.0)
        clock.note(150.0)
        self.assertEqual((clock.last, clock.mined_seconds), (200.0, 100.0))

    def test_the_average_waits_for_a_minute_of_mining(self) -> None:
        clock = R.MiningClock()
        clock.note(0.0)
        clock.note(R.MIN_AVERAGE_SECONDS - 1)
        self.assertIsNone(clock.average_per_hour(5))
        clock.note(R.MIN_AVERAGE_SECONDS)
        self.assertIsNotNone(clock.average_per_hour(5))

    def test_event_time_reads_the_journal_stamp(self) -> None:
        self.assertEqual(R.event_time({"timestamp": "2026-10-20T18:59:00Z"}) - R.event_time({"timestamp": "2026-10-20T18:58:00Z"}), 60.0)
        self.assertEqual(R.event_time({"timestamp": "nonsense"}, fallback=7.0), 7.0)
        self.assertEqual(R.event_time({}, fallback=8.0), 8.0)
        self.assertAlmostEqual(R.event_time({}), time.time(), delta=5)


class RunTextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.space = space_mining.SpaceMiningRepository()
        self.space.set_current_cmdr("Test")
        self.surface = surface_mining.SurfaceMiningRepository()
        self.surface.set_current_cmdr("Test")

    def test_a_run_with_no_events_says_none_yet_and_zero_now(self) -> None:
        run = self.space.current_run()
        self.assertEqual(render.format_run_average(run), "Run average: none yet")
        self.assertEqual(render.format_rate_now(run), "Refining now: 0 t/h")

    def test_one_event_needs_more_mining(self) -> None:
        self.space.record_refined("Painite", at=1000.0)
        self.assertEqual(render.format_run_average(self.space.current_run()), "Run average: needs a minute of mining")

    def test_the_average_text_with_a_gap(self) -> None:
        for at in (0.0, 60.0, 120.0, 180.0, 5000.0, 5060.0):                  # one gap of over ten minutes
            self.space.record_refined("Painite", at=at)
        run = self.space.current_run()
        self.assertEqual(run.clock.mined_seconds, 240.0)
        self.assertEqual(render.format_run_average(run), "Run average: 90 t/h over 4 min")        # six tons in four minutes of mining

    def test_the_average_survives_the_rate_list_being_pruned(self) -> None:
        for at in (0.0, 60.0, 120.0):
            self.space.record_refined("Painite", at=at)
        run = self.space.current_run()
        R.current_rate(run.refined_timestamps, now=10000.0)                    # prunes it empty
        self.assertEqual(run.refined_timestamps, [])
        self.assertEqual(render.format_run_average(run), "Run average: 90 t/h over 2 min")

    def test_the_other_mining_events_count_toward_mining_time(self) -> None:
        self.space.record_limpet("Prospector", at=0.0)
        self.space.record_prospected("", None, None, at=60.0)
        self.space.record_asteroid_cracked(at=120.0)
        self.space.record_refined("Painite", at=180.0)
        self.assertEqual(self.space.current_run().clock.mined_seconds, 180.0)

    def test_the_surface_page_words_it_the_same(self) -> None:
        for at in (0.0, 60.0, 120.0):
            self.surface.record_refined("Uranium", at=at)
        run = self.surface.current_run()
        self.assertEqual(render.format_run_average(run), "Run average: 90 t/h over 2 min")
        self.assertTrue(render.format_rate_now(run).startswith("Refining now: "))

    def test_the_hud_uses_the_same_lines(self) -> None:
        for at in (0.0, 60.0, 120.0):
            self.space.record_refined("Painite", at=at)
        from plugin import mining_overlay      # imported here: importing it at the top would load the overlay glue before test_overlay_placement swaps in its own config stub
        run = self.space.current_run()
        seen: list = []
        inline = types.SimpleNamespace(Thread=lambda target, **kw: types.SimpleNamespace(start=target))
        with mock.patch.object(space_mining, "space_mining_repository", self.space), \
                mock.patch.object(mining_overlay, "threading", inline), \
                mock.patch.object(mining_overlay, "_send_overlay_panel", side_effect=lambda client, msg_id, x, y, lines, *a, **k: seen.append(list(lines))), \
                mock.patch.object(mining_overlay.overlay_placement, "client_for", return_value=mock.MagicMock()), \
                mock.patch.object(mining_overlay.overlay_appearance, "current_look", return_value=mining_overlay.LEGACY):
            mining_overlay.push_stats_overlay(mining_pages.SPACE_MINING, display_cargo_bar=True, display_session_totals=True, display_prospector_hints=False)
        self.assertEqual(seen[-1][-2:], [render.format_rate_now(run), render.format_run_average(run)])
        self.assertIn("Run average: 90 t/h over 2 min", seen[-1])


class HistoryAgreesTests(unittest.TestCase):
    STAMPS = ("2026-10-20T10:00:00Z", "2026-10-20T10:01:00Z", "2026-10-20T10:02:00Z", "2026-10-20T10:40:00Z", "2026-10-20T10:41:00Z")   # a 38 minute gap in the middle

    def lines(self):
        out = [{"timestamp": "2026-10-20T09:59:00Z", "event": "Commander", "Name": "T"}, {"timestamp": "2026-10-20T09:59:30Z", "event": "Undocked"}]
        out += [{"timestamp": stamp, "event": "MiningRefined", "Type": "painite", "Type_Localised": "Painite"} for stamp in self.STAMPS]
        out.append({"timestamp": "2026-10-20T10:50:00Z", "event": "Docked"})
        return out

    def test_a_long_gap_is_not_mining_time_in_the_history_either(self) -> None:
        run, = mining_history.runs_from(self.lines(), "J.log")
        self.assertEqual(run["idle"], 38 * 60)
        self.assertEqual(mining_history_data.mining_hours(run) * 3600, 3 * 60)

    def test_it_is_the_figure_the_live_clock_gives_for_the_same_events(self) -> None:
        run, = mining_history.runs_from(self.lines(), "J.log")
        clock = R.MiningClock()
        for entry in self.lines():
            if entry["event"] == "MiningRefined":
                clock.note(R.event_time(entry))
        self.assertEqual(clock.mined_seconds, mining_history_data.mining_hours(run) * 3600)

    def test_a_run_without_a_gap_has_no_idle_and_a_saved_run_without_it_reads_as_none(self) -> None:
        lines = [{"timestamp": "2026-10-20T10:00:00Z", "event": "Undocked"}] + [
            {"timestamp": stamp, "event": "MiningRefined", "Type": "painite"} for stamp in self.STAMPS[:3]]
        run, = mining_history.runs_from(lines + [{"timestamp": "2026-10-20T10:05:00Z", "event": "Docked"}], "J.log")
        self.assertNotIn("idle", run)
        self.assertAlmostEqual(mining_history_data.mining_hours(run), 2 / 60)
        self.assertEqual(mining_history_data.mining_hours({"first": "2026-10-20T10:00:00Z", "last": "2026-10-20T11:00:00Z"}), 1.0)


if __name__ == "__main__":
    unittest.main()
