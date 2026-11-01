"""
The Surface Mining Book (the BOOK button on the Surface Mining page; the Space Mining Book is `mining_ring_book.py`) - Mine mode's three-pane window - bodies on the left,
a body's saved hotspots in the middle, and a detail card with a map on the
right. Built on the shared kit in plugin/uikit (see
docs/WINDOW_FRAMEWORK_SPEC.md).

Singleton, like the other WFMT windows (module-level show/refresh/close,
saved geometry). It lists what this session's journal scan has shown for
the current system plus every saved hotspot, anywhere; the data shaping is in
mining_ledger_data.py (tested), this file is only widgets.

No "Guide me there" button: the Surface Compass (surface_compass.py) points at the nearest saved hotspot on the current body by
default, or at a mark of the commander's own; there is no per-hotspot target to set.
"""
from __future__ import annotations

import dataclasses
import logging
import os
import threading
import tkinter as tk
from typing import Optional

from config import appname, config

from . import edsm_client
from . import mining_coverage as coverage
from . import mining_body_cache
from . import mining_body_lookup as body_lookup
from . import mining_deposit
from . import mining_depletion as depletion
from . import mining_hotspot_dialog as hotspot_dialog
from . import mining_hotspots as hotspots
from . import mining_live_position as live_position
from . import mining_ground
from . import mining_history, mining_location
from . import mining_ledger_data as data
from . import mining_market_research_dialog as market_research
from . import mining_what_pays_dialog as what_pays
from . import mining_share as share
from . import mining_stops as stops
from . import mining_surface as surface_mining
from . import panelkit
from .mining_body_survey import system_body_survey
from .uikit import dialogs
from .uikit import palette as P
from .uikit import style
from .uikit.mapview import MapCircle, MapMarker, MapView
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Card, Combobox, FlatButton, FoldList, Pill, StatTile, TileRow, clip, section_header

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_mining_ledger_geometry"
CONFIG_STOP_RADIUS = "wfmt_mining_stop_radius_m"

_DENSITY_COLORS = {"High": "OK", "Medium": "WARN", "Low": "DANGER"}   # palette token names, read when drawn
_AMOUNT_COLORS = {"High": "OK", "Medium": "WARN", "Low": "DANGER", "Depleted": "MUTED"}

_PROSPECT_COLUMNS = (
    Column("material", "Material", 150, stretch=True, max_chars=28),
    Column("pct", "Share", 80, anchor="e"),
    Column("count", "Recorded", 90, anchor="e"),
    Column("saved", "Saved", 60, anchor="center"),
)

JOURNAL_TICK_MS = 1500

_window: Optional["MiningBook"] = None


