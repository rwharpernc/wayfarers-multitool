"""
Tracks every landable body the journal has told us about in the
commander's current system, for the Surface Mining page's "System
Bodies" overview - "which bodies here are even worth flying to", not
tied to any single deployment the way mining_surface.py's per-run state
is.

Two journal events feed this, both already flowing through
mining_panel.py's handle_event(): `Scan` (BodyName/PlanetClass/
Volcanism/Landable - only non-landable bodies are dropped, since this
view exists for Rhino/surface mining candidates specifically) and
`SAASignalsFound` (a "$PlanetaryMiningLocation_Name;" signal's Count -
"how many surface mining locations does DSS-mapping say this body has",
the strongest signal that's worth a look without having actually
visited). Signal counts are kept in their own dict rather than folded
into SurveyedBody directly, since a signal can be found (DSS mapping)
before or after the body's own Scan event arrives in the journal.

Pure logic, no tkinter - see tests/test_mining_body_survey.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SurveyedBody:
    name: str
    planet_class: Optional[str]
    volcanism: Optional[str]
    mining_signal_count: Optional[int] = None


class SystemBodySurvey:
    """Constructed empty - no persistence, unlike mining_hotspots.py's
    catalog: a system's landable-body list is exactly what the journal
    has told us about *this session's* current system, not something
    worth remembering once the commander leaves (EDMC replays only new
    journal lines on restart anyway, so yesterday's list would be
    incomplete and stale the moment it's shown)."""

    def __init__(self) -> None:
        self._current_system: Optional[str] = None
        self._bodies: dict[str, SurveyedBody] = {}
        self._signal_counts: dict[str, int] = {}
        self._detailed: set[str] = set()
        """Bodies whose count came from a detailed surface scan, the one the game stands behind."""

    @property
    def current_system(self) -> Optional[str]:
        return self._current_system

    def on_system_changed(self, system: Optional[str]) -> None:
        """Called on every system-carrying journal event (Location,
        FSDJump) - a no-op unless the system actually changed, so this
        can be called unconditionally without wiping the list on every
        Location line re-confirming the system the commander is
        already in."""
        if system and system != self._current_system:
            self._current_system = system
            self._bodies = {}
            self._signal_counts = {}
            self._detailed = set()

    def record_scan(self, system: Optional[str], body_name: Optional[str],
                    planet_class: Optional[str], volcanism: Optional[str], landable: bool) -> None:
        if system != self._current_system or not landable or not body_name:
            return
        key = body_name.strip().casefold()
        self._bodies[key] = SurveyedBody(
            name=body_name, planet_class=planet_class or None, volcanism=volcanism or None,
            mining_signal_count=self._signal_counts.get(key))

    def record_external(self, system: Optional[str], body_name: Optional[str],
                        planet_class: Optional[str], volcanism: Optional[str]) -> bool:
        """A landable body learned from outside the journal (an EDSM lookup): added only when the journal has not already told us about it, so what the game said
        about a body always wins. Returns whether it was added."""
        if system != self._current_system or not body_name:
            return False
        key = body_name.strip().casefold()
        if key in self._bodies:
            return False
        self._bodies[key] = SurveyedBody(
            name=body_name, planet_class=planet_class or None, volcanism=volcanism or None,
            mining_signal_count=self._signal_counts.get(key))
        return True

    def record_signal(self, system: Optional[str], body_name: Optional[str], count: int, detailed: bool = True) -> None:
        """A mining-location count from the journal. `detailed` is a detailed surface scan (`SAASignalsFound`), which always sets it; a count from the FSS (`FSSBodySignals`) sets it
        only while no detailed count is known, so a later FSS line never replaces the authoritative one."""
        if system != self._current_system or not body_name:
            return
        key = body_name.strip().casefold()
        if not detailed and key in self._detailed:
            return
        if detailed:
            self._detailed.add(key)
        self._signal_counts[key] = count
        if key in self._bodies:
            self._bodies[key].mining_signal_count = count

    def record_external_count(self, system: Optional[str], body_name: Optional[str], count: int) -> bool:
        """A mining-location count learned from outside the journal: kept only when the journal has given none for this body. Returns whether it was kept."""
        if system != self._current_system or not body_name:
            return False
        key = body_name.strip().casefold()
        if key in self._signal_counts:
            return False
        self._signal_counts[key] = count
        if key in self._bodies:
            self._bodies[key].mining_signal_count = count
        return True

    def landable_bodies(self) -> list[SurveyedBody]:
        """Every landable body scanned so far this system, most
        promising first: a higher known mining-location-signal count
        before an unknown one, then alphabetical so the rest of the
        list is stable and scannable rather than insertion-ordered."""
        def sort_key(body: SurveyedBody):
            has_signal = body.mining_signal_count is not None
            return (not has_signal, -(body.mining_signal_count or 0), body.name.casefold())
        return sorted(self._bodies.values(), key=sort_key)

    def grouped_by_class(self) -> dict[str, list[SurveyedBody]]:
        """landable_bodies(), grouped by PlanetClass ("Unknown" for a
        body whose Scan event didn't carry one - shouldn't happen in
        practice, but journals from odd edge cases have surprised this
        project before)."""
        groups: dict[str, list[SurveyedBody]] = {}
        for body in self.landable_bodies():
            groups.setdefault(body.planet_class or "Unknown", []).append(body)
        return groups


def seed_from_system_survey(target: SystemBodySurvey, shared: object) -> int:
    """Add to `target` the landable planets the shared System targets survey (`system_survey.survey`, restored from its saved copy and from the journals when EDMC starts or a system is
    entered again) knows for the same system, where the journal lines of this session have not given them. This is what keeps the Mining body list across an EDMC restart and brings back
    bodies scanned on an earlier visit. A body the journal gave stays as it is. Returns how many were added."""
    name = str(getattr(shared, "name", "") or "")
    if not name:
        return 0
    if target.current_system is None:
        target.on_system_changed(name)
    if (target.current_system or "").casefold() != name.casefold():
        return 0
    added = 0
    for body in list(getattr(shared, "bodies", {}).values()):
        if body.kind == "planet" and body.landable and body.planet_class and (body.scanned or body.known):
            if target.record_external(target.current_system, body.name, body.planet_class, body.volcanism or None):
                added += 1
    return added


system_body_survey = SystemBodySurvey()
