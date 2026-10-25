"""FormDialog: the window kit's form. Labeled fields in one column under optional section headings, an error line, and Save and Cancel, in the same window chrome as every other WFMT window.

The old add/edit dialogs were plain Toplevels with a fixed grid; this replaces them with one shared layout. A field is a `Field`:

- `kind="text"`: a one-line entry. `kind="system"`: the same, with system-name suggestions. `kind="choice"`: a dropdown that only offers `values` (and an empty choice when `allow_blank`).
  `kind="combo"`: a dropdown that offers `values` but takes any typed text. `kind="commodity"`: a one-line entry with commodity-name suggestions as you type (`values` are the names to lead with). `kind="section"`: no input, a heading that groups the fields under it (`label` is its text).
- `required` puts a mark after the label; the check itself is the submit function's, so its message can say what is wrong.

`submit(values)` gets every field's text by key and returns an error message to show, or None when it took the values, which closes the window. Enter submits, Escape closes. The window hangs off the
caller's toplevel (never a frame the panel rebuilds), is transient for it, and takes the keyboard focus for its first field. Pure presentation: validation and what is saved are the caller's.
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Sequence

from . import palette as P
from . import style
from .shell import WindowShell
from .widgets import Combobox, FlatButton, NoteLabel

LABEL_PX = 130          # the label column, so every field's box starts at the same place
ROW_PX = 38             # a height per field, for sizing the window to its fields
HINT_PX = 20
SECTION_PX = 34
CHROME_PX = 110         # the title, the error line and the buttons


@dataclass
class Field:
    key: str
    label: str
    kind: str = "text"
    value: str = ""
    values: Sequence[str] = ()
    required: bool = False
    allow_blank: bool = True
    hint: str = ""


class FormDialog:
    def __init__(self, parent: tk.Misc, title: str, fields: Sequence[Field], submit: Callable[[Dict[str, str]], Optional[str]],
                 subtitle: str = "", save_text: str = "Save", width: int = 560) -> None:
        self._submit = submit
        self._fit_pending = False
        self._fields = list(fields)
        self._vars: Dict[str, tk.StringVar] = {}
        height = CHROME_PX + sum(SECTION_PX if f.kind == "section" else ROW_PX + (HINT_PX if f.hint else 0) for f in self._fields)
        self._shell = WindowShell(parent, title, subtitle, size=(width, height), min_size=(width - 120, min(height, 420)))
        window = self._shell.window
        window.transient(parent)
        window.resizable(True, False)
        body = self._shell.body
        body.columnconfigure(1, weight=1)
        first: Optional[tk.Widget] = None
        row = 0
        for field in self._fields:
            if field.kind == "section":
                tk.Label(body, text=field.label.upper(), fg=P.ACCENT, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD)).grid(
                    row=row, column=0, columnspan=2, sticky="w", pady=(P.PAD if row else 0, P.PAD_SM))
                row += 1
                continue
            label = field.label + (" *" if field.required else "")
            tk.Label(body, text=label, fg=P.MUTED, bg=P.BG, anchor="w", width=LABEL_PX // 8).grid(row=row, column=0, sticky="w", padx=(0, P.PAD), pady=3)
            var = tk.StringVar(value=field.value)
            self._vars[field.key] = var
            widget = self._input(body, field, var)
            widget.grid(row=row, column=1, sticky="ew", pady=3)
            if first is None:
                first = widget
            row += 1
            if field.hint:
                NoteLabel(body, field.hint, fg=P.FAINT, bg=P.BG, font=P.FONT_SMALL, padx=0).grid(row=row, column=1, sticky="ew")
                row += 1
        self._error = NoteLabel(body, fg=P.DANGER, bg=P.BG, padx=0)
        self._error.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(P.PAD_SM, 0))
        buttons = tk.Frame(body, bg=P.BG)
        buttons.grid(row=row + 1, column=0, columnspan=2, sticky="e", pady=(P.PAD_SM, 0))
        FlatButton(buttons, save_text, self.submit, kind="accent").pack(side="left")
        FlatButton(buttons, "Cancel", self.close).pack(side="left", padx=(6, 0))
        window.bind("<Return>", lambda _e: self.submit())
        window.bind("<Configure>", lambda e: self._later_fit() if e.widget is window else None)
        if first is not None:
            window.after(60, first.focus_set)

    @staticmethod
    def _input(parent: tk.Misc, field: Field, var: tk.StringVar) -> tk.Widget:
        if field.kind == "choice":
            values = ([""] if field.allow_blank else []) + list(field.values)
            return Combobox(parent, textvariable=var, values=values, state="readonly", width=24)
        if field.kind == "combo":
            return Combobox(parent, textvariable=var, values=list(field.values), width=24)
        entry = tk.Entry(parent, textvariable=var, width=24)
        if field.kind == "system":
            from .. import system_autocomplete
            system_autocomplete.attach(entry, var)
        elif field.kind == "commodity":
            from .. import commodity_autocomplete
            commodity_autocomplete.attach(entry, var, lambda: field.values)
        return entry

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    @property
    def window(self) -> tk.Toplevel:
        return self._shell.window

    def values(self) -> Dict[str, str]:
        return {key: var.get() for key, var in self._vars.items()}

    def set_error(self, text: str) -> None:
        self._error.configure(text=text)
        self._later_fit()

    def _later_fit(self) -> None:
        """The window is not resizable up and down, so when hints or the error line wrap onto more lines (a narrow window, a long message) it grows to hold them. Waits a moment for the notes to re-wrap."""
        if self._fit_pending or not self.alive:
            return
        self._fit_pending = True
        self._shell.window.after(60, self._fit_height)

    def _fit_height(self) -> None:
        self._fit_pending = False
        if not self.alive:
            return
        window = self._shell.window
        window.update_idletasks()
        needed = window.winfo_reqheight()
        if needed > window.winfo_height() + 1:
            window.geometry(f"{window.winfo_width()}x{needed}")

    def submit(self) -> None:
        """Hand the values to the caller; show its error, or close when it took them."""
        message = self._submit(self.values())
        if message:
            self.set_error(message)
            return
        self.close()

    def close(self) -> None:
        self._shell.close()


def blank_to_none(text: str) -> Optional[str]:
    return text.strip() or None


def parse_optional_int(text: str, name: str, low: Optional[int] = None, high: Optional[int] = None) -> Optional[int]:
    """A whole number from a text box, None when blank; ValueError with a message naming `name` when it is not one, or outside low..high."""
    text = text.strip()
    if not text:
        return None
    try:
        number = int(text)
    except ValueError:
        raise ValueError(f"{name} must be a whole number (or left blank).")
    if (low is not None and number < low) or (high is not None and number > high):
        raise ValueError(f"{name} must be {low} to {high} (or left blank).")
    return number


def parse_optional_float(text: str, name: str) -> Optional[float]:
    text = text.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"{name} must be a number (or left blank).")
