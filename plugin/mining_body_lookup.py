"""Get body info: the landable bodies of a system, from EDSM and Spansh, for bodies the journal never gave a Scan for.

The Surface Mining Book builds its body list from the journal's `Scan` events, and a body scanned in a session whose journal is gone has none. Two services keep what players uploaded:
- **EDSM** gives each scanned body's name, kind (`subType`), volcanism and radius (in kilometers).
- **Spansh** gives the same fields and, on top, how many Planetary Mining Locations a body carries (its `signals`), which the journal only gives after a scan of that body.

`parse_edsm` and `parse_spansh` turn each answer into the landable planets, `merge` puts the two together, `apply` adds them to the Mining body list and the known body sizes without overwriting
anything the journal said, and the Book's **Get body info** button (opt-in) does the asking. The Spansh request goes through the courtesy layer (`spansh_courtesy`) and needs the system's
game id, which `mining_location` keeps from the latest jump or login; without it only EDSM is asked. Neither service says where a mining location is. No tkinter; see tests/test_mining_body_lookup.py.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from config import appname, config

from . import http_identity
from . import mining_body_survey
from . import mining_surface
from . import spansh_courtesy

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_ENABLED = "wfmt_mining_edsm_body_lookup_enabled"
"""Settings > Mining: allow the Book to ask EDSM and Spansh for a system's bodies. The name is from when only EDSM was asked; it is kept so a tick made then still counts."""

SPANSH_DUMP_URL = "https://spansh.co.uk/api/dump/"
SPANSH_TIMEOUT_S = 20
_USER_AGENT = http_identity.user_agent("mining-bodies")


def enabled() -> bool:
    return bool(config.get_bool(CONFIG_ENABLED, False))


@dataclass(frozen=True)
class OutsideBody:
    name: str
    planet_class: str
    """The service's `subType` (`Icy body`, `Rocky body`, `High metal content world`...): `mining_ground.classify` reads it by its first words, as it does the journal's `PlanetClass`."""
    volcanism: Optional[str]
    radius_m: Optional[float]
    mining_locations: Optional[int] = None
    """How many Planetary Mining Locations the body carries, when the service says (Spansh does, EDSM does not)."""


@dataclass(frozen=True)
class Applied:
    landable: int
    """How many landable bodies the services listed."""
    bodies_added: int
    """How many of them the Mining body list did not have and now does."""
    sizes_added: int
    """How many body sizes were not known and now are."""
    counts_added: int = 0
    """How many mining-location counts the journals had not given and now are known."""


def _volcanism(raw: Any) -> Optional[str]:
    text = str(raw or "").strip()
    return None if not text or text.casefold().startswith("no volcanism") else text


def _radius_m(raw: Any) -> Optional[float]:
    try:
        km = float(raw)
    except (TypeError, ValueError):
        return None
    return km * 1000.0 if km > 0 else None


def _count(raw: Any) -> Optional[int]:
    if isinstance(raw, bool) or not isinstance(raw, (int, float)) or raw < 0:
        return None
    return int(raw)


def _landable(raw: Sequence[Any], with_counts: bool) -> list[OutsideBody]:
    found: list[OutsideBody] = []
    for body in raw or ():
        if not isinstance(body, dict) or body.get("type") != "Planet" or body.get("isLandable") is not True:
            continue
        name, kind = body.get("name"), body.get("subType")
        if not isinstance(name, str) or not name.strip() or not isinstance(kind, str) or not kind.strip():
            continue
        count = None
        if with_counts:
            signals = body.get("signals")
            inner = signals.get("signals") if isinstance(signals, dict) else None
            count = _count(inner.get(mining_surface.MINING_LOCATION_SIGNAL_TYPE)) if isinstance(inner, dict) else None
        found.append(OutsideBody(name.strip(), kind.strip(), _volcanism(body.get("volcanismType")), _radius_m(body.get("radius")), count))
    return found


def parse_edsm(raw_bodies: Optional[Sequence[Any]]) -> list[OutsideBody]:
    """The landable planets in EDSM's `bodies` list, in its order. Stars, gas giants, anything not landable and anything without a name or a kind are left out."""
    return _landable(raw_bodies or (), with_counts=False)


def parse_spansh(system: Optional[dict]) -> list[OutsideBody]:
    """The landable planets in a Spansh system dump (`{"system": {...}}` or the system itself), with their mining-location counts."""
    if not isinstance(system, dict):
        return []
    inner = system.get("system") if isinstance(system.get("system"), dict) else system
    bodies = inner.get("bodies")
    return _landable(bodies if isinstance(bodies, list) else (), with_counts=True)


