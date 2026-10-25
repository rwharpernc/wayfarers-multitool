"""The Check Ring Reserve Level window (the RES button on the Space Mining page): the reserve level and ring type EDSM has for a system's rings, with a warning for a ring that is not Metallic.

Type a system (it starts as the one you are in) and, if you want one body, its name or a ring's name (it starts as the ring you are in); leave the name empty to list every ringed body in the system.
The results fill a table: the ring, the body it circles, the body's reserve level (Pristine, Major, Common, Low, Depleted) and the ring's type, with a note on each ring that is not Metallic, since
premium laser-mined yields are usually best on Metallic rings. Double-click a row, or press **Copy system** or **Copy ring**, to put a name on the clipboard. Opt-in through "Enable EDSM ring
reserve lookup" in Settings; the network call is in the shared `edsm_client.py` (`system_bodies()`), and the only thing sent is the system name, when you press Search.

The passive counterpart is the ring-caution line on the Space Mining page (`mining_render.py`), fed automatically on every drop into a ring; `parse_ringed_bodies` and `find_body_or_ring` below
are shared with it (`mining_panel.py`). This window is for looking a ring up by name without flying there. Built on the shared window kit (plugin/uikit); the lookup runs on a worker thread and the
result is picked up by an after() poll, so no widget is touched off the main thread. `fetch_bodies` is a module-level name so tests can replace it.
"""
import logging
import os
import queue
import threading
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from config import appname, config

from . import edsm_client, panelkit, system_autocomplete
from . import mining_location as location
from . import mining_rings_data
from . import mining_space as space_mining
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import FlatButton, NoteLabel, clip

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_mining_reserve_lookup_geometry"
DEFAULT_SIZE = (940, 560)
MIN_SIZE = (760, 420)
POLL_MS = 200
NOT_METALLIC = "Not Metallic: premium laser-mined yields are usually best on Metallic rings"
METALLIC = "Metallic"

fetch_bodies = edsm_client.system_bodies

METALLIC_RING_TYPES = frozenset({"Metallic"})
"""Community knowledge, not journal/API-documented fact - like
mining_methods.py's commodity table, this needs the same kind of manual
upkeep as the game's ring-composition mechanics evolve. Premium-metal
laser-mining yields are generally best on Metallic rings; Metal Rich,
Rocky and Icy rings are the ones a "non-metallic ring" warning should
flag, hence only "Metallic" itself is excluded here."""


@dataclass
class RingInfo:
    name: str
    ring_type: str

    def is_metallic(self) -> bool:
        return self.ring_type in METALLIC_RING_TYPES


@dataclass
class BodyInfo:
    """One ringed body in a system, parsed from edsm_client.system_bodies()'s
    raw response. `reserve_level` is None for a body EDSM has on file
    without ring reserve data (rare, but the API doesn't guarantee every
    ringed body has it filled in)."""
    name: str
    reserve_level: Optional[str]
    rings: List[RingInfo]


def parse_ringed_bodies(raw_bodies: List[Dict[str, Any]]) -> List[BodyInfo]:
    """Filters `edsm_client.system_bodies()`'s raw list down to bodies
    that actually have rings, parsed into BodyInfo/RingInfo. Kept as
    Mining-specific parsing (not part of the shared edsm_client.py)
    since no other WFMT mode needs this shape. Public (not
    underscore-prefixed): mining_panel.py's automatic ring-reserve
    lookup (`_check_ring_reserve()`) reuses this directly rather than
    duplicating the same parse."""
    bodies: List[BodyInfo] = []
    for body in raw_bodies:
        rings = body.get("rings") or []
        if not rings:
            continue
        bodies.append(BodyInfo(
            name=body.get("name", "?"),
            reserve_level=body.get("reserveLevel"),
            rings=[RingInfo(name=r.get("name", "?"), ring_type=r.get("type", "?")) for r in rings],
        ))
    return bodies


def find_body_or_ring(bodies: List[BodyInfo], name: str) -> Optional[BodyInfo]:
    """Matches `name` case-insensitively against either a body's own name
    or any of its ring names - a commander is as likely to type the ring
    name off their nav panel ("Jupiter Halo Ring") as the body name
    ("Jupiter")."""
    query = name.strip().casefold()
    if not query:
        return None
    for body in bodies:
        if body.name.strip().casefold() == query:
            return body
        if any(ring.name.strip().casefold() == query for ring in body.rings):
            return body
    return None


_COLUMNS = (
    Column("ring", "Ring", 260, stretch=True, max_chars=52),
    Column("body", "Body", 180, max_chars=40),
    Column("reserve", "Reserve level", 130),
    Column("type", "Ring type", 110),
    Column("note", "Laser mining", 340, stretch=True, max_chars=80),
)

_window: Optional["ReserveWindow"] = None


def open_reserve_lookup_dialog(parent: tk.Misc) -> None:
    """Open the window, or raise it if it is open. Parented on the main window's toplevel: the Mining panel rebuilds its own content frame, which would take a window parented there with it."""
    global _window
    if _window is not None and _window.alive:
        _window.lift()
        return
    _window = ReserveWindow(parent.winfo_toplevel())


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def result_rows(bodies: List[BodyInfo]) -> List[Tuple[str, str, str, str, str]]:
    """One table row per ring: (ring, body, reserve level, ring type, the laser-mining note). The reserve level reads `Pristine`, not EDSM's `PristineResources`; a body EDSM has none for reads `Unknown`."""
    rows = []
    for body in bodies:
        for ring in body.rings:
            rows.append((ring.name, body.name, mining_rings_data.reserve_text(body.reserve_level) or "Unknown", ring.ring_type, METALLIC if ring.is_metallic() else NOT_METALLIC))
    return rows


class ReserveWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self._busy = False
        self._results: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self._rows: Dict[str, Tuple[str, str]] = {}
        self._shell = WindowShell(
            parent, "Check Ring Reserve Level", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Copy ring", lambda: self._copy("ring"))
        self._shell.add_action("Copy system", lambda: self._copy("system"))
        body = self._shell.body

        first = tk.Frame(body, bg=P.BG)
        first.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(first, text="System", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._system = tk.StringVar(value=location.current_system() or "")
        entry = tk.Entry(first, textvariable=self._system, width=30)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        system_autocomplete.attach(entry, self._system)
        entry.bind("<Return>", lambda _e: self._search())
        FlatButton(first, "Here", self._fill_here).pack(side="left")

        second = tk.Frame(body, bg=P.BG)
        second.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(second, text="Body or ring", fg=P.MUTED, bg=P.BG).pack(side="left")
        tracked = space_mining.space_mining_repository.current_ring()
        self._name = tk.StringVar(value=tracked[1] if tracked else "")
        name_entry = tk.Entry(second, textvariable=self._name, width=38)
        name_entry.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        name_entry.bind("<Return>", lambda _e: self._search())
        self._search_button = FlatButton(second, "Search", self._search, kind="accent")
        self._search_button.pack(side="left", padx=(0, P.PAD))
        NoteLabel(second, "Leave empty to list every ringed body in the system.", fg=P.MUTED, bg=P.BG, padx=0).pack(side="left", fill="x", expand=True)

        self._heading = tk.Label(body, text="", fg=P.MUTED, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD))
        self._heading.pack(fill="x", pady=(P.PAD_SM, 0))
        self._table = DataTable(body, _COLUMNS, on_activate=lambda _iid: self._copy("system"), empty_text="Type a system and press Search.")
        self._table.tag_configure("warn", foreground=P.WARN)
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._say("Pressing Search sends EDSM the system name, nothing else. Double-click a row to copy its system.")

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

    def _fill_here(self) -> None:
        self._system.set(location.current_system() or "")

    # --- the lookup ---------------------------------------------------------------------------------------------------

    def _search(self) -> None:
        if self._busy:
            return
        system = " ".join(self._system.get().split())
        name = " ".join(self._name.get().split())
        if not system:
            self._say("Type a system, or press Here (your system is not known yet).")
            return
        self._busy = True
        self._search_button.set_enabled(False)
        self._say(f"Asking EDSM about {clip(system, 40)}...")
        threading.Thread(target=self._worker, args=(system, name), daemon=True, name="WFMT-mining-edsm-search").start()
        self._shell.window.after(POLL_MS, self._poll)

    def _worker(self, system: str, name: str) -> None:
        """Runs off the main thread: it must not touch any Tk widget."""
        try:
            raw = fetch_bodies(system)
        except Exception:
            logger.exception("EDSM reserve lookup failed")
            raw = None
        if raw is None:
            logger.warning("EDSM reserve lookup failed for %r", system)
            self._results.put(("failed", "The lookup failed. Check your connection and try again (see the EDMC log)."))
            return
        bodies = parse_ringed_bodies(raw)
        if not name:
            self._results.put(("ok", (system, name, bodies)))
            return
        match = find_body_or_ring(bodies, name)
        self._results.put(("ok", (system, name, [match] if match else [])))

    def _poll(self) -> None:
        """Runs on the main thread via after(): safe to touch widgets."""
        try:
            outcome, payload = self._results.get_nowait()
        except queue.Empty:
            if self.alive and self._busy:
                self._shell.window.after(POLL_MS, self._poll)
            return
        self._busy = False
        if not self.alive:
            return
        self._search_button.set_enabled(True)
        if outcome != "ok":
            self._say(str(payload))
            return
        self._fill_results(*payload)

    def _fill_results(self, system: str, name: str, bodies: List[BodyInfo]) -> None:
        self._table.clear()
        self._rows = {}
        rows = result_rows(bodies)
        for number, (ring, body, reserve, ring_type, note) in enumerate(rows):
            iid = f"r{number}"
            self._rows[iid] = (ring, system)
            self._table.insert(iid, (clip(ring, 52), clip(body, 40), reserve, ring_type, note), tag=None if note == METALLIC else "warn")
        self._shell.set_subtitle(system)
        if not rows:
            self._heading.configure(text="")
            self._say(f"EDSM has no ringed body named {clip(name, 40)} in {clip(system, 40)}." if name else f"EDSM has no ringed body on file in {clip(system, 40)}.")
            return
        if name:
            scope = f"{clip(bodies[0].name, 40)} in {clip(system, 40)}"
        else:
            scope = f"the {len(bodies)} ringed bod{'y' if len(bodies) == 1 else 'ies'} in {clip(system, 40)}"
        self._heading.configure(text=f"Rings of {scope}")
        warned = sum(1 for row in rows if row[4] != METALLIC)
        self._say(f"{len(rows)} ring{'s' if len(rows) != 1 else ''}" + (f", {warned} not Metallic (shown in amber)." if warned else ", all Metallic.")
                  + " Double-click a row to copy its system.")

    def _copy(self, what: str) -> None:
        chosen = self._table.selection()
        held = self._rows.get(chosen[0]) if chosen else None
        if held is None:
            self._say("Select a row first.")
            return
        text = held[0] if what == "ring" else held[1]
        ok = panelkit.copy_to_clipboard(self._shell.window, text)
        self._say(f"Copied {text}." if ok else "Could not reach the clipboard.")
