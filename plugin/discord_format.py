"""
Discord text for the reports WFMT can share: escaping, bold, links, code blocks, timestamps and splitting a long report into messages.

Pure: no Tk, no network, nothing from EDMC. The reports build their text from their own data with these helpers (see bgs_discord.py and
powerplay_discord.py), so a system or faction name can never turn into formatting or a mention. Copy for Discord and Post to Discord use the
same text. The plain Copy buttons do not use this module: other chat programs, forums and notes get the report without Discord marks.

Discord's limit is 2,000 characters in a message. `split_message` keeps every message under it, breaking between blocks first, then between
lines, and repairing a code block it has to cut so each message opens and closes its own fence.
"""
from __future__ import annotations

import re
from typing import List, Sequence

MESSAGE_LIMIT = 2000
ZERO_WIDTH_SPACE = "​"          # breaks up a mention or a tag without showing; the plain text still reads the same
FENCE = "```"
TIMESTAMP_STYLES = "tTdDfFR"         # short time, long time, short date, long date, short date and time, long date and time, relative

_MARKDOWN = re.compile(r"([\\*_~`|>#\[\]()])")


def escape(text: object) -> str:
    """`text` made safe to put in a Discord message: on one line, with every mark that would format it backslash-escaped, and every `@` and `<`
    followed by an invisible space so it cannot ping anyone or make a tag (`@everyone`, `<@123>`, `<#123>`, `<:name:123>`, `<t:123>`)."""
    flat = " ".join(str(text).split())
    flat = _MARKDOWN.sub(r"\\\1", flat)
    return flat.replace("@", "@" + ZERO_WIDTH_SPACE).replace("<", "<" + ZERO_WIDTH_SPACE)


def bold(text: object) -> str:
    return f"**{escape(text)}**" if str(text).strip() else ""


def italic(text: object) -> str:
    return f"*{escape(text)}*" if str(text).strip() else ""


def link(label: object, url: str) -> str:
    """`[label](<url>)`: the angle brackets keep Discord from adding a preview card. A url that is not http or https leaves just the label."""
    if not re.match(r"https?://", url or ""):
        return escape(label)
    safe = url.replace(" ", "%20").replace("<", "%3C").replace(">", "%3E")
    return f"[{escape(label)}](<{safe}>)"


def code_block(lines: Sequence[object]) -> str:
    """The lines in a fenced block (for aligned columns). A fence inside a line is broken up so it cannot close the block early."""
    body = [str(line).replace(FENCE, "``" + ZERO_WIDTH_SPACE + "`").replace("\r", "") for line in lines]
    return FENCE + "\n" + "\n".join(body) + "\n" + FENCE


def timestamp(epoch: float, style: str = "F") -> str:
    """A Discord time tag: it shows in each reader's own time zone and language. `style` is one of `tTdDfFR` (F is the full date and time, R is
    relative, like "in 10 minutes"). The tag only renders inside Discord, so give the plain time as well when the text may be read elsewhere."""
    if style not in TIMESTAMP_STYLES or len(style) != 1:
        style = "F"
    return f"<t:{int(epoch)}:{style}>"


def _split_long(block: str, limit: int) -> List[str]:
    """One block that does not fit in a message, cut between lines (a line longer than a message is cut too). A code block that is cut is closed at
    the end of each message and opened again at the start of the next."""
    chunk = max(1, limit - 2 * (len(FENCE) + 1))       # room left on a line for a closing and a reopening fence
    pieces: List[str] = []
    for line in block.split("\n"):
        if len(line) > chunk:
            pieces.extend(line[i:i + chunk] for i in range(0, len(line), chunk))
        else:
            pieces.append(line)
    messages: List[str] = []
    current: List[str] = []
    fenced = False
    for piece in pieces:
        before = fenced
        if piece.startswith(FENCE):
            fenced = not fenced
        closing = len("\n" + FENCE) if before else 0
        if current and len("\n".join(current + [piece])) + closing > limit:
            messages.append("\n".join(current) + ("\n" + FENCE if before else ""))
            current = [FENCE] if before else []
        current.append(piece)
    if current:
        messages.append("\n".join(current))
    return messages


def split_message(blocks: Sequence[str], limit: int = MESSAGE_LIMIT) -> List[str]:
    """The blocks (each a piece of the report that reads best kept together, such as one system) joined with newlines into as few messages
    as fit under `limit`. A block is never split unless it is longer than a message on its own. Empty blocks are skipped."""
    messages: List[str] = []
    current = ""
    for block in blocks:
        block = str(block).rstrip("\n")
        if not block.strip():
            continue
        if len(block) > limit:
            if current:
                messages.append(current)
                current = ""
            parts = _split_long(block, limit)
            messages.extend(parts[:-1])
            current = parts[-1]
            continue
        joined = block if not current else current + "\n" + block
        if len(joined) <= limit:
            current = joined
        else:
            messages.append(current)
            current = block
    if current:
        messages.append(current)
    return messages
