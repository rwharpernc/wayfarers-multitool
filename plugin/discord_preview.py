"""
An approximation of how Discord shows a message, for the customize dialog's preview. Pure (no Tk): `segments(text)` turns a message's markdown into (text, tags) pieces
that a Tk Text widget can draw.

It handles only what WFMT's posts use: `**bold**`, `*italic*`, a `[label](<url>)` link (shown as its label), a backslash that escapes the next mark, and a `- ` bullet line (shown
with a bullet, a nested one indented). Discord's own rendering is the truth; this is close enough to judge a layout and the length of a post.
"""
from __future__ import annotations

import re
from typing import List, Tuple

Segment = Tuple[str, Tuple[str, ...]]

_TOKEN = re.compile(r"\\(.)|\*\*(.+?)\*\*|\*(.+?)\*|\[([^\]]*)\]\(<[^>]*>\)", re.DOTALL)
_BULLET = re.compile(r"^( *)- ")


def _inline(text: str, tags: Tuple[str, ...]) -> List[Segment]:
    pieces: List[Segment] = []
    position = 0
    for match in _TOKEN.finditer(text):
        if match.start() > position:
            pieces.append((text[position:match.start()], tags))
        escaped, bold, italic, link = match.groups()
        if escaped is not None:
            pieces.append((escaped, tags))
        elif bold is not None:
            pieces.extend(_inline(bold, tags + ("bold",)))
        elif italic is not None:
            pieces.extend(_inline(italic, tags + ("italic",)))
        else:
            pieces.append((link, tags + ("link",)))
        position = match.end()
    if position < len(text):
        pieces.append((text[position:], tags))
    return pieces


def segments(text: str) -> List[Segment]:
    """The message as (text, tags) pieces with its newlines kept, where tags are any of "bold", "italic" and "link"."""
    result: List[Segment] = []
    lines = text.split("\n")
    for index, line in enumerate(lines):
        bullet = _BULLET.match(line)
        if bullet:
            result.append((("    " if bullet.group(1) else "") + "• ", ()))
            line = line[bullet.end():]
        result.extend(_inline(line, ()))
        if index < len(lines) - 1:
            result.append(("\n", ()))
    return [(piece, tags) for piece, tags in result if piece]
