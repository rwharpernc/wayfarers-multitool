"""The Space Mining Book window (the BOOK button on the Space Mining page): every ring your journals show hotspots for or that you mined at, with its hotspots by mineral, its class and reserve level, the tons you mined there and
when, and your own note and favorite star. Rings you add by hand join the list.

The rings are built from the journals (`mining_history.py` reads every journal once, in the background, then only the new ones; `mining_rings_data.py` says what each field is). The journal
gives each mineral's hotspot **count** for a ring, not where the hotspots are, so overlaps are not shown. The notes, favorites and by-hand rings are the commander's own, per commander
(`mining_rings.py`). Nothing is sent anywhere. The Surface Mining Book (`mining_ledger.py`) is the separate book for the Rhino's deposits.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import List, Optional

from config import appname, config

from . import mining_history, mining_location, mining_rings, mining_rings_data as RD
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, FlatButton, NoteLabel

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_mining_ring_book_geometry"
DEFAULT_SIZE = (1100, 640)
MIN_SIZE = (900, 480)
TICK_MS = 1500
MAX_ROWS = 150      # the table draws a label per cell, so thousands of rings take seconds to open and to close; Find reaches the rest
DASH = "—"

COLUMNS = (
    Column("star", "★", 36, anchor="center"),
    Column("ring", "Ring", 250, stretch=True),
    Column("system", "System", 170),
    Column("hotspots", "Hotspots (count per mineral)", 270),
    Column("class", "Class", 90),
    Column("reserve", "Reserve", 80),
    Column("tons", "Tons mined", 90, anchor="e"),
    Column("last", "Last mined", 100),
)
CLASS_CHOICES = ("", "Icy", "Rocky", "Metallic", "Metal rich")
RESERVE_CHOICES = ("", "Pristine", "Major", "Common", "Low", "Depleted")

_window: Optional["RingBook"] = None


_HELP = (
    ("Rings", "Come from your journals. A DSS scan of a ring gives each mineral's hotspot count, not where they are, and mining at a ring adds its tons."),
    ("Remove", "Only a ring you added by hand can be removed."),
)


def show(parent: tk.Misc) -> None:
    """Open the book, or raise it (and refresh it) if it is open. Parented on the main window's toplevel, since the panel rebuilds its own content frame."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return
    _window = RingBook(parent.winfo_toplevel())


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def date_text(stamp: str) -> str:
    return str(stamp or "")[:10] or DASH


