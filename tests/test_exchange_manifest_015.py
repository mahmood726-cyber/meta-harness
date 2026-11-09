"""CROSS-EXCH-015 raw manifest controls from the handoff stack."""
import json
import sys

import pytest

from test_exchange_v01 import ROOT
from harness.exchange_v01 import main, validate_manifest
from harness.exchange_v01.wire import validate_manifest_json


def _manifest_fixture():
    path = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    return json.loads(path.read_bytes()), path.parent


# CROSS-EXCH-015: preserve all raw JSON object members before benchmark
# status/provenance validation. Ordinary json.loads silently keeps the last
# duplicate and could erase an earlier FAIL, REFUSE, or unpinned commit.
def test_manifest_wire_positive_utf8_roundtrip_is_only_structural():
    manifest, root = _manifest_fixture()
    validate_manifest_json(json.dumps(manifest).encode("utf-8"), root)
    # This is not an executed cross-repository benchmark or an R oracle.


@pytest.mark.parametrize("key,shadow,accepted", [
    ("benchmark_version", "not-a-real-version", "0.1.0"),
    ("commit", "f" * 40, "a62cbc43416a94561b7bee3ec48bb659ac3286e2"),
    ("input_sha256", "f" * 64, "56d4cbd83b355b1c6275237aea526c5d993b9227241a7a0d3859ffac719639a4"),
    ("status", "FAIL", "NOT_RUN"),
    ("id", "CROSS-EXCH-999", "CROSS-EXCH-001"),
])
def test_manifest_wire_shadowed_member_refuses(key, shadow, accepted):
    manifest, root = _manifest_fixture()
    raw = json.dumps(manifest)
    marker = f'{json.dumps(key)}: {json.dumps(accepted)}'
    assert marker in raw
    poisoned = raw.replace(marker, f'{json.dumps(key)}: {json.dumps(shadow)}, ' + marker, 1)
    assert json.loads(poisoned) == manifest  # demonstrates unsafe last-value-wins parsing
    with pytest.raises(ValueError, match=f"duplicate JSON object member: {key}"):
        validate_manifest_json(poisoned, root)


def test_manifest_wire_unicode_escaped_duplicate_member_refuses():
    manifest, root = _manifest_fixture()
    raw = json.dumps(manifest)
    marker = '"status": "NOT_RUN"'
    assert marker in raw
    poisoned = raw.replace(marker, r'"\u0073tatus": "FAIL", ' + marker, 1)
    assert json.loads(poisoned) == manifest
    with pytest.raises(ValueError, match="duplicate JSON object member: status"):
        validate_manifest_json(poisoned, root)


@pytest.mark.parametrize("bad_bytes", [b"\xff", b"\xef\xbb\xbf{}"])
def test_manifest_wire_invalid_utf8_or_bom_refuses(bad_bytes):
    manifest, root = _manifest_fixture()
    with pytest.raises(ValueError, match="UTF-8"):
        validate_manifest_json(bad_bytes, root)


def test_manifest_wire_malformed_json_refuses():
    manifest, root = _manifest_fixture()
    with pytest.raises(ValueError, match="malformed benchmark manifest JSON"):
        validate_manifest_json('{"cases": ', root)


def test_manifest_cli_refuses_shadowed_status_before_reporting_verified(tmp_path, monkeypatch, capsys):
    manifest, _ = _manifest_fixture()
    raw = json.dumps(manifest)
    marker = '"status": "NOT_RUN"'
    assert marker in raw
    malicious = raw.replace(marker, '"status": "FAIL", ' + marker, 1)
    target = tmp_path / "manifest.json"
    target.write_text(malicious, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["exchange_v01", str(target)])
    with pytest.raises(ValueError, match="duplicate JSON object member: status"):
        main()
    assert "MANIFEST VERIFIED" not in capsys.readouterr().out


def test_fifteenth_case_not_run_with_original_immutable_source():
    manifest, root = _manifest_fixture()
    validate_manifest(manifest, root)
    case = next(c for c in manifest["cases"] if c["id"] == "CROSS-EXCH-015")
    assert case["status"] == "NOT_RUN"
    assert case["input_sha256"] == manifest["cases"][0]["input_sha256"]
