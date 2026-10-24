"""Refuse duplicate JSON members in externally released prospective topic inputs.

Structural failure-injection fixtures only. No live retrieval, independent
clinical adjudication, held-out release, R validation or scientific accuracy
claim is made by these tests.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import run_prospective_topic as runner


def _synthetic_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        runner.prospective,
        "load_declaration",
        lambda *_args: {"time_limit_s": 60, "invariants": []},
    )
    monkeypatch.setattr(
        runner.prospective, "check_declaration_frozen", lambda *_args: None
    )
    monkeypatch.setattr(
        runner.prospective.architecture_identity, "identity", lambda *_args: "f" * 64
    )
    monkeypatch.setattr(
        runner.prospective, "external_dependency_mutability", lambda *_args: True
    )


@pytest.mark.parametrize(
    "raw_topic",
    [
        b'{"slug":"safe-topic","slug":"different-topic"}',
        b'{"slug":"safe-topic","protocol_sha":"first","protocol_sha":"second"}',
        b'{"slug":"safe-topic","eligibility":{"include":true,"include":false}}',
        b'{"slug":"safe-topic","searches":[{"query":"trial","query":"seed"}]}',
        b'{"slug":"safe-topic","\\u0073lug":"different-topic"}',
    ],
    ids=[
        "duplicate-slug",
        "duplicate-protocol",
        "nested-eligibility",
        "array-nested-query",
        "escaped-duplicate-slug",
    ],
)
def test_duplicate_raw_members_refused_before_acquisition_and_bytes_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw_topic: bytes
) -> None:
    _synthetic_batch(monkeypatch)
    source = tmp_path / "externally-released.json"
    source.write_bytes(raw_topic)
    package = tmp_path / "single-run"
    calls: list[str] = []

    def forbidden_refresh(*_args: object, **_kwargs: object) -> str:
        calls.append("called")
        pytest.fail("ambiguous held-out JSON must not reach retrieval")

    monkeypatch.setattr(runner.acquisition, "refresh", forbidden_refresh)
    result = runner.run_topic("synthetic-batch", str(source), str(package))

    assert calls == []
    assert result["outcome"] == "FAILED_CRASH"
    assert (package / "topic-config.json").read_bytes() == raw_topic
    failure = json.loads((package / "failure.json").read_text(encoding="utf-8"))
    assert failure["type"] == "ProspectiveRefusal"
    assert "duplicate JSON member" in failure["message"]
    record = json.loads((package / "run_record.json").read_text(encoding="utf-8"))
    assert record["outcome"] == "FAILED_CRASH"
    assert "topic-config.json" in record["artefact_paths"]
    assert "failure.json" in record["artefact_paths"]


def test_unique_members_continue_to_acquisition_without_cached_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _synthetic_batch(monkeypatch)
    source = tmp_path / "topic.json"
    source.write_text(
        '{"slug":"safe-topic","eligibility":{"include":true},'
        '"searches":[{"query":"concept"}]}',
        encoding="utf-8",
    )
    package = tmp_path / "single-run"
    calls: list[str] = []

    def controlled_stop(*_args: object, **_kwargs: object) -> str:
        calls.append("attempt")
        raise RuntimeError("synthetic stop: no external API request")

    monkeypatch.setattr(runner.acquisition, "refresh", controlled_stop)
    result = runner.run_topic("synthetic-batch", str(source), str(package))

    assert calls == ["attempt"]
    assert result["outcome"] == "FAILED_CRASH"
    failure = json.loads((package / "failure.json").read_text(encoding="utf-8"))
    assert failure["type"] == "RuntimeError"
