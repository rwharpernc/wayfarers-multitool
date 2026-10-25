"""The Exploration Dashboard window: everything WFMT knows about the system, the body under you, the biology on it and your exploration so far, in one place, for when
you would rather read it than have it drawn over the game.

Four tabs, each a different question:

- **Overview**: the system in numbers, where you are, and the expedition in a line.
- **Orbit**: every body in the system (sortable), the selected body in full, what is worth mapping, what life is left to analyse and what others found there.
- **Surface**: the body you are on or near: its conditions, materials and atmosphere, then the exobiology (each genus, what it could be and pay, how far from the last
  sample), the specimens being tracked and where your ship and SRV are.
- **Exploration**: the running expedition in full, the route, and the Exploration panel's readouts.

The window opens on Orbit or Surface depending on where you are, and switches to Surface when you land and back to Orbit when you lift off (a tab you chose yourself is
left alone until the next change). The two header buttons switch the exploration overlays and the exobiology overlays off and on without touching Settings: what comes
back is exactly what you had switched on. All the numbers come from `explore_dashboard_data`; this module only draws them. The owner (`explore_dashboard`) is `ctx`, which
supplies `snapshot()`, `overlay_hidden(name)` and `toggle_overlays(name)`; tests give it a stand-in.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import Any, List, Mapping, Optional, Sequence, Tuple

from config import appname, config

from . import explore_dashboard_data as D
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Card, FlatButton, ScrollFrame, StatTile, Tabs, section_header

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_explore_dashboard_geometry"
DEFAULT_SIZE = (1240, 780)
MIN_SIZE = (940, 560)
TAB_OVERVIEW, TAB_ORBIT, TAB_SURFACE, TAB_EXPLORATION = 0, 1, 2, 3
TAB_NAMES = ("Overview", "Orbit", "Surface", "Exploration")

_ROLE_COLORS = {D.TEXT: P.TEXT, D.GOOD: P.OK, D.WARN: P.WARN, D.INFO: P.INFO, D.MUTED: P.MUTED, D.BAD: P.DANGER}

_window: Optional["ExploreDashboardWindow"] = None


def show(parent: tk.Misc, ctx: Any) -> None:
    """Open the window, or raise it if it is open."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return
    _window = ExploreDashboardWindow(parent, ctx)


def refresh() -> None:
    if _window is not None and _window.alive:
        _window.refresh()


def refresh_position() -> None:
    if _window is not None and _window.alive:
        _window.refresh_position()


def sync_overlays() -> None:
    if _window is not None and _window.alive:
        _window.sync_overlay_buttons()


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def is_open() -> bool:
    return _window is not None and _window.alive


def columns_for(spec: Sequence[Tuple[str, str, int, str]]) -> List[Column]:
    """The data layer's column specs as the table widget's columns; the widest text column takes the spare width."""
    widest = max(range(len(spec)), key=lambda i: spec[i][2]) if spec else -1
    return [Column(key, heading, width, anchor=anchor, stretch=index == widest, max_chars=60) for index, (key, heading, width, anchor) in enumerate(spec)]


