"""
Starting a Raven Colonial project for a construction site WFMT tracks, the step Raven's own site and SrvSurvey both offer and WFMT
did not: until a project exists, the progress and delivery sharing in rcc_sync.py finds nothing to update.

What a run does, in order (each only after the commander confirmed the dialog; nothing happens on docking):

1. The system's plan is read (no key needed) to see whether a project already exists for the site, and which planned sites it has.
2. A site chosen from the plan is built from. With none chosen the project stands on its own, as SrvSurvey's does; the plan is
   never edited by this.
3. The project is created (`PUT /api/project`) from the depot snapshot WFMT already holds: the market id, the system, the
   commodities still needed and the total need. Raven answers with the project, whose build id is what every later call uses.
4. The commander is linked to it, and, when asked, it is made their primary project and their fleet carrier is attached.

A failed project stops the run; the optional ones after the project exists report their own failure and never undo it. Pure
shaping plus one function (`create`) whose network calls are passed in, so it is tested without a connection.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from . import build_costs, colonization, rcc_client
from .colonization import Site

NO_PLAN_ENTRY = "None (a project of its own)"
NAME_MAX = 60
NOTES_MAX = 500
BUILD_ID_MAX = rcc_client.BUILD_ID_MAX

Writer = Callable[..., Any]


@dataclass(frozen=True)
class BuildChoice:
    """One building, with the build types (layouts) Raven Colonial knows it by; the layout is what a project is made with."""
    key: str
    name: str
    tier: int
    location: str                    # "orbital" or "surface"
    layouts: Tuple[str, ...]


LOCATIONS = ("orbital", "surface")


def build_choices() -> List[BuildChoice]:
    """Every building in the bundled cost table, by tier then name."""
    seen = set()
    choices = []
    for cost in build_costs.table().values():
        if cost.key in seen:
            continue
        seen.add(cost.key)
        choices.append(BuildChoice(cost.key, cost.name, cost.tier, cost.location, tuple(build_costs.layouts_of(cost))))
    return sorted(choices, key=lambda c: (c.tier, c.name.casefold(), c.key))


def choices_at(location: str) -> List[BuildChoice]:
    return [c for c in build_choices() if c.location == location]


def choice_label(choice: BuildChoice) -> str:
    return f"Tier {choice.tier}: {choice.name}"


def choice_for_layout(layout: str) -> Optional[BuildChoice]:
    """The building that a build type (layout) makes, or None for one the table does not know."""
    wanted = (layout or "").strip().casefold()
    return next((c for c in build_choices() if wanted in (x.casefold() for x in c.layouts)), None)


_SHIP_NAME = re.compile(r"colon[a-z]*ation[\s_;]*ship", re.IGNORECASE)   # either spelling, with or without a space


def is_construction_ship(site: Site) -> bool:
    """Whether the site is the system's colonization ship (its primary port), by the name the game gives it."""
    return bool(_SHIP_NAME.search(site.name))


def planned_sites(sites: Sequence[rcc_client.RccSite]) -> List[rcc_client.RccSite]:
    """The sites in the plan with no project yet and no market (nothing built), the ones a new project could belong to."""
    return [s for s in sites if s.site_id and s.status == rcc_client.STATUS_PLANNED and not s.build_id and s.market_id is None]


PRIMARY_PORT_NAME = "Primary port"


def suggested_name(site: Site) -> str:
    """The name to offer: "Primary port" for the system's colonization ship, else the station's own name without the game's
    construction-site prefix."""
    if is_construction_ship(site):
        return PRIMARY_PORT_NAME
    return rcc_client.station_part(site.display_name())[:NAME_MAX]


def guess_planned(sites: Sequence[rcc_client.RccSite], name: str) -> Optional[rcc_client.RccSite]:
    """The planned site whose name is the one given, or the only planned site there is (None when it is not clear which)."""
    wanted = name.strip().casefold()
    named = [s for s in planned_sites(sites) if s.name.casefold() == wanted]
    if len(named) == 1:
        return named[0]
    everything = planned_sites(sites)
    return everything[0] if len(everything) == 1 else None


def parse_due(text: str) -> Optional[str]:
    """`YYYY-MM-DD` as the ISO time Raven stores, or None for a blank. Raises ValueError for anything else."""
    text = (text or "").strip()
    if not text:
        return None
    day = datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return day.isoformat().replace("+00:00", "Z")


@dataclass
class Request:
    """Everything the dialog collected, plus what the journal holds for the site."""
    site: Site
    cmdr: str
    key: str
    system: str
    system_address: Optional[int]
    star_pos: Optional[Tuple[float, float, float]]
    name: str
    build_type: str
    body_num: Optional[int] = None
    body_name: str = ""
    planned: Optional[rcc_client.RccSite] = None     # a planned site to build from; None makes a project of its own
    architect: str = ""
    notes: str = ""
    due: Optional[str] = None
    primary_port: bool = False
    make_primary: bool = True
    fleet_carrier: Optional[int] = None              # the market id of the carrier to attach, or None


@dataclass
class Result:
    build_id: str = ""
    steps: List[str] = field(default_factory=list)       # what worked, in words
    warnings: List[str] = field(default_factory=list)    # optional steps that did not

    @property
    def summary(self) -> str:
        text = "; ".join(self.steps)
        return text + (" Not done: " + " ".join(self.warnings) if self.warnings else "")


