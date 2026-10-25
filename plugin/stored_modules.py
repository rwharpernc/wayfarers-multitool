"""The modules a commander has in storage, and where, from the journal's Module Storage events. No Tk.

The game writes `StoredModules` when Module Storage is opened at a station: every stored module in every system, with the system, the station's `MarketID`, the
transfer cost and time, and the engineering and hot flags. Between visits `ModuleStore`, `MassModuleStore` and `ModuleRetrieve` say what was put into storage
or taken out at the station the commander was docked at, and this module applies them to the last snapshot. Nothing else reports storage, so the list is only as
fresh as the last visit to Module Storage plus those events. Before the first snapshot is seen the list stays empty: a store or retrieve event alone cannot say what
else is in storage.

A module fitted to a ship is part of that ship's loadout and is not listed; modules on ships kept in storage are known by ship type only and are not listed either.

Kept per commander in `stored_modules.json` beside the plugin (`commander_data.py`), at most `MAX_ITEMS` modules each; nothing is sent anywhere. At start-up the
commander's newest journals are read on a worker thread (the newest `StoredModules` snapshot and the events after it), so storage changes made while EDMC was not
running are not missed. The station names come from what the commander's own journals show (`Docked` and the snapshot's own station); the other stations in a
snapshot are known by system and market number only.
"""
from __future__ import annotations

import calendar
import hashlib
import json
import logging
import os
import re
import threading
import time
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple

try:
    from config import appname
except ImportError:   # unit tests outside EDMC
    appname = "EDMarketConnector"

from . import commander_data, journal_files, ship_plan
from .journal_blueprints import BLUEPRINT_NAMES

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

STATE_FILENAME = "stored_modules.json"
MAX_ITEMS = 2000          # modules kept per commander
MAX_STATIONS = 500        # station names remembered per commander
TEXT_CAP = 60             # longest name, system or blueprint kept
STATION_CAP = 80
MAX_ROWS = 400            # table rows shown at once; the filter narrows a longer list
STORE_EVENTS = ("ModuleStore", "MassModuleStore", "ModuleRetrieve")
SNAPSHOT = "StoredModules"
NAME_EVENTS = ("Docked", "Location")
READ_EVENTS = (SNAPSHOT,) + STORE_EVENTS + NAME_EVENTS + ("LoadGame",)
CLASSES = "EDCBA"         # a module's class number 1 to 5 as the letter the game's outfitting shows
_SIZES = ("tiny", "small", "medium", "large", "huge")
_MOUNTS = ("fixed", "gimbal", "turret")
_SIZE_CLASS = re.compile(r"size(\d)_class(\d)")


def _empty() -> Dict[str, Any]:
    return {"items": [], "asof": None, "stations": {}, "through": "", "tail": [], "scan": 0.0}


def _is_legacy(_raw: Any) -> bool:
    return False


# --- names -------------------------------------------------------------------------------------------------------------------------------------

def normalize_item(raw: Any) -> str:
    """The journal's lower-case `Item` form of a module name: `$int_engine_size3_class5_name;` becomes `int_engine_size3_class5`."""
    text = str(raw or "").strip()
    if text.startswith("$") and text.endswith(";"):
        text = text[1:-1]
    text = text.casefold()
    if text.endswith("_name"):
        text = text[:-5]
    return text[:80]


def display_name(item: str, localised: Any = "") -> str:
    """A readable name: the game's own localized name when the event has one, else the module type of the blueprint table, else the item's words."""
    named = str(localised or "").strip()
    if named:
        return named[:TEXT_CAP]
    return (ship_plan.module_type(item) or " ".join(item.replace("_", " ").split()).title())[:TEXT_CAP]


def rating(item: str) -> str:
    """The size and class of an internal module (`5A`), or the size and mounting of a weapon (`Medium gimbal`); empty when the item name does not say."""
    found = _SIZE_CLASS.search(item)
    if found:
        number = int(found.group(2))
        return f"{found.group(1)}{CLASSES[number - 1] if 1 <= number <= len(CLASSES) else number}"
    if item.startswith("hpt_"):
        parts = item.split("_")
        size = next((p for p in parts if p in _SIZES), "")
        mount = next((p for p in parts if p in _MOUNTS), "")
        return " ".join(p for p in (size.capitalize(), mount) if p)
    return ""


def engineering_text(item: str, blueprint: str, level: int) -> str:
    """`Increased FSD Range G5` style text for an engineered module, or `-`."""
    if not blueprint:
        return "-"
    name = BLUEPRINT_NAMES.get(blueprint, {}).get(ship_plan.module_type(item))
    if not name:
        name = " ".join(re.sub(r"([a-z])([A-Z])", r"\1 \2", blueprint.split("_", 1)[-1]).replace("_", " ").split())
    return f"{name} G{level}" if level else name


