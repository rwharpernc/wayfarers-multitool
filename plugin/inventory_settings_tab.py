"""The Settings tab of the Inventory window: the pillage message, the pickup sound, which categories announce a pickup, and each suit loadout's backpack capacity.

Set only here; the Settings tab says where they went (see inventory_settings.py). A box saves when you press Enter or click away; a tick saves at once."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, Optional, Tuple

from . import commit_entry
from . import inventory_settings as S
from . import inventory_suit as suit
from . import platform_support
from .inventory import CATEGORY_SHORT, TRACKED_CATEGORIES
from .inventory_sound import PillageSound
from .uikit import palette as P
from .uikit.tooltip import add_tooltip
from .uikit.widgets import NoteLabel, ScrollFrame, section_header


class SettingsTab:
    def __init__(self, parent: tk.Frame, commander: Callable[[], Optional[str]]) -> None:
        self._commander = commander
        self._scroll = ScrollFrame(parent)
        self._scroll.pack(fill="both", expand=True)
        body = self._scroll.body
        self._format = tk.StringVar(value=S.message_format())
        self._sound = tk.BooleanVar(value=S.sound_enabled())
        self._announce: Dict[str, tk.BooleanVar] = {}
        self._capacity_vars: Dict[Tuple[str, str], tk.StringVar] = {}
        self._capacity_entries: Dict[Tuple[str, str], tk.Entry] = {}
        self._format_entry: Optional[tk.Entry] = None
        self._loadout_frame: Optional[tk.Frame] = None
        self._loadouts_shown: Optional[tuple] = None

        section_header(body, "Pillage message").pack(fill="x")
        line = tk.Frame(body, bg=P.PANE)
        line.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        self._format_entry = tk.Entry(line, textvariable=self._format, width=60)
        self._format_entry.pack(side="left", fill="x", expand=True)
        add_tooltip(self._format_entry, "Pillage message - what a pickup says; blank restores the default")
        commit_entry.bind_commit(self._format_entry, self._format, lambda raw: str(S.set_message_format(raw)))
        NoteLabel(body, text="Placeholders: {item} (resource name), {total} (new combined total). Leave blank to reset to the default.").pack(fill="x")

        section_header(body, "Sound").pack(fill="x", pady=(P.PAD, 0))
        available = PillageSound().available
        box = tk.Checkbutton(body, text="Play a sound on pickup", variable=self._sound, bg=P.PANE, fg=P.TEXT, activebackground=P.PANE, activeforeground=P.TEXT,
                             selectcolor=P.BUTTON, highlightthickness=0, anchor="w", state=tk.NORMAL if available else tk.DISABLED,
                             command=lambda: S.set_sound_enabled(self._sound.get()))
        box.pack(fill="x", padx=P.PAD, pady=(P.PAD_SM, 0))
        note, supported = platform_support.sound_support_note()
        NoteLabel(body, text=note, fg=P.OK if supported else P.WARN).pack(fill="x")

        section_header(body, "Announce pickups for").pack(fill="x", pady=(P.PAD, 0))
        row = tk.Frame(body, bg=P.PANE)
        row.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        enabled = S.announced_categories()
        for category in TRACKED_CATEGORIES:
            var = tk.BooleanVar(value=category in enabled)
            self._announce[category] = var
            tick = tk.Checkbutton(row, text=CATEGORY_SHORT[category], variable=var, bg=P.PANE, fg=P.TEXT, activebackground=P.PANE, activeforeground=P.TEXT,
                                  selectcolor=P.BUTTON, highlightthickness=0, command=lambda c=category, v=var: S.set_announced(c, v.get()))
            tick.pack(side="left", padx=(0, P.PAD))
            add_tooltip(tick, f"{CATEGORY_SHORT[category]} - announce pickups of this category")
        NoteLabel(body, text="Unchecked categories are still tracked and counted; only their pickup notification (log, overlay, panel) is muted.").pack(fill="x")

        section_header(body, "Suit Backpack Capacity").pack(fill="x", pady=(P.PAD, 0))
        self._loadout_frame = tk.Frame(body, bg=P.PANE)
        self._loadout_frame.pack(fill="x")
        self._draw_loadouts()
        NoteLabel(body, text="These are the same settings as Settings → WFMT → Inventory.", fg=P.FAINT).pack(fill="x", pady=(P.PAD, 0))
        S.add_listener(self.sync)
        parent.bind("<Destroy>", lambda _e: S.remove_listener(self.sync), add="+")

    # --- suit loadouts -----------------------------------------------------------------------------------------------

    def _loadouts(self) -> dict:
        cmdr = self._commander() or ""
        return suit.known_loadouts_for(cmdr) if cmdr else {}

    def _draw_loadouts(self) -> None:
        """One row per suit loadout seen for this commander, pre-filled with the unengineered default; rebuilt when the set of loadouts changes."""
        frame = self._loadout_frame
        if frame is None:
            return
        loadouts = self._loadouts()
        shown = (self._commander() or "", *sorted(loadouts))        # the commander too: the boxes save against the commander they were built for
        if shown == self._loadouts_shown:
            return
        self._loadouts_shown = shown
        for child in frame.winfo_children():
            child.destroy()
        self._capacity_vars, self._capacity_entries = {}, {}
        if not loadouts:
            NoteLabel(frame, text="No suits recorded yet for this commander. Wear a suit in the game and it appears here.").pack(fill="x")
            return
        NoteLabel(frame, text="Pre-filled with the unengineered default. If a suit is engineered, or otherwise holds a different amount, update the number to what you see in the game.").pack(fill="x")
        cmdr = self._commander() or ""
        for loadout_id, record in sorted(loadouts.items(), key=lambda kv: kv[1].get("name") or kv[0]):
            suit_name = suit.SUIT_DISPLAY_NAMES.get(record.get("suit_key", ""), record.get("suit_key") or "Unknown suit")
            name = record.get("name") or ""
            tk.Label(frame, text=f'{suit_name} - "{name}"' if name else suit_name, fg=P.TEXT, bg=P.PANE, anchor="w").pack(fill="x", padx=P.PAD, pady=(P.PAD_SM, 0))
            fields = tk.Frame(frame, bg=P.PANE)
            fields.pack(fill="x", padx=P.PAD * 2)
            for column, category in enumerate(TRACKED_CATEGORIES):
                tk.Label(fields, text=f"{CATEGORY_SHORT[category]}:", fg=P.MUTED, bg=P.PANE).grid(row=0, column=column * 2, sticky="w", padx=(0 if column == 0 else P.PAD, 4))
                var = tk.StringVar(value=S.capacity_text(record, category))
                entry = tk.Entry(fields, textvariable=var, width=6)
                entry.grid(row=0, column=column * 2 + 1, sticky="w")
                add_tooltip(entry, f"{CATEGORY_SHORT[category]} capacity - how many this suit holds; blank or the default clears your number")
                commit_entry.bind_commit(entry, var, lambda raw, l=loadout_id, c=category: str(S.set_capacity(cmdr, l, c, raw)))
                self._capacity_vars[(loadout_id, category)] = var
                self._capacity_entries[(loadout_id, category)] = entry

    # --- staying in step ---------------------------------------------------------------------------------------------

    def sync(self) -> None:
        """Show what is saved (the Settings tab may have changed it), leaving a box alone while it is being typed in."""
        try:
            focused = self._scroll.focus_get()
        except (tk.TclError, KeyError):
            focused = None
        if focused is not self._format_entry and self._format.get() != S.message_format():
            self._format.set(S.message_format())
        if self._sound.get() != S.sound_enabled():
            self._sound.set(S.sound_enabled())
        enabled = S.announced_categories()
        for category, var in self._announce.items():
            if var.get() != (category in enabled):
                var.set(category in enabled)
        self._draw_loadouts()
        loadouts = self._loadouts()
        for (loadout_id, category), var in self._capacity_vars.items():
            record = loadouts.get(loadout_id)
            if record is not None and self._capacity_entries[(loadout_id, category)] is not focused and var.get() != S.capacity_text(record, category):
                var.set(S.capacity_text(record, category))
