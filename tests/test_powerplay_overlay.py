"""Powerplay overlay (powerplay_overlay.py): what the card says in each situation, and that the controller hands it only the system you are in."""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for name in ("myNotebook", "ttkHyperlinkLabel", "theme", "monitor", "plug", "l10n", "requests"):
    sys.modules.setdefault(name, mock.MagicMock())
if "config" not in sys.modules:
    config_stub = types.ModuleType("config")
    config_stub.appname = "EDMarketConnector"
    config_stub.config = mock.MagicMock()
    sys.modules["config"] = config_stub

import threading  # noqa: E402

from plugin import powerplay, powerplay_overlay as O, powerplay_system_lookup as L  # noqa: E402
from plugin.formulas import ACQUISITION, DELIVERY, REINFORCEMENT, UNDERMINING, UNKNOWN  # noqa: E402


def rows(card):
    return {left: (right, role) for left, right, role in card.rows}


class BuildCardTests(unittest.TestCase):
    def test_no_info_or_no_state_is_an_empty_card(self):
        self.assertFalse(O.build_card(None))
        self.assertFalse(O.build_card(O.Info("Sol", "")))

    def test_a_system_without_powerplay_says_so(self):
        card = O.build_card(O.Info("Shinrarta Dezhra", "", status=O.NO_POWERPLAY))
        self.assertEqual(card.header, (("No Powerplay Detected in system", "muted"),))
        self.assertEqual(card.title[0], "Shinrarta Dezhra")
        self.assertEqual(card.badge, "")

    def test_a_destination_is_marked_jumping_and_says_what_it_is_waiting_for(self):
        for status, words in ((O.NO_POWERPLAY, "No Powerplay Detected in system"), (O.LOOKING, "Looking up Powerplay…"), (O.UNAVAILABLE, "Powerplay lookup unavailable")):
            card = O.build_card(O.Info("Sol", "", status=status, destination=True))
            self.assertEqual((card.header[0][0], card.badge), (words, "jumping"))

    def test_a_destination_with_a_standing_shows_it_without_the_session_rows(self):
        info = O.Info("Sol", "Stronghold", "Jerome Archer", "Aisling Duval", 4, 100, "Cycle 3", 50, "undermining", destination=True, progress=0.657)
        shown = rows(O.build_card(info))
        self.assertEqual(shown["System"][0], "Stronghold · 66%")
        self.assertEqual(shown["Held by"][0], "Jerome Archer")
        self.assertEqual(shown["Merits there count as"][0], "Undermining")
        self.assertNotIn("Earned here", shown)
        self.assertEqual(O.build_card(info).badge, "jumping")

    def test_the_sample_card_shows_everything(self):
        card = O.build_card(O.sample_info())
        self.assertEqual(card.title[0], "Sample System")
        self.assertEqual(card.badge, "Rank 12")
        shown = rows(card)
        self.assertEqual(shown["Power"][0], "Aisling Duval")
        self.assertEqual(shown["Total merits"][0], "1,204,500")
        self.assertEqual(shown["Cycle 41 merits"][0], "86,300")
        self.assertEqual(shown["System"][0], "Fortified")
        self.assertEqual(shown["Held by"][0], "Aisling Duval")
        self.assertEqual(shown["Merits here count as"][0], "Reinforcement")
        self.assertEqual(shown["Reinforcement"][0], "4,200 merits · ~1680 CP")

    def test_a_delivery_shows_merits_but_no_control_points(self):
        shown = rows(O.build_card(O.sample_info()))
        self.assertEqual(shown["Delivery/Donation"][0], "1,500 merits")

    def test_not_pledged_leaves_out_the_power_figures_and_the_guess(self):
        shown = rows(O.build_card(O.Info("Sol", "Unoccupied", activity=ACQUISITION)))
        self.assertEqual(shown["Power"][0], "not pledged")
        self.assertNotIn("Total merits", shown)
        self.assertNotIn("Merits here count as", shown)
        self.assertNotIn("Earned here", shown)
        self.assertEqual(O.build_card(O.Info("Sol", "Unoccupied")).badge, "")

    def test_nothing_earned_yet_says_so(self):
        info = O.Info("Sol", "Stronghold", "Li Yong-Rui", "Li Yong-Rui", 3, 100, "Cycle 2", 0, UNDERMINING)
        shown = rows(O.build_card(info))
        self.assertEqual(shown["Earned here"][0], "nothing yet")
        self.assertEqual(shown["Merits here count as"][0], "Undermining")

    def test_an_unheld_system_says_no_one_holds_it(self):
        self.assertEqual(rows(O.build_card(O.Info("Sol", "Unoccupied")))["Held by"][0], "no one")


