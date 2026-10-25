"""Runs the local star index's download and build on a worker thread, for the Settings page.

`StarIndexJob.start` is called only from a button the user pressed. It downloads the dump (`star_index_download`), builds the index (`star_index_build`), deletes the dump, and reports where it is
through `snapshot()`, which the page reads on a timer; nothing here touches Tkinter. `cancel` stops either step: a cancelled download keeps its partial file so the next press continues it, and
a cancelled or failed build leaves the index that was installed before untouched (the dump is deleted either way, to give the disk space back).

Only one job runs at a time. `delete_index` removes the installed index and any leftover download.
"""
from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Callable, Optional

from . import spansh_courtesy, star_index, star_index_build, star_index_download

logger = logging.getLogger(__name__)

IDLE, DOWNLOADING, BUILDING, DONE, FAILED, CANCELLED = "idle", "downloading", "building", "done", "failed", "cancelled"
ACTIVE = (DOWNLOADING, BUILDING)


@dataclass(frozen=True)
class JobState:
    state: str = IDLE
    fraction: float = 0.0           # 0 to 1 within the current step
    text: str = ""                  # what the step is doing, or how the last job ended

    @property
    def active(self) -> bool:
        return self.state in ACTIVE


class StarIndexJob:
    def __init__(self, directory: Optional[str] = None, courtesy: Optional[spansh_courtesy.Courtesy] = None,
                 free_space: Callable[[str], int] = star_index_download.free_bytes, run_inline: bool = False,
                 clock: Optional[Callable[[], datetime]] = None) -> None:
        self.directory = directory or star_index.default_dir()
        self._courtesy = courtesy
        self._free_space = free_space
        self._run_inline = run_inline        # tests run the work on the calling thread
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._lock = threading.Lock()
        self._state = JobState()
        self._cancel = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # --- what the page reads ---------------------------------------------------------------------------------------
    def snapshot(self) -> JobState:
        with self._lock:
            return self._state

    def _set(self, state: str, fraction: float = 0.0, text: str = "") -> None:
        with self._lock:
            self._state = JobState(state, fraction, text)

    # --- the buttons -------------------------------------------------------------------------------------------------
    def start(self, update: bool = False) -> bool:
        """Starts the download and build. `update` makes the request conditional on the file the installed index was built from. False if a job is already running."""
        with self._lock:
            if self._state.active:
                return False
            self._state = JobState(DOWNLOADING, 0.0, "Starting the download")
            self._cancel = threading.Event()
        if self._run_inline:
            self._run(update)
            return True
        self._thread = threading.Thread(target=self._run, args=(update,), name="WFMT-star-index", daemon=True)
        self._thread.start()
        return True

    def cancel(self) -> None:
        self._cancel.set()

    def delete_index(self) -> str:
        """Deletes the installed index and any partial download. Returns a sentence for the page."""
        if self.snapshot().active:
            return "Cancel the running job first."
        star_index.forget()
        try:
            path = star_index.index_path(self.directory)
            if os.path.isfile(path):
                os.remove(path)
            star_index_download.discard(self.directory)
        except OSError as err:
            return star_index_download.local_problem(err, self.directory)
        self._set(IDLE)
        return "The local star index was deleted. The N.S. button asks Spansh again."

    def _now(self) -> datetime:
        return self._clock()

    def _downloaded(self, done: int, total: int) -> None:
        size = total or star_index_download.EXPECTED_BYTES
        self._set(DOWNLOADING, min(1.0, done / size), f"Downloading: {star_index_download.megabytes(done)} of {star_index_download.megabytes(size)}")

    def _full(self, conditional: bool, installed: star_index.IndexStatus, cancel: threading.Event) -> None:
        """Downloads the full dump and builds the index from it. `conditional` asks the server first whether the dump has changed since the index's lineage began."""
        result = star_index_download.download(self.directory, installed.full_etag if conditional else "", installed.full_modified if conditional else "", cancel,
                                              self._downloaded, self._courtesy, self._free_space)
        if result.not_modified:
            self._set(DONE, 1.0, "The index is already up to date: Spansh's file has not changed since it was built.")
            return
        if self._free_space(self.directory) < star_index_download.BUILD_SPACE_BYTES:
            raise star_index_download.NotEnoughSpace("Not enough free disk space to build the index.")
        source = {"url": star_index_download.DUMP_URL, "etag": result.etag, "last_modified": result.last_modified, "bytes": result.size,
                  "full_etag": result.etag, "full_modified": result.last_modified, "topups": 0}
        self._set(BUILDING, 0.0, "Building the index")
        built = star_index_build.build(result.path, self.directory, source, cancel, lambda fraction, text: self._set(BUILDING, fraction, text))
        self._set(DONE, 1.0, f"Installed: {built.count:,} neutron stars, {star_index_download.megabytes(built.size_bytes)}, built in {built.seconds:.0f} seconds.")

    def _topup(self, installed: star_index.IndexStatus, plan, cancel: threading.Event) -> bool:
        """Brings the index up to date from one of Spansh's small update files. True when that finished the job (updated, or nothing newer); False when the update file cannot be
        trusted to cover the gap, so the caller downloads the full dump instead."""
        url, label = plan
        current = star_index_download.parse_time(installed.source_modified)
        try:
            result = star_index_download.download(self.directory, "", installed.source_modified, cancel, self._downloaded, self._courtesy, self._free_space, url)
            if result.not_modified:
                self._set(DONE, 1.0, f"The index is already up to date: Spansh's {label} file has not changed since {current:%Y-%m-%d %H:%M} UTC.")
                return True
            if self._free_space(self.directory) < star_index_download.BUILD_SPACE_BYTES:
                raise star_index_download.NotEnoughSpace("Not enough free disk space to update the index.")
            source = {"url": url, "etag": result.etag, "last_modified": result.last_modified, "bytes": result.size, "kind": "topup",
                      "full_etag": installed.full_etag, "full_modified": installed.full_modified, "topups": installed.topups + 1}
            self._set(BUILDING, 0.0, "Merging the update into the index")
            built = star_index_build.build(result.path, self.directory, source, cancel, lambda fraction, text: self._set(BUILDING, fraction, text),
                                           topup_from=star_index_download.iso_time(current) if current else "")
            change = built.count - installed.count
            self._set(DONE, 1.0, f"Updated from Spansh's {label} file ({star_index_download.megabytes(result.size)}): {built.changed:,} systems had changed, "
                                 f"{built.added:,} of them with a neutron star as the main star. The index now holds {built.count:,} neutron stars ({change:+,}).")
            return True
        except (star_index_build.TopupGap, star_index.IndexUnusable) as err:
            logger.info("Star index top-up not possible (%s); downloading the full dump", err)
            self._set(DOWNLOADING, 0.0, "The update file does not cover the gap; downloading the full dump instead")
            return False
        finally:
            leftover = os.path.join(self.directory, star_index_download.DUMP_NAME)
            if os.path.isfile(leftover):
                try:
                    os.remove(leftover)
                except OSError:
                    pass

    # --- the work ------------------------------------------------------------------------------------------------------
    def _run(self, update: bool) -> None:
        installed = star_index.status(self.directory)
        cancel = self._cancel
        try:
            if update and installed.usable:
                plan = star_index_download.choose_update(installed.source_modified, installed.topups, installed.full_modified, self._now())
                if plan is not None and self._topup(installed, plan, cancel):
                    return
            self._full(update and installed.usable, installed, cancel)
        except (spansh_courtesy.Cancelled, star_index_build.BuildCancelled):
            self._set(CANCELLED, 0.0, "Cancelled. The index that was installed before is unchanged.")
        except star_index_download.DownloadError as err:
            self._set(FAILED, 0.0, str(err))
        except spansh_courtesy.SpanshBusy as err:
            self._set(FAILED, 0.0, str(err))
        except star_index_build.BuildError as err:
            logger.warning("Star index build failed: %s", err)
            self._set(FAILED, 0.0, f"The index could not be built: {err}. The index that was installed before is unchanged.")
        except OSError as err:
            logger.warning("Star index build failed", exc_info=True)
            self._set(FAILED, 0.0, star_index_download.local_problem(err, self.directory))
        except Exception as err:                                  # noqa: BLE001 - nothing may escape a worker thread unreported
            logger.exception("Star index job failed")
            self._set(FAILED, 0.0, f"Something went wrong ({err}); see EDMarketConnector.log.")
        finally:
            built_or_stopped = os.path.join(self.directory, star_index_download.DUMP_NAME)
            if os.path.isfile(built_or_stopped):
                try:
                    os.remove(built_or_stopped)                    # the dump is only the source of the index
                except OSError:
                    pass
            star_index.forget()


job = StarIndexJob()
"""The one job the Settings page controls."""
