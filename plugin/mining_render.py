"""
Mining mode's per-page content rendering: this module owns "what goes on the panel for the Space Mining /
Surface Mining page", while
`mining_panel.py` owns the panel's persistent chrome (page nav, the
scrollable Canvas/Scrollbar frame, the persistent hotspot/finder
buttons) and calls into `render_space_mining()`/`render_surface_mining()`
each time it needs to redraw.

Every label showing variable-length content uses the `wrap` value
`mining_panel.py` derives from the canvas's real measured width, never a
fixed wraplength - see the main-window-sizing rule in
docs/TECHNICAL.md section 5.
"""
import logging
import tkinter as tk
import dataclasses
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from . import mining_alerts
from . import mining_bearing as bearing
from . import mining_coverage as coverage
from . import mining_coverage_render as coverage_render
from . import mining_deposit
from . import mining_ground
from . import mining_hotspots as hotspots
from . import mining_live_position as live_position
from . import mining_market
from . import mining_methods
from . import mining_rate
from . import mining_sources
from . import mining_space as space_mining
from . import mining_stops
from . import mining_surface as surface_mining
from .mining_body_survey import system_body_survey

_ROW_LIMIT = 8
"""Cap on distinct commodities/limpet-types shown per summary line - a
long mining trip can rack up a dozen+ distinct materials, and every line
below already goes through wraplength, but capping the count keeps a
single line from becoming a wall of text no one reads."""

_WARNING_COLOR = "#c0392b"
"""Same hex as mining_reserve_lookup_dialog.py's own warning color -
kept in sync deliberately so the passive ring-caution line here and the
manual dialog's result read as the same warning, not two different
reds."""


@dataclass
class PanelSettings:
    """The subset of mining_panel.py's config Mining's own render/overlay
    logic needs - passed in explicitly rather than each render function
    reaching into config itself, so this module stays a pure "given this
    state, build these widgets" layer."""
    display_session_totals: bool
    display_cargo_bar: bool
    display_prospector_hints: bool
    spansh_hotspot_finder_enabled: bool
    spansh_price_finder_enabled: bool
    edsm_reserve_lookup_enabled: bool
    display_coverage_minimap: bool
    rig_gap_m: int = 0
    """The commander's own "too close for another rig" distance in meters (Settings, Mining); 0 is off. The game does not publish one."""


@dataclass
class PanelButtons:
    """The panel's persistent buttons (see mining_panel.py's module
    docstring for why they're created once and only grid()/grid_remove()'d
    rather than destroyed/recreated every render - the same native-widget-
    flicker lesson every WFMT feature with a persistent button follows)."""
    bar: tk.Frame
    hotspot_finder: tk.Button
    price_finder: tk.Button
    reserve_lookup: tk.Button
    ledger: tk.Button
    history: tk.Button
    live: tk.Button


def format_counts(counts: Dict[str, int], with_mine_via: bool = False) -> str:
    """{"Palladium": 12, "Osmium": 3} -> "Palladium x12, Osmium x3" -
    highest count first, capped at _ROW_LIMIT distinct entries so a trip
    with a dozen+ commodities doesn't produce one unreadably long line.

    with_mine_via appends each commodity's mining_methods.py extraction-
    method hint, e.g. "Painite x3 (Mine via: Core, Laser Surface or
    Sub-surface Deposit)" - only meaningful for dicts keyed by commodity
    display name (refined/prospected_commodities), not limpet types."""
    if not counts:
        return "none yet"
    items = sorted(counts.items(), key=lambda kv: -kv[1])[:_ROW_LIMIT]
    parts = []
    for name, count in items:
        text = f"{name} x{count}"
        if with_mine_via:
            hint = mining_methods.format_methods(mining_methods.methods_for(name))
            if hint:
                text += f" (Mine via: {hint})"
        parts.append(text)
    if with_mine_via and any("(Mine via" in part for part in parts):
        return _as_list(parts, len(counts))
    text = ", ".join(parts)
    if len(counts) > _ROW_LIMIT:
        text += ", ..."
    return text


