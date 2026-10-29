"""
What the report windows call to share with Discord (discord_share.py): posting, editing an earlier post, trimming extra messages, the gates, and
that the webhook link never reaches the sentence shown to the commander. The network is a stand-in; no real webhook is ever called.
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import threading
import types
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
for name in ("myNotebook", "ttkHyperlinkLabel", "theme", "monitor", "plug", "l10n", "requests"):
    sys.modules.setdefault(name, mock.MagicMock())
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = mock.MagicMock()
    sys.modules["config"] = _stub

from plugin import discord_client, discord_settings, discord_share as S, discord_webhooks  # noqa: E402

TOKEN = "SECRETtoken_abc-123"
LINK = f"https://discord.com/api/webhooks/1234567890/{TOKEN}"
LINK2 = f"https://discord.com/api/webhooks/1234567891/{TOKEN}2"


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = io.BytesIO(body)

    def read(self, size=-1):
        return self._body.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Discord:
    """Stands in for Discord: numbers the messages it is given and remembers what each says."""

    def __init__(self):
        self.messages, self.calls, self.next_id, self.deleted_ids = {}, [], 100, set()

    def __call__(self, request, timeout=None):
        method, url = request.get_method(), request.full_url
        self.calls.append((method, url))
        data = json.loads(request.data) if request.data else {}
        if method == "POST":
            self.next_id += 1
            self.messages[str(self.next_id)] = data["content"]
            return FakeResponse(json.dumps({"id": str(self.next_id)}).encode())
        message_id = url.split("/messages/")[1].split("?")[0]
        if method == "PATCH":
            if message_id in self.deleted_ids:
                raise urllib.error.HTTPError(url, 404, "x", {}, io.BytesIO(b""))
            self.messages[message_id] = data["content"]
            return FakeResponse(json.dumps({"id": message_id}).encode())
        if method == "DELETE":
            self.messages.pop(message_id, None)
            return FakeResponse(b"")
        raise AssertionError(method)


def no_sleep(seconds):
    pass


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        store = discord_webhooks.DiscordWebhooks(self._tmp.name)
        store.set_destinations("CMDR A", [{"name": "Squadron BGS", "url": LINK, "thread": ""}])
        for patcher in (mock.patch.object(discord_webhooks, "webhooks", store),
                        mock.patch.object(discord_webhooks, "config", types.SimpleNamespace(get_bool=lambda key, default=False: True)),
                        mock.patch.object(discord_settings, "_cmdr", "CMDR A")):
            patcher.start()
            self.addCleanup(patcher.stop)
        S._posted.clear()
        self.discord = Discord()


class Sending(Base):
    def test_a_report_is_posted_in_order(self):
        text = S.send("CMDR A", ["one", "two"], "bgs:tick", "", self.discord, no_sleep)
        self.assertEqual(text, "Posted to Squadron BGS (2 messages).")
        self.assertEqual(list(self.discord.messages.values()), ["one", "two"])
        self.assertEqual([c[0] for c in self.discord.calls], ["POST", "POST"])

    def test_the_same_report_again_edits_the_earlier_messages(self):
        S.send("CMDR A", ["one", "two"], "bgs:tick", "", self.discord, no_sleep)
        text = S.send("CMDR A", ["ONE", "TWO"], "bgs:tick", "", self.discord, no_sleep)
        self.assertEqual(text, "Updated your earlier post in Squadron BGS.")
        self.assertEqual(sorted(self.discord.messages.values()), ["ONE", "TWO"])
        self.assertEqual([c[0] for c in self.discord.calls], ["POST", "POST", "PATCH", "PATCH"])

    def test_a_longer_report_adds_messages_and_a_shorter_one_removes_them(self):
        S.send("CMDR A", ["one"], "k", "", self.discord, no_sleep)
        text = S.send("CMDR A", ["one", "two", "three"], "k", "", self.discord, no_sleep)
        self.assertIn("added 2 more messages", text)
        S.send("CMDR A", ["only"], "k", "", self.discord, no_sleep)
        self.assertEqual(list(self.discord.messages.values()), ["only"])
        self.assertIn("DELETE", [c[0] for c in self.discord.calls])

    def test_a_message_deleted_in_discord_is_posted_again(self):
        S.send("CMDR A", ["one"], "k", "", self.discord, no_sleep)
        self.discord.deleted_ids.add(next(iter(self.discord.messages)))
        text = S.send("CMDR A", ["one again"], "k", "", self.discord, no_sleep)
        self.assertTrue(text.startswith("Posted to"))
        self.assertIn("one again", self.discord.messages.values())

    def test_different_reports_do_not_share_ids(self):
        S.send("CMDR A", ["a"], "bgs:1", "", self.discord, no_sleep)
        S.send("CMDR A", ["b"], "bgs:2", "", self.discord, no_sleep)
        self.assertEqual([c[0] for c in self.discord.calls], ["POST", "POST"])

    def test_nothing_saved_or_nothing_to_post(self):
        with self.assertRaises(discord_client.DiscordError):
            S.send("CMDR B", ["x"], "k", "", self.discord, no_sleep)
        with self.assertRaises(discord_client.DiscordError):
            S.send("CMDR A", [], "k", "", self.discord, no_sleep)
        self.assertEqual(self.discord.calls, [])


class Destinations(Base):
    def setUp(self):
        super().setUp()
        discord_webhooks.webhooks.set_destinations("CMDR A", [{"name": "Squadron BGS", "url": LINK, "thread": ""},
                                                              {"name": "Friends", "url": LINK2, "thread": "42"}])

    def test_a_named_destination_is_the_one_posted_to(self):
        text = S.send("CMDR A", ["hello"], "k", "friends", self.discord, no_sleep)
        self.assertEqual(text, "Posted to Friends.")
        self.assertIn("1234567891", self.discord.calls[0][1])
        self.assertTrue(self.discord.calls[0][1].endswith("thread_id=42"))

    def test_no_name_means_the_first_destination(self):
        self.assertEqual(S.send("CMDR A", ["hello"], "k", "", self.discord, no_sleep), "Posted to Squadron BGS.")
        self.assertIn("1234567890", self.discord.calls[0][1])

    def test_an_unknown_destination_is_refused_before_anything_is_sent(self):
        with self.assertRaises(discord_client.DiscordError) as caught:
            S.send("CMDR A", ["hello"], "k", "Nowhere", self.discord, no_sleep)
        self.assertIn("Nowhere", str(caught.exception))
        self.assertEqual(self.discord.calls, [])

    def test_the_same_report_keeps_its_own_posts_for_each_destination(self):
        S.send("CMDR A", ["one"], "k", "Squadron BGS", self.discord, no_sleep)
        S.send("CMDR A", ["one"], "k", "Friends", self.discord, no_sleep)
        self.assertEqual([c[0] for c in self.discord.calls], ["POST", "POST"])            # the second destination is not an edit of the first
        again = S.send("CMDR A", ["ONE"], "k", "Friends", self.discord, no_sleep)
        self.assertEqual(again, "Updated your earlier post in Friends.")
        self.assertEqual([c[0] for c in self.discord.calls], ["POST", "POST", "PATCH"])


class Window:
    """A window whose `after` runs the call at once."""

    def after(self, milliseconds, callback):
        callback()


class Async(Base):
    def run_post(self, messages, key="k", opener=None, destination=""):
        results = []
        S.post_async(Window(), messages, key, lambda text, ok: results.append((text, ok)), destination, opener or self.discord, no_sleep)
        for thread in threading.enumerate():
            if thread.name == "WFMT-discord-post":
                thread.join(5)
        return results

    def test_a_post_reports_back(self):
        self.assertEqual(self.run_post(["hello"]), [("Posted to Squadron BGS.", True)])

    def test_it_will_not_start_until_ready(self):
        with mock.patch.object(discord_webhooks, "config", types.SimpleNamespace(get_bool=lambda key, default=False: False)):
            self.assertEqual(self.run_post(["hello"]), [(S.NOT_READY, False)])
        self.assertEqual(self.discord.calls, [])

    def test_a_failure_is_worded_without_the_link(self):
        def refuse(request, timeout=None):
            raise urllib.error.HTTPError(LINK, 401, "x", {}, io.BytesIO(b""))
        (text, ok), = self.run_post(["hello"], opener=refuse)
        self.assertFalse(ok)
        self.assertIn("did not accept", text)
        self.assertNotIn(TOKEN, text)

    def test_an_unexpected_failure_is_logged_without_its_text_and_worded_plainly(self):
        def explode(request, timeout=None):
            raise RuntimeError(LINK)
        with self.assertLogs(S.logger, level="ERROR") as logs:
            (text, ok), = self.run_post(["hello"], opener=explode)
        self.assertFalse(ok)
        self.assertNotIn(TOKEN, text)
        self.assertNotIn(TOKEN, "\n".join(logs.output))

    def test_the_gate_is_released_after_a_failure(self):
        def refuse(request, timeout=None):
            raise urllib.error.HTTPError(LINK, 500, "x", {}, io.BytesIO(b""))
        self.run_post(["hello"], opener=refuse)
        self.assertEqual(self.run_post(["hello"])[0][1], True)

    def test_a_second_press_while_one_is_under_way_is_refused(self):
        self.assertTrue(S._busy.acquire(blocking=False))
        try:
            results = []
            S.post_async(Window(), ["x"], "k", lambda text, ok: results.append((text, ok)), "", self.discord, no_sleep)
            self.assertEqual(results, [("A post is already on its way.", False)])
        finally:
            S._busy.release()


class Choosing(Base):
    def choose_and_post(self, messages, popup=None):
        results = []
        S.post_choosing(Window(), messages, "k", lambda text, ok: results.append((text, ok)), popup, opener=self.discord, sleep=no_sleep)
        for thread in threading.enumerate():
            if thread.name == "WFMT-discord-post":
                thread.join(5)
        return results

    def test_one_destination_is_posted_to_without_asking(self):
        asked = []
        self.assertEqual(self.choose_and_post(["hello"], lambda widget, names, choose: asked.append(names)), [("Posted to Squadron BGS.", True)])
        self.assertEqual(asked, [])

    def test_several_destinations_ask_and_post_to_the_one_picked(self):
        discord_webhooks.webhooks.set_destinations("CMDR A", [{"name": "Squadron BGS", "url": LINK, "thread": ""}, {"name": "Friends", "url": LINK2, "thread": ""}])
        asked = []

        def pick_second(widget, names, choose):
            asked.append(list(names))
            choose(names[1])

        self.assertEqual(self.choose_and_post(["hello"], pick_second), [("Posted to Friends.", True)])
        self.assertEqual(asked, [["Squadron BGS", "Friends"]])
        self.assertIn("1234567891", self.discord.calls[0][1])

    def test_closing_the_menu_without_a_choice_posts_nothing(self):
        discord_webhooks.webhooks.set_destinations("CMDR A", [{"name": "A", "url": LINK, "thread": ""}, {"name": "B", "url": LINK2, "thread": ""}])
        self.assertEqual(self.choose_and_post(["hello"], lambda widget, names, choose: None), [])
        self.assertEqual(self.discord.calls, [])

    def test_nothing_saved_or_the_switch_off_says_what_to_set_up(self):
        with mock.patch.object(discord_webhooks, "config", types.SimpleNamespace(get_bool=lambda key, default=False: False)):
            self.assertEqual(self.choose_and_post(["hello"]), [(S.NOT_READY, False)])
        discord_webhooks.webhooks.set_destinations("CMDR A", [])
        self.assertEqual(self.choose_and_post(["hello"]), [(S.NOT_READY, False)])
        self.assertEqual(self.discord.calls, [])


class Copying(unittest.TestCase):
    def test_messages_are_joined_with_a_blank_line_for_pasting(self):
        with mock.patch.object(S.panelkit, "copy_to_clipboard", return_value=True) as copy:
            self.assertTrue(S.copy_for_discord(object(), ["one", "two"]))
        copy.assert_called_once_with(mock.ANY, "one\n\ntwo")


if __name__ == "__main__":
    unittest.main()
