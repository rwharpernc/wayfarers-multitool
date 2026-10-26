"""The "My Projects" window: every active project the commander has on Raven Colonial, across systems, not only the sites WFMT has seen
them dock at. Opened from the panel's PROJECTS button or the Raven Colonial menu of the Colonization Sites window.

Each row shows the project, its system, the building (the game's name and the build type Raven knows it by), how much is delivered and
how many tons are still needed. A project is *counted* unless it is on the commander's hidden list on Raven Colonial; the line under
the title adds up the counted ones and the trips they take in the ship the commander is flying. Double-click a row, or use the
button, to count or stop counting it; **Save Counted List** writes that to Raven Colonial (which other tools read too, so it asks
first). **Set as My Primary** makes the picked project the commander's primary one there.

Reading needs no key and no switch. The two writes need the Raven key and the master switch, as everything WFMT writes does. A worker
thread does the three reads and the Tk thread polls for the answer; an older answer is dropped. What the rows are and how they add up
is in rcc_projects.py; this file only draws them.
"""
from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
import webbrowser
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set

from config import appname, config

from . import panelkit, rcc_client, rcc_keys, rcc_projects as projects
from .uikit import dialogs, palette as P
from .uikit.shell import WindowShell
from .uikit.table import Column, DataTable

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CONFIG_GEOMETRY = "wfmt_colonization_projects_window_geometry"
MIN_WIDTH = 800
MIN_HEIGHT = 380
DEFAULT_SIZE = (940, 520)
_POLL_MS = 150
_NAME_MAX = 60

_COLUMNS = (
    Column("counted", "Count", 60, anchor="center", max_chars=6),
    Column("name", "Project", 200, stretch=True, max_chars=40),
    Column("system", "System", 170, stretch=True, max_chars=32),
    Column("building", "Building", 230, max_chars=44),
    Column("done", "Done", 70, anchor="e", max_chars=8),
    Column("needed", "Still needed", 100, anchor="e", max_chars=12),
    Column("note", "Note", 90, max_chars=12),
)
_HELP = (
    ("Source", "These come from Raven Colonial (ravencolonial.com), a community site, for your commander name. Only that name is sent to read them."),
    ("Count", "A project is counted unless it is on your hidden list on Raven Colonial. Double-click a row to change it, then Save Counted List "
              "to keep the change there. Other tools that read the list, such as SrvSurvey, see the same one."),
    ("Note", "Primary is your primary project on Raven Colonial. Here marks a site WFMT also tracks from your journal."),
    ("Writing", "Saving the list and setting your primary project need your Raven Colonial key and the master switch in Settings → Colonization."),
)

_window: Optional["ProjectsWindow"] = None


def show(parent: tk.Misc, cmdr: Callable[[], str], tracked: Callable[[], FrozenSet[int]], capacity: Callable[[], int]) -> None:
    """Open the window, or refresh and raise it if it is open. `cmdr` gives the commander now, `tracked` the market ids of the sites
    WFMT tracks for them, and `capacity` the ship's cargo capacity (0 when unknown)."""
    global _window
    if _window is not None and _window.alive:
        _window.refresh()
        _window.lift()
        return
    _window = ProjectsWindow(parent, cmdr, tracked, capacity)


def refresh_cmdr() -> None:
    """The commander changed: an open window follows them."""
    if _window is not None and _window.alive:
        _window.refresh()


def close() -> None:
    if _window is not None and _window.alive:
        _window.close()


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


