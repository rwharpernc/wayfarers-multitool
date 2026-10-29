"""Route Planner: the Exploration panel's button for it, and the owner of its window (route_planner_window.py).

It keeps what the plotter needs from the game: the ship (the `Loadout` event, and the cargo on board from Status.json), the system the commander is in and its address, and the
route once one is plotted. Spansh's exact plotter works out the jump range from the ship itself, so nothing about the ship is typed. Arriving in a system on the route moves the position along it, which the window shows and (if ticked) copies the next system for. The line
under the button says what is next. The plotted route is kept per commander (route_planner_state.py) so it survives a restart; nothing is sent until the window's **Generate route** button is pressed.

The button sits in the Exploration panel's collapsible Route Planner section (folded by default).
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from typing import Any, Dict, List, Mapping, Optional, Tuple

from config import appname, config

from . import expedition, expedition_hub, expedition_panel, expedition_window, route_planner as NP
from . import carrier_route_panel, route_planner_state, route_planner_window, route_secondary, panelkit, ship_current, spansh_exact

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "exploration"
ARRIVALS = ("FSDJump", "CarrierJump", "Location")
IDLE_TEXT = "Plots a route with Spansh for your ship."


def summary_text(route: Optional[NP.Route], copied: str = "") -> str:
    """The line beside the button: what is next on the route (and that it is on the clipboard), or what the button does."""
    if route is None or not route.legs:
        return IDLE_TEXT
    nxt = route.next_leg
    if nxt is None:
        return f"Arrived at {route.end}."
    text = f"Next: {nxt.system}" + (" (neutron)" if nxt.neutron else " (white dwarf)" if nxt.white_dwarf else "") + f" · {route.jumps_left} jumps left"
    return text + (" · copied" if copied and copied == nxt.system else "")


def route_stops(route: NP.Route) -> List[Tuple[str, str, str, Optional[NP.XYZ]]]:
    """The stops an expedition made from the route has: the systems still ahead where something is done (a neutron star, a marked white dwarf, a refuel) and the destination, in
    route order, each with what to do there. A neutron star the route marks as possibly a secondary star says so."""
    ahead = route.legs[route.reached:]
    stops = []
    for index, leg in enumerate(ahead):
        note = NP.notes_for(leg, leg.system.casefold() in route.suspect)
        if leg.boost or leg.refuel or index == len(ahead) - 1:
            stops.append((leg.system, "", note or "destination", leg.xyz))
    return stops


def expedition_name(route: NP.Route) -> str:
    """"Neutron Highway from <start> to <destination>", or without the destination when that would not leave room for a number after it."""
    start, end = " ".join(route.start.split()), " ".join(route.end.split())
    full = f"Neutron Highway from {start} to {end}"
    return full if len(full) <= 70 else f"Neutron Highway from {start}"[:80]


def route_key(route: NP.Route) -> Tuple[str, str, Tuple[str, ...]]:
    """What makes a plot the same plot: where it starts and ends and every system on it (not how far along it the commander is)."""
    return route.start.casefold(), route.end.casefold(), tuple(leg.system.casefold() for leg in route.legs)


class PlotterController:
    def __init__(self) -> None:
        self.ship = NP.ShipInfo()
        self.route: Optional[NP.Route] = None
        self.auto_copy = config.get_bool(route_planner_window.CONFIG_AUTO_COPY, default=True)
        self.auto_var: Optional[tk.BooleanVar] = None      # the tickbox on the panel; the window shares it so the two always agree
        self.copied = ""                                   # the system last put on the clipboard
        self._system = ""
        self._address: Optional[int] = None
        self._store = route_planner_state.RouteStore()      # the plotted route, kept per commander so it survives a restart
        self._cmdr = ""
        self._checker = route_secondary.SecondaryChecker(lambda id64: spansh_exact.fetch_stars(id64))     # looks at the neutron stops ahead for a neutron star that is a secondary star
        self._polling = False
        self._parent: Optional[tk.Misc] = None
        self._summary: Optional[tk.StringVar] = None
        self._made: Dict[Tuple[str, str, Tuple[str, ...]], str] = {}      # the expedition made from each plot (see `make_expedition`)

    # --- what the window reads ------------------------------------------------------------------------------------------
    def system(self) -> str:
        return self._system

    def address(self) -> Optional[int]:
        """The system address of the system the commander is in (from the arrival event), or None before one has been seen."""
        return self._address

    def start(self, plugin_dir: str) -> None:
        self._store.load(plugin_dir)
        carrier_route_panel.start(plugin_dir)

    def _save(self) -> None:
        self._store.put(self._cmdr, self.route)

    def _follow_commander(self, cmdr: str) -> bool:
        """Note which commander is playing. When it changes (the first event after EDMC starts is a change), put back the route they had; a route plotted before the commander was known is
        kept and saved for them. True when the route on show changed."""
        cmdr = str(cmdr or "").strip()
        if not cmdr or route_planner_state.commander_data.key_for(cmdr) == route_planner_state.commander_data.key_for(self._cmdr):
            return False
        first = not self._cmdr
        self._cmdr = cmdr
        if first and self.route is not None:
            self._save()
            return False
        restored = self._store.get(cmdr)
        if restored is not None and restored.next_leg is None:
            restored = None                      # already finished: nothing to follow
        self.route, self.copied = restored, ""
        self.check_ahead()
        return True

    def set_route(self, route: Optional[NP.Route]) -> None:
        self.route = route
        self._save()
        self.check_ahead()
        if self.auto_copy:
            self.copy_next()            # the first stop is on the clipboard as soon as the route is ready
        self._update()

    def learn_ship(self) -> bool:
        """Read the ship being flown from the journals when the game's `Loadout` was written before EDMC was running (a fallback: start-up also replays it). True when a ship is
        known afterwards."""
        if self.ship.loadout is None:
            loadout = ship_current.latest_loadout()
            if loadout is not None and self.ship.apply_loadout(loadout):
                route_planner_window.refresh_ship()
                self._update()
        return self.ship.loadout is not None

    def clear_route(self) -> bool:
        """Abandon the plotted route: the panel line, the window's table and the Route overlay all go back to having none, and the game's own route shows again. Returns
        whether there was a route to clear."""
        had = self.route is not None
        self.copied = ""
        self.set_route(None)
        return had

    def clear_all(self) -> bool:
        """CLEAR ROUTE: forget the Route Planner's route and the route the Route overlay is following from the game, so the overlay closes. Returns whether there was
        anything to clear."""
        try:
            from . import route_overlay
            had_game = route_overlay.get_state().forget_game_route()
        except Exception:
            logger.debug("Could not clear the Route overlay's route", exc_info=True)
            had_game = False
        had = self.clear_route()
        if self._summary is not None:
            try:
                self._summary.set("Route cleared." if had or had_game else "No route to clear.")
            except tk.TclError:
                pass
        return had or had_game

    def set_auto_copy(self, on: bool) -> None:
        """Switch the automatic copy of the next system on or off (remembered). Switching it on copies the next system straight away."""
        self.auto_copy = bool(on)
        config.set(route_planner_window.CONFIG_AUTO_COPY, self.auto_copy)
        if self.auto_var is not None and bool(self.auto_var.get()) != self.auto_copy:
            self.auto_var.set(self.auto_copy)
        if self.auto_copy:
            self.copy_next()
        self._update()

    def copy_next(self) -> str:
        """Put the next system on the route on the clipboard. Returns its name, or '' when there is nothing to copy or no clipboard."""
        nxt = self.route.next_leg if self.route is not None else None
        if nxt is None or self._parent is None:
            return ""
        try:
            self._parent.clipboard_clear()
            self._parent.clipboard_append(nxt.system)
        except tk.TclError:
            logger.debug("Could not copy the next neutron system", exc_info=True)
            return ""
        self.copied = nxt.system
        self._update()
        return nxt.system

    def _expedition_from(self, route: NP.Route) -> Optional[expedition.Expedition]:
        """The unfinished expedition already made from this plot, if there is one: the one remembered for it, or (after a restart of EDMC) one with its name that holds
        exactly the stops it would have."""
        book = expedition_panel.book
        known = book.get(self._made.get(route_key(route), ""))
        if known is not None and known.status != expedition.DONE:
            return known
        wanted, name = [expedition.name_key(stop[0][:expedition.MAX_SYSTEM]) for stop in route_stops(route)], expedition_name(route).casefold()
        return next((e for e in book.expeditions() if e.status != expedition.DONE and (e.name.casefold() == name or e.name.casefold().startswith(name + " ("))
                     and [expedition.name_key(s.system) for s in e.stops] == wanted), None)

    def make_expedition(self, start: bool = False) -> Tuple[Optional[str], str]:
        """The route as an Expedition planner expedition, started when `start` is true (with its Expedition Log run, as the Setting says). Returns (the expedition's id, or None
        when none was made; what to tell the commander). Pressing it again for the same plot picks the expedition made the first time instead of making another; one that
        is running or paused is left as it is. Neither a new plot nor Clear route changes an expedition."""
        route = self.route
        if route is None or not route.legs:
            return None, "Plot a route first."
        stops = route_stops(route)
        if not stops:
            return None, "You have arrived: there is nothing left to make an expedition from."
        book = expedition_panel.book
        if not book.ready:
            return None, "Expeditions are kept per commander and no commander is known yet. Log in first."
        made = self._expedition_from(route)
        created = made is None
        if made is None:
            name, taken, number = expedition_name(route), {x.name.casefold() for x in book.expeditions()}, 1
            base = name
            while name.casefold() in taken:
                number += 1
                name = f"{base[:70]} ({number})"
            try:
                made = book.create(name)
                book.add_planned(made.id, stops)
            except expedition.ExpeditionError as err:
                return None, str(err) or "Could not make the expedition."
            self._made[route_key(route)] = made.id
        expedition_window.select(made.id)
        if not start:
            return made.id, (f"Made '{made.name}' with {len(made.stops)} stops, not started. Check the order in the Expedition window, then press Start." if created else
                             f"'{made.name}' was made from this route already ({made.status}).")
        if made.status == expedition.ACTIVE:
            return made.id, f"'{made.name}' is already running."
        if made.status == expedition.PAUSED:
            return made.id, f"'{made.name}' is paused. Press Start in the Expedition window to carry on."
        try:
            began = expedition_panel.link.start(made.id)
        except expedition.ExpeditionError as err:
            return made.id, str(err)
        return made.id, " ".join(part for part in (f"Started '{made.name}': {len(made.stops)} stops.", began.log_words()) if part)

    def start_expedition(self) -> str:
        """START EXPEDITION: make the expedition from the route (unless it was made already), start it and its Expedition Log run, and say so."""
        return self.make_expedition(start=True)[1]

    def review_expedition(self) -> str:
        """REVIEW: open the Expedition window on the expedition made from the route, making it first (not started) when there is none."""
        made, said = self.make_expedition(start=False)
        if made is not None:
            expedition_panel.open_window(select=made)
        return said

    # --- the journal ----------------------------------------------------------------------------------------------------
    def handle_event(self, entry: Mapping[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        event = entry.get("event")
        changed = self._follow_commander(cmdr)
        carrier_route_panel.handle_event(entry, cmdr)            # the carrier route follows the commander's carrier (it ignores events that are not about one)
        if event == "Loadout":
            changed = self.ship.apply_loadout(entry)
        if event in ARRIVALS and isinstance(entry.get("StarSystem"), str) and entry["StarSystem"].strip():
            self._system = " ".join(entry["StarSystem"].split())
            address = entry.get("SystemAddress")
            self._address = address if isinstance(address, int) and not isinstance(address, bool) else None
            changed = True
            if self.route is not None and self.route.arrive(self._system):
                self._after_arrival()
        elif not self._system and system:
            self._system = system.strip()
        if changed:
            self._update()

    @staticmethod
    def overlay_note() -> str:
        """"Sent to the Route overlay." when that overlay is switched on (so the route is on screen), else nothing."""
        try:
            from . import route_overlay
            return "Sent to the Route overlay." if route_overlay.load_config().enabled else ""
        except Exception:
            logger.debug("Could not read the Route overlay's setting", exc_info=True)
            return ""

    def _after_arrival(self) -> None:
        """The commander reached a system on the route: copy the next one if they asked, and say what happened."""
        route = self.route
        if route is None:
            return
        self._save()
        self.check_ahead()
        if self.auto_copy:
            self.copy_next()
        note = self.overlay_note()
        if route.next_leg is None:
            route_planner_window.announce(f"Reached {self._system}: the end of the route. " + (note + " " if note else "") + "The route is reset in a few seconds.")
            return
        copied = f"{route.next_leg.system} is on the clipboard: paste it into the galaxy map." if self.auto_copy and self.copied else f"Next: {route.next_leg.system}."
        doubt = " Its neutron star may be a secondary star: check the system map." if route.next_leg.neutron and route.next_leg.system.casefold() in route.suspect else ""
        route_planner_window.announce(f"Reached {self._system}. {copied}{doubt}" + (" The Route overlay is updated." if note else ""))

    # --- neutron stars that may be secondary stars ---------------------------------------------------------------------
    def check_ahead(self) -> None:
        """Ask Spansh about the stars of the next few neutron stops (once each), in the background; the answers are marked as they arrive."""
        route = self.route
        if route is None:
            return
        stops = [(leg.id64, leg.system) for leg in route.legs[route.reached:] if leg.neutron and leg.id64 is not None and leg.system.casefold() not in route.checked]
        if stops[:route_secondary.WINDOW] and self._checker.ensure(stops[:route_secondary.WINDOW]):
            self._poll_checks()

    def _poll_checks(self) -> None:
        """Collect the answers the checker has (on the main thread) and keep looking until it is idle."""
        route = self.route
        found = self._checker.drain()
        if route is not None and found:
            newly = []
            for name, answer in found.items():
                route.checked.add(name)
                if answer:
                    route.suspect.add(name)
                    newly.append(name)
            ahead = {leg.system.casefold(): leg.system for leg in route.legs[route.reached:]}
            named = [ahead[name] for name in newly if name in ahead]
            if named:
                route_planner_window.announce("Check the system map at " + ", ".join(named[:3]) + (" and more" if len(named) > 3 else "")
                                              + ": the neutron star there may be a secondary star, so the supercharge needs a flight to it (marked NEUTRON ?).")
            self._update()
        if self._checker.busy() and self._parent is not None and not self._polling:
            self._polling = True
            self._parent.after(500, self._poll_again)

    def _poll_again(self) -> None:
        self._polling = False
        self._poll_checks()

    def dashboard_status(self, entry: Mapping[str, Any]) -> None:
        """Status.json: the cargo on board (the one ship number that changes while flying), which the plotter sends Spansh."""
        if self.ship.apply_status(entry):
            route_planner_window.refresh_ship()

    def _update(self) -> None:
        try:
            if self._summary is not None:
                self._summary.set(summary_text(self.route, self.copied))
            route_planner_window.refresh()
        except tk.TclError:
            pass         # the panel is gone
        self._refresh_route_overlay()

    @staticmethod
    def _refresh_route_overlay() -> None:
        """The Route overlay shows the neutron route in place of the game's, so it redraws whenever this one changes."""
        try:
            from . import route_overlay
            route_overlay.get_state().refresh()
        except Exception:
            logger.debug("Could not refresh the Route overlay", exc_info=True)

    # --- the panel ------------------------------------------------------------------------------------------------------
    def build_panel(self, parent: tk.Frame) -> None:
        self._parent = parent
        self._register_tab()
        self._summary = tk.StringVar(value=summary_text(self.route, self.copied))
        body = panelkit.collapsible_section(parent, "Route Planner", "wfmt_route_planner_collapsed")
        button = tk.Button(body, text="Plot", command=self.open)
        button.grid(row=0, column=0, sticky=tk.W, pady=(2, 0))
        panelkit.add_tooltip(button, "Route Planner: plot a neutron-star route to another system with Spansh's exact plotter, using your ship's numbers from the journal (no jump range to type). "
                                     "Best for long trips (the Bubble to deep space, Colonia). You paste each system into the galaxy map yourself; the next one is kept on the clipboard. "
                                     "Online, only when you press Plot in the window.")
        panelkit.wrap_label(body, min_wrap=150, textvariable=self._summary, anchor="w", font=panelkit.view_fonts()["small"]).grid(
            row=0, column=1, columnspan=2, sticky=tk.W, padx=(8, 0), pady=(2, 0))
        self._clear_button = tk.Button(body, text="Clear Route", command=self.clear_all)
        panelkit.add_tooltip(self._clear_button, "Clear the route: forget the route plotted here and the route the Route overlay is following, so the overlay closes")
        self._clear_button.grid(row=2, column=0, sticky=tk.W, pady=(2, 0))
        self.auto_var = tk.BooleanVar(master=parent, value=self.auto_copy)
        check = tk.Checkbutton(body, text="Copy the next system to the clipboard automatically", variable=self.auto_var,
                               command=lambda: self.set_auto_copy(bool(self.auto_var.get())))
        check.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        panelkit.add_tooltip(check, "When you plot a route, and each time you reach a stop on it, the next system's name is put on the clipboard, ready to paste into "
                                    "the galaxy map's search.")

    def _register_tab(self) -> None:
        expedition_hub.register(expedition_hub.ROUTE, lambda window, host: route_planner_window.show(window, self, host))

    def open(self) -> None:
        self.learn_ship()
        if self._parent is not None:
            self._register_tab()
            expedition_hub.show(self._parent, expedition_hub.ROUTE)

    def stop(self) -> None:
        route_planner_window.close()


controller = PlotterController()


def start(plugin_dir: str) -> None:
    controller.start(plugin_dir)


def stop() -> None:
    controller.stop()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def dashboard_status(entry: Dict[str, Any]) -> None:
    controller.dashboard_status(entry)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)


def open_window() -> None:
    controller.open()
