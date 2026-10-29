"""The saved Discord webhook of each commander (discord_webhooks.py): per commander, forgotten when emptied, and the master switch off by default."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_bool=lambda key, default=False: default)
    sys.modules["config"] = _stub

from plugin import discord_webhooks as W  # noqa: E402

LINK = "https://discord.com/api/webhooks/1234567890/abcDEF-_123"


class Store(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = W.DiscordWebhooks(self._tmp.name)

    def path(self):
        return os.path.join(self._tmp.name, W.STATE_FILENAME)

    def test_nothing_is_saved_at_first(self):
        self.assertEqual(self.store.get("CMDR A"), {"url": "", "nickname": "", "thread": ""})
        self.assertEqual(self.store.url("CMDR A"), "")

    def test_each_commander_has_their_own(self):
        self.store.set("CMDR A", LINK, "Squadron", "42")
        self.store.set("CMDR B", LINK + "x", "Friends")
        self.assertEqual(self.store.get("cmdr a"), {"url": LINK, "nickname": "Squadron", "thread": "42"})
        self.assertEqual(self.store.url("CMDR B"), LINK + "x")
        self.assertEqual(self.store.url("CMDR C"), "")

    def test_it_is_kept_in_the_file_and_read_back(self):
        self.store.set("CMDR A", "  " + LINK + "  ", " My   server ", " 7 ")
        self.assertTrue(os.path.exists(self.path()))
        again = W.DiscordWebhooks(self._tmp.name)
        self.assertEqual(again.get("CMDR A"), {"url": LINK, "nickname": "My server", "thread": "7"})

    def test_an_empty_link_forgets_the_webhook_and_its_labels(self):
        self.store.set("CMDR A", LINK, "Squadron", "42")
        self.store.set("CMDR A", "", "Squadron", "42")
        self.assertEqual(self.store.get("CMDR A"), {"url": "", "nickname": "", "thread": ""})

    def test_without_a_commander_nothing_is_saved(self):
        self.store.set("", LINK)
        self.assertFalse(os.path.exists(self.path()))

    def test_long_values_are_clipped(self):
        self.store.set("CMDR A", LINK + "x" * 500, "n" * 100, "1" * 100)
        saved = self.store.get("CMDR A")
        self.assertEqual((len(saved["url"]), len(saved["nickname"]), len(saved["thread"])), (W.URL_MAX, W.NICKNAME_MAX, W.THREAD_MAX))

    def test_a_damaged_file_is_survived(self):
        with open(self.path(), "w", encoding="utf-8") as handle:
            handle.write("{not json")
        self.assertEqual(W.DiscordWebhooks(self._tmp.name).url("CMDR A"), "")


class Switch(unittest.TestCase):
    def test_it_is_off_by_default(self):
        with mock.patch.object(W, "config", types.SimpleNamespace(get_bool=lambda key, default=False: default)):
            self.assertFalse(W.enabled())

    def test_ready_needs_the_switch_and_a_link(self):
        on = types.SimpleNamespace(get_bool=lambda key, default=False: True)
        with mock.patch.object(W, "config", on), mock.patch.object(W.webhooks, "url", lambda cmdr: LINK):
            self.assertTrue(W.ready("CMDR A"))
        with mock.patch.object(W, "config", on), mock.patch.object(W.webhooks, "url", lambda cmdr: ""):
            self.assertFalse(W.ready("CMDR A"))
        with mock.patch.object(W, "config", None), mock.patch.object(W.webhooks, "url", lambda cmdr: LINK):
            self.assertFalse(W.ready("CMDR A"))

    def test_the_file_name_is_what_the_updater_and_backup_expect(self):
        self.assertEqual(W.STATE_FILENAME, "discord_webhooks.json")
        with open(os.path.join(os.path.dirname(__file__), "..", "plugin", "update.py"), encoding="utf-8") as handle:
            self.assertIn('"discord_webhooks.json"', handle.read())
        self.assertIn("discord_webhooks.json", json.dumps(__import__("plugin.data_backup", fromlist=["x"]).LEFT_OUT))


if __name__ == "__main__":
    unittest.main()
