"""The Find Nearby Hotspots window (the H.S. button on the Space Mining page): the nearest rings Spansh confirms have a hotspot for a material, closest first.

Type a material, say how far to look and the system to search from (it starts as the one you are in), then press **Search**. The results fill a table you can sort by any column: the ring and the
body it circles, the system, how many hotspots of that material the ring has, the distance in light years, the distance from the arrival star and the body's reserve level. Double-click a row, or
press **Copy system**, **Copy body** or **Copy ring**, to put a name on the clipboard for the galaxy map. Opt-in through "Enable Spansh nearby hotspot finder" in Settings; the network call is
`mining_spansh_client.search_ring_hotspots`, and the only thing sent is the system name and the material, when you press Search.

Built on the shared window kit (plugin/uikit), like the Find Best Price window. The lookup runs on a worker thread and the result is picked up by an after() poll, so no widget is touched off the
main thread. `search_rings` is a module-level name so tests can replace it. Only one window is open at a time.
"""
from __future__ import annotations

import logging
import os
import queue
import threading
import tkinter as tk
from typing import Any, Dict, Optional, Tuple

from config import appname, config

from . import mining_location as location
from . import mining_spansh_client as spansh_client
from . import spansh_courtesy
from . import panelkit, system_autocomplete
from .uikit import palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, FlatButton, NoteLabel, clip

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_mining_hotspot_finder_geometry"
DEFAULT_SIZE = (1040, 580)
MIN_SIZE = (840, 420)
POLL_MS = 200
MAX_RESULTS = 25

DEFAULT_WHERE = "Within 100 ly"
WHERE_CHOICES: Tuple[Tuple[str, float], ...] = (
    ("Within 25 ly", 25.0), ("Within 50 ly", 50.0), (DEFAULT_WHERE, 100.0), ("Within 250 ly", 250.0), ("Within 500 ly", 500.0), ("Within 1,000 ly", 1000.0))

search_rings = spansh_client.search_ring_hotspots

_window: Optional["HotspotFinderWindow"] = None

_COLUMNS = (
    Column("ring", "Ring", 220, stretch=True, max_chars=52),
    Column("body", "Body", 170, max_chars=40),
    Column("system", "System", 170, max_chars=36),
    Column("count", "Hotspots", 90, anchor="e"),
    Column("distance", "Distance (ly)", 110, anchor="e"),
    Column("arrival", "Arrival (ls)", 100, anchor="e"),
    Column("reserve", "Reserve level", 130),
)


def open_hotspot_finder_dialog(parent: tk.Misc) -> None:
    """Open the window, or raise it if it is open. Parented on the main window's toplevel: the panels rebuild their own content frames, which would take a window parented there with it."""
    global _window
    if _window is not None and _window.alive:
        here = location.current_system()
        if here and not _window._origin.get():
            _window._origin.set(here)
        _window.lift()
        return
    _window = HotspotFinderWindow(parent.winfo_toplevel())


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def distance_for(label: str) -> float:
    """The furthest to look in light years for a "Within" choice; 100 ly for anything unknown."""
    return dict(WHERE_CHOICES).get(label, 100.0)


def row_values(hotspot: spansh_client.RingHotspot) -> Tuple[str, ...]:
    return (clip(hotspot.ring_name, 52), clip(hotspot.body, 40), clip(hotspot.system, 36), f"{hotspot.hotspot_count:,}", f"{hotspot.distance_ly:,.1f}",
            f"{hotspot.distance_to_arrival_ls:,.0f}", clip(hotspot.reserve_level, 24))


def heading_text(material: str, where: str, reference: str) -> str:
    return f"Rings with {clip(material, 40)} hotspots, {where.lower()} of {clip(reference, 40)}"


class HotspotFinderWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self._busy = False
        self._results: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self._shown: Dict[str, spansh_client.RingHotspot] = {}
        self._shell = WindowShell(
            parent, "Find Nearby Hotspots", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Copy ring", lambda: self._copy("ring"))
        self._shell.add_action("Copy body", lambda: self._copy("body"))
        self._shell.add_action("Copy system", lambda: self._copy("system"))
        body = self._shell.body

        first = tk.Frame(body, bg=P.BG)
        first.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(first, text="Material", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._material = tk.StringVar()
        # Editable: the list is every material confirmed to work, but a name that is in neither list is still allowed (a hotspot material Spansh or the game adds later).
        Combobox(first, textvariable=self._material, values=list(spansh_client.KNOWN_RING_HOTSPOT_MATERIALS), width=26).pack(side="left", padx=(P.PAD_SM, P.PAD))
        tk.Label(first, text="Where", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._where = tk.StringVar(value=DEFAULT_WHERE)
        Combobox(first, textvariable=self._where, values=[name for name, _ in WHERE_CHOICES], state="readonly", width=16).pack(side="left", padx=(P.PAD_SM, 0))

        second = tk.Frame(body, bg=P.BG)
        second.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(second, text="Search from", fg=P.MUTED, bg=P.BG).pack(side="left")
        self._origin = tk.StringVar(value=location.current_system() or "")
        entry = tk.Entry(second, textvariable=self._origin, width=34)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD_SM))
        system_autocomplete.attach(entry, self._origin)
        entry.bind("<Return>", lambda _e: self._search())
        FlatButton(second, "Here", self._fill_here).pack(side="left")
        self._search_button = FlatButton(second, "Search", self._search, kind="accent")
        self._search_button.pack(side="left", padx=(P.PAD, 0))

        self._heading = NoteLabel(body, fg=P.MUTED, bg=P.BG, font=P.FONT_BOLD, padx=0)
        self._heading.pack(fill="x", pady=(P.PAD_SM, 0))
        self._table = DataTable(body, _COLUMNS, on_activate=lambda _iid: self._copy("system"), empty_text="Type a material and press Search.")
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._shell.set_subtitle(f"Near {self._origin.get()}" if self._origin.get() else "Waiting for your current system (jump or log in)")
        self._say("Pressing Search sends Spansh the system name and the material, nothing else. Click a heading to sort; double-click a row to copy its system.")
        self._shell.window.bind("<Return>", lambda _e: self._search())

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
        self._origin.set(location.current_system() or "")

    # --- the lookup ---------------------------------------------------------------------------------------------------

    def _search(self) -> None:
        if self._busy:
            return
        material = " ".join(self._material.get().split())
        origin = " ".join(self._origin.get().split())
        if not material:
            self._say("Type a material to search for.")
            return
        if not origin:
            self._say("Type the system to search from, or press Here (your system is not known yet).")
            return
        where = self._where.get()
        self._busy = True
        self._search_button.set_enabled(False)
        self._say(f"Asking Spansh about {clip(material, 40)} hotspots near {clip(origin, 40)}...")
        threading.Thread(target=self._worker, args=(origin, material, distance_for(where), where), daemon=True, name="WFMT-mining-spansh-search").start()
        self._shell.window.after(POLL_MS, self._poll)

    def _worker(self, origin: str, material: str, distance: float, where: str) -> None:
        """Runs off the main thread: it must not touch any Tk widget."""
        try:
            found = search_rings(origin, material, distance, max_results=MAX_RESULTS)
            self._results.put(("ok", (found, origin, material, where)))
        except Exception as exc:
            logger.exception("Spansh hotspot search failed")
            self._results.put(("failed", str(exc) if isinstance(exc, spansh_courtesy.SpanshBusy) else "The search failed. Check your connection and try again (see the EDMC log)."))

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

    def _fill_results(self, found: list, origin: str, material: str, where: str) -> None:
        self._table.clear()
        self._shown = {}
        self._heading.configure(text=heading_text(material, where, origin))
        self._shell.set_subtitle(f"Near {origin}")
        for number, hotspot in enumerate(found):
            iid = f"h{number}"
            self._shown[iid] = hotspot
            self._table.insert(iid, row_values(hotspot))
        if found:
            self._say(f"{len(found)} found, closest first. Click a heading to sort; double-click a row to copy its system.")
        else:
            self._say("No ring with that hotspot within range. Try a longer distance, or check the material's spelling.")

    def _copy(self, what: str) -> None:
        chosen = self._table.selection()
        hotspot = self._shown.get(chosen[0]) if chosen else None
        if hotspot is None:
            self._say("Select a row first.")
            return
        text = {"system": hotspot.system, "body": hotspot.body, "ring": hotspot.ring_name}[what]
        ok = panelkit.copy_to_clipboard(self._shell.window, text)
        self._say(f"Copied {text}." if ok else "Could not reach the clipboard.")
