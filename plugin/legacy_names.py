"""
One-time renames of saved names, after British spellings were replaced with American ones.

A commander's saved files and settings from before the change still carry the old spellings: three data files
(`colonisation_*.json`), the `wfmt_colonisation_*` settings, the overlay slot keys for the Colonization card, and the mode key
saved in settings, and the field names `tonnes` and `analysed` inside saved JSON. `migrate` moves each to its new name so nothing is lost. It runs at start-up, after a
pending restore (an old backup brings the old names back), and does nothing when there is nothing to move, so it is safe to run
every time.

Rules:

- A file is renamed when the new name is not there yet. If both exist, the one saved more recently wins (a restore from an old
  backup writes the old name, and it is then newer than the current file); the other is left where it is.
- A setting is copied to the new key only when the new key was never saved, and the old key is then forgotten.
- A JSON field is renamed in place. If a record already has the new field, it keeps it and the old one is dropped.
- Names the game uses (journal events such as `ColonisationContribution`) are not touched: they are not ours to rename.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from . import overlay_profile

logger = logging.getLogger(__name__)

# (old name, new name) of each data file that was renamed.
FILE_RENAMES: Tuple[Tuple[str, str], ...] = (
    ("colonisation_sites.json", "colonization_sites.json"),
    ("colonisation_history.json", "colonization_history.json"),
    ("colonisation_carrier.json", "colonization_carrier.json"),
)

_OLD_SETTING_SUFFIXES = (
    "builds_window_geometry", "group_by_category", "history_window_geometry", "overlay_enabled", "overlay_forced",
    "overlay_right_panel", "overlay_row_limit", "overlay_rows", "overlay_x", "overlay_y", "search_prefs", "window_geometry",
)

# (old key, new key) of each setting that was renamed.
SETTING_RENAMES: Tuple[Tuple[str, str], ...] = tuple(
    (f"wfmt_colonisation_{name}", f"wfmt_colonization_{name}") for name in _OLD_SETTING_SUFFIXES
) + (
    ("wfmt_overlay_place_colonisation", "wfmt_overlay_place_colonization"),
    ("wfmt_overlay_hidden_colonisation", "wfmt_overlay_hidden_colonization"),
    ("wfmt_mode_hidden_colonisation", "wfmt_mode_hidden_colonization"),
)

# Settings whose saved *value* held an old spelling: key -> {old value: new value}.
VALUE_RENAMES: Dict[str, Dict[str, str]] = {"wfmt_active_panel_mode": {"colonisation": "colonization"}}

_SETTING_MAP: Dict[str, str] = dict(SETTING_RENAMES)

# Words that were renamed inside the field names of saved JSON, as (old, new), longest first.
FIELD_RENAMES: Tuple[Tuple[str, str], ...] = (("tonnes", "tons"), ("tonne", "ton"), ("analysed", "analyzed"))

# An old word is only renamed as a whole piece of a field name (the start or end of it, or between underscores), so a key that happens to hold the letters,
# such as a body named after a place, is left alone.
_FIELD_PATTERNS = tuple((re.compile(rf"(?<![A-Za-z0-9]){old}(?![A-Za-z0-9])"), new) for old, new in FIELD_RENAMES)

_MARKERS = tuple(old.encode("ascii") for old, _new in FIELD_RENAMES) + (b"colonisation",)


def legacy_file_names() -> Tuple[str, ...]:
    """The old data file names, so an old backup's files are still recognized when it is restored."""
    return tuple(old for old, _new in FILE_RENAMES)


def new_name(key: str) -> str:
    """The current name of a saved JSON key (a settings key or a field name), or the key itself when it never changed."""
    if key in _SETTING_MAP:
        return _SETTING_MAP[key]
    for pattern, new in _FIELD_PATTERNS:
        key = pattern.sub(new, key)
    return key


def rename_keys(value: Any) -> Tuple[Any, int]:
    """`value` with every dict key renamed by `new_name`, and how many keys changed. A record that already has the new key keeps it."""
    if isinstance(value, dict):
        changed = 0
        out: Dict[Any, Any] = {}
        for key, item in value.items():
            fresh = new_name(key) if isinstance(key, str) else key
            item, inner = rename_keys(item)
            changed += inner
            if fresh != key:
                changed += 1
                if fresh in value:
                    continue            # the new key is already there; it wins
            out[fresh] = item
        return out, changed
    if isinstance(value, list):
        total = 0
        items: List[Any] = []
        for item in value:
            item, inner = rename_keys(item)
            total += inner
            items.append(item)
        return items, total
    return value, 0


def _rename_files(plugin_dir: str) -> List[str]:
    done: List[str] = []
    for old, new in FILE_RENAMES:
        old_path, new_path = os.path.join(plugin_dir, old), os.path.join(plugin_dir, new)
        if not os.path.isfile(old_path):
            continue
        if os.path.exists(new_path):
            try:
                newer = os.path.getmtime(old_path) > os.path.getmtime(new_path)
            except OSError:
                newer = False
            if not newer:
                logger.warning("Both %s and %s exist; keeping %s", old, new, new)
                continue
        try:
            os.replace(old_path, new_path)
            done.append(f"{old} -> {new}")
        except OSError:
            logger.exception("Could not rename %s", old)
    return done


def _rename_json_keys(plugin_dir: str) -> List[str]:
    """Rename the old keys inside every saved JSON file that holds one. Files without one are only read, never rewritten."""
    done: List[str] = []
    try:
        names = sorted(name for name in os.listdir(plugin_dir) if name.endswith(".json"))
    except OSError:
        return done
    for name in names:
        path = os.path.join(plugin_dir, name)
        try:
            with open(path, "rb") as handle:
                raw = handle.read()
            if not any(marker in raw for marker in _MARKERS):
                continue
            data, changed = rename_keys(json.loads(raw.decode("utf-8")))
            if not changed:
                continue
            temp = path + ".tmp"
            with open(temp, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
            os.replace(temp, path)
            done.append(f"{name}: {changed} key(s)")
        except (OSError, ValueError):
            logger.exception("Could not rename the keys in %s", name)
            try:
                os.remove(path + ".tmp")
            except OSError:
                pass
    return done


def _rename_settings(cfg: Any) -> List[str]:
    done: List[str] = []
    for key, values in VALUE_RENAMES.items():
        try:
            value = overlay_profile.read_setting(cfg, key)
            if isinstance(value, str) and value in values:
                overlay_profile.write_setting(cfg, key, values[value])
                done.append(f"{key}: {value} -> {values[value]}")
        except Exception:
            logger.exception("Could not rename the value of %s", key)
    for old, new in SETTING_RENAMES:
        try:
            value = overlay_profile.read_setting(cfg, old)
            if value is None:
                continue
            if overlay_profile.read_setting(cfg, new) is None:
                overlay_profile.write_setting(cfg, new, value)
            overlay_profile.write_setting(cfg, old, None)
            done.append(f"{old} -> {new}")
        except Exception:
            logger.exception("Could not rename the setting %s", old)
    return done


def migrate(plugin_dir: str, cfg: Optional[Any] = None) -> List[str]:
    """Move everything saved under an old name to its new one. Returns a line for each thing moved (empty when nothing was)."""
    done = _rename_files(plugin_dir)
    done += _rename_json_keys(plugin_dir)
    if cfg is not None:
        done += _rename_settings(cfg)
    if done:
        logger.info("Renamed saved names: %s", "; ".join(done))
    return done
