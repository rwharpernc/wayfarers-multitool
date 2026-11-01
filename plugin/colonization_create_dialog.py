"""The "Create Raven Colonial project" dialog: what the commander confirms before WFMT starts a project for the selected site (see
rcc_create.py for what is then sent). Modal over the Colonization Sites window, built on the shared window kit (plugin/uikit); every
field is bounded, so the dialog never grows with what is typed in it.

The building is chosen in three steps, as on Raven Colonial: where it goes (orbital or surface), which building (by tier and the
game's name), then its **layout**, the exact build type Raven knows it by (`vulcan`, `dual_truss`, ...). The layout is what is sent,
so it is always shown as it is written. A planned site chosen from the plan fills in all three.

`ask` returns a `Choices` (the commander's answers) or None when cancelled. The values are only read here, never sent: the caller
validates and sends.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from config import appname

from . import rcc_client, rcc_create
from .uikit import dialogs, palette as P, style
from .uikit.widgets import Combobox, FlatButton, clip

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")
_WIDTH_CHARS = 44
_LABEL_CHARS = 56
_NO_PLAN = rcc_create.NO_PLAN_ENTRY
_NO_BODY = "Unknown"
_LOCATION_LABELS = {"orbital": "Orbital", "surface": "Surface"}


@dataclass
class Choices:
    planned: Optional[rcc_client.RccSite]
    name: str
    build_type: str                  # the layout, as Raven writes it
    body_num: Optional[int]
    body_name: str
    architect: str
    notes: str
    due: str
    primary_port: bool
    make_primary: bool
    fleet_carrier: bool


def _planned_label(site: rcc_client.RccSite) -> str:
    return clip(f"{site.name} ({site.build_type or 'type not set'})", _LABEL_CHARS)


def _body_label(body: rcc_client.RccBody) -> str:
    return clip(f"{body.name} ({body.kind})" if body.kind else body.name, _LABEL_CHARS)


def ask(parent: tk.Misc, system: str, name: str, planned: Sequence[rcc_client.RccSite], guess: Optional[rcc_client.RccSite],
        architect: str, can_attach_carrier: bool, bodies: Sequence[rcc_client.RccBody] = (), primary_port: bool = False,
        locked_note: str = "", primary_exists: str = "") -> Optional[Choices]:
    """Show the dialog. `planned` are the plan's unbuilt sites, `guess` the one preselected, `bodies` the system's bodies (for the body
    choice), `primary_port` whether the site is the system's colonization ship, `locked_note` a line to show when Raven says the system
    is locked to someone else, `primary_exists` the reason the system already has a primary port ("" when nothing shows one): the primary port tick is then
    off and cannot be set."""
    buildings: Dict[str, List[rcc_create.BuildChoice]] = {loc: rcc_create.choices_at(loc) for loc in rcc_create.LOCATIONS}
    planned_labels = {_planned_label(s): s for s in planned}
    body_labels = {_body_label(b): b for b in bodies}
    top = parent.winfo_toplevel()
    window = tk.Toplevel(parent)
    window.withdraw()
    answer: List[Optional[Choices]] = [None]
    try:
        style.skin(window)
        window.title("Create Raven Colonial project")
        window.configure(bg=P.BG)
        window.resizable(False, False)

        planned_var = tk.StringVar(master=window, value=_planned_label(guess) if guess else _NO_PLAN)
        name_var = tk.StringVar(master=window, value=name)
        location_var = tk.StringVar(master=window, value=_LOCATION_LABELS["orbital"])
        building_var = tk.StringVar(master=window, value="")
        layout_var = tk.StringVar(master=window, value="")
        body_var = tk.StringVar(master=window, value=_NO_BODY)
        architect_var = tk.StringVar(master=window, value=architect)
        notes_var = tk.StringVar(master=window, value="")
        due_var = tk.StringVar(master=window, value="")
        port_var = tk.BooleanVar(master=window, value=primary_port and not primary_exists)
        primary_var = tk.BooleanVar(master=window, value=True)
        carrier_var = tk.BooleanVar(master=window, value=can_attach_carrier)
        error_var = tk.StringVar(master=window, value="")

        body = tk.Frame(window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD * 2)
        body.pack(fill="x")
        tk.Label(body, text=clip(f"Start a project for this site in {system}", 70), fg=P.TEXT, bg=P.BG, anchor="w",
                 font=style.font(P.FONT_SECTION)).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(body, text="Only what you confirm here, the site's depot figures and your Raven key are sent to Raven Colonial.",
                 fg=P.MUTED, bg=P.BG, anchor="w", justify="left", wraplength=520).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, P.PAD))
        row = [2]

        def line(caption: str, widget: tk.Widget) -> None:
            tk.Label(body, text=caption, fg=P.MUTED, bg=P.BG, anchor="w").grid(row=row[0], column=0, sticky="w", padx=(0, P.PAD), pady=2)
            widget.grid(row=row[0], column=1, sticky="w", pady=2)
            row[0] += 1

        def entry(variable: tk.StringVar, limit: int) -> tk.Entry:
            field = tk.Entry(body, textvariable=variable, width=_WIDTH_CHARS)
            variable.trace_add("write", lambda *_: variable.set(variable.get()[:limit]) if len(variable.get()) > limit else None)
            return field

        def combo(variable: tk.StringVar, values: Sequence[str]) -> Combobox:
            return Combobox(body, textvariable=variable, values=list(values), state="readonly", width=_WIDTH_CHARS - 4)

        picker = combo(planned_var, [_NO_PLAN] + list(planned_labels))
        line("Plan entry", picker)
        line("Name", entry(name_var, rcc_create.NAME_MAX))
        location_box = combo(location_var, list(_LOCATION_LABELS.values()))
        line("Location", location_box)
        building_box = combo(building_var, [])
        line("Building", building_box)
        layout_box = combo(layout_var, [])
        line("Layout (build type)", layout_box)
        body_box = combo(body_var, [_NO_BODY] + list(body_labels))
        line("Body", body_box)
        line("Architect", entry(architect_var, rcc_create.NAME_MAX))
        line("Notes", entry(notes_var, rcc_create.NOTES_MAX))
        line("Due (YYYY-MM-DD)", entry(due_var, 10))

        def location() -> str:
            return next((k for k, v in _LOCATION_LABELS.items() if v == location_var.get()), "orbital")

        def current_building() -> Optional[rcc_create.BuildChoice]:
            return next((c for c in buildings[location()] if rcc_create.choice_label(c) == building_var.get()), None)

        def on_location(_event: object = None) -> None:
            building_box.configure(values=[rcc_create.choice_label(c) for c in buildings[location()]])
            building_var.set("")
            layout_var.set("")
            layout_box.configure(values=[])

        def on_building(_event: object = None) -> None:
            choice = current_building()
            layout_box.configure(values=list(choice.layouts) if choice else [])
            layout_var.set(choice.layouts[0] if choice else "")

        def on_plan(_event: object = None) -> None:
            site = planned_labels.get(planned_var.get())
            if site is None:
                return
            name_var.set(site.name)
            choice = rcc_create.choice_for_layout(site.build_type)
            if choice is not None:
                location_var.set(_LOCATION_LABELS[choice.location])
                on_location()
                building_var.set(rcc_create.choice_label(choice))
                on_building()
                layout_var.set(next((x for x in choice.layouts if x.casefold() == site.build_type.strip().casefold()), choice.layouts[0]))
            match = next((label for label, b in body_labels.items() if b.num == site.body_num), None)
            body_var.set(match or _NO_BODY)

        location_box.bind("<<ComboboxSelected>>", on_location)
        building_box.bind("<<ComboboxSelected>>", on_building)
        picker.bind("<<ComboboxSelected>>", on_plan)
        on_location()
        on_plan()

        for text, variable in (("This is the system's primary port", port_var), ("Make it my primary project", primary_var)):
            tk.Checkbutton(body, text=text, variable=variable, fg=P.TEXT, bg=P.BG, selectcolor=P.CARD, activebackground=P.BG,
                           activeforeground=P.TEXT, anchor="w",
                           state="disabled" if (variable is port_var and primary_exists) else "normal").grid(row=row[0], column=0, columnspan=2, sticky="w")
            row[0] += 1
            if variable is port_var and primary_exists:
                tk.Label(body, text=clip(primary_exists, 200), fg=P.MUTED, bg=P.BG, anchor="w", justify="left",
                         wraplength=520).grid(row=row[0], column=0, columnspan=2, sticky="w", padx=(P.PAD, 0))
                row[0] += 1
        carrier_check = tk.Checkbutton(body, text="Attach my fleet carrier", variable=carrier_var, fg=P.TEXT, bg=P.BG, selectcolor=P.CARD,
                                       activebackground=P.BG, activeforeground=P.TEXT, anchor="w",
                                       state="normal" if can_attach_carrier else "disabled")
        carrier_check.grid(row=row[0], column=0, columnspan=2, sticky="w")
        row[0] += 1
        if not can_attach_carrier:
            tk.Label(body, text="(WFMT has not seen your carrier's id this session; log in again or open Carrier Management once.)",
                     fg=P.MUTED, bg=P.BG, anchor="w", justify="left", wraplength=520).grid(row=row[0], column=0, columnspan=2, sticky="w")
            row[0] += 1
        if locked_note:
            tk.Label(body, text=clip(locked_note, 160), fg=P.WARN, bg=P.BG, anchor="w", justify="left",
                     wraplength=520).grid(row=row[0], column=0, columnspan=2, sticky="w", pady=(P.PAD_SM, 0))
            row[0] += 1
        tk.Label(body, textvariable=error_var, fg=P.DANGER, bg=P.BG, anchor="w", justify="left",
                 wraplength=520).grid(row=row[0], column=0, columnspan=2, sticky="w", pady=(P.PAD_SM, 0))

        def finish(accept: bool) -> None:
            if accept:
                layout = layout_var.get().strip()
                if not layout:
                    error_var.set("Choose the building and its layout.")
                    return
                try:
                    rcc_create.parse_due(due_var.get())
                except ValueError:
                    error_var.set("The due date must look like 2026-12-31.")
                    return
                chosen_body = body_labels.get(body_var.get())
                answer[0] = Choices(planned_labels.get(planned_var.get()), name_var.get().strip(), layout,
                                    chosen_body.num if chosen_body else None, chosen_body.name if chosen_body else "",
                                    architect_var.get().strip(), notes_var.get().strip(), due_var.get().strip(), port_var.get(),
                                    primary_var.get(), carrier_var.get() and can_attach_carrier)
            window.destroy()

        buttons = tk.Frame(window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD)
        buttons.pack(fill="x")
        FlatButton(buttons, "Create", lambda: finish(True), kind="accent",
                   tip="Create - start the project on Raven Colonial with these choices (nothing is sent before this)").pack(side="right", padx=(P.PAD_SM, 0))
        FlatButton(buttons, "Cancel", lambda: finish(False), tip="Cancel - close this window without creating anything").pack(side="right")
        window.bind("<Escape>", lambda _e: finish(False))
        window.protocol("WM_DELETE_WINDOW", lambda: finish(False))

        dialogs._center(window, top)    # sized to its content, never past the screen, and over `top` (or the screen)
        try:
            if top.winfo_viewable():
                window.transient(top)
        except tk.TclError:
            pass
        window.deiconify()
        window.lift()
        style.grab_when_visible(window)
        window.update_idletasks()
        logger.info("Create project dialog shown: geometry %s, wanted %dx%d, screen %dx%d, viewable %s", window.winfo_geometry(),
                    window.winfo_reqwidth(), window.winfo_reqheight(), window.winfo_screenwidth(), window.winfo_screenheight(),
                    window.winfo_viewable())
    except tk.TclError:
        logger.exception("The Create Raven Colonial project dialog could not be built")
        try:
            window.destroy()
        except tk.TclError:
            pass
        return None
    try:
        window.wait_window()
    except tk.TclError:
        pass
    return answer[0]
