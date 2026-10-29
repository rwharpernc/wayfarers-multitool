"""The "Local star index" group on Settings → General → Online lookups: what is installed, and the buttons that download, update, cancel and delete it.

Everything here follows the user: the download starts only from **Download and build** or **Update**, and nothing is requested in the background. The text says plainly what is fetched, from
where, how large it is and how much disk it takes. The work itself runs on `star_index_job.job`'s worker thread; this page polls its `snapshot()` twice a second while it is on screen.
`status_text` and `button_states` are pure functions of what is installed and what the job is doing, so they are tested without a window.
"""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from typing import Dict, Optional, Tuple

import myNotebook as nb
from config import config

from . import star_index, star_index_download, star_index_job

POLL_MS = 500
WRAP = 440

DESCRIPTION = (
    "This is optional: WFMT works fully without it. The N.S. button can answer from a file on this computer instead of asking Spansh each time. Download and build fetches one public file from Spansh's download server "
    "(downloads.spansh.co.uk, " + star_index_download.megabytes(star_index_download.EXPECTED_BYTES) + ", once) and builds an index of the neutron stars from it, about 110 MB on "
    "disk. While it builds it needs about " + str(star_index_download.BUILD_SPACE_BYTES // (1024 * 1024)) + " MB more free space; the downloaded file is deleted afterward. "
    "Nothing is downloaded unless you press a button. Update fetches only what changed: Spansh's small 1-day (about 3 MB) or 1-week (about 19 MB) file of changed systems when your index is "
    "recent enough, and the whole file again only when it is not (or after 20 updates). Pressing it again the same day downloads nothing. "
    "The index lists systems whose main star is a neutron star; a neutron star that is a secondary star is not in it. It is the same for every commander and is not part of Back up my data."
)


def size_text(count: int) -> str:
    return star_index_download.megabytes(count)


def date_text(value: str) -> str:
    """A date for the page from an ISO time ("2026-10-21T06:26:22Z") or an HTTP date ("Wed, 21 Oct 2026 06:26:22 GMT"); the text unchanged when it is neither."""
    for form in ("%Y-%m-%dT%H:%M:%SZ", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.strptime(value, form).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return value


def status_text(installed: star_index.IndexStatus, job: star_index_job.JobState) -> str:
    """The status line: the running step, or what is installed, then how the last job ended."""
    if job.active:
        percent = f" ({round(job.fraction * 100)}%)" if job.state == star_index_job.DOWNLOADING or job.fraction else ""
        return f"{job.text}{percent}"
    if installed.state == "ok":
        built = f", built {date_text(installed.built)}" if installed.built else ""
        source = f" from Spansh's file of {date_text(installed.full_modified or installed.source_modified)}" if (installed.full_modified or installed.source_modified) else ""
        updated = ""
        if installed.topups and installed.source_modified:
            updated = f", up to date as of {date_text(installed.source_modified)} ({installed.topups} update{'s' if installed.topups != 1 else ''} since)"
        line = f"Installed: {installed.count:,} neutron stars, {size_text(installed.size_bytes)}{built}{source}{updated}."
    elif installed.state == "damaged":
        line = f"The installed index cannot be used ({installed.message}), so the N.S. button asks Spansh. Delete it and download again."
    elif installed.state == "old":
        line = f"The installed index was made by another version of WFMT ({installed.message}), so the N.S. button asks Spansh. Press Download and build to make a new one."
    else:
        line = "Not installed. The N.S. button asks Spansh."
    if job.state in (star_index_job.DONE, star_index_job.FAILED, star_index_job.CANCELLED) and job.text and job.text not in line:
        line += "\n" + job.text
    return line


def button_states(installed: star_index.IndexStatus, job: star_index_job.JobState) -> Dict[str, bool]:
    """Which buttons can be pressed: download when nothing usable is installed, update when an index is, cancel while a job runs, delete when there is a file."""
    busy = job.active
    return {
        "download": not busy and installed.state != "ok",
        "update": not busy and installed.state == "ok",
        "cancel": busy,
        "delete": not busy and installed.state != "missing",
    }


class StarIndexGroup:
    """The widgets of the group, placed in `parent` from `row` down."""

    def __init__(self, parent: tk.Misc, row: int, job: Optional[star_index_job.StarIndexJob] = None, directory: Optional[str] = None) -> None:
        self._parent = parent
        self._job = job or star_index_job.job
        self._directory = directory or self._job.directory
        nb.Label(parent, text="Local star index (neutron stars)", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        nb.Label(parent, text=DESCRIPTION, wraplength=WRAP, justify=tk.LEFT).grid(row=row + 1, column=0, sticky=tk.W, padx=10)
        self.status = tk.StringVar(value="")
        nb.Label(parent, textvariable=self.status, wraplength=WRAP, justify=tk.LEFT).grid(row=row + 2, column=0, sticky=tk.W, padx=10, pady=(6, 2))
        buttons = tk.Frame(parent)
        buttons.grid(row=row + 3, column=0, sticky=tk.W, padx=10, pady=2)
        self.buttons: Dict[str, tk.Widget] = {}
        for key, label, command in (("download", "Download and build", self.download), ("update", "Update", self.update),
                                    ("cancel", "Cancel", self.cancel), ("delete", "Delete", self.delete)):
            button = nb.Button(buttons, text=label, command=command)
            button.pack(side=tk.LEFT, padx=(0, 6))
            self.buttons[key] = button
        self.use = tk.BooleanVar(value=bool(config.get_bool(star_index.CONFIG_USE, default=True)))
        nb.Checkbutton(parent, text="Use the local index for Neutron Star when it is installed", variable=self.use, command=self.save).grid(row=row + 4, column=0, sticky=tk.W, padx=10, pady=(4, 0))
        self.message = ""
        self.refresh()
        parent.after(POLL_MS, self._poll)

    # --- the buttons -------------------------------------------------------------------------------------------------
    def download(self) -> None:
        self.message = ""
        self._job.start(update=False)
        self.refresh()

    def update(self) -> None:
        self.message = ""
        self._job.start(update=True)
        self.refresh()

    def cancel(self) -> None:
        self._job.cancel()

    def delete(self) -> None:
        self.message = self._job.delete_index()
        self.refresh()

    def save(self) -> None:
        """The tick takes effect at once (the N.S. button reads it each time), so it is saved when it is changed."""
        config.set(star_index.CONFIG_USE, bool(self.use.get()))

    # --- keeping the page current --------------------------------------------------------------------------------------
    def refresh(self) -> None:
        installed = star_index.status(self._directory)
        job = self._job.snapshot()
        text = status_text(installed, job)
        if self.message and not job.active:
            text += "\n" + self.message
        self.status.set(text)
        for key, enabled in button_states(installed, job).items():
            self.buttons[key]["state"] = tk.NORMAL if enabled else tk.DISABLED

    def _poll(self) -> None:
        try:
            if not self._parent.winfo_exists():
                return
            self.refresh()
            self._parent.after(POLL_MS, self._poll)
        except tk.TclError:
            return


def build_group(parent: tk.Misc, row: int) -> Tuple[StarIndexGroup, int]:
    """Adds the group to `parent` starting at `row`; returns it and the next free row."""
    return StarIndexGroup(parent, row), row + 5
