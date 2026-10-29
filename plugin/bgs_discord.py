"""The BGS report as Discord messages: the tick the BGS Report window is showing, one block for each system.

Pure (no Tk, no network). It reads the same data as the plain Copy Summary (`bgs_ledger.PeriodView`) and the same wording helpers in bgs_format.py,
and adds Discord marks through discord_format.py, so a faction or system name can never become formatting or a mention. Copy Summary is unchanged:
that plain text is what other chat programs, forums and notes get. A report is split into messages under Discord's 2,000-character limit between
systems first, so a system's block stays together when it fits.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

from . import bgs_format, discord_format as fmt
from .bgs_ledger import PeriodView


def report_key(view: PeriodView) -> str:
    """What identifies this tick's report, so posting it again edits the earlier post instead of adding another."""
    return "bgs:" + (view.tick_start or "current")


def system_block(view: PeriodView, system: str, pinned: bool = False) -> str:
    """One system's factions: who controls it, each faction's state and influence (with the change since before the tick), pending, recovering and
    active states, and what you did for it."""
    lines = [fmt.bold(("★ " if pinned else "") + bgs_format.clip(system, 60))]
    tracks = sorted(view.tracks_for(system), key=lambda t: (not (t.latest() and t.latest().is_controlling), t.faction.casefold()))
    activity = {a.faction.casefold(): a for a in view.activity_for(system)}
    if not tracks and not activity:
        lines.append("- " + fmt.italic("nothing recorded"))
    seen = set()
    for track in tracks:
        seen.add(track.faction.casefold())
        controlling = bool(track.latest() and track.latest().is_controlling)
        name = bgs_format.clip(track.faction, 50)
        parts = [part for part in (bgs_format.state_change_text(track), bgs_format.influence_change_text(track)) if part]
        lines.append(f"- {fmt.bold(name) if controlling else fmt.escape(name)}" + (f" — {fmt.escape(', '.join(parts))}" if parts else ""))
        now = track.latest()
        if now:
            for label, states in (("Pending", now.pending_states), ("Recovering", now.recovering_states), ("Active", now.active_states)):
                if states:
                    lines.append(f"  - {label}: {fmt.escape(', '.join(states))}")
        act = activity.get(track.faction.casefold())
        if act:
            lines.append(f"  - You: {fmt.escape('; '.join(bgs_format.activity_bits(act)))}")
    for key, act in sorted(activity.items()):
        if key not in seen:
            lines.append(f"- {fmt.escape(bgs_format.clip(act.faction, 50))} — You: {fmt.escape('; '.join(bgs_format.activity_bits(act)))}")
    return "\n".join(lines)


def report_messages(view: PeriodView, current_system: Optional[str], pinned: Optional[Iterable[str]] = None) -> List[str]:
    """The report for this tick as one or more messages, ready to copy or post. The heading names the tick (the plain UTC times, since a Discord
    time tag only renders in Discord and this text is also pasted from the clipboard)."""
    pin_list = list(pinned or [])
    heading = fmt.bold("WFMT BGS report") + "\n" + fmt.italic(bgs_format.period_label(view))
    systems = view.systems(current_system, pin_list)
    if not systems:
        return fmt.split_message([heading, "- " + fmt.italic("no activity")])
    blocks = [heading] + [system_block(view, system, bgs_format.is_pinned(system, pin_list)) for system in systems]
    return fmt.split_message(blocks)
