"""Route overlay: the route you are following, on one overlay card: a copy of what the Route Planner plotted, or of the route the game's galaxy map worked out.

The card says where you are going and in how many jumps, then lists the systems still to visit, the next first, each with its star in a color, and ends with the light years left:

    You are navigating to:
    <the destination>
    You will be there in 12 jumps.
    ------
    <next system>        NEUTRON
    <the one after> ...
    ------
    4,310 LY left to jump.

A system is taken off the list as you reach it, and the jump count and the light years follow. A route plotted in the Route Planner replaces the game's plotted route on
the card until its last jump; with neither, nothing is drawn. Fuel and range are not on this card (the Exploration Dashboard shows them).

Nothing is sent anywhere unless the EDSM option is ticked: the card reads the journal, `NavRoute.json` and EDMC's copy of `Status.json`, and draws through the shared
overlay connection (EDMCModernOverlay, which WFMT does not install or launch). Settings-tab-only and off until ticked, like every overlay. Where the card sits is the global
Overlay Placement setting ("Route and ship status")."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import tkinter as tk

import myNotebook as nb
from config import appname, config

from . import fuel_alerts, journal_files, route_planner, overlay, overlay_appearance, overlay_link, overlay_placement, restore, route_edsm, route_plan
from .overlay import OverlayClient
from .overlay_card import Card, CardLayout, Line, Row, cut
from .overlay_style import LEGACY, Look
from .route_plan import Hop, RouteTracker

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None   # Settings-tab-only, no main-panel widget

_CFG_ENABLED = "wfmt_route_enabled"
_CFG_ROWS = "wfmt_route_rows"
_CFG_EDSM = "wfmt_route_edsm"                   # opt-in: ask EDSM which of the next systems it does not know

ROWS_RANGE = (3, 20)
DEFAULT_ROWS = 8
TICK_S = 1.0
OVERLAY_TTL = 4          # each draw lasts this long, so a stalled WFMT cannot leave the card up
END_SHOW_S = 10.0         # how long "Route ended" stays up before the route is reset and the card closes
RESEND_S = 3.0           # an unchanged card is drawn again this often, so it does not expire between fuel changes


@dataclass
class RouteConfig:
    enabled: bool = False
    rows: int = DEFAULT_ROWS
    edsm: bool = False          # mark the systems ahead that EDSM does not know (sends their names to EDSM; off until ticked)


def clamp_rows(value: Any) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return DEFAULT_ROWS
    return max(ROWS_RANGE[0], min(ROWS_RANGE[1], number))


def load_config() -> RouteConfig:
    return RouteConfig(enabled=config.get_bool(_CFG_ENABLED, default=False), rows=clamp_rows(config.get_str(_CFG_ROWS)),
                       edsm=config.get_bool(_CFG_EDSM, default=False))


def save_config(cfg: RouteConfig) -> None:
    config.set(_CFG_ENABLED, cfg.enabled)
    config.set(_CFG_ROWS, str(cfg.rows))
    config.set(_CFG_EDSM, cfg.edsm)


# --- what the card says (pure) ---------------------------------------------------------------------------------------

TAG_CHARS = 11                    # the widest star text ("WHITE DWARF")
SAMPLE_TAG = "WHITE DWARF"
NAME_CHARS = 32                   # characters of "NN. System name" in a row (the longest procedural names run about 28); a longer one is cut with an ellipsis

# The color of a star on the card: blue for a neutron star, red for a white dwarf, green for a star you can scoop fuel from, yellow for one you cannot.
_KIND_ROLE = {route_plan.KIND_NEUTRON: "info", route_plan.KIND_WHITE_DWARF: "danger", route_plan.KIND_SCOOPABLE: "ok", route_plan.KIND_NO_SCOOP: "warn"}
_KIND_WORD = {route_plan.KIND_NEUTRON: "neutron star", route_plan.KIND_WHITE_DWARF: "white dwarf"}


def _jumps(count: int) -> str:
    return f"{count} jump" + ("" if count == 1 else "s")


def fuel_line(tracker: RouteTracker, low_percent: int = fuel_alerts.DEFAULT_LOW_PERCENT) -> Optional[Line]:
    """The fuel on board (red when it is low), or None before the game has said."""
    watcher = tracker.fuel
    if watcher.fuel is None:
        return None
    percent = watcher.percent()
    if percent is not None and watcher.capacity:
        text = f"Fuel {percent:.0f}%  {watcher.fuel:.1f} / {watcher.capacity:.0f} t"
    else:
        text = f"Fuel {watcher.fuel:.1f} t"
    low = (percent is not None and percent <= low_percent) or (percent is None and bool(watcher.flags & fuel_alerts.FLAG_LOW_FUEL))
    return text, "danger" if low else "text"


def status_lines(tracker: RouteTracker, low_percent: int = fuel_alerts.DEFAULT_LOW_PERCENT) -> List[Line]:
    """The travel status lines: fuel, range, what is left of the route and the next supercharge. A number the game has not given yet
    leaves its line out."""
    lines: List[Line] = []
    fuel = fuel_line(tracker, low_percent)
    if fuel is not None:
        lines.append(fuel)
    parts = []
    if tracker.jump_range is not None:
        parts.append(f"Range {tracker.jump_range:.1f} ly")
    if tracker.last_fuel_used is not None:
        parts.append(f"Last jump {tracker.last_fuel_used:.1f} t")
    if parts:
        lines.append(("   ".join(parts), "text"))
    ahead = tracker.remaining()
    if ahead:
        left = tracker.distance_left()
        lines.append((f"{_jumps(len(ahead))} left" + (f"   {left:,.0f} ly" if left is not None else ""), "title"))
        found = tracker.next_supercharge()
        if found is not None:
            number, hop = found
            kind = route_plan.star_kind(hop.star_class)
            lines.append((f"Next supercharge: {_jumps(number)}, {_KIND_WORD[kind]}", _KIND_ROLE[kind]))
        else:
            lines.append(("No supercharge on the route", "muted"))
    return lines


NEW_MARK = " *"                   # after a system's name: EDSM does not know it (only when that option is ticked)
CHECK_AHEAD = 30                  # systems asked about at once (the rows shown and a few beyond, so scrolling down the route is already answered)


Stop = Tuple[str, str, str]       # (system, star text, color role): one row of the card


def game_stop(hop: Hop) -> Stop:
    """A system of the game's plotted route with its star: the class letters of a star you can scoop (green), a name for one you cannot (yellow), NEUTRON (blue) or WHITE DWARF (red)."""
    tag, kind = route_plan.star_tag(hop.star_class)
    return hop.name, cut(tag, TAG_CHARS), _KIND_ROLE.get(kind, "muted")