def _as_list(parts: List[str], total: int) -> str:
    """Long entries one to a line, each indented, starting on a new line under the heading the caller puts before them, so they read as a list and not as one run-on sentence."""
    lines = ["   " + part for part in parts]
    if total > len(parts):
        lines.append(f"   and {total - len(parts)} more")
    return "\n" + "\n".join(lines)


def limpets_on_board(run: space_mining.SpaceMiningRun) -> str:
    """The limpets aboard as the panel and the HUD both show them: the exact count when EDMC has said ("12"), else the bought-less-launched estimate ("~12"), else "" when neither is known."""
    if run.limpets_aboard is not None:
        return str(run.limpets_aboard)
    if run.limpets_bought:
        return f"~{max(run.limpets_bought - sum(run.limpets_launched.values()), 0)}"
    return ""


def format_materials_seen(run: space_mining.SpaceMiningRun) -> str:
    """Like format_counts(with_mine_via=True), but for
    prospected_commodities specifically: each entry also gets a "%
    Range" yield hint (min-avg-max Materials[].Proportion seen this run,
    space_mining.format_yield_range()) before the Mine via hint - not
    something format_counts's generic counts dict shape can express,
    since it needs the separate prospected_proportions samples."""
    counts = run.prospected_commodities
    if not counts:
        return "none yet"
    items = sorted(counts.items(), key=lambda kv: -kv[1])[:_ROW_LIMIT]
    parts = []
    for name, count in items:
        text = f"{name} x{count}"
        proportions = run.prospected_proportions.get(name)
        if proportions:
            text += f" [{space_mining.format_yield_range(proportions)}]"
        hint = mining_methods.format_methods(mining_methods.methods_for(name))
        if hint:
            text += f" (Mine via: {hint})"
        parts.append(text)
    return _as_list(parts, len(counts))


def format_rate_now(run) -> str:
    """"Refining now: 840 t/h": tons refined in the last minute, scaled to an hour (`mining_rate.current_rate`), for a run with a `refined_timestamps` list (SpaceMiningRun or
    SurfaceMiningRun). The panel, the HUD and the live window all word it this way."""
    return f"Refining now: {mining_rate.current_rate(run.refined_timestamps):,.0f} t/h"


def format_run_average(run) -> str:
    """"Run average: 720 t/h over 41 min": the tons refined this run over its mining time, first to last mining event without the gaps of more than ten minutes
    (`mining_rate.MiningClock`; Mining History reads a run's mining time the same way). Says so while there is nothing to average yet."""
    clock = run.clock
    if clock.first is None:
        return "Run average: none yet"
    average = clock.average_per_hour(sum(run.refined.values()))
    if average is None:
        return "Run average: needs a minute of mining"
    return f"Run average: {average:,.0f} t/h over {clock.mined_seconds / 60:,.0f} min"


def format_time_to_full(run, tons: int, capacity: Optional[int], label: str = "Hold", live: bool = True) -> str:
    """"Hold full in about 14 min": the room left in the hold (`capacity` less `tons`) over the run's average rate, or over the rate now in the first minute, before there is an
    average. "Hold is full" once it is; nothing ("") when the capacity or a rate is not known, or when nothing is being refined, so a line only shows when it says something. `live` is
    False for a Rhino that is stowed, whose hold is not filling. The panel, the HUD and the live window all word it this way."""
    if not capacity or not live:
        return ""
    free = capacity - tons
    if free <= 0:
        return f"{label} is full"
    rate = run.clock.average_per_hour(sum(run.refined.values()))
    if rate is None:
        rate = mining_rate.current_rate(run.refined_timestamps)
    minutes = mining_rate.minutes_to_fill(free, rate)
    return f"{label} full in {mining_rate.full_in_text(minutes)}" if minutes is not None else ""


