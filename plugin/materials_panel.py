"""Engineering: the commander's Raw, Manufactured and Encoded materials and where they stand with the engineers, in Operations mode's panel.

A collapsible "Engineering" row shows how many pieces of each type are held, the last change the journal reported, which materials are at the
most the game lets you hold, how many engineers are unlocked and the wishlist, with a row of buttons: Materials opens the window
(`materials_window.py`) to search, filter and read every count with its grade and limit, Blueprints opens the Engineering window
(`blueprints_window.py`) and Engineers opens it on its Engineers tab. The counts are kept per commander (`materials.py`) and never leave the computer. They come from the journal's `Materials`
list at login and every event that changes a count; if WFMT starts in the middle of a session it takes EDMC's own totals once."""
from __future__ import annotations

import logging
import os
import queue
import threading
import tkinter as tk
from typing import Any, Dict, Mapping, Optional, Tuple

from config import appname

from . import blueprint_needs, blueprint_wishlist, blueprints_window, canonn_poi_panel, commander_data, mission_sources, mission_sources_window, engineer_requirements, engineers, inventory_panel, material_trader_window, materials, materials_window, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "fieldops"

_FULL_SHOWN = 3        # names listed on the "at the limit" line; the rest are counted
_NAME_SHOWN = 40       # characters of a material name shown in the panel
_HOLDING_EVENTS = ("ShipLocker", "Backpack", "BackpackChange", "Resupply", "TransferMicroResources", "BuyMicroResources", "SellMicroResources",
                   "UseConsumable", "CollectItems", "DropItems", "Embark", "Disembark", "LoadGame")
_ARRIVAL_EVENTS = ("FSDJump", "CarrierJump", "Location")
_PROGRESS_POLL_MS = 400    # how often the Tk thread looks for the journal read's result
_WRAP_PX = 200         # the summary wraps here: what it shows comes from the game, and must not widen EDMC's window

book = materials.MaterialBook()
wishlist = blueprint_wishlist.WishBook()
engineer_book = engineers.EngineerBook()


def holdings() -> blueprint_needs.Holdings:
    """What the wishlist is weighed against: ship materials from the journal, on-foot items from the Inventory's ship locker."""
    return blueprint_needs.Holdings(book.count_of, inventory_panel.micro_resource_count)


def wishlist_line(wishbook: blueprint_wishlist.WishBook) -> str:
    """`Wishlist: 3 blueprints, 2 can be made, 14 pieces short`; empty when nothing is on it."""
    if not wishbook.count():
        return ""
    shopping = blueprint_needs.shopping_list(wishbook.items(), holdings())
    n = len(shopping.entries)
    line = f"Wishlist: {n} blueprint{'s' if n != 1 else ''}, {shopping.ready_count} can be made"
    return line + (f", {shopping.short_pieces:,} pieces short" if shopping.short_pieces else "")


def engineers_line(engineer_book_: engineers.EngineerBook) -> str:
    """`Engineers: 7 of 38 unlocked · 2 invited · 4 known`; empty until the game has listed the commander's engineers."""
    if not engineer_book_.has_data:
        return ""
    standings = engineer_book_.all()
    unlocked = sum(1 for s in standings if s.unlocked)
    invited = sum(1 for s in standings if s.progress == engineers.INVITED)
    known = sum(1 for s in standings if s.progress == engineers.KNOWN)
    line = f"Engineers: {unlocked} of {len(engineers.INFO)} unlocked"
    if invited:
        line += f" · {invited} invited"
    if known:
        line += f" · {known} known"
    return line


def summary_lines(book_: materials.MaterialBook, engineer_book_: Optional[engineers.EngineerBook] = None) -> Tuple[str, str]:
    """(the lines under the title, and the note after the title when folded, which is always empty: the title says just Engineering). The engineers line comes last but one, before the wishlist."""
    engineer_book_ = engineer_book if engineer_book_ is None else engineer_book_
    people = engineers_line(engineer_book_)
    if not book_.ready:
        return "\n".join(["Log in to see your materials."] + ([people] if people else [])), ""
    held = book_.held()
    if not held:
        return "\n".join(["No materials yet. The counts fill in when you are in the game."] + ([people] if people else [])), ""
    totals = book_.totals()
    lines = ["Materials held: " + " · ".join(f"{kind} {totals.get(kind, 0):,}" for kind in materials.TYPES)]
    if totals.get(materials.OTHER):
        lines[0] += f" · Other {totals[materials.OTHER]:,}"
    last = book_.last
    if last is not None:
        name = _clip(last.name)
        lines.append(f"Last change: {'+' if last.delta > 0 else '-'}{abs(last.delta):,} {name} (now {last.total:,})")
    full = book_.full()
    if full:
        names = ", ".join(_clip(h.material.name) for h in full[:_FULL_SHOWN])
        more = f" and {len(full) - _FULL_SHOWN} more" if len(full) > _FULL_SHOWN else ""
        lines.append(f"At the limit: {names}{more}")
    if not book_.has_counts:
        lines.append("As of your last session.")
    if people:
        lines.append(people)
    wish = wishlist_line(wishlist)
    if wish:
        lines.append(wish)
    return "\n".join(lines), ""      # the folded title says just Engineering; the figures are in the section


