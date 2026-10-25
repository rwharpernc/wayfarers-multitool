"""Catching Organic Scanning's saved progress up from recent journals, for the samples taken while EDMC was closed.

EDMC only passes a plugin the events that happen while it runs, so a species logged, sampled or analyzed with it closed never reaches the tracker: the survey
(which is rebuilt from the journals) knew the species was analyzed, while the Bio status card and the Dashboard still said 2/3. The journals have every `ScanOrganic`,
so this reads the recent ones and merges them into the saved per-body progress.

The same pass recovers what the prediction needs for a body scanned with EDMC closed: its conditions (from the `Scan`), the genera its signals name (from
`FSSBodySignals` or `SAASignalsFound`) and whether nobody had set foot there. Without them a body landed on afterwards showed no predicted species. These are only
added where nothing is saved for the body, never over what the live tracker saved.

A `ScanOrganic` names its body only by number (`Body`, the body ID), so the name is learned from the `Scan`, `FSSBodySignals`, `SAASignalsFound` and `ApproachBody`
events that name the same body in the same system. A sample whose body cannot be named is skipped.

The merge only ever raises a stage (Log 1, Sample 2, Analyse 3), the rule the live tracker uses too, so reading the same events again, or events the tracker already
saw, changes nothing. The game's journals are only ever read.
"""
from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple

from . import journal_files, organic_scan, organic_species_data

logger = logging.getLogger(__name__)

CATCH_UP_DAYS = 14
STAGES = {"Log": 1, "Sample": 2, "Analyse": 3}
_WANTED = journal_files.event_pattern("Commander", "LoadGame", "Location", "FSDJump", "CarrierJump", "ApproachBody", "Scan", "FSSBodySignals",
                                      "SAASignalsFound", "ScanOrganic")
_SYSTEM_EVENTS = frozenset({"Location", "FSDJump", "CarrierJump"})
_BODY_EVENTS = frozenset({"Scan", "FSSBodySignals", "SAASignalsFound", "ApproachBody"})

Sample = Dict[str, Any]   # system, body, genus, species, species_name, variant, scan_type, timestamp
BODY_FIELDS = ("conditions", "genus_hints", "first_footfall")


class CatchUp(NamedTuple):
    samples: List[Sample]
    bodies: Dict[str, Dict[str, Any]]      # body key -> what to add where nothing is saved: conditions, genus_hints, first_footfall


def read_since(cmdr: str, since_epoch: float, folder: Optional[str] = None) -> CatchUp:
    """The organic scans `cmdr` made in journals modified since `since_epoch`, oldest first, each with the system and the name of the body it was taken on, and the
    conditions, genus hints and footfall of the bodies scanned in them."""
    wanted = cmdr.strip().casefold()
    found: List[Sample] = []
    bodies: Dict[str, Dict[str, Any]] = {}
    if not wanted:
        return CatchUp(found, bodies)
    names: Dict[Tuple[Any, Any], Tuple[str, str]] = {}      # (system address, body ID) -> (system name, body name)
    for path in journal_files.files_modified_since(since_epoch, folder):
        current, system, address, star_type, star_pos = "", "", None, None, None
        for entry in journal_files.read_events(path, _WANTED):
            kind = entry.get("event")
            if kind == "Commander" and entry.get("Name"):
                current = str(entry["Name"]).strip().casefold()
            elif kind == "LoadGame" and entry.get("Commander"):
                current = str(entry["Commander"]).strip().casefold()
            elif current != wanted:
                continue
            elif kind in _SYSTEM_EVENTS and entry.get("StarSystem"):
                system, address = str(entry["StarSystem"]), entry.get("SystemAddress")
                star_type = None
                position = entry.get("StarPos")
                star_pos = tuple(position) if isinstance(position, list) and len(position) == 3 and all(isinstance(v, (int, float)) for v in position) else None
            elif kind in _BODY_EVENTS:
                body = entry.get("Body") if kind == "ApproachBody" else entry.get("BodyName")
                body_id, where = entry.get("BodyID"), entry.get("SystemAddress", address)
                if body and body_id is not None and where is not None:
                    names[(where, body_id)] = (str(entry.get("StarSystem") or system), str(body))
                if kind == "Scan" and entry.get("StarType"):
                    star_type = entry["StarType"]
                _collect_body(bodies, kind, entry, str(entry.get("StarSystem") or system), star_type, star_pos)
            elif kind == "ScanOrganic":
                named = names.get((entry.get("SystemAddress", address), entry.get("Body")))
                if named and entry.get("Genus") and entry.get("Species") and entry.get("ScanType") in STAGES:
                    found.append({
                        "system": named[0], "body": named[1], "genus": entry["Genus"], "species": entry["Species"],
                        "species_name": entry.get("Species_Localised") or entry["Species"], "variant": entry.get("Variant_Localised"),
                        "scan_type": entry["ScanType"], "timestamp": entry.get("timestamp"),
                    })
    return CatchUp(found, bodies)


