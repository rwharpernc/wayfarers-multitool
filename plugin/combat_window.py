"""The Combat Record window: the COMBAT button of the Operations panel's Combat Record section.

Three tabs, all for the active commander:

- **This session**: the kills, deaths and rewards of the game login being played, and the same split by ship.
- **All time**: every session added up (the journals are read once, so play from before WFMT counts), split by ship.
- **Sessions**: one row per session, newest first; selecting a row shows that session's split by ship underneath.

The figures come from `combat_record` (kept per commander, read from the journals in the background); this module only draws them. It polls the record's
`revision` and redraws when it changed, because the record is also changed by a worker thread at start-up.
"""
from __future__ import annotations

import logging
import os
import time
import tkinter as tk
from typing import Any, Dict, List, Optional, Sequence, Tuple

from config import appname, config

from . import combat_record as C
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import NoteLabel, StatTile, Tabs, TileRow

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_combat_window_geometry"
DEFAULT_SIZE = (940, 640)
MIN_SIZE = (700, 440)
POLL_MS = 700

SHIP_COLUMNS = (
    Column("ship", "Ship", 150, stretch=True, max_chars=40),
    Column("name", "Name", 150, max_chars=50),
    Column("kills", "Kills", 60, anchor="e"),
    Column("pvp", "PvP kills", 70, anchor="e"),
    Column("deaths", "Deaths", 65, anchor="e"),
    Column("kd", "K/D", 55, anchor="e"),
    Column("reward", "Rewards (cr)", 110, anchor="e"),
)
SESSION_COLUMNS = (
    Column("date", "Started", 170, stretch=True, max_chars=40),
    Column("kills", "Kills", 60, anchor="e"),
    Column("pvp", "PvP kills", 70, anchor="e"),
    Column("deaths", "Deaths", 65, anchor="e"),
    Column("kd", "K/D", 55, anchor="e"),
    Column("reward", "Rewards (cr)", 110, anchor="e"),
)

_HELP = (
    ("Kills", "Ships destroyed for a bounty (Bounty) or a bond (FactionKillBond), and on-foot targets that paid a bounty. Kills in a conflict zone count when the game pays a bond for them."),
    ("PvP kills", "Other commanders destroyed (PVPKill). They are counted apart from kills; K/D counts both."),
    ("Deaths", "Each time your ship, SRV or suit was destroyed (Died), on the ship that was lost."),
    ("K/D", "Kills and PvP kills divided by deaths. A dash while there has been no death."),
    ("Rewards", "The credits the bounties and bonds paid. Bonds and bounties are not profit: they are what the game said you were owed."),
    ("Ships", "A ship is its type and the game's number for it, so two Pythons are two rows and a renamed ship stays one row. The SRV and being on foot have rows of their own."),
    ("Session", "One game login, the journal file it was played in. A logout to the menu and back is the same session."),
    ("Rebuild from journals", "Clear this commander's record and read every journal again. Use it if the figures look wrong; it gives the same figures when the journals are all there."),
)

_window: Optional["CombatWindow"] = None


