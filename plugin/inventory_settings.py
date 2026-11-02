"""Inventory's pickup settings, set in the Inventory window (the Settings → WFMT → Operations → Inventory tab says where they went).

The pillage message format, the pickup sound, which categories announce a pickup, and each suit loadout's backpack capacity are set only there. The window's **Settings** tab (`inventory_settings_tab.SettingsTab`) draws them; this module reads and saves them and tells listeners (`add_listener`):
the panel's listener switches the sound and redraws the bars. The overlay choices (the pillage notifications and bars on the in-game
overlay, and where they sit) stay on the Overlays tab.

The config keys and readers live here so `inventory_window` can use them without importing `inventory_panel`, which imports the window."""
from __future__ import annotations

import json
from typing import Callable, FrozenSet, List, Optional

from config import config

from . import inventory_suit as suit
from .inventory import TRACKED_CATEGORIES

CFG_SOUND_ENABLED = "wfmt_inventory_sound_enabled"
CFG_MESSAGE_FORMAT = "wfmt_inventory_message_format"
CFG_ANNOUNCE_CATEGORIES = "wfmt_inventory_announce_categories"
DEFAULT_MESSAGE_FORMAT = "[{item}] pillaged! New Inventory Total: {total}"

_listeners: List[Callable[[], None]] = []


def add_listener(callback: Callable[[], None]) -> None:
    if callback not in _listeners:
        _listeners.append(callback)


def remove_listener(callback: Callable[[], None]) -> None:
    if callback in _listeners:
        _listeners.remove(callback)


def announce() -> None:
    for callback in list(_listeners):
        try:
            callback()
        except Exception:        # one listener failing must not stop the others
            pass


def sound_enabled() -> bool:
    return config.get_bool(CFG_SOUND_ENABLED, default=False)


def message_format() -> str:
    return config.get_str(CFG_MESSAGE_FORMAT) or DEFAULT_MESSAGE_FORMAT


def announced_categories() -> FrozenSet[str]:
    """Categories whose pickups get a pillage notification (log line, overlay, panel status). Counts are always tracked regardless: this only gates the notification."""
    raw = config.get_str(CFG_ANNOUNCE_CATEGORIES)
    if not raw:
        return frozenset(TRACKED_CATEGORIES)
    try:
        selected = json.loads(raw)
    except (TypeError, ValueError):
        return frozenset(TRACKED_CATEGORIES)
    if not isinstance(selected, list):
        return frozenset(TRACKED_CATEGORIES)
    return frozenset(category for category in selected if category in TRACKED_CATEGORIES)


def set_sound_enabled(on: bool) -> bool:
    config.set(CFG_SOUND_ENABLED, bool(on))
    announce()
    return sound_enabled()


def set_message_format(text: object) -> str:
    """Save the pillage message (blank means the default) and return what is now held."""
    config.set(CFG_MESSAGE_FORMAT, str(text).strip())
    announce()
    return message_format()


def set_announced(category: str, on: bool) -> bool:
    """Turn the pickup notification for one category on or off; returns whether it is on."""
    if category not in TRACKED_CATEGORIES:
        return False
    chosen = set(announced_categories())
    chosen.add(category) if on else chosen.discard(category)
    config.set(CFG_ANNOUNCE_CATEGORIES, json.dumps([c for c in TRACKED_CATEGORIES if c in chosen]))
    announce()
    return category in announced_categories()


def capacity_text(record: dict, category: str) -> str:
    """What a loadout's capacity box shows: the override if there is one, else the unengineered default, else nothing."""
    overrides = record.get("overrides", {})
    if category in overrides:
        return str(overrides[category])
    default = suit.default_capacity(record.get("suit_key", ""), bool(record.get("has_capacity_mod"))).get(category)
    return str(default) if default is not None else ""


def set_capacity(cmdr: str, loadout_id: str, category: str, text: object) -> str:
    """Save one backpack capacity as Settings does: blank, or the unengineered default, clears the override; a number above 0 is kept; anything else leaves it. Returns
    what the box should now show."""
    record = suit.known_loadouts_for(cmdr).get(loadout_id)
    if record is None:
        return str(text)
    value: Optional[int]
    clean = str(text).strip()
    default = suit.default_capacity(record.get("suit_key", ""), bool(record.get("has_capacity_mod"))).get(category)
    if not clean:
        suit.set_override(cmdr, loadout_id, category, None)
    else:
        try:
            value = int(clean)
        except ValueError:
            return capacity_text(record, category)
        if value <= 0:
            return capacity_text(record, category)
        suit.set_override(cmdr, loadout_id, category, None if value == default else value)
    suit.save_overrides()
    announce()
    return capacity_text(record, category)
