"""Spansh's exact plotter, from WFMT: look a system up, ask for a route for the ship, wait for the answer. The only network code of the Route Planner.

The request was taken from Spansh's own page and checked against a real answer (2026-10-18, a Mk II overcharge explorer from the Bubble's far side to Colonia, 42 jumps):
- `GET https://spansh.co.uk/api/systems/field_values/system_names?q=<name>` -> `{"min_max": [{"id64", "name", "x", "y", "z"}, ...]}`; the plotter wants systems by `id64`
- `POST https://spansh.co.uk/api/generic/route` with the form `route_planner.build_form` makes -> `{"job": "<id>", "status": "queued"}`
- `GET /api/results/<job>` until `state == "completed"`; `result["jumps"]` lists every system from the start, each with `name`, `id64`, `x`, `y`, `z`, `distance`,
  `distance_to_destination`, `fuel_in_tank`, `fuel_used`, `has_neutron`, `must_refuel`, `must_inject` and `is_scoopable`
If Spansh changes it, this is the one place to fix. It sends Spansh the two systems and the ship's numbers, nothing else. Only when the commander ticks *Mark white dwarfs the route passes* does it send EDSM the names of the route's systems
(`edsm_client.primary_star_types`), to learn which have a white dwarf as their main star; Spansh's router knows only neutron stars.
"""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable, List, Optional, Tuple

from . import http_identity, spansh_courtesy, route_planner, spansh_planners
from .trade_spansh_client import RouteSearchError

LOOKUP_URL = "https://spansh.co.uk/api/systems/field_values/system_names"
ROUTE_URL = "https://spansh.co.uk/api/generic/route"
LOOKUP_TIMEOUT_S = 15
_USER_AGENT = http_identity.user_agent("route-planner")


def lookup_system(name: str) -> Tuple[int, str]:
    """(id64, the name as Spansh spells it) for an exact system name. Raises RouteSearchError when Spansh does not know it, or an OSError when it cannot be reached."""
    wanted = " ".join(str(name or "").split())
    if not wanted:
        raise RouteSearchError("Give a system name.")
    request = urllib.request.Request(LOOKUP_URL + "?" + urllib.parse.urlencode({"q": wanted}), headers={"User-Agent": _USER_AGENT})
    try:
        data = json.loads(spansh_courtesy.call(request, LOOKUP_TIMEOUT_S).decode("utf-8"))
    except spansh_courtesy.SpanshBusy as err:
        raise RouteSearchError(str(err)) from err
    for row in data.get("min_max", []) if isinstance(data, dict) else []:
        if isinstance(row, dict) and isinstance(row.get("name"), str) and row.get("name", "").casefold() == wanted.casefold() and isinstance(row.get("id64"), int):
            return row["id64"], row["name"]
    raise RouteSearchError(f"Spansh does not know a system called '{wanted}'. Check the spelling.")


SYSTEM_URL = "https://spansh.co.uk/api/system/"


def fetch_stars(id64: int) -> Optional[List[dict]]:
    """The stars of a system, as Spansh lists them (each with `name`, `subtype`, `is_main_star` and `distance_to_arrival`): `GET /api/system/<id64>`. None when Spansh does not know the system.
    A network error is raised."""
    request = urllib.request.Request(SYSTEM_URL + str(int(id64)), headers={"User-Agent": _USER_AGENT})
    try:
        data = json.loads(spansh_courtesy.call(request, LOOKUP_TIMEOUT_S).decode("utf-8"))
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise
    record = data.get("record") if isinstance(data, dict) else None
    bodies = record.get("bodies") if isinstance(record, dict) else None
    return [body for body in bodies if isinstance(body, dict) and body.get("type") == "Star"] if isinstance(bodies, list) else None


def plot(ship: route_planner.ShipInfo, start: str, destination: str, options: route_planner.Options, start_id: Optional[int] = None,
         cancel: Optional[threading.Event] = None, on_state: Optional[Callable[[str], None]] = None) -> route_planner.Route:
    """Ask for a route from `start` to `destination` for `ship` and return it. `start_id` is the start's system address when the game gave it, which saves a lookup.
    Raises route_planner.PlotterError (the ship), RouteSearchError (Spansh refused or could not find a system) or a network error."""
    params = ship.params()
    if start_id is None:
        start_id, start = lookup_system(start)
    if on_state is not None:
        on_state("Looking up the destination")
    destination_id, destination = lookup_system(destination)
    form = route_planner.build_form(params, ship.cargo, options, start_id, destination_id)
    result = spansh_planners.fetch_job(ROUTE_URL, form, cancel, on_state, slow_hint="Try again, or a nearer destination.")
    route = route_planner.Route(" ".join(start.split()), destination, route_planner.legs_from_result(result))
    if options.mark_white_dwarfs and route.legs:
        if on_state is not None:
            on_state("Asking EDSM which stars are white dwarfs")
        from . import edsm_client                     # imported here: it needs `requests`, which only this option uses
        star_types = edsm_client.primary_star_types([leg.system for leg in route.legs])
        if star_types is None:
            route.white_dwarf_check = "failed"
        else:
            route.legs = route_planner.mark_white_dwarfs(route.legs, star_types)
            route.white_dwarf_check = "done"
    return route
