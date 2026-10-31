"""The Engineering window: every engineering blueprint to browse, and the commander's wishlist with a combined shopping list.

**Blueprints** tab: search and pick a module type; pick a blueprint to see who offers it, its effects and what ONE craft takes against what you
hold and where each ingredient is found; set a number of crafts and add it to the wishlist (or double-click a row to add one craft).
**Wishlist** tab: each entry with its crafts, whether it can be made now (worked out in list order, so an entry only sees what the ones above it
leave), how many pieces it is short and who can do it (an engineer you have unlocked, or a vendor that needs none), then one shopping list for the
whole wishlist: need, have, short and where to find each ingredient.
**Ship planner** tab: paste a ship loadout (SLEF from EDSY or Coriolis, or a journal `Loadout` line) and put what its engineering takes on the wishlist
(`ship_plan_tab.py`, logic in `ship_plan.py`).
**Upgrade planner** tab: take an Odyssey suit or weapon from one class to another and fit up to four modifications, see the materials and credits, and put
them on the wishlist (`odyssey_plan_tab.py`, logic in `odyssey_upgrade_plan.py`).
**Engineers** tab: where you stand with each engineer (from the journal's `EngineerProgress`), the module types they work on and what unlocking them takes, with
buttons to list their blueprints or put their unlock on the wishlist.

Built on the shared window kit (plugin/uikit); the lists are `blueprints.py` and `blueprint_wishlist.WishBook`, the arithmetic is
`blueprint_needs.py`, and the counts come in as a `Holdings` from the panel (`materials_panel.py`). Module-level show/refresh/close and saved
geometry follow notes_window.py."""
from __future__ import annotations

import logging
import os
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple

from config import appname, config

from . import blueprint_needs as needs_mod
from . import blueprint_wishlist as wishlist_mod
from . import blueprints, engineer_guides_data, engineer_path, engineers, ingredient_sources, issue_report, stored_modules
from .powerplay_clipboard import inara_system_url
from .odyssey_plan_tab import UpgradePlanTab
from .ship_plan_tab import ShipPlanTab
from .uikit import palette as P
from .uikit import style
from .uikit.richtext import RichText
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable
from .uikit.widgets import Combobox, FlatButton, NoteLabel, ScrollFrame, Tabs, clip

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_blueprints_window_geometry"
CONFIG_ENGINEER_REGION = "wfmt_engineers_region"
BOTH = "Both"
REGION_CHOICES = (BOTH, *engineers.REGIONS)
DEFAULT_SIZE = (1080, 760)
MIN_SIZE = (860, 560)
ALL = "All types"
SHOWN = 150            # blueprints listed at once; a note says when there are more
SEARCH_DELAY_MS = 250  # typing in the search box refills the table once it pauses
CONFIRM_MS = 5000      # how long a first press of Remove or Clear waits for the second
FOUND_CHARS = 80

KIND_LABELS = {blueprints.SHIP: "Ship material", blueprints.ODYSSEY: "On foot", blueprints.COMMODITY: "Commodity"}

_window: Optional["BlueprintsWindow"] = None

_BLUEPRINT_COLUMNS = (
    Column("type", "Module", 170, max_chars=32),
    Column("name", "Blueprint", 230, stretch=True, max_chars=48),
    Column("grade", "Grade", 60, anchor="e"),
    Column("engineers", "Offered by", 260, max_chars=60),
)
_INGREDIENT_COLUMNS = (
    Column("ingredient", "Ingredient", 230, stretch=True, max_chars=44),
    Column("kind", "Kind", 110),
    Column("need", "Need", 60, anchor="e"),
    Column("have", "Have", 60, anchor="e"),
    Column("found", "Where it is found", 360, stretch=True, max_chars=FOUND_CHARS),
)
_WISH_COLUMNS = (
    Column("blueprint", "Blueprint", 330, stretch=True, max_chars=64),
    Column("crafts", "Crafts", 60, anchor="e"),
    Column("ready", "Can be made now", 170, max_chars=44),
    Column("short", "Short", 60, anchor="e"),
    Column("who", "Who can do it", 250, max_chars=60),
)
_ENGINEER_COLUMNS = (
    Column("engineer", "Engineer", 170, max_chars=34),
    Column("standing", "You are", 130, max_chars=30),
    Column("works", "Works on", 260, max_chars=60),
    Column("where", "Where", 250, max_chars=60),
    Column("unlock", "Next step", 340, stretch=True, max_chars=170),
)
_SHOPPING_COLUMNS = (
    Column("ingredient", "Ingredient", 230, stretch=True, max_chars=44),
    Column("kind", "Kind", 110),
    Column("need", "Need", 60, anchor="e"),
    Column("have", "Have", 60, anchor="e"),
    Column("short", "Short", 60, anchor="e"),
    Column("found", "Where it is found", 320, stretch=True, max_chars=FOUND_CHARS),
)

