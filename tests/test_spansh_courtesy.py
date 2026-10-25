"""The courtesy layer for Spansh requests (spansh_courtesy.py): spacing, retries and back-off, the stop after repeated failures, cancel, and the cap on requests in flight. The clock, the sleep and
the network are replaced, so nothing waits and nothing is sent."""
from __future__ import annotations

import errno
import io
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from email.message import Message
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import spansh_courtesy as C  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from fake_dump_server import FakeServer, busy  # noqa: E402


class FakeResponse:
    def __init__(self, body=b"{}"):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code, retry_after=None):
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError("https://spansh.co.uk/x", code, "x", headers, io.BytesIO(b'{"error":"x"}'))


class World:
    """A fake clock that only moves when something sleeps, and an opener that plays back a script of answers."""

    def __init__(self, script):
        self.now = 1000.0
        self.slept = []
        self.script = list(script)
        self.calls = 0
        self.courtesy = C.Courtesy(opener=self.opener, clock=lambda: self.now, sleep=self.sleep, jitter=lambda: 0.0)

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds

    def opener(self, request, timeout=None):
        self.calls += 1
        item = self.script.pop(0) if self.script else FakeResponse()
        if isinstance(item, BaseException):
            raise item
        return item

    def get(self):
        return urllib.request.Request("https://spansh.co.uk/api/x")

    def post(self):
        return urllib.request.Request("https://spansh.co.uk/api/x", data=b"a=1", method="POST")


class SpacingTests(unittest.TestCase):
    def test_a_request_is_not_delayed_when_it_is_the_first(self):
        world = World([FakeResponse(b"one")])
        self.assertEqual(world.courtesy.call(world.get(), 5), b"one")
        self.assertEqual(world.slept, [])

    def test_requests_are_spaced_apart(self):
        world = World([FakeResponse(), FakeResponse(), FakeResponse()])
        for _ in range(3):
            world.courtesy.call(world.get(), 5)
        self.assertEqual(len(world.slept), 2)
        self.assertTrue(all(abs(gap - C.MIN_GAP_S) < 1e-9 for gap in world.slept), world.slept)

    def test_no_more_than_the_limit_are_in_flight(self):
        gate = threading.Event()
        state = {"now": 0, "most": 0}
        lock = threading.Lock()

        def opener(request, timeout=None):
            with lock:
                state["now"] += 1
                state["most"] = max(state["most"], state["now"])
            gate.wait(0.2)
            with lock:
                state["now"] -= 1
            return FakeResponse()

        courtesy = C.Courtesy(opener=opener, sleep=lambda s: None)
        threads = [threading.Thread(target=courtesy.call, args=(urllib.request.Request("https://spansh.co.uk/api/x"), 5)) for _ in range(8)]
        for thread in threads:
            thread.start()
        time.sleep(0.05)
        gate.set()
        for thread in threads:
            thread.join(5)
        self.assertLessEqual(state["most"], C.MAX_CONCURRENT)
        self.assertEqual(courtesy.requests, 8)