class RingBook:
    def __init__(self, parent: tk.Misc) -> None:
        self._rows: List[RD.RingRow] = []
        self._shown: dict = {}
        self._signature: Optional[tuple] = None
        self._shell = WindowShell(
            parent, "Space Mining Book", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Space Mining Book help", _HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Add ring", self._add_ring, accent=True, tip="Add ring - add a ring by hand to the book")
        self._shell.add_action("This system", self._find_here, tip="This system - go to the rings in the system you are in")
        self._shell.add_action("Refresh", self._reread, tip="Refresh - read the newest journal again and redraw the list")
        body = self._shell.body

        controls = tk.Frame(body, bg=P.BG)
        controls.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(controls, text="Find:", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._find = tk.StringVar()
        entry = tk.Entry(controls, textvariable=self._find, width=28)
        entry.pack(side="left", padx=(6, 6))
        entry.bind("<KeyRelease>", lambda _e: self.refresh())
        self._favorites = tk.BooleanVar(master=self._shell.window, value=False)
        tk.Checkbutton(controls, text="Favorites only", variable=self._favorites, command=self.refresh, fg=P.TEXT, bg=P.BG, selectcolor=P.PANE,
                       activebackground=P.BG, activeforeground=P.TEXT).pack(side="left", padx=(P.PAD, 0))
        tk.Label(controls, text="Type a ring, a system, a mineral or part of a note.", fg=P.MUTED, bg=P.BG).pack(side="left", padx=(P.PAD, 0))

        self._banner = tk.Label(body, text="", fg=P.ACCENT, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD))
        self._banner.pack(fill="x", pady=(0, P.PAD_SM))
        self._table = DataTable(body, COLUMNS, on_select=self._select, empty_text="No rings yet: DSS-scan a ring, or press Add ring.")
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))

        card = tk.Frame(body, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        card.pack(fill="x", side="bottom", before=self._table)       # packed ahead of the table, so a short window shrinks the table, not the note and buttons
        card.columnconfigure(1, weight=1)
        self._detail = NoteLabel(card, "Select a ring.", fg=P.TEXT, bg=P.CARD, font=P.FONT_BOLD, padx=0)
        self._detail.grid(row=0, column=0, columnspan=4, sticky="ew")
        tk.Label(card, text="Your note", fg=P.MUTED, bg=P.CARD, anchor="w").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._note = tk.StringVar()
        note_entry = tk.Entry(card, textvariable=self._note)
        note_entry.grid(row=1, column=1, sticky="ew", padx=P.PAD_SM, pady=(4, 0))
        note_entry.bind("<Return>", lambda _e: self._save_note())
        actions = tk.Frame(card, bg=P.CARD)
        actions.grid(row=1, column=2, columnspan=2, sticky="e", pady=(4, 0))
        FlatButton(actions, "Save note", self._save_note, tip="Save note - keep your note on the selected ring").pack(side="left")
        FlatButton(actions, "Favorite", self._toggle_favorite, tip="Favorite - mark or unmark the selected ring as a favorite").pack(side="left", padx=(6, 0))
        FlatButton(actions, "Copy system", self._copy_system, tip="Copy system - copy the selected ring's system name to the clipboard").pack(side="left", padx=(6, 0))
        FlatButton(actions, "Remove", self._remove, tip="Remove - remove the selected ring (only a ring you added by hand)").pack(side="left", padx=(6, 0))
        self.refresh()
        self._shell.window.after(TICK_MS, self._tick)

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._shell.close()

    def _say(self, text: str) -> None:
        self._shell.set_status(text)

    def _tick(self) -> None:
        """While the journals are still being read for the first time, show what has been found so far; then stop."""
        if not self.alive:
            return
        self.refresh()
        if mining_history.history.reading or not mining_history.history.ready:
            self._shell.window.after(TICK_MS, self._tick)

    def _find_here(self) -> None:
        """Go to the rings in the system you are in; say so when the book has none."""
        system = mining_location.current_system()
        if not system:
            self._say("WFMT does not know your current system yet: jump or log in first.")
            return
        self.refresh()
        here = [row for row in self._rows if row.system.casefold() == system.casefold()]
        if not here:
            self._say("You have not worked this system yet.")
            return
        self._find.set(system)                                   # narrows the list to this system, so the match is within the rows drawn
        self._favorites.set(False)
        self.refresh()
        self._table.select(here[0].key, notify=True)
        self._table.after_idle(lambda: self._table.see(here[0].key))
        self._say(f"{system}: {len(here)} ring{'s' if len(here) != 1 else ''} in your book. Showing {here[0].ring}.")

    def _reread(self) -> None:
        mining_history.history.refresh()
        self.refresh()
        self._say("Reading the newest journal again.")
        self._shell.window.after(TICK_MS, self._tick)

    # --- the list -----------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        if not self.alive:
            return
        history = mining_history.history
        all_rows = RD.build_rows(history.rings(), history.runs(), mining_rings.notes.entries())
        self._rows = all_rows
        matching = RD.filter_rows(all_rows, self._find.get(), bool(self._favorites.get()))
        shown = matching[:MAX_ROWS]
        reading = history.reading.replace("for the mining history", "for rings and mining") if history.reading else ("" if history.ready else "Reading your journals for rings…")
        self._banner.configure(text=(reading + "  (once, in the background: the list grows as it goes)") if reading else "")
        tons = sum(row.tons for row in all_rows)
        self._shell.set_subtitle(f"{history.commander or 'No commander yet'}  ·  {len(all_rows)} rings, {tons:,} t mined"
                                   + (f"  ·  showing the first {len(shown)} of {len(matching)}: use Find to reach the rest" if len(matching) > len(shown) else ""))
        signature = tuple((r.key, r.ring, r.system, tuple(sorted(r.hotspots.items())), r.ring_class, r.reserve, r.tons, r.last_mined, r.favorite, r.note, r.manual) for r in shown)
        if signature == self._signature:
            return                                    # nothing changed: leave the table alone so it does not flicker while the journals are read
        self._signature = signature
        selected = next(iter(self._table.selection()), None)
        self._shown = {row.key: row for row in shown}
        self._table.clear()
        for row in shown:
            self._table.insert(row.key, ["★" if row.favorite else "", row.ring, row.system or DASH, RD.hotspot_text(row.hotspots) or DASH, row.ring_class or DASH,
                                          row.reserve or DASH, f"{row.tons:,}" if row.tons else DASH, date_text(row.last_mined)])
        if selected in self._shown:
            self._table.select(selected, notify=False)
        else:
            self._render(None)

    def _select(self, key: str) -> None:
        self._render(self._shown.get(key))

    def _current(self) -> Optional[RD.RingRow]:
        chosen = self._table.selection()
        return self._shown.get(chosen[0]) if chosen else None

    def _render(self, row: Optional[RD.RingRow]) -> None:
        if row is None:
            self._detail.configure(text="Select a ring.")
            self._note.set("")
            return
        parts = [row.ring + (f"  ·  {row.system}" if row.system else "")]
        parts.append("Hotspots: " + (RD.hotspot_text(row.hotspots, limit=30) or "none recorded (DSS-scan the ring)") + (f" ({row.hotspot_total} in all)" if row.hotspots else ""))
        parts.append(f"Class: {row.ring_class or 'not known'}  ·  Reserve: {row.reserve or 'not known'}")
        parts.append(f"Mined: {row.tons:,} t in {row.runs} run{'s' if row.runs != 1 else ''}" + (f", last {date_text(row.last_mined)}" if row.last_mined else "") if row.runs else "Not mined yet")
        if row.manual:
            parts.append("Added by hand")
        self._detail.configure(text="\n".join(parts))
        self._note.set(row.note)

    # --- using it -----------------------------------------------------------------------------------------------------

    def _save_note(self) -> None:
        row = self._current()
        if row is None:
            self._say("Select a ring first.")
            return
        mining_rings.notes.set_note(row.key, self._note.get())
        self.refresh()
        self._say("Note saved.")

    def _toggle_favorite(self) -> None:
        row = self._current()
        if row is None:
            self._say("Select a ring first.")
            return
        mining_rings.notes.set_favorite(row.key, not row.favorite)
        self.refresh()
        self._say("Favorite." if not row.favorite else "No longer a favorite.")

    def _copy_system(self) -> None:
        row = self._current()
        if row is None or not row.system:
            self._say("Select a ring that has a system first.")
            return
        try:
            self._shell.window.clipboard_clear()
            self._shell.window.clipboard_append(row.system)
        except tk.TclError:
            self._say("Could not use the clipboard.")
            return
        self._say(f"Copied {row.system}. Paste it into the galaxy map's search.")

    def _remove(self) -> None:
        row = self._current()
        if row is None:
            self._say("Select a ring first.")
            return
        if not row.manual:
            self._say("Only a ring you added by hand can be removed. Rings from your journals come back when the journals are read.")
            return
        mining_rings.notes.remove_manual(row.key)
        self.refresh()
        self._say("Removed.")

    # --- adding a ring by hand ------------------------------------------------------------------------------------------

    def _add_ring(self) -> None:
        dialog = tk.Toplevel(self._shell.window)
        dialog.title("Add a ring")
        dialog.configure(bg=P.BG)
        dialog.transient(self._shell.window)
        fields = {}
        for row, (label, key) in enumerate((("Ring (as the game names it)", "ring"), ("System", "system"), ("Hotspots, e.g. Painite 3, Platinum 2", "hotspots"))):
            tk.Label(dialog, text=label, fg=P.MUTED, bg=P.BG, anchor="w").grid(row=row, column=0, sticky="w", padx=P.PAD, pady=(P.PAD_SM, 0))
            var = tk.StringVar()
            tk.Entry(dialog, textvariable=var, width=40).grid(row=row, column=1, padx=P.PAD, pady=(P.PAD_SM, 0))
            fields[key] = var
        class_var, reserve_var = tk.StringVar(value=""), tk.StringVar(value="")
        tk.Label(dialog, text="Class", fg=P.MUTED, bg=P.BG, anchor="w").grid(row=3, column=0, sticky="w", padx=P.PAD, pady=(P.PAD_SM, 0))
        Combobox(dialog, textvariable=class_var, values=list(CLASS_CHOICES), state="readonly", width=14).grid(row=3, column=1, sticky="w", padx=P.PAD, pady=(P.PAD_SM, 0))
        tk.Label(dialog, text="Reserve level", fg=P.MUTED, bg=P.BG, anchor="w").grid(row=4, column=0, sticky="w", padx=P.PAD, pady=(P.PAD_SM, 0))
        Combobox(dialog, textvariable=reserve_var, values=list(RESERVE_CHOICES), state="readonly", width=14).grid(row=4, column=1, sticky="w", padx=P.PAD, pady=(P.PAD_SM, 0))
        message = tk.Label(dialog, text="", fg=P.DANGER, bg=P.BG, anchor="w", wraplength=380, justify="left")
        message.grid(row=5, column=0, columnspan=2, sticky="w", padx=P.PAD, pady=(P.PAD_SM, 0))

        def save() -> None:
            hotspots = RD.parse_hotspots(fields["hotspots"].get())
            if not " ".join(fields["ring"].get().split()):
                message.configure(text="Give the ring's name.")
            elif hotspots is None:
                message.configure(text="Write the hotspots like: Painite 3, Platinum 2.")
            elif mining_rings.notes.add_manual(fields["ring"].get(), fields["system"].get(), hotspots, class_var.get(), reserve_var.get()) is None:
                message.configure(text="No commander is known yet: log in first.")
            else:
                dialog.destroy()
                self.refresh()
                self._say("Ring added.")

        buttons = tk.Frame(dialog, bg=P.BG)
        buttons.grid(row=6, column=0, columnspan=2, sticky="e", padx=P.PAD, pady=P.PAD)
        FlatButton(buttons, "Add", save, kind="accent", tip="Add - save this ring in the Mining Book").pack(side="left")
        FlatButton(buttons, "Cancel", dialog.destroy, tip="Cancel - close this window without adding a ring").pack(side="left", padx=(6, 0))
