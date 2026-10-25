"""The Stored modules tab of the Ship Builds window: the modules the commander has in storage and where (`stored_modules.py`), with a filter box.

The list is only as fresh as the last visit to Module Storage plus the store and retrieve events since, and the line above the table says when that visit was. The
table shows at most `stored_modules.MAX_ROWS` rows at a time; the filter narrows a longer list. The tab polls the book's `revision`, because the book is also changed
by a worker thread at start-up and Tk must only be touched from its own thread.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from . import stored_modules
from .uikit import palette as P
from .uikit.table import Column, DataTable
from .uikit.widgets import NoteLabel

POLL_MS = 1500
FILTER_DELAY_MS = 250

COLUMNS = (
    Column("module", "Module", 140, stretch=True, max_chars=60),
    Column("class", "Class", 60, max_chars=14),
    Column("engineering", "Engineering", 130, max_chars=40),
    Column("where", "Where", 150, max_chars=70),
    Column("transfer", "Transfer", 120, anchor="e", max_chars=24),
    Column("marks", "Marks", 70, max_chars=16),
)


class StoredModulesTab:
    def __init__(self, parent: tk.Frame, book: stored_modules.ModuleBook, get_cmdr: Callable[[], str]) -> None:
        self._book, self._get_cmdr = book, get_cmdr
        self._parent = parent
        self._seen = (-1, "", "")
        self._job = None

        pad = tk.Frame(parent, bg=P.PANE)
        pad.pack(fill="both", expand=True, padx=P.PAD, pady=P.PAD)
        filters = tk.Frame(pad, bg=P.PANE)
        filters.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(filters, text="Filter", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._query = tk.StringVar()
        tk.Entry(filters, textvariable=self._query, width=26).pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._query.trace_add("write", lambda *_: self._filter_later())
        self._count = tk.Label(filters, text="", fg=P.MUTED, bg=P.PANE, anchor="w")
        self._count.pack(side="left")
        self._fresh = NoteLabel(pad, padx=0)
        self._fresh.pack(fill="x", pady=(0, P.PAD_SM))
        self._table = DataTable(pad, COLUMNS, empty_text="No stored module to show.")
        self._table.pack(fill="both", expand=True)
        self.refresh()
        self._poll()

    def _alive(self) -> bool:
        try:
            return bool(self._parent.winfo_exists())
        except tk.TclError:
            return False

    def _poll(self) -> None:
        if not self._alive():
            return
        if self._seen[:1] != (self._book.revision,) or self._seen[1] != self._get_cmdr():
            self.refresh()
        self._parent.after(POLL_MS, self._poll)

    def _filter_later(self) -> None:
        if self._job is not None:
            try:
                self._parent.after_cancel(self._job)
            except tk.TclError:
                pass
        self._job = self._parent.after(FILTER_DELAY_MS, self.refresh)

    def refresh(self) -> None:
        """Redraws the list for the current commander and filter."""
        if not self._alive():
            return
        cmdr = self._get_cmdr()
        query = self._query.get()
        self._seen = (self._book.revision, cmdr, query)
        rows, total = self._book.rows(cmdr, query) if cmdr else ([], 0)
        self._table.set_rows(rows)
        everything = len(self._book.modules(cmdr)) if cmdr else 0
        if not cmdr:
            self._count.configure(text="(no commander detected yet)")
        elif total > len(rows):
            self._count.configure(text=f"Showing {len(rows)} of {total}; filter to narrow")
        else:
            self._count.configure(text=f"{total} of {everything} stored modules" if query.strip() else f"{everything} stored modules")
        self._fresh.configure(text=self._book.freshness(cmdr) if cmdr else "Waiting for a commander to log in.")