def validate(request: Request) -> str:
    """What is wrong with the request, in words to show ("" when nothing is)."""
    if not request.key.strip():
        return "No Raven Colonial key is saved for this commander."
    if not request.name.strip():
        return "Give the site a name."
    if not request.build_type.strip():
        return "Choose what is being built."
    if request.system_address is None:
        return "WFMT does not know this system's address yet. Dock at the site once, then try again."
    return ""


def depot_snapshot(site: Site) -> Dict[str, Any]:
    """The depot event Raven expects, rebuilt from the figures WFMT holds (the journal's own entry is not kept past its folding in)."""
    return {
        "timestamp": site.journal_at or site.updated, "event": colonization.EVENT_DEPOT, "marketID": site.market_id,
        "constructionProgress": site.progress, "constructionComplete": site.complete, "constructionFailed": site.failed,
        "resourcesRequired": [{"name": f"${r.key}_name;", "name_Localised": r.label, "requiredAmount": r.required,
                               "providedAmount": r.provided, "payment": r.payment} for r in site.resources]}


def project_body(request: Request, site_id: str) -> Dict[str, Any]:
    """The `PUT /api/project` body. Optional fields are left out when unknown, never sent empty."""
    site = request.site
    commodities = {r.key: r.remaining for r in site.resources}
    body: Dict[str, Any] = {
        "marketId": site.market_id, "systemAddress": request.system_address, "buildName": request.name.strip()[:NAME_MAX],
        "buildType": request.build_type, "systemName": request.system, "commodities": commodities,
        "maxNeed": sum(r.required for r in site.resources), "colonisationConstructionDepot": depot_snapshot(site),
        "isPrimaryPort": request.primary_port}
    if site_id:
        body["systemSiteId"] = site_id
    if request.star_pos:
        body["starPos"] = list(request.star_pos)
    if request.body_num is not None:
        body["bodyNum"] = request.body_num
    if request.body_name.strip():
        body["bodyName"] = request.body_name.strip()[:NAME_MAX]
    if request.architect.strip():
        body["architectName"] = request.architect.strip()[:NAME_MAX]
    if request.notes.strip():
        body["notes"] = request.notes.strip()[:NOTES_MAX]
    if request.due:
        body["timeDue"] = request.due
    return body


def locate(system: str, plan: Optional[rcc_client.RccSystem], state: Mapping[str, Any]
           ) -> Tuple[Optional[int], Optional[Tuple[float, float, float]]]:
    """The system's address and galactic position: Raven's own when its plan has them, else the commander's game state (EDMC's
    `monitor.state`) when they are in that very system, else unknown (None)."""
    address = plan.id64 if plan else None
    pos = plan.pos if plan else None
    if str(state.get("SystemName") or "").strip().casefold() == system.strip().casefold():
        if address is None and isinstance(state.get("SystemAddress"), int) and not isinstance(state.get("SystemAddress"), bool):
            address = state["SystemAddress"]
        raw = state.get("StarPos")
        if pos is None and isinstance(raw, (list, tuple)) and len(raw) == 3 and all(isinstance(v, (int, float)) for v in raw):
            pos = (float(raw[0]), float(raw[1]), float(raw[2]))
    return address, pos


def _quote(text: Any) -> str:
    return urllib.parse.quote(str(text).strip(), safe="")


def create(request: Request, send: Writer = rcc_client.send_json) -> Result:
    """Run the steps (see the module docstring). Raises rcc_client.RccError when the project could not be made; the later
    steps only add a warning to the result. `send(method, path, body, key, cmdr=...)` returns Raven's parsed answer."""
    problem = validate(request)
    if problem:
        raise rcc_client.RccError(problem)
    result = Result()
    key, cmdr = request.key.strip(), request.cmdr
    site_id = request.planned.site_id if request.planned else ""
    answer = send("PUT", "/api/project", project_body(request, site_id), key, cmdr=cmdr)
    build_id = str(answer.get("buildId") or "").strip()[:BUILD_ID_MAX] if isinstance(answer, Mapping) else ""
    if not build_id:
        raise rcc_client.RccError("Raven Colonial made the project but did not say which; open it on the site to check.")
    result.build_id = build_id
    result.steps.append(f"Created the project for {request.name.strip()}.")
    build = _quote(build_id)

    def optional(done: str, failed: str, method: str, path: str) -> None:
        try:
            send(method, path, None, key, cmdr=cmdr)
            result.steps.append(done)
        except rcc_client.RccError as err:
            result.warnings.append(f"{failed} ({err})")

    optional("Linked you to it.", "Linking you to it failed.", "PUT", f"/api/project/{build}/link/{_quote(cmdr.casefold())}")
    if request.make_primary:
        optional("Made it your primary project.", "Making it your primary project failed.", "PUT",
                 f"/api/Cmdr/{_quote(cmdr.casefold())}/primary/{build}")
    if request.fleet_carrier is not None:
        optional("Attached your fleet carrier.", "Attaching your fleet carrier failed.", "PUT",
                 f"/api/project/{build}/fc/{int(request.fleet_carrier)}")
    return result


def demolish_body(site: rcc_client.RccSite) -> Dict[str, Any]:
    """The `PUT /api/v2/system/<id64>/sites` body that marks one planned site demolished (Raven's status, not a game action)."""
    return {"update": [{"id": site.site_id, "name": site.name, "bodyNum": site.body_num or 0, "buildType": site.build_type,
                        "status": rcc_client.STATUS_DEMOLISH, **({"buildId": site.build_id} if site.build_id else {}),
                        **({"marketId": site.market_id} if site.market_id is not None else {})}], "delete": []}
