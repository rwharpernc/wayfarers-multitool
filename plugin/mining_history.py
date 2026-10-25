"""The commander's mining history, built from their journals, for the Mining History window (the DASHBOARD button in Mining mode).

The Mining pages show the run in progress and nothing else, and that run lives only in memory, so a run that spanned an EDMC restart, a relog or an EDMC that was closed
could not be seen afterwards and nothing added the runs up. The journals hold all of it, so this reads them and keeps one record per run: when it started and ended, where,
how many asteroids were prospected (by content grade), what was refined, the limpets launched and, from the `MarketSell` events after docking, what it sold for.

A run is the same trip the live Space Mining page counts: `Undocked` to `Docked`. Mining that begins with no `Undocked` before it (a relog in space) starts a run of its own.
A sale is matched to the runs that mined what was sold, wherever it is made. Every finished run adds the tons it refined to a per-commodity list of mined tons not yet sold (`unsold`,
kept with the runs and carried across dockings, undockings and journals), and a `MarketSell` takes tons off that list, oldest run first, crediting those runs with the tons and, in
proportion, the `TotalSale`. Tons sold beyond what the list holds (cargo that was bought, or mined while EDMC was closed) are ignored, and tons sold for less than were mined leave the rest waiting.

Like the system history (`system_history.py`) it reads every finished journal once, in the background, keeps those runs in `mining_history.json` beside the plugin (one record
per commander, `commander_data.py`), and reads only the journals written since on a later start. The newest journal, which may still be growing, is never saved: its runs are
read afresh each time the window refreshes, so nothing is counted twice. The journals of another commander are skipped. Nothing is sent anywhere. No Tk.
"""

from __future__ import annotations

import copy
import logging
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from config import appname
except ImportError:   # unit tests outside EDMC
    appname = "EDMarketConnector"

from . import commander_data, journal_files, mining_rate
from .mining_alerts import prospect_key
from .mining_names import normalize

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

STATE_FILENAME = "mining_history.json"
MINING_EVENTS = ("ProspectedAsteroid", "MiningRefined", "AsteroidCracked", "LaunchDrone")
RING_EVENTS = ("SAASignalsFound", "Scan")         # a ring's hotspots (a DSS scan) and a body's ring classes and reserve level, for the Space Mining Book
BODY_EVENTS = ("ApproachBody", "LeaveBody", "SupercruiseEntry", "LaunchSRV", "DockSRV", "SRVDestroyed", "Died", "Cargo")   # with the above and MiningRefined: the bodies the Rhino mined on, for the Surface Mining Book
RUNS_VERSION = 5          # what the saved runs hold (5 adds what the limpets launched cost, `limpet_cost` and `limpet_unpriced`): 1 the run's totals, 2 also what was refined in the Rhino and on which body, 3 a Rhino already out when the journal began counted too, 4 the gaps of more than ten minutes between mining events (`idle`) left out of the mining time (an older file's runs are read once more)
EXTRAS_VERSION = 3        # what the saved scan_files cover: 1 rings, 2 rings and bodies, 3 bodies mined in a Rhino already out when the journal began (an older file is read once more)
EVENTS = MINING_EVENTS + RING_EVENTS + BODY_EVENTS + ("Commander", "LoadGame", "Undocked", "Docked", "FSDJump", "CarrierJump", "Location", "SupercruiseExit", "MarketSell", "BuyDrones")
SAVE_EVERY = 250          # journals read between saves, so a quit part-way through keeps its progress
PAUSE = 0.004             # seconds between journals, so reading years of them never starves EDMC
GRADES = ("Low", "Medium", "High")
RHINO_SRV = "mev_rhino"


def _empty() -> Dict[str, Any]:
    return {"files": [], "runs": [], "scan_files": [], "rings": {}, "bodies": {}, "unsold": {}, "extras": EXTRAS_VERSION, "runs_v": RUNS_VERSION, "limpet_price": 0}


def _is_legacy(_raw: Any) -> bool:
    return False


def _grade(entry: Dict[str, Any]) -> Optional[str]:
    """The content grade of a prospected rock, or None when the text names none of the three (a localized client): unknown, as the live page shows "?", and not counted as Low."""
    text = str(entry.get("Content_Localised") or entry.get("Content") or "")
    for grade in GRADES:
        if grade.casefold() in text.casefold():
            return grade
    return None


