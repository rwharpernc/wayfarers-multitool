"""Expedition plan as Discord messages: an announcement of where an expedition is going and how far it has got.

Pure (no Tk, no network). The data is the planner's `Expedition` (name, status, stops with bodies and notes, visited marks, jumps and light-years), the same one Copy list
uses. The Discord marks come from discord_format.py, so a stop, body or expedition name can never become formatting or a mention. `options` (see discord_templates.py)
choose which parts appear: the Standard options give the heading, progress, route ends, next stop and the next 10 stops; Compact keeps the heading, progress and next stop;
Detailed lists every stop with its notes; Plain removes the formatting marks. A long list is split under Discord's 2,000-character limit between stops.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Optional

from . import discord_format as fmt, discord_templates
from .expedition import Expedition, Stop

SHORT_STOPS = 10          # how many stops the short list shows


def report_key(e: Expedition) -> str:
    """What identifies this expedition's announcement, so posting it again edits the earlier post."""
    return "plan:" + str(e.id or "plan")


def _opts(options: Optional[Mapping[str, Any]]) -> dict:
    return discord_templates.resolve(discord_templates.ANNOUNCEMENT, options)


def _place(stop: Stop, bodies: bool) -> str:
    return f"{stop.system} / {stop.body}" if bodies and stop.body else stop.system


def summary_messages(e: Optional[Expedition], options: Optional[Mapping[str, Any]] = None) -> List[str]:
    """The expedition plan as one or more messages. An empty list when there is no expedition or it has no stops, so a button can say so."""
    if e is None or not e.stops:
        return []
    o = _opts(options)
    plain = o["plain"]

    def head(text: str) -> str:
        return fmt.escape(text) if plain else fmt.bold(text)

    blocks: List[str] = []
    if o["heading"]:
        blocks.append(head(f"WFMT Expedition plan — {e.name}") + "\n" + (fmt.escape(e.status) if plain else fmt.italic(e.status)))
    if o["progress"]:
        text = f"{e.visited_count} of {len(e.stops)} stops reached"
        if e.jumps:
            text += f", {e.jumps:,} jumps"
        if e.light_years:
            text += f", {e.light_years:,.0f} ly"
        blocks.append(fmt.escape(text))
    if o["route"] and len(e.stops) > 1:
        blocks.append(fmt.escape(f"From {e.stops[0].system} to {e.stops[-1].system}"))
    nxt = e.next_stop()
    if o["next"]:
        blocks.append(f"{head('Next stop')} {fmt.escape(_place(nxt, o['bodies']))}" if nxt is not None else fmt.escape("All stops reached."))
    if o["stops"]:
        numbered = list(enumerate(e.stops, start=1))
        if o["short"]:
            numbered = [(n, s) for n, s in numbered if not s.is_visited][:SHORT_STOPS]
        if numbered:
            title = "Stops" if not o["short"] else f"Next {len(numbered)} stop{'s' if len(numbered) != 1 else ''}"
            blocks.append(head(title))
            for number, stop in numbered:
                mark = "✓ " if stop.is_visited else ""
                note = f" — {fmt.escape(stop.note)}" if o["notes"] and stop.note else ""
                blocks.append(f"{number}. {mark}{fmt.escape(_place(stop, o['bodies']))}{note}")
    return fmt.split_message(blocks)


def sample_expedition() -> Expedition:
    """Made-up data for the customize dialog's preview when there is no expedition to show yet."""
    names = ["Example System", "Sample Reach", "Demo Nebula", "Test Cluster"]
    stops = [Stop(id=str(i), system=name, body=f"{name} A 1" if i % 2 else "", note="Check the ring" if i == 2 else "",
                  visited="2026-11-01T10:00:00Z" if i == 0 else "") for i, name in enumerate(names)]
    return Expedition(id="sample", name="Example Expedition", status="active", jumps=12, light_years=840.0, stops=stops)
