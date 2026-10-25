"""Route Planner: your ship's numbers from the journal, the request Spansh's exact plotter takes, and its route turned into jumps you can read, copy and follow. Pure Python:
no Tk, no network, no EDMC. The window (route_planner_window.py) draws it, the panel (route_planner_panel.py) feeds it the journal, and `spansh_exact` asks Spansh.

**Why the exact plotter.** Spansh's neutron router wants a jump range, and the game writes none for the current load. The exact plotter (https://spansh.co.uk/exact-plotter) works the range out itself, jump by jump, from the ship: the unladen mass, the fuel tanks, the cargo, and the frame shift drive's optimal mass, maximum fuel
per jump and fuel formula, so the ship lightens as it burns fuel and the route knows when to refuel. Every number is in the journal's `Loadout` and Status.json, so the
commander types nothing about the ship. The values below are what Spansh's own page sends for a ship (read from its script on 2026-10-18; a route for this ship was asked for and answered):

- `base_mass` = `Loadout.UnladenMass` + `FuelCapacity.Reserve`; `tank_size` = `FuelCapacity.Main`; `internal_tank_size` = `FuelCapacity.Reserve`; `cargo` = tons carried (Status.json)
- `optimal_mass` and `max_fuel_per_jump` = the drive's base values (`fsd_data.FSD`), replaced by the drive module's engineering modifiers `FSDOptimalMass` and `MaxFuelPerJump` when it has them
- `fuel_multiplier` and `fuel_power` = the drive's (`fsd_data.FSD`); `supercharge_multiplier` = 6 for the Mk II overcharge drive, else 4; `injection_multiplier` = 2
- `range_boost` = the jump range a Guardian FSD booster adds (`fsd_data.GUARDIAN_BOOST`), left out when there is none

A drive that is not in the table is reported, not guessed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

from . import fsd_data

XYZ = Tuple[float, float, float]
RATINGS = {1: "E", 2: "D", 3: "C", 4: "B", 5: "A"}
ALGORITHMS: Tuple[Tuple[str, str], ...] = (("optimistic", "Optimistic"), ("fuel", "Fuel"), ("fuel_jumps", "Fuel and jumps"), ("guided", "Guided"), ("pessimistic", "Pessimistic"))
DEFAULT_ALGORITHM = "optimistic"
_DRIVE = re.compile(r"^int_hyperdrive_(?:overcharge_)?size(\d)_class(\d)")
_BOOSTER = re.compile(r"^int_guardianfsdbooster_size(\d)")
_SCOOP = re.compile(r"^int_fuelscoop_size\d_class\d")


class PlotterError(Exception):
    """Something about the ship that stops a route being asked for; the message is shown to the commander."""


@dataclass(frozen=True)
class ShipParams:
    """What Spansh's exact plotter needs to know about the ship."""
    fuel_power: float
    fuel_multiplier: float
    optimal_mass: float
    base_mass: float
    tank_size: float
    internal_tank_size: float
    max_fuel_per_jump: float
    supercharge_multiplier: int
    injection_multiplier: int
    range_boost: Optional[float] = None
    drive: str = ""
    size: int = 0
    rating: str = ""


