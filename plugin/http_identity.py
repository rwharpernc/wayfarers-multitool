"""
How WFMT identifies itself to the web services it calls.

Every request carries a User-Agent that names WFMT, its version and where to
find the project, so a service operator who sees traffic can tell what it is
and get in touch. `feature` says which part of WFMT made the request.

Example: "WFMT/1.4.1 (rare-goods; +https://github.com/rwharpernc/wayfarers-multitool)"
"""
from __future__ import annotations

from . import __version__

HOMEPAGE = "https://github.com/rwharpernc/wayfarers-multitool"


def user_agent(feature: str = "") -> str:
    detail = f"{feature}; " if feature else ""
    return f"WFMT/{__version__} ({detail}+{HOMEPAGE})"
