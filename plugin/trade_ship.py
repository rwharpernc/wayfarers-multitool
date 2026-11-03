"""
Which landing pad your ship needs, so Trade mode can leave out stations you could not
dock at. Pure logic.

The pad class of each ship comes from ship data (input: https://github.com/EDCD/coriolis-data,
`properties.class`: 1 = small, 2 = medium,
3 = large), checked 2026-10-09. A ship fits a pad of its own size or bigger, so:
- small ship  -> any pad
- medium ship -> a medium or large pad
- large ship  -> a large pad only

Ship names are matched after lower-casing and dropping everything but letters and
digits, so "Cobra Mk III", "CobraMkIII" and the journal's "cobramkiii" all meet.
The journal's `Loadout.Ship` is an internal name (`cobramkiii`, `empire_trader`);
`ship_display_name` turns it into the display name with the table in `ship_names.py`, then EDMC's own table when it is available, and shows a ship neither
knows as words. Only the pad size is never guessed: a ship that cannot be matched gives None, and the caller falls back to the Settings override or asks
for no pad restriction.
"""
from __future__ import annotations

import re
from typing import Dict, Optional

from . import ship_names

SMALL, MEDIUM, LARGE = "small", "medium", "large"

_BY_CLASS = {1: SMALL, 2: MEDIUM, 3: LARGE}

# normalized display name -> pad class
_PAD_CLASS: Dict[str, int] = {}


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())


def _add(pad_class: int, *names: str) -> None:
    for name in names:
        _PAD_CLASS[_norm(name)] = pad_class


_add(1, "Adder", "Cobra Mk III", "Cobra Mk IV", "Cobra Mk V", "Diamondback Explorer", "Diamondback Scout",
     "Dolphin", "Eagle", "Eagle MkII", "Hauler", "Imperial Courier", "Imperial Eagle", "Kestrel Mk II",
     "Sidewinder", "Sidewinder MkI", "Viper", "Viper MkIII", "Viper Mk IV", "Vulture")
_add(2, "Alliance Challenger", "Alliance Chieftain", "Alliance Crusader", "Asp Explorer", "Asp Scout",
     "Federal Assault Ship", "Federal Dropship", "Federal Gunship", "Fer-de-Lance", "Corsair", "Imperial Corsair",
     "Keelback", "Krait Mk II", "Krait Phantom", "Lynx Highliner", "Mamba", "Mandalay", "Python", "Python Mk II",
     "Type-11 Prospector", "Type-6 Transporter", "Type-8 Transporter")
_add(3, "Anaconda", "Anaconda Mk II", "Beluga Liner", "Caspian Explorer", "Federal Corvette", "Imperial Clipper", "Imperial Cutter",
     "Orca", "Panther Clipper Mk II", "Type-10 Defender", "Type-7 Transporter", "Type-9 Heavy")


def ship_display_name(internal: str) -> str:
    """'empire_trader' -> 'Imperial Clipper'. EDMC's own table names what `ship_names` does not know, and a ship neither knows is shown as words, never as the raw name."""
    key = str(internal or "").lower()
    if not key:
        return ""
    if key in ship_names.NAMES or key in ship_names.VEHICLES or key.endswith("_taxi"):
        return ship_names.display_name(key)
    try:
        from edmc_data import ship_name_map  # EDMC's own table; absent in unit tests
        if key in ship_name_map:
            return str(ship_name_map[key])
    except ImportError:
        pass
    return ship_names.display_name(key)


def pad_size(ship: Optional[str]) -> Optional[str]:
    """'small' / 'medium' / 'large' for a journal ship name or a display name, else None."""
    if not ship:
        return None
    for candidate in (ship, ship_display_name(ship)):
        pad_class = _PAD_CLASS.get(_norm(candidate))
        if pad_class:
            return _BY_CLASS[pad_class]
    return None


def fits(ship_pad: Optional[str], small: Optional[int], medium: Optional[int], large: Optional[int]) -> bool:
    """Can a ship needing `ship_pad` dock at a station with these pad counts? A count of None
    means Spansh did not say, which is treated as 'fits' rather than hiding a good station."""
    if ship_pad in (None, SMALL):
        return True
    needed = [large] if ship_pad == LARGE else [medium, large]
    known = [count for count in needed if count is not None]
    return True if not known else any(count > 0 for count in known)


def label(ship_pad: Optional[str]) -> str:
    return f"{ship_pad} pad" if ship_pad else "pad size unknown"


def known_ships() -> list:
    """Every ship name WFMT knows, as the game shows it (Imperial Clipper, Fer-de-Lance...), A to Z: for the boxes that take a ship."""
    names = set(ship_names.ships())
    try:
        from edmc_data import ship_name_map  # EDMC's own table; absent in unit tests
        names.update(str(name) for name in ship_name_map.values())
    except ImportError:
        pass
    return sorted(names, key=str.casefold)