def show(parent: tk.Misc, book: Optional[C.CombatBook] = None) -> None:
    """Open the window, or raise it if it is open. Parented on the main window's toplevel, so rebuilding the panel does not close it."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh_now()
        _window.lift()
        return
    _window = CombatWindow(parent.winfo_toplevel(), book or C.book)


def close() -> None:
    global _window
    if _window is not None and _window.alive:
        _window.close()
    _window = None


# --- text (pure, so the figures can be checked without a window) ---------------------------------------------------------------------------------

def credits_text(amount: int) -> str:
    return f"{int(amount):,}"


def tally_cells(tally: Dict[str, int]) -> Tuple[str, str, str, str, str]:
    return (f"{tally['kills']:,}", f"{tally['pvp']:,}", f"{tally['deaths']:,}", C.ratio_text(tally), credits_text(tally["reward"]))


def ship_table_rows(rows: Sequence[Dict[str, Any]]) -> List[Tuple[str, ...]]:
    return [(C.ship_label(row, row["key"]), C.ship_title(row)) + tally_cells(row["tally"]) for row in rows]


def tiles_for(tally: Dict[str, int]) -> List[Tuple[str, str, str]]:
    """(value, caption, role) for the tiles over a table: role is a palette token name."""
    kills, pvp, deaths, ratio, reward = tally_cells(tally)
    return [
        (kills, "Kills", "OK" if tally["kills"] else "TEXT"),
        (pvp, "PvP kills", "TEXT"),
        (deaths, "Deaths", "DANGER" if tally["deaths"] else "TEXT"),
        (ratio, "K/D", "TEXT"),
        (reward, "Rewards (cr)", "TEXT"),
    ]


def started_text(stamp: str, current: bool) -> str:
    """'2026-10-20 10:00' (UTC, as the journal writes it), with ' (this session)' on the one being played."""
    try:
        when = time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
        text = time.strftime("%Y-%m-%d %H:%M", when)
    except ValueError:
        text = stamp[:16].replace("T", " ") or "Unknown"
    return text + (" (this session)" if current else "")


def subtitle_text(cmdr: str, total: Dict[str, int], sessions: int, reading: bool) -> str:
    if not cmdr:
        return "Waiting for your commander: log in or play first."
    text = f"{cmdr}: {C.summary_text(total)} in {sessions:,} session{'s' if sessions != 1 else ''}"
    return text + " (reading your journals...)" if reading else text


# --- the window --------------------------------------------------------------------------------------------------------------------------------------

class _Breakdown:
    """A row of tiles over a per-ship table."""

    def __init__(self, parent: tk.Misc, empty_text: str) -> None:
        self.frame = tk.Frame(parent, bg=P.PANE)
        self._tiles = TileRow(self.frame)
        self._tiles.pack(fill="x", padx=P.PAD, pady=(P.PAD, 0))
        self._signature: Optional[tuple] = None
        self.table = DataTable(self.frame, SHIP_COLUMNS, empty_text=empty_text)
        self.table.pack(fill="both", expand=True, padx=P.PAD, pady=P.PAD)

    def fill(self, tally: Dict[str, int], rows: Sequence[Dict[str, Any]]) -> None:
        tiles = tiles_for(tally)
        if tuple(tiles) != self._signature:
            self._signature = tuple(tiles)
            for child in self._tiles.winfo_children():
                child.destroy()
            for value, caption, role in tiles:
                StatTile(self._tiles, value, caption, getattr(P, role, P.TEXT))
            self._tiles.arrange(force=True)
        self.table.set_rows(ship_table_rows(rows))


class CombatWindow:
    def __init__(self, parent: tk.Misc, book: C.CombatBook) -> None:
        self._book = book
        self._signature: Optional[tuple] = None
        self._selected_session = ""
        self._session_ids: List[str] = []
        self._shell = WindowShell(
            parent, "Combat Record", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Combat Record help", _HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Refresh", self.refresh_now, tip="Refresh - redraw the figures")
        self._shell.add_action("Rebuild from journals", self._rebuild, tip="Rebuild from journals - clear this commander's record and read every journal again")

        self._tabs = Tabs(self._shell.body)
        self._tabs.pack(fill="both", expand=True)
        self._session = _Breakdown(self._tabs.add("This session"), "No kill or death yet this session.")
        self._session.frame.pack(fill="both", expand=True)
        self._all = _Breakdown(self._tabs.add("All time"), "No kill or death recorded yet.")
        self._all.frame.pack(fill="both", expand=True)

        sessions_tab = self._tabs.add("Sessions")
        pane = tk.Frame(sessions_tab, bg=P.PANE)
        pane.pack(fill="both", expand=True, padx=P.PAD, pady=P.PAD)
        self._sessions = DataTable(pane, SESSION_COLUMNS, on_select=self._on_pick, empty_text="No session with a kill or a death yet.", visible_rows=8)
        self._sessions.pack(fill="x")
        self._detail_note = NoteLabel(pane, padx=0)
        self._detail_note.pack(fill="x", pady=(P.PAD, P.PAD_SM))
        self._detail = DataTable(pane, SHIP_COLUMNS, empty_text="Select a session to see its ships.")
        self._detail.pack(fill="both", expand=True)

        self._tabs.select(0)
        self._draw()
        self._shell.window.after(POLL_MS, self._poll)

    # --- the window -----------------------------------------------------------------------------------------------------------------------------
    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._shell.close()

    def refresh_now(self) -> None:
        self._signature = None
        self._draw()

    def _rebuild(self) -> None:
        if not self._book.cmdr:
            self._shell.set_status("Waiting for your commander: log in or play first.")
            return
        self._book.rebuild(self._book.cmdr)
        self.refresh_now()

    def _poll(self) -> None:
        if not self.alive:
            return
        self._draw()
        self._shell.window.after(POLL_MS, self._poll)

    def _on_pick(self, session_id: str) -> None:
        self._selected_session = session_id
        self._draw_detail()

    # --- drawing --------------------------------------------------------------------------------------------------------------------------------
    def _draw(self) -> None:
        if not self.alive:
            return
        book = self._book
        signature = (book.revision, book.cmdr, book.session_id, book.reading)
        if signature == self._signature:
            return
        self._signature = signature
        try:
            cmdr = book.cmdr
            total = book.total(cmdr)
            sessions = book.sessions(cmdr)
            now = book.session_id
            self._session.fill(book.session_total(cmdr, now), book.ship_rows(cmdr, now) if now else [])
            self._all.fill(total, book.ship_rows(cmdr))
            self._sessions.clear()
            self._session_ids = [s["id"] for s in sessions]
            for session in sessions:
                self._sessions.insert(session["id"], (started_text(session["start"], session["id"] == now),) + tally_cells(session["tally"]))
            if self._selected_session not in self._session_ids:
                self._selected_session = self._session_ids[0] if self._session_ids else ""
            if self._selected_session:
                self._sessions.select(self._selected_session)
            self._draw_detail()
            self._shell.set_subtitle(subtitle_text(cmdr, total, len(sessions), book.reading))
            self._shell.set_status("Reading your journals for earlier play..." if book.reading else "")
        except Exception:
            logger.warning("The Combat Record window could not redraw", exc_info=True)

    def _draw_detail(self) -> None:
        cmdr, chosen = self._book.cmdr, self._selected_session
        session = next((s for s in self._book.sessions(cmdr) if s["id"] == chosen), None)
        if session is None:
            self._detail_note.configure(text="")
            self._detail.set_rows([])
            return
        self._detail_note.configure(text=f"{started_text(session['start'], session['id'] == self._book.session_id)}: {C.summary_text(session['tally'])}")
        self._detail.set_rows(ship_table_rows(self._book.ship_rows(cmdr, chosen)))
