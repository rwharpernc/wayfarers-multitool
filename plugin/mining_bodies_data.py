"""What the journals say about the bodies the Rhino mines on, for the Surface Mining Book's "From your journals" list: every body whose DSS scan found planetary mining locations (how many), the
planet class from its `Scan`, and the tons refined on it while a Rhino was deployed (when, and how many). Pure Python: no Tk, no network, no EDMC.

The journal does not say where a deposit is, so none of this can be placed on a body: the Surface Mining Book's hotspots stay what the commander saves, and this list says only *which bodies* were
worth landing on and how much was refined on each. Read from the journals by `mining_history.py` in the same background pass as the mining runs and the rings.

- `SAASignalsFound` with a `$PlanetaryMiningLocation_Name;` signal: the body and its count of mining locations.
- `Scan` with `Landable` and `PlanetClass`: the class, kept for the bodies that have a record.
- `MiningRefined` while a Rhino is deployed (`LaunchSRV` with `SRVType` `mev_rhino`, or a `Cargo` event for an SRV's hold when the launch is in an earlier journal, until `DockSRV`, `SRVDestroyed` or `Died`) on the body the commander last approached (`ApproachBody`, or `Location` on
  a planet): one ton each.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping

MINING_LOCATION_SIGNAL = "$PlanetaryMiningLocation_Name;"
RHINO = "mev_rhino"


def body_key(body: str) -> str:
    return " ".join(str(body or "").split()).casefold()


def new_body(body: str, system: str = "") -> Dict[str, Any]:
    return {"body": " ".join(str(body or "").split()), "system": " ".join(str(system or "").split()), "locations": 0, "class": "", "scanned": "", "tons": 0, "last": ""}


def merge(into: Dict[str, Dict[str, Any]], record: Mapping[str, Any]) -> Dict[str, Any]:
    """Put `record` into `into` (by body name) and return the merged record. Tons add up (each journal is read once); the mining location count of the more recent scan wins; a class already known is kept."""
    key = body_key(str(record.get("body") or ""))
    have = into.get(key)
    if have is None:
        have = into[key] = {**new_body(str(record.get("body") or "")), **{k: v for k, v in record.items()}}
        return have
    have["tons"] = int(have.get("tons") or 0) + int(record.get("tons") or 0)
    if int(record.get("locations") or 0) > 0 and str(record.get("scanned") or "") >= str(have.get("scanned") or ""):
        have["locations"], have["scanned"] = int(record["locations"]), str(record.get("scanned") or "")
    if record.get("class") and not have.get("class"):
        have["class"] = record["class"]
    if record.get("system") and not have.get("system"):
        have["system"] = record["system"]
    have["last"] = max(str(have.get("last") or ""), str(record.get("last") or ""))
    return have


def bodies_from(entries: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """What one journal's events say about the bodies mined on (see the module docstring)."""
    found: Dict[str, Dict[str, Any]] = {}
    classes: Dict[str, str] = {}
    system, body, rhino = "", "", False
    for entry in entries:
        event, stamp = entry.get("event"), str(entry.get("timestamp") or "")
        if event in ("FSDJump", "CarrierJump"):
            system, body, rhino = str(entry.get("StarSystem") or system), "", False
        elif event == "Location":
            system = str(entry.get("StarSystem") or system)
            body = str(entry.get("Body") or "") if entry.get("BodyType") == "Planet" else ""
        elif event == "ApproachBody":
            system, body = str(entry.get("StarSystem") or system), str(entry.get("Body") or "")
        elif event in ("LeaveBody", "SupercruiseEntry"):
            body = ""
        elif event == "LaunchSRV":
            rhino = entry.get("SRVType") == RHINO
        elif event in ("DockSRV", "SRVDestroyed", "Died"):
            rhino = False
        elif event == "Cargo":                       # the hold of an SRV that is out: covers a Rhino launched before this journal began (only the Rhino refines ore)
            rhino = True if entry.get("Vessel") == "SRV" else (False if entry.get("Vessel") == "Ship" else rhino)
        elif event == "SAASignalsFound":
            name = str(entry.get("BodyName") or "")
            if not name or name.casefold().endswith(" ring"):
                continue
            for signal in entry.get("Signals") if isinstance(entry.get("Signals"), list) else []:
                count = signal.get("Count") if isinstance(signal, Mapping) else None
                if isinstance(signal, Mapping) and signal.get("Type") == MINING_LOCATION_SIGNAL and isinstance(count, (int, float)) and not isinstance(count, bool) and count > 0:
                    record = merge(found, new_body(name, system))
                    record["locations"], record["scanned"] = int(count), stamp
        elif event == "Scan":
            if entry.get("Landable") and entry.get("PlanetClass") and entry.get("BodyName"):
                classes[body_key(str(entry["BodyName"]))] = str(entry["PlanetClass"])
        elif event == "MiningRefined" and rhino and body:
            record = merge(found, new_body(body, system))
            record["tons"] = int(record.get("tons") or 0) + 1
            record["last"] = stamp
    for key, record in found.items():
        if classes.get(key):
            record["class"] = classes[key]
    return found