def engineering_of(module: Dict[str, Any]) -> str:
    """The engineering column for a stored module: its blueprint and grade, `-` for none, `?` for a module swapped out of a ship (the game did not report it)."""
    if module.get("p") and not module.get("e"):
        return "?"
    return engineering_text(module["i"], module["e"], module["l"])


def _int(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _module(item: str, localised: Any, hot: Any, blueprint: Any, level: Any, system: str, market: Optional[int],
            cost: Optional[int] = None, seconds: Optional[int] = None, transit: bool = False, partial: bool = False) -> Dict[str, Any]:
    """One stored module as it is kept: the item, its name, engineering, hot flag, and where it is."""
    return {"i": item, "n": display_name(item, localised), "e": str(blueprint or "")[:TEXT_CAP], "l": _int(level) or 0, "h": bool(hot),
            "s": system[:TEXT_CAP], "m": market, "c": cost, "t": seconds, "x": bool(transit), "p": bool(partial)}


def parse_snapshot(entry: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """The modules and the as-of record (when and where) of a `StoredModules` event."""
    own_system = str(entry.get("StarSystem") or "")
    items = []
    for raw in entry.get("Items") or []:
        if not isinstance(raw, dict) or not raw.get("Name"):
            continue
        transit = bool(raw.get("InTransit"))
        system = str(raw.get("StarSystem") or "")
        market = _int(raw.get("MarketID"))
        items.append(_module(normalize_item(raw.get("Name")), raw.get("Name_Localised"), raw.get("Hot"), raw.get("EngineerModifications"), raw.get("Level"),
                             "" if transit and not system else system, market, _int(raw.get("TransferCost")), _int(raw.get("TransferTime")), transit))
        if len(items) >= MAX_ITEMS:
            break
    asof = {"t": str(entry.get("timestamp") or ""), "station": str(entry.get("StationName") or "")[:STATION_CAP], "system": own_system[:TEXT_CAP],
            "market": _int(entry.get("MarketID"))}
    return items, asof


def matches(module: Dict[str, Any], query: str, where: str = "") -> bool:
    """Whether every word of `query` appears in the module's name, item, engineering, hot/transit marks or where it is."""
    words = query.casefold().split()
    if not words:
        return True
    text = " ".join((module["n"], module["i"], engineering_of(module), where, "hot" if module["h"] else "",
                     "in transit" if module["x"] else "")).casefold()
    return all(word in text for word in words)


def transfer_time(seconds: Optional[int]) -> str:
    """`2d 16h`, `3h 20m`, `42m`, or `-` when not known."""
    if seconds is None:
        return "-"
    if seconds <= 0:
        return "0m"
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes = rest // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{max(minutes, 1)}m"


def date_text(stamp: str) -> str:
    """`2026-10-10T08:15:00Z` as `10 Oct 2026`; the text unchanged when it cannot be read."""
    try:
        year, month, day = int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10])
        return f"{day} {('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec').split()[month - 1]} {year}"
    except (ValueError, IndexError):
        return stamp[:20]


def _epoch(stamp: str) -> float:
    try:
        return float(calendar.timegm(time.strptime(stamp[:19], "%Y-%m-%dT%H:%M:%S")))
    except ValueError:
        return 0.0


