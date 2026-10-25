"""What Get body info found, kept between sessions, per commander.

A lookup (`mining_body_lookup`, the Surface Mining Book's Get body info button) asks EDSM and Spansh once for a system's bodies. The answer is remembered here, in `mining_body_cache.json`
beside the plugin (one payload per commander, `commander_data.py`), so arriving in that system again, or restarting EDMC, brings the bodies back without another request: the Mining body
list is seeded from it on arrival. Nothing is asked for here and nothing is sent anywhere; the file only holds what the button already fetched. It keeps the most recently looked-up
systems (`MAX_SYSTEMS`), and a new lookup of a system replaces its entry. Pure apart from the file: no Tk, no EDMC beyond the logger.
"""
from __future__ import annotations

import dataclasses
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from . import commander_data
from .mining_body_lookup import OutsideBody

try:
    from config import appname
except ImportError:   # unit tests outside EDMC
    appname = "EDMarketConnector"

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

STATE_FILENAME = "mining_body_cache.json"
MAX_SYSTEMS = 60
MAX_BODIES = 120
"""The most bodies kept for one system (a system has at most a few hundred bodies; the landable ones are far fewer)."""


def _key(system: str) -> str:
    return str(system or "").strip().casefold()


def _empty() -> Dict[str, Any]:
    return {"systems": {}}


def _is_legacy(_raw: Any) -> bool:
    return False


def _body(raw: Any) -> Optional[OutsideBody]:
    """A body from a saved dict, or None for one that is damaged."""
    if not isinstance(raw, dict) or not isinstance(raw.get("name"), str) or not raw["name"].strip() or not isinstance(raw.get("planet_class"), str) or not raw["planet_class"].strip():
        return None
    radius, count = raw.get("radius_m"), raw.get("mining_locations")
    return OutsideBody(
        raw["name"].strip(), raw["planet_class"].strip(), raw["volcanism"] if isinstance(raw.get("volcanism"), str) and raw["volcanism"] else None,
        float(radius) if isinstance(radius, (int, float)) and not isinstance(radius, bool) and radius > 0 else None,
        int(count) if isinstance(count, int) and not isinstance(count, bool) and count >= 0 else None)


class BodyCache:
    """Constructed empty; `load(plugin_dir)` is called once from mining_panel.start() and `set_commander` when a commander is known."""

    def __init__(self) -> None:
        self._store = commander_data.new_store()
        self._plugin_dir: Optional[str] = None
        self._cmdr = ""
        self._systems: Dict[str, Dict[str, Any]] = {}

    def load(self, plugin_dir: str) -> None:
        self._plugin_dir = plugin_dir
        self._store = commander_data.read(os.path.join(plugin_dir, STATE_FILENAME), _is_legacy)
        self._cmdr, self._systems = "", {}

    def set_commander(self, cmdr: str) -> None:
        """Switch to this commander's remembered lookups (the previous commander's are already saved)."""
        key = commander_data.key_for(cmdr)
        if not key or key == commander_data.key_for(self._cmdr):
            return
        self._cmdr = str(cmdr).strip()
        try:
            payload = commander_data.payload_for(self._store, self._cmdr, _empty)
            systems = payload.get("systems") if isinstance(payload, dict) else None
            self._systems = {k: v for k, v in systems.items() if isinstance(v, dict)} if isinstance(systems, dict) else {}
        except Exception:
            logger.exception("Could not read %s's remembered body lookups", cmdr)
            self._systems = {}

    def remember(self, system: str, bodies: Sequence[OutsideBody], when: Optional[datetime] = None) -> None:
        """Keep `bodies` as the answer for `system` (replacing the last one), the newest lookup last; nothing is kept for no bodies or no commander."""
        key = _key(system)
        if not key or not self._cmdr or not bodies:
            return
        moment = (when or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        self._systems.pop(key, None)
        self._systems[key] = {"system": str(system).strip(), "asked": moment, "bodies": [dataclasses.asdict(b) for b in list(bodies)[:MAX_BODIES]]}
        while len(self._systems) > MAX_SYSTEMS:
            del self._systems[next(iter(self._systems))]
        self._save()

    def bodies_for(self, system: str) -> List[OutsideBody]:
        """The bodies remembered for `system`, damaged entries skipped; empty when it was never looked up."""
        entry = self._systems.get(_key(system))
        raw = entry.get("bodies") if isinstance(entry, dict) else None
        return [b for b in (_body(item) for item in raw) if b is not None] if isinstance(raw, list) else []

    def asked(self, system: str) -> str:
        """The date (YYYY-MM-DD) of the lookup remembered for `system`, or an empty string."""
        entry = self._systems.get(_key(system))
        return str(entry.get("asked") or "") if isinstance(entry, dict) else ""

    def _save(self) -> None:
        if self._plugin_dir is None or not self._cmdr:
            return
        commander_data.put(self._store, self._cmdr, {"systems": self._systems})
        commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)


cache = BodyCache()
