"""Spansh's fleet carrier router, from WFMT: look the systems up, ask for a route, wait for the answer. The only network code of the Carrier Route planner; the request and the answer are
described in `carrier_route.py`. It sends Spansh the systems (by address) and the carrier's size, space used and tritium, nothing else; a request goes through the shared courtesy layer
(`spansh_courtesy`) like the other Spansh calls, one route job and one lookup per system."""
from __future__ import annotations

import threading
from typing import Callable, List, Optional, Sequence

from . import carrier_route, spansh_exact, spansh_planners
from .trade_spansh_client import RouteSearchError

ROUTE_URL = "https://spansh.co.uk/api/fleetcarrier/route"


def plot(kind: str, start: str, destinations: Sequence[str], used_capacity: int, work_out_fuel: bool = True, tritium_in_tank: int = 0, tritium_in_market: int = 0,
         start_id: Optional[int] = None, cancel: Optional[threading.Event] = None, on_state: Optional[Callable[[str], None]] = None) -> carrier_route.CarrierRoute:
    """A route for a carrier from `start` through `destinations` in order. `start_id` is the start's system address when the journal gave it, which saves a lookup. Raises RouteSearchError
    (Spansh refused or does not know a system) or a network error."""
    wanted = [" ".join(str(name).split()) for name in destinations if " ".join(str(name).split())]
    if not wanted:
        raise RouteSearchError("Give the system to go to.")
    if len(wanted) > carrier_route.MAX_DESTINATIONS:
        raise RouteSearchError(f"Spansh takes at most {carrier_route.MAX_DESTINATIONS} destinations.")
    if start_id is None:
        if on_state is not None:
            on_state("Looking up the start")
        start_id, start = spansh_exact.lookup_system(start)
    ids: List[int] = []
    names: List[str] = []
    for name in wanted:
        if on_state is not None:
            on_state(f"Looking up {name}")
        found_id, found_name = spansh_exact.lookup_system(name)
        ids.append(found_id)
        names.append(found_name)
    form = carrier_route.build_form(kind, start_id, ids, used_capacity, work_out_fuel, tritium_in_tank, tritium_in_market)
    result = spansh_planners.fetch_job(ROUTE_URL, form, cancel, on_state, slow_hint="Try again, or a nearer destination.")
    return carrier_route.CarrierRoute(kind, " ".join(start.split()), names[-1], carrier_route.legs_from_result(result), 0, carrier_route.start_needs(result))
