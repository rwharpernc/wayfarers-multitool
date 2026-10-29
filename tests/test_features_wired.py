"""
Every feature that handles journal events is wired in both places that need it: `ui.FEATURES` (Settings tabs and panels) and `load._FEATURES` (the journal
events). A module listed only in `ui.FEATURES` never sees an event, so what depends on one (the Discord tab, which learns the commander from the journal) silently
does nothing. This reads the two lists from the source, so it needs no EDMC and no Tk.
"""
from __future__ import annotations

import os
import re
import sys
import types
import unittest
from unittest import mock

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
for name in ("myNotebook", "ttkHyperlinkLabel", "theme", "monitor", "plug", "l10n", "requests"):
    sys.modules.setdefault(name, mock.MagicMock())
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = mock.MagicMock()
    sys.modules["config"] = _stub


def _block(path: str, opener: str) -> str:
    with open(os.path.join(ROOT, "plugin", path), encoding="utf-8") as handle:
        text = handle.read()
    block = text[text.index(opener):]
    return block[:block.index("\n)\n")]


class Wiring(unittest.TestCase):
    def test_every_ui_feature_that_handles_events_is_in_the_journal_list(self):
        ui_names = set(re.findall(r"\b([a-z_][a-z0-9_]*)\b", _block("ui.py", "FEATURES = (")))
        load_block = _block("load.py", "_FEATURES = (")
        missing = []
        for name in sorted(ui_names):
            path = os.path.join(ROOT, "plugin", name + ".py")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as handle:
                    handles = re.search(r"^def handle_event\(", handle.read(), re.M)
                if handles and not re.search(r"\b%s\b" % name, load_block):
                    missing.append(name)
        self.assertEqual(missing, [], "these handle journal events but are not in load._FEATURES, so they never see one")


class DiscordTab(unittest.TestCase):
    def setUp(self):
        from plugin import discord_settings, discord_webhooks
        import tempfile
        self.S, self.W = discord_settings, discord_webhooks
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = discord_webhooks.DiscordWebhooks(self._tmp.name)
        self.saved = {}
        config = types.SimpleNamespace(set=lambda key, value: self.saved.__setitem__(key, value), get_bool=lambda key, default=False: self.saved.get(key, default))
        for patcher in (mock.patch.object(discord_webhooks, "webhooks", self.store), mock.patch.object(discord_settings, "config", config),
                        mock.patch.object(discord_webhooks, "config", config), mock.patch.object(discord_settings, "_cmdr", ""),
                        mock.patch.object(discord_settings, "_pending", None), mock.patch.object(discord_settings, "_vars", {}),
                        mock.patch.object(discord_settings, "_rows", [])):
            patcher.start()
            self.addCleanup(patcher.stop)

    class Var:
        def __init__(self, value):
            self.value = value

        def get(self):
            return self.value

    LINK = "https://discord.com/api/webhooks/1/abc"
    LINK2 = "https://discord.com/api/webhooks/2/def"

    def fill(self, *rows):
        """The tab as the commander left it: the switch on and these (name, link, thread) rows."""
        self.S._vars["enabled"] = self.Var(True)
        self.S._rows.extend({"name": self.Var(n), "url": self.Var(u), "thread": self.Var(t)} for n, u, t in rows)

    def test_the_journal_names_the_commander(self):
        self.assertEqual(self.S.commander(), "")
        self.S.handle_event({"event": "LoadGame"}, "CMDR A", None, None, {})
        self.assertEqual(self.S.commander(), "CMDR A")
        self.S.handle_event({"event": "Music"}, "", None, None, {})
        self.assertEqual(self.S.commander(), "CMDR A")      # an event with no commander does not forget them

    def test_saving_writes_every_destination_for_the_commander_the_journal_named(self):
        self.fill(("Squadron", self.LINK, ""), ("Friends", self.LINK2, "42"))
        self.S.handle_event({"event": "LoadGame"}, "CMDR A", None, None, {})
        self.S.save_settings()
        self.assertEqual(self.store.destinations("CMDR A"), [{"name": "Squadron", "url": self.LINK, "thread": ""}, {"name": "Friends", "url": self.LINK2, "thread": "42"}])
        self.assertTrue(self.saved[self.W.CFG_ENABLED])
        self.assertTrue(self.W.ready("CMDR A"))

    def test_removing_every_row_forgets_the_commanders_destinations(self):
        self.store.set_destinations("CMDR A", [{"name": "x", "url": self.LINK}])
        self.fill()
        self.S.handle_event({"event": "LoadGame"}, "CMDR A", None, None, {})
        self.S.save_settings()
        self.assertEqual(self.store.destinations("CMDR A"), [])

    def test_destinations_saved_before_a_commander_is_known_go_to_the_one_who_logs_in_next(self):
        self.fill(("Squadron", self.LINK, ""), ("", "  ", ""))
        self.S.save_settings()
        self.assertTrue(self.saved[self.W.CFG_ENABLED])
        self.assertEqual(self.store.destinations("CMDR A"), [])             # nobody to save them for yet
        self.S.handle_event({"event": "LoadGame"}, "CMDR A", None, None, {})
        self.assertEqual(self.store.destinations("CMDR A"), [{"name": "Squadron", "url": self.LINK, "thread": ""}])
        self.assertIsNone(self.S._pending)

    def test_an_empty_link_before_login_leaves_nothing_waiting(self):
        self.fill(("x", "  ", ""))
        self.S.save_settings()
        self.assertIsNone(self.S._pending)

    def test_copying_another_commanders_destinations_adds_only_the_new_links(self):
        self.store.set_destinations("CMDR B", [{"name": "Friends", "url": self.LINK2}, {"name": "Squadron", "url": self.LINK}])
        self.fill(("Mine", self.LINK, ""))
        added = []
        with mock.patch.object(self.S, "_add_row", added.append):
            self.S._copy_from("CMDR B")
        self.assertEqual([d["url"] for d in added], [self.LINK2])              # the link this list already has is not added twice


if __name__ == "__main__":
    unittest.main()
