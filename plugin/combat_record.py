"""The Combat Record: a commander's kills and deaths, per ship, for the current session and added up over every session. No Tk.

What is counted, from the journal:

- a **kill** is a `Bounty` (a wanted ship or on-foot target destroyed) or a `FactionKillBond` (a ship destroyed in a conflict zone or for a faction);
- a **PvP kill** is a `PVPKill` (another commander destroyed); it is counted apart from kills, and the K/D ratio counts both;
- a **death** is a `Died`;
- the **rewards** are the credits those bounties and bonds paid (`TotalReward` / `Reward`).

Each count belongs to the vessel the commander was in. `Craft` follows that from `LoadGame`, `Loadout`, `ShipyardSwap`, `SetUserShipName`, `Embark`, `Disembark`,
`LaunchSRV` and `DockSRV`: a ship is known by its type and `ShipID` (so two ships of one type are two rows, and a renamed ship stays one row), and the SRV and the
commander on foot are rows of their own. A kill of an on-foot target is on the "On foot" row whatever the tracker believes (the target's name says it was a ground
fight).

A **session** is one game login, tied to the journal file it was played in (the same rule as `session_credits.py`), so the session of a live game and the same session
read back from the journal are one record. Every session keeps its own per-ship counts; the totals are kept separately, so the 300-session limit never changes them.

Kept per commander in `combat_record.json` beside the plugin (`commander_data.py`); nothing is sent anywhere. At start-up the commander's journals are read on a worker
thread (all of them the first time, afterwards only the files that changed), so play with EDMC closed is counted. An event is never counted twice: `through` is the
timestamp of the newest event counted and `seen` holds the fingerprints of the events at that very second.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional, Tuple

try:
    from config import appname
except ImportError:   # unit tests outside EDMC
    appname = "EDMarketConnector"

from . import commander_data, journal_files
from .ship_names import display_name

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

STATE_FILENAME = "combat_record.json"
MAX_SESSIONS = 300        # sessions kept per commander (the totals do not depend on them)
MAX_SHIPS = 400           # ships kept per commander
TEXT_CAP = 60
COUNT_EVENTS = ("Bounty", "FactionKillBond", "PVPKill", "Died")
CONTEXT_EVENTS = ("Commander", "LoadGame", "Loadout", "ShipyardSwap", "SetUserShipName", "Embark", "Disembark", "LaunchSRV", "DockSRV", "Resurrect")
READ_EVENTS = COUNT_EVENTS + CONTEXT_EVENTS
FIELDS = ("kills", "pvp", "deaths", "reward")
FOOT, SRV, UNKNOWN = "foot", "srv", "unknown"
_FIXED_NAMES = {FOOT: "On foot", SRV: "SRV", UNKNOWN: "Unknown ship"}


# --- counts ------------------------------------------------------------------------------------------------------------------------------

def new_tally() -> Dict[str, int]:
    return {name: 0 for name in FIELDS}


def clean_tally(raw: Any) -> Dict[str, int]:
    """A tally with every field a non-negative int, whatever a hand-edited file held."""
    tally = new_tally()
    if isinstance(raw, dict):
        for name in FIELDS:
            value = raw.get(name)
            if isinstance(value, int) and not isinstance(value, bool) and value > 0:
                tally[name] = value
    return tally


def add_to(tally: Dict[str, int], delta: Dict[str, int]) -> None:
    for name in FIELDS:
        tally[name] = tally.get(name, 0) + int(delta.get(name, 0))


def is_empty(tally: Dict[str, int]) -> bool:
    return not any(tally.get(name) for name in FIELDS)


def all_kills(tally: Dict[str, int]) -> int:
    """Kills and PvP kills together: what the K/D ratio counts."""
    return int(tally.get("kills", 0)) + int(tally.get("pvp", 0))


def ratio_text(tally: Dict[str, int]) -> str:
    """Kills per death to one decimal; a dash while there has been no death (nothing to divide by)."""
    deaths = int(tally.get("deaths", 0))
    return f"{all_kills(tally) / deaths:.1f}" if deaths else "-"


def summary_text(tally: Dict[str, int]) -> str:
    """'12 kills, 1 death, K/D 12.0' (PvP kills are named only when there are some)."""
    kills, deaths = int(tally.get("kills", 0)), int(tally.get("deaths", 0))
    parts = [f"{kills:,} kill{'s' if kills != 1 else ''}"]
    if tally.get("pvp"):
        parts.append(f"{int(tally['pvp']):,} PvP")
    parts.append(f"{deaths:,} death{'s' if deaths != 1 else ''}")
    parts.append(f"K/D {ratio_text(tally)}")
    return ", ".join(parts)


def _as_int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0 else 0


def is_ground_target(entry: Dict[str, Any]) -> bool:
    """A `Bounty` on an on-foot target: NPC suit archetypes ("suitai_scientist") and citizens, where a ship kill names a ship type."""
    target = str(entry.get("Target") or "").lower()
    return "suitai" in target or "citizen" in target or target.startswith("suit_")


def delta_for(entry: Dict[str, Any]) -> Optional[Dict[str, int]]:
    """What one journal event adds to the counts, or None when it is not a kill or a death."""
    event = entry.get("event")
    if event == "Bounty":
        reward = _as_int(entry.get("TotalReward"))
        if not reward:
            reward = _as_int(entry.get("Reward"))
        if not reward and isinstance(entry.get("Rewards"), list):
            reward = sum(_as_int(r.get("Reward")) for r in entry["Rewards"] if isinstance(r, dict))
        return {"kills": 1, "reward": reward}
    if event == "FactionKillBond":
        return {"kills": 1, "reward": _as_int(entry.get("Reward"))}
    if event == "PVPKill":
        return {"pvp": 1}
    if event == "Died":
        return {"deaths": 1}
    return None


def fingerprint(entry: Dict[str, Any]) -> str:
    """A short stable id for an event, to tell two different events of one second from one event seen twice."""
    text = json.dumps(entry, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:16]


# --- the vessel ----------------------------------------------------------------------------------------------------------------------------

def _text(value: Any) -> str:
    return str(value or "").strip()[:TEXT_CAP]


def _ship_id(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


class Craft:
    """The vessel the commander is in, followed from the journal's events (a fresh one for each journal file: every file begins with `LoadGame`)."""

    def __init__(self) -> None:
        self.type = ""
        self.id: Optional[int] = None
        self.name = ""
        self.ident = ""
        self.kind = ""            # the game's own name for the kind of ship, when the journal gave one
        self.vessel = "ship"

    def see(self, entry: Dict[str, Any]) -> None:
        event = entry.get("event")
        if event in ("LoadGame", "Loadout"):
            if _text(entry.get("Ship")):
                self.type, self.id = _text(entry.get("Ship")).lower(), _ship_id(entry.get("ShipID"))
                self.name, self.ident = _text(entry.get("ShipName")), _text(entry.get("ShipIdent"))
                self.kind = _text(entry.get("Ship_Localised"))
            if event == "LoadGame":
                self.vessel = "ship"
        elif event == "ShipyardSwap":
            self.type, self.id = _text(entry.get("ShipType")).lower(), _ship_id(entry.get("ShipID"))
            self.name = self.ident = ""      # the Loadout that follows names it
            self.kind = _text(entry.get("ShipType_Localised"))
            self.vessel = "ship"
        elif event == "SetUserShipName":
            if _ship_id(entry.get("ShipID")) == self.id:
                self.name, self.ident = _text(entry.get("UserShipName")), _text(entry.get("UserShipId"))
        elif event == "Embark":
            self.vessel = SRV if entry.get("SRV") else "ship"
        elif event == "Disembark":
            self.vessel = SRV if entry.get("SRV") else FOOT
        elif event == "LaunchSRV":
            self.vessel = SRV
        elif event in ("DockSRV", "Resurrect"):
            self.vessel = "ship"

    def adopt(self, state: Any) -> None:
        """Take the ship from EDMC's own state when no event has said which ship it is (EDMC started with the game running)."""
        if self.type or not isinstance(state, dict) or not _text(state.get("ShipType")):
            return
        self.type, self.id = _text(state.get("ShipType")).lower(), _ship_id(state.get("ShipID"))
        self.name, self.ident = _text(state.get("ShipName")), _text(state.get("ShipIdent"))
        self.kind = ""

    def key_for(self, entry: Dict[str, Any]) -> str:
        """The row a count belongs to: a ship (`type#id`), `srv` or `foot`."""
        if entry.get("event") == "Bounty" and is_ground_target(entry):
            return FOOT
        if self.vessel in (SRV, FOOT):
            return self.vessel
        if not self.type:
            return UNKNOWN
        return f"{self.type}#{self.id}" if self.id is not None else self.type

    def meta(self, key: str) -> Dict[str, Any]:
        if key in _FIXED_NAMES:
            return {"type": key, "name": "", "ident": ""}
        return {"type": self.type, "name": self.name, "ident": self.ident, "kind": self.kind}