def _fingerprint(entry: Dict[str, Any]) -> str:
    return hashlib.md5(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def commander_of(entries: List[Dict[str, Any]]) -> str:
    return next((str(e.get("Commander") or "").casefold() for e in entries if e.get("event") == "LoadGame"), "")


# --- the book ----------------------------------------------------------------------------------------------------------------------------------

class ModuleBook:
    """Every commander's stored modules. `load(plugin_dir)` once at start-up, `set_commander` when a commander is seen, `handle` for each journal event."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._store = commander_data.new_store()
        self._plugin_dir: Optional[str] = None
        self._cmdr = ""
        self._catching = False
        self._pending: List[Dict[str, Any]] = []
        self._thread: Optional[threading.Thread] = None
        self.revision = 0                 # changes whenever the list does, so a window can tell it is out of date
        self.reading = False              # the journals are being read to catch up

    # --- state ---------------------------------------------------------------------------------------------------------------------------------
    def load(self, plugin_dir: str) -> None:
        with self._lock:
            self._plugin_dir = plugin_dir
            self._store = commander_data.read(os.path.join(plugin_dir, STATE_FILENAME), _is_legacy)
            self.revision += 1

    def _payload(self, cmdr: str) -> Optional[Dict[str, Any]]:
        if not cmdr:
            return None
        payload = commander_data.payload_for(self._store, cmdr, _empty)
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list) or not isinstance(payload.get("stations"), dict):
            payload = _empty()
            commander_data.put(self._store, cmdr, payload)
        for key, value in _empty().items():
            payload.setdefault(key, value)
        return payload

    def _save(self) -> None:
        if self._plugin_dir:
            commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)

    # --- asking --------------------------------------------------------------------------------------------------------------------------------
    @property
    def cmdr(self) -> str:
        return self._cmdr

    def modules(self, cmdr: str) -> List[Dict[str, Any]]:
        with self._lock:
            payload = self._payload(cmdr)
            return [dict(m) for m in payload["items"]] if payload else []

    def asof(self, cmdr: str) -> Optional[Dict[str, Any]]:
        """When and where the last snapshot was written (`t`, `station`, `system`, `market`), or None when none has been seen."""
        with self._lock:
            payload = self._payload(cmdr)
            return dict(payload["asof"]) if payload and payload.get("asof") else None

    def where(self, cmdr: str, module: Dict[str, Any]) -> str:
        """`Station (System)` when the station's name is known, else `System (market 123)`; `In transit` when the module is on its way."""
        system, market = module.get("s") or "", module.get("m")
        with self._lock:
            payload = self._payload(cmdr)
            known = payload["stations"].get(str(market)) if payload and market is not None else None
        if known and known[0]:
            return f"{known[0][:STATION_CAP]} ({(known[1] or system)[:TEXT_CAP]})"
        if module.get("x") and not system:
            return "In transit"
        if system and market is not None:
            return f"{system} (market {market})"
        return system or ("In transit" if module.get("x") else "Unknown")

    def freshness(self, cmdr: str) -> str:
        """The line above the list: when the last snapshot was written, or what to do to get one."""
        found = self.asof(cmdr)
        if not found:
            return "No stored-modules list yet. Open Module Storage at a station once so the game writes the list."
        place = ", ".join(part for part in (found.get("station"), found.get("system")) if part)
        return "As of the last visit to Module Storage: " + ", ".join(part for part in (date_text(found.get("t") or ""), place) if part)

    # --- following the journal -----------------------------------------------------------------------------------------------------------------
    def set_commander(self, cmdr: str, folder: Optional[str] = None, wait: bool = False) -> None:
        """Takes a commander in (the window and the list then show theirs) and catches up from their newest journals in the background."""
        cmdr = str(cmdr or "").strip()
        if not cmdr or commander_data.key_for(cmdr) == commander_data.key_for(self._cmdr):
            return
        with self._lock:
            self._cmdr, self._catching, self._pending = cmdr, True, []
            self.revision += 1
        thread = threading.Thread(target=self._catch_up, args=(cmdr, folder), name="WFMT-stored-modules", daemon=True)
        self._thread = thread
        thread.start()
        if wait:
            thread.join()

    def handle(self, entry: Dict[str, Any], cmdr: str = "") -> None:
        """Takes one journal event as it happens. Events that arrive while the journals are being read wait and are applied afterwards, in order."""
        event = entry.get("event")
        if event not in (SNAPSHOT,) + STORE_EVENTS + NAME_EVENTS:
            return
        with self._lock:
            if self._catching:
                self._pending.append(entry)
                return
            if self._apply(self._cmdr, entry):
                self._save()

    def _catch_up(self, cmdr: str, folder: Optional[str]) -> None:
        try:
            self._read_journals(cmdr, folder)
        except Exception:
            logger.debug("Could not catch up the stored modules from the journals", exc_info=True)
        finally:
            with self._lock:
                if commander_data.key_for(cmdr) == commander_data.key_for(self._cmdr):
                    pending, self._pending, self._catching = self._pending, [], False
                    for entry in pending:
                        self._apply(cmdr, entry)
                    self._save()
                self.reading = False

    def _read_journals(self, cmdr: str, folder: Optional[str]) -> None:
        wanted = commander_data.key_for(cmdr)
        with self._lock:
            payload = self._payload(cmdr)
            if payload is None:
                return
            since, has_snapshot = float(payload.get("scan") or 0.0), bool(payload.get("asof"))
        paths = journal_files.files_modified_since(max(0.0, since - 2.0), folder)
        if not paths:
            return
        self.reading = True
        if not has_snapshot:
            # nothing is known yet: start from the newest journal that holds a snapshot (it lists everything), the events before it add nothing
            snapshots = journal_files.event_pattern(SNAPSHOT)
            for index in range(len(paths) - 1, -1, -1):
                if commander_of(list(journal_files.read_events(paths[index], journal_files.event_pattern("LoadGame")))) not in ("", wanted):
                    continue
                if any(True for _ in journal_files.read_events(paths[index], snapshots)):
                    paths = paths[index:]
                    break
            else:
                paths = paths[-1:]
        pattern, newest = journal_files.event_pattern(*READ_EVENTS), 0.0
        for path in paths:
            if commander_data.key_for(self._cmdr) != wanted:
                return                                    # another commander loaded in: this read is no longer wanted
            entries = list(journal_files.read_events(path, pattern))
            if commander_of(entries) not in ("", wanted):
                continue
            with self._lock:
                for entry in entries:
                    self._apply(cmdr, entry)
            try:
                newest = max(newest, os.path.getmtime(path))
            except OSError:
                pass
        with self._lock:
            payload = self._payload(cmdr)
            if payload is not None and newest:
                payload["scan"] = newest

    # --- applying an event ---------------------------------------------------------------------------------------------------------------------
    def _apply(self, cmdr: str, entry: Dict[str, Any]) -> bool:
        """Applies one event to the commander's list if it is newer than what was applied before; True when anything changed."""
        payload = self._payload(cmdr)
        if payload is None:
            return False
        event, stamp = entry.get("event"), str(entry.get("timestamp") or "")
        if event == "LoadGame":
            return False
        through, tail = str(payload["through"]), payload["tail"]
        if stamp:
            fingerprint = _fingerprint(entry)
            if stamp < through or (stamp == through and fingerprint in tail):
                return False                              # already applied: the journal read at start-up and the live event are the same event
            if stamp > through:
                payload["through"], payload["tail"] = stamp, [fingerprint]
            else:
                tail.append(fingerprint)
        changed = False
        if event in NAME_EVENTS:
            changed = self._learn_station(payload, entry.get("MarketID"), entry.get("StationName"), entry.get("StarSystem"))
        elif event == SNAPSHOT:
            items, asof = parse_snapshot(entry)
            payload["items"], payload["asof"] = items, asof
            self._learn_station(payload, asof["market"], asof["station"], asof["system"])
            changed = True
        elif payload.get("asof"):
            changed = self._store_or_retrieve(payload, entry)
        if changed:
            self.revision += 1
        return changed

    @staticmethod
    def _learn_station(payload: Dict[str, Any], market: Any, name: Any, system: Any) -> bool:
        market, name = _int(market), str(name or "").strip()
        if market is None or not name:
            return False
        stations = payload["stations"]
        stations.pop(str(market), None)                   # re-added last, so the oldest names are the ones dropped
        stations[str(market)] = [name[:STATION_CAP], str(system or "")[:TEXT_CAP]]
        while len(stations) > MAX_STATIONS:
            stations.pop(next(iter(stations)))
        return False                                       # a name alone does not change the list

    def _store_or_retrieve(self, payload: Dict[str, Any], entry: Dict[str, Any]) -> bool:
        event, market = entry.get("event"), _int(entry.get("MarketID"))
        known = payload["stations"].get(str(market)) if market is not None else None
        system = known[1] if known else ""
        items: List[Dict[str, Any]] = payload["items"]
        if event == "ModuleStore" and entry.get("StoredItem"):
            added = [_module(normalize_item(entry["StoredItem"]), entry.get("StoredItem_Localised"), entry.get("Hot"), entry.get("EngineerModifications"),
                             entry.get("Level"), system, market)]
        elif event == "MassModuleStore":
            added = [_module(normalize_item(raw["Name"]), raw.get("Name_Localised"), raw.get("Hot"), raw.get("EngineerModifications"), raw.get("Level"),
                             system, market)
                     for raw in entry.get("Items") or [] if isinstance(raw, dict) and raw.get("Name")]
        elif event == "ModuleRetrieve" and entry.get("RetrievedItem"):
            self._remove(items, normalize_item(entry["RetrievedItem"]), str(entry.get("EngineerModifications") or ""), _int(entry.get("Level")) or 0,
                         bool(entry.get("Hot")), market)
            # a module swapped out for the retrieved one goes into storage here; the event does not say how it was engineered
            added = [_module(normalize_item(entry["SwapOutItem"]), entry.get("SwapOutItem_Localised"), False, "", 0, system, market, partial=True)] \
                if entry.get("SwapOutItem") else []
        else:
            return False
        items.extend(added)
        del items[MAX_ITEMS:]
        return True

    @staticmethod
    def _remove(items: List[Dict[str, Any]], item: str, blueprint: str, level: int, hot: bool, market: Optional[int]) -> None:
        """Takes the best match out: the same module at this station first, then anywhere (its transfer has arrived), then a module known only by its
        item (one that was swapped out, whose engineering the game did not report) at this station."""
        passes = (lambda m: m["m"] == market and not m["p"], lambda m: not m["p"], lambda m: m["m"] == market and m["p"])
        for same_place in passes:
            for index, module in enumerate(items):
                if module["i"] == item and same_place(module) and (module["p"] or (module["e"] == blueprint and module["l"] == level and module["h"] == hot)):
                    del items[index]
                    return

    def rows(self, cmdr: str, query: str = "", limit: int = MAX_ROWS) -> Tuple[List[Tuple[str, ...]], int]:
        """The table rows for the commander's modules that match `query` (module, class, engineering, where, transfer, marks), sorted by name, at most `limit`
        of them, and how many matched in all."""
        found = []
        for module in self.modules(cmdr):
            where = self.where(cmdr, module)
            if matches(module, query, where):
                found.append((module["n"].casefold(), where.casefold(), module, where))
        found.sort(key=lambda row: row[:2])
        rows = [(m["n"], rating(m["i"]), engineering_of(m), where, transfer_text(m), marks_text(m)) for _a, _b, m, where in found[:limit]]
        return rows, len(found)


FULL, PARTIAL = "full", "partial"


class StoredMatch(NamedTuple):
    """Whether a planned module is in storage: `kind` is FULL, PARTIAL or "" (not in storage); `short` fills the table cell; `detail` is the sentence under it."""
    kind: str
    short: str
    detail: str


NO_MATCH = StoredMatch("", "-", "")


def match_plan(planned: Sequence[ship_plan.PlannedModule], modules: Sequence[Dict[str, Any]], where: Callable[[Dict[str, Any]], str] = lambda m: "") -> List[StoredMatch]:
    """For each planned module of a Ship planner build, the stored module that would do for it, in the order given.

    Only modules in storage count (not those fitted to a ship). A stored module matches on its item (the same module, size and class); it is a FULL match when it
    carries the planned blueprint at the planned level or higher, and a PARTIAL one when its engineering differs (none, another blueprint, a lower level, or one the
    game did not report for a module swapped out of a ship). One stored module serves one planned module: full matches are given out first, then partial ones.
    The experimental effect is not part of the match, since the game does not report it for stored modules."""
    pool = list(modules)
    found: List[StoredMatch] = [NO_MATCH] * len(planned)

    def take(want, index: int, kind: str, lead: str) -> bool:
        item = planned[index]
        for at, module in enumerate(pool):
            if module["i"] == item.item and want(module, item):
                del pool[at]
                place = where(module)
                has = {"-": "none", "?": "not reported"}.get(engineering_of(module), engineering_of(module))
                detail = f"{lead}: {has}" + (f" at {place}" if place else "")
                if kind == PARTIAL:
                    detail += f"; the build has {item.blueprint}" + (f" G{item.level}" if item.level else "")
                found[index] = StoredMatch(kind, "Yes" if kind == FULL else "Partly", detail)
                return True
        return False

    def full(module: Dict[str, Any], item: ship_plan.PlannedModule) -> bool:
        return not module["p"] and bool(item.journal) and module["e"] == item.journal and module["l"] >= item.level

    def same_blueprint(module: Dict[str, Any], item: ship_plan.PlannedModule) -> bool:
        return not module["p"] and bool(item.journal) and module["e"] == item.journal

    for index in range(len(planned)):
        take(full, index, FULL, "In storage")
    for want in (same_blueprint, lambda m, i: True):
        for index in range(len(planned)):
            if found[index] is NO_MATCH:
                take(want, index, PARTIAL, "In storage with different engineering")
    return found


def transfer_text(module: Dict[str, Any]) -> str:
    """`1,200 cr, 2d 16h` from the game's figures at the last snapshot, or `-` when it gave none."""
    cost, seconds = module.get("c"), module.get("t")
    if cost is None and seconds is None:
        return "-"
    return ", ".join(part for part in (f"{cost:,} cr" if cost is not None else "", transfer_time(seconds) if seconds is not None else "") if part)


def marks_text(module: Dict[str, Any]) -> str:
    return ", ".join(mark for mark, on in (("Hot", module.get("h")), ("In transit", module.get("x"))) if on)


book = ModuleBook()
