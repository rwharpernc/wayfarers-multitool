"""The Mining live window: the LIVE button on both Mining pages, a window for a second screen (or a corner of the first) that carries what the EDMC panel would otherwise have to.

Surface Mining: a **radar** centered on the Rhino, north up, with range rings, the ground driven, the mining locations you marked, your saved deposits and a line to the nearest one; beside it the
same lines the panel shows (the run, cargo, refined, the nearest marked location and saved deposit); and the controls that act on the ground: **Mark center** and **Mark border** (mark a mining location's
center and border), **Add hotspot** (save a deposit where you stand) and **Import/export** (import or export your saved deposits). Five buttons under the radar set how far it reaches (50 m to 2 km).

Space Mining: the same live lines as the panel, large and readable, with the lookups the panel offers (Hotspots, Prices, Reserves) when they are switched on. There is no radar here: the journal does not say
where a ring's hotspots are, so there is nothing to place on one.

It needs no overlay: everything it shows is drawn in the window, and it redraws once a second while open. The page is drawn by the same code as the panel (`mining_render.render_surface_mining` and
`render_space_mining` with no button bar), so the two never disagree. One window per page; both hang off the main window, not the panel (which rebuilds its content every second). Built on the shared
window kit (plugin/uikit).
"""
from __future__ import annotations

import dataclasses
import logging
import os
import re
import tkinter as tk
from tkinter import filedialog
from typing import Callable, Dict, Optional

from config import appname, config

from . import mining_coverage as coverage
from . import mining_map_picture
from . import mining_radar_view
from . import mining_coverage_render as radar
from . import mining_hotspot_import_export as hotspot_import_export
from . import mining_hotspot_finder_dialog as hotspot_finder_dialog
from . import mining_pages
from . import mining_price_finder_dialog as price_finder_dialog
from . import mining_render as render
from . import mining_sources
from . import mining_reserve_lookup_dialog as reserve_lookup_dialog
from . import mining_space as space_mining
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.widgets import FlatButton, ScrollFrame

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = {mining_pages.SURFACE_MINING: "wfmt_mining_live_surface_geometry", mining_pages.SPACE_MINING: "wfmt_mining_live_space_geometry"}
CONFIG_RANGE = mining_radar_view.CONFIG_RANGE            # the range is shared with the radar card over the game
saved_range = mining_radar_view.saved_range
DEFAULT_SIZE = {mining_pages.SURFACE_MINING: (1180, 700), mining_pages.SPACE_MINING: (620, 640)}
MIN_SIZE = {mining_pages.SURFACE_MINING: (1120, 520), mining_pages.SPACE_MINING: (520, 420)}
TICK_MS = 1000
RADAR_MIN_PX, RADAR_MAX_PX = 240, 1200
WRAP_MIN, WRAP_MAX = 240, 700

SIMULATION_SUFFIX = "|simulation"

_SURFACE_HELP = (
    "The radar shows the ground around the Rhino, with the Rhino always in the middle and north at the top. The buttons under it set how far it reaches, from the middle to the edge.",
    ("Blue arrow", "The Rhino, pointing the way it faces."),
    ("Gray circles", "Range rings, each labeled with its distance from the Rhino."),
    ("Green area", "Ground you have driven: a disc of scanner reach (2 km, the community figure) round every point of your track. It means driven within reach, not proven scanned: "
                   "the game does not log a scan."),
    ("Dotted line", "Your track."),
    ("Black patches", "Ground inside the green that nothing has been driven near."),
    ("Yellow +", "The center of a mining location you marked with Mark center."),
    ("Yellow circle", "The border you marked with Mark border: its radius is the distance from the center to where you pressed it."),
    ("Orange dashed circles", "Where to drive to cover the nearest marked location: rings worked out from the 2 km scanner reach, the first at 2 km from the center and the rest a little under "
                              "4 km further out, the last on the border. They are a guide from that one estimate, not a measurement of where deposits are. Mark the border (Mark border) to get them right."),
    ("Violet circles", "The best stops: deposits close enough to work from one place (the stop radius is in Settings → Mining)."),
    ("Cream dots", "Your saved deposits, with the first letters of the material. The nearest has a line to it and its distance beside it."),
    ("Bright yellow line", "Set a target commodity (Settings → Mining) and the radar points at the nearest saved deposit of it, with the nearest of any kind dotted. A deposit beyond the radar is "
                           "labeled where the line leaves it."),
    ("Gray hollow ring", "A deposit marked Depleted."),
    ("Not on the radar", "A deposit saved without a position, and any deposit beyond the range. The lines on the right still list the deposits for this body."),
    ("Rig placed", "Notes the Rhino's position as a mining rig you have just placed (Ctrl+Alt+Shift+R or the chat command `!wf rig` does the same without the window). The journal does not say where a rig went, so this is how the radar learns it."),
    ("Rig markers", "A small square with a number at each rig you noted with Rig placed, 1 for the first. The number is its order, so you can tell which rig is which; it needs no rig gap."),
    ("Rig bands", "With a rig gap set in Settings → Mining, a band of that radius round each noted rig: a filled red-brown disc while the Rhino is inside it, a thin teal outline once it is clear, so the next rig goes down outside every band. The rigs are forgotten when the Rhino is stowed or launched, or destroyed. Clear rigs forgets them now."),
    ("Save map", "Saves a picture of this location (the ground driven, the border, the drive rings, the stops and the deposits, with a title and a legend) to a PNG file you choose, "
                 "to post or keep. It holds no commander name."),
    ("Mark center, Mark border", "Mark the center and the border of the mining location you are at."),
    ("Add hotspot", "Save a deposit where you stand."),
    ("Import/export", "Import or export your saved deposits."),
)

