"""Checking an engineer's invitation requirement against what the journal says the commander has done. No Tk.

**What can be checked.** Only a requirement the journal records as a number: a rank (the `Rank` event at login and `Promotion` when one changes)
and a lifetime figure (the `Statistics` event at login): the greatest distance from the start, markets and black markets traded with, tons mined,
combat bonds and bounties claimed. About half of the invitation requirements are of these kinds. The rest (a faction's standing, missions of
one kind, selling a data item to a bartender, a rank with a minor faction) are not in the journal as a total, and are left as the table's words
with no mark.

**How fresh it is.** The game writes `Rank` and `Statistics` at login, so a figure is as old as the last login; a promotion is picked up when it
happens, but a lifetime figure such as the markets you have traded with is not. `Progress.at` is the time of the `Statistics` event, so the
window can say so.

**Before the first login this session.** EDMC does not replay a journal's earlier events to a plugin, so a plugin started after the game's login has
not seen `Rank` or `Statistics`. `read_from_journals` finds the commander's newest ones in the newest journal files; `Progress.fill_from` adds them
to what the live events have already given, never replacing a newer figure with an older one.

**Where the numbers come from.** Rank names are the game's, in the order of the journal's numbers (0 for the first). The requirements are the
engineer table's own words restated as a number (`CHECKS`); `tests/test_engineer_requirements.py` checks that the words and the number agree."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

from . import commander_data, journal_files

_ELITE = ("Elite", "Elite I", "Elite II", "Elite III", "Elite IV", "Elite V")    # the journal goes on past Elite: 8 is Elite, 13 is Elite V

RANK_NAMES: Dict[str, Tuple[str, ...]] = {
    "Combat": ("Harmless", "Mostly Harmless", "Novice", "Competent", "Expert", "Master", "Dangerous", "Deadly") + _ELITE,
    "Trade": ("Penniless", "Mostly Penniless", "Peddler", "Dealer", "Merchant", "Broker", "Entrepreneur", "Tycoon") + _ELITE,
    "Explore": ("Aimless", "Mostly Aimless", "Scout", "Surveyor", "Trailblazer", "Pathfinder", "Ranger", "Pioneer") + _ELITE,
    "Federation": ("None", "Recruit", "Cadet", "Midshipman", "Petty Officer", "Chief Petty Officer", "Warrant Officer", "Ensign", "Lieutenant",
                   "Lieutenant Commander", "Post Commander", "Post Captain", "Rear Admiral", "Vice Admiral", "Admiral"),
    "Empire": ("None", "Outsider", "Serf", "Master", "Squire", "Knight", "Lord", "Baron", "Viscount", "Count", "Earl", "Marquis", "Duke", "Prince",
               "King"),
}
RANKS = tuple(RANK_NAMES)

# Our name -> (Statistics section, key). Each is a lifetime number.
STAT_SOURCES: Dict[str, Tuple[str, str]] = {
    "distance_from_start": ("Exploration", "Greatest_Distance_From_Start"),
    "markets_traded": ("Trading", "Markets_Traded_With"),
    "black_markets": ("Smuggling", "Black_Markets_Traded_With"),
    "tons_mined": ("Mining", "Quantity_Mined"),
    "combat_bonds": ("Combat", "Combat_Bonds"),
    "bounties_claimed": ("Combat", "Bounties_Claimed"),
}
STAT_UNITS: Dict[str, str] = {"distance_from_start": " ly", "markets_traded": " markets", "black_markets": " black markets", "tons_mined": " t",
                              "combat_bonds": " combat bonds", "bounties_claimed": " bounty vouchers"}


@dataclass(frozen=True)
class Check:
    kind: str                # "rank" or "stat"
    key: str                 # a RANK_NAMES key, or a STAT_SOURCES key
    value: int               # the rank number, or the figure
    more_than: bool = False  # "more than 50" rather than "at least 50"

    def need(self) -> str:
        if self.kind == "rank":
            return RANK_NAMES[self.key][self.value]
        return ("more than " if self.more_than else "") + f"{self.value:,}{STAT_UNITS.get(self.key, '')}"


@dataclass(frozen=True)
class Result:
    met: Optional[bool]      # None: the journal has not told us yet
    have: str
    need: str

    def describe(self) -> str:
        if self.met is None:
            return f"needs {self.need}; not read from the game yet"
        return f"you have {self.have}: " + ("met" if self.met else f"needs {self.need}")


def _rank(engineer_rank: str, name: str) -> Check:
    return Check("rank", engineer_rank, RANK_NAMES[engineer_rank].index(name))


def _stat(key: str, value: int, more_than: bool = False) -> Check:
    return Check("stat", key, value, more_than)


CHECKS: Dict[str, Check] = {
    "broo tarquin": _rank("Combat", "Competent"),
    "lori jameson": _rank("Combat", "Dangerous"),
    "petra olmanova": _rank("Combat", "Expert"),
    "etienne dorn": _rank("Trade", "Dealer"),
    "didi vatermann": _rank("Trade", "Merchant"),
    "felicity farseer": _rank("Explore", "Scout"),
    "marsha hicks": _rank("Explore", "Surveyor"),
    "ram tah": _rank("Explore", "Surveyor"),
    "hera tani": _rank("Empire", "Outsider"),
    "the sarge": _rank("Federation", "Midshipman"),
    "chloe sedesi": _stat("distance_from_start", 5000),
    "professor palin": _stat("distance_from_start", 5000),
    "elvira martuuk": _stat("distance_from_start", 300),
    "lei cheung": _stat("markets_traded", 50, more_than=True),
    "the dweller": _stat("black_markets", 5),
    "selene jean": _stat("tons_mined", 500),
    "juri ishmaak": _stat("combat_bonds", 50, more_than=True),
    "tod mcquinn": _stat("bounties_claimed", 15, more_than=True),
}
"""The invitation requirement of each engineer the journal can check, by `engineers.name_key`."""


def _whole(value: Any) -> Optional[int]:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0 else None


@dataclass
class Progress:
    """What the journal has said a commander has: ranks (as the journal's numbers) and lifetime figures."""
    ranks: Dict[str, int] = field(default_factory=dict)
    stats: Dict[str, int] = field(default_factory=dict)
    at: str = ""             # when the Statistics event was written (ISO, UTC); empty when none has been seen

    def to_json(self) -> Dict[str, Any]:
        return {"ranks": dict(self.ranks), "stats": dict(self.stats), "at": self.at}

    @classmethod
    def from_json(cls, raw: Any) -> "Progress":
        raw = raw if isinstance(raw, Mapping) else {}
        ranks = {k: n for k, v in (raw.get("ranks") or {}).items() if k in RANK_NAMES and (n := _whole(v)) is not None} \
            if isinstance(raw.get("ranks"), Mapping) else {}
        stats = {k: n for k, v in (raw.get("stats") or {}).items() if k in STAT_SOURCES and (n := _whole(v)) is not None} \
            if isinstance(raw.get("stats"), Mapping) else {}
        at = raw.get("at")
        return cls(ranks, stats, at if isinstance(at, str) else "")

    def apply_event(self, entry: Mapping[str, Any]) -> bool:
        """Take one journal event; True when something changed."""
        kind = entry.get("event")
        before = (dict(self.ranks), dict(self.stats), self.at)
        if kind in ("Rank", "Promotion"):
            for name in RANK_NAMES:
                number = _whole(entry.get(name))
                if number is not None and number < len(RANK_NAMES[name]):
                    self.ranks[name] = number
        elif kind == "Statistics":
            for ours, (section, key) in STAT_SOURCES.items():
                block = entry.get(section)
                number = _whole(block.get(key)) if isinstance(block, Mapping) else None
                if number is not None:
                    self.stats[ours] = number
            stamp = entry.get("timestamp")
            if isinstance(stamp, str):
                self.at = stamp
        return before != (self.ranks, self.stats, self.at)

    @property
    def empty(self) -> bool:
        return not self.ranks and not self.stats

    def fill_from(self, older: "Progress") -> bool:
        """Add what `older` has and this does not (a rank or a figure the live events have not given yet); True when something was added."""
        before = (dict(self.ranks), dict(self.stats), self.at)
        for name, number in older.ranks.items():
            self.ranks.setdefault(name, number)
        for name, number in older.stats.items():
            self.stats.setdefault(name, number)
        self.at = self.at or older.at
        return before != (self.ranks, self.stats, self.at)

    def evaluate(self, check: Check) -> Result:
        if check.kind == "rank":
            number = self.ranks.get(check.key)
            if number is None:
                return Result(None, "", check.need())
            return Result(number >= check.value, RANK_NAMES[check.key][number], check.need())
        figure = self.stats.get(check.key)
        if figure is None:
            return Result(None, "", check.need())
        met = figure > check.value if check.more_than else figure >= check.value
        return Result(met, f"{figure:,}{STAT_UNITS.get(check.key, '')}", check.need())

    def check(self, engineer_key: str) -> Optional[Result]:
        """The result for one engineer (by `engineers.name_key`), or None when their requirement is not one the journal can check."""
        check = CHECKS.get(engineer_key)
        return self.evaluate(check) if check is not None else None


MAX_FILES = 40   # newest journal files looked through


def read_from_journals(cmdr: str, folder: Optional[str] = None, max_files: int = MAX_FILES) -> Progress:
    """The commander's ranks and lifetime figures from the newest journal files, newest first: the newest `Rank` event (and the `Promotion`s since)
    and the newest `Statistics` event. Stops as soon as it has both. Real file reading, so call it off the Tk thread."""
    wanted = commander_data.key_for(cmdr)
    found = Progress()
    if not wanted:
        return found
    have_rank = have_stats = False
    pattern = journal_files.event_pattern("Commander", "LoadGame", "Rank", "Promotion", "Statistics")
    for path in reversed(journal_files.files_modified_since(0.0, folder)[-max_files:]):
        current = ""
        here = Progress()
        saw_rank = saw_stats = False
        for entry in journal_files.read_events(path, pattern):
            kind = entry.get("event")
            if kind == "Commander" and entry.get("Name"):
                current = commander_data.key_for(entry["Name"])
            elif kind == "LoadGame" and entry.get("Commander"):
                current = commander_data.key_for(entry["Commander"])
            elif current == wanted and kind in ("Rank", "Promotion", "Statistics"):
                here.apply_event(entry)                 # in file order, so a later event in the file replaces an earlier one
                saw_rank = saw_rank or kind == "Rank"
                saw_stats = saw_stats or kind == "Statistics"
        if not have_rank:
            found.fill_from(Progress(here.ranks, {}, ""))
            have_rank = saw_rank
        if not have_stats and saw_stats:
            found.fill_from(Progress({}, here.stats, here.at))
            have_stats = True
        if have_rank and have_stats:
            break
    return found