def _number(value: Any) -> Optional[float]:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def params_from_loadout(entry: Mapping[str, Any]) -> ShipParams:
    """The ship's numbers from a `Loadout` event. Raises PlotterError saying what is missing."""
    modules = entry.get("Modules")
    drive = next((m for m in modules if isinstance(m, Mapping) and m.get("Slot") == "FrameShiftDrive"), None) if isinstance(modules, list) else None
    if drive is None:
        raise PlotterError("The loadout has no frame shift drive.")
    item = str(drive.get("Item") or "").lower()
    base = fsd_data.FSD.get(item)
    match = _DRIVE.match(item)
    if base is None or match is None:
        raise PlotterError(f"WFMT does not know this frame shift drive ({item or 'unnamed'}), so it cannot tell Spansh what it does. Please report it.")
    optimal, fuel_max, fuel_multiplier, fuel_power = base
    engineering = drive.get("Engineering")
    for modifier in (engineering.get("Modifiers") or []) if isinstance(engineering, Mapping) else []:
        if not isinstance(modifier, Mapping) or _number(modifier.get("Value")) is None:
            continue
        label = str(modifier.get("Label") or "").lower()
        if label == "fsdoptimalmass":
            optimal = float(modifier["Value"])
        elif label == "maxfuelperjump":
            fuel_max = float(modifier["Value"])
    unladen = _number(entry.get("UnladenMass"))
    capacity = entry.get("FuelCapacity")
    main = _number(capacity.get("Main")) if isinstance(capacity, Mapping) else None
    reserve = (_number(capacity.get("Reserve")) if isinstance(capacity, Mapping) else None) or 0.0
    if unladen is None or unladen <= 0 or main is None or main <= 0:
        raise PlotterError("The loadout does not give the ship's mass and fuel tank: change ship, or log in again, so the game sends it.")
    boost = None
    for module in modules:
        found = _BOOSTER.match(str(module.get("Item") or "").lower()) if isinstance(module, Mapping) else None
        if found:
            boost = fsd_data.GUARDIAN_BOOST.get(int(found.group(1)))
    return ShipParams(fuel_power, fuel_multiplier, optimal, unladen + reserve, main, reserve, fuel_max,
                      fsd_data.SUPERCHARGE.get(item, fsd_data.SUPERCHARGE_DEFAULT), fsd_data.INJECTION_MULTIPLIER, boost,
                      item, int(match.group(1)), RATINGS.get(int(match.group(2)), "?"))


@dataclass
class ShipInfo:
    """What the journal has told us about the ship being flown: the loadout (kept as sent) and the cargo on board."""
    loadout: Optional[Dict[str, Any]] = None
    cargo: float = 0.0

    def apply_loadout(self, entry: Mapping[str, Any]) -> bool:
        """Takes a Loadout event. True when it changed anything."""
        changed = self.loadout != dict(entry)
        self.loadout = dict(entry)
        return changed

    def apply_status(self, entry: Mapping[str, Any]) -> bool:
        """Takes a Status.json entry: the cargo on board. True when it changed. (Fuel is not read: the plotter starts from a full tank.)"""
        cargo = _number(entry.get("Cargo"))
        if cargo is None or cargo == self.cargo:
            return False
        self.cargo = cargo
        return True

    def has_fuel_scoop(self) -> Optional[bool]:
        """Whether a fuel scoop is fitted: None while the loadout is not known."""
        modules = (self.loadout or {}).get("Modules")
        if self.loadout is None or not isinstance(modules, list):
            return None
        return any(isinstance(m, Mapping) and _SCOOP.match(str(m.get("Item") or "").lower()) for m in modules)

    def params(self) -> ShipParams:
        """The numbers for Spansh. Raises PlotterError when there is no loadout yet or the ship cannot be described."""
        if self.loadout is None:
            raise PlotterError("The ship is not known yet: log in, or change ship, so the game sends its loadout.")
        return params_from_loadout(self.loadout)

    def name(self) -> str:
        loadout = self.loadout or {}
        custom, ident = str(loadout.get("ShipName") or "").strip(), str(loadout.get("ShipIdent") or "").strip()
        kind = str(loadout.get("Ship_Localised") or loadout.get("Ship") or "").strip()
        if custom and ident:
            return f"{custom} ({ident})"
        return custom or ident or kind

    def describe(self) -> List[Tuple[str, str]]:
        """Label and value rows for the window's ship block: what Spansh will be told. Only the cargo changes while flying, so the block stays still."""
        if self.loadout is None:
            return [("Ship", "not known yet: the game tells WFMT when you log in or change ship")]
        rows: List[Tuple[str, str]] = [("Ship", self.name() or "unnamed")]
        try:
            params = self.params()
        except PlotterError as err:
            return rows + [("Problem", str(err))]
        rows.append(("Frame shift drive", f"Class {params.size}, Rating {params.rating}"))
        rows.append(("FSD booster", "Guardian, +%g ly" % params.range_boost if params.range_boost else "No"))
        rows.append(("FSD optimal mass", f"{params.optimal_mass:,.1f} t"))
        rows.append(("Fuel scoop", "Yes" if self.has_fuel_scoop() else "NONE FITTED: you cannot refuel at stars, so the route's refuel stops will not work"))
        rows.append(("Supercharge", f"Yes ({params.supercharge_multiplier}x)"))
        rows.append(("Fuel tank", f"{params.tank_size:g} t (the route starts from a full tank)"))
        rows.append(("Cargo", f"{self.cargo:g} t"))
        return rows


