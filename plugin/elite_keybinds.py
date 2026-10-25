"""Which keyboard combinations Elite Dangerous's own controls use, read from the player's binds file, so a WFMT shortcut can be checked against them.

Elite stores each control as `<Action><Primary Device="Keyboard" Key="Key_C"><Modifier Device="Keyboard" Key="Key_LeftControl"/></Primary>...</Action>`. This reads those into
(action, key, modifiers) and says which of them match a combination. Pure parsing: no Tk and no EDMC; `autohonk.py` finds the binds file (on Windows, and inside the Wine prefix
on Linux) and `tests/test_shortcut_actions.py` covers this.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import FrozenSet, List, Optional

CTRL, ALT, SHIFT = "ctrl", "alt", "shift"

_MODIFIERS = {
    "key_leftcontrol": CTRL, "key_rightcontrol": CTRL,
    "key_leftalt": ALT, "key_rightalt": ALT,
    "key_leftshift": SHIFT, "key_rightshift": SHIFT,
}


@dataclass(frozen=True)
class Binding:
    action: str
    key: str
    modifiers: FrozenSet[str]


def short_key(token: str) -> str:
    """Elite's key token as a short name: Key_C is C, Key_5 is 5, Key_F9 is F9. Anything else (Numpad, arrows, punctuation) keeps its token, which no WFMT shortcut uses."""
    match = re.fullmatch(r"Key_([A-Za-z0-9]|F\d{1,2})", token or "")
    return match.group(1).upper() if match else (token or "")


def parse(xml_text: str) -> List[Binding]:
    """Every keyboard binding in a binds file. A file that is not valid XML gives an empty list."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    found: List[Binding] = []
    for action in root:
        for slot in action:
            if slot.tag not in ("Primary", "Secondary") or slot.get("Device") != "Keyboard" or not slot.get("Key"):
                continue
            modifiers = frozenset(_MODIFIERS[m.get("Key", "").lower()] for m in slot.findall("Modifier")
                                  if m.get("Device") == "Keyboard" and m.get("Key", "").lower() in _MODIFIERS)
            found.append(Binding(action.tag, short_key(slot.get("Key", "")), modifiers))
    return found


def clashes(bindings: List[Binding], key: str, modifiers: FrozenSet[str]) -> List[str]:
    """The names of Elite's controls bound to exactly this key with exactly these modifiers."""
    return sorted({b.action for b in bindings if b.key == key.upper() and b.modifiers == modifiers})


def same_key_elsewhere(bindings: List[Binding], key: str, modifiers: FrozenSet[str]) -> List[str]:
    """Controls on the same key with different modifiers: not a clash (Elite tells the combinations apart), but worth knowing about."""
    return sorted({b.action for b in bindings if b.key == key.upper() and b.modifiers != modifiers})


def load(text_loader=None) -> Optional[List[Binding]]:
    """The player's bindings, or None when the binds file cannot be found or read. `text_loader` returns the file's text (a test passes its own); by default it is the active preset
    found by `autohonk`."""
    if text_loader is None:
        from . import autohonk

        def text_loader() -> Optional[str]:
            path = autohonk._find_active_binds_file()
            if not path:
                return None
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    return handle.read()
            except OSError:
                return None
    text = text_loader()
    return parse(text) if text else None
