"""The Carrier Route window: a route for your fleet carrier from Spansh's fleet carrier router, as a table you can read, copy from and follow.

The carrier's details (where it is, the tritium in its tank, the space used) are read from the journal, so only the destination needs typing. Spansh's router works out the jumps, the
tritium each one uses and where to restock; it sends back the tritium you need to start with, or, if you tell it what you already have, whether that is enough. Only when you press
**Generate route** are the systems (by address) and the carrier's numbers sent to Spansh. The game takes no route from an add-on, so you copy each system and schedule the jump in
Carrier Management yourself: the route follows the carrier (systems it has reached turn green, the next is marked), and **Copy next system** puts the next one on the clipboard.

The owner is `carrier_route_panel.planner`. The Spansh call runs on a worker thread and its answer is picked up by an after() poll, so no widget is touched off the main thread.
"""
from __future__ import annotations

import logging
import os
import queue
import threading
import time
import tkinter as tk
from typing import Any, List, Optional, Tuple

from config import appname, config

from . import carrier_route as CR
from . import carrier_route_panel, carrier_route_spansh, system_autocomplete
from .explore_dashboard_data import Row, Table
from .explore_dashboard_window import FieldBlock, TableBox
from .trade_spansh_client import RouteSearchError
from .uikit import palette as P
from .uikit import style
from .uikit.shell import WindowShell
from .uikit.widgets import Combobox, FlatButton, NoteLabel

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_carrier_route_geometry"
DEFAULT_SIZE = (1000, 760)
MIN_SIZE = (820, 560)
POLL_MS = 200
TICK_MS = 500

HELP = (
    "Spansh's fleet carrier router works out each jump (up to 500 ly) and the tritium it uses.",
    "The game takes no route from an add-on: copy each system, schedule the jump in Carrier Management, and the route moves on when your carrier arrives.",
)

COLUMNS = (("number", "#", 48, "e"), ("system", "System", 270, "w"), ("distance", "Distance (ly)", 110, "e"), ("left", "Left (ly)", 100, "e"),
           ("tank", "Tank (t)", 80, "e"), ("market", "Market (t)", 90, "e"), ("do", "At this system", 220, "w"))

_window: Optional["CarrierRouteWindow"] = None