@dataclass(frozen=True)
class Options:
    """What the commander chooses about the route."""
    use_supercharge: bool = True
    use_injections: bool = False
    exclude_secondary: bool = False
    refuel_every_scoopable: bool = False
    algorithm: str = DEFAULT_ALGORITHM
    mark_white_dwarfs: bool = False      # ask EDSM which jump systems have a white dwarf as their main star, and mark them as extra boosts


def build_form(params: ShipParams, cargo: float, options: Options, source_id: int, destination_id: int) -> Dict[str, str]:
    """The form Spansh's exact plotter takes (the field names its own page sends)."""
    form = {
        "source": str(source_id), "destination": str(destination_id),
        "is_supercharged": "0", "use_supercharge": "1" if options.use_supercharge else "0",
        "use_injections": "1" if options.use_injections else "0", "use_injections_when_required": "0",
        "exclude_secondary": "1" if options.exclude_secondary else "0", "refuel_every_scoopable": "1" if options.refuel_every_scoopable else "0",
        "fuel_power": f"{params.fuel_power:.10g}", "fuel_multiplier": f"{params.fuel_multiplier:.10g}", "optimal_mass": f"{params.optimal_mass:.10g}",
        "base_mass": f"{params.base_mass:.10g}", "tank_size": f"{params.tank_size:.10g}", "internal_tank_size": f"{params.internal_tank_size:.10g}", "reserve_size": "0",
        "max_fuel_per_jump": f"{params.max_fuel_per_jump:.10g}", "max_time": "60", "cargo": str(max(0, int(round(cargo)))),
        "algorithm": options.algorithm if options.algorithm in dict(ALGORITHMS) else DEFAULT_ALGORITHM,
        "supercharge_multiplier": str(params.supercharge_multiplier), "injection_multiplier": str(params.injection_multiplier),
    }
    if params.range_boost:
        form["range_boost"] = f"{params.range_boost:.10g}"
    return form


@dataclass(frozen=True)
class Leg:
    """One jump on the route: the system to jump to."""
    number: int                  # 1 for the first jump from the start
    system: str
    jumps: int                   # always 1 for the exact plotter (it lists every jump); kept so a leg can stand for several
    distance: float              # ly jumped to get here
    left: float                  # ly still to go from here
    neutron: bool                # a neutron star: supercharge here
    xyz: Optional[XYZ] = None
    fuel_left: Optional[float] = None
    fuel_used: Optional[float] = None
    refuel: bool = False         # Spansh says to refuel before leaving here
    inject: bool = False         # use an FSD injection here
    scoopable: bool = False
    white_dwarf: bool = False    # EDSM says the main star is a white dwarf (an extra boost Spansh did not plan for; only set when asked)
    id64: Optional[int] = None   # the system's address, to ask Spansh about its stars

    @property
    def boost(self) -> bool:
        """A star that supercharges the drive here: a neutron star, or a white dwarf when white dwarfs were marked."""
        return self.neutron or self.white_dwarf


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def legs_from_result(result: Any) -> List[Leg]:
    """Spansh's exact-plotter `result` (a dict whose `jumps` lists every system from the start) as legs. The start (no distance) is left out; a malformed entry is skipped."""
    entries = result.get("jumps") if isinstance(result, dict) else None
    legs: List[Leg] = []
    for raw in entries if isinstance(entries, list) else []:
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str) or not raw["name"].strip():
            continue
        distance = _num(raw.get("distance"))
        if distance <= 0:
            continue                                     # the start itself
        xyz = None
        if all(isinstance(raw.get(axis), (int, float)) for axis in ("x", "y", "z")):
            xyz = (float(raw["x"]), float(raw["y"]), float(raw["z"]))
        legs.append(Leg(len(legs) + 1, " ".join(raw["name"].split()), 1, distance, _num(raw.get("distance_to_destination")), bool(raw.get("has_neutron")), xyz,
                        _num(raw.get("fuel_in_tank")) if raw.get("fuel_in_tank") is not None else None,
                        _num(raw.get("fuel_used")) if raw.get("fuel_used") is not None else None,
                        bool(raw.get("must_refuel")), bool(raw.get("must_inject")), bool(raw.get("is_scoopable")), False,
                        raw["id64"] if isinstance(raw.get("id64"), int) and not isinstance(raw.get("id64"), bool) else None))
    return legs


