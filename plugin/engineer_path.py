"""The path to unlocking one engineer, in order: any engineers to deal with first, then find them, reach them, earn the invitation and
unlock them, with each step marked done from where the commander stands (`engineers.EngineerBook`). No Tk.

**Where the steps come from.** `engineers.Info` holds how to find an engineer, what earns the invitation and what unlocks them, as the
community table words them. The steps are those texts, not a re-reading of them. The only thing read out of the text is which *engineers* it
names: "From Hera Tani (grade 3-4)" in how to find, or the three engineers a referral task is done for in what earns the invitation. Each is an
engineer to deal with first, and so on down the chain, so Tiana Fortune's path starts with Liz Ryder, then Hera Tani.

**On-foot engineers.** For a ship engineer the table's "unlock" is what to hand *them* to unlock them. For an on-foot (Odyssey) engineer it is what to
hand them to learn of the *next* engineer (Provide Domino Green 5 Push to learn of Kit Fowler), so it is a step on the path of the engineer who
comes after, and an on-foot engineer has no unlock step of their own. The last in a chain (Yarden Bond, Oden Geiger, Uma Laszlo, Yi Shen) hands
nothing over, which is why the table leaves theirs empty.

**What is marked done.** Only what the journal's `EngineerProgress` says: *Known* means found, *Invited* means found and invited, *Unlocked* means
every step. The game does not report permits or the requirements for an invitation, so those steps are never marked done until the engineer is
invited or unlocked."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from . import engineers

FIND, REFER, REACH, INVITE, UNLOCK = "find", "refer", "reach", "invite", "unlock"
MAX_DEPTH = 6
"""The longest referral chain in the table is three engineers; the limit only stops a table that loops."""


@dataclass(frozen=True)
class Step:
    kind: str                # find, refer, reach, invite or unlock
    text: str
    done: bool


@dataclass(frozen=True)
class Path:
    name: str
    steps: Tuple[Step, ...]
    first: Tuple["Path", ...] = field(default_factory=tuple)      # engineers to deal with before this one, in order
    unlocked: bool = False

    @property
    def next_step(self) -> Optional[Step]:
        """The first step not done yet (None when there is nothing left)."""
        return next((s for s in self.steps if not s.done), None)


def _named_in(text: str, own_key: str) -> List[str]:
    """The engineers (as the table names them) that `text` mentions, in the order they appear, never the engineer themselves."""
    folded = text.casefold()
    found = []
    for key, info in engineers.INFO.items():
        if key == own_key:
            continue
        match = re.search(rf"(?<!\w){re.escape(key)}(?!\w)", folded)
        if match:
            found.append((match.start(), info.name))
    return [name for _at, name in sorted(found)]


def referrers(name: str) -> List[str]:
    """The engineers named in how to find `name` (those who refer to them), in the order the table names them."""
    info = engineers.info(name)
    return _named_in(info.find, engineers.name_key(name)) if info is not None else []


def prerequisites(name: str) -> List[str]:
    """The engineers to deal with before `name`: those who refer to them, and those a referral task is done for."""
    info = engineers.info(name)
    if info is None:
        return []
    own = engineers.name_key(name)
    ordered: List[str] = []
    for text in (info.find, info.invite):
        for other in _named_in(text, own):
            if other not in ordered:
                ordered.append(other)
    return ordered


def _progress(book: Optional[engineers.EngineerBook], name: str) -> str:
    standing = book.standing(name) if book is not None else None
    return standing.progress if standing is not None else ""


def build(name: str, book: Optional[engineers.EngineerBook] = None, _seen: Tuple[str, ...] = ()) -> Optional[Path]:
    """The path to unlock `name`, or None when the table does not have them. `book` is where the commander stands; without it nothing is done."""
    info = engineers.info(name)
    if info is None:
        return None
    progress = _progress(book, name)
    unlocked = progress == engineers.UNLOCKED
    invited = unlocked or progress == engineers.INVITED
    found = invited or progress == engineers.KNOWN
    steps: List[Step] = []
    if info.find:
        steps.append(Step(FIND, f"Find them: {info.find}", found))
    for other in referrers(name):
        giver = engineers.info(other)
        if giver is not None and giver.on_foot and giver.unlock:
            steps.append(Step(REFER, f"To learn of {info.name}, give {giver.name} the items: {giver.unlock}", found))
    if info.permit:
        steps.append(Step(REACH, f"Hold the {info.system} permit to reach {info.base}.", unlocked))
    if info.invite:
        steps.append(Step(INVITE, f"Earn the invitation: {info.invite}", invited))
    if info.unlock and not info.on_foot:
        steps.append(Step(UNLOCK, f"Unlock them: {info.unlock}", unlocked))
    first: List[Path] = []
    key = engineers.name_key(name)
    if not unlocked and len(_seen) < MAX_DEPTH:
        for other in prerequisites(name):
            if engineers.name_key(other) in _seen or engineers.name_key(other) == key:
                continue
            sub = build(other, book, _seen + (key,))
            if sub is not None:
                first.append(sub)
    return Path(info.name, tuple(steps), tuple(first), unlocked)


def order(path: Path) -> List[Path]:
    """Every engineer on the way, deepest first and the engineer asked about last, each once, leaving out those already unlocked on the way."""
    seen: List[str] = []
    result: List[Path] = []

    def visit(item: Path, top: bool) -> None:
        for sub in item.first:
            visit(sub, False)
        key = engineers.name_key(item.name)
        if key not in seen and (top or not item.unlocked):
            seen.append(key)
            result.append(item)

    visit(path, True)
    return result


def next_action(path: Path) -> Optional[Tuple[Path, Step]]:
    """What to do next towards unlocking `path.name`: the engineer to deal with and the step. It is the first step not done on the way,
    taking the engineers to deal with first in order. A find step counts only when nothing else is left, since for most engineers it reads
    "Common knowledge" and says nothing to do."""
    stops = order(path)
    for stop in stops:
        for step in stop.steps:
            if not step.done and step.kind != FIND:
                return stop, step
    for stop in stops:
        for step in stop.steps:
            if not step.done:
                return stop, step
    return None


def render(path: Path) -> str:
    """The path as lines of text: a heading per engineer in the order to deal with them, then their numbered steps with `[done]` on those done."""
    lines: List[str] = []
    stops = order(path)
    if path.unlocked:
        return f"{path.name}: unlocked. Nothing left to do."
    if len(stops) > 1:
        lines.append(f"{path.name} takes {len(stops)} engineers, in this order: " + ", then ".join(p.name for p in stops) + ".")
    for stop in stops:
        lines.append(f"{stop.name}:")
        for number, step in enumerate(stop.steps, 1):
            lines.append(f"  {number}. {step.text}" + (" [done]" if step.done else ""))
    return "\n".join(lines)