def ship_hold(cargo: int) -> tuple:
    """(tons, capacity) of the ship's hold as `format_ship_cargo` words it: the tons `Status.json` last said when it has, else `cargo`; the capacity from the last `Loadout`."""
    repo = space_mining.space_mining_repository
    live = repo.live_cargo()
    return (cargo if live is None else live), repo.cargo_capacity()


def format_hold(tons: int, capacity: Optional[int], label: str = "Hold") -> str:
    """"Hold: 64 of 200 t" when the capacity is known, else "Hold: 64 t". `label` names whose hold it is where the page shows two."""
    return f"{label}: {tons} of {capacity} t" if capacity else f"{label}: {tons} t"


def format_ship_cargo(cargo: int, label: str = "Hold") -> str:
    """The ship's hold line: the tons `Status.json` last said (live, about once a second) when it has, else `cargo`, the figure the latest `Cargo` event gave; with the ship's
    `CargoCapacity` (from a `Loadout` event - see mining_space.py) when that is known."""
    tons, capacity = ship_hold(cargo)
    return format_hold(tons, capacity, label)


def format_srv_cargo(cargo: int) -> str:
    """"SRV hold: 40 of 72 t" - the Rhino's capacity is a fixed
    constant (mining_surface.RHINO_CARGO_CAPACITY), unlike the ship's,
    so this is always known once a run exists."""
    return format_hold(cargo, surface_mining.RHINO_CARGO_CAPACITY, "SRV hold")


def format_distance(meters: float) -> str:
    """A distance for the panel's lines, with a space before the unit as the other figures have: `750 m`, `3.75 km`."""
    return f"{meters / 1000:.2f} km" if meters > 1000 else f"{meters:.0f} m"


def format_hotspot(hotspot: hotspots.Hotspot) -> str:
    text = hotspot.material
    if hotspot.rigs is not None:
        text += f", {hotspot.rigs} rig{'s' if hotspot.rigs != 1 else ''}"
    if hotspot.signal_number is not None:
        text += f", signal {hotspot.signal_number}"
    if hotspot.has_position():
        text += f", at {hotspot.latitude:.2f}, {hotspot.longitude:.2f}"
    # Rigs and Amount together are what mining_deposit.reserve_text() needs -
    # a hotspot with only one of the two (or neither) shows no estimate
    # rather than a misleading partial one.
    estimate = mining_deposit.reserve_text(hotspot.rigs, hotspot.amount, hotspot.density, hotspot.mined_tons)
    if estimate:
        text += f" [{estimate}]"
    if hotspot.notes:
        text += f" ({hotspot.notes})"
    return text


def format_hotspots(matches: List[hotspots.Hotspot]) -> str:
    """One deposit to a line, each indented under the heading the caller puts above them, so a long list reads as a list and not as one run-on sentence."""
    items = matches[:_ROW_LIMIT]
    text = "\n".join("   " + format_hotspot(h) for h in items)
    if len(matches) > _ROW_LIMIT:
        text += f"\n   and {len(matches) - _ROW_LIMIT} more"
    return text


# The panel and the live windows redraw once a second, and destroying and re-creating every text line each time makes the text flicker. So a line drawn last time at the
# same row is reused and only changed if its text (or width, or color) differs. `begin_lines` and `end_lines` bracket one redraw of one frame. The lines are kept per frame,
# so the panel and each live window reuse only their own.
_previous_lines: Dict[tk.Widget, Dict[int, Tuple[tk.Label, bool]]] = {}
_current_lines: Dict[tk.Widget, Dict[int, Tuple[tk.Label, bool]]] = {}


def begin_lines(content: tk.Widget) -> List[tk.Widget]:
    """Start a redraw of `content`: the lines drawn there last time wait to be reused. Returns them, so the caller does not destroy them with the rest of the frame."""
    _previous_lines[content], _current_lines[content] = _current_lines.get(content, {}), {}
    return [label for label, _ in _previous_lines[content].values()]


def end_lines(content: tk.Widget) -> None:
    """End a redraw of `content`: lines nothing reused are removed."""
    previous = _previous_lines.pop(content, {})
    for label, _ in previous.values():
        try:
            label.destroy()
        except tk.TclError:
            pass


