"""What to do to find a codex entry you are missing, and how far along each kind of entry is. Pure data: no Tk, no network.

The catalog (codex_catalog.py) lists every biological entry as a species plus a color, for example "Bacterium Aurasus - Teal". WFMT already knows the
conditions a species needs (organic_species_data.py) and which star type or surface material gives each color (organic_variant_data.py), so for a missing
entry the window can say where to look instead of only naming it. The conditions are the same ones the Bio predictions use, so they carry the same limits: a
species can have several sets of conditions and any one is enough, and only the first set is shown here with a count of the others.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from . import organic_species_data, organic_variant_data
from .codex_catalog import CatalogEntry


def split_name(english_name: str) -> Tuple[str, str]:
    """('Bacterium Aurasus', 'Teal') for 'Bacterium Aurasus - Teal'; the variant is empty for an entry that has none."""
    species, separator, variant = english_name.partition(" - ")
    return species.strip(), variant.strip() if separator else ""


def _species_index() -> Dict[str, organic_species_data.SpeciesInfo]:
    return {info.name.casefold(): info for info in organic_species_data.SPECIES.values()}


_SPECIES = _species_index()


def _condition_text(rule: organic_species_data.SpeciesRuleset) -> str:
    parts: List[str] = []
    if rule.body_type:
        parts.append(" or ".join(rule.body_type))
    if rule.atmosphere:
        parts.append(" or ".join(rule.atmosphere) + " atmosphere")
    if rule.min_gravity is not None or rule.max_gravity is not None:
        low = "" if rule.min_gravity is None else f"{rule.min_gravity:g}"
        high = "" if rule.max_gravity is None else f"{rule.max_gravity:g}"
        parts.append(f"gravity {low}-{high} g")
    if rule.min_temperature is not None or rule.max_temperature is not None:
        low = "" if rule.min_temperature is None else f"{rule.min_temperature:g}"
        high = "" if rule.max_temperature is None else f"{rule.max_temperature:g}"
        parts.append(f"{low}-{high} K")
    if rule.volcanism:
        parts.append(" or ".join(rule.volcanism) + " volcanism")
    elif rule.requires_volcanism:
        parts.append("volcanism")
    return ", ".join(parts)


def _variant_text(species: str, variant: str) -> str:
    """Which star class or surface material gives this color, or '' when it is not known."""
    if not variant:
        return ""
    rule = organic_variant_data.SPECIES_RULES.get(species.casefold())
    if rule is None:
        rule = organic_variant_data.GENUS_RULES.get(species.split(" ")[0].casefold())
    if rule is None:
        return ""
    kind, entries = rule
    for name, values, _needs in entries:
        if name.casefold() == variant.casefold():
            what = ", ".join(values)
            if kind == "star":
                return f"{variant}: orbiting a class {what} star"
            if kind == "mats":
                return f"{variant}: surface holds {what}"
    return ""


def hint_for(english_name: str) -> str:
    """Where to look for this entry, from WFMT's own species data; '' when it has nothing to say (a Thargoid or Guardian entry, a stellar body)."""
    species, variant = split_name(english_name)
    info = _SPECIES.get(species.casefold())
    if info is None:
        return ""
    pieces = []
    if info.rulesets:
        text = _condition_text(info.rulesets[0])
        if text:
            pieces.append(text + (f" (+{len(info.rulesets) - 1} other set)" if len(info.rulesets) == 2 else
                                  f" (+{len(info.rulesets) - 1} other sets)" if len(info.rulesets) > 2 else ""))
    color = _variant_text(species, variant)
    if color:
        pieces.append(color)
    return "; ".join(pieces)


def progress(catalog: Iterable[CatalogEntry], found_names: Iterable[str], found_ids: Iterable[int] = ()) -> List[Tuple[str, str, int, int]]:
    """(category, type, found, total) for every type of entry in the catalog, matching what is found by raw name or entry id as the Not found list does."""
    names: Set[str] = {n.casefold() for n in found_names}
    ids: Set[int] = {i for i in found_ids if i}
    totals: Dict[Tuple[str, str], List[int]] = {}
    for entry in catalog:
        row = totals.setdefault((entry.category, entry.sub_class or "Other"), [0, 0])
        row[1] += 1
        if entry.name.casefold() in names or (entry.entry_id and entry.entry_id in ids):
            row[0] += 1
    return [(category, kind, found, total) for (category, kind), (found, total) in sorted(totals.items())]


def percent(found: int, total: int) -> str:
    return f"{found / total:.0%}" if total else ""


def closest_to_done(rows: Iterable[Tuple[str, str, int, int]], limit: int = 5) -> List[Tuple[str, str, int, int]]:
    """The types that are started but not finished, fewest entries left first: the quickest ones to complete."""
    open_rows = [r for r in rows if 0 < r[2] < r[3]]
    return sorted(open_rows, key=lambda r: (r[3] - r[2], r[0], r[1]))[:limit]
