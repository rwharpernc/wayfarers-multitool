"""The live hold figure (plugin/mining_alerts.py, plugin/mining_space.py, plugin/mining_panel.py, plugin/mining_render.py, plugin/flight_alerts.py): the ship's tons from Status.json,
the capacity from Loadout, the Hold line, and the "Hold nearly full" alert following the live figure with the Cargo event as the fallback. No Tk window and no EDMC."""

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

from plugin import mining_alerts as M  # noqa: E402
from plugin import mining_history  # noqa: E402
from plugin import mining_live_position as live_position  # noqa: E402
from plugin import mining_render as render  # noqa: E402
from plugin import mining_space as space_mining  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402

IN_SHIP = live_position.FLAGS_IN_MAIN_SHIP
IN_SRV = live_position.FLAGS_IN_SRV


def status(cargo, flags=IN_SHIP):
    """A Status.json stand-in: the fields the hold reads."""
    entry = {"event": "Status", "Flags": flags}
    if cargo is not None:
        entry["Cargo"] = cargo
    return entry


class StatusHoldTests(unittest.TestCase):
    def test_the_ships_cargo_is_taken_in_the_main_ship(self) -> None:
        self.assertEqual(M.status_hold(status(64.0), False), (True, 64))
        self.assertEqual(M.status_hold(status(64.4), False), (True, 64))
        self.assertEqual(M.status_hold(status(0.0), False), (True, 0))

    def test_it_is_not_taken_in_an_srv_or_on_foot_and_the_live_figure_is_forgotten(self) -> None:
        self.assertEqual(M.status_hold(status(5.0, IN_SRV), False), (True, None))
        self.assertEqual(M.status_hold(status(5.0, IN_SHIP | IN_SRV), False), (True, None))
        self.assertEqual(M.status_hold(status(5.0, IN_SHIP), True), (True, None), "the journal says a Rhino is out")
        self.assertEqual(M.status_hold(status(5.0, 0), False), (True, None))

    def test_an_entry_with_nothing_usable_changes_nothing(self) -> None:
        self.assertEqual(M.status_hold(status(None), False), (False, None))
        self.assertEqual(M.status_hold({"Cargo": 12}, False), (False, None), "no flags: not known to be the ship")
        self.assertEqual(M.status_hold(status("x"), False), (False, None))
        self.assertEqual(M.status_hold(status(-1), False), (False, None))


class WatcherHoldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.at = 1000.0
        self.watcher = M.MiningWatcher(now=lambda: self.at, target=lambda: ("", 20))
        self.watcher.handle_event({"event": "Loadout", "CargoCapacity": 200})
        self.watcher.handle_event({"event": "MiningRefined", "Type": "painite"})

    def hold(self):
        return [a.lines for a in self.watcher.alerts(hold_percent=95) if a.kind == M.KIND_HOLD]

    def test_the_capacity_comes_from_the_loadout(self) -> None:
        self.assertEqual(self.watcher.capacity, 200)
        self.watcher.handle_event({"event": "Loadout", "CargoCapacity": 0})
        self.assertEqual(self.watcher.capacity, 200, "a loadout with no hold does not erase it")

    def test_the_alert_follows_the_live_figure_without_a_cargo_event(self) -> None:
        self.assertEqual(self.hold(), [])
        self.watcher.handle_status(status(191.0))
        self.assertEqual(self.hold(), [("Hold nearly full", "191 of 200 t")])
        self.watcher.handle_status(status(120.0))
        self.assertEqual(self.hold(), [], "emptied: gone with the next Status.json")

    def test_without_status_data_the_cargo_event_is_the_fallback(self) -> None:
        self.watcher.handle_event({"event": "Cargo", "Vessel": "Ship", "Count": 195})
        self.assertIsNone(self.watcher.live_cargo)
        self.assertEqual(self.hold(), [("Hold nearly full", "195 of 200 t")])

    def test_the_live_figure_wins_over_an_older_cargo_event_then_the_next_event_wins_again(self) -> None:
        self.watcher.handle_event({"event": "Cargo", "Vessel": "Ship", "Count": 195})
        self.watcher.handle_status(status(10.0))
        self.assertEqual(self.hold(), [])
        self.watcher.handle_event({"event": "Cargo", "Vessel": "Ship", "Count": 198})
        self.assertEqual(self.hold(), [("Hold nearly full", "198 of 200 t")])

    def test_in_a_rhino_the_live_figure_is_not_used(self) -> None:
        self.watcher.handle_event({"event": "Cargo", "Vessel": "Ship", "Count": 20})
        self.watcher.handle_status(status(199.0))
        self.assertEqual(self.watcher.live_cargo, 199)
        self.watcher.handle_event({"event": "LaunchSRV", "SRVType": "mev_rhino"})
        self.watcher.handle_status(status(5.0, IN_SRV))
        self.assertIsNone(self.watcher.live_cargo)
        self.assertEqual(self.hold(), [], "the ship's last Cargo event (20 t) is what is left to go on")

    def test_the_alert_still_needs_recent_mining_and_a_known_capacity(self) -> None:
        self.watcher.handle_status(status(199.0))
        self.at += M.ACTIVE_S + 1
        self.assertEqual(self.hold(), [])
        fresh = M.MiningWatcher(now=lambda: self.at, target=lambda: ("", 20))
        fresh.handle_event({"event": "MiningRefined", "Type": "painite"})
        fresh.handle_status(status(199.0))
        self.assertEqual(fresh.alerts(), [])

    def test_the_thresholds_and_wording_are_unchanged(self) -> None:
        self.watcher.handle_status(status(190.0))
        self.assertEqual([a.lines for a in self.watcher.alerts(hold_percent=95)], [("Hold nearly full", "190 of 200 t")])
        self.assertEqual(self.watcher.alerts(hold_percent=96), [])