def show(parent: tk.Misc) -> None:
    """Open the browser, or raise it (and refresh) if it's already open.
    Parented on the main window's toplevel - the panel rebuilds its own
    content frame every second, which would destroy a child of it."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return
    _window = MiningBook(parent.winfo_toplevel())


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def _spot_ident(spot: hotspots.Hotspot) -> tuple:
    return (spot.system, spot.body, spot.material, spot.latitude, spot.longitude)


class MiningBook:
    def __init__(self, root: tk.Misc) -> None:
        self._shell = WindowShell(
            root, "Surface Mining Book", "", min_size=(1100, 520),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Add hotspot", self._add_hotspot, accent=True,
                                tip="Add hotspot - save a hotspot; your system, body and position are filled in when you are on the ground")
        self._shell.add_action("Market research", self._market_research,
                                tip="Market research - find markets that buy what you could mine on the selected body (Spansh)")
        self._shell.add_action("What pays", self._what_pays,
                                tip="What pays - rank the commodities you could mine by the best price nearby (Spansh)")
        self._shell.add_action("Get body info", self._get_body_info,
                                tip="Get body info - fill in the system's landable bodies from online records (EDSM and Spansh)")
        self._shell.add_action("Paste spot", self._paste_spot,
                                tip="Paste spot - add a hotspot from a Share line copied to the clipboard")
        self._shell.add_action("This system", self._find_here,
                                tip="This system - go to the body you have worked in the system you are in")

        self._body_entry: Optional[data.BodyEntry] = None
        self._entries: dict[str, data.BodyEntry] = {}
        self._spot_by_key: dict[str, hotspots.Hotspot] = {}
        self._selected_spot: Optional[hotspots.Hotspot] = None
        self._rates = mining_ground.OwnRates([])

        panes = tk.PanedWindow(self._shell.body, orient="horizontal", bg=P.BG, bd=0, sashwidth=6, sashrelief="flat", opaqueresize=True)
        panes.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._panes = panes

        left = tk.Frame(panes, bg=P.PANE)
        section_header(left, "Bodies").pack(fill="x")
        filter_row = tk.Frame(left, bg=P.PANE, padx=P.PAD, pady=P.PAD_SM)
        filter_row.pack(fill="x")
        self._material = Combobox(filter_row, state="readonly", values=[data.ALL_MATERIALS])
        self._material.current(0)
        self._material.pack(fill="x")
        self._material.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self._rigs = Combobox(filter_row, state="readonly", values=[data.ANY_RIGS])
        self._rigs.current(0)
        self._rigs.pack(fill="x", pady=(P.PAD_SM, 0))
        self._rigs.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self._bodies = FoldList(left, on_select=self._select_body)
        self._bodies.pack(fill="both", expand=True)
        panes.add(left, stretch="always", minsize=220)

        middle = tk.Frame(panes, bg=P.PANE)
        self._middle_title = section_header(middle, "Hotspots")
        self._middle_title.pack(fill="x")
        tiles = TileRow(middle)
        tiles.pack(fill="x", padx=P.PAD, pady=P.PAD_SM)
        self._tiles = tiles
        self._tile_saved = StatTile(tiles, "0", "hotspots")
        self._tile_mined = StatTile(tiles, "0 t", "mined here", P.ACCENT)
        self._tile_active = StatTile(tiles, "0", "not depleted", P.OK)
        tiles.arrange()
        self._materials = tk.Label(middle, text="", bg=P.PANE, fg=P.MUTED, anchor="w", justify="left",
                                   padx=P.PAD)
        self._materials.pack(fill="x", pady=(0, P.PAD_SM))
        middle.bind("<Configure>", lambda e: self._materials.configure(wraplength=max(e.width - 2 * P.PAD, 120)))
        self._stops_label = tk.Label(middle, text="", bg=P.PANE, fg=P.ACCENT, anchor="w", justify="left", padx=P.PAD)
        middle.bind("<Configure>", lambda e: self._stops_label.configure(wraplength=max(e.width - 2 * P.PAD, 120)), add="+")
        self._prospect_head = tk.Frame(middle, bg=P.PANE, padx=P.PAD)
        self._prospect_title = tk.Label(self._prospect_head, text="", bg=P.PANE, fg=P.MUTED, anchor="w",
                                        font=style.font(P.FONT_SMALL))
        self._prospect_title.pack(side="left")
        self._prospect_table = DataTable(middle, _PROSPECT_COLUMNS, visible_rows=5)
        self._prospect_note = tk.Label(middle, text="", bg=P.PANE, fg=P.FAINT, anchor="w", justify="left",
                                       padx=P.PAD, font=style.font(P.FONT_SMALL))
        middle.bind("<Configure>", lambda e: self._prospect_note.configure(wraplength=max(e.width - 2 * P.PAD, 120)), add="+")
        self._hotspots = FoldList(middle, on_select=self._select_spot, single_open=False)
        self._hotspots.pack(fill="both", expand=True)
        panes.add(middle, stretch="always", minsize=220)

        right = tk.Frame(panes, bg=P.PANE, padx=P.PAD, pady=P.PAD)
        self._card = Card(right)
        self._card.pack(fill="x")
        self._map = MapView(right, size=280, on_select=self._select_spot)
        self._map.pack(fill="both", expand=True, pady=(P.PAD, 0))
        panes.add(right, stretch="always", minsize=int(330 * style.dpi_factor(self._shell.window)))

        self._shell.window.after(50, self._set_sashes)
        hotspots.hotspot_repository.add_listener(self._on_repo_changed)
        self._journal_sig: Optional[tuple] = None
        self.refresh(select_current=True)
        if not mining_history.history.ready:
            self._shell.set_status("Reading your journals for mining locations and tons refined (once, in the background). The list grows as it goes.")
        self._shell.window.after(JOURNAL_TICK_MS, self._journal_tick)

    # --- lifecycle ------------------------------------------------------------
    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        hotspots.hotspot_repository.remove_listener(self._on_repo_changed)
        self._shell.close()

    def _set_sashes(self) -> None:
        """Initial pane widths (set once the window has its real size)."""
        total = self._panes.winfo_width()
        if total > 600:
            self._panes.sash_place(0, int(total * 0.28), 0)
            self._panes.sash_place(1, int(total * 0.65), 0)

    @staticmethod
    def _reading_text() -> str:
        """What the journal read is doing: empty once the history is ready."""
        history = mining_history.history
        if history.reading:
            return history.reading.replace("for the mining history", "for mining locations and tons")
        return "" if history.ready else "Reading your journals…"

    def _journal_signature(self) -> tuple:
        bodies = mining_history.history.bodies().values()
        return (len(bodies), sum(int(b.get("tons") or 0) for b in bodies), sum(int(b.get("locations") or 0) for b in bodies))

    def _journal_tick(self) -> None:
        """While the journals are read for the first time, say so in the subtitle and redraw only when the list from the journals has changed (so the window does not flicker)."""
        if not self.alive:
            return
        history = mining_history.history
        signature = self._journal_signature()
        if signature != self._journal_sig:
            self.refresh()
        else:
            self._show_subtitle()
        if history.reading or not history.ready:
            self._shell.window.after(JOURNAL_TICK_MS, self._journal_tick)
        elif self._shell._status.cget("text").startswith("Reading your journals"):
            self._shell.set_status("Finished reading your journals.")

    def _show_subtitle(self) -> None:
        surface = surface_mining.surface_mining_repository
        current_system = surface.current_system or system_body_survey.current_system
        reading = self._reading_text()
        self._shell.set_subtitle((current_system or "No system yet") + (f"  ·  {reading}" if reading else ""))

    def _find_here(self) -> None:
        """Go to the body in the system you are in that you have worked (saved hotspots, tons refined, or mining locations found); say so when there is none."""
        surface = surface_mining.surface_mining_repository
        system = mining_location.current_system() or surface.current_system or system_body_survey.current_system
        if not system:
            self._shell.set_status("WFMT does not know your current system yet: jump or log in first.")
            return
        for box in (self._material, self._rigs):                 # a filter would hide the match
            box.current(0)
        self.refresh()
        here = [e for e in self._entries.values() if e.system.casefold() == system.casefold() and (e.saved_count or e.refined_tons or e.mining_signal_count)]
        if not here:
            self._shell.set_status("You have not worked this system yet.")
            return
        here.sort(key=lambda e: (-e.saved_count, -e.refined_tons, -(e.mining_signal_count or 0), e.body.casefold()))
        best = here[0]
        group = self._group_of.get(best.key)
        if group:
            self._bodies.open_group(group)
        self._bodies.select(best.key, notify=False)
        self._select_body(best.key)
        self._bodies.after_idle(lambda: self._bodies.see(best.key))
        self._shell.set_status(f"{system}: {len(here)} bod{'y' if len(here) == 1 else 'ies'} you have worked here. Showing {best.short_name}.")

    def _on_repo_changed(self) -> None:
        if self.alive:
            self._shell.window.after_idle(self.refresh)

    # --- data -> widgets -------------------------------------------------------
    def refresh(self, select_current: bool = False) -> None:
        """Re-read everything and redraw, keeping the selected body and
        hotspot where they still exist."""
        if not self.alive:
            return
        hotspots.hotspot_repository.settle_depletion(notify=False)   # marks that came due while the Book was shut
        saved = hotspots.hotspot_repository.all()
        surface = surface_mining.surface_mining_repository
        current_system = surface.current_system or system_body_survey.current_system
        self._journal_sig = self._journal_signature()
        self._show_subtitle()

        # Your own rates: rebuilt from the saved hotspots on every refresh
        # (one cheap pass), counting hotspots saved before they carried a
        # ground via this session's scanned bodies.
        from . import mining_panel                    # the panel owns seeding the body list from what is already known (also done on arrival)
        mining_panel.controller.seed_bodies(current_system)
        surveyed = system_body_survey.landable_bodies()
        self._rates = mining_ground.OwnRates(saved, mining_ground.survey_grounds(surveyed, current_system))

        materials = data.materials_in(saved)
        self._material.configure(values=materials)
        if self._material.get() not in materials:
            self._material.current(0)

        rig_labels = data.rig_labels(saved)
        self._rigs.configure(values=rig_labels)
        if self._rigs.get() not in rig_labels:
            self._rigs.current(0)

        groups = data.build_body_groups(current_system, surveyed, saved,
                                        self._material.get(), data.rigs_from_label(self._rigs.get()), self._rates, mining_history.history.bodies())
        self._entries = {}
        self._group_of: dict[str, str] = {}
        rows_by_group = []
        for group_key, heading, entries in groups:
            rows = []
            for entry in entries:
                self._entries[entry.key] = entry
                self._group_of[entry.key] = group_key
                title = entry.short_name if group_key not in ("other-systems", "journal") else f"{entry.system} · {entry.short_name}" if entry.system else entry.body
                bits = []
                if entry.rate_pct is not None:
                    bits.append(f"{entry.rate_pct:.0f}% of your recorded deposits here are {self._material.get()}")
                if entry.mining_signal_count is not None:
                    bits.append(f"{entry.mining_signal_count} mining location(s)")
                if entry.refined_tons:
                    bits.append(f"{entry.refined_tons:,} t refined")
                sub = "  ·  ".join(bits)
                rows.append(dict(key=entry.key, title=title, sub=sub,
                                 pill=(f"{entry.saved_count} saved", P.ACCENT) if entry.saved_count else None))
            rows_by_group.append((group_key, f"{heading}  ({len(entries)})", rows))
        open_before = self._bodies.open_keys()
        self._bodies.populate(rows_by_group, keep_scroll=True)
        for group_key in open_before:
            self._bodies.open_group(group_key)

        wanted = self._body_entry.key if self._body_entry else None
        if select_current or wanted not in self._entries:
            wanted = self._current_body_key(surface) or next(iter(self._entries), None)
        if wanted in self._entries:
            for group_key, _heading, entries in groups:
                if any(e.key == wanted for e in entries):
                    self._bodies.open_group(group_key)
            self._bodies.select(wanted, notify=False)
            self._show_body(self._entries[wanted])
        else:
            self._body_entry = None
            self._show_body(None)

    @staticmethod
    def _current_body_key(surface: surface_mining.SurfaceMiningRepository) -> Optional[str]:
        if surface.current_system and surface.current_body:
            return f"{surface.current_system}|{surface.current_body}"
        return None

    def _select_body(self, key: str) -> None:
        entry = self._entries.get(key)
        if entry is not None:
            self._selected_spot = None
            self._show_body(entry)

    def _show_body(self, entry: Optional[data.BodyEntry]) -> None:
        self._body_entry = entry
        previous = _spot_ident(self._selected_spot) if self._selected_spot else None
        self._selected_spot = None
        self._spot_by_key = {}
        if entry is None:
            self._middle_title.configure(text="HOTSPOTS")
            self._hotspots.populate([])
            for tile, text in ((self._tile_saved, "0"), (self._tile_mined, "0 t"), (self._tile_active, "0")):
                tile.set(text)
            self._tiles.arrange()
            self._draw_materials([])
            self._draw_stops([], None)
            self._show_prospecting(False)
            self._map.set_message("Nothing to show yet")
            self._render_card(None)
            return

        self._middle_title.configure(text=f"HOTSPOTS  ·  {clip(entry.short_name, 28).upper()}")
        saved = hotspots.hotspot_repository.all()
        spots = data.spots_on(saved, entry.system, entry.body)
        position_of = {id(h): i for i, h in enumerate(saved)}  # identity, not equality: duplicates compare equal
        radius, live = self._body_ground(entry)
        found = stops.find_stops(spots, radius, self._stop_radius())
        best = stops.best_stops(found)
        stop_number = {id(m): n for n, stop in enumerate(best, 1) for m in stop.members}
        here_spot = data.deposit_here(spots, live[0], live[1], radius) if live and radius else None
        groups = []
        for label, group_spots in data.group_by_location(spots):
            rows = []
            for spot in group_spots:
                key = str(position_of[id(spot)])
                self._spot_by_key[key] = spot
                estimate = mining_deposit.reserve_text(spot.rigs, spot.amount, spot.density, spot.mined_tons)
                bits = ["you are here"] if spot is here_spot else []
                bits += [f"{spot.rigs} rigs"] if spot.rigs else []
                bits.append(estimate or ("assumed refilled" if spot.regrown_at else "no estimate"))
                if id(spot) in stop_number:
                    bits.append(f"stop {stop_number[id(spot)]}")
                rows.append(dict(key=key, title=spot.material, indent=10, sub="  ·  ".join(bits),
                                 detail=f"{spot.mined_tons:,} t" if spot.mined_tons else "",
                                 pill=(spot.amount, getattr(P, _AMOUNT_COLORS.get(spot.amount, "MUTED"))) if spot.amount else None))
            groups.append((label, label, rows))
        self._hotspots.populate(groups, keep_scroll=True)
        for label, _heading, _rows in groups:
            self._hotspots.open_group(label)

        summary = data.summarize(spots)
        self._tile_saved.set(str(summary.saved))
        self._tile_mined.set(f"{max(summary.mined_tons, entry.refined_tons):,} t")      # the journals' total for the body is never less than what was credited to its deposits
        self._tile_active.set(str(summary.still_active))
        self._tiles.arrange()
        self._draw_materials(spots)
        self._draw_stops(found, radius)
        self._draw_prospecting(entry, spots)
        self._draw_map(entry, spots, best)

        reselect = next((k for k, s in self._spot_by_key.items() if _spot_ident(s) == previous), None)
        if reselect is None and here_spot is not None:
            reselect = next((k for k, s in self._spot_by_key.items() if s is here_spot), None)   # stand at one: it is the one to act on
        if reselect:
            self._select_spot(reselect)
        else:
            self._render_card(None)

    def _draw_materials(self, spots: list[hotspots.Hotspot]) -> None:
        """One line summarizing what's saved on this body (your own records):
        "Monazite ×2 · Painite ×1 · +2 more"."""
        lines = data.material_summary(spots)
        text = "  ·  ".join(f"{clip(m.material, 24)} ×{m.hotspots}" for m in lines[:6])
        if len(lines) > 6:
            text += f"  ·  +{len(lines) - 6} more"
        self._materials.configure(text=text)

    @staticmethod
    def _stop_radius() -> int:
        return stops.clamp_radius(config.get_int(CONFIG_STOP_RADIUS, default=stops.DEFAULT_RADIUS_M))

    @staticmethod
    def _body_ground(entry: data.BodyEntry) -> tuple[Optional[float], Optional[tuple[float, float]]]:
        """(the body's radius, the Rhino's position on it), each None unless you are on this body now."""
        surface = surface_mining.surface_mining_repository
        here = (surface.current_system or "").casefold() == entry.system.casefold() and \
               (surface.current_body or "").casefold() == entry.body.casefold()
        if not here:
            return None, None
        position = live_position.current_position()
        return surface.radius_for_current_body(), ((position.latitude, position.longitude) if position else None)

    def _draw_stops(self, found: list[stops.Stop], radius: Optional[float]) -> None:
        """The best stops (see mining_stops.py), or a note on why there are none to show."""
        best = stops.best_stops(found)
        lines = []
        for number, stop in enumerate(best, 1):
            tons = stop.tons_left()
            text = f"Stop {number}: {stop.rigs} rigs at {data.location_label(stop.lead)}, {len(stop.members)} deposit(s)"
            if tons:
                text += f", ~{tons[0]:,}-{tons[1]:,} t left"
            lines.append(text)
        if lines:
            lines.insert(0, f"Best stops (deposits within {self._stop_radius():,} m of the lead):")
        elif radius is None:
            lines = ["Stops need the body's radius: visit the body to see them."]
        self._stops_label.configure(text="\n".join(lines))
        if lines:
            self._stops_label.pack(fill="x", pady=(0, P.PAD_SM), before=self._hotspots)
        else:
            self._stops_label.pack_forget()

    def _show_prospecting(self, visible: bool) -> None:
        for widget in (self._prospect_head, self._prospect_table, self._prospect_note):
            widget.pack_forget()
        if visible:
            before = self._hotspots
            self._prospect_head.pack(fill="x", pady=(0, 2), before=before)
            self._prospect_table.pack(fill="x", padx=P.PAD, pady=(0, 2), before=before)
            self._prospect_note.pack(fill="x", pady=(0, P.PAD_SM), before=before)

    def _draw_prospecting(self, entry: data.BodyEntry, spots: list[hotspots.Hotspot]) -> None:
        """Your own rates for this kind of body (see mining_ground.OwnRates):
        the share of the deposits you have recorded on this kind of ground
        that were each material. Hidden for a body we only know from a saved
        hotspot (no class to look up) and until something is recorded on
        this kind of ground."""
        rows = data.prospect_rows(self._rates, entry.ground, spots)
        if not rows:
            self._show_prospecting(False)
            return
        self._show_prospecting(True)
        self._prospect_title.configure(
            text=f"YOUR RECORDS  ·  {mining_ground.label(entry.ground).upper()}  ·  "
                 f"{self._rates.sample_size(entry.ground)} DEPOSITS RECORDED")
        self._prospect_table.clear()
        chosen = self._material.get().strip().casefold()
        if chosen and chosen != data.ALL_MATERIALS.casefold():
            rows = sorted(rows, key=lambda r: r.material.casefold() != chosen)  # the filtered material first
        for row in rows[:12]:
            self._prospect_table.append((row.material, f"{row.pct:.0f}%", row.count,
                                         "✓" if row.saved_here else ""))
        self._prospect_note.configure(
            text="Built only from deposits you have saved: what you have found so far on this kind of "
                 "body, not what this body holds. A small sample says little.")

    def _draw_map(self, entry: data.BodyEntry, spots: list[hotspots.Hotspot],
                  best: Optional[list[stops.Stop]] = None) -> None:
        surface = surface_mining.surface_mining_repository
        here = (surface.current_system or "").casefold() == entry.system.casefold() and \
               (surface.current_body or "").casefold() == entry.body.casefold()
        radius = surface.radius_for_current_body() if here else None
        if not radius:
            self._map.set_message("Map needs the body's radius - visit the body to see it here"
                                  if not here else "Body radius not known yet")
            return
        position = live_position.current_position() if here else None
        current = (position.latitude, position.longitude) if position else None
        body_coverage = coverage.coverage_repository.for_body(entry.system, entry.body)
        center = data.map_center(body_coverage, current, spots)
        if center is None:
            self._map.set_message("Nothing recorded on this body yet")
            return
        cover = [data.project_m(center[0], center[1], p.latitude, p.longitude, radius)
                 for p in (body_coverage.points if body_coverage else ())]
        markers = []
        for key, spot in self._spot_by_key.items():
            if spot.has_position():
                east, north = data.project_m(center[0], center[1], spot.latitude, spot.longitude, radius)
                label = str(spot.signal_number) if spot.signal_number is not None else ""
                markers.append(MapMarker(key, east, north, label, spot.amount == "Depleted"))
        you = data.project_m(center[0], center[1], current[0], current[1], radius) if current else None
        self._map.set_message(None)
        circles = []
        for number, stop in enumerate(best or (), 1):
            east, north = data.project_m(center[0], center[1], stop.lead.latitude, stop.lead.longitude, radius)
            circles.append(MapCircle(east, north, self._stop_radius(), f"Stop {number}"))
        self._map.set_data(cover, markers, you, circles)

    # --- selection / card --------------------------------------------------------
    def _select_spot(self, key: str) -> None:
        spot = self._spot_by_key.get(key)
        if spot is None:
            return
        self._selected_spot = spot
        self._hotspots.select(key, notify=False)
        self._map.select(key)
        self._render_card(spot)

    def _render_card(self, spot: Optional[hotspots.Hotspot]) -> None:
        for child in self._card.winfo_children():
            child.destroy()
        if spot is None:
            tk.Label(self._card, text="Select a hotspot", fg=P.MUTED, bg=P.CARD).pack(anchor="w")
            return
        tk.Label(self._card, text=clip(spot.material, 30), fg=P.TEXT, bg=P.CARD,
                 font=style.font(P.FONT_TITLE)).pack(anchor="w")
        subtitle = [data.location_label(spot)]
        if spot.rigs:
            subtitle.append(f"{spot.rigs} rigs")
        tk.Label(self._card, text="  ·  ".join(subtitle), fg=P.MUTED, bg=P.CARD).pack(anchor="w", pady=(0, 6))
        pills = tk.Frame(self._card, bg=P.CARD)
        pills.pack(anchor="w", pady=(0, 8))
        if spot.density:
            Pill(pills, f"{spot.density} density", getattr(P, _DENSITY_COLORS.get(spot.density, "MUTED"))).pack(side="left", padx=(0, 6))
        if spot.amount:
            Pill(pills, f"{spot.amount} amount", getattr(P, _AMOUNT_COLORS.get(spot.amount, "MUTED"))).pack(side="left")
        estimate = mining_deposit.reserve_text(spot.rigs, spot.amount, spot.density, spot.mined_tons)
        if estimate:
            tk.Label(self._card, text=estimate, fg=P.ACCENT, bg=P.CARD,
                     font=style.font(P.FONT_SECTION)).pack(anchor="w")
        status = depletion.status_text(spot, depletion.now_utc(), hotspots.hotspot_repository.refill_days)
        if status:
            tk.Label(self._card, text=status, fg=P.MUTED, bg=P.CARD, wraplength=300,
                     justify="left").pack(anchor="w")
        if spot.mined_tons:
            tk.Label(self._card, text=f"{spot.mined_tons:,} t mined so far", fg=P.MUTED, bg=P.CARD).pack(anchor="w")
        if spot.has_position():
            tk.Label(self._card, text=f"{spot.latitude:.4f}, {spot.longitude:.4f}", fg=P.MUTED,
                     bg=P.CARD).pack(anchor="w")
        if spot.notes:
            tk.Label(self._card, text=clip(spot.notes, 120), fg=P.TEXT, bg=P.CARD, wraplength=300,
                     justify="left").pack(anchor="w", pady=(6, 0))
        buttons = tk.Frame(self._card, bg=P.CARD)
        buttons.pack(fill="x", pady=(10, 0))
        buttons.columnconfigure((0, 1), weight=1)
        actions = [("Mark depleted", self._mark_depleted, spot.amount != "Depleted", "Mark depleted - note that this deposit has run out"),
                   ("Copy coords", self._copy_coords, spot.has_position(), "Copy coords - copy the deposit's latitude and longitude to the clipboard"),
                   ("Share line", self._copy_share_line, share.can_share(spot), "Share line - copy one line describing this hotspot, to paste into Discord or another Mining Book"),
                   ("Edit", self._edit, True, "Edit - change this hotspot's details"),
                   ("Delete", self._delete, True, "Delete - remove this hotspot from your list")]
        for index, (text, command, enabled, tip) in enumerate(a for a in actions if a[2]):
            FlatButton(buttons, text, command, kind="danger" if text == "Delete" else "normal", tip=tip
                       ).grid(row=index // 2, column=index % 2, sticky="ew", padx=2, pady=2)

    # --- actions ---------------------------------------------------------------
    def _index_of(self, spot: hotspots.Hotspot) -> Optional[int]:
        for index, candidate in enumerate(hotspots.hotspot_repository.all()):
            if candidate is spot:
                return index
        return None

    def _mark_depleted(self) -> None:
        spot = self._selected_spot
        index = self._index_of(spot) if spot else None
        if spot is not None and index is not None:
            hotspots.hotspot_repository.update(index, dataclasses.replace(spot, amount="Depleted"))
            self._shell.set_status(f"{spot.material} marked depleted")

    def _copy_share_line(self) -> None:
        """One line of text for someone else's Mining Book (see mining_share.py): no name, notes, tons or dates in it."""
        spot = self._selected_spot
        if spot is None or not share.can_share(spot):
            return
        radius = self._body_ground(self._body_entry)[0] if self._body_entry else None
        if panelkit.copy_to_clipboard(self._shell.window, share.encode(spot, radius)):
            self._shell.set_status("Share line copied: paste it into Discord, or into another Mining Book with Paste spot")

    def _paste_spot(self) -> None:
        """Takes in a line copied with Share line, after checking it and asking."""
        try:
            text = self._shell.window.clipboard_get()
        except tk.TclError:
            text = ""
        try:
            shared = share.decode(text)
        except share.ShareError as err:
            self._shell.set_status(str(err))
            return
        entry_radius = None
        if self._body_entry and self._body_entry.system.casefold() == shared.hotspot.system.casefold()                 and self._body_entry.body.casefold() == shared.hotspot.body.casefold():
            entry_radius = self._body_ground(self._body_entry)[0]
        duplicate = share.find_duplicate(shared, hotspots.hotspot_repository.all(), entry_radius)
        if duplicate is not None:
            self._shell.set_status(f"You already have {duplicate.material} within {hotspots.SAME_SPOT_M:.0f} m of that spot")
            return
        spot = shared.hotspot
        rigs = f", {spot.rigs} rigs" if spot.rigs else ""
        if not dialogs.confirm(self._shell.window, "Paste spot", f"Add {spot.material}{rigs} on {spot.body} ({spot.system})?"):
            return
        hotspots.hotspot_repository.add(spot)
        self._shell.set_status(f"Added {spot.material} on {spot.body}")

    def _copy_coords(self) -> None:
        spot = self._selected_spot
        if spot is not None and spot.has_position():
            if panelkit.copy_to_clipboard(self._shell.window, f"{spot.latitude:.4f}, {spot.longitude:.4f}"):
                self._shell.set_status("Coordinates copied")

    def _edit(self) -> None:
        spot = self._selected_spot
        index = self._index_of(spot) if spot else None
        if spot is None or index is None:
            return
        hotspot_dialog.open_hotspot_dialog(
            self._shell.window, existing=spot,
            on_save=lambda updated, i=index: hotspots.hotspot_repository.update(i, updated))

    def _delete(self) -> None:
        spot = self._selected_spot
        index = self._index_of(spot) if spot else None
        if spot is None or index is None:
            return
        if dialogs.confirm(self._shell.window, "Delete hotspot", f"Delete {spot.material} on {spot.body}?"):
            hotspots.hotspot_repository.remove(index)
            self._shell.set_status("Hotspot deleted")

    def _market_research(self) -> None:
        """Markets in the selected body's system (else the current one) that buy what you could mine there."""
        if not market_research.enabled():
            self._shell.set_status("Turn on Enable Spansh best price finder in Settings > Mining to use Market research")
            return
        surface = surface_mining.surface_mining_repository
        current = surface.current_system or system_body_survey.current_system
        system = self._body_entry.system if self._body_entry else current
        if not system:
            self._shell.set_status("No system yet: market research needs one")
            return
        surveyed = system_body_survey.landable_bodies() if current and system.casefold() == current.casefold() else []
        market_research.open_dialog(self._shell.window, system, surveyed, self._rates)

    def _get_body_info(self) -> None:
        """Ask EDSM and Spansh for the current system's landable bodies (kind, volcanism, size and mining-location count) and add what the journals never gave, for a body scanned in a session whose journal is gone."""
        if not body_lookup.enabled():
            self._shell.set_status("Turn on Enable body lookup in Settings > Mining to use Get body info")
            return
        surface = surface_mining.surface_mining_repository
        system = surface.current_system or system_body_survey.current_system or mining_location.current_system()
        if not system:
            self._shell.set_status("No system yet: Get body info needs one (jump or log in first)")
            return
        address = mining_location.current_address()
        self._shell.set_status(f"Asking EDSM{' and Spansh' if address else ''} for the bodies in {system}...")

        def worker() -> None:
            """Runs off the main thread: it must not touch any Tk widget."""
            raw = edsm_client.system_bodies(system)
            dump = body_lookup.fetch_spansh(address)
            try:
                self._shell.window.after(0, lambda: self._body_info_done(system, raw, dump, address))
            except (tk.TclError, RuntimeError):
                pass                                        # the window closed while the services were answering

        threading.Thread(target=worker, daemon=True, name="WFMT-mining-edsm-bodies").start()

    def _body_info_done(self, system: str, raw: Optional[list], dump: Optional[dict], address: Optional[int]) -> None:
        if not self.alive:
            return
        if raw is None and dump is None:
            self._shell.set_status("Neither EDSM nor Spansh answered. Check your connection and try again (see the EDMC log)."
                                   if address else "EDSM did not answer. Check your connection and try again (see the EDMC log).")
            return
        bodies = body_lookup.merge(body_lookup.parse_edsm(raw), body_lookup.parse_spansh(dump))
        applied = body_lookup.apply(system, bodies, system_body_survey, surface_mining.surface_mining_repository)
        mining_body_cache.cache.remember(system, bodies)
        self._shell.set_status(body_lookup.message(system, applied, asked_spansh=dump is not None, address_known=address is not None))
        self.refresh()

    def _what_pays(self) -> None:
        """The commodities you could mine, ranked by the best price Spansh shows, within a distance of the system you are in."""
        if not what_pays.enabled():
            self._shell.set_status("Turn on Enable Spansh best price finder in Settings > Mining to use What pays")
            return
        surface = surface_mining.surface_mining_repository
        current = surface.current_system or system_body_survey.current_system or ""
        surveyed = system_body_survey.landable_bodies() if current else []
        what_pays.open_dialog(self._shell.window, current, surveyed, self._rates)

    def _add_hotspot(self) -> None:
        from . import mining_render
        mining_render.open_add_hotspot_dialog(self._shell.window)