def ship_label(meta: Dict[str, Any], key: str = "") -> str:
    """The ship's kind as a player reads it ('Federal Corvette', 'Anaconda Mk II'): the game's own name when the journal gave one, else `ship_names`. The SRV
    and on foot have fixed names."""
    kind = str(meta.get("type") or key)
    if kind in _FIXED_NAMES:
        return _FIXED_NAMES[kind]
    return display_name(kind, meta.get("kind")) or kind


def ship_title(meta: Dict[str, Any]) -> str:
    """The ship's own name and ident ('Wayward Star [WS-01]'), empty when it has none."""
    name, ident = str(meta.get("name") or ""), str(meta.get("ident") or "")
    return f"{name} [{ident}]" if name and ident else name or (f"[{ident}]" if ident else "")


# --- the book ------------------------------------------------------------------------------------------------------------------------------------

def _empty() -> Dict[str, Any]:
    return {"through": "", "seen": [], "total": new_tally(), "ships": {}, "sessions": [], "scan": 0.0}


def _is_legacy(_raw: Any) -> bool:
    return False


class CombatBook:
    """Every commander's combat record. `load(plugin_dir)` once at start-up, `set_commander` when a commander is seen, `handle` for each journal event."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._store = commander_data.new_store()
        self._plugin_dir: Optional[str] = None
        self._cmdr = ""
        self._craft = Craft()
        self._session_id = ""
        self._seed: Optional[Tuple[str, Craft]] = None     # the vessel at the end of the newest journal read
        self._catching = False
        self._pending: List[Tuple[Dict[str, Any], Any]] = []
        self._thread: Optional[threading.Thread] = None
        self.logfile = journal_files.current_logfile          # a test replaces it
        self.revision = 0                        # changes whenever a count does, so a window can tell it is out of date
        self.reading = False                     # the journals are being read to catch up

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
        if not isinstance(payload, dict):
            payload = _empty()
            commander_data.put(self._store, cmdr, payload)
        for name, value in _empty().items():
            payload.setdefault(name, value)
        if not isinstance(payload["ships"], dict) or not isinstance(payload["sessions"], list) or not isinstance(payload["seen"], list):
            payload["ships"], payload["sessions"], payload["seen"] = {}, [], []
        payload["total"] = clean_tally(payload["total"])
        return payload

    def _save(self) -> None:
        if self._plugin_dir:
            commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)

    @property
    def cmdr(self) -> str:
        return self._cmdr

    # --- asking --------------------------------------------------------------------------------------------------------------------------------
    def total(self, cmdr: str) -> Dict[str, int]:
        with self._lock:
            payload = self._payload(cmdr)
            return dict(payload["total"]) if payload else new_tally()

    def ship_rows(self, cmdr: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """The per-ship counts, most kills first: over every session, or only those of the session `session_id`. Each row has `key`, `type`, `name`, `ident`
        and a `tally`."""
        with self._lock:
            payload = self._payload(cmdr)
            if not payload:
                return []
            if session_id is None:
                counts = {key: entry.get("t") for key, entry in payload["ships"].items() if isinstance(entry, dict)}
            else:
                session = self._find_session(payload, session_id)
                counts = session.get("ships", {}) if session else {}
            rows = []
            for key, raw in counts.items():
                tally = clean_tally(raw)
                if is_empty(tally):
                    continue
                meta = payload["ships"].get(key) if isinstance(payload["ships"].get(key), dict) else {}
                rows.append({"key": key, "type": str(meta.get("type") or key), "name": str(meta.get("name") or ""), "ident": str(meta.get("ident") or ""), "tally": tally})
        rows.sort(key=lambda r: (-all_kills(r["tally"]), r["tally"]["deaths"], ship_label(r, r["key"]).casefold()))
        return rows

    def session_total(self, cmdr: str, session_id: str) -> Dict[str, int]:
        with self._lock:
            payload = self._payload(cmdr)
            session = self._find_session(payload, session_id) if payload else None
            return clean_tally(session.get("t")) if session else new_tally()

    def sessions(self, cmdr: str) -> List[Dict[str, Any]]:
        """The sessions with a kill or a death, newest first: `id`, `start`, `end` (ISO times) and a `tally`."""
        with self._lock:
            payload = self._payload(cmdr)
            if not payload:
                return []
            found = [{"id": str(s.get("id") or ""), "start": str(s.get("start") or ""), "end": str(s.get("end") or ""), "tally": clean_tally(s.get("t"))}
                     for s in payload["sessions"] if isinstance(s, dict)]
        return list(reversed(found))

    @property
    def session_id(self) -> str:
        """The session being played now ('' before the first event)."""
        return self._session_id

    # --- changing ------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _find_session(payload: Optional[Dict[str, Any]], session_id: str) -> Optional[Dict[str, Any]]:
        if not payload or not session_id:
            return None
        for session in reversed(payload["sessions"]):
            if isinstance(session, dict) and session.get("id") == session_id:
                return session
        return None

    def _count(self, payload: Dict[str, Any], entry: Dict[str, Any], craft: Craft, session_id: str) -> bool:
        """Add one kill or death to the record. Returns False when the event had been counted already or is not one."""
        delta = delta_for(entry)
        stamp = str(entry.get("timestamp") or "")
        if delta is None or not stamp:
            return False
        through, mark = str(payload.get("through") or ""), fingerprint(entry)
        if stamp < through or (stamp == through and mark in payload["seen"]):
            return False
        if stamp > through:
            payload["through"], payload["seen"] = stamp, []
        payload["seen"].append(mark)
        key, info = craft.key_for(entry), None
        ships = payload["ships"]
        if key not in ships and len(ships) >= MAX_SHIPS:
            key, info = UNKNOWN, {"type": UNKNOWN, "name": "", "ident": ""}
        add_to(payload["total"], delta)
        meta = ships.setdefault(key, {"t": new_tally()})
        meta.update(info or craft.meta(key))
        meta["t"] = clean_tally(meta.get("t"))
        add_to(meta["t"], delta)
        session = self._find_session(payload, session_id)
        if session is None:
            session = {"id": session_id or "unknown", "start": stamp, "end": stamp, "t": new_tally(), "ships": {}}
            payload["sessions"].append(session)
            del payload["sessions"][:-MAX_SESSIONS]
        session["end"] = max(str(session.get("end") or ""), stamp)
        session["t"] = clean_tally(session.get("t"))
        add_to(session["t"], delta)
        session.setdefault("ships", {})
        session["ships"][key] = clean_tally(session["ships"].get(key))
        add_to(session["ships"][key], delta)
        return True

    def clear(self, cmdr: str) -> None:
        """Forget this commander's record (a rebuild from the journals follows)."""
        with self._lock:
            commander_data.put(self._store, cmdr, _empty())
            self._session_id = ""
            self.revision += 1
            self._save()

    # --- following the journal -----------------------------------------------------------------------------------------------------------------
    def set_commander(self, cmdr: str, folder: Optional[str] = None, wait: bool = False, force: bool = False) -> None:
        """Takes a commander in (the window then shows theirs) and counts what they did while EDMC was not running, in the background."""
        cmdr = str(cmdr or "").strip()
        if not cmdr or (not force and commander_data.key_for(cmdr) == commander_data.key_for(self._cmdr)):
            return
        with self._lock:
            self._cmdr, self._catching, self._pending, self._craft, self._session_id = cmdr, True, [], Craft(), ""
            self.reading = True
            self.revision += 1
        thread = threading.Thread(target=self._catch_up, args=(cmdr, folder), name="WFMT-combat-record", daemon=True)
        self._thread = thread
        thread.start()
        if wait:
            thread.join()

    def rebuild(self, cmdr: str, folder: Optional[str] = None, wait: bool = False) -> None:
        """Clear this commander's record and read every journal again."""
        if not cmdr:
            return
        self.clear(cmdr)
        self.set_commander(cmdr, folder, wait, force=True)

    def handle(self, entry: Dict[str, Any], cmdr: str = "", state: Any = None) -> bool:
        """Takes one journal event as it happens. Returns True when a count changed. Events that arrive while the journals are being read wait, in order."""
        event = entry.get("event")
        if event not in READ_EVENTS or not self._cmdr:
            return False
        with self._lock:
            if self._catching:
                self._pending.append((entry, dict(state) if isinstance(state, dict) else None))
                return False
            return self._apply_live(entry, state)

    def _apply_live(self, entry: Dict[str, Any], state: Any) -> bool:
        event = entry.get("event")
        if event in ("LoadGame", "Commander") or not self._session_id:
            self._session_id = self._session_for(entry)
        self._craft.see(entry)
        if event not in COUNT_EVENTS:
            return False
        self._craft.adopt(state)
        payload = self._payload(self._cmdr)
        if payload is None or not self._count(payload, entry, self._craft, self._session_id):
            return False
        self.revision += 1
        self._save()
        return True

    def _seed_live(self) -> None:
        """When the newest journal read is the one the game is writing now, carry its last vessel into the live tracking (EDMC may have started while the
        commander was on foot or in the SRV, which no later event would say)."""
        seed, self._seed = self._seed, None
        logfile = self.logfile()
        if seed and logfile and seed[0] == os.path.basename(logfile):
            self._craft = seed[1]

    def _session_for(self, entry: Dict[str, Any]) -> str:
        logfile = self.logfile()
        if logfile:
            return os.path.basename(logfile)
        return self._session_id or "live-" + str(entry.get("timestamp") or "")

    def _catch_up(self, cmdr: str, folder: Optional[str]) -> None:
        try:
            self._read_journals(cmdr, folder)
        except Exception:
            logger.debug("Could not catch up the combat record from the journals", exc_info=True)
        finally:
            with self._lock:
                if commander_data.key_for(cmdr) == commander_data.key_for(self._cmdr):
                    pending, self._pending, self._catching = self._pending, [], False
                    self._seed_live()
                    for entry, state in pending:
                        self._apply_live(entry, state)
                    self.revision += 1
                    self._save()
                self.reading = False

    def _read_journals(self, cmdr: str, folder: Optional[str]) -> None:
        wanted = commander_data.key_for(cmdr)
        with self._lock:
            payload = self._payload(cmdr)
            if payload is None:
                return
            since = float(payload.get("scan") or 0.0)
        paths = journal_files.files_modified_since(max(0.0, since - 2.0), folder)
        pattern, newest = journal_files.event_pattern(*READ_EVENTS), since
        for path in paths:
            if commander_data.key_for(self._cmdr) != wanted:
                return                                    # another commander loaded in: this read is no longer wanted
            try:
                modified = os.path.getmtime(path)
            except OSError:
                continue
            session_id, craft, current, changed, mine = os.path.basename(path), Craft(), "", False, False
            for entry in journal_files.read_events(path, pattern):
                kind = entry.get("event")
                if kind == "Commander" and entry.get("Name"):
                    current = commander_data.key_for(entry["Name"])
                    continue
                if kind == "LoadGame" and entry.get("Commander"):
                    current = commander_data.key_for(entry["Commander"])
                if current != wanted:
                    continue
                craft.see(entry)
                mine = True
                if kind in COUNT_EVENTS:
                    with self._lock:
                        payload = self._payload(cmdr)
                        if payload is not None and self._count(payload, entry, craft, session_id):
                            changed = True
            newest = max(newest, modified)
            if mine:
                with self._lock:
                    self._seed = (session_id, craft)
            if changed:
                with self._lock:
                    self.revision += 1
        with self._lock:
            payload = self._payload(cmdr)
            if payload is not None:
                payload["scan"] = newest
                self._save()


book = CombatBook()