class RetryTests(unittest.TestCase):
    def test_a_busy_answer_is_retried_with_growing_waits(self):
        world = World([http_error(503), http_error(429), FakeResponse(b"ok")])
        self.assertEqual(world.courtesy.call(world.get(), 5), b"ok")
        waits = [s for s in world.slept if s >= 1]
        self.assertEqual(waits, [C.BACKOFF_S[0], C.BACKOFF_S[1]])
        self.assertEqual(world.courtesy.retries, 2)

    def test_retry_after_is_honored_and_capped(self):
        world = World([http_error(429, retry_after=30), http_error(429, retry_after=9999), FakeResponse()])
        world.courtesy.call(world.get(), 5)
        waits = [s for s in world.slept if s >= 1]
        self.assertEqual(waits, [30.0, C.MAX_WAIT_S])

    def test_it_gives_up_after_the_retries(self):
        world = World([http_error(503)] * (C.MAX_RETRIES + 1))
        with self.assertRaises(urllib.error.HTTPError):
            world.courtesy.call(world.get(), 5)
        self.assertEqual(world.calls, C.MAX_RETRIES + 1)

    def test_retries_zero_tries_once_and_does_not_wait(self):
        world = World([http_error(503), FakeResponse(b"ok")])
        with self.assertRaises(urllib.error.HTTPError):
            world.courtesy.call(world.get(), 5, retries=0)
        self.assertEqual(world.calls, 1)
        self.assertEqual([s for s in world.slept if s >= 1], [])
        self.assertEqual(world.courtesy.retries, 0)

    def test_retries_cannot_exceed_the_limit(self):
        world = World([http_error(503)] * 20)
        with self.assertRaises(urllib.error.HTTPError):
            world.courtesy.call(world.get(), 5, retries=50)
        self.assertEqual(world.calls, C.MAX_RETRIES + 1)

    def test_an_answer_that_is_a_refusal_is_not_retried(self):
        for code in (400, 404, 422):
            world = World([http_error(code)])
            with self.assertRaises(urllib.error.HTTPError) as caught:
                world.courtesy.call(world.get(), 5)
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(world.calls, 1)

    def test_a_timeout_is_retried_for_a_get_but_not_for_a_post(self):
        get = World([TimeoutError("slow"), FakeResponse(b"ok")])
        self.assertEqual(get.courtesy.call(get.get(), 5), b"ok")
        post = World([TimeoutError("slow"), FakeResponse(b"ok")])
        with self.assertRaises(TimeoutError):
            post.courtesy.call(post.post(), 5)
        self.assertEqual(post.calls, 1, "a POST that may have been accepted is not sent twice")

    def test_a_post_rejected_as_busy_is_retried(self):
        world = World([http_error(503), FakeResponse(b"ok")])
        self.assertEqual(world.courtesy.call(world.post(), 5), b"ok")

    def test_cancel_during_a_wait_stops_at_once(self):
        cancel = threading.Event()
        cancel.set()
        world = World([http_error(503), FakeResponse()])
        with self.assertRaises(C.Cancelled):
            world.courtesy.call(world.get(), 5, cancel)
        self.assertEqual(world.calls, 1)


class BreakerTests(unittest.TestCase):
    def fail_once(self, world):
        world.script = [http_error(503)] * (C.MAX_RETRIES + 1)
        with self.assertRaises(urllib.error.HTTPError):
            world.courtesy.call(world.get(), 5)

    def test_repeated_failures_stop_further_requests_for_a_while(self):
        world = World([])
        for _ in range(C.BREAKER_FAILURES):
            self.fail_once(world)
        calls = world.calls
        with self.assertRaises(C.SpanshBusy) as caught:
            world.courtesy.call(world.get(), 5)
        self.assertIn("minute", str(caught.exception))
        self.assertEqual(world.calls, calls, "nothing was sent while it is stopped")
        self.assertEqual(world.courtesy.refused, 1)

    def test_it_asks_again_after_the_pause(self):
        world = World([])
        for _ in range(C.BREAKER_FAILURES):
            self.fail_once(world)
        world.now += C.BREAKER_S + 1
        world.script = [FakeResponse(b"back")]
        self.assertEqual(world.courtesy.call(world.get(), 5), b"back")

    def test_a_success_resets_the_count(self):
        world = World([])
        for _ in range(C.BREAKER_FAILURES - 1):
            self.fail_once(world)
        world.script = [FakeResponse()]
        world.courtesy.call(world.get(), 5)
        self.fail_once(world)
        world.script = [FakeResponse()]
        self.assertEqual(world.courtesy.call(world.get(), 5), b"{}")

    def test_a_refusal_counts_as_an_answer_not_a_failure(self):
        world = World([http_error(404)] * (C.BREAKER_FAILURES + 2))
        for _ in range(C.BREAKER_FAILURES + 2):
            with self.assertRaises(urllib.error.HTTPError):
                world.courtesy.call(world.get(), 5)
        world.script = [FakeResponse()]
        world.courtesy.call(world.get(), 5)           # still allowed

    def test_the_counters_are_available_for_the_diagnostics(self):
        world = World([FakeResponse()])
        world.courtesy.call(world.get(), 5)
        self.assertEqual(world.courtesy.stats(), {"requests": 1, "retries": 0, "refused": 0})


