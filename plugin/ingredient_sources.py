"""How a player gets an ingredient, and what WFMT can do to help. No Tk.

An engineer's unlock (and a blueprint) asks for ingredients that are got in different ways: some are bought at a market, some mined, some are engineering materials
that a trader can swap, some are found at a Thargoid or Guardian site, some come from on-foot settlements, some from scanning ships, and some only from a mission
or a rescue. `classify` puts an ingredient in one of those kinds from what the data already says about it (its kind and the places it is found), so the details of an
engineer can say how to get each item and offer the finder WFMT already has for that kind:

- `BUY`: the Source commodities lookup (nearest stations that have it in stock, Spansh, only when asked).
- `TRADE`: the Material trader finder.
- `SITE`: the Canonn lookup of the nearest Thargoid site (the result is in Exploration, POI Reference).
- `MINE`, `SETTLEMENT`, `SCAN` and `SPECIAL`: no finder; the hint says where it comes from.

The wording is the data's own (`Ingredient.found`); nothing here is looked up or sent."""
from __future__ import annotations

from typing import Tuple

from . import blueprints

BUY, MINE, TRADE, SITE, SETTLEMENT, SCAN, SPECIAL = "buy", "mine", "trade", "site", "settlement", "scan", "special"

LABELS = {
    BUY: "Buy at a market",
    MINE: "Mine it",
    TRADE: "Trade engineering materials",
    SITE: "Collect at a Thargoid or Guardian site",
    SETTLEMENT: "Collect at a planetary settlement (on foot)",
    SCAN: "Scan ships or data points",
    SPECIAL: "A mission reward or a rescue",
}

_SITE_GROUPS = ("ThargoidSite", "GuardianSite")


def classify(ingredient: blueprints.Ingredient) -> str:
    """The kind of source of an ingredient, from its kind and where the data says it is found."""
    found = " ".join(ingredient.found).casefold()
    if ingredient.kind == blueprints.COMMODITY:
        if "market" in found:
            return BUY
        if "mining" in found or "prospecting" in found:
            return MINE
        return SPECIAL
    if ingredient.kind == blueprints.ODYSSEY:
        return SETTLEMENT if ("settlement" in found or "crash site" in found or "markers" in found) else SPECIAL
    if ingredient.group in _SITE_GROUPS or "thargoid" in found and "scanning" not in found:
        return SITE
    if "scanning" in found or "data point" in found or "poi" in found:
        return SCAN
    return TRADE


def label(kind: str) -> str:
    return LABELS.get(kind, "")


def how_to_get(ingredient: blueprints.Ingredient) -> Tuple[str, str]:
    """(the kind's label, where the data says it is found) for one line under an ingredient."""
    kind = classify(ingredient)
    where = "; ".join(ingredient.found)
    return label(kind), where