class FlightAlertsHoldTests(unittest.TestCase):
    def test_a_status_update_alone_raises_the_card(self) -> None:
        from plugin import flight_alerts       # imported here, not at the top: the overlay glue it loads must not be imported before test_overlay_placement swaps in its own config stub
        drawn: list = []
        cfg = flight_alerts.FlightConfig(enabled=True, mining=True)
        alerts = flight_alerts.FlightAlerts(draw=drawn.append, cfg=lambda: cfg)
        alerts.handle_event({"event": "Loadout", "CargoCapacity": 100})
        alerts.handle_event({"event": "MiningRefined", "Type": "painite"})
        alerts.handle_status(status(96.0))
        self.assertIn(("Hold nearly full", flight_alerts.COLOR_AMBER), drawn[-1])
        self.assertIn(("96 of 100 t", flight_alerts.COLOR_AMBER), drawn[-1])


class PanelHoldTests(unittest.TestCase):
    def setUp(self) -> None:
        global mining_panel
        from plugin import mining_panel        # imported here for the same reason as flight_alerts above
        self.space = space_mining.SpaceMiningRepository()
        self.surface = surface_mining.SurfaceMiningRepository()
        fake = types.SimpleNamespace(get_bool=lambda key, default=False: default, get_str=lambda key, default="": default, get_int=lambda key, default=0: default,
                                     set=lambda *a, **k: None)
        for patcher in (mock.patch.object(surface_mining, "surface_mining_repository", self.surface), mock.patch.object(space_mining, "space_mining_repository", self.space),
                        mock.patch.object(mining_panel, "config", fake), mock.patch.object(mining_history.history, "refresh"),
                        mock.patch.object(mining_panel.mining_radar_overlay, "update")):
            patcher.start()
            self.addCleanup(patcher.stop)
        live_position.set_status({})
        self.addCleanup(lambda: live_position.set_status({}))
        self.controller = mining_panel.MiningPanelController()
        self.send({"event": "Commander", "Name": "Test"})

    def send(self, entry):
        self.controller.handle_event(entry, "Test", "Sys", "", {})

    def dash(self, entry):
        self.controller.dashboard_status(entry)

    def test_the_capacity_is_read_from_the_loadout(self) -> None:
        self.send({"event": "Loadout", "Ship": "python", "CargoCapacity": 256})
        self.assertEqual(self.space.cargo_capacity(), 256)

    def test_the_hold_line_follows_status_json_and_falls_back_to_the_cargo_event(self) -> None:
        self.send({"event": "Loadout", "CargoCapacity": 200})
        self.send({"event": "Cargo", "Vessel": "Ship", "Count": 40})
        self.assertEqual(render.format_ship_cargo(self.space.current_run().cargo), "Hold: 40 of 200 t")
        self.dash(status(64.0))
        self.assertEqual(render.format_ship_cargo(self.space.current_run().cargo), "Hold: 64 of 200 t")
        self.dash(status(None))                                    # an entry with no Cargo changes nothing
        self.assertEqual(render.format_ship_cargo(self.space.current_run().cargo), "Hold: 64 of 200 t")
        self.send({"event": "Cargo", "Vessel": "Ship", "Count": 70})
        self.assertEqual(render.format_ship_cargo(self.space.current_run().cargo), "Hold: 70 of 200 t")

    def test_no_capacity_shows_the_tons_alone(self) -> None:
        self.dash(status(12.0))
        self.assertEqual(render.format_ship_cargo(0), "Hold: 12 t")

    def test_in_a_rhino_the_ship_figure_is_the_cargo_events(self) -> None:
        self.send({"event": "Loadout", "CargoCapacity": 200})
        self.send({"event": "Cargo", "Vessel": "Ship", "Count": 40})
        self.dash(status(64.0))
        self.send({"event": "LaunchSRV", "SRVType": "mev_rhino", "ID": 7})
        self.dash(status(3.0, IN_SRV))
        self.assertIsNone(self.space.live_cargo())
        self.assertEqual(render.format_ship_cargo(40, "Ship hold"), "Ship hold: 40 of 200 t")
        self.assertEqual(render.format_srv_cargo(12), "SRV hold: 12 of 72 t")

    def test_the_hud_and_the_page_word_the_hold_the_same(self) -> None:
        self.assertEqual(render.format_hold(64, 200), "Hold: 64 of 200 t")
        self.assertEqual(render.format_hold(64, None), "Hold: 64 t")
        self.assertEqual(render.format_hold(64, 200, "Ship hold"), "Ship hold: 64 of 200 t")


if __name__ == "__main__":
    unittest.main()
