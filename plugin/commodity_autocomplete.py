"""Type-ahead for any box that takes a commodity name: `attach(entry, var, preferred)` adds a short list of suggestions under the box as you type, the way `system_autocomplete` does for
system names (it is the same list: Down and Up move through it, Enter or a click takes the highlighted name, Escape closes it, and Enter with nothing highlighted goes on to whatever the
box already did). The names are the game's commodities (`trade_commodities.SUGGESTIBLE`, salvage left out), those that start with what is typed first, then those that contain it, with the
`preferred` names (the commodities of the run, the materials you have saved deposits of) leading each group and alone when the box is empty. Nothing is fetched. No network, no Spansh.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional, Sequence

from . import system_autocomplete, trade_commodities

MAX_SUGGESTIONS = 16


def attach(entry: tk.Entry, var: Optional[tk.StringVar] = None, preferred: Callable[[], Sequence[str]] = lambda: (),
           on_pick: Optional[Callable[[], None]] = None) -> system_autocomplete.Autocomplete:
    """Give `entry` commodity-name suggestions. `preferred()` is asked each time the list opens or the text changes, so it can follow data that changed since the box was built."""
    def provider(text: str) -> List[str]:
        return trade_commodities.suggest(text, preferred(), limit=MAX_SUGGESTIONS)

    return system_autocomplete.attach(entry, var, on_pick, provider=provider)
