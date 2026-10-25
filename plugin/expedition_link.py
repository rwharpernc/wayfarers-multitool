"""The link between a planned expedition (`expedition.py`) and an Expedition Log run (`expedition_log.py`): one start, one Pause, one Stop.

The planner keeps the stops to visit and the log records what happened, so an expedition the commander starts is also a run in the log (when *Start the Expedition Log when I
start an expedition* is ticked, which it is by default). The expedition remembers the run's id (`log_run_id`), and from then on the two always agree:

- **Start** starts the expedition and a new run (or, for an expedition that already has one, reopens it as the log's Resume does). Another expedition that was running is set aside,
  as it always was; its run is paused with it, or stopped when the new expedition gets a run of its own (the log keeps one running at a time).
- **Pause** pauses both; the run's clock stops, and the expedition shows the run's time, so the time paused is in neither.
- **Stop** stops both. Starting the expedition again reopens the run.
- Pressing Pause, Resume or Stop on the log's own row or window does the same to the linked expedition (`_on_log_changed`), and so does starting another run there.

This is the one place that knows both books; the panels and windows call it (nothing else changes one half of a pair). It has no Tk, and the books and the way a run is started are
passed in, so the two panels need not import each other.
"""
from __future__ import annotations

import logging
import os
from typing import Callable, Dict, NamedTuple, Optional

from . import expedition, expedition_log

try:
    from config import appname
except ImportError:  # unit tests outside EDMC
    appname = "EDMarketConnector"

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")


class Started(NamedTuple):
    """What starting an expedition did: the expedition, its log run (None when it has none), and whether that run was a new one."""
    expedition: expedition.Expedition
    run: Optional[expedition_log.Run]
    new_run: bool

    def log_words(self) -> str:
        """The sentence that says what happened in the Expedition Log, or nothing when it was left alone."""
        if self.run is None:
            return ""
        return "Logging in Expedition Log." if self.new_run else "Expedition Log carries on."


