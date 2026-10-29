"""The Route Planner window: your ship's numbers read from the journal, a start and an end, and Spansh's exact-plotter route as a table you can read, copy from and follow.

It asks Spansh's exact plotter (spansh_exact), only when you press **Generate route**, for the route between two systems for your ship: it works out the jump range itself from the
ship's mass, fuel, cargo and drive, jump by jump, and says where to supercharge at a neutron star, where to refuel and (if you ask) where to use an FSD injection. The ship
block shows what it is being told, from the journal's loadout; nothing about the ship is typed. The start is the system you are in. The route stays in the table as you fly it:
systems you have reached turn green, the next one is marked, and **Copy next system** (or the automatic copy) puts its name on the clipboard for the galaxy map.
**Start expedition** turns the stops of the route (neutron stars, marked white dwarfs, refuels and the destination) into an Expedition planner expedition, starts it and starts its
Expedition Log run; **Review** opens the Expedition window on that expedition (making it, not started, if there is none) to check the order first.

The owner (`route_planner_panel`) is `ctx`: it supplies the ship, the current system and its address, the route, the clipboard copy and what to do with a finished route. The
Spansh call runs on a worker thread and its answer is picked up by an after() poll, so no widget is touched off the main thread.
"""
from __future__ import annotations

import json
import logging
import os
import queue
import threading
import time
import tkinter as tk
from typing import Any, Callable, List, Optional, Tuple

from config import appname, config

from . import carrier_route_window
from . import route_planner as NP
from . import spansh_exact, system_autocomplete
from .explore_dashboard_data import Row, Table
from .explore_dashboard_window import FieldBlock, TableBox
from .trade_spansh_client import RouteSearchError
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.widgets import Combobox, FlatButton, NoteLabel

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_neutron_plotter_geometry"
CONFIG_AUTO_COPY = "wfmt_neutron_plotter_auto_copy"
CONFIG_OPTIONS = "wfmt_neutron_plotter_options"          # the last route choices, as JSON
DEFAULT_SIZE = (1040, 800)
MIN_SIZE = (940, 580)
POLL_MS = 200
ANIMATE_MS = 90
BAR_HEIGHT = 8
CONFIRM_MS = 4000          # how long Start expedition reads "Started" after it has started one
BLOCK = 0.18

# What to tell the commander about when this is worth using and what it cannot do (the same words are in the guide, under Route Planner).
HELP = (
    ("Best for", "Long trips, such as the Bubble to deep space or Colonia. Inside the Bubble it may be no better than the route the galaxy map plots for you."),
    ("In the game", "The game takes no route from an add-on, so you paste each system into the galaxy map and set it yourself."),
    ("Clipboard", "WFMT keeps the next system on the clipboard, ready to paste."),
)

COLUMNS = (("number", "#", 48, "e"), ("system", "System", 280, "w"), ("distance", "Distance (ly)", 110, "e"), ("left", "Left (ly)", 100, "e"),
           ("fuel", "Fuel (t)", 80, "e"), ("do", "At this system", 240, "w"))

_window: Optional["RoutePlannerWindow"] = None


def show(parent: tk.Misc, ctx: Any, host: Optional[Callable[..., Any]] = None) -> "RoutePlannerWindow":
    """Open the window, or raise it if it is open. `host` builds it in a tab of the Expedition window (`expedition_hub.py`) instead of a window of its own. Returns the window."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return _window
    _window = RoutePlannerWindow(parent, ctx, host)
    return _window


def announce(text: str) -> None:
    """Say something in the open window's status line (the panel line has its own text)."""
    if _window is not None and _window.alive:
        _window._say(text)


def refresh() -> None:
    if _window is not None and _window.alive:
        _window.refresh()


def refresh_ship() -> None:
    if _window is not None and _window.alive:
        _window.refresh_ship()


def is_open() -> bool:
    return _window is not None and _window.alive


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def route_table(route: Optional[NP.Route]) -> Table:
    """The route as rows: reached jumps tagged done, the next one tagged map (amber), neutron stars tagged neutron."""
    rows: List[Row] = []
    if route is not None:
        for index, leg in enumerate(route.legs):
            tag = "done" if index < route.reached else ("map" if index == route.reached else ("neutron" if leg.boost else ""))
            rows.append(Row(str(leg.number), [str(leg.number), leg.system, f"{leg.distance:,.1f}", f"{leg.left:,.0f}",
                                              f"{leg.fuel_left:,.1f}" if leg.fuel_left is not None else "", NP.notes_for(leg, leg.system.casefold() in route.suspect)], tag))
    return Table(COLUMNS, rows, "Press Generate route to ask Spansh for a route.")


