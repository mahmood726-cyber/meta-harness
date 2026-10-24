"""CROSS-EXCH-016: raw CLI/API exchange parity (synthetic transport only).

These local tests are not the frozen two-repository benchmark. See frozen
workflow for actual pinned RapidMeta consumer, output digests and CI evidence.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest import mock

import pytest

from harness.exchange_v01 import import_exchange_json

ROOT = Path(__file__).resolve().parents[1]
CANARY_PATH = ROOT / "benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py"
spec = importlib.util.spec_from_file_location("candidate_canary_016", CANARY_PATH)
assert spec is not None and spec.loader is not None
canary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canary)


def candidate(name: str) -> bytes:
    accepted = canary.produce("ALLOW")
    if name == "allow":
        return canary.wire(accepted)
    if name in ("REFUSE", "MANUAL_REVIEW"):
        return canary.wire(canary.produce(name))
    if name == "duplicate_shadow":
        raw = canary.wire(accepted)
        old = b'"decision":"ALLOW"'
        assert old in raw
        return raw.replace(old, b'"decision":"REFUSE","decision":"ALLOW"', 1)
    if name == "duplicate_unicode_shadow":
        raw = canary.wire(accepted)
        old = b'"decision":"ALLOW"'
        assert old in raw
        return raw.replace(old, b'"decision":"REFUSE","decisio\\u006e":"ALLOW"', 1)
    if name == "trial_mismatch":
        accepted["rows"][0]["trial_id"] = "SYN-TRIAL-99"
    elif name == "source_sha_tamper":
        accepted["rows"][0]["source"]["sha256"] = "f" * 64
    elif name == "estimand_mismatch":
        accepted["proposed_pool"]["estimand"]["measure"] = "OR"
    elif name == "line_locator_mismatch":
        accepted["rows"][0]["source_span"]["locator"] = "line 1"
    elif name == "unknown_override":
        accepted["rows"][0]["manual_override"] = True
    elif name == "malformed_json":
        return b'{"schema_version":'
    elif name == "bad_utf8":
        return b'\\xff'
    else:
        raise AssertionError(name)
    return canary.wire(accepted)


@pytest.mark.parametrize("name", [
    "allow", "REFUSE", "MANUAL_REVIEW", "duplicate_shadow",
    "duplicate_unicode_shadow", "trial_mismatch", "source_sha_tamper",
    "estimand_mismatch", "line_locator_mismatch", "unknown_override",
    "malformed_json", "bad_utf8",
])
def test_api_and_cli_equivalent_on_raw_wire(tmp_path, name):
    raw = candidate(name)
    input_file = tmp_path / "wire.json"
    input_file.write_bytes(raw)
    cli = subprocess.run([
        sys.executable, "-m", "harness.exchange_v01", "--exchange", str(input_file),
        "--archive-root", str(ROOT),
    ], cwd=ROOT, capture_output=True, text=True, check=False, timeout=15)
    if name == "allow":
        payload = import_exchange_json(raw, ROOT)
        assert cli.returncode == 0
        assert "EXCHANGE VERIFIED" in cli.stdout
        assert [r["trial_id"] for r in payload["rows"]] == [
            "SYN-TRIAL-01", "SYN-TRIAL-02"]
        assert all(r["source_span"]["locator"].startswith("line ") for r in payload["rows"])
        assert payload["proposed_pool"]["estimand"]["measure"] == "RR"
        return
    with pytest.raises(ValueError) as api_error:
        import_exchange_json(raw, ROOT)
    assert cli.returncode != 0
    assert str(api_error.value) in cli.stderr
    # Strong no-pool guarantee: any engine subprocess would fail this test.
    with mock.patch.object(canary.subprocess, "run",
                           side_effect=AssertionError("invalid evidence reached engine")) as engine:
        outcome = canary.consume(raw, tmp_path, name)
        engine.assert_not_called()
    assert outcome["status"] == "REFUSED"
    assert outcome["engine_invoked"] is False


def test_manifest_cli_backward_compatible():
    manifest = ROOT / "benchmarks/cross_repo/v0.1/manifest.json"
    result = subprocess.run(
        [sys.executable, "-m", "harness.exchange_v01", str(manifest)],
        cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert "MANIFEST VERIFIED" in result.stdout


def test_raw_cli_rejects_missing_archive_root(tmp_path):
    f = tmp_path / "wire.json"
    f.write_bytes(candidate("allow"))
    result = subprocess.run(
        [sys.executable, "-m", "harness.exchange_v01", "--exchange", str(f)],
        cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
    )
    assert result.returncode != 0
    assert "--archive-root" in result.stderr
