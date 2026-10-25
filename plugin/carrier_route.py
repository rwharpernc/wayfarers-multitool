"""The Carrier Route planner's logic: what the journal says about your fleet carrier, the request Spansh's fleet carrier router wants, and the route it answers with. Pure Python: no Tk, no
network, no EDMC (`carrier_route_spansh` makes the request and `carrier_route_window` shows the result).

What the journal gives (checked against a real journal, 2026-10-19):

- `CarrierStats` (written when Carrier Management is opened): `CarrierType` ("FleetCarrier" or "SquadronCarrier"), `Name`, `Callsign`, `FuelLevel` (the tritium in the tank), and
  `SpaceUsage` (`TotalCapacity` and `FreeSpace`, so the capacity used is the difference).
- `CarrierLocation` (written at login): `StarSystem` and `SystemAddress`, the system the carrier is in.
The planner is filled in from these, so nothing about the carrier is typed unless the commander wants to change it.

What Spansh's fleet carrier router wants and answers (read from Spansh's own page script and checked against a live answer, 2026-10-19: Sol to Colonia, 46 jumps):

- `POST https://spansh.co.uk/api/fleetcarrier/route`, form fields `source` (a system address), `destinations` (one or more addresses, repeated), `capacity` and `mass` (the carrier's: 25000 and
  25000 for a fleet carrier, 60000 and 15000 for a squadron carrier, as Spansh's page has them), `capacity_used`, and then either `calculate_starting_fuel=1` (with optional
  `refuel_destinations`, the addresses where the commander will restock) or `calculate_starting_fuel=0` with `fuel_loaded` (tritium in the tank) and `tritium_stored` (tritium in the market).
  The answer is `{"job": ..., "status": "queued"}`, then `GET /api/results/<job>`.
- `result["jumps"]` lists every system from the start. Each has `name`, `id64`, `x`, `y`, `z`, `distance` (0 for the start), `distance_to_destination`, `fuel_in_tank`, `fuel_used`,
  `tritium_in_market` (what is left in the carrier's market), `must_restock` and `restock_amount` (restock tritium before leaving there; on the first entry
  it is the total to have at the start, here 3,739 = 1,000 in the tank + 2,739 in the market), `has_icy_ring`, `is_system_pristine` and `is_desired_destination`.
If Spansh changes it, `build_form` and `legs_from_result` are the places to fix.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

FLEET, SQUADRON = "fleet", "squadron"
KIND_LABELS = {FLEET: "Fleet carrier", SQUADRON: "Squadron carrier"}
# (mass, capacity) as Spansh's page has them: a carrier's mass and its total space, which decide its fuel use.
STATS: Dict[str, Tuple[int, int]] = {FLEET: (25000, 25000), SQUADRON: (15000, 60000)}
JOURNAL_KINDS = {"fleetcarrier": FLEET, "squadroncarrier": SQUADRON}
MAX_DESTINATIONS = 10
MAX_TRITIUM = 1000                 # a carrier's tank holds this much tritium
EVENTS = ("CarrierStats", "CarrierLocation", "CarrierJump", "Location")

XYZ = Tuple[float, float, float]


def _int(value: Any) -> Optional[int]:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _number(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def kind_of(raw: Any) -> str:
    """The journal's `CarrierType` as FLEET or SQUADRON (a fleet carrier when it says nothing)."""
    return JOURNAL_KINDS.get(str(raw or "").strip().casefold(), FLEET)


@dataclass
class CarrierInfo:
    """What the journal has told us about one carrier."""
    kind: str = FLEET
    name: str = ""
    callsign: str = ""
    system: str = ""                      # where it is
    address: Optional[int] = None
    tritium: Optional[int] = None         # in the tank
    used_capacity: Optional[int] = None   # tons of its space in use

    def describe(self) -> List[Tuple[str, str]]:
        rows = [("Carrier", f"{self.name or KIND_LABELS[self.kind]} ({KIND_LABELS[self.kind].lower()})"), ("Is in", self.system or "unknown")]
        rows.append(("Tritium in the tank", f"{self.tritium:,} t" if self.tritium is not None else "not known yet"))
        rows.append(("Space used", f"{self.used_capacity:,} of {STATS[self.kind][1]:,} t" if self.used_capacity is not None else "not known yet"))
        return rows


