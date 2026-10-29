"""Mining alerts for the Flight Alerts card: a core asteroid found, a rock rich in the commodity you chose, limpets running low and a hold nearly full. Pure logic: no Tk, no network,
and EDMC's `config` only when the settings are read. `flight_alerts` draws what this module decides, and `mining_space` / `mining_render` show the same rock findings on the Space Mining page.

What the journal gives (checked against a real journal, 2026-10-19):

- `ProspectedAsteroid` carries `Materials` (each with `Name` and a `Proportion` in percent), a `Content` grade, `Remaining` (percent of the rock left) and, for a core (motherlode)
  asteroid, `MotherlodeMaterial` (the name of the core mineral, for example "Bromellite"). A rock's own composition is the only thing the game says about it: not its value.
- `Cargo` (Vessel "Ship") gives the number of tons aboard; `Loadout` gives `CargoCapacity` (checked against a real journal, 2026-10-21). `Status.json` carries the tons the ship
  holds as `Cargo` as well, and EDMC hands it over about once a second, so the hold alert reads that when it has it and falls back to the `Cargo` event when it has not. What `Cargo`
  means in `Status.json` while an SRV is out is not known (the file is overwritten every second and keeps no history), so the live figure is not taken then. EDMC also passes the ship's cargo by name in the `state` it hands to every plugin;
  limpets are `drones` there, so the number of limpets aboard is exact (the panel's older "bought less launched" figure is only an estimate).

An alert about a rock lasts `ROCK_ALERT_S` seconds; the limpet and hold alerts last while their condition holds, and only while you are mining (a prospector, refinery or collector event in the
last `ACTIVE_S` seconds), so a hold that is full for another reason never nags.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional, Tuple

from .mining_live_position import FLAGS_IN_MAIN_SHIP, FLAGS_IN_SRV
from .mining_names import normalize
from .mining_targets import DEFAULT_TARGET_PERCENT, MAX_TARGETS, TARGET_PERCENT_RANGE, Target, parse_targets

CFG_TARGET = "wfmt_mining_target_commodity"
CFG_TARGET_PERCENT = "wfmt_mining_target_percent"

DEFAULT_LIMPETS_LOW = 5
LIMPETS_RANGE = (0, 99)
DEFAULT_HOLD_PERCENT = 95
HOLD_RANGE = (50, 100)

MAX_TARGET_CARDS = 3         # a rock rich in more targets than this shows the richest few, so the card stays short
ROCK_ALERT_S = 30.0          # how long a core or target-rock alert stays on the card
ACTIVE_S = 30 * 60           # the limpet and hold alerts apply this long after the last mining event
MIN_REMAINING_PERCENT = 25.0  # a rock with less than this share of itself left is not worth a "rich rock" alert (a core alert is still raised)

RHINO_SRV = "mev_rhino"      # the `SRVType` of the Rhino, the only vehicle that refines ore
# Limpet controllers that mining uses, as the start of a `Loadout` module's `Item` (for example "int_dronecontrol_prospector_size3_class5").
MINING_CONTROLLERS = ("int_dronecontrol_prospector", "int_dronecontrol_collection")

MINING_EVENTS = ("ProspectedAsteroid", "MiningRefined", "LaunchDrone", "AsteroidCracked")

KIND_CORE = "core"
KIND_TARGET = "target"
KIND_LIMPETS = "limpets"
KIND_HOLD = "hold"


def clamp(value: Any, low: int, high: int, default: int) -> int:
    try:
        number = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def load_target() -> Tuple[str, int]:
    """(the target box's text, the default minimum percent) from Settings → Mining. The text is "" when none is chosen, one commodity name as it always was, or several with their own
    percentages (`mining_targets.parse_targets` reads it); the percent is the one used for a name that has none of its own."""
    from config import config
    return (str(config.get_str(CFG_TARGET) or "").strip(),
            clamp(config.get_str(CFG_TARGET_PERCENT), *TARGET_PERCENT_RANGE, DEFAULT_TARGET_PERCENT))


def primary_target() -> str:
    """The first commodity in the target box ("" for none): what the radar points at and What pays puts first, which take one commodity."""
    text, percent = load_target()
    parsed = parse_targets(text, percent).targets
    return parsed[0].name if parsed else ""


@dataclass(frozen=True)
class Alert:
    kind: str
    lines: Tuple[str, ...]
    rock: Optional[tuple] = None                  # for a rock alert, the rock's composition: what its sound is keyed on, so changing text never sounds twice
    target: Optional[str] = None                  # for a target alert, the commodity that hit: a rock rich in two targets sounds for each


@dataclass(frozen=True)
class RockFinding:
    """What a prospected rock is, for the page and the card."""
    materials: Tuple[Tuple[str, float], ...]      # (name, percent), richest first
    grade: str
    remaining: Optional[float]                    # percent of the rock left, when the journal says
    core: Optional[str]                           # the core mineral, for a motherlode asteroid
    target: Optional[Tuple[str, float]]           # (the target commodity's name, its percent) of the richest target at or over its threshold
    key: Optional[tuple] = None                   # the rock's composition (`prospect_key`), to tell a re-prospect of the same rock
    hits: Tuple[Tuple[str, float], ...] = ()      # every target at or over its own threshold, richest first (`target` is the first)


def display_name(material: Mapping[str, Any]) -> str:
    """A material's name as the game words it (`Name_Localised`), else its raw name with a capital."""
    localised = material.get("Name_Localised")
    if isinstance(localised, str) and localised.strip():
        return localised.strip()
    raw = str(material.get("Name") or "").strip()
    return raw[:1].upper() + raw[1:] if raw else ""


def core_name(entry: Mapping[str, Any]) -> Optional[str]:
    """The core mineral of a motherlode asteroid, or None for an ordinary rock."""
    text = str(entry.get("MotherlodeMaterial_Localised") or entry.get("MotherlodeMaterial") or "").strip()
    return (text[:1].upper() + text[1:]) if text else None


def _number(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def prospect_key(materials: Optional[List[Any]]) -> Optional[tuple]:
    """A rock's material composition as a hashable signature, to spot the same asteroid prospected twice (a re-scan after the prospector's cooldown, or a relog while still in the same
    belt): the journal gives asteroids no identity of their own. The proportion is rounded to one decimal place since repeat scans of the same rock can differ by a rounding error.
    The Space Mining page, Mining History and the rock alerts all count a rock once by this key. None when the event lists no usable materials, which is never treated as a repeat."""
    if not materials:
        return None
    parsed = []
    for material in materials:
        if not isinstance(material, Mapping):
            continue
        name, proportion = material.get("Name"), material.get("Proportion")
        if not isinstance(name, str) or proportion is None:
            continue
        try:
            parsed.append((name.lower(), round(float(proportion), 1)))
        except (TypeError, ValueError):
            continue
    return tuple(sorted(parsed)) if parsed else None


def rock_finding(entry: Mapping[str, Any], target: str = "", threshold: int = DEFAULT_TARGET_PERCENT) -> RockFinding:
    """Read a `ProspectedAsteroid` event. `target` is the target box's text from Settings (blank for none: one commodity, or several each with its own percent, see
    `mining_targets.parse_targets`) and `threshold` the least percent for a commodity that names none of its own."""
    found: List[Tuple[str, float]] = []
    for material in entry.get("Materials") or []:
        if not isinstance(material, Mapping):
            continue
        name, percent = display_name(material), _number(material.get("Proportion"))
        if name and percent is not None:
            found.append((name, percent))
    found.sort(key=lambda pair: -pair[1])
    grade = str(entry.get("Content_Localised") or "").rsplit(":", 1)[-1].strip() or str(entry.get("Content") or "").strip("$;").rsplit("_", 1)[-1] or "?"
    hits: List[Tuple[str, float]] = []
    for wanted in parse_targets(target, threshold).targets:
        # both sides in the one canonical spelling, so "Void Opals" finds a rock reported as "Void Opal"
        hit = next(((name, percent) for name, percent in found if normalize(name) == wanted.key and percent >= wanted.percent), None)
        if hit is not None and hit not in hits:
            hits.append(hit)
    hits.sort(key=lambda pair: -pair[1])
    return RockFinding(tuple(found), grade, _number(entry.get("Remaining")), core_name(entry), hits[0] if hits else None, prospect_key(entry.get("Materials")), tuple(hits))


def rock_text(finding: RockFinding, limit: int = 3, last_core: str = "") -> str:
    """One line for the Space Mining page: "Last rock: Painite 34%, Platinum 12% (High)". `last_core` is the core the run's "Core asteroids found" line already names; the rock's core is left off when it is that one."""
    parts = ", ".join(f"{name} {percent:.0f}%" for name, percent in finding.materials[:limit]) or "no materials listed"
    return f"Last rock: {parts} ({finding.grade})" + (f", core: {finding.core}" if finding.core and finding.core != last_core else "") + (f", target: {_hit_names(finding)}" if finding.target else "")


def _hit_names(finding: RockFinding, limit: int = MAX_TARGET_CARDS) -> str:
    """The targets a rock hit, richest first, for the page line: "Painite", "Painite / Platinum", "Painite / Platinum / Osmium / 2 more"."""
    names = [name for name, _percent in finding.hits] or ([finding.target[0]] if finding.target else [])
    shown = names[:limit] + ([f"{len(names) - limit} more"] if len(names) > limit else [])
    return " / ".join(shown)


def limpets_aboard(state: Optional[Mapping[str, Any]]) -> Optional[int]:
    """The exact number of limpets in the hold, from the cargo EDMC keeps by name; None when EDMC has not told us the cargo yet."""
    cargo = (state or {}).get("Cargo")
    if not isinstance(cargo, Mapping):
        return None
    for name, count in cargo.items():
        if str(name).casefold() == "drones":
            number = _number(count)
            return int(number) if number is not None else None
    return 0


class MiningWatcher:
    """Remembers the latest rock, the limpets and the hold, and says which alerts are active. `now` and `target` are injected so it is tested without the clock or the settings."""

    def __init__(self, now: Callable[[], float] = time.time, target: Callable[[], Tuple[str, int]] = load_target) -> None:
        self._now = now
        self._target = target
        self._rocks: List[Tuple[Alert, float]] = []   # the rock alerts showing, each with the time it ends
        self._last_mining: Optional[float] = None
        self.limpets: Optional[int] = None
        self.cargo: Optional[int] = None          # tons aboard as the latest `Cargo` event said
        self.live_cargo: Optional[int] = None     # tons aboard as the latest `Status.json` said; None until it has, and while an SRV is out
        self.capacity: Optional[int] = None
        self.last_rock: Optional[RockFinding] = None
        self._seen_rocks: set = set()             # compositions already handled this run
        self._alerted: set = set()                # (composition, "core" or the target's name) already alerted this run
        self._controller: Optional[bool] = None   # whether the latest Loadout fits a prospector or collector controller; None before any Loadout
        self._limpets_seen = False                # limpets were aboard at some point since the latest Loadout
        self._rhino = False                       # a Rhino is out

    def handle_event(self, entry: Mapping[str, Any], state: Optional[Mapping[str, Any]] = None) -> None:
        event = entry.get("event")
        known = limpets_aboard(state)
        if known is not None:
            self.limpets = known
        if event == "Cargo" and entry.get("Vessel", "Ship") == "Ship":
            count = _number(entry.get("Count"))
            if count is not None:
                self.cargo = int(count)
                self.live_cargo = None             # the event is the newest word on the hold; the next Status.json update says again
        elif event == "Loadout":
            capacity = _number(entry.get("CargoCapacity"))
            if capacity is not None and capacity > 0:
                self.capacity = int(capacity)
            self._controller = fits_controller(entry)
            self._limpets_seen = False         # another ship: whether it carries limpets is learned again
        elif event == "Undocked":
            self._seen_rocks.clear()           # a new run starts, as on the Space Mining page
            self._alerted.clear()
        elif event == "LaunchSRV":
            self._rhino = entry.get("SRVType") == RHINO_SRV
        elif event in ("DockSRV", "SRVDestroyed", "Died", "FSDJump", "CarrierJump"):
            self._rhino = False
        if event == "Cargo" and entry.get("Vessel") in ("Ship", "SRV"):
            self._rhino = entry.get("Vessel") == "SRV"
        if self.limpets:
            self._limpets_seen = True
        if event in MINING_EVENTS:
            self._last_mining = self._now()
        if event == "ProspectedAsteroid":
            wanted, threshold = self._target()
            finding = rock_finding(entry, wanted, threshold)
            self.last_rock = finding
            repeat = finding.key is not None and finding.key in self._seen_rocks
            fresh = rock_alerts(finding)
            if finding.key is not None:
                self._seen_rocks.add(finding.key)
                # a core and each target are alerted once per composition per run
                fresh = [alert for alert in fresh if (finding.key, alert.target or alert.kind) not in self._alerted]
                self._alerted.update((finding.key, alert.target or alert.kind) for alert in fresh)
            if repeat and not fresh:
                return                         # the same rock prospected again: no second alert, and the ones showing are left to run out
            self._rocks = [(alert, self._now() + ROCK_ALERT_S) for alert in fresh]

    def handle_status(self, entry: Mapping[str, Any]) -> None:
        """A `Status.json` update (EDMC's dashboard hook): the tons the ship holds, for the hold alert. Not taken while an SRV is out, and forgotten then."""
        known, tons = status_hold(entry, self._rhino)
        if known:
            self.live_cargo = tons

    def held(self) -> Optional[int]:
        """The tons the ship holds: `Status.json`'s figure when it has given one, else the latest `Cargo` event's."""
        return self.live_cargo if self.live_cargo is not None else self.cargo

    def _uses_limpets(self) -> bool:
        """Whether the low-limpet alert applies: not in a Rhino, and only when a prospector or collector controller is fitted or limpets have been seen aboard. A laser miner who
        carries no limpets, and a commander whose loadout has not been seen yet, are never told they are out. (Unverified: that a fitted controller always shows in the `Loadout`
        as a `Modules[].Item` starting `int_dronecontrol_prospector` or `int_dronecontrol_collection`; if not, the alert still starts once limpets have been seen aboard.)"""
        return not self._rhino and bool(self._controller or self._limpets_seen)

    def active(self) -> bool:
        return self._last_mining is not None and self._now() - self._last_mining <= ACTIVE_S

    def alerts(self, limpets_low: int = DEFAULT_LIMPETS_LOW, hold_percent: int = DEFAULT_HOLD_PERCENT) -> List[Alert]:
        found: List[Alert] = []
        found.extend(alert for alert, ends in self._rocks if self._now() < ends)
        if self.active():
            if self._uses_limpets() and self.limpets is not None and self.limpets <= limpets_low:
                found.append(Alert(KIND_LIMPETS, ("Low on limpets", f"{self.limpets} aboard")))
            held = self.held()
            if self.capacity and held is not None and held * 100 >= hold_percent * self.capacity:
                found.append(Alert(KIND_HOLD, ("Hold nearly full", f"{held} of {self.capacity} t")))
        return found


def fits_controller(loadout: Mapping[str, Any]) -> bool:
    """Whether a `Loadout` event lists a prospector or collector limpet controller."""
    modules = loadout.get("Modules")
    for module in modules if isinstance(modules, list) else []:
        item = str(module.get("Item") or "").casefold() if isinstance(module, Mapping) else ""
        if item.startswith(MINING_CONTROLLERS):
            return True
    return False


def status_hold(entry: Mapping[str, Any], srv_out: bool) -> Tuple[bool, Optional[int]]:
    """What a `Status.json` entry says about the ship's hold: (whether to take it, the tons). `Cargo` there is the tons carried, a figure checked only for the main ship, so it is
    taken only while the entry's flags say the commander is in it. While an SRV is out (the flag, or `srv_out` from the journal), or in any other vehicle or on foot, what `Cargo`
    counts is not known: the answer is (True, None), forget the live figure and let the `Cargo` events speak. An entry with no flags or no usable `Cargo` changes nothing:
    (False, None)."""
    flags = entry.get("Flags")
    if not isinstance(flags, int):
        return False, None
    if srv_out or flags & FLAGS_IN_SRV or not flags & FLAGS_IN_MAIN_SHIP:
        return True, None
    tons = _number(entry.get("Cargo"))
    if tons is None or tons < 0:
        return False, None
    return True, int(round(tons))


def rock_alerts(finding: RockFinding) -> List[Alert]:
    """The cards for a rock worth a look: a core asteroid, and one for each target it holds enough of (the richest MAX_TARGET_CARDS; none when the rock is mostly used up). Empty for an
    ordinary rock."""
    alerts: List[Alert] = []
    if finding.core:
        alerts.append(Alert(KIND_CORE, ("Core asteroid", finding.core), finding.key))
    if finding.remaining is None or finding.remaining >= MIN_REMAINING_PERCENT:
        for name, percent in (finding.hits or ((finding.target,) if finding.target else ()))[:MAX_TARGET_CARDS]:
            alerts.append(Alert(KIND_TARGET, (f"Rich rock: {name}", f"{percent:.0f}% of the rock"), finding.key, normalize(name)))
    return alerts


def rock_alert(finding: RockFinding) -> Optional[Alert]:
    """The first card `rock_alerts` gives for a rock, or None for an ordinary one."""
    alerts = rock_alerts(finding)
    return alerts[0] if alerts else None