Counts = Callable[[], needs_mod.Holdings]

_HELP = (
    ("Counts", "Ship materials come from your journal. On-foot items come from your ship locker only, not the backpack or a carrier's locker. Trade goods are not counted."),
    ("Engineers", "Standings come from the journal's engineer list, sent at login and when one changes."),
    ("Places and steps", "From a community-maintained table. What each engineer offers is from the blueprint table (March 2024). Both may lag the game."),
)


BLUEPRINTS_TAB, ENGINEERS_TAB = "Blueprints", "Engineers"


@dataclass(frozen=True)
class Tools:
    """The finders the Engineering window can start for an ingredient, given by whoever opens it (materials_panel), so this window does not import them: the Source
    commodities lookup for something bought at a market (`where_to_buy` is given `(name, tons)` pairs), the Material trader, and the nearest Thargoid site."""
    where_to_buy: Optional[Callable[[Sequence[Tuple[str, int]]], None]] = None
    open_trader: Optional[Callable[[], None]] = None
    find_site: Optional[Callable[[], str]] = None         # starts the lookup and returns a line for the status bar
RANK_TEXT = ("Crafting modules with them raises your standing. Some engineers also take other activities, such as selling exploration data or commodities "
             "at their base.")
RANK_UNCONFIRMED = "Community-reported and not yet checked for this engineer. The in-game Engineers panel shows what theirs asks for."
VERIFY_TEXT = ("WFMT cannot check this invitation requirement against your journal (it is a faction's standing, a kind of mission, a data sale or similar), "
               "so confirm it in the game. If you can tell us what the game shows for this engineer, press Report engineer data below.")


def show(parent: tk.Misc, wishbook: wishlist_mod.WishBook, holdings: Counts, engineer_book: engineers.EngineerBook,
         tab: Optional[str] = None, tools: Optional[Tools] = None) -> None:
    """Open the Engineering window, or raise it if it is already open. `tab` (a tab's title, such as "Engineers") opens it on that tab."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
    else:
        _window = BlueprintsWindow(parent, wishbook, holdings, engineer_book)
    if tools is not None:
        _window._tools = tools
    if tab:
        _window.select_tab(tab)


def refresh() -> None:
    if _window is not None and _window.alive:
        _window.refresh()


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def engineers_text(blueprint: blueprints.Blueprint, book: Optional[engineers.EngineerBook] = None) -> str:
    """Who offers a blueprint; with the commander's standings, each engineer is followed by where they stand with them."""
    if not blueprint.engineers:
        return "-"
    parts = []
    for name in blueprint.engineers:
        standing = book.standing(name) if book is not None and name not in blueprints.STAND_IN_NAMES else None
        parts.append(f"{name} ({standing.describe().lower()})" if standing is not None else name)
    return ", ".join(parts)


def works_on_text(name: str) -> str:
    """The module types an engineer works on, each with its top grade ("Frame Shift Drive 5, Thrusters 3"); a type with no grades (an on-foot
    engineer's suits and weapons) is named alone. "-" when the blueprint table has nothing for them."""
    kinds = blueprints.works_on(name, key=engineers.name_key)
    return ", ".join(f"{kind} {grade}" if grade else kind for kind, grade, _names in kinds) or "-"


def who_can(blueprint: blueprints.Blueprint, book: Optional[engineers.EngineerBook]) -> str:
    """Who can do a blueprint for the commander now: a vendor or the synthesis panel (nothing to unlock) and any engineer who is unlocked. When
    the journal has not told WFMT about the engineers yet, it says who offers it instead of guessing."""
    free = [e for e in blueprint.engineers if e in blueprints.STAND_IN_NAMES]
    if book is None or not book.has_data:
        return clip("Offered by " + ", ".join(blueprint.engineers), 48) if blueprint.engineers else "-"
    unlocked = [e for e in blueprints.real_engineers(blueprint) if (s := book.standing(e)) is not None and s.unlocked]
    if free or unlocked:
        return clip(", ".join(free + unlocked), 60)
    return clip("No engineer unlocked yet", 60)


def effects_text(blueprint: blueprints.Blueprint) -> str:
    return ", ".join(f"{e.effect} {e.prop}".strip() for e in blueprint.effects) or "none listed"


def found_text(ingredient: blueprints.Ingredient) -> str:
    return clip("; ".join(ingredient.found) or "-", FOUND_CHARS)


def number(value: Optional[int]) -> str:
    return "-" if value is None else f"{value:,}"


def ingredient_rows(blueprint: blueprints.Blueprint, crafts: int, holdings: needs_mod.Holdings) -> List[tuple]:
    return [(n.ingredient.name, KIND_LABELS[n.ingredient.kind], f"{n.need:,}", number(n.have), found_text(n.ingredient))
            for n in needs_mod.needs_for(blueprint, crafts, holdings)]


