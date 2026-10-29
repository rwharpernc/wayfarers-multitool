"""The saved Discord destinations of each commander (discord_webhooks.py): a list for each commander, cleaned and capped, the first version's single webhook read as a list of one, and the master switch off by default."""
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
LINK2 = "https://discord.com/api/webhooks/987654321/zzzYYY-_999"


def dest(name, url=LINK, thread=""):
    return {"name": name, "url": url, "thread": thread}


class Clean(unittest.TestCase):
    def test_an_entry_with_no_link_is_dropped_and_a_missing_name_becomes_discord(self):
        self.assertEqual(W.clean([dest("A", ""), dest("", LINK), {"url": "  " + LINK2 + "  "}, "junk", None]),
                         [dest("Discord", LINK), dest("Discord 2", LINK2)])

    def test_names_are_one_line_and_unique_in_any_case(self):
        out = W.clean([dest(" My   server ", LINK), dest("my server", LINK2), dest("MY SERVER", LINK + "x")])
        self.assertEqual([d["name"] for d in out], ["My server", "my server 2", "MY SERVER 3"])

    def test_values_are_clipped_and_the_list_is_capped(self):
        out = W.clean([dest("n" * 100, LINK + "x" * 500, "1" * 100)])
        self.assertEqual((len(out[0]["name"]), len(out[0]["url"]), len(out[0]["thread"])), (W.NAME_MAX, W.URL_MAX, W.THREAD_MAX))
        self.assertEqual(len(W.clean([dest(f"d{i}", LINK + str(i)) for i in range(25)])), W.MAX_DESTINATIONS)

    def test_a_clipped_name_still_stays_unique(self):
        out = W.clean([dest("x" * 50, LINK), dest("x" * 50, LINK2)])
        self.assertEqual(len({d["name"].casefold() for d in out}), 2)
        self.assertTrue(all(len(d["name"]) <= W.NAME_MAX for d in out))


class Store(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = W.DiscordWebhooks(self._tmp.name)

    def path(self):
        return os.path.join(self._tmp.name, W.STATE_FILENAME)

    def test_nothing_is_saved_at_first(self):
        self.assertEqual(self.store.destinations("CMDR A"), [])
        self.assertIsNone(self.store.find("CMDR A"))

    def test_a_commander_can_save_several_destinations(self):
        kept = self.store.set_destinations("CMDR A", [dest("Squadron BGS", LINK), dest("Friends", LINK2, "42")])
        self.assertEqual([d["name"] for d in kept], ["Squadron BGS", "Friends"])
        self.assertEqual(self.store.find("cmdr a", "friends"), dest("Friends", LINK2, "42"))
        self.assertEqual(self.store.find("CMDR A"), dest("Squadron BGS", LINK))       # no name: the first
        self.assertIsNone(self.store.find("CMDR A", "nobody"))

    def test_each_commander_has_their_own_list(self):
        self.store.set_destinations("CMDR A", [dest("Squadron", LINK)])
        self.store.set_destinations("CMDR B", [dest("Friends", LINK2)])
        self.assertEqual([d["name"] for d in self.store.destinations("CMDR A")], ["Squadron"])
        self.assertEqual([d["name"] for d in self.store.destinations("CMDR B")], ["Friends"])
        self.assertEqual(self.store.destinations("CMDR C"), [])

    def test_it_is_kept_in_the_file_and_read_back(self):
        self.store.set_destinations("CMDR A", [dest("Squadron", LINK, "7")])
        self.assertEqual(W.DiscordWebhooks(self._tmp.name).destinations("CMDR A"), [dest("Squadron", LINK, "7")])

    def test_an_empty_list_forgets_everything(self):
        self.store.set_destinations("CMDR A", [dest("Squadron", LINK)])
        self.store.set_destinations("CMDR A", [])
        self.assertEqual(self.store.destinations("CMDR A"), [])

    def test_without_a_commander_nothing_is_saved(self):
        self.assertEqual(self.store.set_destinations("", [dest("x", LINK)]), [])
        self.assertFalse(os.path.exists(self.path()))

    def test_the_other_commanders_with_destinations(self):
        self.store.set_destinations("CMDR A", [dest("a", LINK)])
        self.store.set_destinations("Cmdr B", [dest("b", LINK2)])
        self.store.set_destinations("CMDR C", [])
        self.assertEqual(self.store.other_commanders("CMDR A"), ["Cmdr B"])
        self.assertEqual(self.store.other_commanders("someone else"), ["CMDR A", "Cmdr B"])

    def test_the_first_versions_single_webhook_is_read_as_a_list_of_one(self):
        with open(self.path(), "w", encoding="utf-8") as handle:
            json.dump({"version": 2, "commanders": {"cmdr a": {"name": "CMDR A", "data": {"url": LINK, "nickname": "Squadron BGS", "thread": "5"}}},
                       "legacy": None, "meta": {}}, handle)
        old = W.DiscordWebhooks(self._tmp.name)
        self.assertEqual(old.destinations("CMDR A"), [dest("Squadron BGS", LINK, "5")])
        old.set_destinations("CMDR A", old.destinations("CMDR A") + [dest("Friends", LINK2)])
        self.assertEqual([d["name"] for d in W.DiscordWebhooks(self._tmp.name).destinations("CMDR A")], ["Squadron BGS", "Friends"])

    def test_a_damaged_file_is_survived(self):
        with open(self.path(), "w", encoding="utf-8") as handle:
            handle.write("{not json")
        self.assertEqual(W.DiscordWebhooks(self._tmp.name).destinations("CMDR A"), [])


class Switch(unittest.TestCase):
    def test_it_is_off_by_default(self):
        with mock.patch.object(W, "config", types.SimpleNamespace(get_bool=lambda key, default=False: default)):
            self.assertFalse(W.enabled())

    def test_ready_needs_the_switch_and_a_destination(self):
        on = types.SimpleNamespace(get_bool=lambda key, default=False: True)
        with mock.patch.object(W, "config", on), mock.patch.object(W.webhooks, "destinations", lambda cmdr: [dest("x")]):
            self.assertTrue(W.ready("CMDR A"))
        with mock.patch.object(W, "config", on), mock.patch.object(W.webhooks, "destinations", lambda cmdr: []):
            self.assertFalse(W.ready("CMDR A"))
        with mock.patch.object(W, "config", None), mock.patch.object(W.webhooks, "destinations", lambda cmdr: [dest("x")]):
            self.assertFalse(W.ready("CMDR A"))

    def test_the_file_name_is_what_the_updater_and_backup_expect(self):
        self.assertEqual(W.STATE_FILENAME, "discord_webhooks.json")
        with open(os.path.join(os.path.dirname(__file__), "..", "plugin", "update.py"), encoding="utf-8") as handle:
            self.assertIn('"discord_webhooks.json"', handle.read())
        self.assertIn("discord_webhooks.json", json.dumps(__import__("plugin.data_backup", fromlist=["x"]).LEFT_OUT))


if __name__ == "__main__":
    unittest.main()
