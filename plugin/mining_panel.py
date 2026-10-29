"""
Mining mode's feature-module contract entry point. Owns the panel's
persistent chrome (page nav between Space Mining/Surface Mining, the
scrollable Canvas/Scrollbar frame mirroring missions_ui.py's own
pattern, and the six persistent buttons (HOTSPOTS, PRICES, RESERVES, BOOK, DASHBOARD,
LIVE) - see their own docstring below for why they're never destroyed/recreated), the
Settings tab, and the full journal/dashboard dispatch. Per-page content
rendering lives in `mining_render.py`; HUD-overlay pushes live in
`mining_overlay.py`; the data models live in `mining_space.py`/
`mining_surface.py`/`mining_hotspots.py`.

`PANEL_PLACEMENT = "mining"` - this module's entry in `ui.py`'s FEATURES
tuple is what puts the panel in Mining mode.
"""
from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
from typing import Any, Dict, Optional

import myNotebook as nb
from config import appname, config

from . import edsm_client
from . import mining_alerts
from . import mining_body_survey as body_survey
from . import mining_ledger as ledger
from . import mining_rate
from . import mining_live_window as live_window
from . import mining_coverage as coverage
from . import mining_hotspot_finder_dialog as hotspot_finder_dialog
from . import mining_history_window as history_window
from . import mining_hotspot_settings
from . import mining_depletion as depletion
from . import mining_hotspots as hotspots
from . import mining_history
from . import mining_history_data
from . import mining_ring_book, mining_rings
from . import mining_journal_backfill as journal_backfill
from . import mining_live_position as live_position
from . import mining_market
from . import mining_location as location
from . import mining_overlay
from . import mining_rigs
from . import mining_radar_overlay
from . import mining_pages
from . import mining_price_finder_dialog as price_finder_dialog
from . import mining_render as render
from . import mining_reserve_lookup_dialog as reserve_lookup_dialog
from . import commodity_autocomplete
from . import mining_body_cache
from . import mining_spansh_client
from . import mining_body_lookup
from . import mining_session_archive as session_archive
from . import mining_simulation
from . import mining_stops
from . import mining_targets
from . import mining_space as space_mining
from . import mining_surface as surface_mining
from . import overlay
from . import panelkit
from . import system_survey

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "mining"

# --- Config keys (wfmt_mining_*) -------------------------------------------

_CFG_DISPLAY_SESSION_TOTALS = "wfmt_mining_display_session_totals"
_CFG_DISPLAY_CARGO_BAR = "wfmt_mining_display_cargo_bar"
_CFG_DISPLAY_PROSPECTOR_HINTS = "wfmt_mining_display_prospector_hints"
_CFG_SPANSH_HOTSPOT_FINDER_ENABLED = "wfmt_mining_spansh_hotspot_finder_enabled"
_CFG_SPANSH_PRICE_FINDER_ENABLED = "wfmt_mining_spansh_price_finder_enabled"
_CFG_EDSM_RESERVE_LOOKUP_ENABLED = "wfmt_mining_edsm_reserve_lookup_enabled"
_CFG_OVERLAY_ENABLED = "wfmt_mining_overlay_enabled"
_CFG_DISPLAY_COVERAGE_MINIMAP = "wfmt_mining_display_coverage_minimap"
_CFG_ARCHIVE_SESSIONS = "wfmt_mining_archive_sessions"
_CFG_CURRENT_PAGE = "wfmt_mining_current_page"
_CFG_STOP_RADIUS = "wfmt_mining_stop_radius_m"
_CFG_RIG_GAP = "wfmt_mining_rig_gap_m"
_CFG_REFILL_DAYS = "wfmt_mining_refill_days"

_MAX_PANEL_HEIGHT = 760
"""Hard cap on the scrollable content area's rendered height, in pixels
- past this the content scrolls internally instead of growing EDMC's
window. This bounds one axis; wraplength (panelkit.wrap_label-derived)
bounds the other. 760 is tall enough for the Surface page with a Rhino out
(the run's lines, the marks and deposits, the rig line and the button bar,
about 430 px in the simulation, more with the extra lines a real run adds) so the buttons show without scrolling;
the optional coverage minimap adds a picture and can still scroll."""

_CONTENT_RIGHT_MARGIN = 8
_WRAP_FALLBACK = 280
_PERIODIC_TICK_MS = 1000
"""How often the panel re-renders itself with no new journal event, so
the "Refining now" line (mining_rate.py) visibly decays back toward
zero during a mining lull rather than freezing at its last value."""



def _cfg_bool(key: str, default: bool) -> bool:
    return config.get_bool(key, default=default)


def _clamp_refill_days(value: object) -> int:
    try:
        return min(depletion.MAX_REGEN_DAYS, max(0, int(round(float(value)))))   # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _refill_days() -> int:
    return _clamp_refill_days(config.get_int(_CFG_REFILL_DAYS, default=0))


def _settings() -> render.PanelSettings:
    return render.PanelSettings(
        display_session_totals=_cfg_bool(_CFG_DISPLAY_SESSION_TOTALS, True),
        display_cargo_bar=_cfg_bool(_CFG_DISPLAY_CARGO_BAR, True),
        display_prospector_hints=_cfg_bool(_CFG_DISPLAY_PROSPECTOR_HINTS, True),
        spansh_hotspot_finder_enabled=_cfg_bool(_CFG_SPANSH_HOTSPOT_FINDER_ENABLED, False),
        spansh_price_finder_enabled=_cfg_bool(_CFG_SPANSH_PRICE_FINDER_ENABLED, False),
        edsm_reserve_lookup_enabled=_cfg_bool(_CFG_EDSM_RESERVE_LOOKUP_ENABLED, False),
        display_coverage_minimap=_cfg_bool(_CFG_DISPLAY_COVERAGE_MINIMAP, False),
        rig_gap_m=mining_stops.clamp_rig_gap(config.get_int(_CFG_RIG_GAP, default=0)),
    )


