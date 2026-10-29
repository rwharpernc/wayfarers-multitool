"""The BGS report as Discord messages: the tick the BGS Report window is showing, one block for each system.

Pure (no Tk, no network). It reads the same data as the plain Copy Summary (`bgs_ledger.PeriodView`) and the same wording helpers in bgs_format.py,
and adds Discord marks through discord_format.py, so a faction or system name can never become formatting or a mention. Copy Summary is unchanged:
that plain text is what other chat programs, forums and notes get. A report is split into messages under Discord's 2,000-character limit between
systems first, so a system's block stays together when it fits.

`options` (see discord_templates.py) choose which sections appear and the style: the Standard options give the layout the posts first had, a compact one-line-for-each-system
layout, extra government and allegiance detail, or no formatting marks at all. Escaping and splitting do not depend on the options.
"""
from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Optional

from . import bgs_format, discord_format as fmt, discord_templates
from .bgs_ledger import FactionTrack, PeriodView
from .bgs_tracker import FactionActivity, FactionSnapshot


def report_key(view: PeriodView) -> str:
    """What identifies this tick's report, so posting it again edits the earlier post instead of adding another."""
    return "bgs:" + (view.tick_start or "current")


def _opts(options: Optional[Mapping[str, Any]]) -> dict:
    return discord_templates.resolve(discord_templates.BGS, options)


def _strong(text: str, o: dict, strong: bool = True) -> str:
    """`text` in bold, or just escaped when the style is plain or it is not meant to stand out."""
    return fmt.bold(text) if strong and not o["plain"] else fmt.escape(text)


def _emphasis(text: str, o: dict) -> str:
    return fmt.italic(text) if not o["plain"] else fmt.escape(text)


def _bullet(o: dict, level: int = 0) -> str:
    if o["plain"]:
        return "• " if level == 0 else "   · "
    return "- " if level == 0 else "  - "


def _controlling(track: FactionTrack) -> bool:
    return bool(track.latest() and track.latest().is_controlling)


def _faction_parts(track: FactionTrack, o: dict) -> List[str]:
    """The words after a faction's name: its state and influence (with the change), and its government and allegiance when those are asked for."""
    parts = []
    if o["states"]:
        parts.append(bgs_format.state_change_text(track))
    if o["influence"]:
        parts.append(bgs_format.influence_change_text(track))
    now = track.latest()
    if o["details"] and now:
        parts.append(" / ".join(part for part in (now.government, now.allegiance) if part))
    return [part for part in parts if part]


def _tracks(view: PeriodView, system: str) -> List[FactionTrack]:
    return sorted(view.tracks_for(system), key=lambda t: (not _controlling(t), t.faction.casefold()))


def _you(act: FactionActivity) -> str:
    return "; ".join(bgs_format.activity_bits(act))


def _compact_line(view: PeriodView, system: str, pinned: bool, o: dict) -> str:
    """One line for the system: the controlling faction with its state and influence, then what you did there when that is asked for."""
    star = "★ " if pinned and o["pinned_star"] else ""
    head = _strong(star + bgs_format.clip(system, 60), o)
    tracks = _tracks(view, system)
    activity = view.activity_for(system)
    if not tracks and not activity:
        return f"{_bullet(o)}{head} — {_emphasis('nothing recorded', o)}"
    pieces = []
    lead = next((t for t in tracks if _controlling(t)), tracks[0] if tracks else None)
    if lead is not None:
        parts = _faction_parts(lead, o)
        pieces.append(fmt.escape(bgs_format.clip(lead.faction, 50)) + (f" ({fmt.escape(', '.join(parts))})" if parts else ""))
    if o["activity"] and activity:
        pieces.append("You: " + " / ".join(f"{fmt.escape(bgs_format.clip(a.faction, 30))} {fmt.escape(_you(a))}" for a in sorted(activity, key=lambda a: a.faction.casefold())))
    return f"{_bullet(o)}{head}" + (f" — {' — '.join(pieces)}" if pieces else "")


