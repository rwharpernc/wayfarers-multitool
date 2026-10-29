"""Exploration Dashboard: the Exploration panel's button, and the owner of the window (explore_dashboard_window.py).

The window is for the times you would rather read what WFMT knows than have it drawn over the game. This module is its journal hook and its data supply: it keeps the
newest Status.json, hands the window a `snapshot()` of everything it shows (the system survey, Organic Scanning's view of the body you are at, the running expedition,
the route and the panel readouts, all read from the features that already hold them), and refreshes an open window when something changed (journal events at once,
Status.json at most once a second). It stores nothing and sends nothing.

It also owns the two overlay switches in the window's header. Hiding is `overlay.set_group_hidden` on the cards' id prefixes (`GROUPS`): nothing is written to Settings, so
showing a group again brings back exactly the cards that were switched on. It is not saved either: overlays are shown whenever EDMC starts.
"""
from __future__ import annotations

import logging
import os
import time
import tkinter as tk
from typing import Any, Dict, Mapping, Optional, Tuple

from config import appname

from . import explore_dashboard_data as data
from . import explore_dashboard_window, route_planner_panel, overlay, panelkit

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = "exploration"

REFRESH_DELAY_MS = 150          # journal events often arrive in bursts (a scan and its signals): redraw once after them
POSITION_EVERY_S = 1.0          # Status.json changes about once a second in flight; the position part of the window follows at that pace

# The overlay cards each switch covers, by the prefix of their ids (the cards' GROUP_PREFIX). Flight Alerts and the other non-exploration cards are not touched.
GROUPS: Dict[str, Tuple[str, ...]] = {
    "exploration": ("wfmt_route_", "wfmt_targets_", "wfmt_body_info_", "wfmt_expedition_log_", "wfmt_compass_", "wfmt_discovery_", "wfmt_notable_"),
    "exobiology": ("wfmt_exo_status_", "wfmt_exo_pred_", "wfmt_exo_radar_", "wfmt_exo_popup_"),
}


def summary_text(survey: Any, threshold: int, basis: str) -> str:
    """The line beside the button: where you are in the system, or that nothing is known yet."""
    if not survey.name:
        return "Everything WFMT knows about the system, the body under you and your exploration."
    parts = [survey.name]
    worth = len(survey.to_map(threshold, basis))
    if worth:
        parts.append(f"{worth} worth mapping")
    left = len(survey.with_life())
    if left:
        parts.append(f"{left} with life to do")
    return " · ".join(parts)


class DashboardController:
    def __init__(self) -> None:
        self._parent: Optional[tk.Misc] = None
        self._summary: Optional[tk.StringVar] = None
        self._status: Mapping[str, Any] = {}
        self._pending: Optional[str] = None
        self._last_position = 0.0

    # --- the journal ---------------------------------------------------------------------------------------------------
    def handle_event(self, entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
        self._schedule()

    def dashboard_status(self, entry: Mapping[str, Any]) -> None:
        """Status.json: keep the newest, and let an open window follow the position."""
        self._status = entry
        now = time.monotonic()
        if explore_dashboard_window.is_open() and now - self._last_position >= POSITION_EVERY_S:
            self._last_position = now
            explore_dashboard_window.refresh_position()

    def _schedule(self) -> None:
        """Redraw once shortly after the latest event (and update the panel line)."""
        if self._parent is None or self._pending is not None:
            return
        try:
            self._pending = self._parent.after(REFRESH_DELAY_MS, self._redraw)
        except tk.TclError:
            self._pending = None            # the panel is gone

    def _redraw(self) -> None:
        self._pending = None
        try:
            self._update_summary()
            explore_dashboard_window.refresh()
        except Exception:
            logger.warning("The Exploration Dashboard could not refresh", exc_info=True)

    def _update_summary(self) -> None:
        if self._summary is not None:
            from . import system_survey, targets_overlay
            cfg = targets_overlay.load_config()
            self._summary.set(summary_text(system_survey.survey, cfg.threshold, cfg.basis))

    # --- what the window shows -----------------------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        """Everything the window draws, read from the features that hold it. A source that fails reads as empty, so one broken feature never blanks the dashboard."""
        from . import exobiology_overlay, expedition_log_panel, exploration_value, route_overlay, system_survey, targets_overlay
        cfg = targets_overlay.load_config()
        out: Dict[str, Any] = {"survey": system_survey.survey, "status": self._status, "threshold": cfg.threshold, "basis": cfg.basis,
                               "view": None, "run": None, "route": [], "readouts": ("", "")}
        for key, read in (("view", exobiology_overlay.current_view), ("run", expedition_log_panel.book.active), ("readouts", exploration_value.readouts),
                          ("route", lambda: route_overlay.status_lines(route_overlay.get_state().tracker))):
            try:
                out[key] = read()
            except Exception:
                logger.debug("The Exploration Dashboard could not read %s", key, exc_info=True)
        return out

    # --- the overlay switches ------------------------------------------------------------------------------------------
    @staticmethod
    def overlay_hidden(name: str) -> bool:
        return overlay.group_hidden(name)

    @staticmethod
    def toggle_overlays(name: str) -> bool:
        """Hide the group if it is showing, show it if it is hidden. Returns whether it is hidden now."""
        hidden = not overlay.group_hidden(name)
        overlay.set_group_hidden(name, GROUPS[name], hidden)
        return hidden

    @staticmethod
    def open_neutron() -> None:
        """The Route Planner, from the dashboard's header."""
        route_planner_panel.open_window()

    # --- the panel -----------------------------------------------------------------------------------------------------
    def build_panel(self, parent: tk.Frame) -> None:
        self._parent = parent
        self._summary = tk.StringVar()
        body = panelkit.collapsible_section(parent, "Dashboard", "wfmt_explore_dashboard_collapsed")
        button = tk.Button(body, text="DASHBOARD", command=self._open)
        button.grid(row=0, column=0, sticky=tk.W, pady=(2, 0))
        panelkit.add_tooltip(button, "Open a window with everything WFMT knows about this system, the body you are on, its biology and your exploration so far. "
                                     "Its header buttons switch the exploration and exobiology overlays off and on.")
        panelkit.wrap_label(body, min_wrap=150, textvariable=self._summary, anchor="w", font=panelkit.view_fonts()["small"]).grid(
            row=0, column=1, columnspan=2, sticky=tk.W, padx=(8, 0), pady=(2, 0))
        from . import exploration_value                  # imported here, as in snapshot(), to keep the import cycle out of module load
        exploration_value.build_rows(body, 1)             # the readout lines that used to be a section of their own
        self._update_summary()

    def _open(self) -> None:
        if self._parent is not None:
            explore_dashboard_window.show(self._parent, self)

    def stop(self) -> None:
        explore_dashboard_window.close()


controller = DashboardController()
_hooked = False


def _group_changed(name: str, hidden: bool) -> None:
    explore_dashboard_window.sync_overlays()


def start(plugin_dir: str) -> None:
    """Called once at start-up: lets an open window follow overlay switches made elsewhere."""
    global _hooked
    if not _hooked:
        overlay.on_group_visibility_change(_group_changed)
        _hooked = True


def stop() -> None:
    controller.stop()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    controller.handle_event(entry, cmdr, system, station, state)


def dashboard_status(entry: Dict[str, Any]) -> None:
    controller.dashboard_status(entry)


def build_panel(parent: tk.Frame) -> None:
    controller.build_panel(parent)
