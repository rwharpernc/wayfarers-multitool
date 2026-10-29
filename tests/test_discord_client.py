"""
The Discord webhook client (discord_client.py): what is sent, how a repeat post edits, how a pause or a deleted message is handled, and that the
webhook link (a secret) never appears in an error or its cause. The network is a stand-in; no real webhook is ever called.
"""
from __future__ import annotations

import io
import json
import os
import sys
import types
import unittest
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import discord_client as C  # noqa: E402

TOKEN = "SECRETtoken_abc-123"
URL = f"https://discord.com/api/webhooks/1234567890/{TOKEN}"


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = io.BytesIO(body)

    def read(self, size=-1):
        return self._body.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Opener:
    """Stands in for urlopen: records the requests and answers from a script."""

    def __init__(self, *answers):
        self.answers, self.requests = list(answers), []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return FakeResponse(answer if isinstance(answer, bytes) else json.dumps(answer).encode("utf-8"))


def http_error(code, body=b"", headers=None):
    return urllib.error.HTTPError(URL, code, "x", headers or {}, io.BytesIO(body))


class Sleeper:
    def __init__(self):
        self.waits = []

    def __call__(self, seconds):
        self.waits.append(seconds)


class Links(unittest.TestCase):
    def test_a_webhook_link_is_accepted(self):
        self.assertEqual(C.parse_webhook(URL), (URL, ""))
        self.assertEqual(C.parse_webhook(f" https://discordapp.com/api/v10/webhooks/5/{TOKEN}/ ")[0], f"https://discordapp.com/api/webhooks/5/{TOKEN}")

    def test_a_thread_id_on_the_end_is_read(self):
        self.assertEqual(C.parse_webhook(URL + "?thread_id=987654321"), (URL, "987654321"))
        self.assertEqual(C.parse_webhook(URL + "?thread_id=abc"), (URL, ""))

    def test_other_links_are_refused(self):
        for bad in ("", "discord.com/api/webhooks/1/x", "http://discord.com/api/webhooks/1/x", "https://example.com/api/webhooks/1/x",
                    "https://discord.com/channels/1/2", "https://discord.com/api/webhooks/abc/x", "https://discord.com.evil.com/api/webhooks/1/x"):
            with self.assertRaises(C.DiscordError, msg=bad):
                C.parse_webhook(bad)


class Posting(unittest.TestCase):
    def test_post_sends_the_text_with_no_mentions_and_returns_the_id(self):
        opener = Opener({"id": "555"})
        self.assertEqual(C.post(URL, "hello", opener=opener, sleep=Sleeper()), "555")
        request = opener.requests[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, URL + "?wait=true")
        self.assertEqual(json.loads(request.data), {"content": "hello", "allowed_mentions": {"parse": []}})
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertTrue(request.get_header("User-agent").startswith("WFMT/") and "discord" in request.get_header("User-agent"))

    def test_a_thread_is_added_to_the_address(self):
        opener = Opener({"id": "1"})
        C.post(URL, "x", thread="42", opener=opener, sleep=Sleeper())
        self.assertEqual(opener.requests[0].full_url, URL + "?wait=true&thread_id=42")
        opener = Opener({"id": "1"})
        C.post(URL + "?thread_id=77", "x", opener=opener, sleep=Sleeper())
        self.assertTrue(opener.requests[0].full_url.endswith("thread_id=77"))
        with self.assertRaises(C.DiscordError):
            C.post(URL, "x", thread="not a number", opener=Opener(), sleep=Sleeper())

    def test_an_empty_or_long_message_is_refused_before_anything_is_sent(self):
        opener = Opener()
        for text in ("", "   ", "x" * 2001):
            with self.assertRaises(C.DiscordError):
                C.post(URL, text, opener=opener, sleep=Sleeper())
        self.assertEqual(opener.requests, [])

    def test_a_missing_id_in_the_answer_gives_an_empty_id(self):
        self.assertEqual(C.post(URL, "x", opener=Opener(b""), sleep=Sleeper()), "")
        self.assertEqual(C.post(URL, "x", opener=Opener(b"not json"), sleep=Sleeper()), "")


