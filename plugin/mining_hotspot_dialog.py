"""The Add/Edit Hotspot window, shared by the Surface Mining page's live window (+H.S.), the Surface Mining Book and the Settings tab's hotspot list (`mining_hotspot_settings.py`). The same fields and
checks either way: only the prefilled values and the save callback differ.

Built on the shared form (`uikit/form.py`): fields grouped under Where, Deposit and Filing, one error line, Save and Cancel. What the form means is here and testable without a window: `build_hotspot`
turns the typed text into a `Hotspot` or says what is wrong, and writes the material in the one spelling the books use (`mining_names.normalize`, so `painite` and `Painite` are the same material).
"""
import tkinter as tk
from typing import Callable, Dict, List, Optional, Sequence

from . import mining_deposit
from . import mining_spansh_client
from .mining_hotspots import Hotspot, hotspot_repository
from .mining_names import normalize
from .uikit.form import Field, FormDialog, blank_to_none, parse_optional_float, parse_optional_int


def preferred_materials() -> List[str]:
    """The names the Contains box suggests first: the materials of the deposits already saved, then the commodities Mining mode knows."""
    return list(dict.fromkeys(list(hotspot_repository.materials()) + list(mining_spansh_client.KNOWN_MINING_COMMODITIES)))


def fields_for(existing: Optional[Hotspot], prefill_system: str = "", prefill_body: str = "", prefill_latitude: Optional[float] = None,
               prefill_longitude: Optional[float] = None, folders: Optional[List[str]] = None, materials: Optional[Sequence[str]] = None) -> List[Field]:
    """The form's fields, filled from `existing` when editing, else from the `prefill_*` values (the commander's current system, body and spot)."""
    latitude = existing.latitude if existing else prefill_latitude
    longitude = existing.longitude if existing else prefill_longitude

    def text(value: object) -> str:
        return "" if value is None else str(value)

    return [
        Field("", "Where", "section"),
        Field("system", "System", "system", existing.system if existing else prefill_system, required=True),
        Field("body", "Body", "text", existing.body if existing else prefill_body, required=True),
        Field("latitude", "Latitude", "text", text(latitude)),
        Field("longitude", "Longitude", "text", text(longitude)),
        Field("", "Deposit", "section"),
        Field("material", "Contains", "commodity", existing.material if existing else "", values=list(materials or []), required=True,
              hint="The commodity the deposit holds, for example Painite. Suggestions follow what you type."),
        Field("rigs", "Rigs", "text", text(existing.rigs if existing else None), hint=f"How many mining rigs it takes, 1 to {mining_deposit.MAX_RIGS}."),
        Field("signal_number", "Signal number", "text", text(existing.signal_number if existing else None)),
        # Only the readouts the scanner itself shows are offered: any other text would silently drop out of the tons-left estimate.
        Field("amount", "Amount", "choice", existing.amount if existing and existing.amount else "", values=mining_deposit.AMOUNTS),
        Field("density", "Density", "choice", existing.density if existing and existing.density else "", values=mining_deposit.DENSITIES),
        Field("", "Filing", "section"),
        # Editable: the folders you have are offered, and typing a name that does not exist yet makes that folder (there is no separate "new folder" action).
        Field("folder", "Folder", "combo", existing.folder if existing else "", values=list(folders or [])),
        Field("notes", "Notes", "text", existing.notes if existing else ""),
    ]


def build_hotspot(values: Dict[str, str], existing: Optional[Hotspot] = None) -> Hotspot:
    """The Hotspot the typed `values` describe, keeping what an edit does not touch (the mined tons and the ground). ValueError, with a message to show, when something is missing or wrong."""
    system, body, material = values["system"].strip(), values["body"].strip(), normalize(values["material"])
    if not system or not body or not material:
        raise ValueError("System, Body and Contains are required.")
    rigs = parse_optional_int(values["rigs"], "Rigs", 1, mining_deposit.MAX_RIGS)
    return Hotspot(system=system, body=body, material=material, notes=values["notes"].strip(),
                   latitude=parse_optional_float(values["latitude"], "Latitude"), longitude=parse_optional_float(values["longitude"], "Longitude"),
                   folder=values["folder"].strip(), rigs=rigs, signal_number=parse_optional_int(values["signal_number"], "Signal number"),
                   amount=blank_to_none(values["amount"]), density=blank_to_none(values["density"]),
                   mined_tons=existing.mined_tons if existing else None, ground=existing.ground if existing else None)


def open_hotspot_dialog(
    parent: tk.Misc,
    on_save: Callable[[Hotspot], None],
    existing: Optional[Hotspot] = None,
    prefill_system: str = "",
    prefill_body: str = "",
    prefill_latitude: Optional[float] = None,
    prefill_longitude: Optional[float] = None,
) -> None:
    """Opens the Add/Edit Hotspot window. `existing` fills every field for an edit; otherwise the `prefill_*` values seed a blank form. Calls `on_save(hotspot)` once the form checks out and Save is
    pressed, never when it is cancelled. Parented on the caller's toplevel, not on a frame the panel rebuilds every second (which would take the window with it)."""
    def submit(values: Dict[str, str]) -> Optional[str]:
        try:
            hotspot = build_hotspot(values, existing)
        except ValueError as problem:
            return str(problem)
        on_save(hotspot)
        return None

    FormDialog(parent.winfo_toplevel(), "Edit Hotspot" if existing else "Add Hotspot",
               fields_for(existing, prefill_system, prefill_body, prefill_latitude, prefill_longitude, hotspot_repository.folders(), preferred_materials()), submit)
