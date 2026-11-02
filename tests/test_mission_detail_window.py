"""The Mission description window's content (mission_detail_window.sections): which groups appear, which journal fields get a label and which fall under
"Other journal fields". No Tk window is opened; only the module's import needs tkinter."""
from __future__ import annotations

import importlib
import os
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class _Anything(types.ModuleType):
    def __getattr__(self, name: str):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock(name=f"{self.__name__}.{name}")


import tkinter  # noqa: E402,F401

_EDMC = ("theme", "myNotebook", "monitor", "ttkHyperlinkLabel", "edmc_data", "plug", "companion", "EDMCLogging", "l10n", "timeout_session",
         "protocol", "prefs", "killswitch", "Tooltips", "ttkDefaults", "requests")
_CONFIG = types.ModuleType("config")
_CONFIG.appname = "EDMarketConnector"  # type: ignore[attr-defined]
_CONFIG.config = types.SimpleNamespace(get_str=lambda *_a, **_k: "", get_bool=lambda *_a, default=False, **_k: default, set=lambda *_a: None)  # type: ignore[attr-defined]

import plugin as _plugin_package  # noqa: E402

_BEFORE = set(sys.modules)
with mock.patch.dict(sys.modules, {**{name: _Anything(name) for name in _EDMC}, "config": _CONFIG}):
    W = importlib.import_module("plugin.mission_detail_window")
    B = importlib.import_module("plugin.missions_board")
    all_missions = importlib.import_module("plugin.all_missions")
    mission_types = importlib.import_module("plugin.mission_types")
    _ADDED = [name for name in sys.modules if name not in _BEFORE and name.startswith("plugin.")]
for _name in _ADDED:
    _short = _name.split(".", 1)[1]
    if "." not in _short and hasattr(_plugin_package, _short):
        delattr(_plugin_package, _short)

NOW = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)


def _summary(**kw):
    base = dict(id=7, name="Deliver Gold", source_faction="Faction", destination_system="Sol", destination_station="Dock", reward=1_000_000,
                is_wing=False, expiry=(NOW + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ"), accepted_at="2026-10-15T02:00:00Z",
                category=mission_types.TRADE, is_illegal=False, commodity="", needed_commodity="", needed_commodity_count=0)
    base.update(kw)
    return all_missions.MissionSummary(**base)


def _sections(summary, event):
    row = B.rows_from({summary.id: summary})[0]
    return dict(W.sections(row, summary, event, NOW))


class SectionsTests(unittest.TestCase):
    def test_overview_is_always_there_even_without_the_journal_record(self):
        found = _sections(_summary(), None)
        self.assertEqual(list(found), ["Overview", "Reward and standing", "Journal"])
        self.assertIn(("Mission", "Deliver Gold"), found["Overview"])

    def test_objective_lists_the_target_kills_and_passengers(self):
        event = {"MissionID": 7, "Target_Localised": "Smuggler", "TargetFaction": "Pirates", "KillCount": 40, "PassengerCount": 6,
                 "PassengerType": "Tourist", "PassengerWanted": False, "DestinationSettlement": "Camp 1"}
        objective = dict(_sections(_summary(), event)["Objective"])
        self.assertEqual((objective["Target"], objective["Target faction"], objective["Kills required"]), ("Smuggler", "Pirates", "40"))
        self.assertEqual(objective["Passengers"], "6 (Tourist)")
        self.assertEqual(objective["Destination settlement"], "Camp 1")
        self.assertEqual(objective["Wanted"], "No")      # False is a real journal value, so it is shown

    def test_empty_fields_are_left_out(self):
        event = {"MissionID": 7, "Target": "", "Influence": "", "Reputation": None}
        found = _sections(_summary(), event)
        self.assertNotIn("Objective", found)
        self.assertNotIn("Influence gained", dict(found["Reward and standing"]))

    def test_unlabelled_journal_fields_are_listed_not_dropped(self):
        found = _sections(_summary(), {"MissionID": 7, "Influence": "++", "SomethingNew": ["a", "b"]})
        self.assertEqual(dict(found["Other journal fields"]), {"SomethingNew": "a, b"})
        self.assertEqual(dict(found["Reward and standing"])["Influence gained"], "++")

    def test_a_long_value_is_cut(self):
        found = _sections(_summary(), {"MissionID": 7, "Odd": "x" * 5000})
        self.assertLessEqual(len(dict(found["Other journal fields"])["Odd"]), W._MAX_VALUE)

    def test_pickup_details_appear_under_cargo(self):
        found = _sections(_summary(pickup_commodity="Gold", pickup_count=30, pickup_station="Dock", pickup_pad="Large"), {"MissionID": 7})
        cargo = dict(found["Cargo"])
        self.assertEqual((cargo["Still to pick up"], cargo["Pick up at"], cargo["Largest pad there"]), ("30 t of Gold", "Dock", "Large"))


if __name__ == "__main__":
    unittest.main()