class MiningPanelController:
    def __init__(self) -> None:
        self._plugin_dir: Optional[str] = None
        self._parent: Optional[tk.Frame] = None
        self._nav: Optional[tk.Frame] = None
        self._page_label: Optional[tk.Label] = None
        self._canvas: Optional[tk.Canvas] = None
        self._scrollbar: Optional[tk.Scrollbar] = None
        self._content: Optional[tk.Frame] = None
        self._content_window: Optional[int] = None
        self._wrap = _WRAP_FALLBACK
        self._buttons: Optional[render.PanelButtons] = None
        self._current_page = config.get_str(_CFG_CURRENT_PAGE) or mining_pages.PAGE_ORDER[0]
        if self._current_page not in mining_pages.PAGE_ORDER:
            self._current_page = mining_pages.PAGE_ORDER[0]

        self._srv_out = False            # an SRV is out, from the journal's Cargo events (Vessel SRV) and their end: covers a Rhino launched before the journal in view began
        self._backfilling = False
        """True only while replaying today's journal file through
        handle_event() on a mid-session start. Guards the two side
        effects that only make sense for a live event: the automatic
        EDSM ring-reserve lookup (would otherwise fire once per ring
        visited today, hammering edsm.net on every EDMC restart) and
        session-archive writes (would otherwise re-archive a run an
        earlier EDMC process already wrote to disk, under a fresh
        now()-stamped filename each time)."""
        self._ring_reserve_cache: Dict[Any, Optional[space_mining.RingCaution]] = {}
        """(system, ring) -> the EDSM lookup result, keyed casefold -
        see _check_ring_reserve(). Ring composition/reserve level is
        static game data, so this never needs invalidating; it just
        stops repeated supercruise hops within the same belt from
        re-querying edsm.net every time."""

        # Settings-tab variables, populated in build_settings().
        self._display_session_totals_var: Optional[tk.BooleanVar] = None
        self._display_cargo_bar_var: Optional[tk.BooleanVar] = None
        self._display_prospector_hints_var: Optional[tk.BooleanVar] = None
        self._spansh_hotspot_finder_var: Optional[tk.BooleanVar] = None
        self._spansh_price_finder_var: Optional[tk.BooleanVar] = None
        self._edsm_reserve_lookup_var: Optional[tk.BooleanVar] = None
        self._edsm_body_lookup_var: Optional[tk.BooleanVar] = None
        self._overlay_enabled_var: Optional[tk.BooleanVar] = None
        self._radar_card_var: Optional[tk.BooleanVar] = None
        self._radar_size_var: Optional[tk.StringVar] = None
        self._radar_opacity_var: Optional[tk.StringVar] = None
        self._radar_result_label: Optional[tk.Label] = None
        self._overlay_result_label: Optional[tk.Misc] = None
        self._display_coverage_minimap_var: Optional[tk.BooleanVar] = None
        self._archive_sessions_var: Optional[tk.BooleanVar] = None
        self._stop_radius_var: Optional[tk.StringVar] = None
        self._rig_gap_var: Optional[tk.StringVar] = None
        self._target_var: Optional[tk.StringVar] = None
        self._target_percent_var: Optional[tk.StringVar] = None
        self._target_status: Optional[tk.Label] = None
        self._refill_days_var: Optional[tk.StringVar] = None

    # --- lifecycle -----------------------------------------------------

    def start(self, plugin_dir: str) -> None:
        self._plugin_dir = plugin_dir
        hotspots.hotspot_repository.refill_days = _refill_days()
        hotspots.hotspot_repository.load(plugin_dir)
        coverage.coverage_repository.load(plugin_dir)
        mining_body_cache.cache.load(plugin_dir)
        mining_history.history.start(plugin_dir)
        mining_rings.notes.start(plugin_dir)
        space_mining.space_mining_repository.add_listener(lambda _run: self._redraw_if_alive())
        surface_mining.surface_mining_repository.add_listener(lambda _run: self._redraw_if_alive())
        hotspots.hotspot_repository.add_listener(self._redraw_if_alive)
        try:
            from . import all_missions
            all_missions.view.changed.connect(lambda _missions: self._redraw_if_alive())     # the mission needs shown on the Space Mining page
        except Exception:
            logger.debug("Could not follow the missions for the Space Mining page", exc_info=True)

    def set_overlay_client(self, client: overlay.OverlayClient) -> None:
        mining_overlay.set_overlay_client(client)
        mining_radar_overlay.set_overlay_client(client)

    def stop(self) -> None:
        hotspots.hotspot_repository.flush()  # mined-ton counts are saved on a throttle, not per ton
        history_window.close()
        live_window.close()
        mining_ring_book.close()

    def _credit_mined_ton(self, surface_repo: surface_mining.SurfaceMiningRepository) -> None:
        """One refined ton -> the nearest recorded hotspot (see
        HotspotRepository.add_mined_tons). Skipped during journal
        backfill, where live position isn't available anyway."""
        position = live_position.current_position()
        radius = surface_repo.radius_for_current_body()
        system, body = surface_repo.current_system, surface_repo.current_body
        if self._backfilling or position is None or not radius or not system or not body:
            return
        hotspots.hotspot_repository.add_mined_tons(
            system, body, position.latitude, position.longitude, radius)

    # --- panel chrome ----------------------------------------------------

    def build_panel(self, parent: tk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)  # the scrollbar column keeps its natural width
        self._parent = parent

        self._nav = tk.Frame(parent)
        self._nav.grid(column=0, row=0, columnspan=2, sticky="ew")
        panelkit.nav_arrow(self._nav, -1, lambda: self._step_page(-1)).pack(side=tk.LEFT)
        self._page_label = tk.Label(self._nav, anchor=tk.CENTER, font=panelkit.view_fonts()["bold"])
        self._page_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        panelkit.nav_arrow(self._nav, 1, lambda: self._step_page(1)).pack(side=tk.LEFT)

        # width=1: a bare Canvas requests 10 cm of width, which would widen EDMC's window; it
        # stretches to the panel's width instead (sticky="ew").
        self._canvas = tk.Canvas(parent, width=1, highlightthickness=0, borderwidth=0, yscrollincrement=24)
        self._canvas.grid(column=0, row=1, sticky="ew")
        self._scrollbar = tk.Scrollbar(parent, orient="vertical", command=self._canvas.yview)
        self._scrollbar.grid(column=1, row=1, sticky="ns")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._content = tk.Frame(self._canvas)
        self._content.columnconfigure(0, weight=1)
        self._content_window = self._canvas.create_window((0, 0), window=self._content, anchor="nw")

        # These six buttons are created once and kept alive for the life
        # of the panel, unlike every other widget in self._content
        # (destroyed and rebuilt on every _redraw() call, including once
        # a second from the periodic tick). A plain tk.Button uses
        # native OS chrome, and destroying/recreating one every second
        # produces a visible flicker on Windows even when theme colors
        # come out right each time - see mining_render.py's
        # place_button_bar().
        # All six live in one frame (the "bar"), so a page can show them side by
        # side in a single row instead of one per row (render.place_button_bar).
        button_bar = tk.Frame(self._content)
        self._buttons = render.PanelButtons(
            bar=button_bar,
            hotspot_finder=tk.Button(
                button_bar, text="Hotspots",
                command=lambda: hotspot_finder_dialog.open_hotspot_finder_dialog(self._window_parent())),
            price_finder=tk.Button(
                button_bar, text="Prices",
                command=lambda: price_finder_dialog.open_price_finder_dialog(
                    self._window_parent(), suggested_commodities=self._current_run_refined_commodities())),
            reserve_lookup=tk.Button(
                button_bar, text="Reserves",
                command=lambda: reserve_lookup_dialog.open_reserve_lookup_dialog(self._window_parent())),
            ledger=tk.Button(
                button_bar, text="Book",
                command=self._open_book),
            history=tk.Button(
                button_bar, text="Dashboard",
                command=lambda: history_window.show(self._window_parent(), self._history_mode())),
            live=tk.Button(
                button_bar, text="Live",
                command=self._open_live),
        )
        for button, tip in (
                (self._buttons.hotspot_finder, "Hotspots - find rings with a confirmed hotspot for a commodity (Spansh)"),
                (self._buttons.price_finder, "Prices - find the best-paying station for a commodity (Spansh)"),
                (self._buttons.reserve_lookup, "Reserves - look up a ring's reserve level"),
                (self._buttons.ledger, "Mining Book - the Space Mining Book (your rings) on the Space page, the Surface Mining Book (Rhino deposits) on the Surface page"),
                (self._buttons.live, "Live view - a window to keep on a second screen: the radar, the live numbers and the controls (Mark center, Mark border, Add hotspot, Import/export) for this page"),
                (self._buttons.history, "Mining History - the runs found in your journals, added up for this page: ring mining on the Space page (tons, rates, commodities, rings and what the sales paid), the Rhino on the Surface page (by body)")):
            panelkit.add_tooltip(button, tip)
        for button in (self._buttons.hotspot_finder, self._buttons.price_finder, self._buttons.reserve_lookup,
                      self._buttons.ledger, self._buttons.history, self._buttons.live):
            button.grid_remove()

        self._content.bind("<Configure>", self._sync_scroll_region)
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind("<Enter>", lambda _e: self._bind_mousewheel())
        self._canvas.bind("<Leave>", lambda _e: self._unbind_mousewheel())

        self._redraw()
        parent.after(100, self._redraw_if_alive)
        parent.after(_PERIODIC_TICK_MS, self._periodic_tick)

    def _open_surface_simulation(self) -> None:
        """Settings → Mining → Simulation: the Surface Live window on pretend data."""
        mining_simulation.open_surface_live(self._window_parent(), _settings)

    def _open_live(self) -> None:
        """Live opens the live window for the page you are on: the radar and controls for the Rhino on the Surface page, the live numbers on the Space page."""
        live_window.show(self._window_parent(), self._current_page, _settings)

    def _window_parent(self) -> tk.Misc:
        """Where the panel's windows and dialogs hang from. Not `_content`: `_redraw` destroys every child of it, which would close an open window the moment the panel redraws."""
        return self._content.winfo_toplevel() if self._content is not None else self._parent

    def _history_mode(self) -> str:
        """Which half of the mining history Dashboard opens: the Rhino's on the Surface page, the rings' otherwise."""
        return mining_history_data.SURFACE if self._current_page == mining_pages.SURFACE_MINING else mining_history_data.SPACE

    def _open_book(self) -> None:
        """Book opens the book for the page you are on: rings on the Space Mining page, the Rhino's deposits on the Surface Mining page."""
        if self._current_page == mining_pages.SURFACE_MINING:
            ledger.show(self._window_parent())
        else:
            mining_ring_book.show(self._window_parent())

    def _redraw_if_alive(self) -> None:
        if self._parent is not None and self._parent.winfo_exists():
            self._redraw()

    def _periodic_tick(self) -> None:
        if self._parent is None or not self._parent.winfo_exists():
            return
        self._redraw()
        self._parent.after(_PERIODIC_TICK_MS, self._periodic_tick)

    def _on_canvas_resize(self, event: tk.Event) -> None:
        width = max(event.width - _CONTENT_RIGHT_MARGIN, 0)
        self._canvas.itemconfigure(self._content_window, width=width)
        if width > 1:
            self._wrap = max(width - 20, 80)

    def _sync_scroll_region(self, _event: Optional[tk.Event] = None) -> None:
        if self._canvas is None:
            return
        self._canvas.update_idletasks()
        bbox = self._canvas.bbox("all")
        content_height = (bbox[3] - bbox[1]) if bbox else 0
        self._canvas.configure(scrollregion=bbox, height=min(content_height, _MAX_PANEL_HEIGHT))
        if content_height > _MAX_PANEL_HEIGHT:
            self._scrollbar.grid()
        else:
            self._scrollbar.grid_remove()

    def _bind_mousewheel(self) -> None:
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self) -> None:
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event: tk.Event) -> None:
        if getattr(event, "num", None) == 4:
            self._canvas.yview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self._canvas.yview_scroll(3, "units")
        elif event.delta:
            self._canvas.yview_scroll(-3 if event.delta > 0 else 3, "units")

    def _step_page(self, direction: int) -> None:
        order = mining_pages.PAGE_ORDER
        idx = order.index(self._current_page)
        self._current_page = order[(idx + direction) % len(order)]
        config.set(_CFG_CURRENT_PAGE, self._current_page)
        self._redraw()

    def _current_run_refined_commodities(self) -> list:
        """Whichever page is showing when "Find Best Price..." is
        clicked, suggest commodities from *that* page's own current run
        - the button is shared since both mining types produce
        commodities worth a price check, but each page's `refined` dict
        lives on a different repository/run type."""
        if self._current_page == mining_pages.SURFACE_MINING:
            run = surface_mining.surface_mining_repository.current_run()
        else:
            run = space_mining.space_mining_repository.current_run()
        return list(run.refined.keys()) if run is not None else []

    def _redraw(self) -> None:
        if self._content is None or not self._content.winfo_exists():
            return

        frame_bg = self._parent.cget("background")

        kept = render.begin_lines(self._content)      # last time's text lines are reused where they have not changed, so the text does not flicker every second
        for child in self._content.winfo_children():
            if child is self._buttons.bar or child in kept:
                continue
            child.destroy()

        self._page_label.configure(text=self._current_page)
        settings = _settings()

        try:
            if self._current_page == mining_pages.SPACE_MINING:
                render.render_space_mining(self._content, self._wrap, self._buttons, settings)
            elif self._current_page == mining_pages.SURFACE_MINING:
                render.render_surface_mining(self._content, self._wrap, self._buttons, settings)
        finally:
            render.end_lines(self._content)

        if _cfg_bool(_CFG_OVERLAY_ENABLED, False):
            mining_overlay.push_stats_overlay(
                self._current_page, display_cargo_bar=settings.display_cargo_bar,
                display_session_totals=settings.display_session_totals,
                display_prospector_hints=settings.display_prospector_hints,
            )

        panelkit.apply_theme_deep(self._content)
        self._canvas.configure(background=frame_bg)
        self._content.configure(background=frame_bg)
        self._sync_scroll_region()

    # --- journal/dashboard dispatch --------------------------------------

    def handle_event(self, entry: Dict[str, Any], cmdr: Optional[str], system: Optional[str],
                     station: Optional[str], state: Dict[str, Any]) -> None:
        if cmdr:
            mining_history.history.set_commander(cmdr)
            mining_rings.notes.set_commander(cmdr)
            hotspots.hotspot_repository.set_commander(cmdr)
            coverage.coverage_repository.set_commander(cmdr)
            mining_body_cache.cache.set_commander(cmdr)
            space_mining.space_mining_repository.set_current_cmdr(cmdr)
            surface_mining.surface_mining_repository.set_current_cmdr(cmdr)
        location.set_current_system(system)
        if entry.get("event") in ("Location", "FSDJump", "CarrierJump"):
            location.set_current_address(entry.get("SystemAddress"))

        event = entry.get("event")
        space_repo = space_mining.space_mining_repository
        surface_repo = surface_mining.surface_mining_repository
        space_repo.update_limpets(mining_alerts.limpets_aboard(state))

        if event == "StartUp":
            # EDMC sends this synthetic event once, only when it's
            # started while the game is already running - the only
            # signal a mid-session start happened.
            self._backfill_from_journal(cmdr)

        elif event == "Market":
            mining_market.on_market(entry)              # the station's prices, to set against the galactic average on the Space page

        elif event == "Undocked":
            mining_market.clear()
            space_repo.start_new_run()
            space_repo.update_limpets(mining_alerts.limpets_aboard(state))      # the new run starts with the count EDMC already has

        elif event == "Docked":
            run = space_repo.current_run()
            if not self._backfilling and _cfg_bool(_CFG_ARCHIVE_SESSIONS, False) and run is not None and run.has_data():
                session_archive.archive_run(self._plugin_dir, "space", cmdr, run)

        elif event == "SupercruiseEntry":
            space_repo.pause_run()
            space_repo.set_current_ring(system, None)

        elif event == "SupercruiseExit":
            space_repo.resume_run()
            ring = entry.get("Body") if entry.get("BodyType") == "PlanetaryRing" else None
            space_repo.set_current_ring(system, ring)
            if ring and _cfg_bool(_CFG_EDSM_RESERVE_LOOKUP_ENABLED, False) and not self._backfilling:
                self._check_ring_reserve(system, ring)

        elif event == "LaunchSRV":
            if entry.get("SRVType") == surface_mining.RHINO_SRV_TYPE:
                surface_repo.start_run(entry.get("ID"))
                mining_rigs.rig_book.clear()                 # the rigs of the last deployment are gone

        elif event == "DockSRV":
            self._srv_out = False
            if entry.get("SRVType") == surface_mining.RHINO_SRV_TYPE:
                run = surface_repo.current_run()
                if run is not None and run.cargo:
                    # Docking the Rhino automatically transfers whatever's
                    # still in its hold to the ship - move it over
                    # directly rather than leaving the panel/overlay
                    # showing cargo that's no longer actually in the SRV
                    # (a later authoritative Cargo event, if one arrives,
                    # just overwrites this).
                    space_repo.adjust_cargo(run.cargo)
                    surface_repo.update_cargo(0)
                surface_repo.end_run(entry.get("ID"))
                mining_rigs.rig_book.clear()
                run = surface_repo.current_run()
                if (not self._backfilling and _cfg_bool(_CFG_ARCHIVE_SESSIONS, False)
                        and run is not None and run.has_data()):
                    session_archive.archive_run(self._plugin_dir, "surface", cmdr, run)

        elif event in ("SRVDestroyed", "Died"):
            self._srv_out = False
            surface_repo.force_end_run()
            mining_rigs.rig_book.clear()

        elif event == "ProspectedAsteroid":
            wanted, threshold = mining_alerts.load_target()
            space_repo.record_prospected(entry.get("Content", ""), entry.get("Content_Localised"),
                                         entry.get("Materials"), mining_alerts.rock_finding(entry, wanted, threshold), at=mining_rate.event_time(entry))

        elif event == "AsteroidCracked":
            space_repo.record_asteroid_cracked(at=mining_rate.event_time(entry))

        elif event == "LaunchDrone":
            space_repo.record_limpet(entry.get("Type", "Unknown"), at=mining_rate.event_time(entry))

        elif event == "BuyDrones":
            space_repo.record_limpets_bought(entry.get("Count", 0))

        elif event == "Loadout":
            capacity = entry.get("CargoCapacity")
            if isinstance(capacity, int):
                space_repo.update_cargo_capacity(capacity)

        elif event == "MiningRefined":
            # Same event for ship-based and Rhino mining - nothing in
            # the event itself says which. Route by whether a Rhino is
            # currently deployed.
            commodity = entry.get("Type_Localised") or entry.get("Type", "Unknown")
            if not surface_repo.is_active and (self._srv_out or (live_position.in_srv() and not self._backfilling)):
                surface_repo.adopt_run()       # a ton refined with an SRV out is the Rhino's, whether or not its launch was seen (EDMC or the game was restarted in it)
            at = mining_rate.event_time(entry)         # the event's own time: a journal replayed at start-up does not count a whole run as this second's
            if surface_repo.is_active:
                surface_repo.record_refined(commodity, at=at)
                self._credit_mined_ton(surface_repo)
            else:
                space_repo.record_refined(commodity, at=at)

        elif event == "Cargo":
            vessel = entry.get("Vessel")
            count = entry.get("Count", 0)
            if vessel == "Ship":
                space_repo.update_cargo(count)
                space_repo.update_live_cargo(None)         # the event is the newest word on the hold; the next Status.json update says again
                self._srv_out = False
            elif vessel == "SRV":
                surface_repo.update_cargo(count)
                self._srv_out = True

        elif event == "CargoTransfer":
            for transfer in entry.get("Transfers", []):
                if transfer.get("Direction") != "toship":
                    continue
                commodity = transfer.get("Type_Localised") or str(transfer.get("Type", "Unknown"))
                count = transfer.get("Count", 0)
                surface_repo.record_transfer_to_ship(commodity, count)
                space_repo.adjust_cargo(count)

        elif event == "MaterialCollected":
            if surface_repo.is_active:
                material = entry.get("Name_Localised") or str(entry.get("Name", "Unknown"))
                surface_repo.record_raw_material(material, entry.get("Count", 0))

        elif event == "SAASignalsFound":
            for signal in entry.get("Signals", []):
                if signal.get("Type") == surface_mining.MINING_LOCATION_SIGNAL_TYPE:
                    body_name = entry.get("BodyName", "?")
                    surface_repo.record_mining_location_signal(body_name, signal.get("Count", 0))
                    body_survey.system_body_survey.record_signal(system, body_name, signal.get("Count", 0))

        elif event == "FSSBodySignals":
            # the same mining-location count after a quick FSS scan, without flying out to the body; a later detailed scan replaces it
            for signal in entry.get("Signals", []):
                if signal.get("Type") == surface_mining.MINING_LOCATION_SIGNAL_TYPE:
                    body_survey.system_body_survey.record_signal(system, entry.get("BodyName", "?"), signal.get("Count", 0), detailed=False)

        elif event == "Location":
            body = entry.get("Body") if entry.get("BodyType") == "Planet" else None
            surface_repo.set_current_location(entry.get("StarSystem"), body)
            body_survey.system_body_survey.on_system_changed(entry.get("StarSystem"))
            self.seed_bodies(entry.get("StarSystem"))
            # A relog or an EDMC restart inside a ring starts with a Location, not a SupercruiseExit: the ring is set the same way.
            ring = entry.get("Body") if entry.get("BodyType") == "PlanetaryRing" else None
            ring_system = entry.get("StarSystem") or system
            space_repo.set_current_ring(ring_system, ring)
            if ring and ring_system and _cfg_bool(_CFG_EDSM_RESERVE_LOOKUP_ENABLED, False) and not self._backfilling:
                self._check_ring_reserve(ring_system, ring)

        elif event == "FSDJump":
            surface_repo.set_current_location(entry.get("StarSystem"), None)
            body_survey.system_body_survey.on_system_changed(entry.get("StarSystem"))
            self.seed_bodies(entry.get("StarSystem"))

        elif event == "ApproachBody":
            surface_repo.set_current_location(entry.get("StarSystem"), entry.get("Body"))

        elif event == "LeaveBody":
            surface_repo.set_current_location(entry.get("StarSystem"), None)

        elif event == "Touchdown":
            latitude, longitude = entry.get("Latitude"), entry.get("Longitude")
            if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
                surface_repo.record_touchdown(latitude, longitude)

        elif event == "Liftoff":
            surface_repo.clear_touchdown()

        elif event == "Scan":
            radius = entry.get("Radius")
            body_name = entry.get("BodyName")
            if isinstance(radius, (int, float)) and body_name:
                surface_repo.record_body_radius(body_name, radius)
            body_survey.system_body_survey.record_scan(
                system, body_name, entry.get("PlanetClass"), entry.get("Volcanism"),
                bool(entry.get("Landable", False)))

    def _backfill_from_journal(self, cmdr: str) -> None:
        """Replays today's journal file through handle_event() itself
        (the same method this is called from), so a mid-session EDMC
        start ends up with the same state as if EDMC had been running
        the whole time - the in-progress run, current cargo, current
        body (needed for the "Save Hotspot Here" button to even
        appear), last touchdown, etc. Reuses handle_event()'s own
        dispatch rather than duplicating it, since replaying an entry is
        exactly what handle_event() already does for a live one.

        `cmdr` starts as whatever EDMC's StartUp event carried, but a
        journal file can span more than one commander if the player
        switched account without restarting the game, so it's
        re-derived per `Commander` event while walking the file."""
        path = journal_backfill.find_current_journal_file()
        if path is None:
            return
        self._backfilling = True
        try:
            current_cmdr = cmdr
            current_system = ""
            for line_entry in journal_backfill.read_entries(path):
                event = line_entry.get("event")
                if event == "Commander":
                    name = line_entry.get("Name")
                    if name:
                        current_cmdr = name
                    continue
                system = line_entry.get("StarSystem")
                if system:
                    current_system = system
                self.handle_event(line_entry, current_cmdr, current_system, "", {})
        except Exception:
            logger.exception("Mining journal backfill failed")
        finally:
            self._backfilling = False
        self.seed_bodies(current_system or body_survey.system_body_survey.current_system)
        self._redraw_if_alive()

    def _check_ring_reserve(self, system: str, ring: str) -> None:
        """Automatic counterpart to mining_reserve_lookup_dialog.py's
        on-demand search - fired from `SupercruiseExit` when the
        "Enable EDSM ring reserve lookup" setting is on, so the passive
        Space Mining panel line doesn't need a button press. A cache hit
        resolves synchronously (main thread, no network call); a miss
        runs on a background thread, marshaling the result back via
        `after(0, ...)`."""
        key = (system.casefold(), ring.casefold())
        if key in self._ring_reserve_cache:
            space_mining.space_mining_repository.set_ring_caution(system, ring, self._ring_reserve_cache[key])
            return

        def _worker() -> None:
            raw_bodies = edsm_client.system_bodies(system)
            if raw_bodies is None:
                return
            bodies = reserve_lookup_dialog.parse_ringed_bodies(raw_bodies)
            match = reserve_lookup_dialog.find_body_or_ring(bodies, ring)
            caution = None
            if match is not None:
                ring_info = next(
                    (r for r in match.rings if r.name.strip().casefold() == ring.strip().casefold()), None)
                if ring_info is not None:
                    caution = space_mining.RingCaution(
                        ring_name=ring, reserve_level=match.reserve_level,
                        ring_type=ring_info.ring_type, is_metallic=ring_info.is_metallic())
            self._ring_reserve_cache[key] = caution
            if self._parent is not None and self._parent.winfo_exists():
                self._parent.after(0, lambda: space_mining.space_mining_repository.set_ring_caution(
                    system, ring, caution))

        threading.Thread(target=_worker, daemon=True, name="WFMT-mining-edsm-auto-lookup").start()

    def seed_bodies(self, system: Optional[str]) -> None:
        """Bring back the Mining body list of `system` from what is already known: the saved System targets survey and what Get body info remembered (no request is made)."""
        if not system:
            return
        try:
            mining_body_lookup.seed(system, body_survey.system_body_survey, surface_mining.surface_mining_repository, system_survey.survey, mining_body_cache.cache)
        except Exception:
            logger.debug("Could not seed the Mining body list for %s", system, exc_info=True)

    def dashboard_status(self, entry: Dict[str, Any]) -> None:
        """Status.json's live Latitude/Longitude/Heading - a separate
        hook from handle_event above, since Status.json isn't a
        discrete journal event (see mining_live_position.py's module
        docstring). The periodic tick picks up whatever this last
        recorded the next time it redraws, so there's no need to force
        a refresh here."""
        live_position.set_status(entry)
        # The ship's hold from the same entry, so the Hold line and the hold alert follow it without waiting for a Cargo event (see mining_alerts.status_hold for when it is taken).
        known, tons = mining_alerts.status_hold(entry, surface_mining.surface_mining_repository.is_active or self._srv_out)
        if known:
            space_mining.space_mining_repository.update_live_cargo(tons)
        mining_radar_overlay.update()         # the radar card over the game follows the Rhino (it is a no-op unless switched on)

        # Coverage minimap: only while a Rhino is actually deployed
        # (surface_mining_repository.is_active, set from LaunchSRV/
        # DockSRV journal events - not Status.json's own SRV flag, no
        # reason to parse that separately when this is already tracked)
        # and a body radius is known - without one there's no way to
        # convert lat/lon into meters for the map's geometry.
        surface_repo = surface_mining.surface_mining_repository
        position = live_position.current_position()
        # A body's size normally comes from the Scan event, which the journal only writes when the body was scanned in this session; Status.json carries the
        # body's name and radius whenever the commander is near the ground, so use them too. Without this the ground driven, Mark center, Mark border and the distances
        # to marks and deposits all did nothing on a body that had not been scanned.
        status_body = entry.get("BodyName")
        if position is not None and position.planet_radius and isinstance(status_body, str) and status_body:
            surface_repo.record_body_radius(status_body, position.planet_radius)
            if surface_repo.current_body is None and location.current_system():
                surface_repo.set_current_location(location.current_system(), status_body)
        radius = surface_repo.radius_for_current_body()
        if surface_repo.is_active and position is not None and radius:
            system, body = surface_repo.current_system, surface_repo.current_body
            if system and body:
                coverage.coverage_repository.record(system, body, position.latitude,
                                                    position.longitude, radius)

    # --- Settings tab ----------------------------------------------------

    def build_settings(self, notebook: nb.Notebook) -> None:
        frame = nb.Frame(notebook)
        frame.columnconfigure(0, weight=1)
        notebook.add(frame, text="Mining")

        self._display_session_totals_var = tk.BooleanVar(value=_cfg_bool(_CFG_DISPLAY_SESSION_TOTALS, True))
        self._display_cargo_bar_var = tk.BooleanVar(value=_cfg_bool(_CFG_DISPLAY_CARGO_BAR, True))
        self._display_prospector_hints_var = tk.BooleanVar(value=_cfg_bool(_CFG_DISPLAY_PROSPECTOR_HINTS, True))
        self._spansh_hotspot_finder_var = tk.BooleanVar(value=_cfg_bool(_CFG_SPANSH_HOTSPOT_FINDER_ENABLED, False))
        self._spansh_price_finder_var = tk.BooleanVar(value=_cfg_bool(_CFG_SPANSH_PRICE_FINDER_ENABLED, False))
        self._edsm_reserve_lookup_var = tk.BooleanVar(value=_cfg_bool(_CFG_EDSM_RESERVE_LOOKUP_ENABLED, False))
        self._edsm_body_lookup_var = tk.BooleanVar(value=_cfg_bool(mining_body_lookup.CONFIG_ENABLED, False))
        self._display_coverage_minimap_var = tk.BooleanVar(value=_cfg_bool(_CFG_DISPLAY_COVERAGE_MINIMAP, False))
        self._archive_sessions_var = tk.BooleanVar(value=_cfg_bool(_CFG_ARCHIVE_SESSIONS, False))
        self._stop_radius_var = tk.StringVar(value=str(mining_stops.clamp_radius(
            config.get_int(_CFG_STOP_RADIUS, default=mining_stops.DEFAULT_RADIUS_M))))
        self._rig_gap_var = tk.StringVar(value=str(mining_stops.clamp_rig_gap(config.get_int(_CFG_RIG_GAP, default=0))))
        self._refill_days_var = tk.StringVar(value=str(_refill_days()))
        target, target_percent = mining_alerts.load_target()
        self._target_var = tk.StringVar(value=target)
        self._target_percent_var = tk.StringVar(value=str(target_percent))

        nb.Label(frame, text="UI settings").grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        nb.Checkbutton(frame, text="Show session totals",
                       variable=self._display_session_totals_var).grid(row=1, column=0, sticky=tk.W, padx=10)
        nb.Checkbutton(frame, text="Show the cargo bar",
                       variable=self._display_cargo_bar_var).grid(row=2, column=0, sticky=tk.W, padx=10)
        nb.Checkbutton(frame, text="Show prospector hints",
                       variable=self._display_prospector_hints_var).grid(row=3, column=0, sticky=tk.W, padx=10)

        nb.Checkbutton(
            frame, text="Enable Spansh nearby hotspot finder (Space Mining page - contacts spansh.co.uk)",
            variable=self._spansh_hotspot_finder_var,
        ).grid(row=4, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Checkbutton(
            frame, text="Enable Spansh best price finder and Market research in the Surface Mining Book (contacts spansh.co.uk)",
            variable=self._spansh_price_finder_var,
        ).grid(row=5, column=0, sticky=tk.W, padx=10)
        nb.Checkbutton(
            frame, text=("Enable EDSM ring reserve lookup (Space Mining page - automatically contacts "
                        "edsm.net when you drop into a ring, once for each ring until EDMC restarts, plus manual search)"),
            variable=self._edsm_reserve_lookup_var,
        ).grid(row=6, column=0, sticky=tk.W, padx=10)
        nb.Label(frame, text="The in-game HUD overlay is set up on the Overlays tab (the surface compass is its own tab there).").grid(
            row=7, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Checkbutton(
            frame, text=("Enable body lookup (Surface Mining Book's Get body info button - asks edsm.net and spansh.co.uk for the "
                        "bodies of your system, sending only its name or id)"),
            variable=self._edsm_body_lookup_var,
        ).grid(row=8, column=0, sticky=tk.W, padx=10)
        nb.Checkbutton(
            frame, text=("Show coverage minimap (Surface Mining page - a small map of ground the "
                        "Rhino has driven over on the current body; redrawn once a second while "
                        "deployed)"),
            variable=self._display_coverage_minimap_var,
        ).grid(row=9, column=0, sticky=tk.W, padx=10)
        nb.Checkbutton(
            frame, text="Archive completed mining runs (writes a JSON file per run)",
            variable=self._archive_sessions_var,
        ).grid(row=10, column=0, sticky=tk.W, padx=10)

        radius_row = tk.Frame(frame)
        radius_row.grid(row=11, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Label(radius_row, text="Stop radius in the Surface Mining Book (m):").pack(side=tk.LEFT)
        tk.Spinbox(radius_row, from_=mining_stops.MIN_RADIUS_M, to=mining_stops.MAX_RADIUS_M,
                   increment=mining_stops.STEP_RADIUS_M, width=6, textvariable=self._stop_radius_var).pack(side=tk.LEFT, padx=6)
        nb.Label(frame, text=("Deposits within this distance of the one with the most rigs count as one Rhino stop. "
                              "500 to 2500 in steps of 250."), wraplength=440, justify=tk.LEFT).grid(
            row=12, column=0, sticky=tk.W, padx=10)

        refill_row = tk.Frame(frame)
        refill_row.grid(row=13, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Label(refill_row, text="Assume a depleted deposit has refilled after (days):").pack(side=tk.LEFT)
        tk.Spinbox(refill_row, from_=0, to=depletion.MAX_REGEN_DAYS, increment=1, width=5,
                   textvariable=self._refill_days_var).pack(side=tk.LEFT, padx=6)
        nb.Label(frame, text=("0 means unknown: a Depleted mark stays until you change it. The game gives no refill time and it may "
                              "differ from system to system, so set a number only if you have seen one."),
                 wraplength=440, justify=tk.LEFT).grid(row=14, column=0, sticky=tk.W, padx=10)

        target_row = tk.Frame(frame)
        target_row.grid(row=15, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Label(target_row, text="Target commodities:").pack(side=tk.LEFT)
        target_entry = tk.Entry(target_row, width=30, textvariable=self._target_var)
        target_entry.pack(side=tk.LEFT, padx=6)
        # The type-ahead follows the item being typed (after the last comma) and replaces only that item.
        commodity_autocomplete.attach(target_entry, mining_targets.LastItemVar(self._target_var), lambda: mining_spansh_client.KNOWN_MINING_COMMODITIES)
        nb.Label(target_row, text="worth cracking at").pack(side=tk.LEFT)
        tk.Spinbox(target_row, from_=mining_alerts.TARGET_PERCENT_RANGE[0], to=mining_alerts.TARGET_PERCENT_RANGE[1], width=4,
                   textvariable=self._target_percent_var).pack(side=tk.LEFT, padx=4)
        nb.Label(target_row, text="% or more").pack(side=tk.LEFT)
        nb.Label(frame, text=("Type a commodity as the game names it (for example Painite), or several separated by commas, each with its own percentage after the name "
                              "if you like: Painite 30, Platinum 25, Void Opals (up to %d; a name with no number uses the percentage above). The Space Mining page marks a prospected "
                              "rock that holds at least that much of one, naming which, and Flight Alerts (Settings → Flight Alerts) can put a card on the overlay for each. Leave it "
                              "empty for none. A core asteroid is always flagged." % mining_targets.MAX_TARGETS), wraplength=440, justify=tk.LEFT).grid(
            row=16, column=0, sticky=tk.W, padx=10)
        self._target_status = nb.Label(frame, text="", wraplength=440, justify=tk.LEFT)
        self._target_status.grid(row=17, column=0, sticky=tk.W, padx=10)
        self._target_var.trace_add("write", self._update_target_status)
        self._target_percent_var.trace_add("write", self._update_target_status)
        self._update_target_status()

        gap_row = tk.Frame(frame)
        gap_row.grid(row=18, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Label(gap_row, text="Too close to place another rig (m, 0 = off):").pack(side=tk.LEFT)
        tk.Spinbox(gap_row, from_=0, to=mining_stops.MAX_RIG_GAP_M, increment=mining_stops.STEP_RIG_GAP_M, width=6,
                   textvariable=self._rig_gap_var).pack(side=tk.LEFT, padx=6)
        nb.Label(frame, text=("The game does not publish how close rigs may be. Measure it with Mark center and Mark border (stand at one rig, press Mark center, "
                              "drive until the game lets you place the next, press Mark border) and enter it; the Surface Mining page then says whether "
                              "your nearest saved deposit is far enough away. 0 turns it off."), wraplength=440, justify=tk.LEFT).grid(
            row=19, column=0, sticky=tk.W, padx=10)

        sim_row = tk.Frame(frame)
        sim_row.grid(row=20, column=0, sticky=tk.W, padx=10, pady=(14, 0))
        nb.Label(sim_row, text="Simulation:").pack(side=tk.LEFT)
        tk.Button(sim_row, text="Surface Live (pretend Rhino)", command=self._open_surface_simulation).pack(side=tk.LEFT, padx=6)
        nb.Label(frame, text=("Opens the Surface Live window on made-up data: a Rhino driving a circle over a made-up planet, with a radar, saved deposits and marked "
                              "locations, so you can check the window works on your computer without the game. Nothing is saved, and the window never shows or "
                              "changes your own deposits, marks or runs."), wraplength=440, justify=tk.LEFT).grid(row=21, column=0, sticky=tk.W, padx=10)

        mining_hotspot_settings.build(frame, start_row=22)

    def _update_target_status(self, *_args: object) -> None:
        """The line under the target box: what is wrong with what is typed (a percentage that is not 1 to 100, a name twice, too many names), else how many targets it holds."""
        label = self._target_status
        if label is None or self._target_var is None or self._target_percent_var is None:
            return
        percent = mining_alerts.clamp(self._target_percent_var.get(), *mining_alerts.TARGET_PERCENT_RANGE, mining_alerts.DEFAULT_TARGET_PERCENT)
        parsed = mining_targets.parse_targets(self._target_var.get(), percent)
        if parsed.problems:
            text, color = " ".join(parsed.problems[:3]), "#c07000"
        else:
            text, color = (f"{len(parsed.targets)} target{'s' if len(parsed.targets) != 1 else ''} set." if parsed.targets else ""), "#2e7d32"
        try:
            label.configure(text=text, foreground=color)
        except tk.TclError:
            pass

    def build_overlay_settings(self, notebook: nb.Notebook) -> None:
        """The mining stats HUD, on the Overlays tab."""
        frame = nb.Frame(notebook)
        frame.columnconfigure(0, weight=1)
        notebook.add(frame, text="Mining")

        self._overlay_enabled_var = tk.BooleanVar(value=_cfg_bool(_CFG_OVERLAY_ENABLED, False))
        nb.Checkbutton(
            frame, text="Enable HUD Overlay (sends live stats to the overlay - see the Overlay Connection tab)",
            variable=self._overlay_enabled_var,
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 0))
        nb.Label(
            frame,
            text=("Where it sits on the screen is set on the Overlay Placement tab (Mining stats). The arrow that points at the nearest "
                  "hotspot is now the Surface Compass, on its own tab here."),
            wraplength=440, justify=tk.LEFT,
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(8, 10))

        action_row = tk.Frame(frame)
        action_row.grid(row=2, column=0, sticky=tk.W, padx=10, pady=(0, 10))
        tk.Button(action_row, text="Test HUD", command=self._test_overlay).pack(side=tk.LEFT)
        self._overlay_result_label = nb.Label(action_row, text="", wraplength=320, justify=tk.LEFT)
        self._overlay_result_label.pack(side=tk.LEFT, padx=(10, 0))
        nb.Label(frame, text="(Test HUD works even while the HUD is off above, and says whether the overlay was reachable.)", wraplength=440,
                 justify=tk.LEFT).grid(row=3, column=0, sticky=tk.W, padx=10, pady=(0, 10))

        self._radar_card_var = tk.BooleanVar(value=mining_radar_overlay.enabled())
        self._radar_size_var = tk.StringVar(value=str(mining_radar_overlay.card_size()))
        self._radar_opacity_var = tk.StringVar(value=str(mining_radar_overlay.opacity_percent()))
        nb.Checkbutton(frame, text="Show the Mining radar over the game while the Rhino is out (WFMT's built-in overlay, Windows)",
                       variable=self._radar_card_var).grid(row=4, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Label(frame, text=("The same radar as the Surface Live window, drawn over the game for one screen. It needs WFMT's built-in overlay (Overlay Connection tab): "
                              "EDMCModernOverlay cannot draw a picture. It reaches as far as the Live radar does, so the radar range shortcut or chat command, or the "
                              "Live window's range buttons, change it too. Where it sits is Overlay Placement's Mining radar."),
                 wraplength=440, justify=tk.LEFT).grid(row=5, column=0, sticky=tk.W, padx=10)
        radar_row = tk.Frame(frame)
        radar_row.grid(row=6, column=0, sticky=tk.W, padx=10, pady=(6, 0))
        nb.Label(radar_row, text="Size (pixels):").pack(side=tk.LEFT)
        tk.Spinbox(radar_row, from_=mining_radar_overlay.SIZE_RANGE[0], to=mining_radar_overlay.SIZE_RANGE[1], increment=20, width=5,
                   textvariable=self._radar_size_var).pack(side=tk.LEFT, padx=(4, 12))
        nb.Label(radar_row, text="Background opacity (%):").pack(side=tk.LEFT)
        tk.Spinbox(radar_row, from_=mining_radar_overlay.OPACITY_RANGE[0], to=mining_radar_overlay.OPACITY_RANGE[1], increment=5, width=4,
                   textvariable=self._radar_opacity_var).pack(side=tk.LEFT, padx=4)
        test_row = tk.Frame(frame)
        test_row.grid(row=7, column=0, sticky=tk.W, padx=10, pady=(6, 10))
        tk.Button(test_row, text="Test radar", command=self._test_radar_card).pack(side=tk.LEFT)
        self._radar_result_label = nb.Label(test_row, text="", wraplength=320, justify=tk.LEFT)
        self._radar_result_label.pack(side=tk.LEFT, padx=(10, 0))

    def _test_radar_card(self) -> None:
        """Test radar: the Mining radar card from the simulation's pretend Rhino, for a few seconds, at the size and opacity typed above (not saved until OK)."""
        label = self._radar_result_label
        if label is None:
            return
        try:
            size = int(self._radar_size_var.get())
            opacity = int(self._radar_opacity_var.get())
        except (TypeError, ValueError):
            label.configure(text="Type whole numbers for the size and the opacity.", foreground="#c07000")
            return
        saved = (config.get_int(mining_radar_overlay.CFG_SIZE, default=mining_radar_overlay.SIZE_DEFAULT), config.get_int(mining_radar_overlay.CFG_OPACITY, default=mining_radar_overlay.OPACITY_DEFAULT))
        config.set(mining_radar_overlay.CFG_SIZE, size)
        config.set(mining_radar_overlay.CFG_OPACITY, opacity)
        try:
            drawn = mining_radar_overlay.send_test(overlay.OverlayClient())
        finally:
            config.set(mining_radar_overlay.CFG_SIZE, saved[0])
            config.set(mining_radar_overlay.CFG_OPACITY, saved[1])
        label.configure(text="Sent: check your overlay." if drawn else "Needs WFMT's built-in overlay (Overlay Connection tab).", foreground="#2e7d32" if drawn else "#c07000")

    def _test_overlay(self) -> None:
        label = self._overlay_result_label
        if label is None:
            return
        cfg = overlay.load_config()
        client = overlay.OverlayClient(cfg)

        def worker() -> None:
            try:
                mining_overlay.send_test(client)
                outcome, color = "Sent — check your overlay.", "#2e7d32"
            except OSError as err:
                outcome, color = f"Could not reach the overlay at {cfg.host}:{cfg.port} ({err}).", "#c07000"
            try:
                label.after(0, lambda: label.configure(text=outcome, foreground=color))
            except tk.TclError:
                pass

        threading.Thread(target=worker, name="WFMT-mining-overlay-test", daemon=True).start()

    def save_settings(self) -> None:
        if self._display_session_totals_var is None:
            return
        config.set(_CFG_DISPLAY_SESSION_TOTALS, bool(self._display_session_totals_var.get()))
        config.set(_CFG_DISPLAY_CARGO_BAR, bool(self._display_cargo_bar_var.get()))
        config.set(_CFG_DISPLAY_PROSPECTOR_HINTS, bool(self._display_prospector_hints_var.get()))
        config.set(_CFG_SPANSH_HOTSPOT_FINDER_ENABLED, bool(self._spansh_hotspot_finder_var.get()))
        config.set(_CFG_SPANSH_PRICE_FINDER_ENABLED, bool(self._spansh_price_finder_var.get()))
        config.set(_CFG_EDSM_RESERVE_LOOKUP_ENABLED, bool(self._edsm_reserve_lookup_var.get()))
        config.set(mining_body_lookup.CONFIG_ENABLED, bool(self._edsm_body_lookup_var.get()))
        if self._overlay_enabled_var is not None:
            config.set(_CFG_OVERLAY_ENABLED, bool(self._overlay_enabled_var.get()))
        if self._radar_card_var is not None:
            config.set(mining_radar_overlay.CFG_ENABLED, bool(self._radar_card_var.get()))
            config.set(mining_radar_overlay.CFG_SIZE, mining_alerts.clamp(self._radar_size_var.get(), *mining_radar_overlay.SIZE_RANGE, mining_radar_overlay.SIZE_DEFAULT))
            config.set(mining_radar_overlay.CFG_OPACITY, mining_alerts.clamp(self._radar_opacity_var.get(), *mining_radar_overlay.OPACITY_RANGE, mining_radar_overlay.OPACITY_DEFAULT))
        config.set(_CFG_DISPLAY_COVERAGE_MINIMAP, bool(self._display_coverage_minimap_var.get()))
        config.set(_CFG_ARCHIVE_SESSIONS, bool(self._archive_sessions_var.get()))
        config.set(_CFG_STOP_RADIUS, mining_stops.clamp_radius(self._stop_radius_var.get()))
        config.set(_CFG_RIG_GAP, mining_stops.clamp_rig_gap(self._rig_gap_var.get()))
        config.set(_CFG_REFILL_DAYS, _clamp_refill_days(self._refill_days_var.get()))
        config.set(mining_alerts.CFG_TARGET, " ".join(self._target_var.get().split()))
        config.set(mining_alerts.CFG_TARGET_PERCENT, str(mining_alerts.clamp(self._target_percent_var.get(), *mining_alerts.TARGET_PERCENT_RANGE,
                                                                             mining_alerts.DEFAULT_TARGET_PERCENT)))
        hotspots.hotspot_repository.refill_days = _refill_days()
        self._redraw_if_alive()


controller = MiningPanelController()


def set_overlay_client(client: overlay.OverlayClient) -> None:
    controller.set_overlay_client(client)


def start(plugin_dir: str) -> None:
    controller.start(plugin_dir)


def stop() -> None:
    controller.stop()


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)


def build_settings(notebook: nb.Notebook) -> None:
    controller.build_settings(notebook)


def build_overlay_settings(notebook: nb.Notebook) -> None:
    controller.build_overlay_settings(notebook)


def save_settings() -> None:
    controller.save_settings()


def handle_event(entry: Dict[str, Any], cmdr: Optional[str], system: Optional[str],
                 station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def dashboard_status(entry: Dict[str, Any]) -> None:
    controller.dashboard_status(entry)
