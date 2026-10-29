"""Powerplay progress as Discord messages: this session's merits for each system, and the cycle's totals.

Pure (no Tk, no network). The rows come from `powerplay_clipboard.progress_rows`, the same data Copy Progress uses, and the Discord marks come
from discord_format.py, so a system name can never become formatting or a mention. The editable clipboard template applies to the plain Copy
Progress only. Control Points are estimates (from the editable merit ratios), and the text says so with a `~`. A report is split into messages under
Discord's 2,000-character limit between rows.

`options` (see discord_templates.py) choose which parts appear: the Standard options give the layout the posts first had, and others drop the links, the state or the
cycle line, add the merits for each activity, or remove the formatting marks. Escaping and splitting do not depend on the options.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from . import discord_format as fmt, discord_templates
from .powerplay_clipboard import ProgressRow, inara_system_url


def report_key(session: Dict[str, Any]) -> str:
    """What identifies this session's post, so posting again in the same session edits the earlier post, and a new session (a new login) posts anew."""
    return "powerplay:" + str(session.get("started_at") or "session")


def _opts(options: Optional[Mapping[str, Any]]) -> dict:
    return discord_templates.resolve(discord_templates.POWERPLAY, options)


def _bullet(o: dict) -> str:
    return "• " if o["plain"] else "- "


def row_line(row: ProgressRow, options: Optional[Mapping[str, Any]] = None) -> str:
    """`- [Nervi](<link>) — 120 merits (~48.0 CP) — Exploited`: the system links to its Inara page, without a preview card. Each part after the merits can be left out, and
    the merits for each activity added."""
    o = _opts(options)
    if o["links"] and o["plain"]:
        name = f"{fmt.escape(row.system)} <{inara_system_url(row.system)}>"
    elif o["links"]:
        name = fmt.link(row.system, inara_system_url(row.system))
    else:
        name = fmt.escape(row.system)
    line = f"{_bullet(o)}{name} — {row.merits:,} merits" + (f" (~{row.cp:,.1f} CP)" if o["cp"] else "")
    if o["activities"] and row.by_activity:
        line += " — " + fmt.escape(", ".join(f"{label} {merits:,}" for label, merits in row.by_activity))
    if o["state"] and row.state not in ("", "—"):
        line += f" — {fmt.escape(row.state)}"
    return line


def progress_messages(rows: Sequence[ProgressRow], power: str = "", cycle_line: str = "", options: Optional[Mapping[str, Any]] = None) -> List[str]:
    """This session's progress as one or more messages: a heading (with the Power when it is known), a line for each system, and the cycle's total
    line when there is one. An empty list when there is nothing to share, so a button can say so instead of posting a heading alone."""
    if not rows:
        return []
    o = _opts(options)
    blocks: List[str] = []
    if o["heading"]:
        title = (fmt.bold("WFMT Powerplay progress") if not o["plain"] else fmt.escape("WFMT Powerplay progress")) + (f" — {fmt.escape(power)}" if power and o["power"] else "")
        note = "This session. CP is an estimate (~)." if o["cp"] else "This session."
        blocks.append(title + "\n" + (fmt.italic(note) if not o["plain"] else fmt.escape(note)))
    blocks += [row_line(row, o) for row in rows]
    if cycle_line and o["cycle"]:
        blocks.append((fmt.bold("Cycle") if not o["plain"] else "Cycle") + "\n" + fmt.escape(cycle_line))
    return fmt.split_message(blocks)


def sample_rows() -> List[ProgressRow]:
    """Made-up data for the customize dialog's preview when there is no session to show yet."""
    return [ProgressRow("Example System", 120, 48.0, "Exploited", (("Acquisition", 80), ("Reinforcement", 40))),
            ProgressRow("Sample Station", 1234, 493.6, "—", (("Acquisition", 1234),))]


SAMPLE_CYCLE_LINE = "CYCLE 12 TOTAL — 3,400 merits · est. 1,360.0 CP · 5 systems worked   (Acquisition 2,000 · Reinforcement 1,400)"
SAMPLE_POWER = "Example Power"
