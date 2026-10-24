"""Offline A2 regression: out-of-source HTTP responses must not vanish.

These fixtures use the real HTTP helper and RawRecorder with mocked URL reads.
They neither perform prospective discovery nor verify external responses.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json

import pytest

from harness import acquisition
from harness import http


class _Response:
    def __init__(self, body: bytes, code: int = 200) -> None:
        self.body = body
        self.code = code

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self.body

    def getcode(self) -> int:
        return self.code


def test_direct_unscoped_record_is_not_silently_dropped() -> None:
    recorder = acquisition.RawRecorder()
    raw = b'{"is_oa":true}'
    recorder.record_current("https://example.invalid/oa", None, 200, raw)
    assert recorder.count == 1
    assert recorder.calls[0]["source_id"] == "http_unscoped"
    assert recorder.calls[0]["adapter"] == "harness.http.get_raw"
    assert recorder.calls[0]["body_bytes"] == raw


def test_unscoped_real_http_helper_response_has_verifiable_snapshot(
    tmp_path, monkeypatch
) -> None:
    raw = b'{"is_oa":true}'
    recorder = acquisition.RawRecorder()
    monkeypatch.setattr(http, "RECORDER", recorder)
    monkeypatch.setattr(
        http.urllib.request, "urlopen",
        lambda _request, timeout=30: _Response(raw),
    )
    assert http.get_json("https://example.invalid/oa", {"q": "test"}, tries=1) == {"is_oa": True}
    assert recorder.count == 1
    n, index_sha = recorder.write_snapshot(str(tmp_path))
    assert n == 1
    index_bytes = (tmp_path / "raw" / "INDEX.json").read_bytes()
    assert index_sha == hashlib.sha256(index_bytes).hexdigest()
    entry = json.loads(index_bytes)[0]
    assert entry["source_id"] == "http_unscoped"
    body_path = tmp_path.joinpath(*entry["path"].split("/"))
    body_file = body_path.read_bytes()
    assert hashlib.sha256(body_file).hexdigest() == entry["file_sha256"]
    payload = json.loads(body_file)
    assert payload["url"] == "https://example.invalid/oa"
    assert payload["params"] == {"q": "test"}
    assert payload["adapter"] == "harness.http.get_raw"
    assert payload["body_sha256"] == hashlib.sha256(raw).hexdigest()
    assert base64.b64decode(payload["body_bytes_b64"]) == raw


def test_scoped_sources_retain_original_identity(monkeypatch) -> None:
    recorder = acquisition.RawRecorder()
    monkeypatch.setattr(http, "RECORDER", recorder)
    monkeypatch.setattr(
        http.urllib.request, "urlopen",
        lambda _request, timeout=30: _Response(b'{"ok":true}'),
    )
    with recorder.source("pubmed_concept_query#1", "harness.acquisition.esearch_all"):
        assert http.get_json("https://example.invalid/search", tries=1) == {"ok": True}
    assert recorder.count == 1
    assert recorder.calls[0]["source_id"] == "pubmed_concept_query#1"
    assert recorder.calls[0]["adapter"] == "harness.acquisition.esearch_all"


def test_unscoped_http_failure_body_is_preserved(monkeypatch) -> None:
    recorder = acquisition.RawRecorder()
    monkeypatch.setattr(http, "RECORDER", recorder)

    def unavailable(_request, timeout=30):
        raise http.urllib.error.HTTPError(
            "https://example.invalid/fail", 503, "Service Unavailable",
            {}, io.BytesIO(b"provider down"),
        )

    monkeypatch.setattr(http.urllib.request, "urlopen", unavailable)
    with pytest.raises(RuntimeError, match="GET failed"):
        http.get_raw("https://example.invalid/fail", tries=1)
    assert recorder.count == 1
    assert recorder.calls[0]["source_id"] == "http_unscoped"
    assert recorder.calls[0]["status"] == 503
    assert recorder.calls[0]["body_bytes"] == b"provider down"


def test_scoped_and_unscoped_calls_use_distinct_archive_paths(tmp_path) -> None:
    recorder = acquisition.RawRecorder()
    recorder.record_current("https://example.invalid/oa", None, 200, b"oa")
    with recorder.source("pubmed_concept_query#1", "harness.acquisition.esearch_all"):
        recorder.record_current("https://example.invalid/search", {"term": "x"}, 200, b"search")
    count, index_sha = recorder.write_snapshot(str(tmp_path))
    assert count == 2
    raw_index = (tmp_path / "raw" / "INDEX.json").read_bytes()
    assert index_sha == hashlib.sha256(raw_index).hexdigest()
    entries = json.loads(raw_index)
    assert {entry["source_id"] for entry in entries} == {
        "http_unscoped", "pubmed_concept_query#1",
    }
    assert len({entry["path"] for entry in entries}) == 2
