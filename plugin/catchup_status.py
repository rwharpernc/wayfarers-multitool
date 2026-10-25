"""A line in the WFMT panel that says when WFMT is reading your journals to catch up, so a pause is not a mystery.

The first time a commander is followed, or after a long gap, features read old journals on a worker thread (Powerplay, the BGS replay, the
Codex rebuild). `begin` and `end` bracket each of those; the line shows the names of the ones still running, and only once one has
run for `SHOW_AFTER_MS`, so the quick everyday reads (a second or less) never flash it. Nothing is stored."""
from __future__ import annotations

import time
import tkinter as tk
from typing import Dict, List

SHOW_AFTER_MS = 1500

_running: Dict[str, float] = {}     # task name -> time.monotonic() when it began, in the order begun
_labels: List[tk.Label] = []


def begin(task: str) -> None:
    _running[task] = time.monotonic()
    _schedule_update(SHOW_AFTER_MS + 50)


def end(task: str) -> None:
    _running.pop(task, None)
    _schedule_update(0)


def text(now: float = 0.0) -> str:
    """The panel line: the tasks that have run long enough to mention, or "" when there is nothing to say."""
    now = now or time.monotonic()
    shown = [name for name, started in _running.items() if (now - started) * 1000 >= SHOW_AFTER_MS]
    if not shown:
        return ""
    return f"Reading your journals to catch up ({', '.join(shown)}). This happens once and can take a minute."


def build_panel_line(parent: tk.Misc, row: int) -> tk.Label:
    """The line in the WFMT panel; it takes no room while there is nothing to say."""
    from . import panelkit
    label = panelkit.wrap_label(parent, anchor="w", fg="gray")
    label.grid(row=row, column=0, columnspan=3, sticky=tk.W)
    _labels.append(label)
    _apply(label)
    return label


def _apply(label: tk.Label) -> None:
    message = text()
    if message:
        label.configure(text=message)
        label.grid()
    else:
        label.grid_remove()


def _schedule_update(delay_ms: int) -> None:
    for label in list(_labels):
        try:
            label.after(delay_ms, lambda lab=label: _apply(lab))
        except (tk.TclError, RuntimeError):
            _labels.remove(label)