class ControllerInfoTests(unittest.TestCase):
    def controller(self, system="Nervi", here="Nervi"):
        c = powerplay.PowerplayController()
        c.sessions = mock.MagicMock()
        c.sessions.current = {"by_system": {"Nervi": {"totals": {REINFORCEMENT: 500, DELIVERY: 100}}}}
        c.tracker.my_power, c.tracker.rank, c.tracker.total_merits = "Zachary Hudson", 5, 9000
        c.tracker.system_name, c.tracker.system_state, c.tracker.system_controller = system, "Exploited", "Zachary Hudson"
        c._current_system = here
        return c

    def test_the_figures_come_from_the_tracker_and_the_session(self):
        info = self.controller().overlay_info()
        self.assertEqual((info.system, info.state, info.power, info.rank, info.total_merits), ("Nervi", "Exploited", "Zachary Hudson", 5, 9000))
        self.assertEqual(info.activity, REINFORCEMENT)
        self.assertEqual(dict(info.here), {REINFORCEMENT: 500, DELIVERY: 100})
        self.assertEqual(dict(info.cp), {REINFORCEMENT: 200.0})     # 500 merits at 2.5 per CP; deliveries earn none

    def test_a_context_kept_from_an_earlier_system_is_not_shown(self):
        self.assertIsNone(self.controller(system="Nervi", here="Sol").overlay_info())

    def test_no_powerplay_state_after_an_arrival_says_no_powerplay(self):
        c = self.controller()
        c.tracker.system_state = None
        self.assertIsNone(c.overlay_info())                      # no arrival seen yet: not known, so nothing is claimed
        c._track_jump({"event": "FSDJump", "StarSystem": "Nervi"})
        info = c.overlay_info()
        self.assertEqual((info.system, info.status, info.destination), ("Nervi", O.NO_POWERPLAY, False))

    def test_arriving_somewhere_with_no_powerplay_data_says_so(self):
        c = self.controller(system="Nervi", here="Sol")
        c._track_jump({"event": "FSDJump", "StarSystem": "Sol"})
        self.assertEqual(c.overlay_info().status, O.NO_POWERPLAY)

    def test_system_activity_changes_nothing(self):
        c = self.controller()
        c.tracker._delivery_pending = True
        before = dict(vars(c.tracker))
        self.assertEqual(c.tracker.system_activity("Nervi"), REINFORCEMENT)
        self.assertEqual(vars(c.tracker), before)
        c.tracker.system_controller = "Someone Else"
        self.assertEqual(c.tracker.system_activity("Nervi"), UNDERMINING)
        c.tracker.my_power = None
        self.assertEqual(c.tracker.system_activity("Nervi"), UNKNOWN)


class LookaheadTests(unittest.TestCase):
    ID = 3932277478106

    def setUp(self):
        L.clear()
        self.addCleanup(L.clear)
        self.lookahead = True
        patcher = mock.patch.object(O, "load_config", lambda: O.PowerplayOverlayConfig(enabled=True, lookahead=self.lookahead))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.c = powerplay.PowerplayController()
        self.c.sessions = mock.MagicMock()
        self.c.sessions.current = {}
        self.c.tracker.my_power = "Aisling Duval"
        self.c._current_system = "Sol"

    def start_jump(self, fetch):
        calls = []
        with mock.patch.object(L, "request", lambda id64, on_done=None: calls.append(id64) or True):
            self.c._track_jump({"event": "StartJump", "JumpType": "Hyperspace", "StarSystem": "Nervi", "SystemAddress": self.ID})
        return calls

    def test_a_started_jump_asks_once_and_shows_the_destination(self):
        self.assertEqual(self.start_jump(None), [self.ID])
        self.assertEqual(self.c.overlay_info().status, O.LOOKING)
        L._cache[self.ID] = (L.FOUND, L.Standing("Fortified", "Aisling Duval", ("Aisling Duval",), 0.5), L.time.monotonic())
        info = self.c.overlay_info()
        self.assertEqual((info.system, info.state, info.destination, info.activity), ("Nervi", "Fortified", True, "reinforcement"))

    def test_no_standing_at_the_destination_says_no_powerplay(self):
        self.start_jump(None)
        L._cache[self.ID] = (L.NONE, None, L.time.monotonic())
        info = self.c.overlay_info()
        self.assertEqual((info.system, info.status, info.destination), ("Nervi", O.NO_POWERPLAY, True))

    def test_a_failed_lookup_is_reported(self):
        self.start_jump(None)
        L._cache[self.ID] = (L.FAILED, None, L.time.monotonic())
        self.assertEqual(self.c.overlay_info().status, O.UNAVAILABLE)

    def test_with_the_tick_off_nothing_is_asked_and_the_current_system_shows(self):
        self.lookahead = False
        self.assertEqual(self.start_jump(None), [])
        self.assertIsNone(self.c.overlay_info())                 # in Sol, no arrival seen
        self.c._track_jump({"event": "Location", "StarSystem": "Sol"})
        self.assertEqual(self.c.overlay_info().system, "Sol")

    def test_arriving_or_leaving_the_jump_ends_the_destination(self):
        for event in ("FSDJump", "SupercruiseEntry", "Interdicted", "Died"):
            self.start_jump(None)
            self.c._track_jump({"event": event, "StarSystem": "Nervi"})
            self.assertIsNone(self.c._destination(), event)

    def test_a_jump_that_never_ends_gives_up(self):
        self.start_jump(None)
        with mock.patch.object(powerplay.time, "monotonic", lambda: 1e12):
            self.assertIsNone(self.c._destination())

    def test_a_supercruise_jump_is_not_a_destination(self):
        with mock.patch.object(L, "request", lambda *a, **k: self.fail("asked")):
            self.c._track_jump({"event": "StartJump", "JumpType": "Supercruise", "StarSystem": "Nervi", "SystemAddress": self.ID})
        self.assertIsNone(self.c._destination())