def entry_ready_text(entry: needs_mod.EntryStatus) -> str:
    if entry.ready and entry.uncounted:
        return clip("Yes, not counting " + ", ".join(entry.uncounted), 44)
    return "Yes" if entry.ready else "No"


def entry_short(entry: needs_mod.EntryStatus) -> int:
    return sum(max(0, n.need - n.have) for n in entry.needs if n.have is not None)


def shopping_rows(shopping: needs_mod.Shopping) -> List[tuple]:
    return [(n.ingredient.name, KIND_LABELS[n.ingredient.kind], f"{n.need:,}", number(n.have), number(n.short), found_text(n.ingredient))
            for n in shopping.needs]


class BlueprintsWindow:
    def __init__(self, parent: tk.Misc, wishbook: wishlist_mod.WishBook, holdings: Counts, engineer_book: engineers.EngineerBook) -> None:
        self._wishbook = wishbook
        self._engineers = engineer_book
        self._holdings = holdings
        self._picked: Optional[str] = None         # the blueprint shown in the detail pane
        self._picked_wish: Optional[str] = None    # the wishlist entry selected
        self._confirming: Optional[str] = None     # "remove" or "clear" after a first press
        self._search_job: Optional[str] = None

        self._shell = WindowShell(
            parent, "Engineering", "", size=DEFAULT_SIZE, min_size=MIN_SIZE,
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("Engineering help", _HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Refresh counts", self.refresh, tip="Refresh counts - recount the materials you hold against the wishlist")

        self._tools = Tools()
        self._tab_titles: List[str] = [BLUEPRINTS_TAB, "Wishlist", "Ship planner", "Upgrade planner", ENGINEERS_TAB]
        self._tabs = Tabs(self._shell.body)
        self._tabs.pack(fill="both", expand=True)
        self._build_browse(self._tabs.add("Blueprints"))
        self._build_wishlist(self._tabs.add("Wishlist"))
        self._ship_plan = ShipPlanTab(self._tabs.add("Ship planner"), wishbook, self._shell.set_status, module_book=stored_modules.book)
        self._upgrade_plan = UpgradePlanTab(self._tabs.add("Upgrade planner"), wishbook, self._shell.set_status)
        self._build_engineers(self._tabs.add("Engineers"))
        self._tabs.select(0)

        wishbook.add_listener(self._on_changed)
        engineer_book.add_listener(self._on_changed)
        self._fill_blueprints()
        self.refresh()

    # --- the Blueprints tab --------------------------------------------------------------------------------------------

    def _build_browse(self, tab: tk.Frame) -> None:
        scroll = ScrollFrame(tab)     # the tab is taller than the window's smallest size, so it scrolls instead of squeezing its last controls
        scroll.pack(fill="both", expand=True)
        pad = tk.Frame(scroll.body, bg=P.PANE)
        pad.pack(fill="x", padx=P.PAD, pady=P.PAD)
        filters = tk.Frame(pad, bg=P.PANE)
        filters.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(filters, text="Search", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._query = tk.StringVar()
        tk.Entry(filters, textvariable=self._query, width=26).pack(side="left", padx=(P.PAD_SM, P.PAD))
        self._query.trace_add("write", lambda *_: self._search_later())
        tk.Label(filters, text="Module", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._type = tk.StringVar(value=ALL)
        box = Combobox(filters, textvariable=self._type, values=[ALL, *blueprints.types()], state="readonly", width=26)
        box.pack(side="left", padx=(P.PAD_SM, P.PAD))
        box.bind("<<ComboboxSelected>>", lambda _e: self._fill_blueprints())
        self._count_label = tk.Label(filters, text="", fg=P.MUTED, bg=P.PANE)
        self._count_label.pack(side="left")

        self._table = DataTable(pad, _BLUEPRINT_COLUMNS, on_select=self._pick, on_activate=self._add_one,
                                empty_text="No blueprint matches.", visible_rows=9)
        self._table.pack(fill="x", pady=(0, P.PAD_SM))

        self._title = tk.Label(pad, text="Pick a blueprint above.", fg=P.TEXT, bg=P.PANE, anchor="w", font=style.font(P.FONT_BOLD))
        self._title.pack(fill="x")
        self._facts = NoteLabel(pad, padx=0)
        self._facts.pack(fill="x", pady=(0, P.PAD_SM))
        self._ingredients = DataTable(pad, _INGREDIENT_COLUMNS, sortable=False, visible_rows=6,
                                      empty_text="The ingredients of one craft are listed here.")
        self._ingredients.pack(fill="x", pady=(0, P.PAD_SM))

        adding = tk.Frame(pad, bg=P.PANE)
        adding.pack(fill="x")
        tk.Label(adding, text="Crafts", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._crafts = tk.StringVar(value="1")
        entry = tk.Entry(adding, textvariable=self._crafts, width=5)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD))
        entry.bind("<Return>", lambda _e: self._add())
        self._crafts.trace_add("write", lambda *_: self._fill_detail())
        self._add_button = FlatButton(adding, "Add to wishlist", self._add, kind="accent",
                                     tip="Add to wishlist - add the selected blueprint, for the number of crafts typed, to your wishlist")
        self._add_button.pack(side="left")
        self._add_button.set_enabled(False)

    def _search_later(self) -> None:
        if self._search_job is not None:
            try:
                self._shell.window.after_cancel(self._search_job)
            except tk.TclError:
                pass
        self._search_job = self._shell.window.after(SEARCH_DELAY_MS, self._fill_blueprints)

    def _fill_blueprints(self) -> None:
        self._search_job = None
        if not self.alive:
            return
        kind = None if self._type.get() == ALL else self._type.get()
        found = blueprints.search(self._query.get(), kind, limit=SHOWN + 1)
        shown = found[:SHOWN]
        self._table.clear()
        for b in shown:
            self._table.insert(b.id, (b.type, b.name, b.grade or "-", clip(engineers_text(b), 60)))   # statuses are in the detail below
        if self._picked and any(b.id == self._picked for b in shown):
            self._table.select(self._picked)
        self._count_label.configure(text=f"{len(shown)} shown" + (f", more match: narrow the search" if len(found) > SHOWN else ""))

    def _pick(self, blueprint_id: str) -> None:
        self._picked = blueprint_id
        self._fill_detail()

    def _crafts_value(self) -> int:
        try:
            return max(1, min(wishlist_mod.MAX_CRAFTS, int(self._crafts.get().strip())))
        except ValueError:
            return 1

    def _fill_detail(self) -> None:
        if not self.alive:
            return
        blueprint = blueprints.get(self._picked) if self._picked else None
        self._ingredients.clear()
        self._add_button.set_enabled(blueprint is not None)
        if blueprint is None:
            self._title.configure(text="Pick a blueprint above.")
            self._facts.configure(text="")
            return
        self._title.configure(text=f"{blueprint.type}: {blueprint.title}")
        self._facts.configure(text=clip(f"Offered by: {engineers_text(blueprint, self._engineers)}.   Effects: {effects_text(blueprint)}.", 400))
        for row in ingredient_rows(blueprint, self._crafts_value(), self._holdings()):
            self._ingredients.append(row)

    def _add(self) -> None:
        if self._picked is None:
            return
        self._add_blueprint(self._picked, self._crafts_value())

    def _add_one(self, blueprint_id: str) -> None:
        self._add_blueprint(blueprint_id, 1)

    def _add_blueprint(self, blueprint_id: str, crafts: int) -> None:
        try:
            item = self._wishbook.add(blueprint_id, crafts)
        except wishlist_mod.WishError as err:
            self._shell.set_status(str(err))
            return
        blueprint = item.blueprint
        self._shell.set_status(f"On the wishlist: {blueprint.title if blueprint else blueprint_id} x {item.crafts}.")

    # --- the Wishlist tab ----------------------------------------------------------------------------------------------

    def _build_wishlist(self, tab: tk.Frame) -> None:
        scroll = ScrollFrame(tab)
        scroll.pack(fill="both", expand=True)
        pad = tk.Frame(scroll.body, bg=P.PANE)
        pad.pack(fill="x", padx=P.PAD, pady=P.PAD)
        self._wish_table = DataTable(pad, _WISH_COLUMNS, on_select=self._pick_wish, sortable=False, visible_rows=8,
                                     empty_text="The wishlist is empty. Add blueprints on the Blueprints tab.")
        self._wish_table.pack(fill="x", pady=(0, P.PAD_SM))

        controls = tk.Frame(pad, bg=P.PANE)
        controls.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(controls, text="Crafts", fg=P.MUTED, bg=P.PANE).pack(side="left")
        self._wish_crafts = tk.StringVar(value="1")
        entry = tk.Entry(controls, textvariable=self._wish_crafts, width=5)
        entry.pack(side="left", padx=(P.PAD_SM, P.PAD))
        entry.bind("<Return>", lambda _e: self._set_crafts())
        FlatButton(controls, "Set crafts", self._set_crafts, tip="Set crafts - change how many times the selected wishlist entry is crafted").pack(side="left")
        FlatButton(controls, "Remove", self._remove, kind="danger",
                   tip="Remove - take the selected blueprint off the wishlist (press twice to confirm)").pack(side="left", padx=(P.PAD, 0))
        FlatButton(controls, "Clear list", self._clear, kind="danger",
                   tip="Clear list - empty the whole wishlist (press twice to confirm)").pack(side="left", padx=(6, 0))

        self._shopping_title = tk.Label(pad, text="Shopping list", fg=P.TEXT, bg=P.PANE, anchor="w", font=style.font(P.FONT_BOLD))
        self._shopping_title.pack(fill="x")
        self._shopping_table = DataTable(pad, _SHOPPING_COLUMNS, visible_rows=10, empty_text="Nothing to buy: the wishlist is empty.")
        self._shopping_table.pack(fill="x")

    def _pick_wish(self, blueprint_id: str) -> None:
        self._picked_wish = blueprint_id
        self._confirming = None
        item = self._wishbook.get(blueprint_id)
        if item is not None:
            self._wish_crafts.set(str(item.crafts))

    def _set_crafts(self) -> None:
        if self._picked_wish is None:
            self._shell.set_status("Select a wishlist entry first.")
            return
        try:
            crafts = int(self._wish_crafts.get().strip())
        except ValueError:
            self._shell.set_status(f"The number of crafts must be a whole number from 1 to {wishlist_mod.MAX_CRAFTS}.")
            return
        try:
            self._wishbook.set_crafts(self._picked_wish, crafts)
        except wishlist_mod.WishError as err:
            self._shell.set_status(str(err))
            return
        self._shell.set_status("Crafts changed.")

    def _confirm(self, what: str, message: str) -> bool:
        """A first press asks and a second press (within a few seconds) goes ahead."""
        if self._confirming != what:
            self._confirming = what
            self._shell.set_status(message)
            self._shell.window.after(CONFIRM_MS, self._stop_confirming)
            return False
        self._confirming = None
        return True

    def _stop_confirming(self) -> None:
        self._confirming = None

    def _remove(self) -> None:
        if self._picked_wish is None:
            self._shell.set_status("Select a wishlist entry first.")
            return
        if not self._confirm("remove", "Press Remove again to take this blueprint off the wishlist."):
            return
        gone, self._picked_wish = self._picked_wish, None
        if self._wishbook.remove(gone):
            self._shell.set_status("Removed.")

    def _clear(self) -> None:
        if not self._wishbook.count():
            return
        if not self._confirm("clear", "Press Clear list again to empty the whole wishlist."):
            return
        self._picked_wish = None
        self._shell.set_status(f"Cleared {self._wishbook.clear()} blueprint(s).")

    def _fill_wishlist(self) -> None:
        shopping = needs_mod.shopping_list(self._wishbook.items(), self._holdings())
        keep = self._picked_wish
        self._wish_table.clear()
        for entry in shopping.entries:
            self._wish_table.insert(entry.item.blueprint_id, (clip(f"{entry.blueprint.type}: {entry.blueprint.title}", 64), entry.item.crafts,
                                                              entry_ready_text(entry), f"{entry_short(entry):,}",
                                                              who_can(entry.blueprint, self._engineers)))
        if keep and self._wishbook.get(keep) is not None:
            self._wish_table.select(keep)
        else:
            self._picked_wish = None
        self._shopping_table.set_rows(shopping_rows(shopping))
        if not shopping.entries:
            self._shopping_title.configure(text="Shopping list")
        else:
            self._shopping_title.configure(
                text=f"Shopping list: {shopping.ready_count} of {len(shopping.entries)} can be made now, {shopping.short_pieces:,} pieces short")

    # --- the Engineers tab ---------------------------------------------------------------------------------------------

    def _build_engineers(self, tab: tk.Frame) -> None:
        scroll = ScrollFrame(tab)
        scroll.pack(fill="both", expand=True)
        pad = tk.Frame(scroll.body, bg=P.PANE)
        pad.pack(fill="x", padx=P.PAD, pady=P.PAD)
        region_row = tk.Frame(pad, bg=P.PANE)
        region_row.pack(fill="x", pady=(0, P.PAD_SM))
        tk.Label(region_row, text="Show", fg=P.MUTED, bg=P.PANE).pack(side="left")
        saved = config.get_str(CONFIG_ENGINEER_REGION) or BOTH
        self._region = tk.StringVar(value=saved if saved in REGION_CHOICES else BOTH)
        region_box = Combobox(region_row, textvariable=self._region, values=list(REGION_CHOICES), state="readonly", width=10)
        region_box.pack(side="left", padx=(P.PAD_SM, P.PAD))
        region_box.bind("<<ComboboxSelected>>", lambda _e: self._region_changed())
        self._region_label = tk.Label(region_row, text="", fg=P.MUTED, bg=P.PANE)
        self._region_label.pack(side="left")
        self._engineer_table = DataTable(pad, _ENGINEER_COLUMNS, on_select=self._pick_engineer, visible_rows=14,
                                         empty_text="No engineers yet. They appear when the game lists them (at login).")
        self._engineer_table.tag_configure("unlocked", foreground=P.ENGINEER_UNLOCKED)
        self._engineer_table.tag_configure("progress", foreground=P.ENGINEER_PROGRESS)
        self._engineer_table.tag_configure("unavailable", foreground=P.ENGINEER_UNAVAILABLE)
        self._engineer_table.pack(fill="x", pady=(0, P.PAD_SM))
        controls = tk.Frame(pad, bg=P.PANE)
        controls.pack(fill="x")
        FlatButton(controls, "Show their blueprints", self._show_engineer_blueprints,
                   tip="Show their blueprints - list the blueprints the selected engineer offers").pack(side="left")
        FlatButton(controls, "Put their unlock on the wishlist", self._add_unlock,
                   tip="Put their unlock on the wishlist - add the selected engineer's unlock items to your wishlist").pack(side="left", padx=(P.PAD, 0))
        FlatButton(controls, "Copy details", self._copy_engineer,
                   tip="Copy details - copy the selected engineer's details as plain text (you can also select part of them and press Ctrl+C, or right-click)").pack(side="left", padx=(P.PAD, 0))
        FlatButton(controls, "Report engineer data", self._report_engineer,
                   tip="Report engineer data - open a prefilled GitHub form to tell us what the game shows for the selected engineer (nothing is sent until you submit it there)").pack(side="left", padx=(P.PAD, 0))
        self._engineer_note = RichText(pad)
        self._engineer_note.pack(fill="x", pady=(P.PAD_SM, 0))
        self._picked_engineer: Optional[str] = None

    def _engineer_rows(self) -> List[tuple]:
        """(name, row values) for every engineer the tables or the journal know, unlocked ones first, then A to Z."""
        names: dict = {}
        for name in blueprints.engineer_names():
            names[engineers.name_key(name)] = name
        for key, info in engineers.INFO.items():
            names.setdefault(key, info.name)          # everyone in the location table is listed, even before the game names them
        for standing in self._engineers.all():
            names.setdefault(engineers.name_key(standing.name), standing.name)
        known = self._engineers.has_data
        rows = []
        for key, name in names.items():
            standing = self._engineers.standing(name)
            info = engineers.info(name)
            unlock = blueprints.unlock_for(name, key=engineers.name_key)
            items = "; ".join(self._unlock_part(n) for n in needs_mod.needs_for(unlock, 1, self._holdings())) if unlock is not None else ""
            if standing is not None and standing.unlocked:
                text = "-"
            elif info is not None:
                text = self._next_step_text(name, items)
            elif unlock is not None:
                text = clip(items, 170)
            else:
                text = "not in the table"
            rows.append((standing is not None and standing.unlocked, name, (
                name, standing.describe() if standing is not None else ("not known yet" if known else "?"),
                works_on_text(name), info.place() if info is not None else "-", text)))
        rows.sort(key=lambda r: (not r[0], r[1].casefold()))
        return [(name, values) for _unlocked, name, values in rows]

    def _engineer_tag(self, name: str) -> Optional[str]:
        """The row color: unlocked (green), known or invited (yellow, in progress), or not available yet (red: the game has not listed the commander as
        knowing them, or has barred them). No color before the game has listed any engineers, when nothing is known."""
        if not self._engineers.has_data:
            return None
        standing = self._engineers.standing(name)
        if standing is None or standing.progress == engineers.BARRED:
            return "unavailable"
        return "unlocked" if standing.unlocked else "progress"

    def _next_step_text(self, name: str, items: str) -> str:
        """The next thing to do towards unlocking one engineer: a step on their own path, or the engineer to deal with first and their step.
        The unlock items are added only when the step is the engineer's own, since they belong to that engineer."""
        path = engineer_path.build(name, self._engineers)
        action = engineer_path.next_action(path) if path is not None else None
        if action is None:
            return clip(items, 170) if items else "-"
        owner, step = action
        own = engineers.name_key(owner.name) == engineers.name_key(name)
        text = (step.text if own else f"First {owner.name}: {step.text}") + (f" ({step.note})" if step.note else "")
        if own and items:
            text += f" Items: {items}"
        return clip(text, 170)

    def _in_region(self, name: str) -> bool:
        """Does the Show choice include this engineer? "Both" includes everyone, including a name the location table lacks; Bubble and
        Colonia include only the engineers it places there."""
        choice = self._region.get()
        if choice == BOTH:
            return True
        info = engineers.info(name)
        return info is not None and info.region() == choice

    def _region_changed(self) -> None:
        choice = self._region.get()
        config.set(CONFIG_ENGINEER_REGION, choice)
        if self._picked_engineer and not self._in_region(self._picked_engineer):
            self._picked_engineer = None             # the engineer picked is no longer listed
        self._fill_engineers()

    @staticmethod
    def _unlock_part(need: needs_mod.Need) -> str:
        have = "" if need.have is None else f" (have {need.have:,})"
        return f"{need.need:,} x {need.ingredient.name}{have if need.have is not None else ' (not counted)'}"

    def _fill_engineers(self) -> None:
        keep = self._picked_engineer
        self._engineer_table.clear()
        rows = self._engineer_rows()
        shown = [(name, values) for name, values in rows if self._in_region(name)]
        for name, values in shown:
            self._engineer_table.insert(name, values, tag=self._engineer_tag(name))
        self._region_label.configure(text=f"{len(shown)} of {len(rows)} engineers")
        if keep and self._engineer_table.exists(keep):
            self._engineer_table.select(keep)
        if self._picked_engineer:
            self._pick_engineer(self._picked_engineer)           # keep the picked engineer's details
        elif self._engineers.has_data:
            self._engineer_note.message("Select an engineer to see where they are, how to unlock them and what to do next.")
        else:
            self._engineer_note.message("The game has not listed your engineers yet. Log in to the game and they appear here.")

    def _pick_engineer(self, name: str) -> None:
        self._picked_engineer = name
        self._render_engineer(name)

    def _render_engineer(self, name: str) -> None:
        """The details of one engineer in the pane under the table: the name with where the commander stands, where they are, the path to unlock them,
        how to raise standing with them and any notes, each under a heading."""
        note = self._engineer_note
        note.clear()
        info = engineers.info(name)
        standing = self._engineers.standing(name)
        status, status_tag = "", ""
        if self._engineers.has_data:
            if standing is None or standing.progress == engineers.BARRED:
                status, status_tag = "Not available yet", "bad"
            elif standing.unlocked:
                status, status_tag = standing.describe(), "good"
            else:
                status, status_tag = standing.describe(), "progress"
        if info is None:
            note.title(name, status, status_tag)
            note.paragraph("This engineer is not in the location table. What they offer is in the blueprint table.", "muted")
            note.finish()
            return
        note.title(info.name, status, status_tag)
        region = info.region()
        inara = inara_system_url(info.system)
        note.subtitle(f"{info.base}, ", (info.system, inara), (f" {info.body}" if info.body else "") + (f"  \u00b7  {region}" if region else ""))

        note.heading("Location")
        note.row("Base", info.base)
        note.row("System", info.system, url=inara)
        if info.body:
            note.row("Body", f"{info.system} {info.body}")
        if region:
            note.row("Region", region + (" (the human bubble)" if region == engineers.BUBBLE else " (around Colonia, about 22,000 ly from Sol)"))
        note.row("Getting there", ("On foot (an Odyssey engineer)" if info.on_foot else "By ship") + (f"; the {info.system} permit is needed" if info.permit else ""))

        kinds = blueprints.works_on(name, key=engineers.name_key)
        if kinds:
            note.heading("Works on")
            for kind, grade, names in kinds:
                if grade:
                    value = f"up to grade {grade}" + (f"; experimental effects: {', '.join(names)}" if names else "")
                else:
                    value = ", ".join(names)
                note.row(kind, value)

        path = engineer_path.build(name, self._engineers)
        if path is not None and (path.steps or path.first):
            note.heading("Path to unlock")
            if path.unlocked:
                note.paragraph("Unlocked. Nothing is left to do.", "good")
            else:
                stops = engineer_path.order(path)
                if len(stops) > 1:
                    note.paragraph(f"This takes {len(stops)} engineers, in this order: " + ", then ".join(p.name for p in stops) + ".", "muted")
                for stop in stops:
                    if len(stops) > 1:
                        note.stop(stop.name)
                    for number, step in enumerate(stop.steps, 1):
                        label, detail = engineer_path.describe_step(step)
                        note.step(number, label, detail, done=step.done, note=step.note if not step.done else "")

        unlocked = standing is not None and standing.unlocked
        self._render_items(note, name, info, unlocked)
        if info.standing:
            note.heading("Raising your rank with them")
            if engineers.name_key(name) in engineers.STANDING_CONFIRMED:
                note.paragraph(info.standing)
            else:
                note.paragraph(RANK_TEXT)
                note.paragraph(RANK_UNCONFIRMED, "warn")

        notes = []
        if info.on_foot:
            notes.append(("On foot.", "No ranks: every upgrade is offered once you have met them.", "label"))
        quirk = engineers.QUIRKS.get(engineers.name_key(name))
        if quirk:
            notes.append(("Known problem.", quirk, "label"))
        if not engineers.requirement_checkable(name) and not (standing is not None and standing.progress in (engineers.INVITED, engineers.UNLOCKED)):
            notes.append(("Verification needed.", VERIFY_TEXT, "warn"))
        if notes:
            note.heading("Notes")
            for label, text, tag in notes:
                note.bullet(text, label=label, tag=tag)
        note.finish()

    def _render_items(self, note: RichText, name: str, info: engineers.Info, unlocked: bool) -> None:
        """What the engineer asks to be handed over, each item with how many are needed and held, how it is got, and the finders that can help; then the written guide for
        the engineer if there is one."""
        unlock = blueprints.unlock_for(name, key=engineers.name_key)
        needs = needs_mod.needs_for(unlock, 1, self._holdings()) if unlock is not None else []
        if needs and not unlocked:
            note.heading("What you need to hand over" if not info.on_foot else "What you hand over (to learn of the next engineer)")
            for need in needs:
                kind = ingredient_sources.classify(need.ingredient)
                quantity = f"need {need.need:,}" + (f", have {need.have:,}" if need.have is not None else ", not counted (a commodity)")
                where = "; ".join(need.ingredient.found)
                how = ingredient_sources.label(kind) + (f". Found: {where}" if where else "")
                note.item(need.ingredient.name, quantity, how, self._actions_for(kind, need))
        guide = engineer_guides_data.guide_for(engineers.name_key(name))
        if guide is None:
            if needs and not unlocked:
                note.paragraph("There is no written guide for this engineer yet. If you know how to get these, press Report engineer data and tell us.", "muted")
            return
        note.heading("How to get it")
        note.paragraph(guide.summary)
        for number, text in enumerate(guide.steps, 1):
            note.numbered(number, text)
        if guide.where:
            note.row("Where", guide.where, url=inara_system_url(guide.system) if guide.system else "")
        for item, text in guide.items:
            note.row(item, text)
        for caution in guide.cautions:
            note.bullet(caution, label="Careful.", tag="warn")
        if guide.verified:
            note.paragraph("Confirmed in the game" + (f" on {guide.updated}" if guide.updated else "") + ".", "good")
        else:
            note.paragraph("Community-reported and not yet confirmed in the game. If you can confirm or correct it, press Report engineer data.", "warn")

    def _actions_for(self, kind: str, need: needs_mod.Need) -> List[Tuple[str, Callable[[], None]]]:
        """The finders that fit how an ingredient is got, as (text, what to run)."""
        tools = self._tools
        if kind == ingredient_sources.BUY and tools.where_to_buy is not None:
            return [("Find where to buy", lambda: tools.where_to_buy([(need.ingredient.name, need.need)]))]
        if kind == ingredient_sources.TRADE and tools.open_trader is not None:
            return [("Find a material trader", tools.open_trader)]
        if kind == ingredient_sources.SITE and tools.find_site is not None:
            return [("Look up the nearest Thargoid site", lambda: self._shell.set_status(tools.find_site() or "", ok=True))]
        return []

    def _copy_engineer(self) -> None:
        """Put the selected engineer's details on the clipboard as plain text."""
        if self._picked_engineer is None:
            self._shell.set_status("Select an engineer first.")
            return
        if self._engineer_note.copy_all():
            self._shell.set_status(f"Copied the details for {self._picked_engineer}.", ok=True)

    def _report_engineer(self) -> None:
        """Open the Game data form on GitHub for the selected engineer (the browser does the sending, if the player submits it)."""
        if self._picked_engineer is None:
            self._shell.set_status("Select an engineer first.")
            return
        standing = self._engineers.standing(self._picked_engineer)
        issue_report.open_feedback("Engineers", self._picked_engineer, "Standing in WFMT: " + (standing.describe() if standing is not None else "Unknown"))
        self._shell.set_status("Opened the Game data form in your browser. Read it, fill in what the game shows, and submit it with your own GitHub account.", ok=True)

    def select_tab(self, title: str) -> None:
        """Bring the tab with this title to the front (nothing happens for a title the window does not have)."""
        if title in self._tab_titles:
            self._tabs.select(self._tab_titles.index(title))

    def _show_engineer_blueprints(self) -> None:
        if self._picked_engineer is None:
            self._shell.set_status("Select an engineer first.")
            return
        self._type.set(ALL)
        self._query.set(self._picked_engineer)
        self._fill_blueprints()
        self._tabs.select(0)

    def _add_unlock(self) -> None:
        if self._picked_engineer is None:
            self._shell.set_status("Select an engineer first.")
            return
        unlock = blueprints.unlock_for(self._picked_engineer, key=engineers.name_key)
        if unlock is None:
            info = engineers.info(self._picked_engineer)
            self._shell.set_status("Their unlock is an action, not items, so there is nothing to put on the wishlist." if info is not None and info.unlock
                                   else "The table has no unlock for that engineer.")
            return
        self._add_blueprint(unlock.id, 1)

    # --- the window ----------------------------------------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    def close(self) -> None:
        self._wishbook.remove_listener(self._on_changed)
        self._engineers.remove_listener(self._on_changed)
        self._shell.close()

    def _on_changed(self) -> None:
        try:
            if self.alive:
                self.refresh()
        except tk.TclError:
            pass   # the window went away between the check and the redraw

    def refresh(self) -> None:
        if not self.alive:
            return
        who = self._wishbook.commander
        count = self._wishbook.count()
        self._shell.set_subtitle(f"{who}: {count} blueprint{'s' if count != 1 else ''} on the wishlist" if who
                                 else "Waiting for a commander (log in)")
        self._fill_detail()
        self._fill_wishlist()
        self._fill_engineers()
