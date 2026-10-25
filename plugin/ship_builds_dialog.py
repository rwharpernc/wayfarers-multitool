"""The Add/Edit Ship Build window (SHIPS in Field Ops), on the shared form (`uikit/form.py`). `build_ship` turns the typed text into a `ShipBuild` or says what is wrong, without a window, so it can
be tested; `open_ship_build_dialog` shows the form. Parented on the caller's toplevel, not on a frame the panel rebuilds every second (which would take the window with it).
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Optional

from .ship_builds_data import KNOWN_SITES, ShipBuild, new_id
from .uikit.form import Field, FormDialog


def fields_for(existing: Optional[ShipBuild], prefill_ship: str = "") -> List[Field]:
    return [
        Field("name", "Name", "text", existing.name if existing else "", required=True),
        Field("ship", "Ship", "text", existing.ship if existing else prefill_ship, required=True),
        Field("role", "Role", "text", existing.role if existing else "", hint="What the build is for, for example Exploration or Mining."),
        # Editable: the common build sites are offered, but a commander using another can type its name.
        Field("site", "Site", "combo", existing.site if existing else KNOWN_SITES[0], values=list(KNOWN_SITES), required=True),
        Field("url", "Link", "text", existing.url if existing else "", required=True, hint="The build's web address, starting with http:// or https://"),
        Field("notes", "Notes", "text", existing.notes if existing else ""),
    ]


def build_ship(values: Dict[str, str], existing: Optional[ShipBuild] = None) -> ShipBuild:
    """The ShipBuild the typed `values` describe (an edit keeps the id and dates). ValueError, with a message to show, when something is missing or wrong."""
    name, ship, site, url = (values[key].strip() for key in ("name", "ship", "site", "url"))
    if not name or not ship or not site or not url:
        raise ValueError("Name, Ship, Site and Link are required.")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("The link must start with http:// or https://")
    role, notes = values["role"].strip(), values["notes"].strip()
    if existing is not None:
        return ShipBuild(id=existing.id, ship=ship, name=name, site=site, url=url, role=role, notes=notes, created=existing.created, updated=existing.updated)
    return ShipBuild(id=new_id(), ship=ship, name=name, site=site, url=url, role=role, notes=notes)


def open_ship_build_dialog(parent: tk.Misc, on_save: Callable[[ShipBuild], None], existing: Optional[ShipBuild] = None, prefill_ship: str = "") -> None:
    """Opens the Add/Edit Ship Build window. `existing` fills every field for an edit; otherwise `prefill_ship` seeds a blank form with the ship being flown. Calls `on_save(build)` once the form
    checks out and Save is pressed, never when it is cancelled."""
    def submit(values: Dict[str, str]) -> Optional[str]:
        try:
            build = build_ship(values, existing)
        except ValueError as problem:
            return str(problem)
        on_save(build)
        return None

    FormDialog(parent.winfo_toplevel(), "Edit Ship Build" if existing else "Add Ship Build", fields_for(existing, prefill_ship), submit)
