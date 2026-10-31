"""A polite way to call Spansh: every request WFMT makes to spansh.co.uk can go through here.

Spansh is a community service that many tools use, and every WFMT user's requests reach it from their own address. WFMT keeps its own part of that traffic small and well behaved:

- **Few at a time, spaced out.** At most `MAX_CONCURRENT` requests are in flight, and at least `MIN_GAP_S` passes between the starts of two requests, across every thread of the plugin.
- **Back off when Spansh is busy.** A 429, 502, 503 or 504 answer is retried up to `MAX_RETRIES` times, waiting longer each time (or as long as a `Retry-After` header says, up to
  `MAX_WAIT_S`). A network timeout is retried only for a GET: a POST that timed out may have been accepted, and sending it again could start a second job.
- **Stop when it keeps failing.** After `BREAKER_FAILURES` failed requests in a row (each already retried) WFMT refuses to call Spansh for `BREAKER_S` seconds and says so, instead of
  continuing to ask a service that is already having trouble.
- **Say who is asking.** The callers send WFMT's User-Agent (`http_identity`), so Spansh can tell these requests from anyone else's.

A caller that is answering a keystroke (the system-name suggestions) passes `retries=0`: it still goes through the gate and the breaker, but a busy answer is returned as an error at once, because a
suggestion that arrives after several seconds of waiting is for text the player has already changed.

`call` returns the body of the answer. `stream_to_file` is the same layer for an answer too large to hold in memory (a data dump): it writes the body to a file in chunks, can resume with a
Range request, and can answer "not modified" to a conditional request. An answer that is not worth retrying (400, 404, 422 and so on) raises `urllib.error.HTTPError` unchanged for the caller to read, as before.
The clock, the sleep and the opener are injectable so the behavior is tested without waiting or a network.
"""
from __future__ import annotations

import errno
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

MAX_CONCURRENT = 2
MIN_GAP_S = 0.25
MAX_RETRIES = 3
BACKOFF_S = (2.0, 6.0, 15.0)        # the wait before the first, second and third retry (a little random jitter is added)
MAX_WAIT_S = 60.0                   # the longest wait a Retry-After header can ask for
BREAKER_FAILURES = 5
BREAKER_S = 300.0
RETRY_STATUS = (429, 502, 503, 504)
STREAM_CHUNK = 256 * 1024           # how much of a streamed body is read at a time
_LOCAL_ERRNOS = (errno.ENOSPC, errno.EACCES, errno.EROFS, errno.EDQUOT)    # a problem with the local disk, not with Spansh


def _int(value: Optional[str]) -> int:
    try:
        return max(0, int(value)) if value is not None else 0
    except ValueError:
        return 0


def _total_from(status: int, content_range: Optional[str], length: int, have: int) -> int:
    """The size of the whole file: from `Content-Range: bytes 100-999/1000` for a partial answer, else what is already held plus the length of this body (0 when unknown)."""
    if status == 206 and content_range and "/" in content_range:
        total = _int(content_range.rsplit("/", 1)[1])
        if total:
            return total
    return have + length if length else 0


class SpanshBusy(OSError):
    """WFMT is not asking Spansh for now because it has been failing; the message says for how long."""


class Cancelled(OSError):
    """The caller cancelled while WFMT was waiting to retry (or while a streamed download was running)."""


class Refused(OSError):
    """The caller's `on_response` check refused a streamed download (for example, not enough disk space); it is not retried."""


class TooLarge(Refused):
    """A streamed body is larger than the caller allows."""


@dataclass
class StreamResult:
    """What `stream_to_file` did: the HTTP status (200, 206 or 304), the size the file has now, the size of the whole file where the server said (0 if not), the validators the caller
    keeps (etag, last-modified), and whether the file was started again from the beginning because the server did not honor the Range request."""
    status: int = 0
    size: int = 0
    total: int = 0
    etag: str = ""
    last_modified: str = ""
    restarted: bool = False
    headers: Dict[str, str] = field(default_factory=dict)

    @property
    def not_modified(self) -> bool:
        return self.status == 304