_windows: Dict[str, "LiveWindow"] = {}


def show(parent: tk.Misc, page: str, settings_factory: Callable[[], render.PanelSettings],
         sources: Optional[mining_sources.Sources] = None) -> Optional["LiveWindow"]:
    """Open the live window for `page`, or raise it if it is open. Parented on the main window's toplevel: the panel rebuilds its own content frame, which would take a window parented there
    with it. `settings_factory` gives the panel's current settings, so what the window shows follows Settings. `sources` is where it reads its data from: WFMT's own state, or the
    simulation's (which opens as its own window, so it never replaces one showing real data)."""
    if page not in CONFIG_GEOMETRY:
        return None
    key = page + (SIMULATION_SUFFIX if sources is not None and sources.simulated else "")
    held = _windows.get(key)
    if held is not None and held.alive:
        held.refresh()
        held.lift()
        return held
    _windows[key] = LiveWindow(parent.winfo_toplevel(), page, settings_factory, sources)
    return _windows[key]


def _real_window() -> Optional["LiveWindow"]:
    held = _windows.get(mining_pages.SURFACE_MINING)
    return held if held is not None and held.alive else None


def mark_here(border: bool) -> str:
    """Mark center (`border` False) or Mark border (True) from outside the window (a keyboard shortcut or a chat command): marks on WFMT's own data and, when the Surface Live window is open, says
    so in its status line and redraws it. Returns what was done, or why not."""
    message = render.mark_site(border)
    held = _real_window()
    if held is not None:
        held._say(message)
        held.refresh()
    return message


def place_rig(src: Optional[mining_sources.Sources] = None) -> str:
    """Rig placed, from outside the window (a keyboard shortcut or a chat command) or inside it: note the Rhino's position as a rig on this body, say so in the Surface Live window's
    status line and redraw it. Returns what was done, or why not."""
    src = src or mining_sources.real()
    ctx = mining_radar_view.context(src)
    if ctx is None:
        message = "WFMT cannot read your position: be on or just above the ground."
    else:
        message = src.rigs.add(ctx.system, ctx.body, ctx.position.latitude, ctx.position.longitude, ctx.body_radius_m)
    held = _real_window() if not src.simulated else None
    if held is not None:
        held._say(message)
        held.refresh()
    return message


def cycle_range() -> str:
    """The Live radar's reach steps to the next of `radar.RADAR_RANGES_M` (from 2 km back to 50 m), saved and applied to the open window. Returns what it is now."""
    held = _real_window()
    current = held._range_m if held is not None else saved_range()
    steps = radar.RADAR_RANGES_M
    meters = steps[(steps.index(current) + 1) % len(steps)] if current in steps else radar.DEFAULT_RADAR_RANGE_M
    if held is not None:
        held._set_range(meters)
    else:
        config.set(CONFIG_RANGE, int(meters))
    return f"Radar reaches {radar.range_text(meters)}."


def close() -> None:
    for window in list(_windows.values()):
        if window.alive:
            window.close()
    _windows.clear()