@dataclass
class Route:
    """A plotted route and where the commander is along it."""
    start: str
    end: str
    legs: List[Leg] = field(default_factory=list)
    reached: int = 0             # how many legs have been arrived at, in order
    white_dwarf_check: str = ""   # "" when white dwarfs were not asked about, "done" once EDSM answered, "failed" when it could not be asked
    suspect: Set[str] = field(default_factory=set)    # neutron stops (casefolded names) whose neutron star is probably a secondary star, not where you arrive
    checked: Set[str] = field(default_factory=set)    # neutron stops whose stars have been looked at (so each is asked about once)

    @property
    def total_jumps(self) -> int:
        return sum(leg.jumps for leg in self.legs)

    @property
    def total_distance(self) -> float:
        return sum(leg.distance for leg in self.legs)

    @property
    def neutron_count(self) -> int:
        return sum(1 for leg in self.legs if leg.neutron)

    @property
    def white_dwarf_count(self) -> int:
        return sum(1 for leg in self.legs if leg.white_dwarf and not leg.neutron)

    @property
    def next_leg(self) -> Optional[Leg]:
        return self.legs[self.reached] if self.reached < len(self.legs) else None

    @property
    def jumps_left(self) -> int:
        return sum(leg.jumps for leg in self.legs[self.reached:])

    @property
    def distance_left(self) -> float:
        nxt = self.next_leg
        return nxt.left + nxt.distance if nxt is not None else 0.0

    def next_supercharge(self) -> Optional[Tuple[int, Leg]]:
        """(jumps away, the leg) of the next neutron star (or marked white dwarf) still ahead, or None."""
        for number, leg in enumerate(self.legs[self.reached:], 1):
            if leg.boost:
                return number, leg
        return None

    def next_refuel(self) -> Optional[Tuple[int, Leg]]:
        """(jumps away, the leg) of the next place Spansh says to refuel, or None."""
        for number, leg in enumerate(self.legs[self.reached:], 1):
            if leg.refuel:
                return number, leg
        return None

    def arrive(self, system: str) -> bool:
        """Note an arrival. Reaching a system on the route (the next one, or one further on) moves the position to it. True when it moved."""
        wanted = " ".join(str(system or "").split()).casefold()
        for index in range(self.reached, len(self.legs)):
            if self.legs[index].system.casefold() == wanted:
                self.reached = index + 1
                return True
        return False

    def summary(self) -> str:
        if not self.legs:
            return "No route."
        text = f"{len(self.legs)} jumps, {self.total_distance:,.0f} ly, {self.neutron_count} neutron stars"
        if self.white_dwarf_check == "done":
            text += f" and {self.white_dwarf_count} white dwarfs"
        nxt = self.next_leg
        if nxt is None:
            return text + ". You have arrived."
        return text + f". Next: {nxt.system}" + (" (neutron star)" if nxt.neutron else " (white dwarf)" if nxt.white_dwarf else "") + f", {self.jumps_left} jumps and {self.distance_left:,.0f} ly to go."


def copy_all(route: Route) -> str:
    """The systems still to visit, one per line, in order, for pasting into a note."""
    return "\n".join(leg.system for leg in route.legs[route.reached:])


def notes_for(leg: Leg, suspect: bool = False) -> str:
    """What to do at a leg, as short words: supercharge, refuel, inject. A neutron stop that is `suspect` says its neutron star may be a secondary star."""
    return ", ".join(word for word, on in ((("neutron: may be a secondary star, check" if suspect else "neutron: supercharge"), leg.neutron), ("white dwarf: supercharge", leg.white_dwarf and not leg.neutron), ("refuel", leg.refuel), ("FSD injection", leg.inject)) if on)


def mark_white_dwarfs(legs: List[Leg], star_types: Mapping[str, str]) -> List[Leg]:
    """The legs with `white_dwarf` set for each system whose main star EDSM calls a white dwarf. `star_types` maps a casefolded system name to EDSM's star type
    ("White Dwarf (DA) Star"); a system it does not list is left unmarked. Spansh planned the route without these stars, so they are extra boosts, not planned stops."""
    return [replace(leg, white_dwarf=not leg.neutron and "white dwarf" in star_types.get(leg.system.casefold(), "").casefold()) for leg in legs]
