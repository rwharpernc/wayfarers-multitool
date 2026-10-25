"""A Rhino that was already out when the journal in view began (the game or EDMC was restarted in it, so no LaunchSRV was seen): its refined tons go to the Surface page and the surface history, not
to the ring page and the ring history (plugin/mining_panel.py, plugin/mining_surface.py, plugin/mining_history.py, plugin/mining_bodies_data.py). No Tk window and no EDMC."""

import json
import os
import sys
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

from plugin import mining_bodies_data as bodies_data  # noqa: E402
from plugin import mining_history  # noqa: E402
from plugin import mining_live_position as live_position  # noqa: E402
from plugin import mining_panel  # noqa: E402
from plugin import mining_space as space_mining  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402

SYSTEM, BODY = "Sys", "Sys 1"


def line(**fields):
    return fields


class AdoptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.surface = surface_mining.SurfaceMiningRepository()
        self.space = space_mining.SpaceMiningRepository()
        fake = types.SimpleNamespace(get_bool=lambda key, default=False: default, get_str=lambda key, default="": default, get_int=lambda key, default=0: default, set=lambda *a, **k: None)
        for patcher in (mock.patch.object(surface_mining, "surface_mining_repository", self.surface), mock.patch.object(space_mining, "space_mining_repository", self.space),
                        mock.patch.object(mining_panel, "config", fake), mock.patch.object(mining_history.history, "refresh")):
            patcher.start()
            self.addCleanup(patcher.stop)
        live_position.set_status({})
        self.addCleanup(lambda: live_position.set_status({}))
        self.controller = mining_panel.MiningPanelController()
        self.send(line(event="Commander", Name="Test"), cmdr="Test")
        self.surface.set_current_location(SYSTEM, BODY)

    def send(self, entry, cmdr="Test"):
        self.controller.handle_event(entry, cmdr, SYSTEM, "", {})

    def refine(self, count=1, commodity="Uranium"):
        for _ in range(count):
            self.send(line(event="MiningRefined", Type="$uranium_name;", Type_Localised=commodity))

    def test_a_launch_that_was_seen_still_starts_the_run_as_before(self) -> None:
        self.send(line(event="LaunchSRV", SRVType=surface_mining.RHINO_SRV_TYPE, ID=7))
        self.refine(2)
        self.assertTrue(self.surface.is_active)
        self.assertEqual(self.surface.current_run().refined, {"Uranium": 2})
        self.assertEqual(self.space.current_run().refined if self.space.current_run() else {}, {})

    def test_tons_refined_with_an_srv_out_but_no_launch_seen_go_to_the_surface_page(self) -> None:
        self.send(line(event="Cargo", Vessel="SRV", Count=0))
        self.refine(3)
        self.assertTrue(self.surface.is_active)
        self.assertEqual(self.surface.current_run().refined, {"Uranium": 3})
        run = self.space.current_run()
        self.assertEqual(run.refined if run else {}, {}, "none of it is counted as ring mining")

    def test_the_adopted_run_ends_at_the_dock_whatever_its_id(self) -> None:
        self.send(line(event="Cargo", Vessel="SRV", Count=0))
        self.refine(1)
        self.send(line(event="DockSRV", SRVType=surface_mining.RHINO_SRV_TYPE, ID=99))
        self.assertFalse(self.surface.is_active)
        self.refine(1)                     # a ton after docking, with the ship's hold in view, is ring mining again
        self.send(line(event="Cargo", Vessel="Ship", Count=1))

    def test_a_ton_refined_after_the_rhino_is_docked_is_ring_mining(self) -> None:
        self.send(line(event="Cargo", Vessel="SRV", Count=0))
        self.refine(1)
        self.send(line(event="DockSRV", SRVType=surface_mining.RHINO_SRV_TYPE, ID=99))
        self.send(line(event="Cargo", Vessel="Ship", Count=1))
        self.refine(1, "Platinum")
        self.assertEqual(self.space.current_run().refined, {"Platinum": 1})
        self.assertEqual(self.surface.current_run().refined, {"Uranium": 1})

    def test_a_ship_hold_alone_ends_the_srv_out_signal(self) -> None:
        self.send(line(event="Cargo", Vessel="SRV", Count=0))
        self.send(line(event="Cargo", Vessel="Ship", Count=0))
        self.refine(1)
        self.assertFalse(self.surface.is_active)
        self.assertEqual(self.space.current_run().refined, {"Uranium": 1})

    def test_with_no_sign_of_an_srv_the_tons_are_ring_mining(self) -> None:
        self.refine(2)
        self.assertFalse(self.surface.is_active)
        self.assertEqual(self.space.current_run().refined, {"Uranium": 2})

    def test_status_json_saying_in_srv_is_a_sign_too_but_not_while_replaying_old_lines(self) -> None:
        live_position.set_status({"Flags": 1 << 26})
        self.assertTrue(live_position.in_srv())
        self.controller._backfilling = True
        self.refine(1)
        self.assertFalse(self.surface.is_active, "an old journal line is not judged by the Status.json of now")
        self.controller._backfilling = False
        self.refine(1)
        self.assertTrue(self.surface.is_active)

    def test_a_destroyed_rhino_or_a_death_ends_the_signal_and_the_run(self) -> None:
        for event in ("SRVDestroyed", "Died"):
            self.surface.force_end_run()
            self.send(line(event="Cargo", Vessel="SRV", Count=0))
            self.refine(1)
            self.assertTrue(self.surface.is_active, event)
            self.send(line(event=event))
            self.assertFalse(self.surface.is_active, event)
            self.assertFalse(self.controller._srv_out, event)

    def test_status_in_srv_flag_is_read_and_cleared(self) -> None:
        live_position.set_status({"Flags": 1 << 26})
        self.assertTrue(live_position.in_srv())
        live_position.set_status({"Flags": 0})
        self.assertFalse(live_position.in_srv())
        live_position.set_status({})
        self.assertFalse(live_position.in_srv())