def planned_stop(leg: "route_planner.Leg", suspect: bool = False) -> Stop:
    """A system of a Route Planner route with its star, from what the planner knows: a neutron star (blue), a white dwarf (red), a scoopable star (FUEL, green), else NO FUEL (yellow)."""
    if leg.neutron and suspect:
        return leg.system, "NEUTRON ?", _KIND_ROLE[route_plan.KIND_NO_SCOOP]       # yellow: the neutron star may be a secondary star, away from where you arrive
    if leg.neutron:
        return leg.system, "NEUTRON", _KIND_ROLE[route_plan.KIND_NEUTRON]
    if leg.white_dwarf:
        return leg.system, "WHITE DWARF", _KIND_ROLE[route_plan.KIND_WHITE_DWARF]
    if leg.scoopable:
        return leg.system, "FUEL", _KIND_ROLE[route_plan.KIND_SCOOPABLE]
    return leg.system, "NO FUEL", _KIND_ROLE[route_plan.KIND_NO_SCOOP]


def navigation_card(destination: str, jumps: int, left: Optional[float], stops: Sequence[Stop], rows: int = DEFAULT_ROWS,
                    unknown: Callable[[str], bool] = lambda name: False) -> Card:
    """The card for a route, the same for the game's plotted route and the Route Planner's: where you are going, how many jumps it is, then the systems still to
    visit (the next first; one is taken off as it is reached), each with its star in a color, and the light years left. A system EDSM does not know gets a mark (when that
    option is on). Empty when there is nothing left to jump to."""
    if not stops:
        return Card()
    header = (("You are navigating to:", "muted"), (cut(destination, NAME_CHARS), "title"), (f"You will be there in {_jumps(jumps)}.", "text"))
    listed = tuple((cut(name, NAME_CHARS - len(NEW_MARK)) + NEW_MARK if unknown(name) else cut(name, NAME_CHARS), tag, role) for name, tag, role in stops[:rows])
    footer: Optional[Line] = (f"{left:,.0f} LY left to jump.", "text") if left is not None else None
    return Card(header, listed, footer, rule_after_header=True)


