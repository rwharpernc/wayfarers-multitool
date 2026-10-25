"""The Carrier Route planner's plotted route, kept in `carrier_route.json` beside the plugin so it survives a restart of EDMC.

One route per commander (`commander_data.py`): two commanders on one install never see each other's. The route is saved when it is plotted, when the carrier reaches a system on it and when it
is cleared, and put back when the window next opens for the commander. Nothing is sent anywhere. A file that cannot be read, or a route in it that makes no sense, is ignored: the worst result
is that the route is not restored.
"""
from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List, Optional

from . import commander_data
from .carrier_route import CarrierLeg, CarrierRoute, FLEET, KIND_LABELS

STATE_FILENAME = "carrier_route.json"
MAX_LEGS = 500                      # a carrier route is about 50 jumps for the whole galaxy; a longer one is not saved


def _is_legacy(_raw: Any) -> bool:
    return False                    # the file is new; nothing older to claim


def to_payload(route: Optional[CarrierRoute]) -> Dict[str, Any]:
    """The route as plain data for the file ({"route": None} when there is none)."""
    if route is None or not route.legs or len(route.legs) > MAX_LEGS:
        return {"route": None}
    legs: List[Dict[str, Any]] = []
    for leg in route.legs:
        raw = dataclasses.asdict(leg)
        if raw.get("xyz") is not None:
            raw["xyz"] = list(raw["xyz"])
        legs.append(raw)
    return {"route": {"kind": route.kind, "start": route.start, "end": route.end, "reached": route.reached, "needs": route.needs, "legs": legs}}


def _number(value: Any) -> Optional[float]:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _int(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _leg(raw: Any) -> Optional[CarrierLeg]:
    if not isinstance(raw, dict) or not isinstance(raw.get("system"), str) or not raw["system"].strip():
        return None
    xyz = raw.get("xyz")
    point = tuple(float(v) for v in xyz) if isinstance(xyz, (list, tuple)) and len(xyz) == 3 and all(_number(v) is not None for v in xyz) else None
    return CarrierLeg(_int(raw.get("number")) or 0, raw["system"], _number(raw.get("distance")) or 0.0, _number(raw.get("left")) or 0.0, _number(raw.get("tritium_left")),
                      _number(raw.get("tritium_used")), _int(raw.get("restock")) or 0, bool(raw.get("icy_ring")), bool(raw.get("pristine")), bool(raw.get("stop")), point,
                      _int(raw.get("id64")), _number(raw.get("market")))


def from_payload(payload: Any) -> Optional[CarrierRoute]:
    """The route in a saved payload, or None when there is none or it cannot be understood."""
    raw = payload.get("route") if isinstance(payload, dict) else None
    if not isinstance(raw, dict) or not isinstance(raw.get("legs"), list) or not 0 < len(raw["legs"]) <= MAX_LEGS:
        return None
    legs = [leg for leg in (_leg(item) for item in raw["legs"]) if leg is not None]
    if len(legs) != len(raw["legs"]):
        return None                  # a damaged route is dropped rather than half shown
    reached = _int(raw.get("reached"))
    kind = raw.get("kind")
    return CarrierRoute(kind if kind in KIND_LABELS else FLEET, str(raw.get("start") or ""), str(raw.get("end") or legs[-1].system), legs,
                        max(0, min(len(legs), reached)) if reached is not None else 0, str(raw.get("needs") or ""))


class RouteStore:
    """The file: load it once at start-up, then `get` a commander's route and `put` it whenever it changes."""

    def __init__(self) -> None:
        self._store = commander_data.new_store()
        self._plugin_dir: Optional[str] = None

    def load(self, plugin_dir: str) -> None:
        self._plugin_dir = plugin_dir
        self._store = commander_data.read(os.path.join(plugin_dir, STATE_FILENAME), _is_legacy)

    def get(self, cmdr: str) -> Optional[CarrierRoute]:
        if not commander_data.key_for(cmdr):
            return None
        return from_payload(commander_data.payload_for(self._store, cmdr, lambda: {"route": None}))

    def put(self, cmdr: str, route: Optional[CarrierRoute]) -> None:
        if not commander_data.key_for(cmdr) or self._plugin_dir is None:
            return
        commander_data.put(self._store, cmdr, to_payload(route))
        commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)