def show(parent: tk.Misc) -> None:
    """Open the window, or raise it if it is open."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return
    _window = CarrierRouteWindow(parent)


def is_open() -> bool:
    return _window is not None and _window.alive


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def route_table(route: Optional[CR.CarrierRoute]) -> Table:
    """The route as rows: reached jumps tagged done, the next one tagged map (amber)."""
    rows: List[Row] = []
    if route is not None:
        for index, leg in enumerate(route.legs):
            tag = "done" if index < route.reached else ("map" if index == route.reached else "")
            rows.append(Row(str(leg.number), [str(leg.number), leg.system, f"{leg.distance:,.1f}", f"{leg.left:,.0f}",
                                              f"{leg.tritium_left:,.0f}" if leg.tritium_left is not None else "",
                                              f"{leg.market:,.0f}" if leg.market is not None else "", CR.notes_for(leg)], tag))
    return Table(COLUMNS, rows, "Press Generate route to ask Spansh for a route.")


def _whole(text: str, default: int = 0) -> int:
    try:
        return max(0, int(float(str(text).replace(",", "").strip())))
    except ValueError:
        return default


class CarrierRouteWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self._planner = carrier_route_panel.planner
        self._results: "queue.Queue[Tuple[Any, Any]]" = queue.Queue()
        self._cancel: Optional[threading.Event] = None
        self._busy = False
        self._started = 0.0
        self._note = ""
        self._kind = CR.FLEET

        self._shell = WindowShell(
            parent, "Carrier Route", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Carrier Route help", HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._plot_button = self._shell.add_action("Generate route", self._plot, accent=True)
        self._cancel_button = self._shell.add_action("Cancel", self._cancel_or_close)
        body = self._shell.body

        top = tk.Frame(body, bg=P.BG)
        top.pack(fill="x")
        top.columnconfigure(0, weight=1, uniform="top")
        top.columnconfigure(1, weight=1, uniform="top")
        self._carrier_block = FieldBlock(top, "Your carrier (read from the journal)")
        self._carrier_block.grid(row=0, column=0, sticky="nsew", padx=(0, P.PAD_SM))
        form = tk.Frame(top, bg=P.CARD, padx=P.PAD, pady=P.PAD_SM)
        form.grid(row=0, column=1, sticky="nsew", padx=(P.PAD_SM, 0))
        form.columnconfigure(1, weight=1)
        self._vars = {"start": tk.StringVar(), "end": tk.StringVar(), "used": tk.StringVar(), "tank": tk.StringVar(), "market": tk.StringVar(value="0")}
        self._entries = {}
        self._kind_var = tk.StringVar(master=self._shell.window, value=CR.KIND_LABELS[CR.FLEET])
        tk.Label(form, text="Carrier", fg=P.MUTED, bg=P.CARD, anchor="w", font=style.font(P.FONT_BOLD)).grid(row=0, column=0, sticky="w", pady=2)
        self._kind_box = Combobox(form, textvariable=self._kind_var, values=list(CR.KIND_LABELS.values()), state="readonly", width=16)
        self._kind_box.grid(row=0, column=1, sticky="ew", padx=P.PAD_SM, pady=2)
        self._kind_box.bind("<<ComboboxSelected>>", lambda _e: self._kind_changed())
        for row, (label, key, width) in enumerate((("Where it is now", "start", 14), ("Destination system", "end", 14), ("Space used (t)", "used", 8),
                                                   ("Tritium in the tank (t)", "tank", 8), ("Tritium in the market (t)", "market", 8)), 1):
            tk.Label(form, text=label, fg=P.MUTED, bg=P.CARD, anchor="w", font=style.font(P.FONT_BOLD)).grid(row=row, column=0, sticky="w", pady=2)
            entry = tk.Entry(form, textvariable=self._vars[key], width=width)
            entry.grid(row=row, column=1, sticky="ew" if key in ("start", "end") else "w", padx=P.PAD_SM, pady=2)
            if key in ("start", "end"):
                system_autocomplete.attach(entry, self._vars[key])
                entry.bind("<Return>", lambda _e: self._plot())
            self._entries[key] = entry
        self._work_out = tk.BooleanVar(master=self._shell.window, value=True)
        tk.Checkbutton(form, text="Work out the tritium I need to start with", variable=self._work_out, command=self._fuel_mode, fg=P.TEXT, bg=P.CARD, selectcolor=P.PANE,
                       activebackground=P.CARD, activeforeground=P.TEXT, anchor="w").grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self._activity = tk.Label(body, text="", fg=P.ACCENT, bg=P.BG, anchor="w", font=style.font(P.FONT_BOLD))
        self._activity.pack(fill="x", pady=(P.PAD, 2))
        self._summary = NoteLabel(body, fg=P.TEXT, bg=P.BG, font=P.FONT_BOLD, padx=0)
        self._summary.pack(fill="x", pady=(P.PAD_SM, P.PAD_SM))

        actions = tk.Frame(body, bg=P.BG)
        actions.pack(fill="x", pady=(0, P.PAD_SM))
        FlatButton(actions, "Copy next system", self._copy_next).pack(side="left")
        FlatButton(actions, "Copy all remaining", self._copy_all).pack(side="left", padx=(6, 0))
        FlatButton(actions, "Mark next as reached", self._mark_reached).pack(side="left", padx=(6, 0))
        FlatButton(actions, "Clear route", self._clear_route).pack(side="left", padx=(6, 0))

        self._table = TableBox(body, "The route (double-click a system to copy it)", route_table(None), on_activate=self._copy_row)
        self._table.pack(fill="both", expand=True)
        self._table.table.tag_configure("map", foreground=P.ACCENT)
        self._shell.set_status("Type where the carrier is going and press Generate route. Only the systems and the carrier's size, space used and tritium go to Spansh.")
        self._planner.add_listener(self._on_planner_change)
        self._planner.recover_once()
        self._fill_from_journal(first=True)
        self._fuel_mode()
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

    def _say(self, text: str) -> None:
        self._shell.set_status(text)

    def _on_planner_change(self) -> None:
        """The journal told the owner something (the carrier's place, tritium, or a system reached): redraw."""
        if self.alive:
            self.refresh()

    def _kind_from_label(self) -> str:
        return next((kind for kind, label in CR.KIND_LABELS.items() if label == self._kind_var.get()), CR.FLEET)

    def _kind_changed(self) -> None:
        self._kind = self._kind_from_label()
        self._fill_from_journal(first=True)
        self.refresh()

    def _fill_from_journal(self, first: bool = False) -> None:
        """Put the carrier's place, space used and tritium into the boxes (from the journal), unless the commander has typed something there already."""
        info = self._planner.info(self._kind)
        known = self._planner.kinds()
        if known and self._kind not in known:
            self._kind = known[0]
            self._kind_var.set(CR.KIND_LABELS[self._kind])
            info = self._planner.info(self._kind)
        for key, value in (("start", info.system), ("used", "" if info.used_capacity is None else str(info.used_capacity)),
                           ("tank", "" if info.tritium is None else str(info.tritium))):
            if value and (first or not self._vars[key].get().strip()):
                self._vars[key].set(value)

    def _fuel_mode(self) -> None:
        state = "disabled" if self._work_out.get() else "normal"
        for key in ("tank", "market"):
            self._entries[key].configure(state=state)

    def refresh(self) -> None:
        """Redraw the carrier block, the table and its summary."""
        if not self.alive:
            return
        info = self._planner.info(self._kind)
        self._carrier_block.set(info.describe())
        self._fill_from_journal()
        route = self._planner.route
        self._table.fill(route_table(route))
        self._summary.configure(text=route.summary() if route is not None else "")
        self._shell.set_subtitle(f"Carrier in {info.system}" if info.system else "")

    # --- plotting -----------------------------------------------------------------------------------------------------

    def _plot(self) -> None:
        if self._busy:
            return
        start, end = " ".join(self._vars["start"].get().split()), " ".join(self._vars["end"].get().split())
        if not start or not end:
            self._say("Give both where the carrier is and the system it is going to.")
            return
        info = self._planner.info(self._kind)
        used = _whole(self._vars["used"].get(), info.used_capacity or 0)
        start_id = info.address if info.address is not None and start.casefold() == info.system.casefold() else None
        work_out = bool(self._work_out.get())
        tank, market = _whole(self._vars["tank"].get()), _whole(self._vars["market"].get())
        self._busy = True
        self._started, self._note = time.monotonic(), ""
        self._cancel = threading.Event()
        self._plot_button.configure(text="Plotting...")
        self._plot_button.set_enabled(False)
        self._say("Sent to Spansh. A route can take a minute. You can cancel at any time.")
        self._tick()
        threading.Thread(target=self._worker, args=(self._kind, start, end, used, work_out, tank, market, start_id, self._cancel), daemon=True).start()
        self._shell.window.after(POLL_MS, self._poll)

    def _tick(self) -> None:
        if not self.alive:
            return
        if not self._busy:
            return
        seconds = int(time.monotonic() - self._started)
        self._activity.configure(text=f"Plotting  {seconds // 60}:{seconds % 60:02d} waited" + (f"  ·  {self._note}" if self._note else ""), fg=P.ACCENT)
        self._shell.window.after(TICK_MS, self._tick)

    def _finished(self, message: str = "") -> None:
        self._busy = False
        self._plot_button.configure(text="Generate route")
        self._plot_button.set_enabled(True)
        self._activity.configure(text=message, fg=P.DANGER if message else P.ACCENT)

    def _worker(self, kind: str, start: str, end: str, used: int, work_out: bool, tank: int, market: int, start_id: Optional[int], cancel: threading.Event) -> None:
        """Runs off the main thread: it must not touch any Tk widget. Progress goes through the queue."""
        def tell(text: str) -> None:
            if text:
                self._results.put((None, text))
        try:
            route = carrier_route_spansh.plot(kind, start, [end], used, work_out, tank, market, start_id, cancel, tell)
        except RouteSearchError as err:
            self._results.put((end, str(err)))
        except Exception:
            logger.exception("Spansh fleet carrier router failed")
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
                self._note = str(payload).rstrip(".")
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
            self._say("Spansh found no route between those systems for a carrier. Check both systems, or try a nearer destination.")
            return
        self._planner.set_route(payload)
        self.refresh()
        self._say(f"Route ready: {len(payload.legs)} jumps. " + (payload.needs + " " if payload.needs else "")
                  + "Copy the next system, schedule the jump in Carrier Management, and the route moves on when the carrier arrives.")

    def _cancel_or_close(self) -> None:
        if self._busy and self._cancel is not None:
            self._cancel.set()
            self._note = "Cancelling"
            self._say("Cancelling...")
        else:
            self.close()

    # --- using the route ----------------------------------------------------------------------------------------------

    def _clip(self, text: str, said: str) -> None:
        try:
            self._shell.window.clipboard_clear()
            self._shell.window.clipboard_append(text)
        except tk.TclError:
            self._say("Could not use the clipboard.")
            return
        self._say(said)

    def _copy_next(self) -> None:
        route = self._planner.route
        if route is None or route.next_leg is None:
            self._say("No route to copy from: plot one first." if route is None else "The carrier has arrived: nothing left to copy.")
            return
        self._clip(route.next_leg.system, f"Copied {route.next_leg.system}. Paste it into Carrier Management's jump search.")

    def _copy_all(self) -> None:
        route = self._planner.route
        text = route.copy_all() if route is not None else ""
        if not text:
            self._say("Nothing left to copy.")
            return
        self._clip(text, f"Copied {text.count(chr(10)) + 1} systems, one per line.")

    def _copy_row(self, iid: str) -> None:
        route = self._planner.route
        if route is None or not iid.isdigit() or not 1 <= int(iid) <= len(route.legs):
            return
        leg = route.legs[int(iid) - 1]
        self._clip(leg.system, f"Copied {leg.system}.")

    def _mark_reached(self) -> None:
        if self._planner.mark_reached():
            self.refresh()
            self._say("Moved the route on by one.")
        else:
            self._say("There is no jump left to mark.")

    def _clear_route(self) -> None:
        self._say("Route cleared." if self._planner.clear_route() else "There is no route to clear.")
        self.refresh()
