"""Session details window for Powerplay mode: live breakdown + history.

Built on the shared window kit (plugin/uikit: WindowShell, Tabs, DataTable - see
docs/WINDOW_FRAMEWORK_SPEC.md); the numbers and wording are unchanged."""

from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import Any, Dict, List, Optional

from config import appname, config

from . import panelkit, store
from .formulas import ACTIVITIES, ACTIVITY_LABELS, NO_CP_ACTIVITIES, merits_to_cp
from .powerplay import PowerplayTracker, clipboard_template, ratio_for
from . import discord_customize, discord_share, discord_templates, powerplay_discord
from .powerplay_clipboard import format_system_line, progress_rows
from .powerplay_systems_tab import cycle_summary
from .session import (
    SessionManager,
    duration_hours,
    per_hour,
    system_merit_total,
    system_totals,
    total_merits,
    visited_systems,
)
from .powerplay_megaships_tab import MegaShipsTab
from .powerplay_systems_tab import CyclesTab, DailyTab, SystemsPane, SystemsTab
from .uikit import dialogs
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import FlatButton, NoteLabel, ScrollFrame, Tabs, field_grid, section_header

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_powerplay_window_geometry"

MIN_WIDTH = 860
MIN_HEIGHT = 560
DEFAULT_SIZE = (1040, 720)

# Marks the row for whatever system the commander is in right now in the "By
# System" table, so it doesn't get lost among other rows once a session has
# touched several systems.
_CURRENT_SYSTEM_MARK = "▶ "

_SYSTEM_COLUMNS = (
    Column("system", "System", 200),
    Column("merits", "Merits", 90, anchor="e"),
    Column("cp", "Est. CP", 90, anchor="e"),
    Column("breakdown", "Activity breakdown", 320, stretch=True, max_chars=90),
)
_ACTIVITY_COLUMNS = (
    Column("activity", "Activity", 180, stretch=True),
    Column("merits", "Merits", 110, anchor="e"),
    Column("ratio", "Merits/CP", 110, anchor="e"),
    Column("cp", "Est. CP", 110, anchor="e"),
    Column("cp_hr", "CP/hr", 110, anchor="e"),
)
_HISTORY_COLUMNS = (
    Column("started", "Started", 190),
    Column("cmdr", "Commander", 130),
    Column("power", "Power", 170, stretch=True),
    Column("duration", "Duration", 90, anchor="e"),
    Column("merits", "Merits", 100, anchor="e"),
    Column("cp", "Est. CP", 100, anchor="e"),
)

_window: Optional["SessionWindow"] = None


def show(
    parent: tk.Misc, sessions: SessionManager, pp: PowerplayTracker, current_system: Optional[str],
    systems: Optional[SystemsPane] = None,
) -> None:
    """Open the sessions window, or raise it if already open."""
    global _window

    if _window is not None and _window.alive:
        _window.refresh(current_system, systems)
        _window.lift()
        return

    _window = SessionWindow(parent, sessions, pp, current_system, systems)


def refresh(current_system: Optional[str], systems: Optional[SystemsPane] = None) -> None:
    if _window is not None and _window.alive:
        _window.refresh(current_system, systems)


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


