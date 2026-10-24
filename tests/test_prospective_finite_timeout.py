"""Fail-closed preregistered time-limit tests (synthetic declarations only).

These checks do not establish live search, a frozen external model, blinded
adjudication, an independently reproduced clinical result, or an R oracle.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness import prospective


INVALID_LIMITS = [
    pytest.param(float("nan"), id="nan-number"),
    pytest.param(float("inf"), id="positive-infinity"),
    pytest.param(float("-inf"), id="negative-infinity"),
    pytest.param("NaN", id="nan-string"),
    pytest.param("Infinity", id="infinity-string"),
    pytest.param("-Infinity", id="negative-infinity-string"),
    pytest.param(True, id="true-not-seconds"),
    pytest.param(False, id="false-not-seconds"),
    pytest.param(0, id="zero"),
    pytest.param(-1, id="negative"),
    pytest.param(None, id="missing"),
    pytest.param("not-a-number", id="nonnumeric"),
]


def _stub_architecture(monkeypatch: pytest.MonkeyPatch) -> None:
    # Only the declared-limit boundary is under test; bypass expensive
    # architecture inventory construction, not any production CI gate.
    components = {"model_stages": {"stages": []}}
    monkeypatch.setattr(
        prospective.architecture_identity, "components", lambda _root: components
    )
    monkeypatch.setattr(
        prospective.architecture_identity,
        "identity_from_components",
        lambda _components: "a" * 64,
    )
    monkeypatch.setattr(
        prospective.architecture_identity, "mutable_dependencies", lambda _root: []
    )
    monkeypatch.setattr(
        prospective, "rerun_policy_text", lambda _root: "synthetic A4 policy"
    )


def _declaration(root: Path) -> dict:
    return prospective.batch_declaration(
        root, "synthetic-batch", 60, ["census"], "a" * 64,
        {"definition": "synthetic universe"},
        declared_utc="2026-10-24T12:00:00Z",
    )


@pytest.mark.parametrize("bad_limit", INVALID_LIMITS)
def test_creation_refuses_nonfinite_or_invalid_time_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_limit: object
) -> None:
    _stub_architecture(monkeypatch)
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.batch_declaration(
            tmp_path, "synthetic-batch", bad_limit, ["census"], "a" * 64,
            {"definition": "synthetic universe"},
        )


@pytest.mark.parametrize("bad_limit", INVALID_LIMITS)
def test_frozen_declaration_refuses_mutated_time_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_limit: object
) -> None:
    _stub_architecture(monkeypatch)
    declaration = _declaration(tmp_path)
    assert prospective.check_declaration_frozen(tmp_path, declaration) == declaration
    declaration["time_limit_s"] = bad_limit
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.check_declaration_frozen(tmp_path, declaration)


@pytest.mark.parametrize("bad_limit", [float("nan"), float("inf"), float("-inf")])
def test_nonstandard_json_number_roundtrip_still_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_limit: float
) -> None:
    _stub_architecture(monkeypatch)
    declaration = _declaration(tmp_path)
    declaration["time_limit_s"] = bad_limit
    path = prospective.write_declaration(tmp_path, declaration)
    # Python's default JSON codec accepts these extensions: the run-time
    # frozen-declaration validation must explicitly fail closed.
    assert any(token in path.read_text(encoding="utf-8") for token in ("NaN", "Infinity"))
    loaded = prospective.load_declaration(tmp_path, "synthetic-batch")
    with pytest.raises(prospective.ProspectiveRefusal, match="time_limit_s"):
        prospective.check_declaration_frozen(tmp_path, loaded)


@pytest.mark.parametrize(
    "limit,expected",
    [(1, 1), (0.5, 0.5), ("60", 60.0)],
)
def test_positive_finite_limit_remains_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, limit: object, expected: float
) -> None:
    _stub_architecture(monkeypatch)
    declaration = prospective.batch_declaration(
        tmp_path, "synthetic-batch", limit, ["census"], "a" * 64,
        {"definition": "synthetic universe"},
    )
    assert declaration["time_limit_s"] == expected
    assert prospective.check_declaration_frozen(tmp_path, declaration) == declaration
