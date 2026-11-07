"""The game's ranks, no Tk: the name of every rank on every ladder and how far the commander is to the next one.

The journal's `Rank` event gives each ladder's rank as a number from 0, and `Progress` gives the percent (0 to 100) toward the next rank. `Promotion`
gives a new rank number alone. This module turns those numbers into the names the game shows.

The names are facts, not code, taken from community references and checked against a commander's own journals: the journal reference at
elite-journal.readthedocs.io ("Ranks") and the Elite Dangerous community wiki's rank tables. The six Pilots Federation ladders have nine names (index 0
to 8, the last being `Elite`) and five prestige tiers above them (`Elite I` to `Elite V`, index 9 to 13; a real journal holds a Trade rank of 13). The
Federation and Empire navy ladders have 15 names (index 0 to 14). In the journal Exploration is `Explore` and the Mercenary ladder is `Soldier`.

Where the sources disagree the game's own wording wins. The journal reference calls Exploration's fifth rank `Explorer`; the wiki, TrueAchievements and
GamePur all give `Trailblazer`, which is what the game shows, so that is used. A name is never shortened or reworded here, and a rank number past the end
of a ladder is shown as `Rank <number>` instead of being guessed.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

ELITE_TIERS: Tuple[str, ...] = ("Elite I", "Elite II", "Elite III", "Elite IV", "Elite V")

Ladder = Tuple[str, str, Tuple[str, ...]]      # (journal key, name shown for the ladder, rank names from index 0)


def _career(*names: str) -> Tuple[str, ...]:
    return names + ELITE_TIERS


# The six Pilots Federation ladders, then the two navies, in the order they are listed.
LADDERS: Tuple[Ladder, ...] = (
    ("Combat", "Combat", _career("Harmless", "Mostly Harmless", "Novice", "Competent", "Expert", "Master", "Dangerous", "Deadly", "Elite")),
    ("Trade", "Trade", _career("Penniless", "Mostly Penniless", "Peddler", "Dealer", "Merchant", "Broker", "Entrepreneur", "Tycoon", "Elite")),
    ("Explore", "Exploration", _career("Aimless", "Mostly Aimless", "Scout", "Surveyor", "Trailblazer", "Pathfinder", "Ranger", "Pioneer", "Elite")),
    ("CQC", "CQC", _career("Helpless", "Mostly Helpless", "Amateur", "Semi Professional", "Professional", "Champion", "Hero", "Legend", "Elite")),
    ("Soldier", "Mercenary", _career("Defenceless", "Mostly Defenceless", "Rookie", "Soldier", "Gunslinger", "Warrior", "Gladiator", "Deadeye", "Elite")),   # game spelling
    ("Exobiologist", "Exobiologist", _career("Directionless", "Mostly Directionless", "Compiler", "Collector", "Cataloguer", "Taxonomist", "Ecologist", "Geneticist", "Elite")),   # game spelling
    ("Federation", "Federation", ("None", "Recruit", "Cadet", "Midshipman", "Petty Officer", "Chief Petty Officer", "Warrant Officer", "Ensign", "Lieutenant",
                                  "Lieutenant Commander", "Post Commander", "Post Captain", "Rear Admiral", "Vice Admiral", "Admiral")),
    ("Empire", "Empire", ("None", "Outsider", "Serf", "Master", "Squire", "Knight", "Lord", "Baron", "Viscount", "Count", "Earl", "Marquis", "Duke", "Prince", "King")),
)

KEYS: Tuple[str, ...] = tuple(key for key, _label, _names in LADDERS)
MAX_TEXT = "max"


def _ladder(key: str) -> Optional[Ladder]:
    return next((ladder for ladder in LADDERS if ladder[0] == key), None)


def names(key: str) -> Tuple[str, ...]:
    """Every rank name on one ladder, from index 0 (empty for a ladder WFMT does not know)."""
    ladder = _ladder(key)
    return ladder[2] if ladder else ()


def _whole(value: Any) -> Optional[int]:
    """A journal number as an int, or None for anything else (a bool is not a rank)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value == int(value):
        return int(value)
    return None