class CarrierTracker:
    """The latest `CarrierInfo` for each commander and carrier kind, from `CarrierStats` and `CarrierLocation` events. In memory only; `recover` fills it from the journals."""

    def __init__(self) -> None:
        self._info: Dict[Tuple[str, str], CarrierInfo] = {}

    @staticmethod
    def _key(cmdr: str, kind: str) -> Tuple[str, str]:
        return (" ".join(str(cmdr or "").split()).casefold(), kind)

    def info(self, cmdr: str, kind: str = FLEET) -> CarrierInfo:
        return self._info.get(self._key(cmdr, kind)) or CarrierInfo(kind)

    def kinds(self, cmdr: str) -> List[str]:
        """The carrier kinds this commander's events have shown, fleet first."""
        return [kind for kind in (FLEET, SQUADRON) if self._key(cmdr, kind) in self._info]

    def handle_event(self, entry: Mapping[str, Any], cmdr: str) -> bool:
        """Take a `CarrierStats` or `CarrierLocation` event for `cmdr`. True when it told us something new."""
        event = entry.get("event")
        if event not in EVENTS or not str(cmdr or "").strip():
            return False
        if event in ("CarrierJump", "Location"):
            return self._follow_docked(entry, cmdr)
        kind = kind_of(entry.get("CarrierType"))
        info = self._info.setdefault(self._key(cmdr, kind), CarrierInfo(kind))
        before = (info.name, info.system, info.address, info.tritium, info.used_capacity)
        if event == "CarrierStats":
            info.name = str(entry.get("Name") or info.name).strip()
            info.callsign = str(entry.get("Callsign") or info.callsign).strip()
            info.tritium = _int(entry.get("FuelLevel")) if _int(entry.get("FuelLevel")) is not None else info.tritium
            usage = entry.get("SpaceUsage")
            if isinstance(usage, Mapping) and _int(usage.get("TotalCapacity")) is not None and _int(usage.get("FreeSpace")) is not None:
                info.used_capacity = max(0, _int(usage["TotalCapacity"]) - _int(usage["FreeSpace"]))
        else:
            system = " ".join(str(entry.get("StarSystem") or "").split())
            if system:
                info.system, info.address = system, _int(entry.get("SystemAddress"))
        return before != (info.name, info.system, info.address, info.tritium, info.used_capacity)

    def _follow_docked(self, entry: Mapping[str, Any], cmdr: str) -> bool:
        """A `CarrierJump` or a `Location` while docked at a carrier says where that carrier is. It is ours only when the station's name is our carrier's callsign (from `CarrierStats`),
        so a visit to someone else's carrier never moves ours."""
        station = str(entry.get("StationName") or "").strip().casefold()
        system = " ".join(str(entry.get("StarSystem") or "").split())
        if not station or not system:
            return False
        for kind in (FLEET, SQUADRON):
            info = self._info.get(self._key(cmdr, kind))
            if info is not None and info.callsign and info.callsign.casefold() == station:
                changed = (info.system, info.address) != (system, _int(entry.get("SystemAddress")))
                info.system, info.address = system, _int(entry.get("SystemAddress"))
                return changed
        return False

    def where(self, cmdr: str) -> Dict[str, str]:
        """The system each of this commander's known carriers is in, by kind."""
        return {kind: self._info[self._key(cmdr, kind)].system for kind in self.kinds(cmdr) if self._info[self._key(cmdr, kind)].system}

    def recover(self, cmdr: str, since_epoch: float, folder: Optional[str] = None) -> bool:
        """Read the carrier's latest stats and place back from the journal files modified since `since_epoch` (the events may have been written before EDMC started). Only the commander's own
        stretches are used: `LoadGame` says who is playing. A missing folder or unreadable file gives nothing, never an error."""
        from . import journal_files
        wanted = journal_files.event_pattern("LoadGame", *EVENTS)
        found = False
        for path in journal_files.files_modified_since(since_epoch, folder):
            playing = ""
            try:
                for entry in journal_files.read_events(path, wanted):
                    if entry.get("event") == "LoadGame":
                        playing = str(entry.get("Commander") or "")
                    elif " ".join(playing.split()).casefold() == " ".join(str(cmdr or "").split()).casefold():
                        found = self.handle_event(entry, cmdr) or found
            except OSError:
                continue
        return found


tracker = CarrierTracker()


def build_form(kind: str, source_id: int, destination_ids: Iterable[int], used_capacity: int, work_out_fuel: bool = True, tritium_in_tank: int = 0,
               tritium_in_market: int = 0, restock_ids: Iterable[int] = ()) -> Dict[str, Any]:
    """The form Spansh's fleet carrier router takes (values as text; a list becomes repeated fields)."""
    mass, capacity = STATS.get(kind, STATS[FLEET])
    destinations = [str(int(i)) for i in destination_ids][:MAX_DESTINATIONS]
    form: Dict[str, Any] = {"source": str(int(source_id)), "destinations": destinations, "capacity": str(capacity), "mass": str(mass),
                            "capacity_used": str(max(0, min(capacity, int(used_capacity))))}
    if work_out_fuel:
        form["calculate_starting_fuel"] = "1"
        restock = [str(int(i)) for i in restock_ids if str(int(i)) in destinations]
        if restock:
            form["refuel_destinations"] = restock
    else:
        form["calculate_starting_fuel"] = "0"
        form["fuel_loaded"] = str(max(0, min(MAX_TRITIUM, int(tritium_in_tank))))
        form["tritium_stored"] = str(max(0, int(tritium_in_market)))
    return form


