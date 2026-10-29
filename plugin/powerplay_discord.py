"""Powerplay progress as Discord messages: this session's merits for each system, and the cycle's totals.

Pure (no Tk, no network). The rows come from `powerplay_clipboard.progress_rows`, the same data Copy Progress uses, and the Discord marks come
from discord_format.py, so a system name can never become formatting or a mention. The editable clipboard template applies to the plain Copy
Progress only. Control Points are estimates (from the editable merit ratios), and the text says so with a `~`. A report is split into messages under
Discord's 2,000-character limit between rows.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

from . import discord_format as fmt
from .powerplay_clipboard import ProgressRow, inara_system_url


def report_key(session: Dict[str, Any]) -> str:
    """What identifies this session's post, so posting again in the same session edits the earlier post, and a new session (a new login) posts anew."""
    return "powerplay:" + str(session.get("started_at") or "session")


def row_line(row: ProgressRow) -> str:
    """`- [Nervi](<link>) — 120 merits (~48.0 CP) — Exploited`: the system links to its Inara page, without a preview card."""
    state = "" if row.state in ("", "—") else f" — {fmt.escape(row.state)}"
    return f"- {fmt.link(row.system, inara_system_url(row.system))} — {row.merits:,} merits (~{row.cp:,.1f} CP){state}"


def progress_messages(rows: Sequence[ProgressRow], power: str = "", cycle_line: str = "") -> List[str]:
    """This session's progress as one or more messages: a heading (with the Power when it is known), a line for each system, and the cycle's total
    line when there is one. An empty list when there is nothing to share, so a button can say so instead of posting a heading alone."""
    if not rows:
        return []
    heading = fmt.bold("WFMT Powerplay progress") + (f" — {fmt.escape(power)}" if power else "") + "\n" + fmt.italic("This session. CP is an estimate (~).")
    blocks = [heading] + [row_line(row) for row in rows]
    if cycle_line:
        blocks.append(fmt.bold("Cycle") + "\n" + fmt.escape(cycle_line))
    return fmt.split_message(blocks)
