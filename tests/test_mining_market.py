"""What the docked station pays for what a run refined, against the galactic average (plugin/mining_market.py, the extra fields in plugin/trade_market.py, the line on the Space page in
plugin/mining_render.py). The market items are in the shape of a real Market.json. No Tk window and no EDMC."""

import json
import os
import sys
import tempfile
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

from plugin import mining_market as M  # noqa: E402
from plugin import mining_render as render  # noqa: E402
from plugin import mining_space as space_mining  # noqa: E402
from plugin import trade_market  # noqa: E402


def item(name, token, sell, mean, demand=500, bracket=2):
    """An entry of Market.json's Items, in the shape the game writes (the first entries of a real file were used for the field names)."""
    return {"id": 1, "Name": f"${token}_name;", "Name_Localised": name, "Category": "$MARKET_category_minerals;", "Category_Localised": "Minerals", "BuyPrice": 0, "SellPrice": sell,
            "MeanPrice": mean, "StockBracket": 0, "DemandBracket": bracket, "Stock": 0, "Demand": demand, "Consumer": True, "Producer": False, "Rare": False}


ITEMS = [item("Painite", "painite", 521_400, 482_000), item("Low Temperature Diamonds", "lowtemperaturediamond", 190_000, 200_000),
         item("Platinum", "platinum", 29_966, 55_505, demand=0, bracket=0),             # listed with a price, but not bought here
         item("Gold", "gold", 47_113, 47_113)]


def market_file(folder, market_id=4215761155, items=ITEMS):
    with open(os.path.join(folder, "Market.json"), "w", encoding="utf-8") as handle:
        json.dump({"timestamp": "2026-10-21T12:50:06Z", "event": "Market", "MarketID": market_id, "StationName": "Litke Enterprise", "Items": items}, handle)


class ParseTests(unittest.TestCase):
    def test_the_average_and_the_demand_bracket_are_read(self):
        found = trade_market.parse_market({"Items": ITEMS})
        self.assertEqual((found["painite"].mean_price, found["painite"].demand_bracket, found["painite"].sell_price), (482_000, 2, 521_400))

    def test_a_file_without_them_reads_as_zero(self):
        found = trade_market.parse_market({"Items": [{"Name": "$gold_name;", "SellPrice": 5, "Demand": 1}]})
        self.assertEqual((found["gold"].mean_price, found["gold"].demand_bracket), (0, 0))


class WordingTests(unittest.TestCase):
    def setUp(self):
        self.station = M.Station(1, "Litke", trade_market.parse_market({"Items": ITEMS}))

    def test_above_below_and_at_the_average(self):
        self.assertEqual(M.line_for("Painite", self.station.items["painite"]), "Painite here: 521,400 cr/t, 8% above the galactic average (482,000)")
        self.assertEqual(M.line_for("Low Temperature Diamonds", self.station.items["lowtemperaturediamond"]),
                         "Low Temperature Diamonds here: 190,000 cr/t, 5% below the galactic average (200,000)")
        self.assertEqual(M.line_for("Gold", self.station.items["gold"]), "Gold here: 47,113 cr/t, at the galactic average (47,113)")

    def test_the_percent_is_rounded(self):
        self.assertEqual(M.percent_from_average(104, 100), 4)
        self.assertEqual(M.percent_from_average(996, 1000), 0)
        self.assertEqual(M.percent_from_average(50, 100), -50)


class FindTests(unittest.TestCase):
    def setUp(self):
        self.items = trade_market.parse_market({"Items": ITEMS})

    def test_a_commodity_is_found_by_its_display_name_even_when_the_internal_name_differs(self):
        self.assertEqual(M.find(self.items, "Low Temperature Diamonds").sell_price, 190_000)         # the token is the singular `lowtemperaturediamond`
        self.assertEqual(M.find(self.items, "low temperature diamonds").sell_price, 190_000)

    def test_it_falls_back_to_the_internal_name(self):
        self.assertEqual(M.find(self.items, "Painite").sell_price, 521_400)
        self.assertIsNone(M.find(self.items, "Void Opals"))

    def test_buys_needs_a_price_demand_a_bracket_and_an_average(self):
        make = lambda **kw: trade_market.MarketItem(**{**dict(name="x", sell_price=10, buy_price=0, demand=5, stock=0, mean_price=8, demand_bracket=1), **kw})   # noqa: E731
        self.assertTrue(M.buys(make()))
        for field in ({"sell_price": 0}, {"demand": 0}, {"demand_bracket": 0}, {"mean_price": 0}):
            self.assertFalse(M.buys(make(**field)), field)