class LiveWindow:
    def __init__(self, parent: tk.Misc, page: str, settings_factory: Callable[[], render.PanelSettings],
                 sources: Optional[mining_sources.Sources] = None) -> None:
        self._page = page
        self._src = sources or mining_sources.real()
        self._simulated = self._src.simulated
        self._settings_factory = settings_factory
        self._range_m = saved_range()
        self._photo: Optional[tk.PhotoImage] = None
        self._lookups_shown: Dict[str, bool] = {}
        self._wrap = 380
        surface = page == mining_pages.SURFACE_MINING
        self._shell = WindowShell(
            parent, f"{page} Live" + (" (simulation)" if self._simulated else ""), "", size=DEFAULT_SIZE[page], min_size=MIN_SIZE[page],
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY[page]) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY[page], geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        if surface:
            self._shell.add_action("Mark center", lambda: self._mark(False),
                                    tip="Mark center - mark the center of the mining location you are at, from your live position")
            self._shell.add_action("Mark border", lambda: self._mark(True),
                                    tip="Mark border - mark the edge of the mining location you are at, which gives its radius (mark its center first)")
            self._shell.add_action("Add hotspot", self._save_hotspot,
                                    tip="Add hotspot - save the deposit where you stand as a hotspot; the form opens filled in with your position")
            self._shell.add_action("Save map", self._save_map,
                                    tip="Save map - save a picture of this mining location (ground driven, border, rings, stops, deposits) to a PNG file you choose")
            self._shell.add_action("Clear rigs", self._clear_rigs,
                                    tip="Clear rigs - forget the mining rigs noted on this body (nothing about them is saved)")
            self._shell.add_action("Rig placed", self._place_rig,
                                    tip="Rig placed - note the Rhino's position as a mining rig you have just placed")
            if not self._simulated:        # importing and exporting work on the saved deposits, which a simulation must not touch
                self._shell.add_action("Import/export", lambda: hotspot_import_export.open_import_export_dialog(self._shell.window),
                                    tip="Import/export - open the window that imports or exports your saved hotspots")
            self._shell.add_help("Surface Mining Live help", (
                ("This is a simulation: the Rhino, the ground and the deposits are made up and nothing here is saved.",) if self._simulated else ()) + _SURFACE_HELP)
        else:
            self._lookup_buttons = {
                "hotspot_finder": self._shell.add_action("Hotspots", lambda: hotspot_finder_dialog.open_hotspot_finder_dialog(self._shell.window),
                    tip="Hotspots - find nearby ring hotspots for a material (Spansh)"),
                "price_finder": self._shell.add_action("Prices", lambda: price_finder_dialog.open_price_finder_dialog(self._shell.window),
                    tip="Prices - find the stations that pay the most for a commodity (Spansh)"),
                "reserve_lookup": self._shell.add_action("Reserves", lambda: reserve_lookup_dialog.open_reserve_lookup_dialog(self._shell.window),
                    tip="Reserves - check the reserve level and type of a system's rings (EDSM)"),
            }
        body = self._shell.body
        body.columnconfigure(0, weight=3 if surface else 0)
        body.columnconfigure(1, weight=2 if surface else 1)
        body.rowconfigure(0, weight=1)

        self._radar_label: Optional[tk.Label] = None
        self._radar_box: Optional[tk.Frame] = None
        if surface:
            left = tk.Frame(body, bg=P.BG)
            left.grid(row=0, column=0, sticky="nsew", padx=(0, P.PAD))
            self._radar_box = tk.Frame(left, bg=P.MAP_BG)
            self._radar_box.pack(fill="both", expand=True)
            self._radar_box.pack_propagate(False)       # sized by the window, never by the picture in it
            self._radar_label = tk.Label(self._radar_box, bg=P.MAP_BG, bd=0)
            self._radar_label.place(relx=0.5, rely=0.5, anchor="center")
            zoom = tk.Frame(left, bg=P.BG)
            zoom.pack(fill="x", pady=(P.PAD_SM, 0))
            tk.Label(zoom, text="Radar reaches", fg=P.MUTED, bg=P.BG).pack(side="left", padx=(0, P.PAD_SM))
            self._zoom_buttons: Dict[float, FlatButton] = {}
            for meters in radar.RADAR_RANGES_M:
                button = FlatButton(zoom, radar.range_text(meters), lambda m=meters: self._set_range(m),
                                    tip=f"{radar.range_text(meters)} - set how far the radar reaches")
                button.pack(side="left", padx=(0, 6))
                self._zoom_buttons[meters] = button
            self._show_zoom()

        self._info = ScrollFrame(body)
        self._info.grid(row=0, column=1, sticky="nsew")
        self._info.body.columnconfigure(0, weight=1)
        self._info.bind("<Configure>", self._on_info_resize)
        self.refresh()
        self._shell.window.after(TICK_MS, self._tick)

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    @property
    def toplevel(self) -> tk.Toplevel:
        return self._shell.window

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        render.forget_lines(self._info.body)
        self._shell.close()

    def _tick(self) -> None:
        if not self.alive:
            return
        try:
            self.refresh()
        except tk.TclError:
            return                                      # the window went away mid-redraw
        except Exception:
            logger.debug("Mining live window redraw failed", exc_info=True)
        self._shell.window.after(TICK_MS, self._tick)

    def _on_info_resize(self, event: tk.Event) -> None:
        self._wrap = max(WRAP_MIN, min(WRAP_MAX, event.width - 40))

    def _say(self, text: str) -> None:
        self._shell.set_status(text)

    # --- the controls -------------------------------------------------------------------------------------------------

    def _mark(self, border: bool) -> None:
        self._say(render.mark_site(border, self._src))
        self.refresh()

    def _save_hotspot(self) -> None:
        render.open_add_hotspot_dialog(self._shell.window, self._src)

    def _place_rig(self) -> None:
        self._say(place_rig(self._src) if self._simulated else place_rig())
        self.refresh()

    def _clear_rigs(self) -> None:
        count = self._src.rigs.clear()
        self._say(f"Forgot {count} rig{'s' if count != 1 else ''}." if count else "No rigs were noted.")
        self.refresh()

    def _choose_path(self, default_name: str) -> str:
        """Ask where to save the map picture; an empty string when the commander cancels. A method of its own so a test can answer for it."""
        return filedialog.asksaveasfilename(parent=self._shell.window, title="Save map", defaultextension=".png", initialfile=default_name,
                                            filetypes=[("PNG image", "*.png")]) or ""

    def _save_map(self) -> None:
        ctx = mining_radar_view.context(self._src)
        image = None
        if ctx is not None:
            image = mining_map_picture.render(ctx.body_coverage, ctx.body_radius_m, coverage.CoveragePoint(ctx.position.latitude, ctx.position.longitude), ctx.position.heading, ctx.saved,
                                              ctx.system or "", ctx.body or "", mining_radar_view.extras(ctx, with_target=False))
        if image is None:
            self._say("The map needs your position and the body's size: land, or launch the Rhino, first.")
            return
        name = re.sub(r'[<>:"/\\|?*]', "", f"{ctx.body or 'Mining'} map").strip() + ".png"
        path = self._choose_path(name)
        if not path:
            return
        try:
            mining_map_picture.save(image, path)
        except OSError as err:
            self._say(f"Could not save the map: {err}")
            return
        self._say(f"Saved {os.path.basename(path)}.")

    def _set_range(self, meters: float) -> None:
        self._range_m = meters
        config.set(CONFIG_RANGE, int(meters))
        self._show_zoom()
        self._draw_radar()

    def _show_zoom(self) -> None:
        for meters, button in self._zoom_buttons.items():
            button.configure(fg=P.ACCENT if meters == self._range_m else P.TEXT)

    # --- drawing ------------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        if not self.alive:
            return
        self._src.tick()
        settings = dataclasses.replace(self._settings(), display_coverage_minimap=False)      # the radar is the map here
        body = self._info.body
        kept = render.begin_lines(body)                         # last second's text lines are reused where they have not changed, so the text does not flash
        for child in body.winfo_children():                     # not ScrollFrame.clear(): that would send the scroll position back to the top every second
            if child not in kept:
                child.destroy()
        try:
            self._draw_page(settings)
        finally:
            render.end_lines(body)

    def _draw_page(self, settings: render.PanelSettings) -> None:
        if self._page == mining_pages.SURFACE_MINING:
            render.render_surface_mining(self._info.body, self._wrap, None, settings, self._src)
            self._draw_radar()
            repo = self._src.surface
            self._shell.set_subtitle(("SIMULATION  ·  " if self._simulated else "")
                                     + f"{repo.current_body or 'No body yet'}  ·  {repo.current_system or 'No system yet'}")
        else:
            render.render_space_mining(self._info.body, self._wrap, None, settings)
            self._show_lookups({"hotspot_finder": settings.spansh_hotspot_finder_enabled, "price_finder": settings.spansh_price_finder_enabled,
                                "reserve_lookup": settings.edsm_reserve_lookup_enabled})
            ring = space_mining.space_mining_repository.current_ring()
            self._shell.set_subtitle(ring[1] if ring else "Not at a ring")

    def _show_lookups(self, wanted: Dict[str, bool]) -> None:
        """Show only the lookups switched on in Settings, in their usual order."""
        if wanted == self._lookups_shown:
            return
        self._lookups_shown = dict(wanted)
        for button in self._lookup_buttons.values():
            button.pack_forget()
        for name, button in self._lookup_buttons.items():
            if wanted.get(name):
                button.pack(side="left", padx=(6, 0))

    def _settings(self) -> render.PanelSettings:
        return self._settings_factory()

    def _draw_radar(self) -> None:
        if self._radar_label is None or self._radar_box is None:
            return
        size = max(RADAR_MIN_PX, min(RADAR_MAX_PX, min(self._radar_box.winfo_width(), self._radar_box.winfo_height()) - 4))
        image = mining_radar_view.render(self._src, size, self._range_m)
        if image is None:
            self._photo = None
            self._radar_label.configure(image="", text="The radar draws when you are on or just above the ground.\nLand, or launch the Rhino.",
                                        fg=P.MUTED, justify="center", font=style.font(P.FONT_BODY))
            return
        self._photo = tk.PhotoImage(data=radar.to_window_photo_data(image))
        self._radar_label.configure(image=self._photo, text="")
