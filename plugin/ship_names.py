"""Ship names as a player reads them, from the names the journal uses. No Tk.

The journal names a ship two ways: `Ship` (an internal name such as `anacondamkii`, `empire_trader` or `smallcombat01_nx`, in any case) and, for only some ships,
`Ship_Localised` (the name the game shows). Eagle, Mandalay, Anaconda and Sidewinder, for one, come without the second, and a newer ship can come with only a
codename. `display_name` gives one readable name for all of them:

1. the game's own name (`Ship_Localised` or `ShipType_Localised`) when the journal gave one;
2. otherwise the table here, which covers every ship (and fighter and taxi) the journals of a long-time player hold;
3. otherwise a tidied form of the internal name (`some_new_ship` becomes `Some New Ship`, `mkii` becomes `Mk II`), so a ship added to the game after this table
   was written is still shown as words and never as a raw string.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

NAMES: Dict[str, str] = {
    "adder": "Adder", "anaconda": "Anaconda", "anacondamkii": "Anaconda Mk II", "asp": "Asp Explorer", "asp_scout": "Asp Scout", "belugaliner": "Beluga Liner",
    "cobramkiii": "Cobra Mk III", "cobramkiv": "Cobra Mk IV", "cobramkv": "Cobra Mk V", "corsair": "Corsair", "cutter": "Imperial Cutter",
    "diamondback": "Diamondback Scout", "diamondbackxl": "Diamondback Explorer", "dolphin": "Dolphin", "eagle": "Eagle", "empire_courier": "Imperial Courier",
    "empire_eagle": "Imperial Eagle", "empire_trader": "Imperial Clipper", "explorer_nx": "Caspian Explorer", "federation_corvette": "Federal Corvette",
    "federation_dropship": "Federal Dropship", "federation_dropship_mkii": "Federal Assault Ship", "federation_gunship": "Federal Gunship", "ferdelance": "Fer-de-Lance",
    "hauler": "Hauler", "independant_trader": "Keelback", "independent_trader": "Keelback", "krait_light": "Krait Phantom", "krait_mkii": "Krait Mk II",
    "lakonminer": "Type-11 Prospector", "lander01": "Nomad", "mamba": "Mamba", "mandalay": "Mandalay", "mediumtransport01": "Lynx Highliner", "orca": "Orca",
    "panthermkii": "Panther Clipper Mk II", "python": "Python", "python_nx": "Python Mk II", "sidewinder": "Sidewinder", "smallcombat01_nx": "Kestrel Mk II",
    "type6": "Type-6 Transporter", "type7": "Type-7 Transporter", "type8": "Type-8 Transporter", "type9": "Type-9 Heavy", "type9_military": "Type-10 Defender",
    "typex": "Alliance Chieftain", "typex_2": "Alliance Crusader", "typex_3": "Alliance Challenger", "viper": "Viper Mk III", "viper_mkiv": "Viper Mk IV",
    "vulture": "Vulture",
}
# Ship-launched fighters and the vehicles that are not ships: named like ships, but not offered where a ship is chosen.
VEHICLES: Dict[str, str] = {
    "empire_fighter": "GU-97", "federation_fighter": "F63 Condor", "independent_fighter": "Taipan", "testbuggy": "SRV", "mev_rhino": "Rhino",
}
_ROMAN = {"ii": "II", "iii": "III", "iv": "IV", "v": "V", "vi": "VI"}
_TAXI = "_taxi"


def _key(internal: Any) -> str:
    return str(internal or "").strip().casefold()


def tidy(internal: str) -> str:
    """A readable form of an internal name the table does not know: words split at `_` and before digits, capitalized, `mkii` as `Mk II`."""
    text = re.sub(r"mk(ii|iii|iv|v|vi)\b", lambda m: " mk " + _ROMAN[m.group(1)], internal.replace("_", " "), flags=re.I)
    words = []
    for word in re.sub(r"(?<=[a-z])(?=\d)", " ", text).split():
        words.append(_ROMAN.get(word.lower()) if word.lower() in _ROMAN and words and words[-1] == "Mk" else word.upper() if word.lower() == "nx" else word.capitalize())
    return " ".join(words)


def display_name(internal: Any, localised: Any = "") -> str:
    """The name to show for a ship: the game's own when given, else the table, else the tidied internal name. An empty string only when there is no name at all."""
    named = " ".join(str(localised or "").split())
    if named:
        return named[:60]
    key = _key(internal)
    if not key:
        return ""
    known = {**NAMES, **VEHICLES}
    if key in known:
        return known[key]
    if key.endswith(_TAXI) and key[:-len(_TAXI)] in NAMES:
        return f"{NAMES[key[:-len(_TAXI)]]} (Taxi)"
    return tidy(key)[:60]


def ships() -> List[str]:
    """Every ship the table names, as the game shows it, A to Z (no fighters or vehicles): for a box that takes a ship."""
    return sorted(set(NAMES.values()), key=str.casefold)
