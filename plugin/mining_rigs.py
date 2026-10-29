"""The mining rigs you have placed on the body you are on, for the radar's spacing bands.

The journal does not say where a rig was put down, so this holds only what the commander tells WFMT: the **Rig placed** action (a button in the Surface Live window, a keyboard shortcut or the
`!wf rig` chat command) notes the Rhino's position as a rig. With the **rig gap** from Settings → Mining (how close the game lets two rigs be; it does not publish the figure, so the
commander measures it with Mark center and Mark border), the radar draws a band of that radius round each rig, filled while the Rhino is inside one and an outline once it is clear, so the next rig goes
down outside every band. Nothing is saved: the rigs belong to this deployment and are forgotten when the Rhino is launched or stowed, destroyed, or the body changes. Pure: no Tk, no EDMC.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from . import mining_bearing as bearing

SAME_SPOT_M = 5.0
"""Pressing the action twice at one spot is the same rig: a second press within this distance of a placed rig adds nothing."""
MAX_RIGS = 40


@dataclass(frozen=True)
class Placed:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Spacing:
    count: int
    nearest_m: float
    inside: bool
    """The Rhino is closer to the nearest rig than the rig gap (always False without a gap)."""


class RigBook:
    def __init__(self) -> None:
        self._where: Optional[tuple[str, str]] = None
        self._rigs: List[Placed] = []

    @staticmethod
    def _key(system: Optional[str], body: Optional[str]) -> tuple[str, str]:
        return str(system or "").strip().casefold(), str(body or "").strip().casefold()

    def add(self, system: Optional[str], body: Optional[str], latitude: float, longitude: float, radius_m: Optional[float]) -> str:
        """Note a rig at this position and say what was done. A rig on another body than the last starts a new set."""
        if not system or not body or not radius_m:
            return "WFMT does not know the body yet: land first."
        key = self._key(system, body)
        if key != self._where:
            self._where, self._rigs = key, []
        for rig in self._rigs:
            if bearing.distance_m(rig.latitude, rig.longitude, latitude, longitude, radius_m) < SAME_SPOT_M:
                return f"Rig already noted here ({len(self._rigs)} placed)."
        if len(self._rigs) >= MAX_RIGS:
            return f"{MAX_RIGS} rigs are noted already: clear them first."
        self._rigs.append(Placed(latitude, longitude))
        return f"Rig {len(self._rigs)} noted here."

    def rigs_for(self, system: Optional[str], body: Optional[str]) -> List[Placed]:
        """The rigs noted on this body, in the order they were placed; none for any other body."""
        return list(self._rigs) if self._where == self._key(system, body) and self._where != ("", "") else []

    def clear(self) -> int:
        """Forget every rig; returns how many there were."""
        count = len(self._rigs)
        self._where, self._rigs = None, []
        return count

    def spacing(self, system: Optional[str], body: Optional[str], latitude: float, longitude: float, radius_m: Optional[float], gap_m: float = 0.0) -> Optional[Spacing]:
        """How the Rhino stands against the rigs noted on this body, or None when there are none or the body's size is not known."""
        rigs = self.rigs_for(system, body)
        if not rigs or not radius_m:
            return None
        nearest = min(bearing.distance_m(rig.latitude, rig.longitude, latitude, longitude, radius_m) for rig in rigs)
        return Spacing(len(rigs), nearest, bool(gap_m) and nearest < gap_m)


rig_book = RigBook()