class SessionWindow:
    def __init__(
        self, parent: tk.Misc, sessions: SessionManager, pp: PowerplayTracker, current_system: Optional[str],
        systems: Optional[SystemsPane] = None,
    ) -> None:
        self._sessions = sessions
        self._pp = pp
        self._current_system = current_system
        self._systems = systems

        self._shell = WindowShell(
            parent, "Powerplay Sessions", "", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Powerplay session help", _HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._toplevel = self._shell.window

        self._shell.add_action("Refresh", self._flush, tip="Refresh - redraw the tab you are looking at with the latest merit counts")
        self._copy_button = self._shell.add_action("Copy Progress", self._copy_progress,
                                                 tip="Copy Progress - copy one line per system from the By System table, using your clipboard template")
        self._shell.add_action("Reset Current System", self._reset_current_system,
                                tip="Reset Current System - zero this session's merits for the system you are in (asks first)")
        self._shell.add_action("Reset Session", self._reset_session,
                                tip="Reset Session - zero all of this session's merit totals without ending the session (asks first)")

        share = tk.Frame(self._shell.body, bg=P.BG)      # a row of its own: the header bar has no room for more buttons at a narrow width
        share.pack(fill="x", pady=(0, P.PAD_SM))
        FlatButton(share, "Post to Discord", self._on_post_discord,
                   tip="Post to Discord - send this session's merit report to your Discord webhook (Discord)").pack(side="right")
        FlatButton(share, "Copy for Discord", self._on_copy_discord,
                   tip="Copy for Discord - copy this session's merit report, formatted for pasting into Discord").pack(side="right", padx=(0, 6))
        FlatButton(share, "Customize…", self._on_customize_discord,
                   tip="Customize - choose how the Discord report is worded and laid out").pack(side="right", padx=(0, 6))
        discord_customize.register_data(discord_templates.POWERPLAY, self._customize_data)      # the dialog's preview uses this session

        self._tabs = tabs = Tabs(self._shell.body)
        tabs.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._current_tab = _CurrentTab(tabs.add("Current session"))
        self._systems_tab = SystemsTab(tabs.add("Systems"), self._toplevel)
        self._cycles_tab = CyclesTab(tabs.add("Cycles"))
        self._daily_tab = DailyTab(tabs.add("Daily"))
        self._megaships_tab = MegaShipsTab(tabs.add("Megaships"))
        self._history_tab = _HistoryTab(tabs.add("History"))

        # Journal events arrive in bursts and every tab is a table of widgets, so a refresh is
        # coalesced into one pass a moment later and only the tab on screen is redrawn; the
        # others are marked stale and drawn when they are selected.
        self._updaters = [
            lambda: self._current_tab.update(self._sessions.current, self._pp, self._current_system),
            lambda: self._systems_tab.update(self._systems, self._current_system),
            lambda: self._cycles_tab.update(self._systems),
            lambda: self._daily_tab.update(self._systems),
            lambda: self._megaships_tab.update(self._systems),
            lambda: self._history_tab.update(self._sessions.history, self._sessions.current),
        ]
        self._stale = set(range(len(self._updaters)))
        self._flush_job: Optional[str] = None
        tabs.on_select = self._draw_if_stale
        self._flush()

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._toplevel.deiconify()
        self._toplevel.lift()

    REFRESH_DELAY_MS = 250

    def refresh(self, current_system: Optional[str], systems: Optional[SystemsPane] = None) -> None:
        """New data is available: remember it and redraw soon (one pass, however many calls)."""
        if not self.alive:
            return
        self._current_system = current_system
        if systems is not None:
            self._systems = systems
        self._stale = set(range(len(self._updaters)))
        if self._flush_job is None:
            self._flush_job = self._toplevel.after(self.REFRESH_DELAY_MS, self._flush)

    def _flush(self) -> None:
        """Redraw the tab being shown now; mark the rest stale."""
        if self._flush_job is not None:
            try:
                self._toplevel.after_cancel(self._flush_job)
            except tk.TclError:
                pass
            self._flush_job = None
        if not self.alive:
            return
        self._stale = set(range(len(self._updaters)))
        self._draw_if_stale(self._tabs.selected)

    def _draw_if_stale(self, index: int) -> None:
        if self.alive and index in self._stale and 0 <= index < len(self._updaters):
            self._stale.discard(index)
            self._updaters[index]()

    def _reset_session(self) -> None:
        """Zeroes this session's merit counts entirely (session identity untouched) — mainly for correcting a bad count, e.g.
        the donation-mission duplicate-merit journal bug. Confirms first
        since it destroys in-memory/persisted counters."""
        if not dialogs.confirm(
            self._toplevel,
            "Reset Session",
            "Zero this session's merit totals (by system and by activity)?\n\n"
            "This does not end the session, and can't be undone.",
        ):
            return
        self._sessions.reset_session()
        self.refresh(self._current_system)

    def _reset_current_system(self) -> None:
        if not self._current_system:
            dialogs.info(self._toplevel, "Reset Current System", "No current system to reset.")
            return
        if not dialogs.confirm(
            self._toplevel,
            "Reset Current System",
            f"Zero merits earned in {self._current_system} this session (subtracted from the "
            "session totals too)?\n\nThis can't be undone.",
        ):
            return
        self._sessions.reset_system(self._current_system)
        self.refresh(self._current_system)

    def _copy_progress(self) -> None:
        """Copies one formatted line per system in the By System table to
        the clipboard, using the user's configured template (Settings ->
        Powerplay -> Clipboard)."""
        template = clipboard_template()
        lines = [format_system_line(template, system=row.system, merits=f"{row.merits:,}", cp=f"{row.cp:,.1f}", state=row.state)
                 for row in progress_rows(self._sessions.current, self._current_system, self._pp.system_state, ratio_for)]

        panelkit.copy_to_clipboard(self._toplevel, "\n".join(lines))

        original_text = self._copy_button.cget("text")
        self._copy_button.configure(text="Copied!")
        self._copy_button.after(1500, lambda: self._copy_button.configure(text=original_text))

    def _discord_messages(self) -> List[str]:
        """This session's progress as Discord messages (see powerplay_discord.py), with the cycle's totals when the cycles are known."""
        views = self._systems.views() if self._systems is not None else []
        rows = progress_rows(self._sessions.current, self._current_system, self._pp.system_state, ratio_for)
        options = discord_templates.templates.chosen(discord_templates.POWERPLAY).options
        return powerplay_discord.progress_messages(rows, self._sessions.current.get("power") or "", cycle_summary(views[0]) if views else "", options)

    def _customize_data(self) -> Optional[tuple]:
        """What the Customize dialog's preview is made from: this session's rows, the Power and the cycle's total line (None when nothing is earned yet)."""
        views = self._systems.views() if self._systems is not None else []
        rows = progress_rows(self._sessions.current, self._current_system, self._pp.system_state, ratio_for)
        return (rows, self._sessions.current.get("power") or "", cycle_summary(views[0]) if views else "") if rows else None

    def _on_customize_discord(self) -> None:
        discord_customize.show(self._toplevel, discord_templates.POWERPLAY)

    def _on_copy_discord(self) -> None:
        messages = self._discord_messages()
        if not messages:
            self._shell.set_status("No merits earned this session yet.")
        elif discord_share.copy_for_discord(self._toplevel, messages):
            self._shell.set_status("Copied for Discord" + (f" ({len(messages)} messages: paste each one on its own)." if len(messages) > 1 else "."), ok=True)

    def _on_post_discord(self) -> None:
        messages = self._discord_messages()
        if not messages:
            self._shell.set_status("No merits earned this session yet.")
            return
        self._shell.set_status("Posting to Discord...")
        discord_share.post_choosing(self._toplevel, messages, powerplay_discord.report_key(self._sessions.current),
                                    lambda text, ok: self.alive and self._shell.set_status(text, ok=ok))

    def close(self) -> None:
        discord_customize.unregister_data(discord_templates.POWERPLAY, self._customize_data)
        if self._flush_job is not None:
            try:
                self._toplevel.after_cancel(self._flush_job)
            except tk.TclError:
                pass
            self._flush_job = None
        self._shell.close()


_HELP = (
    ("Activity", "The journal doesn't say which activity your merits were for, so WFMT infers it from who controlled the system when they landed."),
    ("Acquisition", "The system was uncontrolled."),
    ("Reinforcement", "The system was controlled by your Power."),
    ("Undermining", "The system was controlled by a rival Power."),
    ("If it looks wrong", "Compare a system's breakdown against the context shown with it."),
)


class _CurrentTab:
    """Live breakdown of the in-progress session: who/how long, what's been
    earned in each system visited, and the same broken out by activity."""

    def __init__(self, parent: tk.Frame) -> None:
        self._heading_shown: Optional[tuple] = None
        self._context_shown: Optional[tuple] = None
        # Explanatory notes are pinned to the bottom of the tab, full width, and
        # packed before the scroll area so they keep their height when it shrinks.
        NoteLabel(
            parent,
            text="By System: what you've earned in each system this session — the current one is marked and stays first.",
        ).pack(side="bottom", fill="x")
        scroll = ScrollFrame(parent)
        scroll.pack(fill="both", expand=True)
        body = scroll.body

        # --- Session heading: commander/power/started/duration -----------
        self._heading = tk.Frame(body, bg=P.PANE)
        self._heading.pack(fill="x", padx=P.PAD, pady=(P.PAD, 4))

        # --- By system -----------------------------------------------------
        section_header(body, "By System").pack(fill="x")
        self._system_table = DataTable(body, _SYSTEM_COLUMNS, sortable=False, visible_rows=6)
        self._system_table.pack(fill="x", padx=P.PAD, pady=(0, P.PAD))

        # --- By activity (session-wide) ------------------------------------
        section_header(body, "By Activity (session total)").pack(fill="x")
        self._activity_table = DataTable(body, _ACTIVITY_COLUMNS, sortable=False,
                                         visible_rows=len(ACTIVITIES) + 1)
        self._activity_table.pack(fill="x", padx=P.PAD, pady=(0, P.PAD))

        # --- Live PowerPlay context ------------------------------------------
        section_header(body, "Current PowerPlay Context").pack(fill="x")
        self._context = tk.Frame(body, bg=P.PANE)
        self._context.pack(fill="x", padx=P.PAD, pady=(0, 8))

    def update(self, session: Dict[str, Any], pp: PowerplayTracker, current_system: Optional[str]) -> None:
        cmdr = session.get("cmdr") or "(unknown)"
        power = pp.pledge_summary() or session.get("power") or "(not pledged)"
        started = session.get("started_at") or "?"
        hours = duration_hours(session)

        heading = (cmdr, power, started, f"{hours:.2f}h")
        if heading != self._heading_shown:
            self._heading_shown = heading
            for child in self._heading.winfo_children():
                child.destroy()
            field_grid(self._heading, 0, (("Commander:", cmdr), ("Power:", power)))
            field_grid(self._heading, 1, (("Started:", started), ("Duration:", f"{hours:.2f}h")))

        name = current_system or pp.system_name or "(none seen yet)"
        state = pp.system_state or "(none seen yet)"
        controller = pp.system_controller or "(none)"
        powers = ", ".join(pp.system_powers) if pp.system_powers else "(none)"
        context = (name, state, controller, powers)
        if context != self._context_shown:
            self._context_shown = context
            for child in self._context.winfo_children():
                child.destroy()
            field_grid(self._context, 0, (("System:", name), ("State:", state)))
            field_grid(self._context, 1, (("Controller:", controller), ("Rival Powers:", powers)))

        self._update_system_table(session, current_system)
        self._update_activity_table(session, hours)

    def _update_system_table(self, session: Dict[str, Any], current_system: Optional[str]) -> None:
        systems = visited_systems(session)
        # The current system leads the list even if it hasn't earned any
        # merits yet this visit, so it's never missing from its own table.
        if current_system and current_system not in systems:
            systems = [current_system] + systems
        elif current_system in systems:
            systems = [current_system] + [s for s in systems if s != current_system]

        if not systems:
            self._system_table.set_rows([("(no systems visited yet)", "", "", "")])
            return

        rows = []
        for name in systems:
            totals = system_totals(session, name)
            merits = system_merit_total(session, name)
            cp = sum(
                merits_to_cp(totals.get(activity, 0), ratio_for(activity))
                for activity in ACTIVITIES
                if activity not in NO_CP_ACTIVITIES
            )
            breakdown = " · ".join(
                f"{ACTIVITY_LABELS[activity]} {totals[activity]:,}"
                for activity in ACTIVITIES
                if totals.get(activity)
            ) or "—"

            label = f"{_CURRENT_SYSTEM_MARK}{name} (current)" if name == current_system else name
            rows.append((label, f"{merits:,}", f"{cp:,.1f}" if merits else "—", breakdown))
        self._system_table.set_rows(rows)

    def _update_activity_table(self, session: Dict[str, Any], hours: float) -> None:
        rows = []
        totals = session.get("totals", {})

        merits_sum = 0
        cp_sum = 0.0
        for activity in ACTIVITIES:
            merits = totals.get(activity, 0)
            merits_sum += merits
            has_cp = activity not in NO_CP_ACTIVITIES
            ratio = ratio_for(activity) if has_cp else 0.0
            cp = merits_to_cp(merits, ratio) if has_cp else 0.0
            cp_sum += cp
            cp_hr = per_hour(cp, hours)
            rows.append((
                ACTIVITY_LABELS[activity],
                f"{merits:,}",
                f"{ratio:g}" if ratio else "—",
                f"{cp:,.1f}" if has_cp else "—",
                f"{cp_hr:,.1f}" if has_cp and hours > 0 else "—",
            ))

        rows.append((
            "Total",
            f"{merits_sum:,}",
            "",
            f"{cp_sum:,.1f}",
            f"{per_hour(cp_sum, hours):,.1f}" if hours > 0 else "—",
        ))
        self._activity_table.set_rows(rows)


def _cumulative_summary(sessions: List[Dict[str, Any]]) -> str:
    """'All sessions — Merits: 12,345   CP: Acquisition 120 / Reinforcement 80 / Undermining 40'."""
    merit_totals: Dict[str, int] = {activity: 0 for activity in ACTIVITIES}
    for s in sessions:
        totals = s.get("totals", {})
        for activity in ACTIVITIES:
            merit_totals[activity] += totals.get(activity, 0)

    cumulative_merits = sum(merit_totals.values())
    cp_bits = " / ".join(
        f"{ACTIVITY_LABELS[activity]} {merits_to_cp(merit_totals[activity], ratio_for(activity)):,.1f}"
        for activity in ACTIVITIES
        if activity not in NO_CP_ACTIVITIES
    )

    return "   ".join([f"All sessions — Merits: {cumulative_merits:,}", f"CP: {cp_bits}"])


class _HistoryTab:
    """Past sessions, most recent first."""

    def __init__(self, parent: tk.Frame) -> None:
        section_header(parent, "All Sessions").pack(fill="x")
        self._summary_label = NoteLabel(parent, fg=P.TEXT, font=P.FONT_BOLD)
        self._summary_label.pack(side="bottom", fill="x")
        self._table = DataTable(parent, _HISTORY_COLUMNS, sortable=False)
        self._table.pack(fill="both", expand=True, padx=P.PAD, pady=(0, P.PAD_SM))

    def update(self, history: List[Dict[str, Any]], current: Dict[str, Any]) -> None:
        rows = []
        # Only this commander's sessions: the file holds everyone's, but a total or a list that mixed commanders would
        # be wrong for all of them.
        sessions = store.sessions_of(history, current.get("cmdr")) + [current]
        self._summary_label.configure(text=_cumulative_summary(sessions))
        for session in reversed(sessions):
            hours = duration_hours(session)
            cp_sum = sum(
                merits_to_cp(session.get("totals", {}).get(activity, 0), ratio_for(activity))
                for activity in ACTIVITIES
                if activity not in NO_CP_ACTIVITIES
            )
            is_current = session is current

            rows.append((
                session.get("started_at", "?") + (" (live)" if is_current else ""),
                session.get("cmdr") or "?",
                session.get("power") or "—",
                f"{hours:.2f}h",
                f"{total_merits(session):,}",
                f"{cp_sum:,.1f}",
            ))

        if not sessions:
            rows.append(("(no sessions yet)", "", "", "", "", ""))
        self._table.set_rows(rows)
