"""Synthetic wire-boundary regressions; never public common-suite PASSes."""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.exchange_v01.wire import validate_exchange_json, validate_manifest_json  # noqa: E402

MANIFEST = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
SOURCE = ROOT / "benchmarks/cross_repo/v0.1/synthetic-source.txt"


def _exchange():
    estimand = {"measure": "RR", "population": "ITT",
                "outcome": "synthetic event", "timepoint": "12 months"}
    return {
        "schema_version": "0.1.0",
        "review_id": "SYNTHETIC-REVIEW",
        "protocol_sha256": "0" * 64,
        "proposed_pool": {"requested": True, "estimand": estimand},
        "rows": [{
            "study_id": "SYNTHETIC-STUDY-001",
            "trial_id": "SYNTHETIC-TRIAL-001",
            "decision": "ALLOW",
            "estimand": copy.deepcopy(estimand),
            "source": {"path": "benchmarks/cross_repo/v0.1/synthetic-source.txt",
                       "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
            "source_span": {"locator": "line 2",
                            "verbatim": "Trial SYNTHETIC-001 measured synthetic endpoint at 12 months."},
        }],
    }


def test_raw_manifest_and_real_cli_accept_only_structurally_valid_fixture():
    validate_manifest_json(MANIFEST.read_bytes(), MANIFEST.parent)
    proc = subprocess.run(
        [sys.executable, "-m", "harness.exchange_v01", str(MANIFEST)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "MANIFEST VERIFIED" in proc.stdout


@pytest.mark.parametrize("shadow,target", [
    ('"status": "FAIL", ', '"status": "NOT_RUN"'),
    ('"\\u0073tatus": "PASS", ', '"status": "NOT_RUN"'),
])
def test_shadowed_manifest_case_status_refused_by_api_and_cli(tmp_path, shadow, target):
    raw = MANIFEST.read_text(encoding="utf-8")
    assert target in raw
    poisoned = raw.replace(target, shadow + target, 1)
    assert json.loads(poisoned) == json.loads(raw)  # unsafe last-value-wins
    with pytest.raises(ValueError, match="duplicate JSON object member: status"):
        validate_manifest_json(poisoned, MANIFEST.parent)
    path = tmp_path / "manifest.json"
    path.write_text(poisoned, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "harness.exchange_v01", str(path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert proc.returncode != 0
    assert "duplicate JSON object member: status" in proc.stderr
    assert "MANIFEST VERIFIED" not in proc.stdout


@pytest.mark.parametrize("key,expected", [
    ("commit", "a62cbc43416a94561b7bee3ec48bb659ac3286e2"),
    ("input_sha256", "56d4cbd83b355b1c6275237aea526c5d993b9227241a7a0d3859ffac719639a4"),
])
def test_shadowed_manifest_identity_refuses(key, expected):
    raw = MANIFEST.read_text(encoding="utf-8")
    marker = f'"{key}": "{expected}"'
    assert marker in raw
    poisoned = raw.replace(marker, f'"{key}": "shadow", ' + marker, 1)
    with pytest.raises(ValueError, match=f"duplicate JSON object member: {key}"):
        validate_manifest_json(poisoned, MANIFEST.parent)


def test_valid_raw_exchange_parses_and_refusal_prevents_pooled_handoff():
    fixture = _exchange()
    validate_exchange_json(json.dumps(fixture).encode("utf-8"), ROOT)
    for decision in ("REFUSE", "MANUAL_REVIEW"):
        fixture["rows"][0]["decision"] = decision
        with pytest.raises(ValueError, match="cannot be pooled"):
            validate_exchange_json(json.dumps(fixture), ROOT)


@pytest.mark.parametrize("key,old,shadow", [
    ("decision", "ALLOW", "REFUSE"),
    ("trial_id", "SYNTHETIC-TRIAL-001", "OTHER-TRIAL"),
    ("measure", "RR", "OR"),
])
def test_shadowed_exchange_refusal_identity_or_estimand_refuses(key, old, shadow):
    original = json.dumps(_exchange())
    marker = f'"{key}": "{old}"'
    assert marker in original
    malicious = original.replace(marker, f'"{key}": "{shadow}", ' + marker, 1)
    assert json.loads(malicious) == json.loads(original)
    with pytest.raises(ValueError, match=f"duplicate JSON object member: {key}"):
        validate_exchange_json(malicious, ROOT)


@pytest.mark.parametrize("raw", [b"\xff", b"\xef\xbb\xbf{}", b'{"x": NaN}', b'{"cases": '])
def test_invalid_raw_manifest_never_validates(raw):
    with pytest.raises(ValueError):
        validate_manifest_json(raw, MANIFEST.parent)


def test_legacy_package_main_cannot_bypass_wire_duplicate_gate(tmp_path, monkeypatch, capsys):
    """The older importable main() must not retain json.loads last-key-wins."""
    from harness.exchange_v01 import main as legacy_main

    raw = MANIFEST.read_text(encoding="utf-8")
    poisoned = raw.replace('"status": "NOT_RUN"',
                           '"status": "FAIL", "status": "NOT_RUN"', 1)
    path = tmp_path / "manifest.json"
    path.write_text(poisoned, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["exchange_v01", str(path)])
    with pytest.raises(ValueError, match="duplicate JSON object member: status"):
        legacy_main()
    assert "MANIFEST VERIFIED" not in capsys.readouterr().out