def _collect_body(bodies: Dict[str, Dict[str, Any]], kind: str, entry: Dict[str, Any], system: str, star_type: Optional[str], star_pos: Optional[tuple]) -> None:
    """Note what one Scan, FSSBodySignals or SAASignalsFound tells about its body (the latest of each wins, as it does live)."""
    name = entry.get("BodyName")
    if not name or not system:
        return
    found: Dict[str, Any] = {}
    if kind == "Scan":
        cond = organic_scan.conditions_from_scan(entry, star_type, system, star_pos)
        if cond is not None:
            fields = asdict(cond)
            fields.pop("system_body_types", None)
            found["conditions"] = fields
            if isinstance(entry.get("WasFootfalled"), bool):
                found["first_footfall"] = not entry["WasFootfalled"]
    elif kind in ("FSSBodySignals", "SAASignalsFound") and isinstance(entry.get("Genuses"), list):
        genera = [g.get("Genus") for g in entry["Genuses"] if isinstance(g, dict) and g.get("Genus")]
        if genera:
            found["genus_hints"] = genera
    if found:
        bodies.setdefault(body_key(system, str(name)), {}).update(found)


def body_key(system: str, body: str) -> str:
    """The key the saved per-body state uses (organic_scan_panel.OrganicScanController._body_key)."""
    return f"{system}|{body}"


def merge_bodies(persisted: Dict[str, Dict[str, Any]], bodies: Dict[str, Dict[str, Any]]) -> Set[str]:
    """Add the conditions, genus hints and footfall of bodies scanned with EDMC closed where nothing is saved for them; returns the body keys that gained something.
    Nothing the live tracker saved is overwritten."""
    changed: Set[str] = set()
    for key, found in bodies.items():
        for field in BODY_FIELDS:
            if field in found and field not in persisted.get(key, {}):
                persisted.setdefault(key, {})[field] = found[field]
                changed.add(key)
    return changed


def merge(persisted: Dict[str, Dict[str, Any]], samples: List[Sample]) -> Set[str]:
    """Raise the saved progress in `persisted` to what `samples` show; returns the body keys that changed. Positions are not in the journal's ScanOrganic events
    (the live tracker takes them from Status.json), so a caught-up sample adds none."""
    changed: Set[str] = set()
    for sample in samples:
        stage = STAGES.get(sample["scan_type"], 0)
        key = body_key(sample["system"], sample["body"])
        stored = persisted.setdefault(key, {})
        organisms = stored.setdefault("organisms", {})
        saved = organisms.get(sample["genus"])
        if saved is not None and saved.get("stage", 0) >= stage:
            continue
        info = organic_species_data.SPECIES.get(f"{sample['genus']}|{sample['species']}")
        organisms[sample["genus"]] = {
            "species_key": sample["species"],
            "species_name": sample["species_name"],
            "value": info.value if info else None,
            "stage": stage,
            "last_lat": (saved or {}).get("last_lat"),
            "last_lon": (saved or {}).get("last_lon"),
            "variant_name": sample["variant"] or (saved or {}).get("variant_name"),
            "positions": list((saved or {}).get("positions") or []),
        }
        changed.add(key)
    return changed