class StreamWorld:
    """A courtesy layer on a fake clock, whose opener is a fake file server."""

    def __init__(self, server):
        self.now = 1000.0
        self.slept = []
        self.server = server
        self.courtesy = C.Courtesy(opener=server, clock=lambda: self.now, sleep=self.sleep, jitter=lambda: 0.0)
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "file.part")

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds

    def get(self):
        return urllib.request.Request("https://downloads.spansh.co.uk/file.gz", headers={"User-Agent": "WFMT-test"})

    def stream(self, **options):
        return self.courtesy.stream_to_file(self.get(), 5, self.path, **options)

    def written(self):
        with open(self.path, "rb") as handle:
            return handle.read()

    def close(self):
        self._tmp.cleanup()


BODY = bytes(range(256)) * 2000          # 512,000 bytes: several chunks


class StreamTests(unittest.TestCase):
    def world(self, **kw):
        world = StreamWorld(FakeServer(BODY, **kw))
        self.addCleanup(world.close)
        return world

    def test_the_body_is_written_with_progress(self):
        world = self.world()
        seen = []
        result = world.stream(progress=lambda done, total: seen.append((done, total)))
        self.assertEqual(world.written(), BODY)
        self.assertEqual((result.status, result.size, result.total, result.etag), (200, len(BODY), len(BODY), '"v1"'))
        self.assertGreater(len(seen), 1)
        self.assertEqual(seen[-1], (len(BODY), len(BODY)))
        self.assertEqual([done for done, _t in seen], sorted(done for done, _t in seen))

    def test_it_goes_through_the_same_gate_and_counts_the_request(self):
        world = self.world()
        world.stream()
        world.stream()
        self.assertEqual(world.courtesy.stats()["requests"], 2)
        self.assertEqual(len(world.slept), 1)
        self.assertAlmostEqual(world.slept[0], C.MIN_GAP_S)

    def test_resume_sends_a_range_and_appends(self):
        world = self.world()
        with open(world.path, "wb") as handle:
            handle.write(BODY[:100000])
        result = world.stream(resume_from=100000)
        self.assertEqual(world.server.requests[0]["range"], "bytes=100000-")
        self.assertEqual((result.status, result.size, result.total, result.restarted), (206, len(BODY), len(BODY), False))
        self.assertEqual(world.written(), BODY)

    def test_a_server_that_ignores_range_restarts_the_file(self):
        world = self.world(ranges=False)
        with open(world.path, "wb") as handle:
            handle.write(b"stale bytes" * 1000)
        result = world.stream(resume_from=11000)
        self.assertTrue(result.restarted)
        self.assertEqual(result.status, 200)
        self.assertEqual(world.written(), BODY)

    def test_a_dropped_connection_continues_from_what_was_written(self):
        world = self.world(script=[("drop", 300000)])
        result = world.stream()
        self.assertEqual(world.written(), BODY)
        self.assertEqual(len(world.server.requests), 2)
        self.assertEqual(world.server.requests[1]["range"], "bytes=300000-")
        self.assertEqual(world.courtesy.stats()["retries"], 1)
        self.assertEqual(result.size, len(BODY))

    def test_a_busy_answer_is_retried_with_a_wait(self):
        world = self.world(script=[busy(503), busy(429)])
        world.stream()
        self.assertEqual(world.written(), BODY)
        self.assertEqual(world.slept[-2:], [C.BACKOFF_S[0], C.BACKOFF_S[1]])

    def test_it_gives_up_after_the_retries_and_the_breaker_opens_after_repeated_failures(self):
        world = self.world(script=[busy(503)] * (C.MAX_RETRIES + 1) * C.BREAKER_FAILURES)
        for _ in range(C.BREAKER_FAILURES):
            with self.assertRaises(urllib.error.HTTPError):
                world.stream()
        with self.assertRaises(C.SpanshBusy):
            world.stream()

    def test_a_conditional_request_that_is_not_modified_writes_nothing(self):
        world = self.world()
        request = urllib.request.Request("https://downloads.spansh.co.uk/file.gz", headers={"If-None-Match": '"v1"'})
        result = world.courtesy.stream_to_file(request, 5, world.path)
        self.assertTrue(result.not_modified)
        self.assertFalse(os.path.exists(world.path))

    def test_a_refusal_is_raised_and_not_retried(self):
        world = self.world(script=[http_error(404)])
        with self.assertRaises(urllib.error.HTTPError):
            world.stream()
        self.assertEqual(len(world.server.requests), 1)

    def test_range_not_satisfiable_is_raised_for_the_caller_to_handle(self):
        world = self.world()
        with open(world.path, "wb") as handle:
            handle.write(BODY)
        with self.assertRaises(urllib.error.HTTPError) as caught:
            world.stream(resume_from=len(BODY))
        self.assertEqual(caught.exception.code, 416)

    def test_the_size_cap_refuses_before_writing_when_the_server_announces_too_much(self):
        world = self.world()
        with self.assertRaises(C.TooLarge):
            world.stream(max_bytes=len(BODY) - 1)
        self.assertFalse(os.path.exists(world.path))

    def test_the_size_cap_stops_a_stream_that_grows_past_it(self):
        world = self.world()
        original = world.server.__call__

        def lying(request, timeout=None):
            response = original(request, timeout)
            del response.headers["Content-Length"]            # a server that does not say how large the file is
            return response

        world.courtesy._opener = lying
        with self.assertRaises(C.TooLarge):
            world.stream(max_bytes=200000)
        self.assertLessEqual(os.path.getsize(world.path), 200000)

    def test_cancel_stops_the_stream_and_keeps_the_partial_file(self):
        world = self.world()
        cancel = threading.Event()

        def progress(done, total):
            if done >= C.STREAM_CHUNK:
                cancel.set()

        with self.assertRaises(C.Cancelled):
            world.stream(cancel=cancel, progress=progress)
        self.assertEqual(os.path.getsize(world.path), C.STREAM_CHUNK)
        self.assertEqual(world.written(), BODY[:C.STREAM_CHUNK])

    def test_cancel_during_a_retry_wait_stops_at_once(self):
        world = self.world(script=[busy(503), busy(503)])
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(C.Cancelled):
            world.stream(cancel=cancel)
        self.assertEqual(len(world.server.requests), 1)

    def test_on_response_can_refuse_before_anything_is_written(self):
        world = self.world()

        def refuse(answer):
            raise C.Refused("no room")

        with self.assertRaises(C.Refused):
            world.stream(on_response=refuse)
        self.assertFalse(os.path.exists(world.path))
        self.assertEqual(len(world.server.requests), 1)           # a refusal is final, not retried

    def test_a_local_disk_error_is_not_blamed_on_the_server_or_retried(self):
        world = self.world()
        with mock.patch("builtins.open", side_effect=OSError(errno.ENOSPC, "No space left on device")):
            with self.assertRaises(OSError):
                world.stream()
        self.assertEqual(len(world.server.requests), 1)
        self.assertEqual(world.courtesy._failures, 0)

    def test_only_a_get_can_be_streamed(self):
        world = self.world()
        with self.assertRaises(ValueError):
            world.courtesy.stream_to_file(urllib.request.Request("https://x/", data=b"a", method="POST"), 5, world.path)

    def test_the_shared_instance_has_a_module_level_entry_point(self):
        self.assertTrue(callable(C.stream_to_file))


if __name__ == "__main__":
    unittest.main()