class ExpeditionLink:
    def __init__(self, plans: expedition.ExpeditionBook, logs: expedition_log.LogBook,
                 begin_run: Callable[[str], Optional[expedition_log.Run]], enabled: Callable[[], bool]) -> None:
        self._plans = plans
        self._logs = logs
        self._begin_run = begin_run          # starts a run with a name, from where the commander is, in the ship they fly
        self._enabled = enabled              # whether starting an expedition also starts a run
        self._busy = False                   # set while this class is changing both books itself, so its own changes are not read back as the log's
        self._seen: Dict[str, str] = {}      # each linked run's status as of the last change, to tell what changed
        self._remember()
        logs.add_listener(self._on_log_changed)
        plans.add_listener(self._on_plans_changed)

    # --- reading --------------------------------------------------------------------------------------------------------

    def run_of(self, e: expedition.Expedition) -> Optional[expedition_log.Run]:
        """The run the expedition is linked to, or None (it has none, or the commander deleted it from the log)."""
        return self._logs.get(e.log_run_id) if e.log_run_id else None

    def elapsed_text(self, e: expedition.Expedition) -> str:
        """How long the expedition has taken: a linked run's own clock (which does not count the time paused), else the time since it was started."""
        run = self.run_of(e)
        if run is not None:
            return expedition.span_text(run.elapsed())
        return expedition.elapsed_text(e.started, e.finished) if e.started else ""

    # --- the planner's buttons ---------------------------------------------------------------------------------------------

    def start(self, expedition_id: str) -> Started:
        """Start (or resume, or reopen) the expedition, and its log run as the setting says. Raises ExpeditionError when it cannot be started (no stops)."""
        e = self._plans.get(expedition_id)
        if e is None:
            raise expedition.ExpeditionError("That expedition no longer exists.")
        self._busy = True
        try:
            aside = self._plans.active()
            self._plans.start(e.id)
            run, new = self.run_of(e), False
            if run is not None:
                if run.status != expedition_log.RUNNING:
                    run = self._logs.resume(run.id) or run
            elif self._enabled() and self._logs.ready:
                run = self._begin_run(e.name)
                if run is not None:
                    self._plans.set_log_run(e.id, run.id)
                    new = True
            other = self.run_of(aside) if aside is not None and aside is not e else None
            if run is None and other is not None and other.status == expedition_log.RUNNING:
                self._logs.pause(other.id)          # nothing replaces the run of the expedition set aside, so it is held with it (a new run would have stopped it)
            return Started(e, run, new)
        finally:
            self._busy = False
            self._remember()

    def pause(self, expedition_id: str) -> expedition.Expedition:
        e = self._plans.get(expedition_id)
        if e is None:
            raise expedition.ExpeditionError("That expedition no longer exists.")
        self._busy = True
        try:
            self._plans.pause(e.id)
            run = self.run_of(e)
            if run is not None and run.status == expedition_log.RUNNING and e.status == expedition.PAUSED:
                self._logs.pause(run.id)
            return e
        finally:
            self._busy = False
            self._remember()

    def stop(self, expedition_id: str) -> expedition.Expedition:
        e = self._plans.get(expedition_id)
        if e is None:
            raise expedition.ExpeditionError("That expedition no longer exists.")
        self._busy = True
        try:
            self._plans.finish(e.id)
            run = self.run_of(e)
            if run is not None and run.status in (expedition_log.RUNNING, expedition_log.PAUSED):
                self._logs.stop(run.id)
            return e
        finally:
            self._busy = False
            self._remember()

    def reset(self, expedition_id: str) -> expedition.Expedition:
        """Forget the progress. A run still going is stopped (its figures stay in the log) and the expedition lets go of it, so a new start begins a new run."""
        e = self._plans.get(expedition_id)
        if e is None:
            raise expedition.ExpeditionError("That expedition no longer exists.")
        self._busy = True
        try:
            run = self.run_of(e)
            if run is not None and run.status in (expedition_log.RUNNING, expedition_log.PAUSED):
                self._logs.stop(run.id)
            return self._plans.reset(e.id)
        finally:
            self._busy = False
            self._remember()

    # --- the log's own buttons -------------------------------------------------------------------------------------------

    def _remember(self) -> None:
        self._seen = {run.id: run.status for run in self._logs.runs()}

    def _on_plans_changed(self) -> None:
        if not self._busy:
            self._remember()        # a change to the plan alone cannot change a run; this also fills in what was loaded at start-up

    def _on_log_changed(self) -> None:
        """A run changed in the log (Pause, Resume, Stop, or START of another run): carry that over to the expedition linked to it."""
        if self._busy:
            return
        if {run.id: run.status for run in self._logs.runs()} == self._seen:
            return          # a journal event changed a run's figures, not its status: nothing to carry over
        linked = [(e, run) for e in self._plans.expeditions() if e.log_run_id for run in [self._logs.get(e.log_run_id)] if run is not None]
        moves = [(e, run, self._seen.get(run.id)) for e, run in linked]
        self._busy = True
        try:
            # What came into force first (a run that carries on makes its expedition the running one, which sets aside the one that was), then what ended.
            for e, run, before in moves:
                if before is None or run.status == before:
                    continue
                try:
                    if run.status == expedition_log.RUNNING and e.status != expedition.ACTIVE:
                        self._plans.start(e.id)
                    elif run.status == expedition_log.PAUSED and e.status == expedition.ACTIVE:
                        self._plans.pause(e.id)
                except expedition.ExpeditionError:
                    logger.debug("The linked expedition could not follow its run", exc_info=True)
            for e, run, before in moves:
                if before is None or run.status == before or run.status != expedition_log.STOPPED:
                    continue
                # A run that ended while its expedition was already set aside (another was started) leaves it paused; any other end stops it.
                if e.status != expedition.DONE and (before == expedition_log.PAUSED or e.status == expedition.ACTIVE):
                    self._plans.finish(e.id)
        finally:
            self._busy = False
            self._remember()
