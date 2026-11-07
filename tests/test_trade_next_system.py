"""Trade: Copy next system follows the leg the commander is on and never gives the system they are in."""
import importlib
import sys
import unittest
from unittest import mock

_EDMC_MODULES = ("config", "theme", "myNotebook", "monitor", "ttkHyperlinkLabel", "edmc_data", "plug", "companion",
                 "EDMCLogging", "l10n", "timeout_session", "protocol", "prefs", "killswitch", "Tooltips", "ttkDefaults")


class NextSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        modules = mock.patch.dict(sys.modules, {name: mock.MagicMock(name=name) for name in _EDMC_MODULES})
        modules.start()
        self.addCleanup(modules.stop)
        for name in [m for m in sys.modules if m.startswith("plugin.")]:
            sys.modules.pop(name)
        self.panel = importlib.import_module("plugin.trade_panel").TradePanelController()

    def route(self, stops, loop=False) -> None:
        self.panel._route_stops, self.panel._route_leg, self.panel._route_loop = list(stops), 0, loop

    def arrive(self, system: str, event: str = "Docked") -> None:
        self.panel._system = system
        self.panel._advance_leg(event, system)

    def test_no_route_gives_nothing(self) -> None:
        self.assertIsNone(self.panel._next_stop())

    def test_first_leg_gives_first_destination(self) -> None:
        self.route(["B", "C", "D"])
        self.panel._system = "A"
        self.assertEqual(self.panel._next_stop(), "B")

    def test_docking_at_a_destination_moves_to_the_next_leg(self) -> None:
        self.route(["B", "C", "D"])
        self.arrive("B")
        self.assertEqual(self.panel._next_stop(), "C")
        self.arrive("C")
        self.assertEqual(self.panel._next_stop(), "D")

    def test_never_gives_the_current_system(self) -> None:
        self.route(["B", "C"])
        self.panel._system = "b"   # in B but not yet docked: B is skipped
        self.assertEqual(self.panel._next_stop(), "C")

    def test_jumping_in_without_docking_does_not_finish_the_leg(self) -> None:
        self.route(["B", "C"])
        self.arrive("B", "FSDJump")
        self.assertEqual(self.panel._route_leg, 0)

    def test_docking_elsewhere_does_not_advance(self) -> None:
        self.route(["B", "C"])
        self.arrive("X")
        self.assertEqual(self.panel._next_stop(), "B")

    def test_last_stop_reached_on_a_route_gives_nothing(self) -> None:
        self.route(["B", "C"])
        self.arrive("B")
        self.arrive("C")
        self.assertIsNone(self.panel._next_stop())

    def test_loop_wraps_round(self) -> None:
        self.route(["B", "A"], loop=True)
        self.panel._system = "A"
        self.assertEqual(self.panel._next_stop(), "B")
        self.arrive("B")
        self.assertEqual(self.panel._next_stop(), "A")
        self.arrive("A")
        self.assertEqual(self.panel._next_stop(), "B")

    def test_round_trip_within_one_system_has_no_next(self) -> None:
        self.route(["A", "A"], loop=True)
        self.panel._system = "A"
        self.assertIsNone(self.panel._next_stop())


if __name__ == "__main__":
    unittest.main()