class LinesTests(unittest.TestCase):
    def setUp(self):
        M.clear()
        self.addCleanup(M.clear)
        self.station = M.Station(1, "Litke", trade_market.parse_market({"Items": ITEMS}))

    def test_a_line_for_each_refined_commodity_that_the_station_buys_most_tons_first(self):
        refined = {"Gold": 2, "Painite": 30, "Platinum": 9, "Low Temperature Diamonds": 5}
        found = M.lines(refined, self.station)
        self.assertEqual([line.split(" here")[0] for line in found], ["Painite", "Low Temperature Diamonds", "Gold"])     # Platinum is not bought here

    def test_at_most_three_lines(self):
        refined = {name: 10 - i for i, name in enumerate(("Painite", "Low Temperature Diamonds", "Gold", "Silver", "Tin"))}
        items = trade_market.parse_market({"Items": ITEMS + [item("Silver", "silver", 1, 1), item("Tin", "tin", 1, 1)]})
        self.assertEqual(len(M.lines(refined, M.Station(1, "x", items))), M.MAX_LINES)

    def test_no_market_no_lines(self):
        self.assertEqual(M.lines({"Painite": 4}), [])
        self.assertEqual(M.lines({"Painite": 4}, M.Station(1, "x", {})), [])

    def test_nothing_refined_no_lines(self):
        self.assertEqual(M.lines({}, self.station), [])


class EventTests(unittest.TestCase):
    def setUp(self):
        M.clear()
        self.addCleanup(M.clear)
        self.folder = tempfile.mkdtemp()
        self.addCleanup(lambda: [os.remove(os.path.join(self.folder, n)) for n in os.listdir(self.folder)] and None or os.rmdir(self.folder))

    def test_the_market_event_reads_the_file_for_that_market(self):
        market_file(self.folder)
        M.on_market({"event": "Market", "MarketID": 4215761155, "StationName": "Litke Enterprise"}, self.folder)
        self.assertEqual((M.current().name, M.current().market_id), ("Litke Enterprise", 4215761155))
        self.assertEqual(M.lines({"Painite": 3}), ["Painite here: 521,400 cr/t, 8% above the galactic average (482,000)"])

    def test_a_file_for_another_station_leaves_nothing(self):
        market_file(self.folder, market_id=111)
        with mock.patch.object(trade_market, "READ_DELAY_S", 0):
            M.on_market({"event": "Market", "MarketID": 222}, self.folder)
        self.assertIsNone(M.current())

    def test_a_new_market_replaces_the_old_and_clear_forgets_it(self):
        market_file(self.folder)
        M.on_market({"event": "Market", "MarketID": 4215761155}, self.folder)
        market_file(self.folder, market_id=9, items=[item("Painite", "painite", 100, 200)])
        M.on_market({"event": "Market", "MarketID": 9}, self.folder)
        self.assertEqual(M.lines({"Painite": 3}), ["Painite here: 100 cr/t, 50% below the galactic average (200)"])
        M.clear()
        self.assertIsNone(M.current())
        self.assertEqual(M.lines({"Painite": 3}), [])


class PageTests(unittest.TestCase):
    def setUp(self):
        M.clear()
        self.addCleanup(M.clear)
        self.repo = space_mining.space_mining_repository
        self.repo.set_current_cmdr("Test")
        self.settings = render.PanelSettings(True, True, True, False, False, False, False)
        for i in range(3):
            self.repo.record_refined("Painite", at=i * 60.0)

    def lines(self):
        shown = []
        with mock.patch.object(render, "add_line", lambda content, row, wrap, text, *a, **kw: shown.append(text)), \
                mock.patch.object(render, "place_button_bar", lambda *a, **kw: None), \
                mock.patch.object(render, "render_ring_caution", lambda content, wrap, row, enabled: row), \
                mock.patch.object(render, "mission_need_lines", lambda: []):
            render.render_space_mining(None, 400, None, self.settings)
        return shown

    def test_the_page_shows_the_lines_while_a_market_is_open(self):
        M._current = M.Station(1, "Litke", trade_market.parse_market({"Items": ITEMS}))
        shown = self.lines()
        self.assertIn("Painite here: 521,400 cr/t, 8% above the galactic average (482,000)", shown)

    def test_the_page_shows_nothing_extra_without_a_market(self):
        self.assertFalse([line for line in self.lines() if " here: " in line])


if __name__ == "__main__":
    unittest.main()
