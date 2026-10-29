"""GEC Nearby POI: an on-demand "find the nearest catalogued point of
interest" lookup against edastro.com's (Elite Dangerous Astrometrics) GEC
API - see gec_poi_edastro.py and docs/ATTRIBUTIONS.md.

Deliberately **manual, not automatic-on-jump**: a button-triggered lookup
rather than a live call firing on every FSDJump, so
this never fires on its own and stays well clear of edastro's published
rate limit (100 requests/15 min) even on long multi-jump exploration runs.
No opt-in/opt-out setting is needed as a result - there's no passive
network activity to gate, unlike exploration_value.py's ELW-rarity/EDSM-
upload readouts.

It is one half of the POI Reference section (poi_reference_panel.py), which owns the
FIND button, the clipboard and the section's frame; this controller owns the edastro
lookup and its result line.
"""

from __future__ import annotations

import logging
import os
import queue
import threading
from typing import Any, Callable, Dict, Mapping, Optional, Tuple
from urllib.parse import quote

import tkinter as tk

import myNotebook as nb
from config import appname
from ttkHyperlinkLabel import HyperlinkLabel

from . import gec_poi_edastro, journal_files, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

_IDLE_TEXT = "GEC: (jump into a system, then click FIND)"
_NO_POSITION_TEXT = "GEC: current position unknown — jump or reload first"
_CHECKING_TEXT = "GEC: checking edastro.com (the first lookup downloads their list)..."
_ERROR_TEXT = "GEC: lookup failed — see EDMarketConnector.log"