def _clip(text: str) -> str:
    return text if len(text) <= _NAME_SHOWN else text[:_NAME_SHOWN - 1].rstrip() + "…"


class MaterialsController:
    def __init__(self) -> None:
        self._system = ""
        self._summary_var: Optional[tk.StringVar] = None
        self._section: Optional[tk.Frame] = None
        self._parent: Optional[tk.Frame] = None
        self._progress_tried: set = set()      # commanders whose ranks and figures were read from the journals this session
        self._progress_found: "queue.Queue[Tuple[str, engineer_requirements.Progress]]" = queue.Queue()
        self._progress_waiting = 0
        book.add_listener(self._update_summary)
        wishlist.add_listener(self._update_summary)
        engineer_book.add_listener(self._update_summary)

    # --- what the game tells us -----------------------------------------------------------------------------------------

    def start(self, plugin_dir: str) -> None:
        book.load(plugin_dir)
        wishlist.load(plugin_dir)
        engineer_book.load(plugin_dir)

    def stop(self) -> None:
        book.flush()
        materials_window.close()
        blueprints_window.close()
        material_trader_window.close()

    def handle_event(self, entry: Mapping[str, Any], cmdr: str, system: Optional[str], station: Optional[str],
                     state: Dict[str, Any]) -> None:
        book.set_commander(cmdr)       # a new commander tells the book's listeners (this row, an open window) itself
        if entry.get("event") in _ARRIVAL_EVENTS and isinstance(entry.get("StarSystem"), str) and entry["StarSystem"].strip():
            self._system = " ".join(entry["StarSystem"].split())
        elif not self._system and system:
            self._system = system.strip()
        wishlist.set_commander(cmdr)
        engineer_book.set_commander(cmdr)
        engineer_book.apply_event(entry)
        if engineer_book.needs_journal_read():
            self._read_progress(cmdr)
        book.apply_event(entry, state)
        if wishlist.count() and entry.get("event") in _HOLDING_EVENTS:
            self._update_summary()              # the Inventory (which runs first) may have changed what the wishlist is weighed against
            blueprints_window.refresh()

    def _read_progress(self, cmdr: str) -> None:
        """Read the commander's ranks and lifetime figures from the journals once, off the Tk thread: EDMC does not replay the game's login events to
        a plugin started after them. Whatever the live events gave meanwhile is kept."""
        key = commander_data.key_for(cmdr)
        if key in self._progress_tried or self._parent is None:
            return
        self._progress_tried.add(key)
        self._progress_waiting += 1
        threading.Thread(target=self._progress_worker, args=(cmdr,), name="WFMT-engineer-progress", daemon=True).start()
        self._schedule_progress_poll()

    def _progress_worker(self, cmdr: str) -> None:
        try:
            found = engineer_requirements.read_from_journals(cmdr)
        except Exception:
            logger.exception("Could not read the ranks and statistics from the journals")
            found = engineer_requirements.Progress()
        self._progress_found.put((cmdr, found))

    def _schedule_progress_poll(self) -> None:
        try:
            if self._parent is not None:
                self._parent.after(_PROGRESS_POLL_MS, self._poll_progress)
        except tk.TclError:
            pass   # the panel has gone

    def _poll_progress(self) -> None:
        try:
            cmdr, found = self._progress_found.get_nowait()
        except queue.Empty:
            if self._progress_waiting:
                self._schedule_progress_poll()
            return
        self._progress_waiting -= 1
        engineer_book.adopt_progress(cmdr, found)
        if self._progress_waiting:
            self._schedule_progress_poll()

    # --- the panel row ---------------------------------------------------------------------------------------------------

    def summary(self) -> Tuple[str, str]:
        return summary_lines(book)

    def _update_summary(self) -> None:
        if self._summary_var is None:
            return
        try:
            text, suffix = self.summary()
            self._summary_var.set(text)
            if self._section is not None:
                self._section.set_title_suffix(suffix)   # type: ignore[attr-defined]
        except tk.TclError:
            pass   # the panel is being torn down

    def build_panel(self, parent: tk.Frame) -> None:
        self._parent = parent
        self._summary_var = tk.StringVar()
        body = panelkit.collapsible_section(parent, "Engineering", "wfmt_materials_collapsed")
        self._section = body
        # Wraps at the window's width but never below _WRAP_PX, so a long name wraps instead of being cut off and still can't widen
        # EDMC's window past the width it already has.
        panelkit.wrap_label(body, min_wrap=_WRAP_PX, textvariable=self._summary_var, anchor="w").grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        # One row of buttons. flow_buttons puts them on a second line only if the row would be wider than EDMC's window already is.
        row = tk.Frame(body)
        row.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(4, 0))
        buttons = []
        for text, command, tip in (
                ("Materials", self._open_window, "Materials - open the window to search and filter every material with its grade and limit"),
                ("Blueprints", self._open_blueprints, "Blueprints - open the Engineering window: browse blueprints, keep a wishlist and see what you still need"),
                ("Engineers", self._open_engineers, "Engineers - open the Engineering window on its Engineers tab: where you stand with each engineer and the path to unlock them")):
            button = tk.Button(row, text=text, command=command)
            panelkit.add_tooltip(button, tip)
            buttons.append(button)
        panelkit.flow_buttons(row, buttons)
        self._update_summary()

    def system(self) -> str:
        """The system the commander is in, or an empty string when it is not known yet."""
        return self._system

    def _open_window(self) -> None:
        if self._parent is not None:
            materials_window.show(self._parent, book, self)

    def _open_blueprints(self) -> None:
        if self._parent is not None:
            blueprints_window.show(self._parent, wishlist, holdings, engineer_book, tab=blueprints_window.BLUEPRINTS_TAB, tools=self._tools())

    def _open_engineers(self) -> None:
        if self._parent is not None:
            blueprints_window.show(self._parent, wishlist, holdings, engineer_book, tab=blueprints_window.ENGINEERS_TAB, tools=self._tools())

    def _tools(self) -> blueprints_window.Tools:
        """The finders the Engineering window can start for an ingredient: the Source commodities lookup, the Material trader and the nearest Thargoid site."""
        return blueprints_window.Tools(where_to_buy=self._where_to_buy, open_trader=self._open_trader, find_site=self._find_site)

    def _where_to_buy(self, items) -> None:
        """Open the Source commodities lookup for these `(commodity, tons)` pairs (nothing is looked up until Find sources is pressed there)."""
        if self._parent is None:
            return
        needs = [mission_sources.Need(commodity=name, tons=tons, missions=0, turn_in="") for name, tons in items]
        mission_sources_window.show_for(self._parent, lambda: needs, self.system, title="WFMT - Where to buy", subtitle="Where to get what an engineer asks for",
                                        empty_text="Nothing to look up.")

    def _open_trader(self) -> None:
        if self._parent is not None:
            material_trader_window.show(self._parent, book, self)

    def _find_site(self) -> str:
        """Start the Canonn lookup of the nearest Thargoid site; the line says where the answer will be."""
        controller = canonn_poi_panel.controller
        if not controller.position_known():
            return ("Could not look up a Thargoid site: WFMT does not know where you are yet. Log in to the game (EDMC must be running) "
                    "and jump to a system or load into one, then try again.")
        if not canonn_poi_panel.thargoid_enabled():
            return ("Could not look up a Thargoid site: Thargoid sites are switched off. Turn on Include Thargoid sites in Settings, "
                    "Exploration, POI Reference.")
        if controller.find_thargoid(self._thargoid_found):
            return "Looking up the nearest Thargoid site..."
        return "Could not look up a Thargoid site just now. Try again in a moment."

    def _thargoid_found(self, sentence: str, system: Optional[str]) -> None:
        """The nearest Thargoid site is known: say so in the Engineers window's status line, and copy its system for the galaxy map."""
        copied = bool(system and self._parent is not None and panelkit.copy_to_clipboard(self._parent, system))
        window = blueprints_window._window
        if window is not None and window.alive:
            window._shell.set_status(sentence + (" The system name is copied: paste it into the galaxy map." if copied else ""), ok=bool(system))

controller = MaterialsController()


def start(plugin_dir: str) -> None:
    controller.start(plugin_dir)


def stop() -> None:
    controller.stop()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)