class FieldBlock(tk.Frame):
    """A titled block of label: value rows. `set` redraws only when the fields changed."""

    def __init__(self, parent: tk.Misc, title: str, bg: str = P.CARD, label_width: int = 22) -> None:
        super().__init__(parent, bg=bg, padx=P.PAD, pady=P.PAD_SM)
        self._bg = bg
        self._label_width = label_width
        self._signature: Optional[Tuple[Tuple[str, str], ...]] = None
        tk.Label(self, text=title.upper(), fg=P.MUTED, bg=bg, anchor="w", font=style.font(P.FONT_SMALL)).pack(fill="x")
        self._grid = tk.Frame(self, bg=bg)
        self._grid.pack(fill="x", pady=(P.PAD_SM, 0))
        self._grid.columnconfigure(1, weight=1)
        self._values: List[Tuple[tk.Label, bool]] = []          # each value label, and whether it has a name label beside it
        self._label_px = 0
        self._grid.bind("<Configure>", self._rewrap)

    def set(self, fields: Sequence[Tuple[str, str]]) -> None:
        signature = tuple((str(label), str(value)) for label, value in fields)
        if signature == self._signature:
            return
        self._signature = signature
        for child in self._grid.winfo_children():
            child.destroy()
        self._values = []
        for row, (label, value) in enumerate(signature):
            if label:
                name = tk.Label(self._grid, text=label, fg=P.MUTED, bg=self._bg, anchor="nw", width=self._label_width, justify="left",
                                font=style.font(P.FONT_BOLD))
                name.grid(row=row, column=0, sticky="nw", pady=1)
                self._label_px = name.winfo_reqwidth()
            text = tk.Label(self._grid, text=value, fg=P.TEXT, bg=self._bg, anchor="nw", justify="left", wraplength=self._wrap(self._grid.winfo_width(), bool(label)))
            text.grid(row=row, column=1 if label else 0, columnspan=1 if label else 2, sticky="nw", pady=1)
            self._values.append((text, bool(label)))

    def _wrap(self, width: int, named: bool) -> int:
        """Where a value wraps: the room the block has beside its names, never more than 420 px nor less than 40 (a block's width is not known until it is laid out)."""
        if width <= 1:
            return 420
        return max(min(width - (self._label_px if named else 0) - 4, 420), 40)

    def _rewrap(self, event: tk.Event) -> None:
        for text, named in self._values:
            wrap = self._wrap(event.width, named)
            if wrap != int(str(text.cget("wraplength"))):
                text.configure(wraplength=wrap)


class TableBox(tk.Frame):
    """A heading over a DataTable that is refilled from a `D.Table` without rebuilding rows that did not change."""

    def __init__(self, parent: tk.Misc, title: str, table: D.Table, rows: Optional[int] = None, on_select: Any = None, on_activate: Any = None) -> None:
        super().__init__(parent, bg=P.PANE)
        self._title = tk.Label(self, text=title.upper(), fg=P.MUTED, bg=P.PANE, anchor="w", font=style.font(P.FONT_SMALL), padx=P.PAD_SM, pady=P.PAD_SM)
        self._title.pack(fill="x")
        self.table = DataTable(self, columns_for(table.columns), sortable=True, visible_rows=rows, empty_text=table.empty, on_select=on_select, on_activate=on_activate)
        self.table.pack(fill="both", expand=rows is None)
        self.table.tag_configure("done", background=P.ROW_OK)
        self.table.tag_configure("life", foreground=P.OK)
        self.table.tag_configure("map", foreground=P.ACCENT)
        self._signature: Optional[list] = None

    def fill(self, data: D.Table) -> None:
        signature = [(row.key, tuple(row.cells), row.tag) for row in data.rows]
        if signature == self._signature:
            return
        self._signature = signature
        selected = self.table.selection()
        self.table.clear()
        for row in data.rows:
            self.table.insert(row.key, row.cells, row.tag or None)
        if selected and self.table.exists(selected[0]):
            self.table.select(selected[0])
        self._signature = signature