def forget_lines(content: tk.Widget) -> None:
    """A frame is going away: let go of its lines."""
    _previous_lines.pop(content, None)
    _current_lines.pop(content, None)


def add_line(content: tk.Frame, row: int, wrap: int, text: str, fg: Optional[str] = None) -> None:
    # fg only passed through when the caller wants a fixed color (e.g.
    # the ring-caution warning below) - a widget that sets its own fg at
    # creation, before theme.update() ever sees it, keeps that color
    # permanently (EDMC's theme system only auto-colors a widget's
    # foreground if it didn't already have one at first registration),
    # which is exactly what a warning line wants.
    kwargs = {"fg": fg} if fg else {}
    old = _previous_lines.get(content, {}).pop(row, None)
    if old is not None and old[1] == bool(fg) and old[0].winfo_exists():
        label = old[0]
        if str(label.cget("text")) != text:
            label.configure(text=text)
        if int(label.cget("wraplength")) != wrap:
            label.configure(wraplength=wrap)
        if fg and str(label.cget("fg")) != fg:
            label.configure(fg=fg)
    else:
        if old is not None:
            old[0].destroy()
        label = tk.Label(content, text=text, anchor=tk.W, justify=tk.LEFT, wraplength=wrap, **kwargs)
        label.grid(row=row, column=0, sticky="w", padx=6, pady=2)
    _current_lines.setdefault(content, {})[row] = (label, bool(fg))


def render_ring_caution(content: tk.Frame, wrap: int, row: int, enabled: bool) -> int:
    """Passive counterpart to the "Check Ring Reserve Level..." button -
    shows the automatic lookup's result (see mining_panel.py's ring-
    reserve auto-lookup) for whichever ring the commander is currently
    at, if any. Silently renders nothing while unknown (no ring tracked
    yet, EDSM has no data for it, or the lookup hasn't completed) rather
    than showing stale/wrong data - same principle as the surface
    surface compass's "show nothing until known" rule."""
    if not enabled:
        return row
    caution = space_mining.space_mining_repository.ring_caution()
    if caution is None:
        return row
    reserve_text = caution.reserve_level or "Unknown"
    text = f"Ring: {caution.ring_name} ({caution.ring_type}) - Reserve: {reserve_text}"
    if not caution.is_metallic:
        text += " - not Metallic: premium laser-mined yields are typically best on Metallic rings"
    add_line(content, row, wrap, text, fg=None if caution.is_metallic else _WARNING_COLOR)
    return row + 1


BUTTON_ORDER = ("ledger", "history", "live", "hotspot_finder", "price_finder", "reserve_lookup")
"""Left-to-right order of the panel's buttons in their one row: BOOK, DASHBOARD, LIVE, H.S., PRICE, RES. A button not offered on the current page, or switched off in Settings, is
simply left out. The controls that act on the ground (CTR, BRD, +H.S., I/E) live in the live window (`mining_live_window.py`), not on the panel."""


def place_button_bar(buttons: Optional[PanelButtons], row: int, shown: Iterable[str]) -> None:
    """Puts the buttons named in `shown` side by side in one row at `row` of the
    content frame (and hides the rest), instead of stacking one per row. The buttons
    live in `buttons.bar`, which is placed once; inside it each button keeps a fixed
    column. Only touches a widget's grid mapping when its state actually changes
    (compares against grid_info(), which is {} while hidden), so a periodic redraw
    that changes nothing doesn't unmap/remap native buttons, which flickers visibly
    on Windows even when the colors come out the same. `buttons` is None when a page is
    drawn into the live window, which has its own controls."""
    if buttons is None:
        return
    shown = set(shown)
    for column, name in enumerate(BUTTON_ORDER):
        button = getattr(buttons, name)
        info = button.grid_info()
        if name in shown:
            if info.get("column") != column:
                button.grid(row=0, column=column, padx=(0, 6))
        elif info:
            button.grid_remove()
    if not shown:
        if buttons.bar.grid_info():
            buttons.bar.grid_remove()
    elif buttons.bar.grid_info().get("row") != row:
        buttons.bar.grid(row=row, column=0, sticky="w", padx=6, pady=(2, 6))


