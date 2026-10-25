"""The shortcuts WFMT offers, and how they are named the same way on Windows and Linux.

One list of actions drives everything: the global key combinations (Windows), the chat commands (both systems) and the Settings page. Every key combination is Ctrl+Alt+Shift plus one
key, so the same muscle memory works on both systems and it is a combination Elite's own controls almost never use (`elite_keybinds.py` checks the player's own binds file). A chat
command is `!wf <word>` typed in Elite's chat; the game writes it to the journal as a `SendText` event and WFMT acts on it. Pure logic: no Tk and no EDMC.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from . import elite_keybinds

CHAT_PREFIX = "!wf"
MODIFIER_TEXT = "Ctrl+Alt+Shift+"
OFF = "Off"

LETTERS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = tuple("0123456789")
FUNCTION_KEYS = tuple(f"F{n}" for n in range(1, 13))
KEY_CHOICES = (OFF,) + LETTERS + DIGITS + FUNCTION_KEYS


@dataclass(frozen=True)
class Action:
    id: str
    label: str
    word: str
    """The chat command's word: `!wf center`."""
    default_key: str
    help: str


ACTIONS: Tuple[Action, ...] = (
    Action("center", "Mark the center (CTR)", "center", "C", "Marks the center of the mining location you are at, as CTR does in the Live window."),
    Action("border", "Mark the border (BRD)", "border", "B", "Marks the border of the nearest marked location, as BRD does."),
    Action("rig", "Rig placed", "rig", "R", "Notes the Rhino's position as a mining rig you have just placed, so the radar can show how close the next one may go."),
    Action("zoom", "Radar range", "zoom", "Z", "Steps the Live radar's reach through 50 m, 250 m, 500 m, 1 km and 2 km."),
    Action("live", "Open the Live window", "live", "L", "Opens the Surface Mining Live window, or raises it if it is open."),
    Action("overlays", "Hide or show overlays", "overlays", "O", "Hides every WFMT overlay, or shows them again."),
)

_BY_ID: Dict[str, Action] = {a.id: a for a in ACTIONS}
_BY_WORD: Dict[str, Action] = {a.word: a for a in ACTIONS}


def action(action_id: str) -> Optional[Action]:
    return _BY_ID.get(action_id)


def config_key(action_id: str) -> str:
    return f"wfmt_shortcut_{action_id}_key"


def combo_text(key: str) -> str:
    """"Ctrl+Alt+Shift+C" for a key choice; "Off" for Off."""
    return OFF if key == OFF else MODIFIER_TEXT + key


def clean_key(raw: object, default: str) -> str:
    """A saved key choice, or `default` for anything not a known choice (an empty value, an old setting, a typo)."""
    text = str(raw or "").strip()
    return text if text in KEY_CHOICES else default


def default_keys() -> Dict[str, str]:
    return {a.id: a.default_key for a in ACTIONS}


def duplicate_keys(keys: Dict[str, str]) -> Dict[str, Tuple[str, ...]]:
    """key -> the actions sharing it, for any key more than one action uses (Off is never a duplicate)."""
    seen: Dict[str, list] = {}
    for action_id, key in keys.items():
        if key != OFF:
            seen.setdefault(key, []).append(action_id)
    return {key: tuple(ids) for key, ids in seen.items() if len(ids) > 1}


TRIPLE = frozenset({elite_keybinds.CTRL, elite_keybinds.ALT, elite_keybinds.SHIFT})
"""The modifiers every WFMT combination uses."""


def conflict_text(key: str, picked: Dict[str, str], action_id: str, bindings: Optional[List[elite_keybinds.Binding]]) -> str:
    """What to tell the commander about one key choice: another WFMT action on the same key, or a control of Elite's on exactly that combination; empty when all is well."""
    if key == OFF:
        return ""
    others = [action(other).label for other, other_key in picked.items() if other != action_id and other_key == key]
    if others:
        return f"Also used by: {', '.join(others)}."
    if bindings is not None:
        found = elite_keybinds.clashes(bindings, key, TRIPLE)
        if found:
            return f"Elite already uses {combo_text(key)} for {', '.join(found)}. Pick another key."
    return ""


MOD_ALT, MOD_CONTROL, MOD_SHIFT = 0x1, 0x2, 0x4
"""Windows' RegisterHotKey modifier flags (plain numbers here, so this module stays free of Windows calls)."""


def win_hotkey(key: str) -> Optional[Tuple[int, int]]:
    """(modifier flags, virtual key code) for Ctrl+Alt+Shift plus `key` on Windows; None for Off or anything not a key choice."""
    mods = MOD_CONTROL | MOD_ALT | MOD_SHIFT
    if key in LETTERS or key in DIGITS:
        return mods, ord(key)                       # a letter or digit's virtual key is its capital letter's or digit's character code
    if key in FUNCTION_KEYS:
        return mods, 0x6F + int(key[1:])            # VK_F1 is 0x70
    return None


def is_recent(timestamp: object, now: datetime, max_age_s: float, skew_s: float = 60.0) -> bool:
    """Whether a journal timestamp (`2026-10-20T12:00:00Z`) is no older than `max_age_s` before `now` and not more than `skew_s` ahead of it; False for anything unreadable."""
    if not isinstance(timestamp, str):
        return False
    try:
        moment = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    age = (now - moment).total_seconds()
    return -skew_s <= age <= max_age_s


_CHAT = re.compile(rf"^\s*{re.escape(CHAT_PREFIX)}\s+([a-z]+)\s*$", re.IGNORECASE)


def parse_chat(message: object) -> Optional[Action]:
    """The action a chat message asks for (`!wf center`, any case, nothing else in the message), or None for any other message."""
    match = _CHAT.match(message) if isinstance(message, str) else None
    return _BY_WORD.get(match.group(1).lower()) if match else None