class GecPoiController:
    def __init__(self) -> None:
        self._star_pos: Optional[Tuple[float, float, float]] = None

        self._result_var: Optional[tk.StringVar] = None
        # Called as (system, distance_ly) when a lookup ends, (None, None) when it found nothing.
        self.on_done: Optional[Callable[[Optional[str], Optional[float]], None]] = None
        self._link_label: Optional[HyperlinkLabel] = None
        self._action_row: Optional[tk.Frame] = None
        self._copy_button: Optional[tk.Button] = None
        self._system: Optional[str] = None      # the system of the result on show, for COPY
        self._parent: Optional[tk.Frame] = None

        # Worker-thread + queue.Queue + after()-polling plumbing, same
        # pattern as exploration_value.py's own opt-in network lookups.
        # Generation counter lets a later click supersede an in-flight one.
        self._generation = 0
        self._result_queue: "queue.Queue[Tuple[int, Optional[gec_poi_edastro.NearestPoi], Optional[str]]]" = queue.Queue()

    # --- journal dispatch -----------------------------------------------

    def handle_event(self, entry: Mapping[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        event = entry.get("event")
        if event == "StartUp":
            # EDMC started with the game running: it replays nothing, so take the position from the current journal.
            self._star_pos = self._star_pos or self._position_from_journal()
            return
        if event not in ("FSDJump", "Location", "CarrierJump"):
            return
        star_pos = entry.get("StarPos")
        if (isinstance(star_pos, list) and len(star_pos) == 3
                and all(isinstance(v, (int, float)) for v in star_pos)):
            self._star_pos = tuple(star_pos)

    @staticmethod
    def _position_from_journal() -> Optional[Tuple[float, float, float]]:
        """The last `StarPos` in the newest journal file (the one being played), or None."""
        try:
            files = journal_files.files_modified_since(0.0)
            if not files:
                return None
            found = None
            for event in journal_files.read_events(files[-1], journal_files.event_pattern("FSDJump", "Location", "CarrierJump")):
                pos = event.get("StarPos")
                if isinstance(pos, list) and len(pos) == 3 and all(isinstance(v, (int, float)) for v in pos):
                    found = (float(pos[0]), float(pos[1]), float(pos[2]))
            return found
        except Exception:
            logger.exception("GEC Nearby POI: couldn't read the current journal for a position")
            return None

    # --- lookup -----------------------------------------------------------

    def start_lookup(self, force_refresh: bool = False) -> bool:
        """Starts a lookup; True when one is running (its end is reported through `on_done`), False when it could not start."""
        if self._star_pos is None:
            if self._result_var is not None:
                self._result_var.set(_NO_POSITION_TEXT)
            return False

        self._generation += 1
        generation = self._generation
        if self._result_var is not None:
            self._result_var.set(_CHECKING_TEXT)
        self._system = None
        if self._action_row is not None:
            self._action_row.grid_remove()

        x, y, z = self._star_pos
        threading.Thread(target=self._worker, args=(generation, x, y, z), daemon=True).start()
        return True

    def _worker(self, generation: int, x: float, y: float, z: float) -> None:
        """Runs off the main thread — must not touch any Tk widget directly."""
        result: Optional[gec_poi_edastro.NearestPoi] = None
        error: Optional[str] = None
        try:
            result = gec_poi_edastro.find_nearest_poi(x, y, z)
        except Exception:
            logger.exception("gec_poi_panel lookup failed for (%s, %s, %s)", x, y, z)
            error = "lookup failed"
        self._result_queue.put((generation, result, error))

    def _poll_queue(self) -> None:
        """Runs on the main thread via after() — safe to touch widgets here."""
        try:
            generation, result, error = self._result_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            if generation == self._generation:
                found: Tuple[Optional[str], Optional[float]] = (None, None)
                if error:
                    if self._result_var is not None:
                        self._result_var.set(_ERROR_TEXT)
                elif result is not None and self._result_var is not None:
                    rating = f", rating {result.rating:.1f}" if result.rating is not None else ""
                    where = f" in {result.system}" if result.system else ""
                    self._result_var.set(
                        f"Nearby POI: {result.name} ({result.category}){where} — "
                        f"{result.distance_ly:,.1f} ly, {result.region}{rating}"
                    )
                    found = (result.system, result.distance_ly)
                    self._system = result.system or None
                    if self._copy_button is not None:
                        self._copy_button.config(state=tk.NORMAL if self._system else tk.DISABLED)
                    # Some results carry no URL; fall back to the system's Inara search, or hide the link when there is no system either.
                    url = result.url or (f"https://inara.cz/elite/starsystem/?search={quote(result.system)}" if result.system else None)
                    if self._link_label is not None:
                        if url:
                            self._link_label.configure(url=url)
                            self._link_label.pack(side=tk.LEFT, padx=(8, 0))
                        else:
                            self._link_label.pack_forget()
                    if self._action_row is not None:
                        self._action_row.grid()
                if self.on_done is not None:
                    self.on_done(*found)
        if self._parent is not None:
            self._parent.after(200, self._poll_queue)

    # --- main-panel widgets -----------------------------------------------

    def build_rows(self, body: tk.Frame, row: int) -> int:
        """Builds the result line and its link into `body` from `row`; returns the next free row."""
        self._parent = body
        self._result_var = tk.StringVar(value=_IDLE_TEXT)
        panelkit.wrap_label(body, textvariable=self._result_var, anchor="w").grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(2, 0),
        )
        self._action_row = tk.Frame(body)
        self._action_row.grid(row=row + 1, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        self._copy_button = tk.Button(self._action_row, text="Copy System", command=self._copy_system)
        panelkit.add_tooltip(self._copy_button, "Copy System - copy this GEC result's system name to paste into the galaxy map")
        self._copy_button.pack(side=tk.LEFT)
        self._link_label = HyperlinkLabel(
            self._action_row, text="View on edastro.com", background=nb.Label().cget("background"), underline=True,
        )
        self._link_label.pack(side=tk.LEFT, padx=(8, 0))
        self._action_row.grid_remove()
        body.after(200, self._poll_queue)
        return row + 2

    def _copy_system(self) -> None:
        if self._system and self._parent is not None:
            panelkit.copy_to_clipboard(self._parent, self._system)

    # --- Settings tab --------------------------------------------------

    def build_settings(self, notebook: nb.Notebook) -> None:
        frame = nb.Frame(notebook)
        frame.columnconfigure(0, weight=1)
        notebook.add(frame, text="GEC Nearby POI")

        nb.Label(frame, text="POI Reference: edastro GEC", font=("TkDefaultFont", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4),
        )
        nb.Label(
            frame,
            text=(
                "The POI Reference section's FIND button looks up the "
                "nearest catalogued point of interest to your current position, via edastro.com's "
                "(Elite Dangerous Astrometrics) Galactic Exploration Catalog. Manual only — this "
                "never makes a network call on its own, only when you click the button."
            ),
            wraplength=440, justify=tk.LEFT,
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 4))

        HyperlinkLabel(
            frame, text="edastro.com GEC", background=nb.Label().cget("background"),
            url="https://edastro.com/gec/", underline=True,
        ).grid(row=2, column=0, sticky=tk.W, padx=10, pady=(0, 10))

    def save_settings(self) -> None:
        pass


controller = GecPoiController()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_settings(notebook: nb.Notebook) -> None:
    controller.build_settings(notebook)


def save_settings() -> None:
    controller.save_settings()