def ended_card(destination: str) -> Card:
    """The card shown for a few seconds when the end of the route is reached, before it is reset and the overlay closes."""
    return Card((("Route ended.", "title"), (f"You have arrived at {cut(destination, NAME_CHARS - 20)}.", "text"), ("The route is being reset.", "muted")))


def build_neutron_card(route: "route_planner.Route", rows: int = DEFAULT_ROWS, edsm: Optional["route_edsm.EdsmChecker"] = None) -> Card:
    """The card for a route plotted in the Route Planner, which replaces the game's route while there is a jump left to make."""
    ahead = route.legs[route.reached:]
    return navigation_card(route.end, route.jumps_left, route.distance_left, [planned_stop(leg, leg.system.casefold() in route.suspect) for leg in ahead], rows,
                           (lambda name: edsm.status(name) is False) if edsm is not None else (lambda name: False))


def build_card(tracker: RouteTracker, rows: int = DEFAULT_ROWS, edsm: Optional["route_edsm.EdsmChecker"] = None) -> Card:
    """The card for the route the game has plotted, from where the ship is on it. Empty when no route applies."""
    ahead = tracker.remaining()
    return navigation_card(tracker.route[-1].name if tracker.route else "", len(ahead), tracker.distance_left(), [game_stop(hop) for hop in ahead], rows,
                           (lambda name: edsm.status(name) is False) if edsm is not None else (lambda name: False))


# --- drawing -------------------------------------------------------------------------------------------------------------

# The card is drawn at this fixed origin; where it sits on the screen is the global Overlay Placement setting. Its top and its width
# are fixed, so it grows downward as rows are added and never moves sideways with what it says. The drawing itself is overlay_card's.
MAX_HEADER = 3              # you are navigating to / the destination / the jump count
GROUP_NAME = "wfmt_route"
GROUP_PREFIX = "wfmt_route_"
LAYOUT = CardLayout(GROUP_PREFIX, x=650, y=100, max_header=MAX_HEADER, max_rows=ROWS_RANGE[1], name_chars=NAME_CHARS, tag_chars=TAG_CHARS,
                    sample_tag=SAMPLE_TAG, sample_lines=MAX_HEADER + DEFAULT_ROWS + 3)
_X, _Y, _CARD_ID = LAYOUT.x, LAYOUT.y, LAYOUT.card_id


def block_rect(look: Look = LEGACY, card: Optional[Card] = None) -> tuple:
    """(left, top, width, height) of the card as `render` draws it. Placement uses the layout's sample height when no card is given."""
    return LAYOUT.block_rect(look, card)


def placed_client(client: OverlayClient, look: Look = LEGACY, card: Optional[Card] = None) -> OverlayClient:
    """`client` moved to where this card is placed, from the card's real size (so a bottom or right edge is the card's own edge)."""
    return overlay_placement.client_for_measured("route", client, block_rect(look, card), look)


def render(card: Card, client: OverlayClient, look: Look = LEGACY) -> None:
    """Draws the card, or clears it when it is empty. Every line starts at the card's left padding. Raises on an overlay failure; the
    live path swallows it and the Settings test reports it."""
    LAYOUT.render(card, client, look, ttl=OVERLAY_TTL)


def sample_tracker() -> RouteTracker:
    """A made-up trip for the Test Card: a neutron highway with a white dwarf and a black hole on it."""
    tracker = RouteTracker(system="Sol", jump_range=61.4, last_fuel_used=3.2)
    tracker.fuel.capacity, tracker.fuel.fuel = 32.0, 12.2
    classes = ("M", "N", "K", "DA", "G", "N", "H", "F", "N", "M", "K", "N")
    tracker.set_route([Hop("Sol", "G", (0.0, 0.0, 0.0))] + [
        Hop(f"Sample System {i}", c, (60.0 * i, 0.0, 0.0)) for i, c in enumerate(classes, 1)])
    return tracker


