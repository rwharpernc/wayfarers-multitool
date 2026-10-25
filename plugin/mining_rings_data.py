"""The Space Mining Book's data: the rings your journals have shown, joined with the mining you did at them and the notes you wrote, as rows for the window. Pure Python: no Tk, no network, no EDMC.

A ring record (`new_ring`) is what the journal says about one ring, by the ring's name (which includes its system's name, so it is unique):

- `hotspots`: each mineral a DSS scan found with its hotspot **count** (`SAASignalsFound` on a ring body). The journal gives the count, not where the hotspots are or whether two minerals share a spot,
  so overlaps cannot be shown.
- `class`: the ring class (Icy, Rocky, Metallic, Metal rich) and `reserve`: the reserve level (Pristine, Major, Common, Low, Depleted), from the parent body's `Scan` (`Rings`, `ReserveLevel`).
- `system`, `seen` (when a scan last showed it) and `scanned` (when its hotspots were found).

Tons mined and when come from the mining runs (`mining_history.py`: each run records its ring and what it refined). The commander's notes, favorites and rings added by hand are in `mining_rings.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .mining_names import normalize

CLASS_NAMES = {"icy": "Icy", "rocky": "Rocky", "metalic": "Metallic", "metallic": "Metallic", "metalrich": "Metal rich"}
RESERVE_NAMES = {"pristine": "Pristine", "major": "Major", "common": "Common", "low": "Low", "depleted": "Depleted"}


def is_ring(body: str) -> bool:
    """Whether a body name is a ring ("Col 285 Sector GG-X d1-123 10 A Ring")."""
    return str(body or "").strip().casefold().endswith(" ring")


def ring_key(ring: str) -> str:
    return " ".join(str(ring or "").split()).casefold()


def new_ring(ring: str, system: str = "") -> Dict[str, Any]:
    return {"ring": " ".join(str(ring or "").split()), "system": " ".join(str(system or "").split()), "hotspots": {}, "class": "", "reserve": "", "seen": "", "scanned": ""}


def hotspots_from(signals: Any) -> Dict[str, int]:
    """A ring's `Signals` as {mineral: hotspot count}; the journal's own signal types (names that start with $) are left out."""
    found: Dict[str, int] = {}
    for signal in signals if isinstance(signals, list) else []:
        if not isinstance(signal, Mapping):
            continue
        name = str(signal.get("Type_Localised") or signal.get("Type") or "").strip()
        count = signal.get("Count")
        if name and not name.startswith("$") and isinstance(count, (int, float)) and not isinstance(count, bool) and count > 0:
            name = normalize(name)
            found[name] = max(found.get(name, 0), int(count))
    return found


def merge(into: Dict[str, Dict[str, Any]], record: Mapping[str, Any]) -> Dict[str, Any]:
    """Put `record` into `into` (by ring name) and return the merged record. The hotspots of the more recent DSS scan win; a class or reserve level already known is kept when the new
    record has none; the system is filled in when it was missing."""
    key = ring_key(str(record.get("ring") or ""))
    have = into.get(key)
    if have is None:
        have = into[key] = {**new_ring(str(record.get("ring") or "")), **{k: v for k, v in record.items() if k != "hotspots"}, "hotspots": dict(record.get("hotspots") or {})}
        return have
    if record.get("hotspots") and str(record.get("scanned") or "") >= str(have.get("scanned") or ""):
        have["hotspots"], have["scanned"] = dict(record["hotspots"]), str(record.get("scanned") or "")
    for name in ("class", "reserve"):
        if record.get(name) and (not have.get(name) or str(record.get("seen") or "") >= str(have.get("seen") or "")):
            have[name] = record[name]
    if record.get("system") and not have.get("system"):
        have["system"] = record["system"]
    have["seen"] = max(str(have.get("seen") or ""), str(record.get("seen") or ""))
    return have


def class_text(raw: Any) -> str:
    """"eRingClass_MetalRich" -> "Metal rich"; empty when unknown."""
    text = str(raw or "").rsplit("_", 1)[-1].strip().casefold().replace(" ", "")
    return CLASS_NAMES.get(text, str(raw or "").rsplit("_", 1)[-1].strip())


def reserve_text(raw: Any) -> str:
    """"PristineResources" -> "Pristine"; empty when unknown."""
    text = str(raw or "").strip()
    if text.casefold().endswith("resources"):
        text = text[:-len("resources")]
    return RESERVE_NAMES.get(text.casefold(), text)


def hotspot_text(hotspots: Mapping[str, int], limit: int = 6) -> str:
    """"Painite 3, Platinum 2": most hotspots first, then by name; a few and a count of the rest."""
    ordered = sorted(hotspots.items(), key=lambda item: (-item[1], item[0].casefold()))
    text = ", ".join(f"{name} {count}" for name, count in ordered[:limit])
    return text + (f" +{len(ordered) - limit} more" if len(ordered) > limit else "")


def mined_by_ring(runs: Iterable[Mapping[str, Any]]) -> Dict[str, Tuple[int, str, int]]:
    """From the mining runs: by ring, (tons refined, when it was last mined, how many runs). A run with no ring recorded is not counted."""
    found: Dict[str, List[Any]] = {}
    for run in runs:
        ring = str(run.get("ring") or "")
        if not ring:
            continue
        entry = found.setdefault(ring_key(ring), [0, "", 0])
        entry[0] += sum(int(v) for v in (run.get("refined") or {}).values() if isinstance(v, (int, float)))
        entry[1] = max(entry[1], str(run.get("start") or ""))
        entry[2] += 1
    return {key: (tons, last, count) for key, (tons, last, count) in found.items()}


@dataclass(frozen=True)
class RingRow:
    key: str
    ring: str
    system: str
    hotspots: Dict[str, int] = field(default_factory=dict)
    ring_class: str = ""
    reserve: str = ""
    tons: int = 0
    last_mined: str = ""
    runs: int = 0
    favorite: bool = False
    note: str = ""
    manual: bool = False

    @property
    def hotspot_total(self) -> int:
        return sum(self.hotspots.values())


def _hotspots_normalized(hotspots: Any) -> Dict[str, int]:
    """Saved hotspots with the mineral names in one spelling (rings read before names were normalized hold `tritium` and `Tritium`); the larger count wins when two spellings meet."""
    found: Dict[str, int] = {}
    for name, count in (hotspots or {}).items():
        name = normalize(name) or str(name)
        found[name] = max(found.get(name, 0), int(count))
    return found


def build_rows(rings: Mapping[str, Mapping[str, Any]], runs: Iterable[Mapping[str, Any]], user: Mapping[str, Mapping[str, Any]]) -> List[RingRow]:
    """One row per ring worth a place in a mining book: from the journals (`rings`), plus rings added by hand and any ring you mined at that no scan showed (`user` holds notes, favorites and the
    by-hand rings, by ring key). A ring the journals only show as part of a scanned planet (a class and a reserve level, no hotspots, no mining) is left out: there are thousands of those, and
    one with a note, a favorite star or a by-hand entry stays. Favorites first, then the most tons mined, then the most recently seen."""
    mined = mined_by_ring(runs)
    keys: Dict[str, Dict[str, Any]] = {key: dict(record) for key, record in rings.items()}
    for key, extra in user.items():
        manual = extra.get("manual")
        if isinstance(manual, Mapping) and key not in keys:
            keys[key] = {**new_ring(str(manual.get("ring") or "")), **dict(manual), "hotspots": dict(manual.get("hotspots") or {})}
    for run in runs:
        ring = str(run.get("ring") or "")
        if ring and ring_key(ring) not in keys:
            keys[ring_key(ring)] = new_ring(ring, str(run.get("system") or ""))
    rows: List[RingRow] = []
    for key, record in keys.items():
        extra = user.get(key) or {}
        tons, last, count = mined.get(key, (0, "", 0))
        manual = extra.get("manual") if isinstance(extra.get("manual"), Mapping) else None
        if not (record.get("hotspots") or count or manual is not None or extra.get("favorite") or extra.get("note")):
            continue
        rows.append(RingRow(key, str(record.get("ring") or key), str(record.get("system") or ""), _hotspots_normalized(record.get("hotspots")), class_text(record.get("class")),
                            reserve_text(record.get("reserve")), tons, last, count, bool(extra.get("favorite")), str(extra.get("note") or ""),
                            manual is not None and key not in rings))
    rows.sort(key=lambda r: (not r.favorite, -r.tons, -r.hotspot_total, r.ring.casefold()))
    return rows


def filter_rows(rows: Sequence[RingRow], text: str = "", favorites_only: bool = False) -> List[RingRow]:
    """The rows whose ring, system, a mineral or a note contains `text` (any case); only favorites when asked."""
    wanted = " ".join(str(text or "").split()).casefold()
    out = []
    for row in rows:
        if favorites_only and not row.favorite:
            continue
        if wanted and not any(wanted in part.casefold() for part in (row.ring, row.system, row.note, " ".join(row.hotspots))):
            continue
        out.append(row)
    return out


def parse_hotspots(text: str) -> Optional[Dict[str, int]]:
    """"Painite 3, Platinum 2" (or a name alone, meaning 1) as {mineral: count}; None when it cannot be read."""
    found: Dict[str, int] = {}
    for part in str(text or "").replace(";", ",").split(","):
        words = part.split()
        if not words:
            continue
        count = 1
        if words[-1].isdigit():
            count, words = int(words[-1]), words[:-1]
        if not words or count <= 0:
            return None
        found[" ".join(words)] = count
    return found
