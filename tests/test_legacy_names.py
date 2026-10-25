"""
Unit tests for plugin/legacy_names.py: saved names from before the spelling fix are moved to their new names, once, and nothing
that is already current is overwritten.

Pure logic - no EDMC runtime needed. Run with:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import legacy_names  # noqa: E402


class FakeConfig:
    """Just enough of EDMC's config: strings and numbers kept apart, refusing the wrong type like the real one does."""

    def __init__(self, **values):
        self.values = dict(values)

    def get_str(self, key, default=None):
        value = self.values.get(key, default)
        if value is not None and not isinstance(value, str):
            raise ValueError("not a string")
        return value

    def get_int(self, key, default=0):
        value = self.values.get(key, default)
        if isinstance(value, str):
            raise ValueError("not an int")
        return value

    def set(self, key, value):
        self.values[key] = value

    def delete(self, key, suppress=False):
        self.values.pop(key, None)


def _write(folder: str, name: str, data) -> str:
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    return path


def _read(folder: str, name: str):
    with open(os.path.join(folder, name), encoding="utf-8") as handle:
        return json.load(handle)


class RenameKeysTests(unittest.TestCase):
    def test_renames_words_inside_keys_at_every_depth(self) -> None:
        data, changed = legacy_names.rename_keys(
            {"commanders": {"a": {"tonnes": {"steel": 4}, "log": [{"profit_per_tonne": 9, "analysed": ["x"]}]}}})
        self.assertEqual(data, {"commanders": {"a": {"tons": {"steel": 4}, "log": [{"profit_per_ton": 9, "analyzed": ["x"]}]}}})
        self.assertEqual(changed, 3)

    def test_leaves_current_names_and_values_alone(self) -> None:
        original = {"tons": 3, "name": "tonnes of steel", "analyzed": []}
        data, changed = legacy_names.rename_keys(original)
        self.assertEqual((data, changed), (original, 0))

    def test_only_whole_words_in_a_key_are_renamed(self) -> None:
        original = {"Hartonnes A 1": 1, "santonne": 2, "analysedish": 3}          # names that merely hold the letters
        data, changed = legacy_names.rename_keys(original)
        self.assertEqual((data, changed), (original, 0))
        data, changed = legacy_names.rename_keys({"cargo_tonnes": 1, "tonnes_analysed": 2})
        self.assertEqual((data, changed), ({"cargo_tons": 1, "tons_analyzed": 2}, 2))        # every old word in a key is renamed

    def test_a_record_that_already_has_the_new_key_keeps_it(self) -> None:
        data, _changed = legacy_names.rename_keys({"tonnes": 1, "tons": 2})
        self.assertEqual(data, {"tons": 2})

    def test_renames_the_settings_keys_and_the_overlay_slot_keys(self) -> None:
        self.assertEqual(legacy_names.new_name("wfmt_colonisation_overlay_enabled"), "wfmt_colonization_overlay_enabled")
        self.assertEqual(legacy_names.new_name("wfmt_overlay_place_colonisation"), "wfmt_overlay_place_colonization")
        self.assertEqual(legacy_names.new_name("wfmt_overlay_hidden_colonisation"), "wfmt_overlay_hidden_colonization")
        self.assertEqual(legacy_names.new_name("wfmt_mining_enabled"), "wfmt_mining_enabled")


