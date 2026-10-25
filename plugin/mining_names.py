"""One spelling for a mineral or commodity name, so the mining books and the pages show `Tritium` and not `tritium` beside it.

The journal gives a name two ways: `Type_Localised` (`Low Temp. Diamonds`, `Liquid oxygen`) and the internal `Type` (`tritium`, `lowtemperaturediamond`), and the game's own capitals are not
consistent (`Liquid oxygen` here, `Liquid Oxygen` in the market). `normalize` makes the capitals of every word match, and maps the internal names and the few long and short forms to
one display name. Pure Python: no Tk, no network, no EDMC.
"""
from __future__ import annotations

from typing import Any, Dict

# Keyed by the name with case, spaces, dots and a trailing "s" removed; the value is the display name.
ALIASES: Dict[str, str] = {
    "lowtemperaturediamond": "Low Temp. Diamonds",
    "lowtempdiamond": "Low Temp. Diamonds",
    "opal": "Void Opal",
    "voidopal": "Void Opal",
}


def _key(name: str) -> str:
    text = "".join(ch for ch in name.casefold() if ch.isalnum())
    return text[:-1] if text.endswith("s") else text


def normalize(name: Any) -> str:
    """`name` with the capital letter of every word in place and the known internal and short forms mapped to one name; empty stays empty."""
    text = " ".join(str(name or "").strip().strip("$;").replace("_name", "").replace("_", " ").split())
    if not text:
        return ""
    known = ALIASES.get(_key(text))
    if known:
        return known
    return " ".join(word[:1].upper() + word[1:] for word in text.split(" "))


def merge_counts(counts: Dict[str, Any]) -> Dict[str, Any]:
    """`counts` keyed by name, with the names that differ only in spelling added together under the normalized name."""
    merged: Dict[str, Any] = {}
    for name, count in counts.items():
        key = normalize(name) or str(name)
        merged[key] = merged.get(key, 0) + count if isinstance(count, (int, float)) else count
    return merged