def _shown_buttons(settings: PanelSettings, *, hotspot_finder: bool = False, price_finder: bool = False, reserve_lookup: bool = False) -> List[str]:
    """Names of the buttons to show on this page: the Mining Book, the Mining History (DASHBOARD) and the live window (LIVE) always, plus the opt-in lookups (Spansh hotspot
    finder, Spansh price finder, EDSM reserve lookup) the page offers, only when switched on in Settings."""
    shown = ["ledger", "history", "live"]
    if hotspot_finder and settings.spansh_hotspot_finder_enabled:
        shown.append("hotspot_finder")
    if price_finder and settings.spansh_price_finder_enabled:
        shown.append("price_finder")
    if reserve_lookup and settings.edsm_reserve_lookup_enabled:
        shown.append("reserve_lookup")
    return shown


logger = logging.getLogger(__name__)


def mission_need_lines() -> list[str]:
    """The Space Mining page's lines for active mining missions (see mining_missions.py); none when there are none or the missions side is not available."""
    try:
        from . import all_missions, current_cargo, mining_missions
        missions = all_missions.view.missions
        return mining_missions.lines(mining_missions.needs(missions.values() if missions else [], current_cargo.held()))
    except Exception:
        logger.debug("Could not work out what the mining missions need", exc_info=True)
        return []


def render_space_mining(content: tk.Frame, wrap: int, buttons: Optional[PanelButtons], settings: PanelSettings) -> None:
    repo = space_mining.space_mining_repository
    run = repo.current_run()
    row = 0

    if run is None:
        add_line(content, row, wrap, "No commander detected yet.")
        row += 1
        # The Mining Book needs nothing from a run (saved hotspots aren't
        # per-commander), so it's offered on both pages - Mining opens on the
        # Space Mining page, which is where people look first.
        # Find Best Price / Check Ring Reserve Level stay available even
        # pre-commander-detection - both are on-demand lookups that don't
        # need an active run, unlike the hotspot finder (which searches
        # relative to the reference system tracked from journal events).
        place_button_bar(buttons, row, _shown_buttons(
            settings, price_finder=True, reserve_lookup=True))
        return

    if not run.has_data():
        add_line(content, row, wrap,
                "No active mining run. Undock to start tracking a new run.")
        row += 1
        for text in mission_need_lines():
            add_line(content, row, wrap, text)
            row += 1
        row = render_ring_caution(content, wrap, row, settings.edsm_reserve_lookup_enabled)
        place_button_bar(buttons, row, _shown_buttons(
            settings, hotspot_finder=True, price_finder=True, reserve_lookup=True))
        return

    if run.is_paused:
        add_line(content, row, wrap, "Paused (in supercruise)")
        row += 1
    row = render_ring_caution(content, wrap, row, settings.edsm_reserve_lookup_enabled)
    if settings.display_cargo_bar:
        add_line(content, row, wrap, format_ship_cargo(run.cargo))
        row += 1
    for text in mission_need_lines():
        add_line(content, row, wrap, text)
        row += 1
    if settings.display_prospector_hints:
        grades = ", ".join(f"{grade} x{count}" for grade, count in sorted(
            run.content_counts.items(), key=lambda kv: -kv[1]))
        suffix = f" ({grades})" if grades else ""
        if run.duplicate_prospected:
            suffix += f" [{run.duplicate_prospected} duplicate(s) ignored]"
        add_line(content, row, wrap, f"Asteroids prospected: {run.prospected_count}{suffix}")
        row += 1
        if run.prospected_commodities:
            add_line(content, row, wrap, f"Materials seen: {format_materials_seen(run)}")
            row += 1
        if run.last_rock is not None:
            add_line(content, row, wrap, mining_alerts.rock_text(run.last_rock))
            row += 1
        if run.cores_found:
            add_line(content, row, wrap, f"Core asteroids found: {run.cores_found} (last: {run.last_core})")
            row += 1
        if run.asteroids_cracked:
            add_line(content, row, wrap, f"Asteroids cracked (core mining): {run.asteroids_cracked}")
            row += 1
        count = limpets_on_board(run)
        onboard_suffix = f" ({count} on board)" if count else ""
        add_line(content, row, wrap,
                f"Limpets launched: {format_counts(run.limpets_launched)}{onboard_suffix}")
        row += 1
    if settings.display_session_totals:
        add_line(content, row, wrap,
                f"Refined: {format_counts(run.refined, with_mine_via=settings.display_prospector_hints)}")
        row += 1
        add_line(content, row, wrap, format_rate_now(run))
        row += 1
        add_line(content, row, wrap, format_run_average(run))
        row += 1
        full = format_time_to_full(run, *ship_hold(run.cargo))
        if full:
            add_line(content, row, wrap, full)
            row += 1
        for text in mining_market.lines(run.refined):         # docked with the market open: what this station pays for what the run refined, against the average
            add_line(content, row, wrap, text)
            row += 1

    place_button_bar(buttons, row, _shown_buttons(
        settings, hotspot_finder=True, price_finder=True, reserve_lookup=True))


