"""Prospective topic-input custody: archive the exact bytes parsed.

Synthetic failure-injection tests; not a live search, independent adjudication,
scientific validation or a claim about the 32 historical cached reviews.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from scripts import run_prospective_topic as runner


def _allow_synthetic_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        runner.prospective,
        "load_declaration",
        lambda *_args: {"time_limit_s": 60, "invariants": []},
    )
    monkeypatch.setattr(
        runner.prospective,
        "check_declaration_frozen",
        lambda *_args: None,
    )


def test_archive_matches_parsed_input_when_source_changes_after_first_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Old read-then-copy logic archived a different, later config."""
    _allow_synthetic_batch(monkeypatch)
    original = b'{"slug":"synthetic-original","topic_identifier":"original"}\n'
    replacement = b'{"slug":"synthetic-replacement","topic_identifier":"replacement"}\n'
    config_path = tmp_path / "topic-input.json"
    config_path.write_bytes(original)
    package = tmp_path / "unique-run-package"

    actual_open = io.open
    mutated = {"done": False}

    class MutateAfterRead:
        def __init__(self, file_handle: object) -> None:
            self.file_handle = file_handle

        def __enter__(self) -> "MutateAfterRead":
            self.file_handle.__enter__()
            return self

        def __exit__(self, *args: object) -> object:
            result = self.file_handle.__exit__(*args)
            config_path.write_bytes(replacement)
            return result

        def read(self, *args: object, **kwargs: object) -> object:
            return self.file_handle.read(*args, **kwargs)

    def open_with_source_change(path: object, mode: str = "r", *args: object, **kwargs: object) -> object:
        fh = actual_open(path, mode, *args, **kwargs)
        if str(path) == str(config_path) and "r" in mode and not mutated["done"]:
            mutated["done"] = True
            return MutateAfterRead(fh)
        return fh

    monkeypatch.setattr(io, "open", open_with_source_change)

    def stop_before_real_retrieval(*_args: object, **_kwargs: object) -> str:
        raise RuntimeError("synthetic controlled stop; no API search performed")

    monkeypatch.setattr(runner.acquisition, "refresh", stop_before_real_retrieval)
    result = runner.run_topic("synthetic-batch", str(config_path), str(package))

    assert mutated["done"]
    assert result["outcome"] == "FAILED_CRASH"
    assert config_path.read_bytes() == replacement
    assert (package / "topic-config.json").read_bytes() == original
    run_record = json.loads((package / "run_record.json").read_text(encoding="utf-8"))
    assert run_record["topic_identifier"] == "original"
    assert "topic-config.json" in run_record["artefact_paths"]
    assert "failure.json" in run_record["artefact_paths"]


@pytest.mark.parametrize(
    "input_bytes",
    [
        b'{"slug":"synthetic-unclosed"',
        b"\xff",
        b'["not-a-dict"]',
        b'{"topic_identifier":"synthetic-missing-slug"}',
    ],
    ids=["malformed-json", "invalid-utf8", "non-object", "missing-slug"],
)
def test_invalid_topic_input_is_preserved_with_failed_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, input_bytes: bytes
) -> None:
    """Even rejected inputs remain available as bytes for subsequent audit."""
    _allow_synthetic_batch(monkeypatch)
    config = tmp_path / "invalid-topic-config.json"
    config.write_bytes(input_bytes)
    package = tmp_path / "one-run"
    monkeypatch.setattr(
        runner.acquisition,
        "refresh",
        lambda *_args, **_kwargs: pytest.fail("invalid input must not start retrieval"),
    )

    result = runner.run_topic("synthetic-batch", str(config), str(package))
    assert result["outcome"] == "FAILED_CRASH"
    assert (package / "topic-config.json").read_bytes() == input_bytes
    record = json.loads((package / "run_record.json").read_text(encoding="utf-8"))
    assert "topic-config.json" in record["artefact_paths"]
    assert "failure.json" in record["artefact_paths"]
