"""Back up my data (data_backup.py): which files go in the zip, what stays out, where it may be written, and that a failure
never leaves a half archive. The plugin folder is a temporary one; no EDMC stand-ins are needed."""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime
from zipfile import ZipFile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import data_backup as B   # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
NAMES = {"expeditions.json", "system_history.json", "rcc_keys.json", "codex_catalog.json", "notes.json"}
WHEN = datetime(2026, 10, 18, 9, 30, 15)


def write(folder, name, text):
    path = os.path.join(folder, *name.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class BackupTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.plugin = os.path.join(self._tmp.name, "plugins", "WFMT")
        self.dest = os.path.join(self._tmp.name, "Documents")
        os.makedirs(self.plugin)
        os.makedirs(self.dest)
        write(self.plugin, "expeditions.json", '{"a": 1}')
        write(self.plugin, "system_history.json", '{"b": 2}')
        write(self.plugin, "rcc_keys.json", '{"key": "secret"}')
        write(self.plugin, "discord_webhooks.json", '{"url": "https://discord.com/api/webhooks/1/secret"}')
        write(self.plugin, "codex_catalog.json", "{}")
        write(self.plugin, "load.py", "code")                                   # not a data file
        write(self.plugin, "mining_sessions/run1.json", '{"run": 1}')

    def backup(self, **kwargs):
        return B.create_backup(self.plugin, self.dest, "9.9.9", WHEN, names=NAMES, **kwargs)

    def test_the_data_files_are_zipped_with_their_contents(self):
        result = self.backup()
        self.assertTrue(result.ok, result.error)
        self.assertEqual(os.path.basename(result.path), "WFMT-data-20261018-093015.zip")
        with ZipFile(result.path) as archive:
            names = set(archive.namelist())
            self.assertEqual(names, {"expeditions.json", "system_history.json", "mining_sessions/run1.json", B.INFO_NAME})
            self.assertEqual(json.loads(archive.read("expeditions.json")), {"a": 1})

    def test_keys_caches_and_code_are_left_out(self):
        with ZipFile(self.backup().path) as archive:
            names = set(archive.namelist())
        for left_out in ("rcc_keys.json", "discord_webhooks.json", "codex_catalog.json", "load.py"):
            self.assertNotIn(left_out, names)

    def test_the_local_star_index_is_left_out_of_the_backup(self):
        """The index is about 110 MB built from a public download; it is not play data and Settings makes it again."""
        write(self.plugin, "star_index/neutron.wfsi", "index bytes")
        write(self.plugin, "star_index/build/b00.raw", "temporary")
        with ZipFile(self.backup().path) as archive:
            names = set(archive.namelist())
        self.assertEqual({name for name in names if name.startswith("star_index")}, set())
        self.assertNotIn("star_index/neutron.wfsi", B.collect(self.plugin, NAMES))
        with mock.patch.object(B, "EXTRA_DIRS", ("mining_sessions", "star_index")):         # even if a folder were listed as extra by mistake
            self.assertEqual([name for name in B.collect(self.plugin, NAMES) if name.startswith("star_index")], [])

    def test_the_info_file_names_the_version_and_files_but_no_commander(self):
        with ZipFile(self.backup().path) as archive:
            info = json.loads(archive.read(B.INFO_NAME))
        self.assertEqual(info["wfmt_version"], "9.9.9")
        self.assertEqual(sorted(entry["name"] for entry in info["files"]), ["expeditions.json", "mining_sessions/", "system_history.json"])
        self.assertEqual([entry["files"] for entry in info["files"] if entry["name"] == "mining_sessions/"], [1])   # run files carry a commander name
        self.assertIn("rcc_keys.json", info["left_out"])
        self.assertRegex(info["created_utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_a_folder_inside_the_plugin_folder_is_refused(self):
        result = B.create_backup(self.plugin, os.path.join(self.plugin, "mining_sessions"), "9.9.9", WHEN, names=NAMES)
        self.assertFalse(result.ok)
        self.assertIn("outside the WFMT plugin folder", result.error)

    def test_a_missing_folder_is_refused(self):
        result = B.create_backup(self.plugin, os.path.join(self.dest, "nope"), "9.9.9", WHEN, names=NAMES)
        self.assertFalse(result.ok)
        self.assertIn("does not exist", result.error)

    def test_nothing_to_back_up_is_said_not_an_empty_zip(self):
        empty = os.path.join(self._tmp.name, "empty")
        os.makedirs(empty)
        result = B.create_backup(empty, self.dest, "9.9.9", WHEN, names=NAMES)
        self.assertFalse(result.ok)
        self.assertEqual(os.listdir(self.dest), [])

    def test_an_existing_archive_is_never_overwritten(self):
        first = self.backup()
        again = self.backup()
        self.assertTrue(first.ok)
        self.assertFalse(again.ok)
        self.assertEqual(len(os.listdir(self.dest)), 1)

    def test_no_temporary_file_is_left_behind(self):
        self.backup()
        self.assertEqual([name for name in os.listdir(self.dest) if name.endswith(".tmp")], [])

    def test_cancelling_the_folder_dialog_does_nothing(self):
        result = B.run_dialog(self.plugin, "9.9.9", lambda **_kw: "", names=NAMES)
        self.assertIsNone(result.path)
        self.assertEqual(result.error, "")
        self.assertEqual(os.listdir(self.dest), [])

    def test_the_dialog_backs_up_into_the_chosen_folder(self):
        seen = {}

        def ask(**kwargs):
            seen.update(kwargs)
            return self.dest

        result = B.run_dialog(self.plugin, "9.9.9", ask, initial="C:/last", names=NAMES)
        self.assertEqual(seen["initialdir"], "C:/last")
        self.assertEqual(os.path.dirname(result.path), self.dest)

    def test_the_summary_says_what_was_saved(self):
        self.assertIn("Saved 3 files", self.backup().summary())
        self.assertTrue(B.BackupResult(error="boom").summary().startswith("Backup failed"))


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.source = os.path.join(self._tmp.name, "source")
        self.target = os.path.join(self._tmp.name, "target")
        self.dest = os.path.join(self._tmp.name, "Documents")
        for folder in (self.source, self.target, self.dest):
            os.makedirs(folder)
        write(self.source, "expeditions.json", '{"from": "backup"}')
        write(self.source, "notes.json", '{"note": 1}')
        write(self.source, "mining_sessions/run1.json", '{"run": 1}')
        self.zip = B.create_backup(self.source, self.dest, "1.2.3", WHEN, names=NAMES).path
        write(self.target, "expeditions.json", '{"from": "live"}')
        write(self.target, "rcc_keys.json", '{"key": "keep me"}')
        write(self.target, "trade_ledger.json", '{"untouched": true}')

    def read(self, name):
        with open(os.path.join(self.target, *name.split("/")), encoding="utf-8") as handle:
            return handle.read()

    def test_a_backup_is_described_without_unpacking_it(self):
        info = B.inspect_backup(self.zip, names=NAMES)
        self.assertTrue(info.ok, info.error)
        self.assertEqual((info.version, info.files), ("1.2.3", ["expeditions.json", "mining_sessions/run1.json", "notes.json"]))
        self.assertIn("3 files", info.describe())

    def test_staging_touches_nothing_live(self):
        result = B.stage_restore(self.zip, self.target, names=NAMES)
        self.assertTrue(result.ok, result.error)
        self.assertEqual(self.read("expeditions.json"), '{"from": "live"}')
        self.assertTrue(os.path.isfile(os.path.join(self.target, B.PENDING_DIRNAME, B.PENDING_MARKER)))
        self.assertEqual(B.pending_restore(self.target).version, "1.2.3")

    def test_applying_replaces_the_backup_files_and_keeps_the_rest(self):
        B.stage_restore(self.zip, self.target, names=NAMES)
        message = B.apply_pending_restore(self.target, WHEN, names=NAMES)
        self.assertIn("Restored 3 files", message)
        self.assertEqual(self.read("expeditions.json"), '{"from": "backup"}')
        self.assertEqual(self.read("mining_sessions/run1.json"), '{"run": 1}')
        self.assertEqual(self.read("rcc_keys.json"), '{"key": "keep me"}')          # not in the backup: left alone
        self.assertEqual(self.read("trade_ledger.json"), '{"untouched": true}')
        self.assertFalse(os.path.exists(os.path.join(self.target, B.PENDING_DIRNAME)))
        self.assertIsNone(B.pending_restore(self.target))

    def test_the_replaced_files_are_kept_so_a_restore_can_be_undone(self):
        B.stage_restore(self.zip, self.target, names=NAMES)
        B.apply_pending_restore(self.target, WHEN, names=NAMES)
        safety = os.path.join(self.target, B.BACKUPS_DIRNAME, "pre-restore-20261018-093015.zip")
        with ZipFile(safety) as archive:
            self.assertEqual(archive.read("expeditions.json"), b'{"from": "live"}')

    def test_nothing_waiting_does_nothing(self):
        self.assertEqual(B.apply_pending_restore(self.target, WHEN, names=NAMES), "")

    def test_an_unfinished_staging_is_discarded_not_applied(self):
        os.makedirs(os.path.join(self.target, B.PENDING_DIRNAME))
        write(self.target, B.PENDING_DIRNAME + "/expeditions.json", '{"half": true}')     # no ready marker
        self.assertIn("Discarded", B.apply_pending_restore(self.target, WHEN, names=NAMES))
        self.assertEqual(self.read("expeditions.json"), '{"from": "live"}')
        self.assertFalse(os.path.exists(os.path.join(self.target, B.PENDING_DIRNAME)))

    def test_a_cancelled_restore_leaves_no_trace(self):
        B.stage_restore(self.zip, self.target, names=NAMES)
        B.cancel_pending(self.target)
        self.assertIsNone(B.pending_restore(self.target))
        self.assertEqual(B.apply_pending_restore(self.target, WHEN, names=NAMES), "")

    def test_a_zip_that_is_not_a_wfmt_backup_is_refused(self):
        other = os.path.join(self._tmp.name, "other.zip")
        with ZipFile(other, "w") as archive:
            archive.writestr("readme.txt", "hello")
        self.assertIn(B.INFO_NAME, B.inspect_backup(other, names=NAMES).error)
        text = os.path.join(self._tmp.name, "text.zip")
        write(self._tmp.name, "text.zip", "not a zip at all")
        self.assertFalse(B.inspect_backup(text, names=NAMES).ok)
        self.assertFalse(B.inspect_backup(os.path.join(self._tmp.name, "missing.zip"), names=NAMES).ok)

    def test_a_backup_with_a_foreign_or_escaping_file_is_refused_whole(self):
        for bad in ("load.py", "../escape.json", "/abs.json", "sub/dir.json", "mining_sessions/../x.json", "C:evil.json"):
            path = os.path.join(self._tmp.name, "bad.zip")
            with ZipFile(path, "w") as archive:
                archive.writestr(B.INFO_NAME, "{}")
                archive.writestr("notes.json", "{}")
                archive.writestr(bad, "x")
            info = B.inspect_backup(path, names=NAMES)
            self.assertFalse(info.ok, bad)
            result = B.stage_restore(path, self.target, names=NAMES)
            self.assertFalse(result.ok, bad)
            self.assertFalse(os.path.exists(os.path.join(self.target, B.PENDING_DIRNAME)), bad)

    def test_keys_and_caches_in_a_backup_are_refused(self):
        path = os.path.join(self._tmp.name, "keys.zip")
        with ZipFile(path, "w") as archive:
            archive.writestr(B.INFO_NAME, "{}")
            archive.writestr("rcc_keys.json", "{}")
        self.assertFalse(B.inspect_backup(path, names=NAMES).ok)


class AutoBackupTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.plugin = os.path.join(self._tmp.name, "WFMT")
        self.dest = os.path.join(self._tmp.name, "Backups")
        os.makedirs(self.plugin)
        os.makedirs(self.dest)
        write(self.plugin, "notes.json", "{}")

    def run_auto(self, when, days=7, force=False):
        return B.run_auto_backup(self.plugin, self.dest, "1.2.3", days, force=force, now=when, names=NAMES)

    def test_the_first_automatic_backup_is_made_and_named_auto(self):
        result = self.run_auto(datetime(2026, 10, 1, 8, 0, 0))
        self.assertTrue(result.ok, result.error)
        self.assertEqual(os.path.basename(result.path), "WFMT-data-auto-20261001-080000.zip")
        self.assertEqual(B.newest_auto_backup(self.dest), datetime(2026, 10, 1, 8, 0, 0))

    def test_nothing_is_made_until_the_interval_has_passed(self):
        self.run_auto(datetime(2026, 10, 1, 8, 0, 0))
        self.assertIsNone(self.run_auto(datetime(2026, 10, 7, 8, 0, 0)))                  # 6 days
        self.assertTrue(self.run_auto(datetime(2026, 10, 8, 8, 0, 0)).ok)                 # 7 days
        self.assertEqual(len(os.listdir(self.dest)), 2)

    def test_force_backs_up_even_when_one_is_recent(self):
        self.run_auto(datetime(2026, 10, 1, 8, 0, 0))
        self.assertTrue(self.run_auto(datetime(2026, 10, 1, 9, 0, 0), force=True).ok)

    def test_only_the_newest_automatic_backups_are_kept_and_manual_ones_never_deleted(self):
        manual = os.path.join(self.dest, "WFMT-data-20250101-000000.zip")
        write(self.dest, "WFMT-data-20250101-000000.zip", "mine")
        other = os.path.join(self.dest, "holiday.zip")
        write(self.dest, "holiday.zip", "mine too")
        for day in range(1, B.AUTO_KEEP + 4):
            self.run_auto(datetime(2026, 10, day, 8, 0, 0), days=1)
        autos = sorted(name for name in os.listdir(self.dest) if name.startswith(B.AUTO_PREFIX))
        self.assertEqual(len(autos), B.AUTO_KEEP)
        self.assertEqual(autos[-1], "WFMT-data-auto-20261013-080000.zip")
        self.assertTrue(os.path.isfile(manual) and os.path.isfile(other))

    def test_no_folder_means_no_backup(self):
        self.assertIsNone(B.run_auto_backup(self.plugin, "", "1.2.3", 7, names=NAMES))

    def test_a_folder_inside_the_plugin_folder_fails_with_a_reason(self):
        result = B.run_auto_backup(self.plugin, self.plugin, "1.2.3", 7, names=NAMES)
        self.assertFalse(result.ok)
        self.assertIn("outside the WFMT plugin folder", result.error)


class FakeConfig:
    def __init__(self, **values):
        self.values = values

    def get_bool(self, key, default=False):
        return self.values.get(key, default)

    def get_str(self, key):
        return self.values.get(key, "")

    def get_int(self, key, default=0):
        return self.values.get(key, default)


class AutoSettingsTests(unittest.TestCase):
    def test_defaults_are_off(self):
        settings = B.auto_settings(FakeConfig())
        self.assertEqual((settings.enabled, settings.folder, settings.days), (False, "", B.DEFAULT_AUTO_DAYS))

    def test_the_interval_is_kept_between_1_and_90_days(self):
        self.assertEqual(B.auto_settings(FakeConfig(**{B.CFG_AUTO_DAYS: 0})).days, B.DEFAULT_AUTO_DAYS)
        self.assertEqual(B.auto_settings(FakeConfig(**{B.CFG_AUTO_DAYS: 500})).days, 90)
        self.assertEqual(B.auto_settings(FakeConfig(**{B.CFG_AUTO_DAYS: -4})).days, 1)

    def test_switched_off_or_without_a_folder_nothing_runs(self):
        self.assertIsNone(B.run_configured_backup("x", FakeConfig(**{B.CFG_AUTO_FOLDER: "y"}), "1.2.3"))
        self.assertIsNone(B.run_configured_backup("x", FakeConfig(**{B.CFG_AUTO: True}), "1.2.3"))


class ListTests(unittest.TestCase):
    def test_the_restore_folder_is_kept_out_of_the_updaters_backups(self):
        with open(os.path.join(ROOT, "plugin", "update.py"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn(f'"{B.PENDING_DIRNAME}"', source[source.index("_OWN_DIRS ="):])

    def test_left_out_names_are_real_data_files(self):
        """A rename in update.py must not leave a stale exclusion behind (the check reads the source, like test_own_data_files)."""
        with open(os.path.join(ROOT, "plugin", "update.py"), encoding="utf-8") as handle:
            source = handle.read()
        block = source[source.index("_OWN_DATA_FILES: set"):source.index("_OWN_DIRS =")]
        listed = set(re.findall(r'"([^"]+\.(?:json|csv))"', block))
        self.assertEqual(sorted(set(B.LEFT_OUT) - listed), [])

    def test_the_star_index_folder_is_protected_by_the_updater_and_left_out_of_backups(self):
        with open(os.path.join(ROOT, "plugin", "update.py"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn('"star_index"', source[source.index("_OWN_DIRS ="):])
        self.assertIn("star_index", B.LEFT_OUT_DIRS)

    def test_the_mining_archive_folder_matches_the_updaters(self):
        with open(os.path.join(ROOT, "plugin", "mining_session_archive.py"), encoding="utf-8") as handle:
            self.assertIn(f'ARCHIVE_DIRNAME = "{B.EXTRA_DIRS[0]}"', handle.read())


if __name__ == "__main__":
    unittest.main()