class ArrivalSeedsCacheTests(unittest.TestCase):
    ARRIVAL = {"event": "FSDJump", "StarSystem": "Nervi", "SystemAddress": 42, "PowerplayState": "Exploited", "ControllingPower": "Zachary Hudson",
               "Powers": ["Zachary Hudson", "Li Yong-Rui"], "PowerplayStateControlProgress": 0.25}

    def setUp(self):
        L.clear()
        self.addCleanup(L.clear)

    def test_an_arrival_with_a_state_is_remembered(self):
        powerplay.PowerplayController()._track_jump(self.ARRIVAL)
        self.assertEqual(L.peek(42), (L.FOUND, L.Standing("Exploited", "Zachary Hudson", ("Zachary Hudson", "Li Yong-Rui"), 0.25)))

    def test_a_remembered_system_is_not_asked_about_on_the_next_lap(self):
        c = powerplay.PowerplayController()
        c._track_jump(self.ARRIVAL)
        with mock.patch.object(L, "_fetch", lambda id64: self.fail("asked Spansh")):
            self.assertFalse(L.request(42))

    def test_an_arrival_without_a_state_stores_nothing(self):
        powerplay.PowerplayController()._track_jump({"event": "FSDJump", "StarSystem": "Sol", "SystemAddress": 43})
        self.assertEqual(L.peek(43)[0], L.UNKNOWN)

    def test_other_events_store_nothing(self):
        powerplay.PowerplayController()._track_jump(dict(self.ARRIVAL, event="Docked"))
        self.assertEqual(L.peek(42)[0], L.UNKNOWN)


class SpanshLookupTests(unittest.TestCase):
    def setUp(self):
        L.clear()
        self.addCleanup(L.clear)

    def test_parse_reads_the_standing(self):
        standing = L.parse({"record": {"power_state": "Stronghold", "controlling_power": "Jerome Archer", "power": ["A", "B"], "power_state_control_progress": 0.5}})
        self.assertEqual(standing, L.Standing("Stronghold", "Jerome Archer", ("A", "B"), 0.5))

    def test_parse_returns_none_without_a_state_or_with_junk(self):
        for data in ({"record": {"name": "Shinrarta Dezhra"}}, {"record": None}, {}, [], None):
            self.assertIsNone(L.parse(data))

    def test_request_asks_once_and_answers_from_memory(self):
        done, asked = threading.Event(), []

        def fetch(id64):
            asked.append(id64)
            return L.FOUND, L.Standing("Exploited")
        self.assertTrue(L.request(7, done.set, fetch))
        self.assertTrue(done.wait(5))
        self.assertEqual(L.peek(7), (L.FOUND, L.Standing("Exploited")))
        self.assertFalse(L.request(7, None, fetch))
        self.assertEqual(asked, [7])

    def test_an_answer_expires_and_a_failure_is_retried_sooner(self):
        L._cache[1] = (L.FOUND, L.Standing("Exploited"), 0.0)
        L._cache[2] = (L.FAILED, None, 0.0)
        self.assertEqual(L.peek(1, L.TTL_S - 1)[0], L.FOUND)
        self.assertEqual(L.peek(1, L.TTL_S + 1)[0], L.UNKNOWN)
        self.assertEqual(L.peek(2, L.RETRY_S - 1)[0], L.FAILED)
        self.assertEqual(L.peek(2, L.RETRY_S + 1)[0], L.UNKNOWN)

    def test_control_progress_is_given_out_only_while_fresh(self):
        L._cache[5] = (L.FOUND, L.Standing("Stronghold", "Jerome Archer", (), 0.66), 0.0)
        self.assertEqual(L.peek(5, L.PROGRESS_FRESH_S - 1)[1].progress, 0.66)
        old = L.peek(5, L.PROGRESS_FRESH_S + 1)
        self.assertEqual((old[0], old[1].state, old[1].controller, old[1].progress), (L.FOUND, "Stronghold", "Jerome Archer", None))
        self.assertEqual(L._cache[5][1].progress, 0.66)             # the stored answer is untouched; only what is given out is trimmed

    def test_a_standing_with_no_progress_is_unchanged_when_old(self):
        L._cache[6] = (L.FOUND, L.Standing("Exploited"), 0.0)
        self.assertEqual(L.peek(6, L.TTL_S - 1)[1], L.Standing("Exploited"))

    def test_a_crashing_fetch_is_a_failure(self):
        done = threading.Event()

        def boom(id64):
            raise RuntimeError("no")
        L.request(9, done.set, boom)
        self.assertTrue(done.wait(5))
        self.assertEqual(L.peek(9)[0], L.FAILED)


if __name__ == "__main__":
    unittest.main()
