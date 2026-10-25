"""What the commander wrote in the Space Mining Book: a note and a favorite star on a ring, and rings added by hand. Kept in `mining_ring_notes.json` beside the plugin, one record per
commander (`commander_data.py`), so two commanders on one install never see each other's. The rings themselves (hotspots, class, reserve level) and the tons mined are not here: they are
rebuilt from the journals (`mining_history.py`, `mining_rings_data.py`). Nothing is sent anywhere. No Tk."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from . import commander_data
from . import mining_rings_data as RD

STATE_FILENAME = "mining_ring_notes.json"
MAX_NOTE = 400


def _is_legacy(_raw: Any) -> bool:
    return False


def _empty() -> Dict[str, Any]:
    return {"rings": {}}


class RingNotes:
    def __init__(self) -> None:
        self._store = commander_data.new_store()
        self._plugin_dir: Optional[str] = None
        self._cmdr = ""

    def start(self, plugin_dir: str) -> None:
        self._plugin_dir = plugin_dir
        self._store = commander_data.read(os.path.join(plugin_dir, STATE_FILENAME), _is_legacy)

    def set_commander(self, cmdr: str) -> None:
        self._cmdr = str(cmdr or "").strip()

    def _rings(self) -> Optional[Dict[str, Any]]:
        if not commander_data.key_for(self._cmdr):
            return None
        payload = commander_data.payload_for(self._store, self._cmdr, _empty)
        if not isinstance(payload, dict) or not isinstance(payload.get("rings"), dict):
            payload = _empty()
            commander_data.put(self._store, self._cmdr, payload)
        return payload["rings"]

    def _save(self) -> None:
        if self._plugin_dir and commander_data.key_for(self._cmdr):
            commander_data.write(os.path.join(self._plugin_dir, STATE_FILENAME), self._store)

    def entries(self) -> Dict[str, Dict[str, Any]]:
        """The commander's notes, favorites and by-hand rings, by ring key (a copy)."""
        rings = self._rings()
        return {key: dict(value) for key, value in (rings or {}).items() if isinstance(value, dict)}

    def _entry(self, key: str) -> Optional[Dict[str, Any]]:
        rings = self._rings()
        if rings is None:
            return None
        entry = rings.setdefault(key, {})
        return entry if isinstance(entry, dict) else rings.setdefault(key, {})

    def _tidy(self, key: str) -> None:
        rings = self._rings()
        if rings is not None and not any(rings.get(key, {}).get(k) for k in ("note", "favorite", "manual")):
            rings.pop(key, None)

    def set_note(self, key: str, note: str) -> bool:
        entry = self._entry(key)
        if entry is None:
            return False
        entry["note"] = " ".join(str(note or "").split())[:MAX_NOTE]
        self._tidy(key)
        self._save()
        return True

    def set_favorite(self, key: str, favorite: bool) -> bool:
        entry = self._entry(key)
        if entry is None:
            return False
        entry["favorite"] = bool(favorite)
        self._tidy(key)
        self._save()
        return True

    def add_manual(self, ring: str, system: str, hotspots: Dict[str, int], ring_class: str = "", reserve: str = "") -> Optional[str]:
        """Add a ring by hand (one the journals have not shown). Returns its key, or None when there is no commander or no ring name."""
        name = " ".join(str(ring or "").split())
        if not name:
            return None
        entry = self._entry(RD.ring_key(name))
        if entry is None:
            return None
        entry["manual"] = {**RD.new_ring(name, system), "hotspots": dict(hotspots), "class": ring_class, "reserve": reserve}
        self._save()
        return RD.ring_key(name)

    def remove_manual(self, key: str) -> bool:
        entry = self._entry(key)
        if entry is None or "manual" not in entry:
            return False
        entry.pop("manual", None)
        self._tidy(key)
        self._save()
        return True


notes = RingNotes()