@dataclass(frozen=True)
class CarrierLeg:
    """One jump of a carrier route: the system to jump to."""
    number: int
    system: str
    distance: float                # ly jumped to get here
    left: float                    # ly still to go from here
    tritium_left: Optional[float]  # in the tank when it arrives
    tritium_used: Optional[float]  # by the jump that got it here
    restock: int = 0               # tritium to have bought before leaving here (0: none)
    icy_ring: bool = False
    pristine: bool = False
    stop: bool = False             # one of the destinations you asked for
    xyz: Optional[XYZ] = None
    id64: Optional[int] = None
    market: Optional[float] = None  # tritium left in the carrier's market when it arrives


def notes_for(leg: CarrierLeg) -> str:
    """What to do at a leg, as short words."""
    words = []
    if leg.restock > 0:
        words.append(f"restock tritium ({leg.restock:,} t)")
    if leg.stop:
        words.append("your stop")
    if leg.icy_ring:
        words.append("icy ring" + (" (pristine)" if leg.pristine else ""))
    return ", ".join(words)


def legs_from_result(result: Any) -> List[CarrierLeg]:
    """Spansh's `result` as legs. The start (no distance) is left out; a malformed entry is skipped."""
    entries = result.get("jumps") if isinstance(result, dict) else None
    legs: List[CarrierLeg] = []
    for raw in entries if isinstance(entries, list) else []:
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str) or not raw["name"].strip():
            continue
        distance = _number(raw.get("distance"))
        if distance <= 0:
            continue                                     # the start itself
        xyz = tuple(float(raw[axis]) for axis in ("x", "y", "z")) if all(isinstance(raw.get(axis), (int, float)) for axis in ("x", "y", "z")) else None
        legs.append(CarrierLeg(
            len(legs) + 1, " ".join(raw["name"].split()), distance, _number(raw.get("distance_to_destination")),
            _number(raw.get("fuel_in_tank")) if raw.get("fuel_in_tank") is not None else None,
            _number(raw.get("fuel_used")) if raw.get("fuel_used") is not None else None,
            int(_number(raw.get("restock_amount"))) if raw.get("must_restock") else 0, bool(raw.get("has_icy_ring")), bool(raw.get("is_system_pristine")),
            bool(raw.get("is_desired_destination")), xyz, _int(raw.get("id64")),
            _number(raw.get("tritium_in_market")) if raw.get("tritium_in_market") is not None else None))
    return legs


def start_needs(result: Any) -> str:
    """What Spansh says you need at the start, from its first entry: "Have 3,739 t of tritium at the start (1,000 in the tank, 2,739 in the carrier's market)." Empty when it says nothing."""
    entries = result.get("jumps") if isinstance(result, dict) else None
    first = entries[0] if isinstance(entries, list) and entries and isinstance(entries[0], dict) else None
    if first is None or not first.get("must_restock"):
        return ""
    total, tank, market = int(_number(first.get("restock_amount"))), int(_number(first.get("fuel_in_tank"))), int(_number(first.get("tritium_in_market")))
    if total <= 0:
        return ""
    return f"Have {total:,} t of tritium at the start ({tank:,} in the tank, {market:,} in the carrier's market)."


@dataclass
class CarrierRoute:
    """A plotted carrier route and how far along it the carrier is."""
    kind: str
    start: str
    end: str
    legs: List[CarrierLeg] = field(default_factory=list)
    reached: int = 0
    needs: str = ""

    @property
    def next_leg(self) -> Optional[CarrierLeg]:
        return self.legs[self.reached] if 0 <= self.reached < len(self.legs) else None

    @property
    def total_distance(self) -> float:
        return sum(leg.distance for leg in self.legs)

    @property
    def distance_left(self) -> float:
        nxt = self.next_leg
        return nxt.distance + nxt.left if nxt is not None else 0.0

    @property
    def jumps_left(self) -> int:
        return max(0, len(self.legs) - self.reached)

    def arrive(self, system: str) -> bool:
        """The carrier is in `system`. When that is a system still ahead on the route (the next or a later one), everything up to it is done. True when something changed."""
        wanted = " ".join(str(system or "").split()).casefold()
        if not wanted:
            return False
        for index in range(self.reached, len(self.legs)):
            if self.legs[index].system.casefold() == wanted:
                self.reached = index + 1
                return True
        return False

    def summary(self) -> str:
        if not self.legs:
            return ""
        text = f"{len(self.legs)} jumps, {self.total_distance:,.0f} ly, {sum(1 for leg in self.legs if leg.restock > 0)} restocks"
        nxt = self.next_leg
        if nxt is None:
            return text + ". Arrived."
        return text + f". Next: {nxt.system}, {self.jumps_left} jumps and {self.distance_left:,.0f} ly to go." + (f" {self.needs}" if self.needs and self.reached == 0 else "")

    def copy_all(self) -> str:
        """The systems still to visit, one per line."""
        return "\n".join(leg.system for leg in self.legs[self.reached:])
