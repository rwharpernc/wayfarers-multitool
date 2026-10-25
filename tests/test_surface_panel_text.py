"""The wording of the Mining panel's lines (plugin/mining_render.py): distances with a space before the unit, deposits and long commodity lists one to a line. No Tk window and no EDMC."""

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

from plugin import mining_hotspots  # noqa: E402
from plugin import mining_render as render  # noqa: E402


def spot(material, rigs=None, **kw):
    return mining_hotspots.Hotspot(system="S", body="B", material=material, rigs=rigs, **kw)


class PanelTextTests(unittest.TestCase):
    def test_distances_have_a_space_before_the_unit(self) -> None:
        self.assertEqual((render.format_distance(750), render.format_distance(3750), render.format_distance(1000)), ("750 m", "3.75 km", "1000 m"))

    def test_a_deposit_reads_in_words(self) -> None:
        self.assertEqual(render.format_hotspot(spot("Painite", 4)), "Painite, 4 rigs")
        self.assertEqual(render.format_hotspot(spot("Painite", 1)), "Painite, 1 rig")

    def test_deposits_go_one_to_a_line_and_a_long_list_says_how_many_more(self) -> None:
        text = render.format_hotspots([spot("Painite", 4), spot("Platinum", 6)])
        self.assertEqual(text.split("\n"), ["   Painite, 4 rigs", "   Platinum, 6 rigs"])
        many = render.format_hotspots([spot(f"M{n}") for n in range(render._ROW_LIMIT + 3)])
        self.assertEqual(many.split("\n")[-1], "   and 3 more")

    def test_the_mine_via_hints_go_one_to_a_line(self) -> None:
        text = render.format_counts({"Painite": 3, "Platinum": 2}, with_mine_via=True)
        self.assertTrue(text.startswith("\n   Painite x3 (Mine via"))
        self.assertEqual(len(text.strip("\n").split("\n")), 2)

    def test_counts_without_hints_stay_on_one_line(self) -> None:
        self.assertEqual(render.format_counts({"Painite": 3, "Platinum": 2}), "Painite x3, Platinum x2")


if __name__ == "__main__":
    unittest.main()