class HistoryTests(unittest.TestCase):
    def ts(self, minute):
        return f"2026-10-20T18:{minute:02d}:00Z"

    def journal(self):
        """The shape of the journal that went wrong: the game started with the Rhino already out, so there is a Location, a hold for the SRV and the refining, but no LaunchSRV."""
        lines = [line(timestamp=self.ts(0), event="Commander", Name="Test"),
                 line(timestamp=self.ts(1), event="Location", StarSystem=SYSTEM, Body=BODY, BodyType="Planet", SystemAddress=1),
                 line(timestamp=self.ts(2), event="Cargo", Vessel="SRV", Count=0)]
        lines += [line(timestamp=self.ts(10 + n), event="MiningRefined", Type="$uranium_name;", Type_Localised="Uranium") for n in range(4)]
        lines += [line(timestamp=self.ts(20), event="DockSRV", SRVType="mev_rhino", ID=3), line(timestamp=self.ts(21), event="Cargo", Vessel="Ship", Count=4),
                  line(timestamp=self.ts(22), event="Docked")]
        return lines

    def test_the_run_history_counts_them_as_the_rhinos_on_that_body(self) -> None:
        runs = mining_history.runs_from(self.journal(), "J.log")
        self.assertEqual(len(runs), 1)
        self.assertEqual((runs[0]["refined"], runs[0]["srv"], runs[0]["body"]), ({"Uranium": 4}, {"Uranium": 4}, BODY))

    def test_the_bodies_list_credits_the_tons_to_the_body(self) -> None:
        found = bodies_data.bodies_from(self.journal())
        self.assertEqual(found[bodies_data.body_key(BODY)]["tons"], 4)

    def test_ring_mining_with_only_the_ships_hold_is_not_the_rhinos(self) -> None:
        lines = [line(timestamp=self.ts(0), event="Commander", Name="Test"), line(timestamp=self.ts(1), event="Undocked"),
                 line(timestamp=self.ts(2), event="Cargo", Vessel="Ship", Count=0),
                 line(timestamp=self.ts(3), event="MiningRefined", Type="$uranium_name;", Type_Localised="Uranium"), line(timestamp=self.ts(9), event="Docked")]
        run = mining_history.runs_from(lines, "J.log")[0]
        self.assertEqual((run["srv"], run["body"]), ({}, ""))

    def test_the_saved_runs_and_bodies_are_read_again_once(self) -> None:
        self.assertEqual(mining_history.RUNS_VERSION, 5)
        self.assertEqual(mining_history.EXTRAS_VERSION, 3)
        self.assertIn("Cargo", mining_history.EVENTS, "the journal reader asks for Cargo lines")


if __name__ == "__main__":
    unittest.main()
