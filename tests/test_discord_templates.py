"""The Discord post templates (discord_templates.py): the options and presets of each report, saving, choosing, renaming and deleting your own, and the file."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace()
    sys.modules["config"] = _stub

from plugin import discord_templates as T  # noqa: E402


class Options(unittest.TestCase):
    def test_resolve_fills_in_the_standard_values_and_drops_the_unknown(self):
        out = T.resolve(T.BGS, {"compact": 1, "nonsense": True, "plain": 0})
        self.assertTrue(out["compact"])
        self.assertFalse(out["plain"])
        self.assertNotIn("nonsense", out)
        self.assertEqual(set(out), set(T.DEFAULTS[T.BGS]))
        self.assertEqual(T.resolve(T.POWERPLAY), T.DEFAULTS[T.POWERPLAY])

    def test_a_bad_scope_becomes_the_default(self):
        self.assertEqual(T.resolve(T.BGS, {"scope": "everything"})["scope"], T.SCOPE_ALL)
        self.assertEqual(T.resolve(T.BGS, {"scope": T.SCOPE_WORKED})["scope"], T.SCOPE_WORKED)

    def test_every_toggle_is_an_option_and_every_option_has_a_toggle(self):
        for report in T.REPORTS:
            toggles = {key for key, _label in T.TOGGLES[report]}
            booleans = {key for key, value in T.DEFAULTS[report].items() if isinstance(value, bool)}
            self.assertEqual(toggles, booleans, report)

    def test_the_presets_only_change_options_that_exist(self):
        for report in T.REPORTS:
            for name, change in T.PRESETS[report].items():
                self.assertTrue(set(change) <= set(T.DEFAULTS[report]), (report, name))
            self.assertEqual(set(T.PRESETS[report]), set(T.PRESET_NAMES))

    def test_the_presets(self):
        self.assertEqual(T.preset(T.BGS, "standard").options, T.DEFAULTS[T.BGS])
        self.assertTrue(T.preset(T.BGS, "COMPACT").options["compact"])
        self.assertTrue(T.preset(T.POWERPLAY, "Plain").options["plain"])
        self.assertTrue(T.preset(T.POWERPLAY, "Detailed").options["activities"])
        self.assertIsNone(T.preset(T.BGS, "Mine"))


class Store(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = T.DiscordTemplates(self._tmp.name)

    def path(self):
        return os.path.join(self._tmp.name, T.STATE_FILENAME)

    def test_at_first_standard_is_the_choice_and_the_presets_are_listed(self):
        self.assertEqual(self.store.names(T.BGS), list(T.PRESET_NAMES))
        self.assertEqual(self.store.chosen(T.BGS).name, T.STANDARD)
        self.assertTrue(self.store.chosen(T.POWERPLAY).preset)

    def test_saving_keeps_the_template_and_chooses_it(self):
        saved = self.store.save(T.BGS, "  My   look ", {"compact": True, "heading": False})
        self.assertEqual(saved.name, "My look")
        self.assertEqual(self.store.names(T.BGS), list(T.PRESET_NAMES) + ["My look"])
        self.assertEqual(self.store.chosen(T.BGS).name, "My look")
        self.assertEqual(self.store.get(T.BGS, "my LOOK").options["compact"], True)
        self.assertEqual(self.store.get(T.BGS, "My look").options["heading"], False)
        self.assertEqual(self.store.names(T.POWERPLAY), list(T.PRESET_NAMES))        # the other report is untouched

    def test_saving_under_the_same_name_replaces_it(self):
        self.store.save(T.BGS, "Look", {"compact": True})
        self.store.save(T.BGS, "look", {"compact": False, "details": True})
        self.assertEqual(self.store.names(T.BGS), list(T.PRESET_NAMES) + ["look"])
        self.assertEqual(self.store.get(T.BGS, "look").options["details"], True)

    def test_a_preset_name_or_an_empty_name_is_refused(self):
        for bad in ("Standard", "compact", "  ", ""):
            with self.assertRaises(T.TemplateError):
                self.store.save(T.BGS, bad, {})
        with self.assertRaises(T.TemplateError):
            self.store.save("nonsense", "x", {})

    def test_the_number_of_saved_templates_is_capped(self):
        for number in range(T.MAX_SAVED):
            self.store.save(T.POWERPLAY, f"t{number}", {})
        with self.assertRaises(T.TemplateError):
            self.store.save(T.POWERPLAY, "one more", {})
        self.store.save(T.POWERPLAY, "t3", {"plain": True})                 # replacing is still fine

    def test_choosing(self):
        self.store.save(T.BGS, "Mine", {"plain": True})
        self.store.choose(T.BGS, "Compact")
        self.assertEqual(self.store.chosen(T.BGS).name, "Compact")
        self.store.choose(T.BGS, "no such")
        self.assertEqual(self.store.chosen(T.BGS).name, "Compact")

    def test_deleting_one_you_chose_goes_back_to_standard(self):
        self.store.save(T.BGS, "Mine", {"plain": True})
        self.store.delete(T.BGS, "mine")
        self.assertEqual(self.store.names(T.BGS), list(T.PRESET_NAMES))
        self.assertEqual(self.store.chosen(T.BGS).name, T.STANDARD)

    def test_deleting_one_you_did_not_choose_leaves_the_choice(self):
        self.store.save(T.BGS, "Mine", {})
        self.store.save(T.BGS, "Other", {})
        self.store.choose(T.BGS, "Other")
        self.store.delete(T.BGS, "Mine")
        self.assertEqual(self.store.chosen(T.BGS).name, "Other")

    def test_a_preset_cannot_be_deleted_or_renamed(self):
        with self.assertRaises(T.TemplateError):
            self.store.delete(T.BGS, "Compact")
        with self.assertRaises(T.TemplateError):
            self.store.rename(T.BGS, "Compact", "Tiny")

    def test_renaming_keeps_the_options_and_the_choice(self):
        self.store.save(T.BGS, "Mine", {"compact": True})
        renamed = self.store.rename(T.BGS, "Mine", "Squadron look")
        self.assertEqual((renamed.name, renamed.options["compact"]), ("Squadron look", True))
        self.assertEqual(self.store.chosen(T.BGS).name, "Squadron look")
        self.assertEqual(self.store.names(T.BGS), list(T.PRESET_NAMES) + ["Squadron look"])

    def test_renaming_to_a_taken_or_preset_name_is_refused(self):
        self.store.save(T.BGS, "A", {})
        self.store.save(T.BGS, "B", {})
        for bad in ("b", "Standard", ""):
            with self.assertRaises(T.TemplateError):
                self.store.rename(T.BGS, "A", bad)
        self.assertEqual(self.store.rename(T.BGS, "A", "a").name, "a")           # a change of case alone is fine

    def test_it_is_written_to_the_file_and_read_back(self):
        self.store.save(T.BGS, "Mine", {"compact": True})
        self.store.save(T.POWERPLAY, "Brief", {"cycle": False})
        self.store.choose(T.POWERPLAY, "Detailed")
        again = T.DiscordTemplates(self._tmp.name)
        self.assertEqual(again.get(T.BGS, "Mine").options["compact"], True)
        self.assertEqual(again.get(T.POWERPLAY, "Brief").options["cycle"], False)
        self.assertEqual((again.chosen(T.BGS).name, again.chosen(T.POWERPLAY).name), ("Mine", "Detailed"))

    def test_a_damaged_or_odd_file_is_survived(self):
        with open(self.path(), "w", encoding="utf-8") as handle:
            handle.write("{not json")
        self.assertEqual(T.DiscordTemplates(self._tmp.name).names(T.BGS), list(T.PRESET_NAMES))
        with open(self.path(), "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "choice": {"bgs": "Gone", "powerplay": 5},
                       "templates": [{"report": "bgs", "name": "Standard", "options": {}}, {"report": "x", "name": "Y"}, "junk",
                                     {"report": "bgs", "name": "Fine", "options": {"compact": True, "bogus": 1}}]}, handle)
        odd = T.DiscordTemplates(self._tmp.name)
        self.assertEqual(odd.names(T.BGS), list(T.PRESET_NAMES) + ["Fine"])          # a saved template cannot take a preset's name
        self.assertNotIn("bogus", odd.get(T.BGS, "Fine").options)
        self.assertEqual(odd.chosen(T.BGS).name, T.STANDARD)                          # the template chosen is gone
        self.assertEqual(odd.chosen(T.POWERPLAY).name, T.STANDARD)

    def test_the_file_is_kept_by_the_updater_and_is_not_a_secret(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "plugin", "update.py"), encoding="utf-8") as handle:
            self.assertIn('"discord_templates.json"', handle.read())
        from plugin import data_backup
        self.assertNotIn(T.STATE_FILENAME, data_backup.LEFT_OUT)


if __name__ == "__main__":
    unittest.main()
