"""Clipboard copy formatting for the Powerplay Sessions window's "Copy
Progress" button.

Kept as pure functions (no Tk imports) so they're trivially testable. `progress_rows` is the data both Copy Progress and the Discord
copy and post (powerplay_discord.py) are built from.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple
from urllib.parse import quote

from .formulas import ACTIVITIES, ACTIVITY_LABELS, NO_CP_ACTIVITIES, merits_to_cp
from .session import system_merit_total, system_totals, visited_systems

DEFAULT_TEMPLATE = "[{system}]({system_url}) - {merits} merits (~{cp} CP) - {state}"

# Documented for the Settings tab's placeholder legend.
PLACEHOLDERS = ("{system}", "{system_url}", "{merits}", "{cp}", "{state}")


def inara_system_url(system: str) -> str:
    """Inara.cz system-search URL for `system` — clicking it lands on that
    system's page (Inara resolves the search itself; there's no public API
    for the numeric system ID Inara's own URLs otherwise use)."""
    return f"https://inara.cz/elite/starsystem/?search={quote(system)}"


@dataclass(frozen=True)
class ProgressRow:
    """One system's row of the session's progress: the merits earned there, the estimated Control Points (from the editable ratios) and the
    system's Powerplay state ("—" when it is not known, which is for every system but the one you are in)."""

    system: str
    merits: int
    cp: float
    state: str
    by_activity: Tuple[Tuple[str, int], ...] = ()      # (activity label, merits) for each activity that earned merits there, for the Discord post's breakdown


def progress_rows(session: Dict[str, Any], current_system: str, current_state: str, ratio_for: Callable[[str], float]) -> List[ProgressRow]:
    """A row for each system with merit activity this session, the system you are in first (even before it has earned anything), then the rest
    most recently active first. `current_state` is the state of the system you are in; `ratio_for(activity)` is the merits needed for one CP."""
    systems = visited_systems(session)
    if current_system and current_system not in systems:
        systems = [current_system] + systems
    elif current_system in systems:
        systems = [current_system] + [name for name in systems if name != current_system]
    rows = []
    for name in systems:
        cp = sum(merits_to_cp(system_totals(session, name).get(activity, 0), ratio_for(activity))
                 for activity in ACTIVITIES if activity not in NO_CP_ACTIVITIES)
        state = current_state if name == current_system and current_state else "—"
        totals = system_totals(session, name)
        breakdown = tuple((ACTIVITY_LABELS.get(activity, activity), totals[activity]) for activity in ACTIVITIES if totals.get(activity))
        rows.append(ProgressRow(name, system_merit_total(session, name), cp, state, breakdown))
    return rows


def format_system_line(
    template: str, *, system: str, merits: str, cp: str, state: str,
) -> str:
    """Substitutes the placeholders in `template` for one system's row.
    Falls back to the raw template on a malformed/unknown placeholder rather
    than raising into a Tk button callback."""
    try:
        return template.format(
            system=system, system_url=inara_system_url(system), merits=merits, cp=cp, state=state,
        )
    except (KeyError, IndexError, ValueError):
        return template
