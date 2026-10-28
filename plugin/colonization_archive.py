"""The facts the Colonization Archive window shows about a finished construction site (see colonization_archive_window.py): how it
ended, when it started and finished, how long it took, what it needed, and the text copied to the clipboard. Pure functions of a
`Site`, so they are tested without a window."""
from __future__ import annotations

from . import colonization
from .colonization import Site


def result_label(site: Site) -> str:
    return "Failed" if site.failed else ("Complete" if site.complete else "Open")


def _day(stamp: str) -> str:
    return stamp[:10] if stamp else ""


def took_text(site: Site) -> str:
    """How long the build took, from when WFMT first saw the site to when the depot reported it done ("" when either time is unknown)."""
    start, end = colonization._parse_time(site.first_seen), colonization._parse_time(site.completed_at)
    if not (site.complete and start and end and end >= start):
        return ""
    days = (end - start).total_seconds() / 86400
    return f"{days:.1f} d" if days >= 1 else f"{days * 24:.1f} h"


def needed_tons(site: Site) -> int:
    return sum(r.required for r in site.resources)


def site_values(site: Site) -> tuple:
    return (site.display_name(), site.system, result_label(site), _day(site.first_seen), _day(site.completed_at or site.updated),
            took_text(site), f"{needed_tons(site):,} t")


def summary_text(site: Site) -> str:
    """The site's facts as text, for the clipboard."""
    lines = [f"{site.display_name()}{f' ({site.system})' if site.system else ''} - {result_label(site).lower()}"]
    when = [f"started {_day(site.first_seen)}" if site.first_seen else "", f"finished {_day(site.completed_at)}" if site.completed_at else "",
            f"took {took_text(site)}" if took_text(site) else ""]
    facts = ", ".join(part for part in when if part)
    if facts:
        lines.append(facts)
    lines.append(f"{needed_tons(site):,} t needed in all:")
    lines.extend(f"- {r.label or r.key}: {r.provided:,} of {r.required:,} t" for r in sorted(site.resources, key=lambda r: (r.label or r.key).casefold()))
    return "\n".join(lines)
