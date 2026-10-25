"""A body's size from Status.json (plugin/mining_panel.py's dashboard_status): the Rhino's ground trail, CTR and BRD work on a body the journal never gave a Scan event for. No Tk window and
no EDMC."""

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_config = sys.modules.setdefault("config", types.ModuleType("config"))      # another test's stand-in may be there already: add what is missing, never replace it
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0"), ("config", mock.MagicMock())):
    if not hasattr(_config, _attr):
        setattr(_config, _attr, _default)


class _Any(types.ModuleType):
    """A stand-in for an EDMC module: any attribute is a mock."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock()


for _name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes",
              "psutil", "ttkHyperlinkLabel", "theme", "myNotebook"):
    sys.modules.setdefault(_name, _Any(_name))

from plugin import mining_coverage as coverage  # noqa: E402
from plugin import mining_live_position as live_position  # noqa: E402
from plugin import mining_location as location  # noqa: E402
from plugin import mining_panel  # noqa: E402
from plugin import mining_render as render  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402

FLAGS_HAS_LAT_LONG = 1 << 21
BODY, SYSTEM, RADIUS = "Pegasi Sector KO-E a13-2 2", "Pegasi Sector KO-E a13-2", 6485063.0


def _status(**extra) -> dict:
    entry = {"Flags": FLAGS_HAS_LAT_LONG | (1 << 26), "Latitude": 56.85, "Longitude": 78.96, "Heading": 325, "Altitude": 1, "BodyName": BODY, "PlanetRadius": RADIUS}
    entry.update(extra)
    return entry


class StatusRadiusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = surface_mining.SurfaceMiningRepository()
        self.store = coverage.CoverageRepository()
        for patcher in (mock.patch.object(surface_mining, "surface_mining_repository", self.repo), mock.patch.object(coverage, "coverage_repository", self.store),
                        mock.patch.object(location, "current_system", lambda: SYSTEM)):
            patcher.start()
            self.addCleanup(patcher.stop)
        live_position.set_status({})
        self.addCleanup(lambda: live_position.set_status({}))
        self.controller = mining_panel.MiningPanelController()
        self.repo.set_current_cmdr("Test")
        self.repo.set_current_location(SYSTEM, BODY)          # as ApproachBody does
        self.repo.start_run(127)                               # as LaunchSRV does; no Scan event was ever seen

    def test_the_body_size_comes_from_status_json_when_it_was_never_scanned(self) -> None:
        self.assertIsNone(self.repo.radius_for_current_body())
        self.controller.dashboard_status(_status())
        self.assertEqual(self.repo.radius_for_current_body(), RADIUS)

    def test_the_ground_trail_is_recorded_without_a_scan(self) -> None:
        self.controller.dashboard_status(_status())
        body = self.store.for_body(SYSTEM, BODY)
        self.assertIsNotNone(body)
        self.assertEqual(len(body.points), 1)

    def test_ctr_and_brd_work_without_a_scan(self) -> None:
        self.controller.dashboard_status(_status())
        self.assertTrue(render.mark_site(False).startswith("Center marked"))
        self.controller.dashboard_status(_status(Latitude=56.88, Longitude=79.0))
        self.assertTrue(render.mark_site(True).startswith("Border marked"))

    def test_a_scanned_bodys_size_is_replaced_by_the_same_figure_not_lost(self) -> None:
        self.repo.record_body_radius(BODY, RADIUS)
        self.controller.dashboard_status(_status())
        self.assertEqual(self.repo.radius_for_current_body(), RADIUS)

    def test_nothing_is_recorded_without_a_position_or_a_body_name(self) -> None:
        self.controller.dashboard_status({"Flags": 0})
        self.controller.dashboard_status(_status(BodyName=""))
        self.assertIsNone(self.repo.radius_for_current_body())
        self.assertIsNone(self.store.for_body(SYSTEM, BODY))

    def test_the_place_is_filled_in_when_the_journal_never_said_where_you_are(self) -> None:
        fresh = surface_mining.SurfaceMiningRepository()
        fresh.set_current_cmdr("Test")
        fresh.start_run(1)
        with mock.patch.object(surface_mining, "surface_mining_repository", fresh):
            self.controller.dashboard_status(_status())
        self.assertEqual((fresh.current_system, fresh.current_body), (SYSTEM, BODY))
        self.assertEqual(fresh.radius_for_current_body(), RADIUS)

    def test_an_unknown_system_leaves_the_place_alone(self) -> None:
        fresh = surface_mining.SurfaceMiningRepository()
        with mock.patch.object(surface_mining, "surface_mining_repository", fresh), mock.patch.object(location, "current_system", lambda: None):
            self.controller.dashboard_status(_status())
        self.assertIsNone(fresh.current_body)


if __name__ == "__main__":
    unittest.main()
