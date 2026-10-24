"""Prospective topic identity must not escape the one-run output boundary.

Synthetic failure-injection tests only: no API calls, actual study discovery,
independent adjudication, external oracle or clinical validation.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import run_prospective_topic as runner


def _synthetic_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid production freeze scans; exercise the actual prospective runner."""
    monkeypatch.setattr(
        runner.prospective,
        "load_declaration",
        lambda *_args: {"time_limit_s": 60, "invariants": []},
    )
    monkeypatch.setattr(runner.prospective, "check_declaration_frozen", lambda *_: None)
    monkeypatch.setattr(runner.prospective.architecture_identity, "identity", lambda *_: "f" * 64)
    monkeypatch.setattr(runner.prospective, "external_dependency_mutability", lambda *_: True)


@pytest.mark.parametrize(
    "slug",
    [
        "../outside",
        "../../outside",
        "/absolute",
        "nested/topic",
        r"..\\outside",
        r"C:\\outside",
        ".",
        "..",
        ".hidden",
        "a..b",
        "topic.",
        "with space",
        "",
        None,
        [],
        True,
        7,
        "CON",
        "com1.txt",
        "LPT9",
    ],
    ids=[
        "parent-traversal",
        "double-parent-traversal",
        "absolute",
        "nested-slash",
        "windows-parent-traversal",
        "windows-drive",
        "single-dot",
        "parent-dot",
        "hidden-directory",
        "internal-parent-sequence",
        "trailing-dot",
        "whitespace",
        "empty",
        "null",
        "list",
        "bool",
        "number",
        "device-con",
        "device-com1",
        "device-lpt9",
    ],
)
def test_unsafe_topic_slug_is_archived_refused_before_any_acquisition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, slug: object
) -> None:
    """Before this guard, refresh could write outside root/cache/<slug>."""
    _synthetic_batch(monkeypatch)
    source = tmp_path / "externally-provided.json"
    source_bytes = (
        json.dumps({"slug": slug, "topic_identifier": "synthetic-heldout"}, sort_keys=True)
        + "\n"
    ).encode("utf-8")
    source.write_bytes(source_bytes)
    package = tmp_path / "reserved-package"
    calls: list[str] = []

    def forbidden_refresh(*_args: object, **_kwargs: object) -> str:
        calls.append("called")
        raise AssertionError("unsafe slug reached acquisition")

    monkeypatch.setattr(runner.acquisition, "refresh", forbidden_refresh)
    result = runner.run_topic("synthetic-batch", str(source), str(package))

    assert calls == [], "no network or snapshot writes are permitted for unsafe identities"
    assert result["outcome"] == "FAILED_CRASH"
    assert (package / "topic-config.json").read_bytes() == source_bytes
    detail = json.loads((package / "failure.json").read_text(encoding="utf-8"))
    assert detail["type"] == "ProspectiveRefusal"
    assert "single safe ASCII path component" in detail["message"]
    record = json.loads((package / "run_record.json").read_text(encoding="utf-8"))
    assert record["outcome"] == "FAILED_CRASH"
    assert "topic-config.json" in record["artefact_paths"]
    assert "failure.json" in record["artefact_paths"]
    assert not (tmp_path / "outside").exists()


@pytest.mark.parametrize("slug", ["a", "safe-topic-v1", "safe.topic_2"])
def test_safe_topic_slug_reaches_refresh_without_canned_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, slug: str
) -> None:
    """Positive routing control; synthetic retrieval stop, not real discovery."""
    _synthetic_batch(monkeypatch)
    source = tmp_path / "safe.json"
    source.write_text(json.dumps({"slug": slug}), encoding="utf-8")
    observed: list[tuple[str, str]] = []

    def controlled_stop(config: dict, _day: str, *, root: str) -> str:
        observed.append((config["slug"], root))
        raise RuntimeError("synthetic no-network acquisition stop")

    monkeypatch.setattr(runner.acquisition, "refresh", controlled_stop)
    package = tmp_path / "single-run-package"
    result = runner.run_topic("synthetic-batch", str(source), str(package))

    assert observed == [(slug, str(package))]
    assert result["outcome"] == "FAILED_CRASH"
    detail = json.loads((package / "failure.json").read_text(encoding="utf-8"))
    assert detail["type"] == "RuntimeError"


def test_loader_also_refuses_traversal_when_invoked_directly(tmp_path: Path) -> None:
    with pytest.raises(runner.prospective.ProspectiveRefusal, match="single safe ASCII"):
        runner._load_or_refresh({"slug": "../outside"}, tmp_path, "2026-10-24")
