"""Expedition Log summary as Discord messages: what an expedition recorded, with the credits its data sales earned.

Pure (no Tk, no network). The figures come from the same `Run` the Copy summary button uses, and the Discord marks come from discord_format.py, so an expedition,
system or ship name can never become formatting or a mention. `options` (see discord_templates.py) choose which parts appear: the Standard options give the whole
summary except the ships and notes; Compact keeps the heading and the earnings; Detailed adds the ships and notes; Plain removes the formatting marks. Escaping and
splitting under Discord's 2,000-character limit do not depend on the options.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Optional

from . import discord_format as fmt, discord_templates
from .expedition_log import Run, Totals, credits, display_time, duration_text


def report_key(run: Run) -> str:
    """What identifies this expedition's post, so posting it again edits the earlier post instead of adding another."""
    return "expedition:" + str(run.id or "run")


def _opts(options: Optional[Mapping[str, Any]]) -> dict:
    return discord_templates.resolve(discord_templates.EXPEDITION, options)


def summary_messages(run: Optional[Run], options: Optional[Mapping[str, Any]] = None, now: Optional[float] = None) -> List[str]:
    """The expedition as one or more messages. An empty list when there is no expedition, so a button can say so instead of posting nothing."""
    if run is None:
        return []
    o = _opts(options)
    plain = o["plain"]
    t = run.totals

    def head(text: str) -> str:
        return fmt.escape(text) if plain else fmt.bold(text)

    def line(label: str, value: str) -> str:
        return f"{fmt.escape(label)} {fmt.escape(value)}" if plain else f"{fmt.escape(label)} {fmt.bold(value)}"

    blocks: List[str] = []
    if o["heading"]:
        title = f"WFMT Expedition — {run.name}"
        times = f"{run.status}, {duration_text(run.elapsed(now))}" + (f", started {display_time(run.started)} UTC" if run.started else "")
        blocks.append(head(title) + "\n" + (fmt.escape(times) if plain else fmt.italic(times)))
    if o["route"] and (run.start_system or run.end_system):
        parts = [f"From {run.start_system}" if run.start_system else "", f"to {run.end_system}" if run.end_system else ""]
        blocks.append(fmt.escape(" ".join(p for p in parts if p)))
    if o["exploration"]:
        blocks.append(head("Exploration") + "\n" + fmt.escape(
            f"{len(run.systems):,} systems, {t.jumps:,} jumps, {t.light_years:,.0f} ly, {t.bodies_scanned:,} bodies scanned "
            f"({t.first_discoveries:,} first discoveries), {t.mapped:,} mapped, {t.landings:,} landings"))
    if o["exobiology"]:
        genera = f" ({', '.join(run.genera)})" if run.genera else ""
        blocks.append(head("Exobiology") + "\n" + fmt.escape(f"{t.bio_samples:,} samples, {t.bio_species:,} species analyzed, {t.bio_first_footfalls:,} first footfalls{genera}"))
    if o["sales"]:
        rows = [line("Exploration data sold:", f"{credits(t.explore_earned)} cr"), line("Exobiology sold:", f"{credits(t.bio_earned)} cr"),
                line("Total earned:", f"{credits(t.earned)} cr")]
        if o["unsold"]:
            rows.append(line("Unsold (estimate):", f"~{credits(t.unsold)} cr"))
        blocks.append(head("Sales") + "\n" + "\n".join(rows))
    elif o["unsold"]:
        blocks.append(line("Unsold (estimate):", f"~{credits(t.unsold)} cr"))
    if o["ships"] and run.ships:
        blocks.append(head("Ships") + "\n" + fmt.escape("; ".join(run.ships)))
    if o["notes"] and run.notes.strip():
        blocks.append(head("Notes") + "\n" + fmt.escape(run.notes))
    return fmt.split_message(blocks)


def sample_run() -> Run:
    """Made-up data for the customize dialog's preview when there is no expedition to show yet."""
    return Run(id="sample", name="Example Expedition", status="stopped", started="2026-11-01T10:00:00Z", ended="2026-11-01T14:30:00Z",
               start_system="Example System", end_system="Sample Reach", ships=["Example Explorer"], notes="A sample note.",
               totals=Totals(jumps=42, light_years=3120.0, bodies_scanned=180, first_discoveries=35, mapped=12, landings=3, bio_samples=9, bio_species=3,
                             bio_first_footfalls=1, explore_earned=2_450_000, explore_estimated=600_000, bio_earned=5_100_000, bio_estimated=0),
               systems=["Example System", "Sample Reach"], genera=["Bacterium", "Fungoida"])