def render_surface_mining(content: tk.Frame, wrap: int, buttons: Optional[PanelButtons], settings: PanelSettings,
                          sources: Optional[mining_sources.Sources] = None) -> None:
    """`sources` is where the data is read from: WFMT's own state unless the simulation passes its own."""
    src = sources or mining_sources.real()
    repo = src.surface
    run = repo.current_run()
    row = 0

    if run is None:
        add_line(content, row, wrap, "No commander detected yet.")
        row += 1
        # The Mining Book / Import/Export Hotspots stay available
        # even pre-commander-detection: mining_hotspots.py's list isn't
        # per-commander, so neither needs anything from `run`.
        place_button_bar(buttons, row, _shown_buttons(settings, price_finder=True))
        return

    is_active = repo.is_active
    if is_active or run.has_data():
        add_line(content, row, wrap,
                "Rhino deployed" if is_active else "Rhino stowed (last deployment)")
        row += 1
        if settings.display_cargo_bar and is_active:           # the hold and the rate describe the Rhino out now; once it is stowed they are the last run's leftovers
            add_line(content, row, wrap, format_srv_cargo(run.cargo))
            row += 1
            ship_run = src.space.current_run()
            if ship_run is not None:
                add_line(content, row, wrap, format_ship_cargo(ship_run.cargo, "Ship hold"))
                row += 1
        if settings.display_session_totals:
            add_line(content, row, wrap, f"Refined: {format_counts(run.refined)}")
            row += 1
            if is_active:
                add_line(content, row, wrap, format_rate_now(run))
                row += 1
            add_line(content, row, wrap, format_run_average(run))
            row += 1
            full = format_time_to_full(run, run.cargo, surface_mining.RHINO_CARGO_CAPACITY, "SRV hold", live=is_active)
            if full:
                add_line(content, row, wrap, full)
                row += 1
            add_line(content, row, wrap,
                    f"Transferred to ship: {format_counts(run.transferred_to_ship)}")
            row += 1
            add_line(content, row, wrap,
                    f"Raw materials: {format_counts(run.raw_materials)}")
            row += 1
    else:
        add_line(content, row, wrap,
                "No active Rhino deployment. Launch the Rhino to start tracking a new run.")
        row += 1

    if settings.display_prospector_hints:
        signal = repo.latest_signal()
        if signal is not None:
            add_line(content, row, wrap,
                    f"Last DSS scan: {signal.count} Planetary Mining Location(s) on {signal.body_name}")
            row += 1

    current_system, current_body = repo.current_system, repo.current_body
    matches: list = []
    if current_body:
        matches = src.hotspots.for_body(current_system, current_body)
        if matches:
            add_line(content, row, wrap, f"Known hotspots here ({len(matches)}):\n{format_hotspots(matches)}")
            row += 1

    if settings.display_coverage_minimap and current_body:
        row = render_coverage_minimap(content, row, current_system, current_body, matches)

    if current_body:
        row = render_site_lines(content, row, wrap, current_system, current_body, matches, settings.rig_gap_m, src)
        row = render_rig_line(content, row, wrap, src, src.rig_gap_override if src.rig_gap_override is not None else settings.rig_gap_m)

    place_button_bar(buttons, row, _shown_buttons(settings, price_finder=True))


