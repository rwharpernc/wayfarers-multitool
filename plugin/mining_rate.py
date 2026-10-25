"""
How fast a run is refining, told two ways that the Space page, the Surface page, the HUD and the live window all word the same:

- the rate now: tons refined in the last RATE_WINDOW_SECONDS, scaled to tons per hour. One `MiningRefined` event is one ton (the Cargo count of the hold goes up by one for each,
  checked against a real journal), so a count of events is a count of tons.
- the run average: tons refined this run over the mining time, which runs from the first to the last mining event of the run (a prospected rock, a ton refined, a limpet launched, a
  rock cracked: the events `mining_history` calls mining events) with every gap of more than MAX_GAP_SECONDS between two of them left out. Mining History reads a run's mining time the
  same way, so the live figure and the history's t/h agree for the same run (see `mining_history.runs_from`).

The refinement timestamps are pruned in place to the rate window, so the average is never derived from them: a `MiningClock` keeps the first and last event times and the time
mined, and is what the average reads.

How long until the hold is full (`minutes_to_fill`, `full_in_text`) is the room left in the hold over the run average, which is steadier than the rate now (a laser works in bursts,
with prospecting between), and over the rate now only in the first minute of a run, before there is an average.

The rate is recomputed on every MiningRefined and by the periodic UI timer (mining_render.py's re-render tick), which re-reads current_rate() against the same list: that is what
makes the displayed rate decay toward zero during a lull instead of freezing at its last value.
"""
import calendar
import time
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

RATE_WINDOW_SECONDS = 60.0
"""How far back a refinement still counts toward the rate now: a minute smooths the one-ton steps of a busy laser and still lets the rate fall to zero within a minute of a lull."""

MIN_RATE_SPAN_SECONDS = 10.0
"""A run younger than the window divides by its own age, but never by less than this, so the first tons of a run do not read as an absurd rate."""

MAX_GAP_SECONDS = 600.0
"""Ten minutes without a mining event is not mining time: it is left out of the mining time (a long flight between rings, or a break)."""

MIN_AVERAGE_SECONDS = 60.0
"""The run average is not shown until the run has this much mining time: a few tons in a few seconds say nothing about a run."""


def event_time(entry: Mapping[str, Any], fallback: Optional[float] = None) -> float:
    """When a journal event happened, as seconds since the epoch, from its UTC `timestamp`; `fallback` (else now) when it has none or cannot be read. Using the event's own time
    keeps a journal replayed at start-up from counting a whole run as if it had all happened this second."""
    stamp = entry.get("timestamp")
    if isinstance(stamp, str):
        try:
            return float(calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")))
        except ValueError:
            pass
    return time.time() if fallback is None else fallback


def record_tick(timestamps: List[float], at: Optional[float] = None) -> None:
    """Call once per ton refined, appending when it was refined (now unless `at` is given)."""
    timestamps.append(time.time() if at is None else at)


def current_rate(timestamps: List[float], now: Optional[float] = None) -> float:
    """Prunes entries older than RATE_WINDOW_SECONDS from `timestamps` in place, then returns tons per hour for what is left (0.0 once the window empties out). A run younger than the
    window is divided by its age (at least MIN_RATE_SPAN_SECONDS), not by a full window it has not lived yet."""
    now = time.time() if now is None else now
    cutoff = now - RATE_WINDOW_SECONDS
    while timestamps and timestamps[0] < cutoff:
        timestamps.pop(0)
    if not timestamps:
        return 0.0
    span = min(RATE_WINDOW_SECONDS, max(MIN_RATE_SPAN_SECONDS, now - timestamps[0]))
    return len(timestamps) * 3600.0 / span


@dataclass
class MiningClock:
    """The first and last mining event of a run and the time mined between them with the long gaps left out. Kept apart from the refined timestamps, which are pruned."""
    first: Optional[float] = None
    last: Optional[float] = None
    mined_seconds: float = 0.0

    def note(self, at: float) -> None:
        """A mining event happened at `at`. An event stamped before the last one adds nothing."""
        if self.first is None or self.last is None:
            self.first = self.last = at
            return
        gap = at - self.last
        if gap > 0:
            if gap <= MAX_GAP_SECONDS:
                self.mined_seconds += gap
            self.last = at

    def average_per_hour(self, tons: float) -> Optional[float]:
        """Tons per hour over the mining time; None until the run has MIN_AVERAGE_SECONDS of it."""
        if self.mined_seconds < MIN_AVERAGE_SECONDS:
            return None
        return tons * 3600.0 / self.mined_seconds


def minutes_to_fill(free_tons: float, per_hour: Optional[float]) -> Optional[float]:
    """Minutes to refine `free_tons` at `per_hour` tons an hour; None when the rate is not known or is zero (nothing is being refined, so there is no time to give)."""
    if per_hour is None or per_hour <= 0 or free_tons <= 0:
        return None
    return free_tons / per_hour * 60.0


def full_in_text(minutes: float) -> str:
    """`less than a minute`, `about 14 min`, `about 1 h 05 min`, or `more than a day` when it would take a day or more (a rate too low to mean anything)."""
    if minutes < 1:
        return "less than a minute"
    if minutes < 90:
        return f"about {round(minutes)} min"
    if minutes >= 24 * 60:
        return "more than a day"
    hours, rest = divmod(round(minutes), 60)
    return f"about {hours} h {rest:02d} min"
