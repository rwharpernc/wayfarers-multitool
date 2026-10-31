"""Written guides for getting what an engineer asks for, one per engineer, shown in the engineer's details on the Engineers tab.

The unlock items of some engineers cannot be bought (Sensor Fragments, items from planetary settlements, scanned data), and the data tables only say in a few
words where each comes from. A guide here says it in full: what to do, in order, where, and what to watch out for. WFMT's own words only, no outside links.

**Adding one.** Add an entry to `GUIDES`, keyed by the engineer's name as `engineers.name_key` writes it (lower case, no nickname): a `Guide(...)` with a one-line
`summary`, the `steps` in order, where it happens (`where`, and a `system` name that the pane links to Inara), `cautions`, and, per item, what to do for just that item
(`items`: item name -> text). Leave `verified` False until the author has done it in the game; the pane then says it is community-reported and not yet confirmed, and
asks for a correction through Report engineer data. Set it True with the date in `updated` once it has been confirmed. `docs/ENGINEER_DATA_COLLECTION.md` says what to
gather and how to check it.

There are no guides yet: an engineer with none shows a line saying so and how to help."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class Guide:
    summary: str                                   # one line: what the player has to do
    steps: Tuple[str, ...] = ()                    # in order
    where: str = ""                                # where it happens, in a few words ("Planet 4 A of an outer system")
    system: str = ""                               # a system name the pane links to Inara ("" for none)
    cautions: Tuple[str, ...] = ()                 # what to watch out for
    items: Tuple[Tuple[str, str], ...] = ()        # (item name, how to get just that item)
    verified: bool = False                         # done and confirmed in the game by the author
    updated: str = ""                              # the date of the last check, as YYYY-MM-DD


GUIDES: Dict[str, Guide] = {}
"""name_key -> Guide. Empty until the guides are written."""


def guide_for(name_key: str) -> Optional[Guide]:
    return GUIDES.get(name_key)
