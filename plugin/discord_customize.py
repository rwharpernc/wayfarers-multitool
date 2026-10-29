"""
The Customize Discord posts dialog: choose how the BGS report and Powerplay progress look when they are copied for Discord or posted, with a live preview and templates you save.

One window with a report choice at the top (BGS Report or Powerplay progress). For each report it shows a template choice (the built-in presets Standard, Compact, Detailed
and Plain, then your own), checkboxes for which parts of the post appear, and a preview of the post made from your current data (made-up example data when there is none yet),
with how many characters and messages it comes to. Choosing a template makes it the one Copy for Discord and Post to Discord use for that report; changing a checkbox only changes
the preview until you press Save (over one of your own templates) or Save as (a new name, since the presets cannot be changed). Rename and Delete act on your own templates.

The templates and the choice are kept by `discord_templates.py`, and the text is written by `bgs_discord.py` and `powerplay_discord.py`; nothing here sends anything. The BGS Report
and Powerplay Sessions windows register where to get their current data (`register_data`) while they are open, and the preview uses it.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from tkinter import font as tkfont
from typing import Any, Callable, Dict, List, Optional, Tuple

from config import appname, config

from . import bgs_discord, discord_preview, discord_templates as T, powerplay_discord
from .uikit import dialogs
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.widgets import Combobox, FlatButton

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_discord_customize_geometry"
DEFAULT_SIZE = (860, 780)
MIN_SIZE = (720, 640)

HELP = (
    ("Templates", "Standard, Compact, Detailed and Plain are built in and cannot be changed. Change the checkboxes, then Save as to keep your version under a name of your own."),
    ("Which one is used", "The template shown in the box is the one Copy for Discord and Post to Discord use for that report. Choosing one in the box switches to it at once."),
    ("Preview", "Made from your current tick or session, or from made-up example data when there is none yet. Discord's own display is the truth; this is close."),
    ("Limits", "Discord allows 2,000 characters in a message, so a long report is several messages. Names are always escaped, and no setting can make a post ping anyone."),
)

_providers: Dict[str, Callable[[], Optional[tuple]]] = {}      # report -> where to get the current data: (view, current system, pinned) or (rows, power, cycle line)
_window: Optional["CustomizeWindow"] = None


def register_data(report: str, provider: Callable[[], Optional[tuple]]) -> None:
    """A report window says where its current data is, so the preview can use it while the window is open."""
    _providers[report] = provider


def unregister_data(report: str, provider: Callable[[], Optional[tuple]]) -> None:
    if _providers.get(report) is provider:
        del _providers[report]


def render(report: str, options: Dict[str, Any]) -> Tuple[List[str], bool]:
    """(the post's messages with these options, whether they were made from example data). Real data is used when the report's window gave some and it makes a post."""
    data = None
    provider = _providers.get(report)
    if provider is not None:
        try:
            data = provider()
        except Exception as err:      # a preview must never break the window it is opened from
            logger.error("Could not read the data for the Discord preview (%s)", type(err).__name__)
    if report == T.BGS:
        if data:
            messages = bgs_discord.report_messages(data[0], data[1], data[2], options)
            if messages:
                return messages, False
        return bgs_discord.report_messages(bgs_discord.sample_view(), "Example System", [], options), True
    if data:
        messages = powerplay_discord.progress_messages(data[0], data[1], data[2], options)
        if messages:
            return messages, False
    return powerplay_discord.progress_messages(powerplay_discord.sample_rows(), powerplay_discord.SAMPLE_POWER, powerplay_discord.SAMPLE_CYCLE_LINE, options), True


def show(parent: tk.Misc, report: str = T.BGS) -> "CustomizeWindow":
    """Open the dialog on `report`, or raise it if it is already open."""
    global _window
    if _window is not None and _window.alive:
        _window.select_report(report)
        _window.lift()
        return _window
    _window = CustomizeWindow(parent, report if report in T.REPORTS else T.BGS)
    return _window


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


class CustomizeWindow:
    def __init__(self, parent: tk.Misc, report: str) -> None:
        self._report = report
        self._loaded: T.Template = T.templates.chosen(report)
        self._vars: Dict[str, tk.Variable] = {}
        self._shell = WindowShell(parent, "Customize Discord posts", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
                                  load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
                                  save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Customize Discord posts help", HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._toplevel = self._shell.window
        self._shell.add_action("Done", self.close, accent=True)

        body = self._shell.body
        top = tk.Frame(body, bg=P.BG)
        top.pack(fill="x", pady=(P.PAD_SM, P.PAD_SM))
        tk.Label(top, text="Report", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._report_var = tk.StringVar(value=T.REPORT_LABELS[report])
        self._report_box = Combobox(top, textvariable=self._report_var, state="readonly", width=20, values=[T.REPORT_LABELS[r] for r in T.REPORTS])
        self._report_box.pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._report_box.bind("<<ComboboxSelected>>", lambda _e: self._on_report_picked())
        tk.Label(top, text="Template", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._template_var = tk.StringVar(value=self._loaded.name)
        self._template_box = Combobox(top, textvariable=self._template_var, state="readonly", width=22, values=T.templates.names(report))
        self._template_box.pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._template_box.bind("<<ComboboxSelected>>", lambda _e: self._on_template_picked())

        buttons = tk.Frame(body, bg=P.BG)
        buttons.pack(fill="x", pady=(0, P.PAD_SM))
        for text, command, kind in (("Save", self._on_save, "normal"), ("Save as…", self._on_save_as, "normal"), ("Rename…", self._on_rename, "normal"),
                                    ("Delete", self._on_delete, "danger")):
            FlatButton(buttons, text, command, kind=kind).pack(side="left", padx=(0, 6))
        self._note = tk.Label(body, text="", fg=P.MUTED, bg=P.BG, anchor="w", justify="left", wraplength=780)
        self._note.pack(fill="x", pady=(0, P.PAD_SM))

        self._options_host = tk.Frame(body, bg=P.PANE, padx=P.PAD, pady=P.PAD)
        self._options_host.pack(fill="x", pady=(0, P.PAD_SM))
        self._count = tk.Label(body, text="", fg=P.MUTED, bg=P.BG, anchor="w")
        self._count.pack(fill="x")
        preview_host = tk.Frame(body, bg=P.CARD, highlightthickness=1, highlightbackground=P.LINE)
        preview_host.pack(fill="both", expand=True, pady=(2, P.PAD_SM))
        self._text = tk.Text(preview_host, wrap="word", relief="flat", bd=0, bg=P.CARD, fg=P.TEXT, insertbackground=P.TEXT, highlightthickness=0,
                             padx=10, pady=8, height=12, font=style.font(P.FONT_BODY), cursor="arrow")
        scroll = tk.Scrollbar(preview_host, command=self._text.yview)
        self._text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._text.pack(side="left", fill="both", expand=True)
        self._configure_tags()
        self._build_options()
        self._refresh()

    # --- lifecycle ----------------------------------------------------------------------------------------------
    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._toplevel.deiconify()
        self._toplevel.lift()

    def close(self) -> None:
        global _window
        self._shell.close()
        if _window is self:
            _window = None

    def select_report(self, report: str) -> None:
        if report in T.REPORTS and report != self._report:
            self._report_var.set(T.REPORT_LABELS[report])
            self._on_report_picked()

    # --- building -----------------------------------------------------------------------------------------------
    def _configure_tags(self) -> None:
        base = style.font(P.FONT_BODY)
        bold = tkfont.Font(font=base)
        bold.configure(weight="bold")
        italic = tkfont.Font(font=base)
        italic.configure(slant="italic")
        self._text.tag_configure("bold", font=bold)
        self._text.tag_configure("italic", font=italic)
        self._text.tag_configure("link", foreground=P.INFO, underline=True)
        self._text.tag_configure("meta", foreground=P.MUTED)

    def _build_options(self) -> None:
        """The checkboxes of the report shown (and, for the BGS report, the choice of which systems), set from the template that is loaded."""
        for child in self._options_host.winfo_children():
            child.destroy()
        self._vars = {}
        options = self._loaded.options
        for index, (key, label) in enumerate(T.TOGGLES[self._report]):
            var = tk.BooleanVar(master=self._toplevel, value=bool(options.get(key)))
            self._vars[key] = var
            tk.Checkbutton(self._options_host, text=label, variable=var, command=self._on_changed, bg=P.PANE, fg=P.TEXT, selectcolor=P.CARD,
                           activebackground=P.PANE, activeforeground=P.TEXT, highlightthickness=0, anchor="w").grid(row=index // 2, column=index % 2, sticky="w", padx=(0, 24), pady=1)
        if "scope" in T.DEFAULTS[self._report]:
            row = (len(T.TOGGLES[self._report]) + 1) // 2
            scope = tk.StringVar(master=self._toplevel, value=options.get("scope", T.SCOPE_ALL))
            self._vars["scope"] = scope
            holder = tk.Frame(self._options_host, bg=P.PANE)
            holder.grid(row=row, column=0, columnspan=2, sticky="w", pady=(6, 0))
            tk.Label(holder, text="Systems", fg=P.MUTED, bg=P.PANE).pack(side="left", padx=(0, 10))
            for value in T.SCOPES:
                tk.Radiobutton(holder, text=T.SCOPE_LABELS[value], variable=scope, value=value, command=self._on_changed, bg=P.PANE, fg=P.TEXT, selectcolor=P.CARD,
                               activebackground=P.PANE, activeforeground=P.TEXT, highlightthickness=0).pack(side="left", padx=(0, 14))

    # --- reading the controls -----------------------------------------------------------------------------------
    def _options(self) -> Dict[str, Any]:
        return T.resolve(self._report, {key: var.get() for key, var in self._vars.items()})

    def _modified(self) -> bool:
        return self._options() != T.resolve(self._report, self._loaded.options)

    # --- reacting -----------------------------------------------------------------------------------------------
    def _on_report_picked(self) -> None:
        report = next((r for r in T.REPORTS if T.REPORT_LABELS[r] == self._report_var.get()), self._report)
        self._report = report
        self._loaded = T.templates.chosen(report)
        self._template_box.configure(values=T.templates.names(report))
        self._template_var.set(self._loaded.name)
        self._build_options()
        self._refresh()

    def _on_template_picked(self) -> None:
        found = T.templates.get(self._report, self._template_var.get())
        if found is None:
            return
        T.templates.choose(self._report, found.name)
        self._loaded = found
        self._build_options()
        self._refresh(f"{found.name} is now the template for this report's posts.")

    def _on_changed(self) -> None:
        self._refresh()

    def _remember(self, template: T.Template, message: str) -> None:
        self._loaded = template
        self._template_box.configure(values=T.templates.names(self._report))
        self._template_var.set(template.name)
        self._build_options()
        self._refresh(message)

    def _on_save(self) -> None:
        if self._loaded.preset:
            self._refresh("The built-in presets cannot be changed. Press Save as to keep your changes under a name of your own.")
            return
        self._save(self._loaded.name, "Saved.")

    def _on_save_as(self) -> None:
        name = dialogs.prompt(self._toplevel, "Save template", "A name for this template:", initial="" if self._loaded.preset else self._loaded.name, ok="Save")
        if name is not None:
            self._save(name, "Saved, and it is now the template for this report's posts.")

    def _save(self, name: str, done: str) -> None:
        try:
            self._remember(T.templates.save(self._report, name, self._options()), done)
        except T.TemplateError as err:
            self._refresh(str(err))

    def _on_rename(self) -> None:
        if self._loaded.preset:
            self._refresh("The built-in presets cannot be renamed.")
            return
        name = dialogs.prompt(self._toplevel, "Rename template", "A new name for this template:", initial=self._loaded.name, ok="Rename")
        if name is None:
            return
        try:
            self._remember(T.templates.rename(self._report, self._loaded.name, name), "Renamed.")
        except T.TemplateError as err:
            self._refresh(str(err))

    def _on_delete(self) -> None:
        if self._loaded.preset:
            self._refresh("The built-in presets cannot be deleted.")
            return
        if not dialogs.confirm(self._toplevel, "Delete template", f"Delete the template {self._loaded.name}? Posts go back to using Standard.", yes="Delete", no="Keep", default_yes=False):
            return
        try:
            T.templates.delete(self._report, self._loaded.name)
        except T.TemplateError as err:
            self._refresh(str(err))
            return
        self._remember(T.templates.chosen(self._report), "Deleted. Standard is the template for this report's posts again.")

    # --- drawing ------------------------------------------------------------------------------------------------
    def _refresh(self, message: str = "") -> None:
        """The note under the buttons, and the preview made from the checkboxes as they are now."""
        if message:
            self._note.configure(text=message)
        elif self._modified():
            self._note.configure(text=f"Changed from {self._loaded.name}. The preview shows your changes; posts keep using {self._loaded.name} until you Save"
                                      + (" or Save as." if self._loaded.preset else " (or Save as a new name)."))
        else:
            self._note.configure(text=f"{self._loaded.name} is the template for this report's posts." + ("" if self._loaded.preset else " It is one of your own: change it and press Save."))
        messages, sample = render(self._report, self._options())
        total = sum(len(m) for m in messages)
        source = ("made-up example data (there is no " + ("tick" if self._report == T.BGS else "session") + " to show yet)") if sample else \
            ("your current " + ("tick" if self._report == T.BGS else "session"))
        self._count.configure(text=f"Preview from {source}: {total:,} characters in {len(messages)} message{'s' if len(messages) != 1 else ''} (Discord allows 2,000 in each)")
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        for number, text in enumerate(messages, start=1):
            if number > 1:
                self._text.insert("end", "\n")
            self._text.insert("end", f"Message {number} of {len(messages)}, {len(text):,} characters\n", ("meta",))
            for piece, tags in discord_preview.segments(text):
                self._text.insert("end", piece, tags)
            self._text.insert("end", "\n")
        self._text.configure(state="disabled")