def render_rig_line(content: tk.Frame, row: int, wrap: int, src: mining_sources.Sources, rig_gap_m: int = 0) -> int:
    """How many rigs you have noted on this body (`mining_rigs.py`) and where the Rhino stands against the nearest: inside its rig gap (too close for the next) or clear of it. Nothing
    until a rig is noted. Returns the next free row."""
    repo, position = src.surface, src.position()
    radius = repo.radius_for_current_body() or (position.planet_radius if position else None)
    if position is None or not radius:
        return row
    spacing = src.rigs.spacing(repo.current_system, repo.current_body, position.latitude, position.longitude, radius, rig_gap_m)
    if spacing is None:
        return row
    text = f"Rigs noted: {spacing.count}. Nearest {format_distance(spacing.nearest_m)} from you"
    if rig_gap_m:
        text += f": inside your {rig_gap_m:,} m rig gap, too close for the next." if spacing.inside else f": clear of your {rig_gap_m:,} m rig gap."
    else:
        text += ". Set a rig gap in Settings → Mining to see the spacing bands."
    add_line(content, row, wrap, text)
    return row + 1


def render_site_lines(content: tk.Frame, row: int, wrap: int, system: Optional[str], body: str, saved: list, rig_gap_m: int = 0,
                      sources: Optional[mining_sources.Sources] = None) -> int:
    """What CTR and BRD last did; for the marked mining location nearest you its size, whether you are inside it, where its center is and how much of its edge the ground driven covers;
    and the saved deposit nearest you, with, when the commander has set a distance, whether it is far enough away to place another rig."""
    src = sources or mining_sources.real()
    store = src.coverage
    if store.last_message:
        add_line(content, row, wrap, store.last_message)
        row += 1
    body_radius = src.surface.radius_for_current_body()
    position = src.position()
    if not body_radius or position is None:
        return row
    body_coverage = store.for_body(system, body)
    near = body_coverage.nearest_site(position.latitude, position.longitude, body_radius) if body_coverage else None
    if near is not None:
        site, distance = near
        heading = bearing.compass_point(bearing.initial_bearing_deg(position.latitude, position.longitude, site.center.latitude, site.center.longitude))
        where = f"center {format_distance(distance)} {heading} of you"
        site_radius = site.radius_m(body_radius)
        if site_radius is None:
            add_line(content, row, wrap, f"Nearest marked location: {where}. Border not marked yet (BRD).")
        else:
            covered = body_coverage.edge_covered(site, body_radius)
            edge = f", edge driven {covered * 100:.0f}%" if covered is not None else ""
            inside, margin = body_coverage.inside(site, position.latitude, position.longitude, body_radius)
            place = f"you are inside it, {format_distance(margin)} from the edge" if inside else f"you are outside it by {format_distance(margin)}"
            add_line(content, row, wrap, f"Nearest marked location: {site_radius / 1000:.2f} km radius, {place}; {where}{edge}")
        row += 1
    spot = mining_stops.nearest_deposit(saved, body_radius, position.latitude, position.longitude)
    if spot is not None:
        deposit, distance, heading_deg = spot
        text = f"Nearest saved deposit: {deposit.material}, {format_distance(distance)} {bearing.compass_point(heading_deg)} of you"
        if rig_gap_m:
            text += (f". Closer than your {rig_gap_m:,} m rig gap: too close to place another rig." if distance < rig_gap_m
                     else f". Beyond your {rig_gap_m:,} m rig gap: far enough to place another rig.")
        add_line(content, row, wrap, text)
        row += 1
    return row


