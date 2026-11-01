"""
Static lookup: mineable commodity -> typical mining method(s).

Not journal data - a MissionAccepted event for a mining mission names the
target commodity (Commodity_Localised) but never says which of the game's
three extraction methods it comes from, because that depends on the ring
being mined, not the mission. Community-sourced, like mission_types.py's
mission-name hints, and needs the same kind of manual upkeep as the game's
ring/commodity tables evolve.

Shared across modes (Missions uses it for mining-mission commodity hints;
Mine mode reuses it too) rather than each mode carrying its own copy.

Most mineable commodities are Laser Surface only, so that's the default
for anything not listed below. A short, well-established list of "premium"
minerals (Alexandrite, Painite, Void Opals, ...) can also come from Core
and/or Sub-surface Deposit mining - some commodities validly have more than
one, since the same material can turn up via different methods depending
on the specific ring/hotspot. Rather than guess which one a given mission
means, every applicable method is shown.
"""

from .mining_names import normalize

CORE = "Core"
LASER_SURFACE = "Laser Surface"
SUBSURFACE = "Sub-surface Deposit"

_METHODS_BY_COMMODITY: dict[str, tuple[str, ...]] = {
    # Void Opals are core-exclusive; everything else in this group can also
    # turn up via a surface deposit or a sub-surface deposit, depending on
    # the ring.
    "Void Opals": (CORE,),
    "Alexandrite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Benitoite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Bromellite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Grandidierite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Low Temperature Diamonds": (CORE, LASER_SURFACE, SUBSURFACE),
    "Monazite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Musgravite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Painite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Rhodplumsite": (CORE, LASER_SURFACE, SUBSURFACE),
    "Serendibite": (CORE, LASER_SURFACE, SUBSURFACE),
}


# The same table under the canonical spelling (mining_names.normalize), so every
# spelling a commodity arrives in - plural, the journal's localized name, the
# internal name, an alias - finds its entry ("Void Opals" and "Void Opal",
# "Low Temperature Diamonds" and "Low Temp. Diamonds").
_METHODS_BY_CANONICAL: dict[str, tuple[str, ...]] = {normalize(name): methods for name, methods in _METHODS_BY_COMMODITY.items()}


def methods_for(commodity: str) -> tuple[str, ...]:
    """Typical mining method(s) for a commodity name in any of its spellings
    (Commodity_Localised, the internal name, the Mining pages' normalized
    name). Defaults to Laser Surface, true for the large majority of
    mineable commodities - only the exceptions above need listing."""
    return _METHODS_BY_CANONICAL.get(normalize(commodity), (LASER_SURFACE,))


def format_methods(methods: tuple[str, ...]) -> str:
    """("Core",) -> "Core"; ("Core", "Laser Surface") -> "Core or Laser
    Surface"; 3+ methods get an Oxford comma before the final "or"."""
    if not methods:
        return ""
    if len(methods) == 1:
        return methods[0]
    lead = ", ".join(methods[:-1])
    return f"{lead}{',' if len(methods) > 2 else ''} or {methods[-1]}"