# --- state and the live path -------------------------------------------------------------------------------------------

def read_route_file() -> Optional[Any]:
    """The parsed `NavRoute.json` in the journal folder, or None when it is missing or unreadable."""
    folder = journal_files.journal_folder()
    if not folder:
        return None
    try:
        with open(os.path.join(folder, "NavRoute.json"), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def active_neutron_route() -> Optional["route_planner.Route"]:
    """The neutron route plotted in the Route Planner, while it has a stop left to go to; None otherwise (or when that feature cannot be loaded)."""
    try:
        from . import route_planner_panel
        route = route_planner_panel.controller.route
    except Exception:
        logger.debug("Could not read the neutron route", exc_info=True)
        return None
    return route if route is not None and route.next_leg is not None else None


def finished_neutron_route() -> Optional[str]:
    """The destination of the Route Planner's route when every jump on it has been made (it is kept until it is reset), else None."""
    try:
        from . import route_planner_panel
        route = route_planner_panel.controller.route
    except Exception:
        logger.debug("Could not read the neutron route", exc_info=True)
        return None
    return route.end if route is not None and route.legs and route.next_leg is None else None


def reset_neutron_route() -> None:
    """Forget the Route Planner's route (its panel line, its table and what it copied)."""
    try:
        from . import route_planner_panel
        route_planner_panel.controller.clear_route()
    except Exception:
        logger.debug("Could not reset the neutron route", exc_info=True)


class RouteOverlay:
    """The tracker, the route file and what is on the card. `draw`, `now`, `cfg` and `read` are injected so the behavior is tested
    without the overlay, the real clock or a journal folder."""

    def __init__(self, draw: Optional[Callable[[Card], None]] = None, now: Callable[[], float] = time.time,
                 cfg: Callable[[], RouteConfig] = load_config, read: Callable[[], Optional[Any]] = read_route_file,
                 edsm: Optional[route_edsm.EdsmChecker] = None,
                 neutron: Callable[[], Optional["route_planner.Route"]] = active_neutron_route,
                 neutron_done: Callable[[], Optional[str]] = finished_neutron_route, reset_neutron: Callable[[], None] = reset_neutron_route) -> None:
        self._lock = threading.RLock()
        self.tracker = RouteTracker()
        self._draw = draw or (lambda card: None)
        self._now = now
        self._cfg = cfg
        self._read = read
        self._neutron = neutron
        self._neutron_done = neutron_done
        self._reset_neutron = reset_neutron
        self._seen = False                 # a card with systems to visit has been shown since the last reset (so a stale route that was already finished says nothing)
        self._ended_at: Optional[float] = None
        self._edsm = edsm if edsm is not None else route_edsm.EdsmChecker()
        self._last: Optional[Card] = None
        self._last_sent = 0.0

    def _load_route(self) -> None:
        data = self._read()
        if data is not None:
            self.tracker.set_route(route_plan.parse_route(data))

    def handle_event(self, entry: Dict[str, Any], system: Optional[str] = None) -> None:
        event = entry.get("event")
        with self._lock:
            reload = self.tracker.handle_event(entry, system)
            if reload or event in ("LoadGame", "StartUp", restore.RESTORE_EVENT):
                try:
                    self._load_route()
                except Exception:   # a route that cannot be read must never stop the live path
                    logger.debug("Could not read the plotted route", exc_info=True)
        self.refresh()

    def handle_status(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self.tracker.handle_status(entry)
        self.refresh()

    def forget_game_route(self) -> bool:
        """Drop the route this overlay is following from the game (the Route Planner's CLEAR ROUTE button), so the card closes. The game's own route is untouched and comes
        back with the next `NavRoute` event, `LoadGame` or restart. True when there was one."""
        with self._lock:
            had = bool(self.tracker.route)
            self.tracker.route = []
            self._seen, self._ended_at = False, None
        self.refresh()
        return had

    def card(self) -> Card:
        cfg = self._cfg()
        plotted = self._neutron()
        if plotted is not None:                  # a route plotted in the Route Planner supersedes the game's plotted route
            with self._lock:
                self._seen, self._ended_at = True, None
                if cfg.edsm:
                    self._edsm.ensure([leg.system for leg in plotted.legs[plotted.reached:plotted.reached + max(cfg.rows, CHECK_AHEAD)]])
                return build_neutron_card(plotted, cfg.rows, edsm=self._edsm if cfg.edsm else None)
        with self._lock:
            done = self._neutron_done() if self._seen else None
            if done:
                return self._route_ended(done, planned=True)
            ahead = self.tracker.remaining()
            if ahead:
                self._seen, self._ended_at = True, None
                if cfg.edsm:
                    self._edsm.ensure([hop.name for hop in ahead[:max(cfg.rows, CHECK_AHEAD)]])      # asks in the background; the answer shows on a later draw
                return build_card(self.tracker, cfg.rows, edsm=self._edsm if cfg.edsm else None)
            if self._seen and self.tracker.on_route() and self.tracker.route:        # the last system of the game's route has been reached
                return self._route_ended(self.tracker.route[-1].name, planned=False)
            return Card()

    def _route_ended(self, destination: str, planned: bool) -> Card:
        """The end of the route has been reached: say so for END_SHOW_S, then reset that route (the Route Planner's, or the game's as this overlay knows it) and let the card close."""
        now = self._now()
        if self._ended_at is None:
            self._ended_at = now
        if now - self._ended_at < END_SHOW_S:
            return ended_card(destination)
        self._seen, self._ended_at = False, None
        if planned:
            self._reset_neutron()
        else:
            self.tracker.route = []
        return self.card()                 # whatever else applies now (the game's route after the planner's, or nothing)

    def refresh(self) -> None:
        """Draws the card when it changed (or now and then, so it does not expire). Does nothing when the Route overlay is off."""
        if not self._cfg().enabled:
            return
        card = self.card()
        now = self._now()
        if card == self._last and now - self._last_sent < RESEND_S:
            return
        if not card and not self._last:
            self._last = card
            return
        self._last, self._last_sent = card, now
        self._draw(card)

    def showing(self) -> bool:
        """Whether the card has anything to say, so the one-second tick keeps it from expiring."""
        return bool(self.card())


# --- wiring ----------------------------------------------------------------------------------------------------------------

_overlay_client = overlay.OverlayClient()


def set_overlay_client(client: overlay.OverlayClient) -> None:
    global _overlay_client
    _overlay_client = client


def _draw_live(card: Card) -> None:
    look = overlay_appearance.current_look()

    def worker() -> None:
        try:
            render(card, placed_client(_overlay_client, look, card), look)
        except OSError:
            logger.debug("Could not reach the overlay for the route card", exc_info=True)

    threading.Thread(target=worker, name="WFMT-route-render", daemon=True).start()


_state: Optional[RouteOverlay] = None
_ticker: Optional[threading.Thread] = None
_stop = threading.Event()


def get_state() -> RouteOverlay:
    global _state
    if _state is None:
        _state = RouteOverlay(draw=_draw_live)
    return _state


def _tick_loop() -> None:
    state = get_state()
    while not _stop.wait(TICK_S):
        try:
            if state.showing():
                state.refresh()
        except Exception:
            logger.debug("Route overlay tick failed", exc_info=True)


def start(plugin_dir: str) -> None:
    global _ticker
    _stop.clear()
    if _ticker is None or not _ticker.is_alive():
        _ticker = threading.Thread(target=_tick_loop, name="WFMT-route-tick", daemon=True)
        _ticker.start()


def stop() -> None:
    _stop.set()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    get_state().handle_event(entry, system)


def dashboard_status(entry: Dict[str, Any]) -> None:
    get_state().handle_status(entry)


# --- Settings tab ----------------------------------------------------------------------------------------------------------

_vars: Dict[str, Any] = {}
_result_label: Optional[nb.Label] = None


def build_settings(notebook: nb.Notebook) -> None:
    global _result_label
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Route")
    cfg = load_config()

    nb.Label(
        frame,
        text=("A card on your in-game overlay, through the overlay (WFMT's built-in one on Windows, or EDMCModernOverlay: a separate, optional helper WFMT does not install or launch; "
              "its connection settings are on the Overlay Connection tab). It says where you are navigating to and in how many jumps, then lists the systems still to visit, "
              "the next first, and ends with the light years left. It follows the route plotted in the Route Planner, or else the route the game's galaxy map plotted, and a "
              "system is taken off the list as you reach it. It comes from your journal and the game's NavRoute.json; nothing is sent anywhere."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
    overlay_link.add(frame)

    _vars["enabled"] = tk.BooleanVar(value=cfg.enabled)
    _vars["rows"] = tk.StringVar(value=str(cfg.rows))
    _vars["edsm"] = tk.BooleanVar(value=cfg.edsm)
    nb.Checkbutton(frame, text="Enable the Route overlay", variable=_vars["enabled"]).grid(row=2, column=0, sticky=tk.W, padx=10, pady=2)

    rows_row = tk.Frame(frame)
    rows_row.grid(row=3, column=0, sticky=tk.W, padx=(30, 10), pady=2)
    nb.Label(rows_row, text="Systems listed:").pack(side=tk.LEFT)
    tk.Spinbox(rows_row, from_=ROWS_RANGE[0], to=ROWS_RANGE[1], width=4, textvariable=_vars["rows"]).pack(side=tk.LEFT, padx=4)
    nb.Label(rows_row, text="(the jump count and the light years cover the whole route)").pack(side=tk.LEFT)

    nb.Checkbutton(frame, text="Mark the systems ahead that EDSM does not know yet (asks EDSM; sends the names of the next systems on your route)",
                   variable=_vars["edsm"]).grid(row=5, column=0, sticky=tk.W, padx=10, pady=2)
    nb.Label(frame, text=("A system EDSM has no record of has not been uploaded by anyone who shares with EDSM, so it may be a first discovery. Such a system gets a * after its "
                          "name. One request per few minutes at most, with the system names and nothing about you. Off until ticked."),
             wraplength=440, justify=tk.LEFT).grid(row=6, column=0, sticky=tk.W, padx=(30, 10), pady=(0, 6))

    nb.Label(
        frame,
        text=("The route is shown while you are in one of its systems; if you jump off it, the card clears until you plot a new route. The light years are the straight-line "
              "distances between the systems of the route."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=7, column=0, sticky=tk.W, padx=10, pady=(6, 4))

    action_row = tk.Frame(frame)
    action_row.grid(row=8, column=0, sticky=tk.W, padx=10, pady=(6, 2))
    tk.Button(action_row, text="Test Card", command=_test_card).pack(side=tk.LEFT)
    _result_label = nb.Label(action_row, text="", wraplength=320, justify=tk.LEFT)
    _result_label.pack(side=tk.LEFT, padx=(10, 0))
    nb.Label(frame, text="(Test Card works even while disabled above, and reports whether the overlay was actually reachable.)",
             wraplength=440, justify=tk.LEFT).grid(row=9, column=0, sticky=tk.W, padx=10, pady=(0, 10))


def _test_card() -> None:
    if _result_label is None:
        return
    cfg = overlay.load_config()
    client = overlay.OverlayClient(cfg)
    label = _result_label
    look = overlay_appearance.current_look()
    rows = clamp_rows(_vars["rows"].get()) if "rows" in _vars else DEFAULT_ROWS
    show_edsm = bool(_vars["edsm"].get()) if "edsm" in _vars else False

    def worker() -> None:
        try:
            sample = build_card(sample_tracker(), rows, edsm=route_edsm.sample_checker() if show_edsm else None)
            render(sample, placed_client(client, look, sample), look)
            outcome, color = "Sent: check your overlay.", "#2e7d32"
        except OSError as err:
            outcome, color = f"Could not reach the overlay at {cfg.host}:{cfg.port} ({err}).", "#c07000"
        try:
            label.after(0, lambda: label.configure(text=outcome, foreground=color))
        except tk.TclError:
            pass   # the Settings dialog was closed before the test finished

    threading.Thread(target=worker, name="WFMT-route-test", daemon=True).start()


def save_settings() -> None:
    if not _vars:
        return
    save_config(RouteConfig(enabled=bool(_vars["enabled"].get()), rows=clamp_rows(_vars["rows"].get()), edsm=bool(_vars["edsm"].get())))   # a card left up simply expires
