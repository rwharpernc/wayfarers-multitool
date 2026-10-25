"""What the docked station pays for what a ring run refined, against the galactic average: `Painite here: 521,400 cr/t, 8% above the galactic average (482,000)`.

The game writes `Market.json` when a commodities market is opened (the journal's `Market` event says so), and every item in it carries `MeanPrice`, the galactic average, beside `SellPrice`, what the
station pays per ton. The Space Mining page shows a line for each commodity the run refined that the station buys, so there is something to go on in deciding whether to sell here or fly on. Nothing
is sent anywhere, and nothing is shown until you open the market.

A station lists a `SellPrice` even for goods it does not buy, with no demand, so only an item with demand and a demand bracket above zero counts as bought here. The market is forgotten when
you undock. The parsing is `trade_market.parse_market`; this module keeps the one market that is open and words the lines. No Tk, no network.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from . import journal_files, trade_market

try:
    from config import appname
except ImportError:   # unit tests outside EDMC
    appname = "EDMarketConnector"

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

MAX_LINES = 3
"""At most this many commodities get a line, the ones with the most tons refined: a run rarely refines more, and each line is a line of the panel."""


@dataclass
class Station:
    """The market that is open: whose it is, and its items by canonical name (`trade_market.canonical_name`)."""
    market_id: Any = None
    name: str = ""
    items: Dict[str, trade_market.MarketItem] = field(default_factory=dict)


_current: Optional[Station] = None


def current() -> Optional[Station]:
    return _current


def clear() -> None:
    global _current
    _current = None


def on_market(entry: Mapping[str, Any], folder: Optional[str] = None) -> None:
    """The journal's `Market` event: read `Market.json` for that market and keep it. A file that cannot be read leaves nothing, never a stale market."""
    global _current
    items = trade_market.read_market_file(folder if folder is not None else journal_files.journal_folder(), entry.get("MarketID"))
    _current = Station(entry.get("MarketID"), str(entry.get("StationName") or ""), items) if items else None


def buys(item: trade_market.MarketItem) -> bool:
    """Whether the station buys this commodity: a price to sell at, and demand for it (a bracket above zero; a station lists a price for goods it does not want)."""
    return item.sell_price > 0 and item.demand > 0 and item.demand_bracket > 0 and item.mean_price > 0


def find(items: Mapping[str, trade_market.MarketItem], commodity: str) -> Optional[trade_market.MarketItem]:
    """The market's item for a commodity as the mining pages name it (`Low Temperature Diamonds`): by its localized name, else by the canonical name. The game's internal names are
    not always the display name (`$lowtemperaturediamond_name;`), which is why the localized name comes first."""
    wanted = commodity.strip().casefold()
    for item in items.values():
        if item.name.strip().casefold() == wanted:
            return item
    return items.get(trade_market.canonical_name(commodity))


def percent_from_average(price: int, mean: int) -> int:
    """How far `price` is from `mean`, in whole percent (positive above)."""
    return round((price - mean) * 100 / mean)


def line_for(commodity: str, item: trade_market.MarketItem) -> str:
    difference = percent_from_average(item.sell_price, item.mean_price)
    if difference == 0:
        where = "at the galactic average"
    else:
        where = f"{abs(difference)}% {'above' if difference > 0 else 'below'} the galactic average"
    return f"{commodity} here: {item.sell_price:,} cr/t, {where} ({item.mean_price:,})"


def lines(refined: Mapping[str, int], station: Optional[Station] = None) -> List[str]:
    """One line for each commodity the run refined that the open market buys, the most tons first, at most `MAX_LINES`; none when no market is open."""
    station = _current if station is None else station
    if station is None or not station.items:
        return []
    found: List[str] = []
    for commodity, tons in sorted(refined.items(), key=lambda kv: (-kv[1], kv[0].casefold())):
        item = find(station.items, commodity)
        if item is not None and buys(item):
            found.append(line_for(commodity, item))
        if len(found) >= MAX_LINES:
            break
    return found
