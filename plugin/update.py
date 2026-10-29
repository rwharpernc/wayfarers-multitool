"""Self-update: checks GitHub Releases for a newer WFMT build, downloads it,
and stages it over the current install (never touching per-mode data files
that aren't part of the distributed release zip; see _OWN_DATA_FILES/
_OWN_DIRS below and scripts/package.mjs).

Runs in a background thread (network I/O) and never touches Tkinter
directly — it hands the new version string to a plain callback, which the
caller marshals onto the main thread (see load.py). Staged files only take
effect on EDMC's next restart; nothing here reloads running code.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import threading
from datetime import datetime
from typing import Callable, Optional, Tuple
from zipfile import ZipFile

import requests
from config import appname, config

from . import __version__, data_backup, http_identity

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

RELEASES_API_URL = "https://api.github.com/repos/rwharpernc/wayfarers-multitool/releases/latest"
RELEASES_PAGE_URL = "https://github.com/rwharpernc/wayfarers-multitool/releases/latest"
REQUEST_TIMEOUT_S = 15
DOWNLOAD_TIMEOUT_S = 60
HEADERS = {"User-Agent": http_identity.user_agent("auto-update")}

CONFIG_AUTO_UPDATE = "wfmt_auto_update"
CONFIG_LAST_VERSION = "wfmt_last_version"

UPDATES_DIRNAME = "updates"
BACKUPS_DIRNAME = "backups"
BACKUPS_KEEP = 3
ZIP_ROOTS = ("Wayfarers-Multitool/", "WFMT/")   # the top-level folder of a release zip
_UPDATE_BACKUP_NAME = re.compile(r"^\d{8}-\d{6}\.zip$")
# Dev handbrake: drop a file with this name in the plugin folder to disable
# auto-update for that install, regardless of the Settings checkbox — e.g.
# for a folder you're actively hand-editing/testing builds in.
DISABLE_SENTINEL = "disable-auto-update.txt"

# Never touched by backup or apply, even though they live inside plugin_dir.
# Each mode's own per-plugin-folder data file (if any) gets added here -
# e.g. a mining hotspot catalog, a survey log.
_OWN_DATA_FILES: set = {
    "sessions.json",  # Powerplay mode's session history (store.py)
    "boxel_state.json",  # Boxel Survey's walker snapshot (boxel_state.py)
    "survey_log.json",  # Boxel Survey's notable-finds log (survey_log.py)
    "boxel_survey_export.csv",  # Boxel Survey's on-demand CSV export
    "region_sweep_state.json",  # Region Sweep's cube queue (region_sweep_state.py)
    "waypoint_route_state.json",  # Waypoint Route's stop list (waypoint_route_state.py)
    "visited_systems.json",  # Boxel Survey's per-commander visited log (visited_systems.py)
    "organic_scan_state.json",  # Organic Scanning's per-body state (organic_scan_state.py)
    "exo_observations.json",  # what lived where, pooled for checking the species prediction; global, no commander named (exo_observations.py)
    "expedition_log.json",  # the Expedition Log's archive of exploration expeditions, per commander (expedition_log.py)
    "system_history.json",  # which systems the commander has been in and scanned in, built from their journals, per commander (system_history.py)
    "system_surveys.json",  # the System targets and Body info cards' saved surveys of each system, per commander (system_survey_store.py)
    "codex_completionist_state.json",  # Codex Completionist's tally (codex_completionist_state.py)
    "income_ledger.json",  # Credits Ledger: income by activity and day (income_ledger.py)
    "session_credits.json",  # Credits this session: the current login's balance record (session_credits.py)
    "bgs_state.json",  # BGS tick ledger, archive, pinned/hidden tabs (bgs_state.py)
    "powerplay_state.json",  # Powerplay per-system ledger, archive, pinned/hidden tabs (powerplay_state.py)
    "mining_hotspots.json",  # Mining's hotspot catalog (mining_hotspots.py)
    "mining_coverage.json",  # Mining's Rhino coverage map (mining_coverage.py)
    "mining_body_cache.json",  # what the Surface Mining Book's Get body info found for each system, per commander (mining_body_cache.py)
    "mining_history.json",  # the Mining History window's runs, built from the journals, per commander (mining_history.py)
    "ship_builds.json",  # Ship Builds list (ship_builds_data.py)
    "stored_modules.json",  # the modules the commander has in storage, per commander (stored_modules.py)
    "codex_catalog.json",  # Codex Completionist's cached Canonn entry catalog (codex_catalog.py)
    "colonization_sites.json",  # Colonization construction sites (colonization_data.py)
    "colonization_carrier.json",  # Colonization's tons transferred to the fleet carrier (colonization_carrier.py)
    "rcc_keys.json",  # each commander's Raven Colonial key (rcc_keys.py)
    "discord_webhooks.json",  # each commander's Discord webhook (discord_webhooks.py)
    "surface_marks.json",  # the commander's surface marks and compass target (surface_marks.py)
    "notes.json",  # the commander's notes on systems and bodies (notes_data.py)
    "materials.json",  # the commander's engineering materials (materials.py)
    "blueprint_wishlist.json",  # the commander's blueprint wishlist (blueprint_wishlist.py)
    "mining_ring_notes.json",  # the Space Mining Book's notes, favorites and rings added by hand, per commander (mining_rings.py)
    "carrier_route.json",  # the Carrier Route planner's plotted route, per commander (carrier_route_state.py)
    "route_planner_route.json",  # the Route Planner's plotted route, per commander (route_planner_state.py)
    "mission_pins.json",  # the missions the commander pinned to the overlay (mission_pins.py)
    "engineers.json",  # the commander's standing with each engineer (engineers.py)
    "expeditions.json",  # the commander's expeditions and their progress (expedition.py)
    "trade_watch.json",  # the commander's market watch list and the prices seen (trade_watch_data.py)
    "colonization_history.json",  # Colonization's record of what the commander delivered (colonization_history.py)
    "trade_ledger.json",  # Trade mode's session ledger (trade_ledger.py)
    "trade_carrier.json",  # Trade mode's fleet/squadron carrier cargo space (trade_carrier.py)
    "trade_route_start.json",  # Trade mode's per-commander route start (trade_route_start.py)
    "trade_stock.json",  # Trade mode's bought-not-yet-sold stock book (trade_stock.py)
    "trade_journal_scan.json",  # which journal files Trade has read (trade_journal_scan.py)
    "trade_history.json",  # Trade mode's saved sessions (trade_history.py)
    "overlay_settings.json",  # each commander's overlay choices: cards, placement, look (overlay_profile.py)
}
_OWN_DIRS = {UPDATES_DIRNAME, BACKUPS_DIRNAME, "mining_sessions", "__pycache__", "restore_pending", "star_index"}  # mining_sessions: mining_session_archive.py; restore_pending: data_backup.py; star_index: star_index.py (the optional local star index, a file WFMT built from a download, shared by every commander)


def _parse_version(value: str) -> Optional[Tuple[int, ...]]:
    try:
        parts = tuple(int(p) for p in value.strip().lstrip("vV").split("."))
    except ValueError:
        return None
    return parts if parts else None


def _pad(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    length = max(len(a), len(b))
    return a + (0,) * (length - len(a)), b + (0,) * (length - len(b))


def check_applied_update() -> Optional[str]:
    """Compares the running version against the version recorded on the
    previous run and records the current one for next time.

    Returns the current version string if it differs from what was
    previously recorded (i.e. a staged update just took effect on this
    restart), or None on the first-ever run or when nothing changed.
    """
    previous = config.get_str(CONFIG_LAST_VERSION)
    config.set(CONFIG_LAST_VERSION, __version__)
    if previous and previous != __version__:
        return __version__
    return None


class UpdateManager:
    """Checks once, downloads/stages at most once, per EDMC run."""

    def __init__(
        self,
        plugin_dir: str,
        on_ready: Callable[[str], None],
        on_downloading: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._plugin_dir = plugin_dir
        self._updates_dir = os.path.join(plugin_dir, UPDATES_DIRNAME)
        self._backups_dir = os.path.join(plugin_dir, BACKUPS_DIRNAME)
        self._on_ready = on_ready
        self._on_downloading = on_downloading

    def check_async(self) -> None:
        if os.path.exists(os.path.join(self._plugin_dir, DISABLE_SENTINEL)):
            logger.info("Auto-update disabled by %s", DISABLE_SENTINEL)
            return
        if not config.get_bool(CONFIG_AUTO_UPDATE, default=False):
            logger.info("Auto-update disabled in Settings")
            return
        threading.Thread(target=self._check, name="WFMT-update-check", daemon=True).start()

    def _check(self) -> None:
        current = _parse_version(__version__)
        if current is None:
            logger.warning("Could not parse current version %r; skipping update check", __version__)
            return

        try:
            resp = requests.get(RELEASES_API_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT_S)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.debug("Update check failed", exc_info=True)
            return

        if data.get("draft") or data.get("prerelease"):
            return

        remote = _parse_version(str(data.get("tag_name", "")))
        if remote is None:
            logger.debug("Could not parse remote version %r", data.get("tag_name"))
            return

        current_p, remote_p = _pad(current, remote)
        if remote_p <= current_p:
            logger.info("WFMT up to date (v%s)", __version__)
            return

        remote_str = ".".join(str(p) for p in remote)
        assets = data.get("assets") or []
        download_url = next(
            (a.get("browser_download_url") for a in assets if str(a.get("name", "")).endswith(".zip")),
            None,
        )
        if not download_url:
            logger.warning("Release v%s has no .zip asset to download", remote_str)
            return

        logger.info("Downloading WFMT v%s (current: v%s)", remote_str, __version__)
        self._download_and_stage(download_url, remote_str)

    def _download_and_stage(self, url: str, version: str) -> None:
        os.makedirs(self._updates_dir, exist_ok=True)
        zip_path = os.path.join(self._updates_dir, "Wayfarers-Multitool.zip")

        if self._on_downloading is not None:
            self._on_downloading(version)

        try:
            resp = requests.get(url, headers=HEADERS, timeout=DOWNLOAD_TIMEOUT_S, stream=True)
            resp.raise_for_status()
            with open(zip_path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=65536):
                    fh.write(chunk)
        except Exception:
            logger.warning("Failed to download v%s update", version, exc_info=True)
            return

        try:
            data_backup.run_configured_backup(self._plugin_dir, config, __version__, force=True)   # the data copy, if switched on
        except Exception:
            logger.warning("Data backup before the update failed", exc_info=True)
        try:
            self._backup_current()
            self._apply(zip_path)
        except Exception:
            logger.warning("Failed to stage v%s update", version, exc_info=True)
            return

        logger.info("WFMT v%s staged — restart EDMC to apply", version)
        self._on_ready(version)

    def _backup_current(self) -> None:
        os.makedirs(self._backups_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(self._backups_dir, f"{stamp}.zip")

        with ZipFile(backup_path, "w") as zf:
            for root, dirs, files in os.walk(self._plugin_dir):
                dirs[:] = [d for d in dirs if d not in _OWN_DIRS]
                for name in files:
                    if name in _OWN_DATA_FILES or name.endswith((".pyc", ".pyo")):
                        continue
                    full = os.path.join(root, name)
                    zf.write(full, os.path.relpath(full, self._plugin_dir))

        self._trim_backups()

    def _trim_backups(self) -> None:
        # Only the update backups: the same folder holds the pre-restore safety zips, which data_backup trims on its own.
        backups = sorted(
            (os.path.join(self._backups_dir, f) for f in os.listdir(self._backups_dir) if _UPDATE_BACKUP_NAME.match(f)),
            key=os.path.getctime,
        )
        for stale in backups[:-BACKUPS_KEEP]:
            try:
                os.remove(stale)
            except OSError:
                logger.debug("Could not remove stale backup %s", stale, exc_info=True)

    def _inside_plugin_dir(self, target: str) -> bool:
        """Guards against a zip entry ("../x", an absolute path, another drive
        on Windows) writing outside the plugin folder."""
        root = os.path.normpath(self._plugin_dir)
        try:
            return os.path.commonpath([root, target]) == root
        except ValueError:  # e.g. a different drive on Windows
            return False

    def _apply(self, zip_path: str) -> None:
        with ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            # Release zips contain a top-level Wayfarers-Multitool/ folder (see
            # scripts/package.mjs), so strip it — plugin_dir *is* that
            # folder already.
            prefix = next((p for p in ZIP_ROOTS if names and all(n.startswith(p) for n in names)), "")

            for member in zf.infolist():
                relative = member.filename[len(prefix):] if prefix and member.filename.startswith(prefix) else member.filename
                if not relative or relative in _OWN_DATA_FILES:
                    continue

                target = os.path.normpath(os.path.join(self._plugin_dir, relative))
                if not self._inside_plugin_dir(target):
                    logger.warning("Skipping update entry outside the plugin folder: %r", member.filename)
                    continue
                if member.is_dir():
                    os.makedirs(target, exist_ok=True)
                    continue

                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(member) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