class Editing(unittest.TestCase):
    def test_edit_patches_the_message(self):
        opener = Opener({"id": "555"})
        self.assertEqual(C.edit(URL, "555", "new", opener=opener, sleep=Sleeper()), "555")
        request = opener.requests[0]
        self.assertEqual(request.get_method(), "PATCH")
        self.assertEqual(request.full_url, URL + "/messages/555")
        self.assertEqual(json.loads(request.data)["content"], "new")

    def test_a_deleted_message_says_not_found(self):
        with self.assertRaises(C.NotFound):
            C.edit(URL, "555", "new", opener=Opener(http_error(404)), sleep=Sleeper())

    def test_a_bad_message_id_is_refused(self):
        with self.assertRaises(C.DiscordError):
            C.edit(URL, "../x", "new", opener=Opener(), sleep=Sleeper())

    def test_delete(self):
        opener = Opener(b"")
        C.delete(URL, "555", opener=opener, sleep=Sleeper())
        self.assertEqual((opener.requests[0].get_method(), opener.requests[0].full_url), ("DELETE", URL + "/messages/555"))


class Pauses(unittest.TestCase):
    def test_a_429_is_retried_once_after_the_wait_discord_asks_for(self):
        sleeper = Sleeper()
        opener = Opener(http_error(429, json.dumps({"retry_after": 1.5}).encode()), {"id": "9"})
        self.assertEqual(C.post(URL, "x", opener=opener, sleep=sleeper), "9")
        self.assertEqual(sleeper.waits, [1.5])
        self.assertEqual(len(opener.requests), 2)

    def test_the_wait_is_capped_and_a_header_is_used_when_there_is_no_body(self):
        sleeper = Sleeper()
        C.post(URL, "x", opener=Opener(http_error(429, json.dumps({"retry_after": 600}).encode()), {"id": "9"}), sleep=sleeper)
        C.post(URL, "x", opener=Opener(http_error(429, b"", {"Retry-After": "3"}), {"id": "9"}), sleep=sleeper)
        C.post(URL, "x", opener=Opener(http_error(503), {"id": "9"}), sleep=sleeper)
        self.assertEqual(sleeper.waits, [C.RETRY_WAIT_MAX_S, 3.0, C.RETRY_WAIT_S])

    def test_a_second_429_gives_up_with_a_friendly_message(self):
        opener = Opener(http_error(429), http_error(429))
        with self.assertRaises(C.DiscordError) as caught:
            C.post(URL, "x", opener=opener, sleep=Sleeper())
        self.assertIn("pause", str(caught.exception))
        self.assertEqual(len(opener.requests), 2)


class Errors(unittest.TestCase):
    def test_each_failure_has_its_own_words(self):
        cases = {401: "did not accept", 403: "did not accept", 404: "could not find", 400: "refused", 500: "error (500)"}
        for code, words in cases.items():
            with self.assertRaises(C.DiscordError) as caught:
                C.post(URL, "x", opener=Opener(http_error(code)), sleep=Sleeper())
            self.assertIn(words, str(caught.exception), code)

    def test_a_dropped_connection_is_explained(self):
        for problem in (urllib.error.URLError("down"), OSError("boom"), TimeoutError()):
            with self.assertRaises(C.DiscordError) as caught:
                C.post(URL, "x", opener=Opener(problem), sleep=Sleeper())
            self.assertIn("Could not reach Discord", str(caught.exception))

    def test_the_link_never_appears_in_an_error_or_its_cause(self):
        problems = [http_error(c) for c in (400, 401, 404, 429, 500)] + [urllib.error.URLError(URL), OSError(URL)]
        for problem in problems:
            opener = Opener(problem, problem)
            try:
                C.post(URL, "x", opener=opener, sleep=Sleeper())
            except C.DiscordError as err:
                self.assertNotIn(TOKEN, str(err))
                self.assertNotIn(TOKEN, repr(err))
                self.assertIsNone(err.__cause__)
                self.assertTrue(err.__suppress_context__)
            else:
                self.fail("expected an error")
        with self.assertRaises(C.DiscordError) as caught:
            C.parse_webhook("https://example.com/" + TOKEN)
        self.assertNotIn(TOKEN, str(caught.exception))


class Checking(unittest.TestCase):
    def test_check_reads_the_webhook_without_posting(self):
        opener = Opener({"name": "Squadron BGS", "id": "1"})
        self.assertEqual(C.check(URL, opener=opener, sleep=Sleeper()), "Squadron BGS")
        self.assertEqual((opener.requests[0].get_method(), opener.requests[0].full_url, opener.requests[0].data), ("GET", URL, None))

    def test_an_unnamed_webhook(self):
        self.assertEqual(C.check(URL, opener=Opener(b"{}"), sleep=Sleeper()), "that webhook")


if __name__ == "__main__":
    unittest.main()