def rank_name(key: str, index: int) -> str:
    """The game's name for a rank. A number past the end of the ladder (a rank added by a later game update) reads `Rank 15`: never a guess."""
    ladder_names = names(key)
    return ladder_names[index] if 0 <= index < len(ladder_names) else f"Rank {index}"


def is_top(key: str, index: int) -> bool:
    """True on the last rank of a ladder: nothing is left to progress toward."""
    ladder_names = names(key)
    return bool(ladder_names) and index >= len(ladder_names) - 1


def percent(progress: Any) -> int:
    """The journal's progress toward the next rank, kept within 0 to 100."""
    value = _whole(progress)
    return 0 if value is None else max(0, min(100, value))


def values_from_entry(entry: Mapping[str, Any]) -> Dict[str, int]:
    """The ladders a `Rank`, `Progress` or `Promotion` event carries, as {journal key: number}. Anything that is not a whole number is left out."""
    found: Dict[str, int] = {}
    for key in KEYS:
        number = _whole(entry.get(key))
        if number is not None:
            found[key] = number
    return found


def values_from_state(state: Any) -> Tuple[Dict[str, int], Dict[str, int]]:
    """(ranks, progress) from EDMC's own state, which holds `Rank` as {ladder: (rank, progress)} once it has seen the game's Rank and Progress events."""
    ranks: Dict[str, int] = {}
    progress: Dict[str, int] = {}
    held = state.get("Rank") if isinstance(state, Mapping) else None
    if isinstance(held, Mapping):
        for key in KEYS:
            pair = held.get(key)
            if isinstance(pair, (tuple, list)) and len(pair) == 2:
                rank, done = _whole(pair[0]), _whole(pair[1])
                if rank is not None:
                    ranks[key] = rank
                    if done is not None:
                        progress[key] = done
    return ranks, progress


def table_rows(ranks: Mapping[str, int], progress: Mapping[str, int]) -> List[Tuple[str, str, str]]:
    """(ladder, rank name, percent to the next rank) for each ladder whose rank is known. The last rank of a ladder reads `max`."""
    rows: List[Tuple[str, str, str]] = []
    for key, label, _names in LADDERS:
        if key not in ranks:
            continue
        index = ranks[key]
        rows.append((label, rank_name(key, index), MAX_TEXT if is_top(key, index) else f"{percent(progress.get(key))}%"))
    return rows


def missing(ranks: Mapping[str, int]) -> Sequence[str]:
    """The ladders with no rank yet (the game has not sent its Rank event for this commander)."""
    return [key for key in KEYS if key not in ranks]


class RankBook:
    """What the journal has said about one commander's ranks: the rank on each ladder and the percent toward the next. A different commander starts empty."""

    def __init__(self) -> None:
        self.cmdr = ""
        self.ranks: Dict[str, int] = {}
        self.progress: Dict[str, int] = {}

    def take(self, entry: Mapping[str, Any], cmdr: str, state: Any = None) -> bool:
        """Take one journal event. Returns True when what is held changed."""
        before = (self.cmdr, dict(self.ranks), dict(self.progress))
        switched = bool(cmdr) and cmdr != self.cmdr
        from_another = switched and bool(self.cmdr)                  # the first commander seen is not a switch: EDMC's state is theirs
        if switched:
            self.cmdr, self.ranks, self.progress = cmdr, {}, {}       # nothing of the last commander's may show on this one's table
        event = entry.get("event")
        found = values_from_entry(entry) if event in ("Rank", "Progress", "Promotion") else {}
        if event == "Rank":
            self.ranks.update(found)
        elif event == "Progress":
            self.progress.update(found)
        elif event == "Promotion":
            for key, number in found.items():
                self.ranks[key] = number
                self.progress[key] = 0                                 # a promotion starts the next rank at 0 percent
        if not self.ranks and not from_another:
            held_ranks, held_progress = values_from_state(state)       # EDMC started after the login: its state still has them
            self.ranks.update(held_ranks)
            self.progress.update(held_progress)
        return before != (self.cmdr, self.ranks, self.progress)

    def rows(self) -> List[Tuple[str, str, str]]:
        return table_rows(self.ranks, self.progress)
