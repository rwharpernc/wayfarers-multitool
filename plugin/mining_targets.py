"""The commodities chosen as mining targets in Settings → WFMT → Mining, read from the one text box that holds them. Pure Python: no Tk, no network, no EDMC.

The box takes one or several commodities separated by commas or semicolons, each optionally followed by the least percent of a rock that makes it worth cracking:
"Painite 30, Platinum 25, Void Opals". A name with no number uses the single percentage beside the box (`default_percent`), so a box holding one plain name behaves exactly as it
did when the box held only one. Names are compared through `mining_names.normalize`, so every spelling of a commodity is one target. A typed name that is not a known commodity is
accepted, since the box has always allowed that.

`parse_targets` also says what is wrong with the text, in short sentences for the Settings page: a percentage that is not a number from 1 to 100, a name listed twice, more than
MAX_TARGETS names. An entry with a bad percentage is left out, not guessed at.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Tuple

from .mining_names import normalize

DEFAULT_TARGET_PERCENT = 20
TARGET_PERCENT_RANGE = (1, 100)
MAX_TARGETS = 8
"""The most targets used; further names in the box are ignored (and the Settings page says so)."""

_NAME_SHOWN = 30
"""A name longer than this is cut when it is quoted in a message, so a stray paste cannot make a long line."""

_SEPARATORS = re.compile(r"[,;]")
_NUMBER = re.compile(r"^(\d+(?:\.\d+)?)%?$")


@dataclass(frozen=True)
class Target:
    name: str          # as typed (spaces tidied)
    percent: float     # the least share of a rock that counts as a hit

    @property
    def key(self) -> str:
        """The name in its one canonical spelling, what a rock's materials are compared with."""
        return normalize(self.name)


@dataclass(frozen=True)
class ParsedTargets:
    targets: Tuple[Target, ...]
    problems: Tuple[str, ...]


def _short(name: str) -> str:
    return name if len(name) <= _NAME_SHOWN else name[:_NAME_SHOWN - 1].rstrip() + "…"


def parse_targets(text: Any, default_percent: float = DEFAULT_TARGET_PERCENT) -> ParsedTargets:
    """The targets in `text` (at most MAX_TARGETS) and the problems found in it."""
    targets: List[Target] = []
    problems: List[str] = []
    seen = set()
    low, high = TARGET_PERCENT_RANGE
    for piece in _SEPARATORS.split(str(text or "")):
        words = piece.split()
        if not words:
            continue
        percent = float(default_percent)
        last = words[-1]
        if len(words) > 1 and (any(ch.isdigit() for ch in last) or last.endswith("%")):
            number = _NUMBER.match(last)
            name = " ".join(words[:-1])
            if number is None or not low <= float(number.group(1)) <= high:
                problems.append(f"{_short(name)}: the percentage must be a number from {low} to {high}.")
                continue
            percent = float(number.group(1))
        else:
            name = " ".join(words)
        if not any(ch.isalpha() for ch in name):
            problems.append(f"\"{_short(name)}\" is not a commodity name.")
            continue
        key = normalize(name)
        if key in seen:
            problems.append(f"{_short(name)} is listed twice: the first is used.")
            continue
        if len(targets) >= MAX_TARGETS:
            problems.append(f"Only the first {MAX_TARGETS} targets are used.")
            break
        seen.add(key)
        targets.append(Target(" ".join(name.split()), percent))
    return ParsedTargets(tuple(targets), tuple(problems))


def last_item(text: str) -> str:
    """The item being typed: what follows the last comma or semicolon, tidied."""
    return " ".join(_SEPARATORS.split(text)[-1].split())


class LastItemVar:
    """Stands in for the box's text variable when the commodity type-ahead is attached: the suggestions are made for the last item being typed, and taking one replaces only that item,
    keeping what came before it. Only `get` and `set` are used by the type-ahead, so this needs no Tk of its own. With one name in the box it reads and writes the whole text, as before."""

    def __init__(self, var: Any) -> None:
        self._var = var

    def get(self) -> str:
        return last_item(str(self._var.get()))

    def set(self, name: str) -> None:
        text = str(self._var.get())
        cut = max(text.rfind(","), text.rfind(";"))
        self._var.set(name if cut < 0 else text[:cut + 1] + " " + name)
