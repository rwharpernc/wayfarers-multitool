"""Written guides for getting what an engineer asks for, one per engineer, shown in the engineer's details on the Engineers tab.

The unlock items of some engineers cannot be bought (Sensor Fragments, items from planetary settlements, scanned data), and the data tables only say in a few
words where each comes from. A guide here says it in full: what to do, in order, where, and what to watch out for. WFMT's own words only, no outside links.

**Adding one.** Add an entry to `GUIDES`, keyed by the engineer's name as `engineers.name_key` writes it (lower case, no nickname): a `Guide(...)` with a one-line
`summary`, the `steps` in order, where it happens (`where`, and a `system` name that the pane links to Inara), `cautions`, and, per item, what to do for just that item
(`items`: item name -> text). Leave `verified` False until the author has done it in the game; the pane then says it is community-reported and not yet confirmed, and
asks for a correction through Report engineer data. Set it True with the date in `updated` once it has been confirmed. `docs/ENGINEER_DATA_COLLECTION.md` says what to
gather and how to check it.

Engineers without a guide show a line saying so and how to help."""
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


_SENSOR_FRAGMENTS = Guide(
    summary="Collect 25 Sensor Fragments from the wreckage of a crashed Thargoid ship, using your SRV.",
    steps=(
        "Bring a ship with an SRV bay, a Detailed Surface Scanner and a fuel scoop (the sites are far from the Bubble), and an SRV that is repaired and fueled.",
        "Fly to HIP 17403 and orbit planet A 4 a. Map it with the Detailed Surface Scanner until the surface markers show.",
        "Select the Crashed Thargoid Ship marker (about -34.98, -141.41), land as close as the ground allows and launch the SRV.",
        "Drive into the wreckage. Target each Thargoid Sensor and shoot it with the SRV's weapon until it breaks apart into Sensor Fragments.",
        "Target a fragment, lower the SRV's cargo scoop and drive slowly over it. Repeat for every fragment you can see.",
        "If you still need more, drive a short way off, log out to the main menu and log back in. The sensors are reported to return.",
    ),
    where="Planet A 4 a, a crashed Thargoid ship (second site: HIP 17862, planet 6 c, about 30.33, -98.58)",
    system="HIP 17403",
    cautions=(
        "Reported but not confirmed: a fragment goes into your materials, not the cargo racks. Check the count in your materials after the first pickup.",
        "Reported but not confirmed: one sensor drops several fragments. Watch the count after the first one and work out how many pickups you need.",
        "A Thargoid Scavenger at an active Thargoid surface site is another reported source (HIP 14909, planet 2 A), but it shoots back.",
        "A loose Thargoid Sensor in space, in a debris field or at a high-threat Non-Human Signal Source, is reported to drop fragments you scoop with the ship.",
    ),
    items=(("Sensor Fragment", "25 are needed. Only the crash sites above are reported by this guide; check your count in your materials as you go."),),
)

GUIDES: Dict[str, Guide] = {
    "chloe sedesi": _SENSOR_FRAGMENTS,
    "professor palin": _SENSOR_FRAGMENTS,
}
"""name_key -> Guide. Both Sensor Fragment engineers share one guide; the others have none yet."""


def guide_for(name_key: str) -> Optional[Guide]:
    return GUIDES.get(name_key)