class MigrateTests(unittest.TestCase):
    def test_moves_the_files_and_renames_the_fields_inside_them(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            _write(folder, "colonisation_carrier.json", {"commanders": {"k": {"tonnes": {"steel": 5}}}})
            _write(folder, "colonisation_sites.json", {"commanders": {"k": {}}})
            _write(folder, "trade_stock.json", {"commanders": {"k": {"items": {"gold": {"name": "Gold", "tonnes": 3}}}}})
            _write(folder, "system_surveys.json", {"sys": {"bodies": [{"analysed": ["Fonticulua"]}]}})
            done = legacy_names.migrate(folder)
            self.assertTrue(done)
            self.assertFalse(os.path.exists(os.path.join(folder, "colonisation_carrier.json")))
            self.assertEqual(_read(folder, "colonization_carrier.json"), {"commanders": {"k": {"tons": {"steel": 5}}}})
            self.assertTrue(os.path.exists(os.path.join(folder, "colonization_sites.json")))
            self.assertEqual(_read(folder, "trade_stock.json")["commanders"]["k"]["items"]["gold"], {"name": "Gold", "tons": 3})
            self.assertEqual(_read(folder, "system_surveys.json")["sys"]["bodies"], [{"analyzed": ["Fonticulua"]}])

    def test_does_nothing_the_second_time(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            _write(folder, "colonisation_history.json", {"commanders": {"k": {"tonnes": 1}}})
            self.assertTrue(legacy_names.migrate(folder))
            before = os.path.getmtime(os.path.join(folder, "colonization_history.json"))
            self.assertEqual(legacy_names.migrate(folder), [])
            self.assertEqual(os.path.getmtime(os.path.join(folder, "colonization_history.json")), before)

    def test_the_newer_file_wins_when_both_names_exist(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            new = _write(folder, "colonization_sites.json", {"which": "current"})
            old = _write(folder, "colonisation_sites.json", {"which": "restored"})
            os.utime(new, (time.time() - 100, time.time() - 100))          # the restore wrote the old name just now
            legacy_names.migrate(folder)
            self.assertEqual(_read(folder, "colonization_sites.json"), {"which": "restored"})
            self.assertFalse(os.path.exists(old))

    def test_the_current_file_stays_when_it_is_newer(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            new = _write(folder, "colonization_sites.json", {"which": "current"})
            old = _write(folder, "colonisation_sites.json", {"which": "stale"})
            os.utime(old, (time.time() - 100, time.time() - 100))
            legacy_names.migrate(folder)
            self.assertEqual(_read(folder, "colonization_sites.json"), {"which": "current"})
            self.assertTrue(os.path.exists(old))

    def test_a_file_that_is_not_json_is_left_alone(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "broken.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write('{"tonnes": ')
            legacy_names.migrate(folder)
            with open(path, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), '{"tonnes": ')

    def test_moves_settings_to_the_new_keys_and_forgets_the_old_ones(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            cfg = FakeConfig(wfmt_colonisation_overlay_enabled=1, wfmt_colonisation_window_geometry="800x600+10+10",
                             wfmt_overlay_place_colonisation="top-left,10,20")
            legacy_names.migrate(folder, cfg)
            self.assertEqual(cfg.values, {"wfmt_colonization_overlay_enabled": 1, "wfmt_colonization_window_geometry": "800x600+10+10",
                                          "wfmt_overlay_place_colonization": "top-left,10,20"})

    def test_renames_the_saved_mode_and_its_hidden_flag(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            cfg = FakeConfig(wfmt_active_panel_mode="colonisation", wfmt_mode_hidden_colonisation=1, wfmt_active_panel_mode_other="x")
            legacy_names.migrate(folder, cfg)
            self.assertEqual(cfg.values["wfmt_active_panel_mode"], "colonization")
            self.assertEqual(cfg.values["wfmt_mode_hidden_colonization"], 1)
            self.assertNotIn("wfmt_mode_hidden_colonisation", cfg.values)

    def test_another_saved_mode_is_left_alone(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            cfg = FakeConfig(wfmt_active_panel_mode="mining")
            self.assertEqual(legacy_names.migrate(folder, cfg), [])
            self.assertEqual(cfg.values["wfmt_active_panel_mode"], "mining")

    def test_a_setting_already_saved_under_the_new_key_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            cfg = FakeConfig(wfmt_colonisation_overlay_row_limit=10, wfmt_colonization_overlay_row_limit=20)
            legacy_names.migrate(folder, cfg)
            self.assertEqual(cfg.values, {"wfmt_colonization_overlay_row_limit": 20})

    def test_renames_the_keys_in_each_commanders_overlay_settings(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            _write(folder, "overlay_settings.json",
                   {"commanders": {"k": {"name": "A", "data": {"wfmt_colonisation_overlay_enabled": 1,
                                                               "wfmt_overlay_place_colonisation": "top-left,0,0"}}}})
            legacy_names.migrate(folder)
            data = _read(folder, "overlay_settings.json")["commanders"]["k"]["data"]
            self.assertEqual(data, {"wfmt_colonization_overlay_enabled": 1, "wfmt_overlay_place_colonization": "top-left,0,0"})


if __name__ == "__main__":
    unittest.main()
