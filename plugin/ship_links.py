"""Links that carry a whole ship loadout: read one a commander pasted, and make one that opens a build in Coriolis or EDSY. Nothing here goes online.

Both sites accept the journal's `Loadout` object inside a link, so the link needs no table of module or blueprint identifiers: the site maps the journal names itself.

- Coriolis: `https://coriolis.io/import?data=<payload>` (`https://beta.coriolis.io/import?data=<payload>` for the beta). Its importer also accepts the payload as a path, `/import/<payload>`.
- EDSY: `https://edsy.org/#/I=<payload>` (`https://edsy.org/beta/#/I=<payload>` for the beta).
- The payload is the loadout as compact JSON with sorted keys (UTF-8), compressed with gzip, then URL-safe base64 with `=` written as `%3D`. Coriolis reads it back with zlib's inflate, so a reader here
  accepts a gzip or a zlib stream.

Links that hold a build's own encoding instead of a loadout (EDSY `#/L=`, Coriolis `/outfit/<ship>?code=`) cannot be read without the sites' identifier tables, and short links need a request to a third-party
service, so both are refused with a message that says which it is. Coriolis refuses a link of 2083 characters or more, so `too_long` tells the caller to warn before a link is copied or opened.

The message of a `LinkError` is shown to the commander in the Ship planner's status line.
"""
from __future__ import annotations

import base64
import binascii
import gzip
import json
import re
import urllib.parse
import zlib
from typing import Any, Dict, Mapping, Optional

CORIOLIS_URL = "https://coriolis.io/import?data="
CORIOLIS_BETA_URL = "https://beta.coriolis.io/import?data="
EDSY_URL = "https://edsy.org/#/I="
EDSY_BETA_URL = "https://edsy.org/beta/#/I="
CORIOLIS_MAX_URL = 2083            # Coriolis shows an error for a link of this many characters or more
MAX_LINK_CHARS = 200_000           # a pasted link longer than this is not read
MAX_LOADOUT_BYTES = 2_000_000      # a payload that inflates to more than this is refused

SHORT_LINK_HOSTS = ("zip1.io", "sh.orbis.zone", "orbis.zone", "ulvis.net", "v.gd", "is.gd", "bit.ly", "tinyurl.com")
_URL = re.compile(r"^\s*https?://", re.IGNORECASE)


class LinkError(ValueError):
    """A pasted link that cannot be read; the message says why in words a commander can act on."""


def loadout_payload(loadout: Mapping[str, Any]) -> str:
    """The payload both sites read: compact sorted JSON, gzip, URL-safe base64, `=` as `%3D`."""
    text = json.dumps(loadout, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    packed = gzip.compress(text, mtime=0)
    return base64.urlsafe_b64encode(packed).decode("ascii").replace("=", "%3D")


def coriolis_url(loadout: Mapping[str, Any], beta: bool = False) -> str:
    return (CORIOLIS_BETA_URL if beta else CORIOLIS_URL) + loadout_payload(loadout)


def edsy_url(loadout: Mapping[str, Any], beta: bool = False) -> str:
    return (EDSY_BETA_URL if beta else EDSY_URL) + loadout_payload(loadout)


def too_long(url: str) -> bool:
    """True when Coriolis would refuse this link for its length."""
    return len(url) >= CORIOLIS_MAX_URL


def looks_like_link(text: Any) -> bool:
    return isinstance(text, str) and bool(_URL.match(text))


def _payload_of(link: str) -> str:
    """The payload in a Coriolis or EDSY link, or a LinkError that says what the link is instead."""
    parts = urllib.parse.urlsplit(link.strip())
    host = (parts.hostname or "").lower()
    if any(host == h or host.endswith("." + h) for h in SHORT_LINK_HOSTS):
        raise LinkError("That is a short link. WFMT does not follow short links (that would ask another website). Open it in your browser and copy the long link, or export the build as SLEF.")
    path, fragment = parts.path, parts.fragment
    if host.endswith("coriolis.io"):
        if path.startswith("/outfit/") or "/outfit" in path:
            raise LinkError("That Coriolis link holds the build in Coriolis's own code, which WFMT cannot read. In Coriolis choose Export and copy the SLEF (or Import link), then paste that.")
        for pair in parts.query.split("&"):                      # not parse_qs: it would turn a base64 "+" into a space
            if pair.startswith("data=") and len(pair) > len("data="):
                return pair[len("data="):]
        if path.startswith("/import/") and len(path) > len("/import/"):
            return path[len("/import/"):]
        raise LinkError("That Coriolis link has no ship in it. Use a link that starts https://coriolis.io/import, or export the build as SLEF.")
    if host.endswith("edsy.org"):
        if fragment.startswith("/I="):
            return fragment[3:]
        if fragment.startswith("/L="):
            raise LinkError("That EDSY link holds the build in EDSY's own code, which WFMT cannot read. In EDSY choose Export, SLEF, and paste that.")
        raise LinkError("That EDSY link has no ship in it. Export the build from EDSY as SLEF and paste that.")
    raise LinkError("WFMT reads links from coriolis.io and edsy.org only. Export the build as SLEF and paste that.")


def _inflate(raw: bytes) -> bytes:
    for wbits in (16 + zlib.MAX_WBITS, zlib.MAX_WBITS):         # gzip, then a plain zlib stream
        try:
            decoder = zlib.decompressobj(wbits)
            out = decoder.decompress(raw, MAX_LOADOUT_BYTES + 1)
            if len(out) > MAX_LOADOUT_BYTES:
                raise LinkError("That link holds more data than a ship loadout can.")
            return out
        except zlib.error:
            continue
    raise LinkError("That link's data could not be unpacked. Copy the whole link and try again.")


def decode_payload(payload: str) -> Any:
    """The JSON a link's payload holds (a loadout object, or a list of SLEF entries)."""
    text = urllib.parse.unquote(payload.strip())
    text += "=" * (-len(text) % 4)
    try:
        raw = base64.urlsafe_b64decode(text.replace("+", "-").replace("/", "_"))
    except (binascii.Error, ValueError):
        raise LinkError("That link's data is not valid. Copy the whole link and try again.") from None
    try:
        return json.loads(_inflate(raw).decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise LinkError("That link does not hold a ship loadout.") from None


def decode_link(link: str) -> Any:
    """The loadout JSON in a pasted Coriolis or EDSY link. Raises LinkError."""
    if not isinstance(link, str) or len(link) > MAX_LINK_CHARS:
        raise LinkError("That is too much text for a link.")
    return decode_payload(_payload_of(link))


def loadout_json_of_link(link: str) -> str:
    """The same as `decode_link`, as JSON text that `ship_plan.parse` reads."""
    return json.dumps(decode_link(link))


def loadout_from_build(ship: str, name: str, modules: Any, ident: Optional[str] = None) -> Dict[str, Any]:
    """A journal-shaped `Loadout` object for a build: the shape both sites import."""
    out: Dict[str, Any] = {"event": "Loadout", "Ship": str(ship or ""), "ShipName": str(name or ""), "Modules": [dict(m) for m in modules if isinstance(m, Mapping)]}
    if ident:
        out["ShipIdent"] = str(ident)
    return out
