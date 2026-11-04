"""The Settings tab of the Powerplay Sessions window: the merits-per-CP ratios, the Copy Progress line format and how many cycles the start-up journal scan covers.

They are set only here; the Settings → WFMT → Powerplay tab says where they went. A box saves when you press Enter or click away (a ratio
must be above 0, the cycles 1 to MAX_BACKFILL_CYCLES; anything else leaves the saved value). `powerplay.py` holds the readers and the savers (`set_ratio`,
`set_clipboard_template`, `set_backfill_cycles`) and the listeners; this tab only draws them."""
from __future__ import annotations

import tkinter as tk
from typing import Dict, Optional

from . import commit_entry, powerplay
from .formulas import ACTIVITIES, ACTIVITY_LABELS, DEFAULT_RATIOS
from .powerplay_ledger import MAX_BACKFILL_CYCLES
from .uikit import palette as P
from .uikit.tooltip import add_tooltip
from .uikit.widgets import FlatButton, NoteLabel, ScrollFrame, section_header

_FORMAT_WIDTH = 64


class SettingsTab:
    def __init__(self, parent: tk.Frame) -> None:
        self._ratios: Dict[str, tk.StringVar] = {}
        self._ratio_entries: Dict[str, tk.Entry] = {}
        self._format = tk.StringVar(value=powerplay.clipboard_template())
        self._cycles = tk.StringVar(value=str(powerplay.backfill_cycles()))
        self._format_entry: Optional[tk.Entry] = None
        self._cycles_entry: Optional[tk.Entry] = None
        self._record_sales = tk.BooleanVar(value=powerplay.record_sales_enabled())
        self._sales_status = tk.StringVar(value="")
        self._parent = parent
        self._scroll = ScrollFrame(parent)      # the page is taller than the window at its smallest size
        self._scroll.pack(fill="both", expand=True)
        body = self._scroll.body

        section_header(body, "Control Points: merits per 1 CP").pack(fill="x")
        NoteLabel(body, text="Frontier doesn't publish these in the journal; the defaults are community estimates. If your in-game CP totals don't line up, correct the ratio here "
                               "(merits required for 1 CP). System strength, ethos and Squadron bonuses are already in the merits the journal reports.").pack(fill="x", pady=(P.PAD_SM, 0))
        row = tk.Frame(body, bg=P.PANE)
        row.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        for activity in ACTIVITIES:
            if activity not in DEFAULT_RATIOS:
                continue
            tk.Label(row, text=f"{ACTIVITY_LABELS[activity]}:", fg=P.MUTED, bg=P.PANE).pack(side="left", padx=(0, P.PAD_SM))
            var = tk.StringVar(value=powerplay._format_ratio(powerplay.ratio_for(activity)))
            entry = tk.Entry(row, textvariable=var, width=7)
            entry.pack(side="left", padx=(0, P.PAD * 2))
            add_tooltip(entry, f"{ACTIVITY_LABELS[activity]} - merits that make 1 Control Point (must be above 0)")
            commit_entry.bind_commit(entry, var, lambda raw, a=activity: str(powerplay.set_ratio(a, raw)))
            self._ratios[activity] = var
            self._ratio_entries[activity] = entry

        section_header(body, "Copy Progress").pack(fill="x", pady=(P.PAD, 0))
        NoteLabel(body, text='Format for each system\'s line when "Copy Progress" copies to the clipboard. Placeholders: ' + "  ".join(powerplay.CLIPBOARD_PLACEHOLDERS)).pack(
            fill="x", pady=(P.PAD_SM, 0))
        line = tk.Frame(body, bg=P.PANE)
        line.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        self._format_entry = tk.Entry(line, textvariable=self._format, width=_FORMAT_WIDTH)
        self._format_entry.pack(side="left", fill="x", expand=True)
        add_tooltip(self._format_entry, "Copy Progress format - one line per system; blank restores the default")
        commit_entry.bind_commit(self._format_entry, self._format, lambda raw: str(powerplay.set_clipboard_template(raw)))
        FlatButton(line, "Reset to default", lambda: self._format.set(powerplay.set_clipboard_template(powerplay.DEFAULT_CLIPBOARD_TEMPLATE)),
                   tip="Reset to default - put the Copy Progress line back to the original format").pack(side="left", padx=(P.PAD_SM, 0))

        section_header(body, "Journal scan").pack(fill="x", pady=(P.PAD, 0))
        NoteLabel(body, text="When a commander is first seen, WFMT reads their journals to fill in Powerplay cycles it missed; after that it reads only what happened while EDMC was closed. "
                               f"This is how many cycles back (this one included, 1 to {MAX_BACKFILL_CYCLES}) to look for a new commander; journals older than you have kept can't be read.").pack(
            fill="x", pady=(P.PAD_SM, 0))
        scan = tk.Frame(body, bg=P.PANE)
        scan.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        tk.Label(scan, text="Cycles to scan:", fg=P.MUTED, bg=P.PANE).pack(side="left", padx=(0, P.PAD_SM))
        self._cycles_entry = tk.Entry(scan, textvariable=self._cycles, width=6)
        self._cycles_entry.pack(side="left")
        add_tooltip(self._cycles_entry, f"Cycles to scan - how far back to read journals for a new commander (1 to {MAX_BACKFILL_CYCLES})")
        commit_entry.bind_commit(self._cycles_entry, self._cycles, lambda raw: str(powerplay.set_backfill_cycles(raw)))

        section_header(body, "Sale-merit log").pack(fill="x", pady=(P.PAD, 0))
        NoteLabel(body, text="Frontier does not say how a sale earns merits, and players' reports disagree. While you are pledged and in a system with a Powerplay state, WFMT writes each sale "
                               "(goods, tons, prices, profit, margin, system state) and the merits that followed it to a spreadsheet file, so the rule can be worked out from your own sales. "
                               "Nothing is estimated or shown in the panel, and nothing is sent anywhere.").pack(fill="x", pady=(P.PAD_SM, 0))
        tick = tk.Checkbutton(body, text="Record sale merits", variable=self._record_sales, bg=P.PANE, fg=P.TEXT, activebackground=P.PANE, activeforeground=P.TEXT,
                              selectcolor=P.BUTTON, highlightthickness=0, anchor="w", command=lambda: powerplay.set_record_sales(self._record_sales.get()))
        tick.pack(fill="x", padx=P.PAD, pady=(P.PAD_SM, 0))
        add_tooltip(tick, "Record sale merits - write each sale made while pledged, with the merits that followed, to the sale-merit log")
        path = tk.Frame(body, bg=P.PANE)
        path.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        FlatButton(path, "Rescan journals for sales", self._rescan,
                   tip="Rescan journals for sales - read all of this commander's journals and add the sales not yet in the log (WFMT already catches up on its own at start-up; this reads everything, which can take a minute or more)").pack(side="left")
        tk.Label(path, textvariable=self._sales_status, fg=P.MUTED, bg=P.PANE, anchor="w").pack(side="left", padx=(P.PAD_SM, 0))
        NoteLabel(body, text="File: " + (powerplay.controller.sale_log_path() or "(available once EDMC has started)"), fg=P.FAINT).pack(fill="x")

        NoteLabel(body, text="These are the same settings as Settings → WFMT → Powerplay.", fg=P.FAINT).pack(fill="x", pady=(P.PAD, 0))
        powerplay.add_settings_listener(self.sync)
        parent.bind("<Destroy>", lambda _e: powerplay.remove_settings_listener(self.sync), add="+")

    def _rescan(self) -> None:
        if powerplay.controller.rescan_sales():
            self._poll_rescan()
        else:
            self._sales_status.set(powerplay.controller.sales_scan_status() or "Not available yet: play or load a commander first.")

    def _poll_rescan(self) -> None:
        """Follow the worker thread's status from the Tk thread until it finishes."""
        try:
            self._sales_status.set(powerplay.controller.sales_scan_status())
            if powerplay.controller._sales_scan_running:
                self._parent.after(500, self._poll_rescan)
        except tk.TclError:      # the window has gone
            pass

    def sync(self) -> None:
        """Show what is saved (the Settings tab may have changed it), leaving a box alone while it is being typed in."""
        try:
            focused = self._format_entry.focus_get() if self._format_entry is not None else None
        except (tk.TclError, KeyError):
            focused = None
        if self._record_sales.get() != powerplay.record_sales_enabled():
            self._record_sales.set(powerplay.record_sales_enabled())
        for activity, var in self._ratios.items():
            held = powerplay._format_ratio(powerplay.ratio_for(activity))
            if focused is not self._ratio_entries[activity] and var.get() != held:
                var.set(held)
        if focused is not self._format_entry and self._format.get() != powerplay.clipboard_template():
            self._format.set(powerplay.clipboard_template())
        if focused is not self._cycles_entry and self._cycles.get() != str(powerplay.backfill_cycles()):
            self._cycles.set(str(powerplay.backfill_cycles()))