class ProjectsWindow:
    def __init__(self, parent: tk.Misc, cmdr: Callable[[], str], tracked: Callable[[], FrozenSet[int]], capacity: Callable[[], int]) -> None:
        self._cmdr = cmdr
        self._tracked = tracked
        self._capacity = capacity
        self._request_id = 0
        self._views: List[rcc_client.RccProjectView] = []
        self._hidden: Set[str] = set()
        self._saved_hidden: Set[str] = set()     # the list as Raven last gave it, to tell what has changed here
        self._primary = ""
        self._loaded_for = ""
        self._shell = WindowShell(
            parent, "My Projects", "", size=DEFAULT_SIZE, min_size=(MIN_WIDTH, MIN_HEIGHT),
            load_geometry=lambda: config.get_str(CONFIG_GEOMETRY) or "",
            save_geometry=lambda geometry: config.set(CONFIG_GEOMETRY, geometry))
        self._shell.add_help("My Projects help", _HELP)
        self._shell.window.protocol("WM_DELETE_WINDOW", self.close)
        self._shell.add_action("Refresh", self.refresh, accent=True)
        self._shell.add_action("Count / Don't Count", self._on_toggle)
        self._shell.add_menu("More", [
            ("Copy Shopping List", self._on_copy),
            None,
            ("Open Project on Raven", self._on_open),
            ("Open My Projects on Raven", lambda: webbrowser.open(rcc_client.WEB_URL + "/build")),
            None,
            ("Set as My Primary…", self._on_set_primary),
            ("Save Counted List…", self._on_save_hidden)])
        self._table = DataTable(self._shell.body, _COLUMNS, sortable=False, on_activate=self._toggle_row,
                                empty_text="No projects yet.")
        self._table.tag_configure("done", foreground=P.MUTED)
        self._table.tag_configure("off", foreground=P.MUTED)
        self._table.pack(fill="both", expand=True, pady=(0, P.PAD_SM))
        self._shell.set_status("")
        self.refresh()

    @property
    def alive(self) -> bool:
        return self._shell.alive

    def lift(self) -> None:
        self._shell.window.deiconify()
        self._shell.window.lift()

    # --- reading ---------------------------------------------------------------------------------------

    def refresh(self) -> None:
        """Read the commander's projects, hidden list and primary project on a worker thread and poll for the answer."""
        if not self.alive:
            return
        cmdr = (self._cmdr() or "").strip()
        self._request_id += 1
        job: Dict[str, Any] = {"id": self._request_id, "done": False, "error": "", "views": [], "hidden": [], "primary": ""}
        if not cmdr:
            self._views, self._hidden, self._saved_hidden, self._primary, self._loaded_for = [], set(), set(), "", ""
            self._table.clear()
            self._shell.set_subtitle("No commander yet")
            self._shell.set_status("WFMT does not know your commander yet; log in to the game first.")
            return
        self._shell.set_subtitle(f"{_clip(cmdr, _NAME_MAX)} - asking Raven Colonial…")

        def work() -> None:
            try:
                job["views"] = rcc_client.fetch_active(cmdr)
                job["hidden"] = rcc_client.fetch_hidden(cmdr)
                job["primary"] = rcc_client.fetch_primary(cmdr)
            except rcc_client.RccError as err:
                job["error"] = str(err)
            except Exception:
                logger.exception("Raven Colonial project lookup failed")
                job["error"] = "The lookup failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-projects").start()
        self._shell.window.after(_POLL_MS, self._poll, job, cmdr)

    def _poll(self, job: Dict[str, Any], cmdr: str) -> None:
        if not self.alive or job["id"] != self._request_id:
            return
        if not job["done"]:
            self._shell.window.after(_POLL_MS, self._poll, job, cmdr)
            return
        if job["error"]:
            self._shell.set_subtitle(f"{_clip(cmdr, _NAME_MAX)} - not available")
            self._shell.set_status(job["error"])
            return
        self._views, self._primary, self._loaded_for = job["views"], job["primary"], cmdr
        self._hidden = set(job["hidden"])
        self._saved_hidden = set(job["hidden"])
        self._shell.set_status("")
        self._render()

    # --- drawing ---------------------------------------------------------------------------------------

    def _rows(self) -> List[projects.Row]:
        return projects.rows(self._views, self._hidden, self._primary, self._tracked())

    def _render(self) -> None:
        shown = self._rows()
        selected = self._table.selection()
        self._table.clear()
        for row in shown:
            view = row.view
            note = "Primary" if row.primary else ("Here" if row.tracked else "")
            tag = "done" if view.complete else (None if row.counted else "off")
            self._table.insert(
                view.build_id, ("✓" if row.counted else "", view.name or "(unnamed)", view.system, projects.building_label(view),
                                "100%" if view.complete else f"{projects.progress(view):.0%}",
                                "complete" if view.complete else f"{view.sum_need:,} t", note), tag=tag)
        if selected and self._table.exists(selected[0]):
            self._table.select(selected[0])
        self._update_subtitle(shown)

    def _update_subtitle(self, shown: List[projects.Row]) -> None:
        counted, tons, trips = projects.totals(shown, self._capacity())
        facts = [f"{len(shown)} project{'s' if len(shown) != 1 else ''}"]
        if shown:
            facts.append(f"{counted} counted need {tons:,} t")
            if trips:
                facts.append(f"{trips:,} trip{'s' if trips != 1 else ''} in your ship")
        if self._hidden != self._saved_hidden:
            facts.append("unsaved changes to the counted list")
        self._shell.set_subtitle(f"{_clip(self._loaded_for, _NAME_MAX)} - " + " · ".join(facts))

    # --- actions on the picked row -----------------------------------------------------------------------

    def _picked(self) -> Optional[projects.Row]:
        picked = self._table.selection()
        return projects.find(self._rows(), picked[0] if picked else None)

    def _toggle_row(self, build_id: str) -> None:
        if projects.find(self._rows(), build_id) is None:
            return
        self._hidden = projects.toggled(self._hidden, build_id)
        self._render()

    def _on_toggle(self) -> None:
        row = self._picked()
        if row is None:
            self._shell.set_status("Select a project first.")
            return
        self._toggle_row(row.view.build_id)

    def _on_copy(self) -> None:
        row = self._picked()
        if row is None:
            self._shell.set_status("Select a project first.")
            return
        if panelkit.copy_to_clipboard(self._shell.window, projects.shopping_text(row.view)):
            self._shell.set_status(f"Copied the shopping list for {row.view.name or 'the project'}.")

    def _on_open(self) -> None:
        row = self._picked()
        if row is None:
            self._shell.set_status("Select a project first.")
            return
        webbrowser.open(rcc_client.build_page_url(row.view.build_id))
        self._shell.set_status(f"Opened {row.view.name or 'the project'} on Raven Colonial in your browser.")

    # --- the two writes --------------------------------------------------------------------------------

    def _write_key(self) -> str:
        """The commander's Raven key when a write may go ahead, else "" (the reason is in the status line). Asks for it when none is saved;
        it is kept only once a write has worked."""
        cmdr = self._loaded_for
        if not rcc_keys.enabled():
            self._shell.set_status("Sending to Raven Colonial is switched off. Turn it on in Settings → Colonization → Raven Colonial.")
            return ""
        if not cmdr:
            self._shell.set_status("Refresh first, so WFMT knows which commander this is.")
            return ""
        key = rcc_keys.keys.get(cmdr)
        if not key:
            entered = dialogs.prompt(
                self._shell.window, "Raven Colonial key", f"Paste {cmdr}'s Raven Colonial key. It is saved for this commander only and sent "
                "only to Raven Colonial.", show="*")
            key = (entered or "").strip()
        return key

    def _write(self, label: str, action: Callable[[str], Any], done: Callable[[Any], str]) -> None:
        """Run one write (`action` is given the key) on a worker thread, then say what happened (and keep the key, which has now been accepted)."""
        cmdr, key = self._loaded_for, self._write_key()
        if not key:
            return
        job: Dict[str, Any] = {"done": False, "error": "", "result": None}
        self._shell.set_status(f"{label}…")

        def work() -> None:
            try:
                job["result"] = action(key)
                rcc_keys.keys.set(cmdr, key)
            except rcc_client.RccError as err:
                job["error"] = str(err)
            except Exception:
                logger.exception("Raven Colonial write failed")
                job["error"] = "The update failed unexpectedly; see the EDMC log."
            job["done"] = True

        threading.Thread(target=work, daemon=True, name="WFMT-rcc-projects-write").start()
        self._poll_write(job, done)

    def _poll_write(self, job: Dict[str, Any], done: Callable[[Any], str]) -> None:
        if not self.alive:
            return
        if not job["done"]:
            self._shell.window.after(_POLL_MS, self._poll_write, job, done)
            return
        if job["error"]:
            self._shell.set_status(_clip(job["error"], 200))
            return
        self._shell.set_status(done(job["result"]))

    def _on_set_primary(self) -> None:
        row = self._picked()
        if row is None:
            self._shell.set_status("Select a project first.")
            return
        cmdr, view = self._loaded_for, row.view
        if not dialogs.confirm(self._shell.window, "Set primary project",
                               f"Make {view.name or 'this project'} in {view.system} your primary project on Raven Colonial?"):
            return

        def action(key: str) -> None:
            rcc_client.set_primary(cmdr, view.build_id, key)

        def done(_result: Any) -> str:
            self._primary = view.build_id
            self._render()
            return f"{view.name or 'The project'} is now your primary project on Raven Colonial."

        self._write("Telling Raven Colonial", action, done)

    def _on_save_hidden(self) -> None:
        if self._hidden == self._saved_hidden:
            self._shell.set_status("The counted list has not changed here, so there is nothing to save.")
            return
        cmdr, wanted = self._loaded_for, sorted(self._hidden)
        if not dialogs.confirm(
                self._shell.window, "Save the counted list",
                f"Replace your hidden list on Raven Colonial with this one ({len(wanted)} hidden)?\n\nIt is your list there, so other tools "
                "that read it, such as SrvSurvey, will see the change too."):
            return

        def action(key: str) -> List[str]:
            return rcc_client.save_hidden(cmdr, wanted, key)

        def done(saved: Any) -> str:
            self._hidden = set(saved)
            self._saved_hidden = set(saved)
            self._render()
            return "Raven Colonial now has your counted list."

        self._write("Saving the counted list", action, done)

    def close(self) -> None:
        self._request_id += 1      # an answer still on its way has nowhere to show
        self._shell.close()