def _commodity(entry: Dict[str, Any]) -> str:
    return normalize(entry.get("Type_Localised") or entry.get("Type")) or "Unknown"


def new_run(started: str, basename: str, system: str, ring: str) -> Dict[str, Any]:
    return {"start": started, "end": started, "file": basename, "system": system, "ring": ring, "first": "", "last": "",
            "prospected": {grade: 0 for grade in GRADES}, "ungraded": 0, "motherlode": 0, "cracked": 0, "limpets": {}, "refined": {}, "sold": {},
            "srv": {}, "body": "", "limpet_cost": 0, "limpet_unpriced": 0}
    # srv: the part of `refined` that was refined while a Rhino was out; body: the body it was refined on; limpet_cost: what the limpets launched cost at the price last paid for
    # limpets (`BuyDrones`), limpet_unpriced: how many were launched before any price was known (bought before the journals WFMT has, say), which the cost leaves out


def run_key(run: Dict[str, Any]) -> str:
    """What names a run in the unsold list: its journal and start time."""
    return f"{run.get('file')}|{run.get('start')}"


def _clean_unsold(raw: Any) -> Dict[str, List[list]]:
    """The saved unsold list with anything malformed dropped: by commodity, [run key, tons] oldest first. A file saved before this list existed has none."""
    clean: Dict[str, List[list]] = {}
    if not isinstance(raw, dict):
        return clean
    for name, queue in raw.items():
        if not isinstance(queue, list):
            continue
        items = [[str(item[0]), item[1]] for item in queue
                 if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[1], int) and not isinstance(item[1], bool) and item[1] > 0]
        if items:
            clean[str(name)] = items
    return clean


def _attribute_sale(entry: Dict[str, Any], carry: Dict[str, List[list]], known: Dict[str, Dict[str, Any]]) -> None:
    """Credit a `MarketSell` to the runs that mined the commodity, oldest first, using up their unsold tons. Each run is given the tons it supplied and the share of `TotalSale` those
    tons make of the tons sold (the shares add up to exactly what the sold mined tons earned); tons sold beyond the list are ignored."""
    name = _commodity(entry)
    count, total = int(entry.get("Count") or 0), int(entry.get("TotalSale") or 0)
    queue = carry.get(name)
    if count <= 0 or not queue:
        return
    left, given, paid = count, 0, 0
    while left > 0 and queue:
        key, tons = queue[0]
        take = min(tons, left)
        left -= take
        if take >= tons:
            queue.pop(0)
        else:
            queue[0][1] = tons - take
        run = known.get(key)
        if run is None:
            continue                                   # a run the history no longer holds
        given += take
        share = total * given // count - paid
        paid += share
        sold = run["sold"].setdefault(name, [0, 0])
        sold[0] += take
        sold[1] += share
    if not queue:
        del carry[name]


def has_mining(run: Dict[str, Any]) -> bool:
    return bool(run["refined"] or run["cracked"] or any(run["prospected"].values()) or run.get("ungraded"))