class Courtesy:
    def __init__(self, opener: Callable[..., Any] = urllib.request.urlopen, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep, jitter: Callable[[], float] = random.random) -> None:
        self._opener = opener
        self._clock = clock
        self._sleep = sleep
        self._jitter = jitter
        self._slots = threading.BoundedSemaphore(MAX_CONCURRENT)
        self._lock = threading.Lock()
        self._next_start = 0.0
        self._failures = 0
        self._open_until = 0.0
        self.requests = 0               # for the diagnostics: how many requests went out this session
        self.retries = 0
        self.refused = 0

    # --- the gate ------------------------------------------------------------------------------------------------------
    def _wait_turn(self) -> None:
        """Wait until at least MIN_GAP_S has passed since the last request started."""
        with self._lock:
            now = self._clock()
            start = max(now, self._next_start)
            self._next_start = start + MIN_GAP_S
        if start > now:
            self._sleep(start - now)

    def _check_breaker(self) -> None:
        with self._lock:
            remaining = self._open_until - self._clock()
            if remaining > 0:
                self.refused += 1
                raise SpanshBusy(f"Spansh has not been answering, so WFMT is not asking it for another {max(1, round(remaining / 60))} minute(s).")

    def _failed(self) -> None:
        with self._lock:
            self._failures += 1
            if self._failures >= BREAKER_FAILURES:
                self._open_until = self._clock() + BREAKER_S
                self._failures = 0

    def _succeeded(self) -> None:
        with self._lock:
            self._failures = 0

    # --- the call ------------------------------------------------------------------------------------------------------
    def _delay(self, attempt: int, error: Optional[BaseException]) -> float:
        wait = BACKOFF_S[min(attempt, len(BACKOFF_S) - 1)] * (1.0 + 0.25 * self._jitter())
        header = error.headers.get("Retry-After") if isinstance(error, urllib.error.HTTPError) and error.headers is not None else None
        if header is not None:
            try:
                wait = max(wait, float(header))
            except ValueError:
                pass
        return min(wait, MAX_WAIT_S)

    @staticmethod
    def _note(request: urllib.request.Request, outcome: str, began: float, attempt: int, size: int = 0) -> None:
        """A line in the diagnostic log (if it is on): the endpoint without its query, the outcome, the time taken and which try it was."""
        from . import diag_log
        if diag_log.enabled():
            parts = urllib.parse.urlsplit(request.full_url)
            diag_log.log("spansh", f"{request.get_method()} {parts.netloc}{parts.path}", outcome=outcome, ms=int((time.monotonic() - began) * 1000),
                         attempt=attempt + 1, bytes=size)

    def call(self, request: urllib.request.Request, timeout: float, cancel: Optional[threading.Event] = None, retries: Optional[int] = None) -> bytes:
        """The body of Spansh's answer to `request`. Raises SpanshBusy while the breaker is open, Cancelled if `cancel` is set during a wait, urllib.error.HTTPError for an
        answer that is not retried (or still failing after the retries), and the network error after the last retry. `retries` overrides MAX_RETRIES (0 = try once)."""
        self._check_breaker()
        began = time.monotonic()
        is_get = (request.get_method() == "GET")
        limit = MAX_RETRIES if retries is None else max(0, min(int(retries), MAX_RETRIES))
        for attempt in range(limit + 1):
            error: Optional[BaseException] = None
            self._wait_turn()
            with self._slots:
                self.requests += 1
                try:
                    with self._opener(request, timeout=timeout) as response:
                        body = response.read()
                    self._succeeded()
                    self._note(request, "ok", began, attempt, len(body))
                    return body
                except urllib.error.HTTPError as err:
                    if err.code not in RETRY_STATUS:
                        self._succeeded()                    # an answer, even a refusal of this request, means Spansh is up
                        self._note(request, f"http {err.code}", began, attempt)
                        raise
                    error = err
                except (OSError, TimeoutError) as err:       # URLError and timeouts
                    if not is_get:
                        self._failed()
                        self._note(request, f"error {type(err).__name__}", began, attempt)
                        raise
                    error = err
            if attempt >= limit:
                self._failed()
                assert error is not None
                self._note(request, f"gave up: {error}", began, attempt)
                raise error
            self.retries += 1
            delay = self._delay(attempt, error)
            if cancel is not None:
                if cancel.wait(delay):
                    raise Cancelled("Cancelled.")
            else:
                self._sleep(delay)
        raise AssertionError("unreachable")                  # pragma: no cover

    def stream_to_file(self, request: urllib.request.Request, timeout: float, path: str, cancel: Optional[threading.Event] = None,
                       progress: Optional[Callable[[int, int], None]] = None, resume_from: int = 0, max_bytes: Optional[int] = None,
                       on_response: Optional[Callable[[StreamResult], None]] = None, retries: Optional[int] = None) -> StreamResult:
        """Writes the body of a GET to `path` in chunks, through the same gate, concurrency cap and breaker as `call`, with the same retries (a busy answer or a network error, for a GET).
        `resume_from` is how many bytes of `path` the caller already has: the request then carries a Range header, and if the server answers 200 instead of 206 the file is started
        again from the beginning (`restarted`). A failure part-way through is retried the same way, continuing from what was written.

        `on_response` is called with the answer's headers before any body is written and may raise to refuse the download (not enough disk space, a size that is too large); the partial
        file is then left as it was. `progress(written, total)` is called after each chunk (total 0 when the server does not say). `max_bytes` stops the stream with TooLarge when the file
        would grow past it. A 304 answer to a conditional request returns a result with `not_modified` and writes nothing. Cancelling raises Cancelled and leaves the partial file for a
        later resume; any other answer that is not retried raises urllib.error.HTTPError, as in `call`."""
        if request.get_method() != "GET":
            raise ValueError("stream_to_file is for GET requests")
        self._check_breaker()
        limit = MAX_RETRIES if retries is None else max(0, min(int(retries), MAX_RETRIES))
        have = max(0, int(resume_from))
        for attempt in range(limit + 1):
            error: Optional[BaseException] = None
            self._wait_turn()
            with self._slots:
                self.requests += 1
                attempt_request = request
                if have > 0:
                    attempt_request = urllib.request.Request(request.full_url, headers=dict(request.header_items()), method="GET")
                    attempt_request.add_header("Range", f"bytes={have}-")
                try:
                    with self._opener(attempt_request, timeout=timeout) as response:
                        status = int(getattr(response, "status", None) or response.getcode())
                        headers = response.headers
                        result = StreamResult(status=status, size=have, etag=headers.get("ETag") or "", last_modified=headers.get("Last-Modified") or "")
                        result.headers = {key: headers.get(key) or "" for key in ("Content-Length", "Content-Range", "Accept-Ranges", "Content-Type")}
                        if status == 200 and have > 0:
                            have = 0                                 # the server ignored the Range request: begin again
                            result.restarted = True
                            result.size = 0
                        result.total = _total_from(status, headers.get("Content-Range"), _int(headers.get("Content-Length")), have)
                        if max_bytes is not None and result.total > max_bytes:
                            raise TooLarge(f"The file is {result.total:,} bytes, more than the {max_bytes:,} allowed.")
                        if on_response is not None:
                            on_response(result)
                        with open(path, "ab" if have > 0 else "wb") as out:
                            while True:
                                if cancel is not None and cancel.is_set():
                                    raise Cancelled("Cancelled.")
                                chunk = response.read(STREAM_CHUNK)
                                if not chunk:
                                    break
                                if max_bytes is not None and have + len(chunk) > max_bytes:
                                    raise TooLarge(f"The file is larger than the {max_bytes:,} bytes allowed.")
                                out.write(chunk)
                                have += len(chunk)
                                if progress is not None:
                                    progress(have, result.total)
                    result.size = have
                    self._succeeded()
                    return result
                except urllib.error.HTTPError as err:
                    if err.code == 304:
                        self._succeeded()
                        return StreamResult(status=304, size=have, etag=(err.headers.get("ETag") or "") if err.headers is not None else "")
                    if err.code not in RETRY_STATUS:
                        self._succeeded()
                        raise
                    error = err
                except (Refused, Cancelled):
                    raise
                except (OSError, TimeoutError) as err:
                    if isinstance(err, PermissionError) or getattr(err, "errno", None) in _LOCAL_ERRNOS:
                        raise
                    error = err
            if attempt >= limit:
                self._failed()
                assert error is not None
                raise error
            self.retries += 1
            delay = self._delay(attempt, error)
            if cancel is not None:
                if cancel.wait(delay):
                    raise Cancelled("Cancelled.")
            else:
                self._sleep(delay)
        raise AssertionError("unreachable")                  # pragma: no cover

    def stats(self) -> Dict[str, int]:
        return {"requests": self.requests, "retries": self.retries, "refused": self.refused}


default = Courtesy()


def stream_to_file(request: urllib.request.Request, timeout: float, path: str, **options: Any) -> StreamResult:
    """`Courtesy.stream_to_file` on the plugin's one shared instance."""
    return default.stream_to_file(request, timeout, path, **options)


def call(request: urllib.request.Request, timeout: float, cancel: Optional[threading.Event] = None, retries: Optional[int] = None) -> bytes:
    """`Courtesy.call` on the plugin's one shared instance, so every caller shares the same gate and the same breaker."""
    return default.call(request, timeout, cancel, retries)