def saved_options() -> NP.Options:
    """The route choices used last time (the defaults when none, or when what was saved cannot be read)."""
    try:
        raw = json.loads(config.get_str(CONFIG_OPTIONS) or "{}")
        algorithm = raw.get("algorithm")
        return NP.Options(bool(raw.get("use_supercharge", True)), bool(raw.get("use_injections", False)), bool(raw.get("exclude_secondary", False)),
                          bool(raw.get("refuel_every_scoopable", False)), algorithm if algorithm in dict(NP.ALGORITHMS) else NP.DEFAULT_ALGORITHM,
                          bool(raw.get("mark_white_dwarfs", False)))
    except (ValueError, AttributeError, TypeError):
        return NP.Options()


class RoutePlannerWindow:
    def __init__(self, parent: tk.Misc, ctx: Any, host: Optional[Callable[..., Any]] = None) -> None:
        self._ctx = ctx
        self._results: "queue.Queue[Tuple[Any, Any]]" = queue.Queue()
        self._cancel: Optional[threading.Event] = None
        self._busy = False
        self._started = 0.0
        self._phase = 0.0
        self._spansh_note = ""
        self._activity_text = ""

        self._shell = (host or WindowShell)(
            parent, "Route Planner", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Route Planner help", HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._plot_button = self._shell.add_action("Generate route", self._plot, accent=True,
                                                tip="Generate route - ask Spansh for a neutron-boosted route from the source to the destination system for your ship")
        self._cancel_button = self._shell.add_action("Cancel", self._cancel_or_close,
                                                  tip="Cancel - stop waiting for Spansh while a route is being worked out, or close this window")
        body = self._shell.body

        top = tk.Frame(body, bg=P.BG)
        top.pack(fill="x")
        top.columnconfigure(0, weight=1, uniform="top")          # equal, fixed halves: nothing here resizes while you fly
        top.columnconfigure(1, weight=1, uniform="top")
        self._ship_block = FieldBlock(top, "Your ship (read from the journal)")
        self._ship_block.grid(row=0, column=0, sticky="nsew", padx=(0, P.PAD_SM))
        form = tk.Frame(top, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        form.grid(row=0, column=1, sticky="nsew", padx=(P.PAD_SM, 0))
        form.columnconfigure(1, weight=1)
        self._vars = {"start": tk.StringVar(value=ctx.system()), "end": tk.StringVar()}
        self._entries = {}
        for row, (label, key) in enumerate((("Source system", "start"), ("Destination system", "end"))):
            tk.Label(form, text=label, fg=P.MUTED, bg=P.CARD, anchor="w", font=style.font(P.FONT_BOLD)).grid(row=row, column=0, sticky="w", pady=2)
            entry = tk.Entry(form, textvariable=self._vars[key], width=14)
            entry.grid(row=row, column=1, sticky="ew", padx=P.PAD_SM, pady=2)
            system_autocomplete.attach(entry, self._vars[key])
            entry.bind("<Return>", lambda _e: self._plot())
            self._entries[key] = entry
        saved = saved_options()
        self._flags = {"use_supercharge": tk.BooleanVar(master=self._shell.window, value=saved.use_supercharge),
                       "use_injections": tk.BooleanVar(master=self._shell.window, value=saved.use_injections),
                       "exclude_secondary": tk.BooleanVar(master=self._shell.window, value=saved.exclude_secondary),
                       "refuel_every_scoopable": tk.BooleanVar(master=self._shell.window, value=saved.refuel_every_scoopable),
                       "mark_white_dwarfs": tk.BooleanVar(master=self._shell.window, value=saved.mark_white_dwarfs)}
        for row, (text, key) in enumerate((("Use supercharge", "use_supercharge"), ("Use FSD injections", "use_injections"),
                                           ("Exclude secondary stars", "exclude_secondary"), ("Refuel every scoopable", "refuel_every_scoopable"),
                                           ("Mark white dwarfs the route passes (asks EDSM)", "mark_white_dwarfs")), 2):
            tk.Checkbutton(form, text=text, variable=self._flags[key], fg=P.TEXT, bg=P.CARD, selectcolor=P.PANE, activebackground=P.CARD, activeforeground=P.TEXT,
                           anchor="w").grid(row=row, column=0, columnspan=2, sticky="w")
        tk.Label(form, text="Algorithm", fg=P.MUTED, bg=P.CARD, anchor="w", font=style.font(P.FONT_BOLD)).grid(row=7, column=0, sticky="w", pady=(4, 2))
        self._algorithm = tk.StringVar(master=self._shell.window, value=dict(NP.ALGORITHMS)[saved.algorithm])
        Combobox(form, textvariable=self._algorithm, values=[label for _key, label in NP.ALGORITHMS], state="readonly", width=16).grid(
            row=7, column=1, sticky="w", padx=P.PAD_SM, pady=(4, 2))
        NoteLabel(form, "Spansh works out the jump range itself from your ship, jump by jump. It starts from a full tank.", bg=P.CARD, padx=0).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self._activity = tk.Label(body, text="", fg=P.ACCENT, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD))
        self._activity.pack(fill="x", pady=(P.PAD, 2))
        self._bar = tk.Canvas(body, height=BAR_HEIGHT, bg=P.PANE, highlightthickness=0, bd=0)
        self._bar.pack(fill="x")
        self._summary = NoteLabel(body, fg=P.TEXT, bg=P.BG, font=P.FONT_BOLD, padx=0)
        self._summary.pack(fill="x", pady=(P.PAD, P.PAD_SM))

        actions = tk.Frame(body, bg=P.BG)
        actions.pack(fill="x", pady=(0, P.PAD_SM))
        FlatButton(actions, "Copy next system", self._copy_next, tip="Copy next system - copy the next system of the route to the clipboard").pack(side="left")
        FlatButton(actions, "Copy all remaining", self._copy_all, tip="Copy all remaining - copy every system still left on the route to the clipboard").pack(side="left", padx=(6, 0))
        self._start = FlatButton(actions, "Start expedition", self._start_expedition, width=len("Start expedition"),
                                   tip="Start expedition - make an expedition from this route and start it")
        self._start.pack(side="left", padx=(6, 0))
        FlatButton(actions, "Review expedition", lambda: self._say(self._ctx.review_expedition()),
                   tip="Review expedition - open the Expedition window on the expedition made from this route, making it first (not started) if there is none").pack(side="left", padx=(6, 0))
        FlatButton(actions, "Clear route", self._clear_route, tip="Clear route - forget the route, here, in the panel and in the Route overlay").pack(side="left", padx=(6, 0))
        FlatButton(actions, "Carrier route", lambda: carrier_route_window.show(self._shell.window),
                   tip="Carrier route - open the Carrier Route window, which plots a fleet carrier jump route").pack(side="left", padx=(6, 0))
        self._auto = ctx.auto_var if ctx.auto_var is not None else tk.BooleanVar(master=self._shell.window, value=ctx.auto_copy)
        tk.Checkbutton(body, text="Copy the next system to the clipboard automatically", variable=self._auto, command=self._save_auto, fg=P.TEXT, bg=P.BG,
                       selectcolor=P.PANE, activebackground=P.BG, activeforeground=P.TEXT).pack(anchor="w", pady=(0, P.PAD_SM))

        self._table = TableBox(body, "The route (double-click a system to copy it)", route_table(None), on_activate=self._copy_row)
        self._table.pack(fill="both", expand=True)
        self._table.table.tag_configure("map", foreground=P.ACCENT)
        self._table.table.tag_configure("neutron", foreground=P.INFO)
        self._shell.set_status("Type where you are going and press Generate route. Only the two systems and your ship's numbers go to Spansh.")
        self.refresh()
        self._entries["end"].focus_set()

    # --- the window ---------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        if self._cancel is not None:
            self._cancel.set()
        self._shell.close()

    def _save_auto(self) -> None:
        self._ctx.set_auto_copy(bool(self._auto.get()))
        if self._auto.get():
            self._say(f"On: the next system is copied now ({self._ctx.copied}) and after every jump." if self._ctx.copied else
                      "On: the next system will be copied when a route is ready and after every jump.")

    def _say(self, text: str, ok: bool = False) -> None:
        self._shell.set_status(text, ok)

    def _start_expedition(self) -> None:
        """START EXPEDITION: say what happened and, when it did start, show it on the button and in the success color for a few seconds."""
        said = self._ctx.start_expedition()
        started = said.startswith("Started '")
        self._say(said, ok=started)
        if started:
            self._start.configure(text="Started ✓", fg=P.OK)
            self._start.after(CONFIRM_MS, self._restore_start)

    def _restore_start(self) -> None:
        if self.alive and self._start.winfo_exists():
            self._start.configure(text="Start expedition", fg=P.TEXT)

    def _clear_route(self) -> None:
        """Clear the route (the panel, this table and the Route overlay all let go of it)."""
        if self._ctx.clear_all():
            self._say("Route cleared. The Route overlay is closed until a route is plotted.")
        else:
            self._say("There is no route to clear.")

    def _cancel_or_close(self) -> None:
        if self._busy and self._cancel is not None:
            self._cancel.set()
            self._spansh_note = "Cancelling"
            self._say("Cancelling...")
        else:
            self.close()

    def refresh_ship(self) -> None:
        """The ship block (it only changes with the loadout and the cargo)."""
        if self.alive:
            self._ship_block.set(self._ctx.ship.describe())

    def refresh(self) -> None:
        """Redraw the ship block, the route table and its summary (the table only rebuilds what changed)."""
        if not self.alive:
            return
        self.refresh_ship()
        route = self._ctx.route
        self._table.fill(route_table(route))
        self._summary.configure(text=route.summary() if route is not None else "")
        self._shell.set_subtitle(self._ctx.system() and f"You are in {self._ctx.system()}" or "")

    # --- the choices --------------------------------------------------------------------------------------------------

    def _options(self) -> NP.Options:
        labels = {label: key for key, label in NP.ALGORITHMS}
        return NP.Options(bool(self._flags["use_supercharge"].get()), bool(self._flags["use_injections"].get()), bool(self._flags["exclude_secondary"].get()),
                          bool(self._flags["refuel_every_scoopable"].get()), labels.get(self._algorithm.get(), NP.DEFAULT_ALGORITHM),
                          bool(self._flags["mark_white_dwarfs"].get()))

    def _remember(self, options: NP.Options) -> None:
        config.set(CONFIG_OPTIONS, json.dumps({"use_supercharge": options.use_supercharge, "use_injections": options.use_injections,
                                               "exclude_secondary": options.exclude_secondary, "refuel_every_scoopable": options.refuel_every_scoopable,
                                               "algorithm": options.algorithm, "mark_white_dwarfs": options.mark_white_dwarfs}))

    # --- plotting -----------------------------------------------------------------------------------------------------

    def _plot(self) -> None:
        if self._busy:
            return
        start, end = " ".join(self._vars["start"].get().split()), " ".join(self._vars["end"].get().split())
        if not start or not end:
            self._say("Give both the system to start from and the system to go to.")
            return
        try:
            self._ctx.learn_ship()
            self._ctx.ship.params()
        except NP.PlotterError as err:
            self._say(str(err))
            return
        options = self._options()
        self._remember(options)
        start_id = self._ctx.address() if start.casefold() == (self._ctx.system() or "").casefold() else None
        self._busy = True
        self._started, self._phase, self._spansh_note = time.monotonic(), 0.0, ""
        self._cancel = threading.Event()
        self._plot_button.configure(text="Plotting...")
        self._plot_button.set_enabled(False)
        self._say("Sent to Spansh. A long route can take a minute or two. You can cancel at any time.")
        self._animate()
        threading.Thread(target=self._worker, args=(start, end, options, start_id, self._cancel), daemon=True).start()
        self._shell.window.after(POLL_MS, self._poll)

    def _animate(self) -> None:
        if not self.alive:
            return
        if not self._busy:
            self._bar.delete("all")
            return
        seconds = int(time.monotonic() - self._started)
        # No animated dots: they changed the width of the line, so everything after them jumped ten times a second. The bar moves; the text changes only when the
        # timer ticks over or Spansh says something new.
        text = f"Plotting  {seconds // 60}:{seconds % 60:02d} waited" + (f"  ·  {self._spansh_note}" if self._spansh_note else "")
        if text != self._activity_text:
            self._activity_text = text
            self._activity.configure(text=text, fg=P.ACCENT)
        width = max(self._bar.winfo_width(), 1)
        block = width * BLOCK
        left = (width + block) * (self._phase % 1.0) - block
        self._bar.delete("all")
        self._bar.create_rectangle(max(left, 0), 0, min(left + block, width), BAR_HEIGHT, fill=P.ACCENT, outline="")
        self._phase += ANIMATE_MS / 1600.0
        self._shell.window.after(ANIMATE_MS, self._animate)

    def _finished(self, message: str = "") -> None:
        self._busy = False
        self._plot_button.configure(text="Generate route")
        self._plot_button.set_enabled(True)
        self._bar.delete("all")
        self._activity_text = message
        self._activity.configure(text=message, fg=P.DANGER if message else P.ACCENT)

    def _worker(self, start: str, end: str, options: NP.Options, start_id: Optional[int], cancel: threading.Event) -> None:
        """Runs off the main thread: it must not touch any Tk widget. Progress goes through the queue."""
        def tell(text: str) -> None:
            if text:
                self._results.put((None, text))
        try:
            route = spansh_exact.plot(self._ctx.ship, start, end, options, start_id, cancel, tell)
        except (RouteSearchError, NP.PlotterError) as err:
            self._results.put((end, str(err)))
        except Exception:
            logger.exception("Spansh exact plotter failed")
            self._results.put((end, "Could not reach Spansh. Check your connection and try again."))
        else:
            self._results.put((end, route))

    def _poll(self) -> None:
        done = None
        while True:
            try:
                key, payload = self._results.get_nowait()
            except queue.Empty:
                break
            if key is None:
                self._spansh_note = str(payload).rstrip(".")
            else:
                done = (key, payload)
        if done is None:
            if self.alive and self._busy:
                self._shell.window.after(POLL_MS, self._poll)
            return
        if not self.alive:
            self._busy = False
            return
        _key, payload = done
        if isinstance(payload, str):
            self._finished(payload)
            self._say("Not plotted. Fix what it says, or try again.")
            return
        self._finished()
        if not payload.legs:
            self._say("Spansh found no route between those systems for your ship. Try a nearer destination, or another algorithm.")
            return
        warning = " EDSM could not be reached, so white dwarfs are not marked." if payload.white_dwarf_check == "failed" else ""
        if self._ctx.ship.has_fuel_scoop() is False and any(leg.refuel for leg in payload.legs):
            warning += " WARNING: no fuel scoop is fitted, and this route has refuel stops that need one."
        payload.arrive(self._ctx.system())          # already at a system on the route
        self._ctx.set_route(payload)
        self.refresh()
        note = self._ctx.overlay_note()
        self._say(f"Route ready: {len(payload.legs)} jumps. " + (note + " " if note else "")
                  + (f"{self._ctx.copied} is on the clipboard: paste it into the galaxy map." if self._ctx.auto_copy and self._ctx.copied
                     else "Copy the next system into the galaxy map, jump, and repeat.") + warning)

    # --- using the route ----------------------------------------------------------------------------------------------

    def _clip(self, text: str, said: str) -> None:
        self._shell.window.clipboard_clear()
        self._shell.window.clipboard_append(text)
        self._say(said)

    def _copy_next(self) -> None:
        route = self._ctx.route
        if route is None or route.next_leg is None:
            self._say("No route to copy from: plot one first." if route is None else "You have arrived: nothing left to copy.")
            return
        name = self._ctx.copy_next()
        self._say(f"Copied {name}. Paste it into the galaxy map's search." if name else "Could not use the clipboard.")

    def _copy_all(self) -> None:
        route = self._ctx.route
        text = NP.copy_all(route) if route is not None else ""
        if not text:
            self._say("Nothing left to copy.")
            return
        self._clip(text, f"Copied {text.count(chr(10)) + 1} systems, one per line.")

    def _copy_row(self, iid: str) -> None:
        route = self._ctx.route
        if route is None or not iid.isdigit() or not 1 <= int(iid) <= len(route.legs):
            return
        leg = route.legs[int(iid) - 1]
        self._clip(leg.system, f"Copied {leg.system}.")