SHIP_MINIMAP_MAX_ALTITUDE_M = 2000.0
"""With no Rhino deployed the minimap shows only under this altitude (the
2 km radar range), so a ship cruising high over a body doesn't keep a map
up. Altitude unknown counts as too high. In the Rhino it always shows."""


def render_coverage_minimap(content: tk.Frame, row: int, system: Optional[str], body: str,
                            known_hotspots: list) -> int:
    """The current body's coverage minimap (mining_coverage.py/
    mining_coverage_render.py), as a fixed-size in-panel image - see
    mining_coverage_render.py's module docstring for the scope
    deliberately left out of this first pass. Renders nothing (returns
    `row` unchanged) rather than a blank/stale image when there's
    nothing recorded yet for this body and no live position either, same
    "say nothing until known" principle used throughout this project."""
    body_coverage = coverage.coverage_repository.for_body(system, body)
    radius = surface_mining.surface_mining_repository.radius_for_current_body()
    position = live_position.current_position()
    if (not surface_mining.surface_mining_repository.is_active and position is not None
            and (position.altitude is None or position.altitude > SHIP_MINIMAP_MAX_ALTITUDE_M)):
        return row  # in the ship, the map only appears inside scanner range of the ground
    current_point = (coverage.CoveragePoint(position.latitude, position.longitude)
                     if position is not None else None)
    image = coverage_render.render(body_coverage, radius, current_point, known_hotspots)
    if image is None:
        return row

    photo = tk.PhotoImage(data=coverage_render.to_photo_data(image))
    label = tk.Label(content, image=photo)
    label.image = photo  # keep a reference - PhotoImage has no other owner
    label.grid(row=row, column=0, pady=(2, 4))
    return row + 1


def mark_site(border: bool, sources: Optional[mining_sources.Sources] = None) -> str:
    """CTR (`border` False) or BRD (True): mark the center or the border of the mining location you are at, from the live position. Returns what was done, or why not."""
    src = sources or mining_sources.real()
    repo = src.surface
    position = src.position()
    if position is None:
        src.coverage.last_message = "WFMT cannot read your position: be on or just above the ground."
        return src.coverage.last_message
    return src.coverage.mark(repo.current_system or "", repo.current_body or "", position.latitude, position.longitude,
                                             repo.radius_for_current_body() or 0.0, border)


def open_add_hotspot_dialog(parent: tk.Misc, sources: Optional[mining_sources.Sources] = None) -> None:
    from . import mining_hotspot_dialog as hotspot_dialog

    src = sources or mining_sources.real()
    repo = src.surface
    # Prefer the live on-foot/on-vehicle position (mining_live_position.py,
    # from Status.json) over the ship's last Touchdown spot - a commander
    # hitting this button has usually driven the Rhino away from the
    # touchdown point to the actual deposit by then, so Touchdown would
    # pre-fill a stale location. Falls back to Touchdown only when live
    # position isn't available (FlagsHasLatLong not currently set, or an
    # older game/EDMC version that doesn't populate it).
    position = src.position()
    if position is not None:
        prefill_latitude, prefill_longitude = position.latitude, position.longitude
    else:
        touchdown = repo.last_touchdown
        prefill_latitude = touchdown.latitude if touchdown else None
        prefill_longitude = touchdown.longitude if touchdown else None
    hotspot_dialog.open_hotspot_dialog(
        parent,
        on_save=lambda hotspot: src.hotspots.add_or_merge(
            dataclasses.replace(hotspot, ground=mining_ground.ground_in_survey(
                system_body_survey, hotspot.system, hotspot.body)),
            repo.radius_for_current_body()),
        prefill_system=repo.current_system or "",
        prefill_body=repo.current_body or "",
        prefill_latitude=prefill_latitude,
        prefill_longitude=prefill_longitude,
    )