def limpet_price(entry: Dict[str, Any]) -> int:
    """What one limpet cost in a `BuyDrones` event: its `BuyPrice`, else the `TotalCost` shared over the `Count`; 0 when the event gives neither."""
    def whole(value: Any) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0
    price = whole(entry.get("BuyPrice"))
    count = whole(entry.get("Count"))
    return price or (whole(entry.get("TotalCost")) // count if count else 0)


def runs_from(entries: List[Dict[str, Any]], basename: str, carry: Optional[Dict[str, List[list]]] = None,
              known: Optional[Dict[str, Dict[str, Any]]] = None, prices: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
    """The mining runs in one journal's events (the commander's own), oldest first. A run still going at the end of the file ends at its last mining event.
    `carry` is the unsold list (by commodity, [run key, tons] oldest first) as the earlier journals left it, and `known` the earlier runs by key: sales in these events are credited to the
    runs they name (in place) and to this journal's, and both are updated as the events are read. Left out, they start empty, which is a journal read on its own.
    `prices` holds the price last paid for a limpet (`prices["unit"]`, 0 before one is known), carried from the earlier journals and updated as `BuyDrones` events are read; each limpet launched
    is charged at it."""
    carry = {} if carry is None else carry
    known = {} if known is None else known
    prices = {"unit": 0} if prices is None else prices
    runs: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    seen: set = set()                                # the compositions prospected in the current run: a rock prospected again is counted once, as on the Space Mining page
    system, ring = "", ""
    body, rhino = "", False                          # the planet last approached, and whether a Rhino is out (what splits a run's refining into surface and ring)
    for entry in entries:
        event, stamp = entry.get("event"), str(entry.get("timestamp") or "")
        if event in ("FSDJump", "CarrierJump"):
            body, rhino = "", False
        elif event == "Location":
            body = str(entry.get("Body") or "") if entry.get("BodyType") == "Planet" else ""
        elif event == "SupercruiseExit":
            body = str(entry.get("Body") or "") if entry.get("BodyType") == "Planet" else ""
        elif event == "ApproachBody":
            body = str(entry.get("Body") or "")
        elif event in ("LeaveBody", "SupercruiseEntry"):
            body = ""
        elif event == "LaunchSRV":
            rhino = entry.get("SRVType") == RHINO_SRV
        elif event in ("DockSRV", "SRVDestroyed", "Died"):
            rhino = False
        elif event == "Cargo":                       # the hold of an SRV that is out: covers a Rhino launched before this journal began (only the Rhino refines ore)
            rhino = True if entry.get("Vessel") == "SRV" else (False if entry.get("Vessel") == "Ship" else rhino)
        if event in ("FSDJump", "CarrierJump"):
            system, ring = str(entry.get("StarSystem") or system), ""
        elif event in ("Location", "SupercruiseExit"):
            system = str(entry.get("StarSystem") or system)
            ring = str(entry.get("Body") or "") if entry.get("BodyType") == "PlanetaryRing" else ""
        elif event == "Undocked":
            current = new_run(stamp, basename, system, ring)
            seen = set()
        elif event == "Docked":
            seen = set()
            if current is not None:
                current["end"] = stamp
                if has_mining(current):
                    _finish(current, runs, carry, known)
                current = None
        elif event == "MarketSell":
            _attribute_sale(entry, carry, known)
        elif event == "BuyDrones":
            prices["unit"] = limpet_price(entry) or prices.get("unit", 0)
        elif event in MINING_EVENTS:
            if current is None:
                current, seen = new_run(stamp, basename, system, ring), set()      # mining with no undocking before it: a relog in space
            if not current["ring"] and ring:
                current["ring"], current["system"] = ring, system or current["system"]
            current["first"] = current["first"] or stamp
            _note_gap(current, stamp)
            current["last"] = stamp
            if event == "ProspectedAsteroid":
                key = prospect_key(entry.get("Materials"))
                if key is None or key not in seen:
                    if key is not None:
                        seen.add(key)
                    grade = _grade(entry)
                    if grade is None:
                        current["ungraded"] = current.get("ungraded", 0) + 1
                    else:
                        current["prospected"][grade] += 1
                    if entry.get("MotherlodeMaterial"):
                        current["motherlode"] += 1
            elif event == "MiningRefined":
                name = _commodity(entry)
                current["refined"][name] = current["refined"].get(name, 0) + 1
                if rhino:
                    current["srv"][name] = current["srv"].get(name, 0) + 1
                    current["body"] = current["body"] or body
            elif event == "AsteroidCracked":
                current["cracked"] += 1
            elif event == "LaunchDrone":
                kind = str(entry.get("Type") or "Unknown")
                current["limpets"][kind] = current["limpets"].get(kind, 0) + 1
                if prices.get("unit"):
                    current["limpet_cost"] = current.get("limpet_cost", 0) + prices["unit"]
                else:
                    current["limpet_unpriced"] = current.get("limpet_unpriced", 0) + 1
    if current is not None and has_mining(current):
        current["end"] = current["last"] or current["end"]
        _finish(current, runs, carry, known)
    return runs


def _note_gap(run: Dict[str, Any], stamp: str) -> None:
    """Add to the run's `idle` the seconds between its last mining event and this one when that is more than `mining_rate.MAX_GAP_SECONDS`: not mining time, as on the live page
    (`mining_rate.MiningClock`). `idle` is only present on a run that had such a gap, and a run saved before it existed reads as having none."""
    last = run["last"]
    if not last or stamp[:15] == last[:15]:       # the same ten minutes of the same hour: no gap that long (cheap check before reading the dates)
        return
    try:
        gap = (datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
    except ValueError:
        return
    if gap > mining_rate.MAX_GAP_SECONDS:
        run["idle"] = run.get("idle", 0) + int(gap)


def _finish(run: Dict[str, Any], runs: List[Dict[str, Any]], carry: Dict[str, List[list]], known: Dict[str, Dict[str, Any]]) -> None:
    """A run is over: keep it and put what it refined on the unsold list, behind what earlier runs left."""
    runs.append(run)
    key = run_key(run)
    known[key] = run
    for name, tons in run["refined"].items():
        if tons > 0:
            carry.setdefault(name, []).append([key, tons])


def rings_from(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """What one journal's events say about rings: by the ring's name (which includes its system's, so it is unique), the hotspots a DSS scan found (`SAASignalsFound` on a ring body: each
    mineral with its count), and the ring class and reserve level the parent body's `Scan` gives (`Rings` and `ReserveLevel`). See `mining_rings_data.py` for how it is shown."""
    from . import mining_rings_data as RD
    found: Dict[str, Dict[str, Any]] = {}
    system = ""
    for entry in entries:
        event, stamp = entry.get("event"), str(entry.get("timestamp") or "")
        if event in ("FSDJump", "CarrierJump", "Location"):
            system = str(entry.get("StarSystem") or system)
        elif event == "SAASignalsFound":
            body = str(entry.get("BodyName") or "")
            if RD.is_ring(body):
                record = RD.merge(found, RD.new_ring(body, system))
                record["hotspots"] = RD.hotspots_from(entry.get("Signals"))
                record["scanned"] = stamp
        elif event == "Scan":
            rings = entry.get("Rings")
            if isinstance(rings, list) and rings:
                for ring in rings:
                    if isinstance(ring, dict) and RD.is_ring(str(ring.get("Name") or "")):
                        record = RD.merge(found, RD.new_ring(str(ring["Name"]), str(entry.get("StarSystem") or system)))
                        record["class"] = str(ring.get("RingClass") or record["class"])
                        record["reserve"] = str(entry.get("ReserveLevel") or record["reserve"])
                        record["seen"] = stamp
    return found


def owner_of(entries: List[Dict[str, Any]]) -> str:
    """The commander (casefolded) a journal's events belong to, from its `Commander` or `LoadGame` line; empty when it does not say."""
    for entry in entries:
        if entry.get("event") == "Commander" and entry.get("Name"):
            return commander_data.key_for(entry["Name"])
        if entry.get("event") == "LoadGame" and entry.get("Commander"):
            return commander_data.key_for(entry["Commander"])
    return ""


class MiningHistory:
    def __init__(self) -> None:
        self._store = commander_data.new_store()
        self._plugin_dir: Optional[str] = None
        self._cmdr = ""
        self._lock = threading.RLock()
        self._live: List[Dict[str, Any]] = []         # the newest journal's runs, not saved
        self._live_rings: Dict[str, Dict[str, Any]] = {}   # and its rings
        self._live_bodies: Dict[str, Dict[str, Any]] = {}  # and its bodies
        self._live_patch: Dict[str, Dict[str, Any]] = {}   # saved runs the newest journal's sales were credited to, as copies (the saved ones are not touched)
        self._live_unsold: Optional[Dict[str, List[list]]] = None   # the unsold list after the newest journal; None when that journal is not this commander's
        self.reading = ""                              # "" idle, else a line saying how far the first read has got
        self._thread: Optional[threading.Thread] = None
        self.pause = PAUSE
        self._again: Optional[tuple] = None
        self.ready = False                             # the history has been read at least once this run

    # --- state --------------------------------------------------------------------------------------------------
    def start(self, plugin_dir: str) -> None:
        with self._lock:
            self._plugin_dir = plugin_dir
            self._store = commander_data.read(os.path.join(plugin_dir, STATE_FILENAME), _is_legacy)

    def set_commander(self, cmdr: str) -> None:
        cmdr = str(cmdr or "").strip()
        if not cmdr or commander_data.key_for(cmdr) == commander_data.key_for(self._cmdr):
            return
        with self._lock:
            self._cmdr, self._live, self._live_rings, self._live_bodies = cmdr, [], {}, {}
            self._live_patch, self._live_unsold = {}, None
            self.ready = False
        self.refresh()

    @property
    def commander(self) -> str:
        return self._cmdr

    def _payload(self) -> Optional[Dict[str, Any]]:
        if not self._cmdr:
            return None
        payload = commander_data.payload_for(self._store, self._cmdr, _empty)
        if not isinstance(payload, dict) or not isinstance(payload.get("runs"), list) or not isinstance(payload.get("files"), list):
            payload = _empty()
            commander_data.put(self._store, self._cmdr, payload)
        if payload.get("runs_v") != RUNS_VERSION:
            payload["files"], payload["runs"], payload["runs_v"], payload["unsold"], payload["limpet_price"] = [], [], RUNS_VERSION, {}, 0      # runs saved before the Rhino's refining was told apart from the rings' are read from the journals once more
        payload["unsold"] = _clean_unsold(payload.get("unsold"))          # absent in a file saved before sales were matched to the runs that mined them: nothing waiting
        if (not isinstance(payload.get("rings"), dict) or not isinstance(payload.get("bodies"), dict) or not isinstance(payload.get("scan_files"), list)
                or payload.get("extras") != EXTRAS_VERSION):
            payload["rings"], payload["bodies"], payload["scan_files"], payload["extras"] = {}, {}, [], EXTRAS_VERSION   # from before the Mining Books: its journals are read once more for rings and bodies
        return payload

    def _save(self) -> None:
        if self._plugin_dir:
            commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)

    # --- asking --------------------------------------------------------------------------------------------------
    def runs(self) -> List[Dict[str, Any]]:
        """Every run, saved and live, oldest first."""
        with self._lock:
            payload = self._payload()
            saved = [self._live_patch.get(run_key(run), run) for run in payload["runs"]] if payload else []
            live = list(self._live)
        return sorted(saved + live, key=lambda run: str(run.get("start") or ""))

    def unsold(self) -> Dict[str, Dict[str, int]]:
        """The tons mined and not yet sold, by run key (`run_key`) and commodity: what the unsold list holds after the newest journal."""
        with self._lock:
            payload = self._payload()
            carry = self._live_unsold if self._live_unsold is not None else (payload["unsold"] if payload else {})
            out: Dict[str, Dict[str, int]] = {}
            for name, queue in carry.items():
                for key, tons in queue:
                    out.setdefault(key, {})[name] = out.get(key, {}).get(name, 0) + tons
            return out

    def rings(self) -> Dict[str, Dict[str, Any]]:
        """Every ring the journals have shown (saved and live), by ring name: hotspots, class and reserve level. Not what the commander wrote (`mining_rings.py` keeps that)."""
        from . import mining_rings_data as RD
        with self._lock:
            payload = self._payload()
            merged: Dict[str, Dict[str, Any]] = {}
            for source in ((payload["rings"] if payload else {}), self._live_rings):
                for record in source.values():
                    RD.merge(merged, record)
            return merged

    def bodies(self) -> Dict[str, Dict[str, Any]]:
        """Every body the Rhino mined on or a DSS scan found mining locations on (saved and live), by body name: location count, class, tons refined and when. See `mining_bodies_data.py`."""
        from . import mining_bodies_data as BD
        with self._lock:
            payload = self._payload()
            merged: Dict[str, Dict[str, Any]] = {}
            for source in ((payload["bodies"] if payload else {}), self._live_bodies):
                for record in source.values():
                    BD.merge(merged, record)
            return merged

    def clear(self) -> None:
        """Forget the saved runs, so the next refresh reads every journal again."""
        with self._lock:
            payload = self._payload()
            if payload is not None:
                payload["files"], payload["runs"], payload["scan_files"], payload["rings"], payload["bodies"], payload["unsold"] = [], [], [], {}, {}, {}
                self._live, self._live_rings, self._live_bodies, self._live_patch, self._live_unsold = [], {}, {}, {}, None
                self._save()
            self.ready = False

    # --- building ------------------------------------------------------------------------------------------------
    def refresh(self, folder: Optional[str] = None, wait: bool = False) -> None:
        """Reads the journals not yet in the history (background), then the newest one into this session's runs."""
        if not self._cmdr:
            return
        if self._thread is not None and self._thread.is_alive():
            self._again = (self._cmdr, folder)              # a read is under way: read once more when it stops
            return
        self._thread = threading.Thread(target=self._build, args=(self._cmdr, folder), name="WFMT-mining-history", daemon=True)
        self._thread.start()
        if wait:
            self._thread.join()

    def _build(self, cmdr: str, folder: Optional[str]) -> None:
        try:
            self._read_all(cmdr, folder)
        except Exception:
            logger.debug("Could not build the mining history", exc_info=True)
        finally:
            self.reading = ""
            again, self._again = self._again, None
            if again is not None:
                self._thread = threading.Thread(target=self._build, args=again, name="WFMT-mining-history", daemon=True)
                self._thread.start()
            elif commander_data.key_for(cmdr) == commander_data.key_for(self._cmdr):
                self.ready = True

    def _read_all(self, cmdr: str, folder: Optional[str]) -> None:
        paths = journal_files.files_modified_since(0.0, folder)
        if not paths:
            return
        wanted, pattern = commander_data.key_for(cmdr), journal_files.event_pattern(*EVENTS)
        with self._lock:
            payload = self._payload()
            if payload is None:
                return
            done, scan_done = set(payload["files"]), set(payload["scan_files"])
            known = {run_key(run): run for run in payload["runs"]}
            prices = {"unit": int(payload.get("limpet_price") or 0)}
        closed, active = paths[:-1], paths[-1]
        todo = [p for p in closed if os.path.basename(p) not in done or os.path.basename(p) not in scan_done]
        for count, path in enumerate(todo, 1):
            if commander_data.key_for(self._cmdr) != wanted:
                return                                        # another commander loaded in: this read is no longer wanted
            if len(todo) > 20:
                self.reading = f"Reading your journals for the mining history ({count * 100 // len(todo)}%)"
            entries = list(journal_files.read_events(path, pattern))
            owner = owner_of(entries)
            with self._lock:
                payload = self._payload()
                if payload is None:
                    return
                name = os.path.basename(path)
                if not owner or owner == wanted:
                    if name not in done:
                        payload["runs"].extend(runs_from(entries, name, payload["unsold"], known, prices))
                    if name not in scan_done:
                        from . import mining_bodies_data as BD, mining_rings_data as RD
                        for record in rings_from(entries).values():
                            RD.merge(payload["rings"], record)
                        for record in BD.bodies_from(entries).values():
                            BD.merge(payload["bodies"], record)
                if name not in done:
                    payload["files"].append(name)
                if name not in scan_done:
                    payload["scan_files"].append(name)
                if count % SAVE_EVERY == 0:
                    self._save()
            time.sleep(self.pause)
        with self._lock:
            payload = self._payload()
            if payload is not None:
                payload["limpet_price"] = prices["unit"]
            self._save()
        entries = list(journal_files.read_events(active, pattern))
        owner = owner_of(entries)
        with self._lock:
            mine = not owner or owner == wanted
            payload = self._payload()
            if mine and payload is not None:
                carry = copy.deepcopy(payload["unsold"])           # the newest journal is read on copies, so reading it again never counts a sale twice
                waiting = {key for queue in carry.values() for key, _tons in queue}
                known = {key: copy.deepcopy(run) for run in payload["runs"] if (key := run_key(run)) in waiting}
                patch = dict(known)
                self._live = runs_from(entries, os.path.basename(active), carry, known, dict(prices))
                self._live_patch, self._live_unsold = patch, carry
            else:
                self._live, self._live_patch, self._live_unsold = [], {}, None
            self._live_rings = rings_from(entries) if mine else {}
            from . import mining_bodies_data as BD
            self._live_bodies = BD.bodies_from(entries) if mine else {}


history = MiningHistory()
