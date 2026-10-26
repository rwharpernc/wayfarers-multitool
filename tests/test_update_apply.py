"""The in-app updater (update.py): a release zip made by scripts/package.mjs has one top-level Wayfarers-Multitool/ folder, which
is stripped so the files land in the plugin folder itself, and trimming the update backups leaves the restore safety zips alone."""
from __future__ import annotations

import os
import sys
import tempfile
import time
import types
import unittest
from unittest import mock
from zipfile import ZipFile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_stub = types.ModuleType("config")
_stub.appname = "EDMarketConnector"
_stub.config = mock.MagicMock()
sys.modules.setdefault("config", _stub)
sys.modules.setdefault("requests", mock.MagicMock())

from plugin import update  # noqa: E402


def _zip(path: str, root: str) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr(f"{root}load.py", "new")
        archive.writestr(f"{root}sub/data.py", "new")


class ApplyTests(unittest.TestCase):
    def _apply(self, root: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = os.path.join(tmp, "plugin")
            os.makedirs(plugin_dir)
            archive = os.path.join(tmp, "release.zip")
            _zip(archive, root)
            update.UpdateManager(plugin_dir, lambda version: None)._apply(archive)
            return ",".join(sorted(os.path.relpath(os.path.join(d, f), plugin_dir).replace(os.sep, "/")
                                   for d, _, files in os.walk(plugin_dir) for f in files))

    def test_the_packaged_folder_name_is_stripped(self):
        self.assertEqual(self._apply("Wayfarers-Multitool/"), "load.py,sub/data.py")

    def test_the_short_folder_name_is_stripped_too(self):
        self.assertEqual(self._apply("WFMT/"), "load.py,sub/data.py")

    def test_a_zip_with_no_top_folder_is_applied_as_is(self):
        self.assertEqual(self._apply(""), "load.py,sub/data.py")


class TrimTests(unittest.TestCase):
    def test_only_update_backups_are_trimmed(self):
        with tempfile.TemporaryDirectory() as tmp:
            backups = os.path.join(tmp, update.BACKUPS_DIRNAME)
            os.makedirs(backups)
            names = [f"2026010{n}-120000.zip" for n in range(1, 6)] + ["pre-restore-20260101-120000.zip", "pre-restore-20260102-120000.zip"]
            for age, name in enumerate(names):
                path = os.path.join(backups, name)
                open(path, "w").close()
                os.utime(path, (time.time() - 1000 + age, time.time() - 1000 + age))
            update.UpdateManager(tmp, lambda version: None)._trim_backups()
            left = sorted(os.listdir(backups))
        self.assertEqual(left, sorted(["20260103-120000.zip", "20260104-120000.zip", "20260105-120000.zip",
                                       "pre-restore-20260101-120000.zip", "pre-restore-20260102-120000.zip"]))


if __name__ == "__main__":
    unittest.main()
