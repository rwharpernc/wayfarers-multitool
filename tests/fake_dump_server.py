"""A fake download server for tests: an opener that answers like a web server holding one file, so streaming, resuming and conditional requests are tested without a network (not a test itself).

`FakeServer(body, etag=..., ranges=True)` is passed as the `opener` of a Courtesy. It records every request's headers in `requests`, honors Range (answering 206 with Content-Range, or 200 with the
whole file when `ranges` is False), If-Range (a different validator gets the whole file), If-None-Match and, when there is none, If-Modified-Since (304) and an out-of-range start (416). `script` is a list of things to do to the next
requests: an exception to raise, or ("drop", n) to deliver n bytes of the body and then fail the connection.
"""
from __future__ import annotations

import io
import urllib.error
import urllib.request
from email.message import Message
from typing import Any, List, Optional


class StreamResponse:
    def __init__(self, body: bytes, status: int, headers: Message, drop_after: Optional[int] = None) -> None:
        self._body = io.BytesIO(body)
        self.status = status
        self.headers = headers
        self._drop_after = drop_after
        self._sent = 0

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:
        if self._drop_after is not None and self._sent >= self._drop_after:
            raise ConnectionResetError("connection dropped")
        if self._drop_after is not None:
            size = min(size if size > 0 else self._drop_after, self._drop_after - self._sent)
        chunk = self._body.read(size)
        self._sent += len(chunk)
        return chunk

    def __enter__(self) -> "StreamResponse":
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False


def _headers(**fields: str) -> Message:
    message = Message()
    for key, value in fields.items():
        message[key.replace("_", "-")] = value
    return message


class FakeServer:
    def __init__(self, body: bytes, etag: str = '"v1"', last_modified: str = "Wed, 21 Oct 2026 06:26:22 GMT", ranges: bool = True, script: Optional[List[Any]] = None) -> None:
        self.body = body
        self.etag = etag
        self.last_modified = last_modified
        self.ranges = ranges
        self.script = list(script or [])
        self.requests: List[dict] = []
        self.urls: List[str] = []

    def __call__(self, request: urllib.request.Request, timeout: Optional[float] = None) -> StreamResponse:
        sent = {key.lower(): value for key, value in request.header_items()}
        self.requests.append(sent)
        self.urls.append(request.full_url)
        step = self.script.pop(0) if self.script else None
        if isinstance(step, BaseException):
            raise step
        drop = step[1] if isinstance(step, tuple) and step[0] == "drop" else None
        common = dict(ETag=self.etag, Last_Modified=self.last_modified, Accept_Ranges="bytes" if self.ranges else "none")
        if sent.get("if-none-match") == self.etag or ("if-none-match" not in sent and sent.get("if-modified-since") == self.last_modified):
            raise urllib.error.HTTPError(request.full_url, 304, "Not Modified", _headers(**common), io.BytesIO(b""))
        total = len(self.body)
        start = 0
        if "range" in sent and self.ranges:
            start = int(sent["range"].split("=")[1].rstrip("-"))
            if "if-range" in sent and sent["if-range"] not in (self.etag, self.last_modified):
                start = 0
            elif start >= total:
                raise urllib.error.HTTPError(request.full_url, 416, "Range Not Satisfiable", _headers(**common), io.BytesIO(b""))
        if start:
            return StreamResponse(self.body[start:], 206, _headers(Content_Length=str(total - start), Content_Range=f"bytes {start}-{total - 1}/{total}", **common), drop)
        return StreamResponse(self.body, 200, _headers(Content_Length=str(total), **common), drop)


def busy(code: int = 503) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://downloads.spansh.co.uk/x", code, "busy", _headers(), io.BytesIO(b""))
