"""How long until the hold is full (plugin/mining_rate.py `minutes_to_fill` and `full_in_text`, plugin/mining_render.py `format_time_to_full`): the room left over the run average, over the rate now
in the first minute, nothing when there is no rate or no capacity, and the same wording on the Space page, the Surface page and the HUD. No Tk window and no EDMC."""

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

from plugin import mining_rate as R  # noqa: E402
from plugin import mining_render as render  # noqa: E402
from plugin import mining_space as space_mining  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402


class ArithmeticTests(unittest.TestCase):
    def test_minutes_to_fill_is_the_room_over_the_rate(self) -> None:
        self.assertEqual(R.minutes_to_fill(60, 360), 10.0)             # 60 t at 360 t/h
        self.assertEqual(R.minutes_to_fill(30, 90), 20.0)

    def test_no_rate_or_no_room_gives_no_time(self) -> None:
        self.assertIsNone(R.minutes_to_fill(60, None))
        self.assertIsNone(R.minutes_to_fill(60, 0))
        self.assertIsNone(R.minutes_to_fill(60, -5))
        self.assertIsNone(R.minutes_to_fill(0, 100))

    def test_the_wording(self) -> None:
        self.assertEqual(R.full_in_text(0.2), "less than a minute")
        self.assertEqual(R.full_in_text(1), "about 1 min")
        self.assertEqual(R.full_in_text(14.4), "about 14 min")
        self.assertEqual(R.full_in_text(89.4), "about 89 min")
        self.assertEqual(R.full_in_text(90), "about 1 h 30 min")
        self.assertEqual(R.full_in_text(125), "about 2 h 05 min")
        self.assertEqual(R.full_in_text(24 * 60), "more than a day")


class LineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.space = space_mining.SpaceMiningRepository()
        self.space.set_current_cmdr("Test")
        self.surface = surface_mining.SurfaceMiningRepository()
        self.surface.set_current_cmdr("Test")

    def mined(self, repo, count, step=60.0, name="Painite"):
        for i in range(count):
            repo.record_refined(name, at=i * step)
        return repo.current_run()

    def test_it_uses_the_run_average(self) -> None:
        run = self.mined(self.space, 5)                                # five tons, 240 s of mining: 75 t/h
        self.assertEqual(round(run.clock.average_per_hour(5)), 75)
        self.assertEqual(render.format_time_to_full(run, 100, 200), "Hold full in about 80 min")      # 100 t over 75 t/h

    def test_it_uses_the_rate_now_in_the_first_minute(self) -> None:
        for i in range(4):
            self.space.record_refined("Painite", at=time.time() - 8 + i * 2)
        run = self.space.current_run()
        self.assertIsNone(run.clock.average_per_hour(4))               # under a minute of mining: no average yet
        self.assertTrue(render.format_time_to_full(run, 100, 200).startswith("Hold full in about "))

    def test_nothing_is_said_without_a_rate(self) -> None:
        run = self.space.current_run()
        self.assertEqual(render.format_time_to_full(run, 10, 200), "")
        self.space.record_refined("Painite", at=1000.0)                # one ton, no average, and the rate window has long passed
        self.assertEqual(render.format_time_to_full(self.space.current_run(), 10, 200), "")

    def test_nothing_is_said_without_a_capacity(self) -> None:
        run = self.mined(self.space, 5)
        self.assertEqual(render.format_time_to_full(run, 10, None), "")
        self.assertEqual(render.format_time_to_full(run, 10, 0), "")

    def test_a_full_hold_says_so(self) -> None:
        run = self.mined(self.space, 5)
        self.assertEqual(render.format_time_to_full(run, 200, 200), "Hold is full")
        self.assertEqual(render.format_time_to_full(run, 230, 200), "Hold is full")        # limpets and other cargo can put it over

    def test_a_label_names_the_hold(self) -> None:
        run = self.mined(self.surface, 5)
        self.assertEqual(render.format_time_to_full(run, 30, 72, "SRV hold"), "SRV hold full in about 34 min")       # 42 t over 75 t/h

    def test_a_stowed_rhino_says_nothing(self) -> None:
        run = self.mined(self.surface, 5)
        self.assertEqual(render.format_time_to_full(run, 30, 72, "SRV hold", live=False), "")

    def test_the_ship_hold_helper_agrees_with_the_hold_line(self) -> None:
        tons, capacity = render.ship_hold(40)
        self.assertEqual(render.format_hold(tons, capacity), render.format_ship_cargo(40))


class HudTests(unittest.TestCase):
    def test_the_hud_adds_the_line_after_the_rates(self) -> None:
        from plugin import mining_overlay, mining_pages
        repo = space_mining.space_mining_repository
        repo.set_current_cmdr("Test")
        for i in range(5):
            repo.record_refined("Painite", at=i * 60.0)
        sent = []
        with mock.patch.object(mining_overlay.space_mining.space_mining_repository, "cargo_capacity", return_value=200), \
                mock.patch.object(mining_overlay.space_mining.space_mining_repository, "live_cargo", return_value=100), \
                mock.patch.object(mining_overlay.threading, "Thread", side_effect=lambda target, **kw: types.SimpleNamespace(start=lambda: sent.append(target))):
            mining_overlay.push_stats_overlay(mining_pages.SPACE_MINING, display_cargo_bar=True, display_session_totals=True, display_prospector_hints=False)
        self.assertTrue(sent, "the overlay worker was started")
        lines = sent[0].__closure__ and [c.cell_contents for c in sent[0].__closure__ if isinstance(c.cell_contents, list)]
        flat = [line for group in lines or [] for line in group]
        self.assertIn("Hold full in about 80 min", flat)
        self.assertEqual(flat[0], "Hold: 100 of 200 t")


if __name__ == "__main__":
    unittest.main()