class ExploreDashboardWindow:
    def __init__(self, parent: tk.Misc, ctx: Any) -> None:
        self._ctx = ctx
        self._perspective: Optional[str] = None
        self._selected_body: Optional[int] = None

        self._shell = WindowShell(
            parent, "Exploration Dashboard", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Route Planner", self._ctx.open_neutron)
        self._exploration_button = self._shell.add_action("", lambda: self._toggle("exploration"))
        self._exobiology_button = self._shell.add_action("", lambda: self._toggle("exobiology"))

        self._tabs = Tabs(self._shell.body)
        self._tabs.pack(fill="both", expand=True)
        self._build_overview(self._tabs.add(TAB_NAMES[TAB_OVERVIEW]))
        self._build_orbit(self._tabs.add(TAB_NAMES[TAB_ORBIT]))
        self._build_surface(self._tabs.add(TAB_NAMES[TAB_SURFACE]))
        self._build_exploration(self._tabs.add(TAB_NAMES[TAB_EXPLORATION]))
        self._tabs.select(TAB_OVERVIEW)
        self._tabs.on_select = self._on_tab         # only now: every tab exists, so a selection can redraw them
        self.sync_overlay_buttons()
        self.refresh()

    # --- tabs ---------------------------------------------------------------------------------------------------------

    def _scroller(self, tab: tk.Frame) -> tk.Frame:
        scroll = ScrollFrame(tab)
        scroll.pack(fill="both", expand=True)
        scroll.body.columnconfigure(0, weight=1)
        scroll.body.columnconfigure(1, weight=1)
        return scroll.body

    def _build_overview(self, tab: tk.Frame) -> None:
        body = self._scroller(tab)
        self._tile_row = tk.Frame(body, bg=P.PANE)
        self._tile_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=P.PAD, pady=(P.PAD, 0))
        self._tile_signature: Optional[tuple] = None
        self._tiles: List[StatTile] = []
        self._tiles_for_width = 0             # the row width the tiles were last laid out for
        self._placing = False
        self._tile_row.bind("<Configure>", lambda _e: self._place_tiles())
        self._system_block = FieldBlock(body, "This system")
        self._system_block.grid(row=1, column=0, sticky="nsew", padx=(P.PAD, P.PAD_SM), pady=P.PAD)
        self._you_block = FieldBlock(body, "You")
        self._you_block.grid(row=1, column=1, sticky="nsew", padx=(P.PAD_SM, P.PAD), pady=P.PAD)
        self._overview_run_block = FieldBlock(body, "Expedition")
        self._overview_run_block.grid(row=2, column=0, columnspan=2, sticky="ew", padx=P.PAD, pady=(0, P.PAD))

    def _build_orbit(self, tab: tk.Frame) -> None:
        tab.configure(padx=P.PAD_SM, pady=P.PAD_SM)
        self._bodies = TableBox(tab, "Every body in the system (click a heading to sort, click a row for the details)", D.Table(D.BODY_COLUMNS, [], "No bodies yet."),
                                rows=11, on_select=self._select_body)
        self._bodies.pack(fill="x")
        lower = tk.Frame(tab, bg=P.PANE)
        lower.pack(fill="both", expand=True, pady=(P.PAD_SM, 0))
        lower.columnconfigure(0, weight=1, uniform="lower")
        lower.columnconfigure(1, weight=2, uniform="lower")
        lower.rowconfigure(0, weight=1)
        detail = ScrollFrame(lower)
        detail.grid(row=0, column=0, sticky="nsew", padx=(0, P.PAD_SM))
        self._detail_body = detail.body
        self._detail_blocks: List[FieldBlock] = []
        self._detail_signature: Optional[tuple] = None
        todo = Tabs(lower, wrap=True, compact=True)
        todo.grid(row=0, column=1, sticky="nsew")
        self._map_box = TableBox(todo.add("Worth mapping"), "Planets and moons not yet mapped, best first", D.Table(D.MAP_COLUMNS, [], ""))
        self._map_box.pack(fill="both", expand=True)
        self._life_box = TableBox(todo.add("Life to analyze"), "Bodies with biology not yet all analyzed", D.Table(D.LIFE_COLUMNS, [], ""))
        self._life_box.pack(fill="both", expand=True)
        self._sites_box = TableBox(todo.add("Found by others"), "What Spansh lists in this system", D.Table(D.SITE_COLUMNS, [], ""))
        self._sites_box.pack(fill="both", expand=True)
        todo.select(0)

    def _build_surface(self, tab: tk.Frame) -> None:
        body = self._scroller(tab)
        self._here_block = FieldBlock(body, "Here")
        self._here_block.grid(row=0, column=0, sticky="nsew", padx=(P.PAD, P.PAD_SM), pady=(P.PAD, 0))
        self._exo_block = FieldBlock(body, "Exobiology on this body")
        self._exo_block.grid(row=0, column=1, sticky="nsew", padx=(P.PAD_SM, P.PAD), pady=(P.PAD, 0))
        self._genus_box = TableBox(body, "Genera: what each could be, what it pays, how far you are from the last sample", D.Table(D.GENUS_COLUMNS, [], ""), rows=5)
        self._genus_box.grid(row=1, column=0, columnspan=2, sticky="ew", padx=P.PAD, pady=(P.PAD, 0))
        self._waypoint_box = TableBox(body, "Specimens being tracked", D.Table(D.WAYPOINT_COLUMNS, [], ""), rows=4)
        self._waypoint_box.grid(row=2, column=0, columnspan=2, sticky="ew", padx=P.PAD, pady=(P.PAD, 0))
        self._surface_blocks_frame = tk.Frame(body, bg=P.PANE)
        self._surface_blocks_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=P.PAD, pady=P.PAD)
        self._surface_blocks_frame.columnconfigure(0, weight=1)
        self._surface_blocks_frame.columnconfigure(1, weight=1)
        self._surface_blocks: List[FieldBlock] = []
        self._surface_signature: Optional[tuple] = None

    def _build_exploration(self, tab: tk.Frame) -> None:
        body = self._scroller(tab)
        self._run_block = FieldBlock(body, "Expedition")
        self._run_block.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(P.PAD, P.PAD_SM), pady=P.PAD)
        self._route_block = FieldBlock(body, "Route")
        self._route_block.grid(row=0, column=1, sticky="nsew", padx=(P.PAD_SM, P.PAD), pady=(P.PAD, 0))
        self._readout_block = FieldBlock(body, "Panel readouts")
        self._readout_block.grid(row=1, column=1, sticky="nsew", padx=(P.PAD_SM, P.PAD), pady=P.PAD)

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._shell.close()

    def _on_tab(self, _index: int) -> None:
        self.refresh()

    def _select_body(self, iid: str) -> None:
        self._selected_body = int(iid) if iid.lstrip("-").isdigit() else None
        self._refresh_detail(self._ctx.snapshot())

    def _toggle(self, name: str) -> None:
        self._ctx.toggle_overlays(name)
        self.sync_overlay_buttons()

    def sync_overlay_buttons(self) -> None:
        """The two header buttons say what pressing them will do."""
        if not self.alive:
            return
        for button, name, label in ((self._exploration_button, "exploration", "Exploration overlays"), (self._exobiology_button, "exobiology", "Exobiology overlays")):
            hidden = self._ctx.overlay_hidden(name)
            button.configure(text=f"{label}: {'OFF - show' if hidden else 'ON - hide'}", fg=P.WARN if hidden else P.TEXT)

    # --- refreshing ---------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        """Redraw everything from the current data (cheap when nothing changed: each block and table compares before it rebuilds)."""
        if not self.alive:
            return
        try:
            data = self._ctx.snapshot()
            self._follow_perspective(data)
            self._refresh_overview(data)
            self._refresh_orbit(data)
            self._refresh_surface(data)
            self._refresh_exploration(data)
            survey = data["survey"]
            self._shell.set_subtitle(f"{survey.name}" if survey.name else "No system yet")
            self._shell.set_status(self._status_line(data))
        except Exception:
            logger.warning("The Exploration Dashboard could not redraw", exc_info=True)

    def refresh_position(self) -> None:
        """Status.json moved (about once a second): update only what depends on the position."""
        if not self.alive:
            return
        try:
            data = self._ctx.snapshot()
            self._follow_perspective(data)
            self._you_block.set(D.you_fields(data["status"], data["survey"]))
            self._refresh_surface(data)
        except Exception:
            logger.warning("The Exploration Dashboard could not update the position", exc_info=True)

    def _status_line(self, data: Mapping[str, Any]) -> str:
        view = D.perspective(data["status"])
        return ("On the ground: the Surface tab follows the body under you." if view == D.GROUND else
                "In space: the Orbit tab shows the whole system.") + "  The header buttons hide and show your overlays; nothing in Settings changes."

    def _follow_perspective(self, data: Mapping[str, Any]) -> None:
        """Pick Orbit or Surface when the window opens and when the commander lands or lifts off; a tab chosen by hand is left alone between those changes."""
        now = D.perspective(data["status"]) if data["status"] else None
        if now is None or now == self._perspective:
            return
        first = self._perspective is None
        self._perspective = now
        if first or self._tabs.selected in (TAB_ORBIT, TAB_SURFACE):
            self._tabs.select(TAB_SURFACE if now == D.GROUND else TAB_ORBIT)

    def _refresh_overview(self, data: Mapping[str, Any]) -> None:
        tiles = D.overview_tiles(data["survey"], data["threshold"], data["basis"], data["run"])
        signature = tuple((t.value, t.caption, t.role) for t in tiles)
        if signature != self._tile_signature:
            self._tile_signature = signature
            for child in self._tile_row.winfo_children():
                child.destroy()
            self._tiles = [StatTile(self._tile_row, tile.value, tile.caption, _ROLE_COLORS.get(tile.role, P.TEXT)) for tile in tiles]
            self._tiles_for_width = 0
            self._place_tiles()
        self._system_block.set(D.system_fields(data["survey"], data["readouts"][0]))
        self._you_block.set(D.you_fields(data["status"], data["survey"]))
        self._overview_run_block.set(D.expedition_fields(data["run"])[:6])

    def _place_tiles(self) -> None:
        """Lay the tiles out in as many columns as fit, wrapping onto further rows rather than cutting a caption off: start with one row
        and take a column away until every caption fits its tile."""
        width = self._tile_row.winfo_width()
        if not self._tiles or width <= 1 or width == self._tiles_for_width or self._placing:
            return
        self._tiles_for_width = width
        self._placing = True
        try:
            per_row = len(self._tiles)
            while True:
                for index, widget in enumerate(self._tiles):
                    row, column = divmod(index, per_row)
                    widget.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else P.PAD_SM, 0), pady=(0 if row == 0 else P.PAD_SM, 0))
                for column in range(len(self._tiles)):
                    self._tile_row.columnconfigure(column, weight=1 if column < per_row else 0, uniform="tiles" if column < per_row else "")
                self._tile_row.update_idletasks()
                cut = any(tile._caption.winfo_reqwidth() > tile.winfo_width() - 2 * P.PAD + 2 for tile in self._tiles)
                if not cut or per_row == 1:
                    break
                per_row -= 1
        finally:
            self._placing = False

    def _refresh_orbit(self, data: Mapping[str, Any]) -> None:
        survey = data["survey"]
        self._bodies.fill(D.bodies_table(survey, data["threshold"], data["basis"]))
        self._map_box.fill(D.map_table(survey, data["threshold"], data["basis"]))
        self._life_box.fill(D.life_table(survey))
        self._sites_box.fill(D.sites_table(survey))
        self._refresh_detail(data)

    def _refresh_detail(self, data: Mapping[str, Any]) -> None:
        survey = data["survey"]
        body = survey.bodies.get(self._selected_body) if self._selected_body is not None else None
        self._show_blocks(self._detail_body, self._detail_blocks, D.body_sections(body), "_detail_signature")

    def _show_blocks(self, host: tk.Misc, blocks: List[FieldBlock], sections: Sequence[Tuple[str, D.Fields]], signature_name: str) -> None:
        """Lay `sections` out as stacked blocks, rebuilding them only when the titles change (their rows update in place)."""
        titles = tuple(title for title, _fields in sections)
        if titles != getattr(self, signature_name):
            setattr(self, signature_name, titles)
            for block in blocks:
                block.destroy()
            blocks.clear()
            for index, (title, _fields) in enumerate(sections):
                block = FieldBlock(host, title, label_width=20)
                if host is self._detail_body:
                    block.pack(fill="x", padx=P.PAD_SM, pady=(0, P.PAD_SM))
                else:
                    block.grid(row=index // 2, column=index % 2, sticky="nsew", padx=P.PAD_SM, pady=P.PAD_SM)
                blocks.append(block)
        for block, (_title, fields) in zip(blocks, sections):
            block.set(fields)

    def _refresh_surface(self, data: Mapping[str, Any]) -> None:
        survey, view, status = data["survey"], data["view"], data["status"]
        here = D.you_fields(status, survey) + D.vehicle_fields(view)
        self._here_block.set(here)
        self._exo_block.set(D.exo_fields(view))
        self._genus_box.fill(D.genus_table(view))
        self._waypoint_box.fill(D.waypoint_table(view))
        body = None
        if status.get("BodyName"):
            body = survey.find(name=str(status["BodyName"]))
        if body is None and view is not None:
            body = survey.find(name=view.body_name)
        self._show_blocks(self._surface_blocks_frame, self._surface_blocks, D.body_sections(body)[:4] if body is not None else [("Body", [("", "No body under you yet: land, or fly close to one.")])],
                          "_surface_signature")

    def _refresh_exploration(self, data: Mapping[str, Any]) -> None:
        self._run_block.set(D.expedition_fields(data["run"]))
        self._route_block.set(D.route_fields(data["route"]))
        self._readout_block.set(D.readout_fields(*data["readouts"]))
