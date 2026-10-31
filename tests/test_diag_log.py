"""The separate diagnostic log (plugin/diag_log.py): off by default and silent while off; on, it writes its own file with the plugin's finer log lines and the lines `log`
writes; it keeps EDMC's log as it was; it hides names, the home folder and webhook links; and switching it off puts everything back."""
from __future__ import annotations

import logging
import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default, default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import diag_log as D  # noqa: E402
from plugin.uikit import trace  # noqa: E402


class _Memory(logging.Handler):
    """Stands in for one of EDMC's handlers."""

    def __init__(self, level=logging.INFO):
        super().__init__(level)
        self.lines = []

    def emit(self, record):
        self.lines.append((record.levelname, record.getMessage()))


class DiagLogTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "logs", "WFMT", D.FILE_NAME)
        self.saved = {}
        self.base = logging.getLogger("EDMarketConnector")
        self.base_level = self.base.level
        self.base.setLevel(logging.INFO)
        self.edmc = _Memory(logging.DEBUG)       # EDMC's handler would take any level it is handed; the guard has to keep the extra ones out
        self.base.addHandler(self.edmc)
        D._names.clear()

    def tearDown(self):
        D.set_enabled(False, save=False)
        self.base.removeHandler(self.edmc)
        self.base.setLevel(self.base_level)

    def lines(self):
        for handler in list(D._diag_logger.handlers):
            handler.flush()
        with open(self.path, encoding="utf-8") as handle:
            return handle.read().splitlines()

    def test_off_by_default_and_nothing_is_written(self):
        self.assertFalse(D.enabled())
        D.log("test", "nothing")
        D.timed("test", "nothing")(x=1)
        self.assertFalse(os.path.exists(self.path))

    def test_on_writes_its_own_file(self):
        self.assertTrue(D.set_enabled(True, save=False, path=self.path))
        D.log("search", "Find nearest", commodity="Steel", ms=12)
        text = "\n".join(self.lines())
        self.assertIn("Diagnostic log switched on", text)
        self.assertIn("search    Find nearest commodity=Steel ms=12", text)
        self.assertRegex(text, r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3} \| DEBUG")

    def test_the_plugins_finer_lines_are_captured_but_edmcs_log_is_unchanged(self):
        plugin = logging.getLogger("EDMarketConnector." + D.plugin_name)
        D.set_enabled(True, save=False, path=self.path)
        plugin.debug("a finer line")
        plugin.info("an ordinary line")
        text = "\n".join(self.lines())
        self.assertIn("a finer line", text)
        self.assertIn("an ordinary line", text)
        messages = [m for _lvl, m in self.edmc.lines]
        self.assertIn("an ordinary line", messages)
        self.assertNotIn("a finer line", messages, "EDMC's log is left as it was")

    def test_switching_off_restores_everything(self):
        plugin = logging.getLogger("EDMarketConnector." + D.plugin_name)
        before = (plugin.level, len(plugin.handlers), len(self.edmc.filters))
        D.set_enabled(True, save=False, path=self.path)
        self.assertGreater(len(self.edmc.filters), before[2])
        D.set_enabled(False, save=False)
        self.assertEqual((plugin.level, len(plugin.handlers), len(self.edmc.filters)), before)
        size = os.path.getsize(self.path)
        plugin.info("after")
        D.log("test", "after")
        self.assertEqual(os.path.getsize(self.path), size, "nothing is written once it is off")
        self.assertIn("Diagnostic log switched off", "\n".join(open(self.path, encoding="utf-8").read().splitlines()))

    def test_names_the_home_folder_and_webhooks_are_hidden(self):
        D.set_enabled(True, save=False, path=self.path)
        D.note_commander("Bocheaux")
        home = os.path.expanduser("~")
        D.log("journal", "FSDJump", system="Sol", station="Bocheaux's Rest", file=os.path.join(home, "x", "y.log"),
              link="https://discord.com/api/webhooks/123456/abcdefSECRET")
        text = "\n".join(self.lines())
        self.assertNotIn("Bocheaux", text)
        self.assertIn("<commander>", text)
        self.assertNotIn(home, text.split("Diagnostic log switched on")[-1])
        self.assertNotIn("abcdefSECRET", text)
        self.assertIn("<webhook>", text)

    def test_a_long_field_is_clipped_and_a_newline_is_flattened(self):
        D.set_enabled(True, save=False, path=self.path)
        D.log("test", "long", value="x" * 1000, text="one\ntwo")
        line = next(l for l in self.lines() if "long" in l and "test" in l)
        self.assertLess(len(line), 450)
        self.assertIn("text=one two", line)

    def test_a_file_that_cannot_be_opened_leaves_it_off(self):
        blocker = os.path.join(self.dir, "blocker")
        open(blocker, "w").close()
        self.assertFalse(D.set_enabled(True, save=False, path=os.path.join(blocker, "inside", D.FILE_NAME)))
        self.assertFalse(D.enabled())

    def test_the_choice_is_saved(self):
        saved = {}
        original = D.config
        D.config = types.SimpleNamespace(set=lambda key, value: saved.__setitem__(key, value), get_bool=lambda key, default=False: saved.get(key, default),
                                         app_dir_path=self.dir)
        try:
            self.assertFalse(D.saved_setting())
            D.set_enabled(True)
            self.assertEqual(saved, {D.CONFIG_ENABLED: True})
            self.assertTrue(D.saved_setting())
            self.assertEqual(D.log_path(), os.path.join(self.dir, "logs", "WFMT", D.FILE_NAME))
            D.set_enabled(False)
            self.assertEqual(saved, {D.CONFIG_ENABLED: False})
        finally:
            D.config = original

    def test_the_window_kit_hook_reaches_the_log(self):
        D.set_enabled(True, save=False, path=self.path)
        trace.listener = D.log
        try:
            trace.emit("ui", "button pressed", label="Refresh", window="My Projects")
        finally:
            trace.listener = None
        self.assertTrue(any("button pressed" in l and "label=Refresh" in l for l in self.lines()))
        trace.emit("ui", "no listener", label="x")        # does nothing, and does not fail


if __name__ == "__main__":
    unittest.main()
