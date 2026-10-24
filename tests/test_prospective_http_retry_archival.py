"""A2 evidence-integrity regressions for HTTP responses received during retries.

All URL responses below are intentionally mocked. These tests do not constitute
prospective searches, provider authentication or independent clinical validation.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import urllib.error

import pytest

from harness import acquisition, http


class _Reply:
    def __init__(self, body: bytes, status: int = 200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body

    def getcode(self):
        return self.status


def _http_error(status: int, body: bytes) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://example.invalid/concept", status, "mock HTTP error",
        {}, io.BytesIO(body),
    )


def _install(recorder, monkeypatch, replies):
    attempts = iter(replies)

    def fake_open(_req, timeout=30):
        response = next(attempts)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(http, "RECORDER", recorder)
    monkeypatch.setattr(http.urllib.request, "urlopen", fake_open)
    monkeypatch.setattr(http.time, "sleep", lambda _delay: None)


def test_intermediate_503_body_is_retained_after_200_recovery(monkeypatch):
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [
        _http_error(503, b"temporary service fault"),
        _Reply(b'{"count":1}'),
    ])
    assert http.get_raw("https://example.invalid/concept", tries=2) == (200, b'{"count":1}')
    assert [c["status"] for c in recorder.calls] == [503, 200]
    assert [c["body_bytes"] for c in recorder.calls] == [
        b"temporary service fault", b'{"count":1}',
    ]
    assert all(c["source_id"] == "http_unscoped" for c in recorder.calls)


def test_each_failed_http_response_preserved_before_final_refusal(monkeypatch):
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [
        _http_error(429, b"rate-limited"),
        _http_error(503, b"unavailable"),
    ])
    with pytest.raises(RuntimeError, match="GET failed after 2 tries"):
        http.get_raw("https://example.invalid/concept", tries=2)
    assert [c["status"] for c in recorder.calls] == [429, 503]
    assert [c["body_bytes"] for c in recorder.calls] == [b"rate-limited", b"unavailable"]


def test_retried_responses_preserve_registered_discovery_source(monkeypatch):
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [
        _http_error(503, b"unavailable"), _Reply(b'{"count":0}'),
    ])
    with recorder.source("pubmed_concept_query#1", "harness.acquisition.esearch_all"):
        assert http.get_json("https://example.invalid/concept", tries=2) == {"count": 0}
    assert [c["source_id"] for c in recorder.calls] == ["pubmed_concept_query#1"] * 2
    assert [c["adapter"] for c in recorder.calls] == ["harness.acquisition.esearch_all"] * 2


def test_connection_exception_without_http_body_is_not_faked(monkeypatch):
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [
        urllib.error.URLError("connection failed"), _Reply(b"received"),
    ])
    assert http.get_raw("https://example.invalid/concept", tries=2) == (200, b"received")
    # No HTTP response bytes were received on the failed connection.
    assert len(recorder.calls) == 1
    assert recorder.calls[0]["status"] == 200
    assert recorder.calls[0]["body_bytes"] == b"received"


def test_snapshot_hashes_cover_intermediate_and_successful_responses(tmp_path, monkeypatch):
    recorder = acquisition.RawRecorder()
    bodies = [b"temporary provider error", b'{"hits":2}']
    _install(recorder, monkeypatch, [_http_error(503, bodies[0]), _Reply(bodies[1])])
    assert http.get_raw("https://example.invalid/concept", {"q": "trial"}, tries=2) == (200, bodies[1])
    n, digest = recorder.write_snapshot(str(tmp_path))
    index_bytes = (tmp_path / "raw" / "INDEX.json").read_bytes()
    assert n == 2
    assert digest == hashlib.sha256(index_bytes).hexdigest()
    index = json.loads(index_bytes)
    assert [row["status"] for row in index] == [503, 200]
    assert len({row["path"] for row in index}) == 2
    for row, received in zip(index, bodies):
        stored_bytes = tmp_path.joinpath(*row["path"].split("/")).read_bytes()
        assert hashlib.sha256(stored_bytes).hexdigest() == row["file_sha256"]
        payload = json.loads(stored_bytes)
        assert payload["body_sha256"] == hashlib.sha256(received).hexdigest()
        assert row["body_sha256"] == payload["body_sha256"]
        assert base64.b64decode(payload["body_bytes_b64"], validate=True) == received
        assert payload["params"] == {"q": "trial"}


def test_empty_http_error_body_is_not_replaced_by_exception_text(monkeypatch):
    """A received zero-byte 503 is not an invented provider error message."""
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [
        _http_error(503, b""), _Reply(b'{"count":0}'),
    ])
    assert http.get_raw("https://example.invalid/concept", tries=2) == (
        200, b'{"count":0}',
    )
    assert [call["status"] for call in recorder.calls] == [503, 200]
    assert recorder.calls[0]["body_bytes"] == b""
    assert recorder.calls[0]["body_sha256"] == hashlib.sha256(b"").hexdigest()


def test_terminal_empty_http_error_refuses_without_inventing_body(monkeypatch):
    """Terminal HTTP errors still refuse while recording exact zero bytes."""
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [_http_error(404, b"")])
    with pytest.raises(RuntimeError, match="GET failed after 1 tries"):
        http.get_raw("https://example.invalid/concept", tries=1)
    assert len(recorder.calls) == 1
    assert recorder.calls[0]["status"] == 404
    assert recorder.calls[0]["body_bytes"] == b""


def test_empty_http_error_snapshot_has_empty_sha256_and_base64(tmp_path, monkeypatch):
    """INDEX and stored body receipts must verify the actual empty wire body."""
    recorder = acquisition.RawRecorder()
    _install(recorder, monkeypatch, [_http_error(503, b"")])
    with pytest.raises(RuntimeError, match="GET failed after 1 tries"):
        http.get_raw("https://example.invalid/concept", tries=1)

    count, index_sha = recorder.write_snapshot(str(tmp_path))
    index_bytes = (tmp_path / "raw" / "INDEX.json").read_bytes()
    assert count == 1
    assert index_sha == hashlib.sha256(index_bytes).hexdigest()
    row = json.loads(index_bytes)[0]
    assert row["status"] == 503
    assert row["body_sha256"] == hashlib.sha256(b"").hexdigest()
    body_record_bytes = tmp_path.joinpath(*row["path"].split("/")).read_bytes()
    assert hashlib.sha256(body_record_bytes).hexdigest() == row["file_sha256"]
    payload = json.loads(body_record_bytes)
    assert payload["body_bytes_b64"] == ""
    assert base64.b64decode(payload["body_bytes_b64"], validate=True) == b""
    assert payload["body_sha256"] == row["body_sha256"]