def merge(first: Sequence[OutsideBody], second: Sequence[OutsideBody]) -> list[OutsideBody]:
    """`first`'s bodies in its order, then the ones only `second` has. A body in both keeps `first`'s kind, volcanism and size, and takes a count from `second` when `first` has none."""
    result: list[OutsideBody] = []
    index: dict[str, int] = {}
    for body in list(first) + list(second):
        key = body.name.casefold()
        if key not in index:
            index[key] = len(result)
            result.append(body)
            continue
        kept = result[index[key]]
        if kept.mining_locations is None and body.mining_locations is not None:
            result[index[key]] = OutsideBody(kept.name, kept.planet_class, kept.volcanism, kept.radius_m, body.mining_locations)
    return result


def fetch_spansh(address: Optional[int]) -> Optional[dict]:
    """Spansh's dump of a system by its game id, or None when there is no id, Spansh does not know the system or it did not answer. Never raises."""
    if not address:
        return None
    request = urllib.request.Request(f"{SPANSH_DUMP_URL}{int(address)}", headers={"User-Agent": _USER_AGENT})
    try:
        data = json.loads(spansh_courtesy.call(request, SPANSH_TIMEOUT_S).decode("utf-8"))
    except Exception:
        logger.warning("Spansh body lookup failed for system address %s", address, exc_info=True)
        return None
    return data if isinstance(data, dict) else None


def apply(system: str, bodies: Sequence[OutsideBody], survey, surface) -> Applied:
    """Add `bodies` of `system` to the Mining body list (`survey`, a `SystemBodySurvey`) and their sizes to `surface` (a `SurfaceMiningRepository`). A body, size or count the journal already
    gave is left as it is. The survey keeps only its current system, so when it does not know one yet it is told this one; when it is on another system the sizes are still recorded."""
    if survey.current_system is None:
        survey.on_system_changed(system)
    added_bodies = added_sizes = added_counts = 0
    for body in bodies:
        if survey.record_external(system, body.name, body.planet_class, body.volcanism):
            added_bodies += 1
        if body.radius_m is not None and surface.known_radius(body.name) is None:
            surface.record_body_radius(body.name, body.radius_m)
            added_sizes += 1
        if body.mining_locations is not None and survey.record_external_count(system, body.name, body.mining_locations):
            added_counts += 1
    return Applied(len(bodies), added_bodies, added_sizes, added_counts)


def seed(system: Optional[str], survey, surface, shared: object = None, cache: object = None) -> int:
    """Bring back what is already known about `system` without asking anyone: the landable planets of the shared System targets survey (`shared`; saved between sessions and rebuilt from
    the journals) and the bodies a lookup remembered (`cache`, a `mining_body_cache.BodyCache`). The journal lines of this session win over both. Returns how many bodies were added."""
    added = mining_body_survey.seed_from_system_survey(survey, shared) if shared is not None else 0
    remembered = cache.bodies_for(system) if cache is not None and system else []
    if remembered:
        added += apply(system, remembered, survey, surface).bodies_added
    return added


def message(system: str, applied: Applied, asked_spansh: bool = False, address_known: bool = True) -> str:
    """What the Book's status line says after a lookup."""
    if applied.landable == 0:
        text = f"No landable bodies found for {system}. EDSM and Spansh only know systems that players' tools have uploaded."
        return text if address_known or asked_spansh else text + " Spansh needs the system's id from a jump or a login."
    noun = "body" if applied.landable == 1 else "bodies"
    if not (applied.bodies_added or applied.sizes_added or applied.counts_added):
        return f"{applied.landable} landable {noun} listed for {system}; your journals already gave WFMT all of it."
    parts = [f"added {applied.bodies_added} to the list", f"{applied.sizes_added} size{'s' if applied.sizes_added != 1 else ''}"]
    if applied.counts_added:
        parts.append(f"{applied.counts_added} mining-location count{'s' if applied.counts_added != 1 else ''}")
    text = f"{applied.landable} landable {noun} listed for {system}: " + ", ".join(parts[:-1]) + (f" and {parts[-1]}" if len(parts) > 1 else parts[0]) + ". Journal data was left as it was."
    if not address_known:
        text += " Spansh was not asked: it needs the system's id from a jump or a login, so mining-location counts are missing."
    return text
