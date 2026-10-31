"""A hook for the plugin's diagnostic log (plugin/diag_log.py) that the window kit can call without importing anything from the plugin: the plugin sets
`listener` when it starts, and the kit calls `emit` at a window opening or closing and a button being pressed. With no listener `emit` does nothing."""
from __future__ import annotations

from typing import Any, Callable, Optional

listener: Optional[Callable[..., None]] = None


def emit(area: str, message: str, **fields: Any) -> None:
    if listener is not None:
        try:
            listener(area, message, **fields)
        except Exception:      # a log line must never break a window
            pass
