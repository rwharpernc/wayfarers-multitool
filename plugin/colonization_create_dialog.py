"""The "Create Raven Colonial project" dialog: what the commander confirms before WFMT starts a project for the selected site (see
rcc_create.py for what is then sent). Modal over the Colonization Sites window, built on the shared window kit (plugin/uikit); every
field is bounded, so the dialog never grows with what is typed in it.

`ask` returns a `Choices` (the commander's answers) or None when cancelled. The values are only read here, never sent: the caller
validates and sends.
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import List, Optional, Sequence

from . import rcc_client, rcc_create
from .uikit import palette as P, style
from .uikit.widgets import Combobox, FlatButton, clip

_WIDTH_CHARS = 44
_LABEL_CHARS = 56
_NEW = rcc_create.NEW_SITE


@dataclass
class Choices:
    planned: Optional[rcc_client.RccSite]
    name: str
    build_type: str
    body_num: str
    architect: str
    notes: str
    due: str
    primary_port: bool
    make_primary: bool
    fleet_carrier: bool


def _planned_label(site: rcc_client.RccSite) -> str:
    return clip(f"{site.name} - {site.type_label or 'type not set'}" + (f" (body {site.body_num})" if site.body_num is not None else ""), _LABEL_CHARS)


def ask(parent: tk.Misc, system: str, name: str, planned: Sequence[rcc_client.RccSite], guess: Optional[rcc_client.RccSite],
        architect: str, can_attach_carrier: bool, locked_note: str = "") -> Optional[Choices]:
    """Show the dialog. `planned` are the plan's unbuilt sites, `guess` the one that matches `name` (preselected), `locked_note` a line
    to show when Raven says the system is locked to someone else."""
    types: List[rcc_create.BuildChoice] = rcc_create.build_choices()
    type_labels = [rcc_create.choice_label(c) for c in types]
    planned_labels = {_planned_label(s): s for s in planned}
    top = parent.winfo_toplevel()
    window = tk.Toplevel(parent)
    window.withdraw()
    answer: List[Optional[Choices]] = [None]
    try:
        style.skin(window)
        window.title("Create Raven Colonial project")
        window.configure(bg=P.BG)
        window.resizable(False, False)

        planned_var = tk.StringVar(master=window, value=_planned_label(guess) if guess else _NEW)
        name_var = tk.StringVar(master=window, value=name)
        type_var = tk.StringVar(master=window, value="")
        body_var = tk.StringVar(master=window, value="")
        architect_var = tk.StringVar(master=window, value=architect)
        notes_var = tk.StringVar(master=window, value="")
        due_var = tk.StringVar(master=window, value="")
        port_var = tk.BooleanVar(master=window, value=False)
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

        picker = Combobox(body, textvariable=planned_var, values=[_NEW] + list(planned_labels), state="readonly", width=_WIDTH_CHARS - 4)
        line("Plan entry", picker)
        line("Name", entry(name_var, rcc_create.NAME_MAX))
        type_box = Combobox(body, textvariable=type_var, values=type_labels, state="readonly", width=_WIDTH_CHARS - 4)
        line("Building", type_box)
        body_entry = entry(body_var, 3)
        line("Body number", body_entry)
        line("Architect", entry(architect_var, rcc_create.NAME_MAX))
        line("Notes", entry(notes_var, rcc_create.NOTES_MAX))
        line("Due (YYYY-MM-DD)", entry(due_var, 10))

        def on_plan_choice(_event: object = None) -> None:
            site = planned_labels.get(planned_var.get())
            if site is None:
                body_entry.configure(state="normal")
                return
            name_var.set(site.name)
            body_var.set("" if site.body_num is None else str(site.body_num))
            body_entry.configure(state="disabled")
            for index, choice in enumerate(types):
                if choice.key == site.build_type.strip().casefold():
                    type_var.set(type_labels[index])
                    break

        picker.bind("<<ComboboxSelected>>", on_plan_choice)
        on_plan_choice()

        for text, variable in (("This is the system's primary port", port_var), ("Make it my primary project", primary_var)):
            tk.Checkbutton(body, text=text, variable=variable, fg=P.TEXT, bg=P.BG, selectcolor=P.CARD, activebackground=P.BG,
                           activeforeground=P.TEXT, anchor="w").grid(row=row[0], column=0, columnspan=2, sticky="w")
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
                chosen = next((c for c, label in zip(types, type_labels) if label == type_var.get()), None)
                if chosen is None:
                    error_var.set("Choose what is being built.")
                    return
                try:
                    rcc_create.parse_due(due_var.get())
                    rcc_create.parse_body_num(body_var.get())
                except ValueError:
                    error_var.set("The due date must look like 2026-12-31, and the body number must be a whole number.")
                    return
                answer[0] = Choices(planned_labels.get(planned_var.get()), name_var.get().strip(), chosen.key, body_var.get().strip(),
                                    architect_var.get().strip(), notes_var.get().strip(), due_var.get().strip(), port_var.get(),
                                    primary_var.get(), carrier_var.get() and can_attach_carrier)
            window.destroy()

        buttons = tk.Frame(window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD)
        buttons.pack(fill="x")
        FlatButton(buttons, "Create", lambda: finish(True), kind="accent").pack(side="right", padx=(P.PAD_SM, 0))
        FlatButton(buttons, "Cancel", lambda: finish(False)).pack(side="right")
        window.bind("<Escape>", lambda _e: finish(False))
        window.protocol("WM_DELETE_WINDOW", lambda: finish(False))

        window.update_idletasks()
        try:
            x = top.winfo_rootx() + max(0, (top.winfo_width() - window.winfo_reqwidth()) // 2)
            y = top.winfo_rooty() + max(0, (top.winfo_height() - window.winfo_reqheight()) // 3)
            window.geometry(f"+{x}+{y}")
            if top.winfo_viewable():
                window.transient(top)
        except tk.TclError:
            pass
        window.deiconify()
        window.lift()
        style.grab_when_visible(window)
    except tk.TclError:
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