def system_block(view: PeriodView, system: str, pinned: bool = False, options: Optional[Mapping[str, Any]] = None) -> str:
    """One system's factions: who controls it, each faction's state and influence (with the change since before the tick), pending, recovering and
    active states, and what you did for it. With the compact option, one line for the whole system."""
    o = _opts(options)
    if o["compact"]:
        return _compact_line(view, system, pinned, o)
    lines = [_strong(("★ " if pinned and o["pinned_star"] else "") + bgs_format.clip(system, 60), o)]
    tracks = _tracks(view, system)
    activity = {a.faction.casefold(): a for a in view.activity_for(system)}
    if not tracks and not activity:
        lines.append(_bullet(o) + _emphasis("nothing recorded", o))
    seen = set()
    for track in tracks:
        seen.add(track.faction.casefold())
        name = bgs_format.clip(track.faction, 50)
        parts = _faction_parts(track, o)
        lines.append(f"{_bullet(o)}{_strong(name, o, _controlling(track) and o['bold_controller'])}" + (f" — {fmt.escape(', '.join(parts))}" if parts else ""))
        now = track.latest()
        if now and o["state_lists"]:
            for label, states in (("Pending", now.pending_states), ("Recovering", now.recovering_states), ("Active", now.active_states)):
                if states:
                    lines.append(f"{_bullet(o, 1)}{label}: {fmt.escape(', '.join(states))}")
        act = activity.get(track.faction.casefold())
        if act and o["activity"]:
            lines.append(f"{_bullet(o, 1)}You: {fmt.escape(_you(act))}")
    if o["activity"]:
        for key, act in sorted(activity.items()):
            if key not in seen:
                lines.append(f"{_bullet(o)}{fmt.escape(bgs_format.clip(act.faction, 50))} — You: {fmt.escape(_you(act))}")
    return "\n".join(lines)


def report_messages(view: PeriodView, current_system: Optional[str], pinned: Optional[Iterable[str]] = None,
                    options: Optional[Mapping[str, Any]] = None) -> List[str]:
    """The report for this tick as one or more messages, ready to copy or post. The heading names the tick (the plain UTC times, since a Discord
    time tag only renders in Discord and this text is also pasted from the clipboard)."""
    o = _opts(options)
    pin_list = list(pinned or [])
    blocks: List[str] = []
    if o["heading"]:
        blocks.append(_strong("WFMT BGS report", o) + "\n" + _emphasis(bgs_format.period_label(view), o))
    systems = view.systems(current_system, pin_list)
    if o["scope"] == discord_templates.SCOPE_WORKED:
        systems = [system for system in systems if view.activity_for(system)]
    if not systems:
        return fmt.split_message(blocks + [_bullet(o) + _emphasis("no activity", o)])
    return fmt.split_message(blocks + [system_block(view, system, bgs_format.is_pinned(system, pin_list), o) for system in systems])


def sample_view() -> PeriodView:
    """Made-up data for the customize dialog's preview when there is no tick to show yet."""
    when = "2026-10-29T09:00:00Z"

    def snap(system: str, faction: str, state: str, influence: float, controlling: bool = False, **extra: Any) -> FactionSnapshot:
        return FactionSnapshot(system, faction, faction_state=state, influence=influence, is_controlling=controlling, government="Democracy", allegiance="Federation",
                               updated_at=when, **extra)

    tracks = [
        FactionTrack("Example System", "Example Union", snap("Example System", "Example Union", "None", 0.439, True), snap("Example System", "Example Union", "Boom", 0.452, True, pending_states=["Famine"], active_states=["Boom"])),
        FactionTrack("Example System", "Example Cartel", None, snap("Example System", "Example Cartel", "War", 0.300)),
        FactionTrack("Sample Station", "Sample Alliance", None, snap("Sample Station", "Sample Alliance", "Expansion", 0.510, True)),
    ]
    activity = [FactionActivity("Example System", "Example Union", missions=2, inf_plus=4, exploration_credits=1_500_000, last_at=when)]
    return PeriodView(when, None, True, activity, tracks)
