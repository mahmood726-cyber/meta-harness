"""Independent archived-artifact comparison for the frozen CROSS-EXCH-016 canary.

Compare *actual outputs from both CI matrix jobs*, not newly manufactured results.
Transport/refusal parity only: does not establish numerical or clinical accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

OS_NAMES = {"ubuntu-24.04": "Linux", "windows-2025": "Windows"}
CASE_ID = "CROSS-EXCH-016"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _unique(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate archived JSON member: {key}")
        output[key] = value
    return output


def _no_nonfinite(value):
    raise ValueError(f"nonfinite archived JSON constant: {value}")


def load_json(path: Path):
    # Explicit raw decoding prevents silent duplicate-key collapse and UTF-8 BOM.
    return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=_unique,
                      parse_constant=_no_nonfinite)


def assert_equal(left, right, explanation):
    if left != right:
        raise ValueError(f"{explanation}: {left!r} != {right!r}")


def check_archive(registration: dict, registration_sha: str, root: Path, os_name: str):
    """Rehash and inspect one real CI job archive without invoking a producer."""
    index = load_json(root / "index.json")
    assert_equal(index.get("case_id"), CASE_ID, "case ID")
    assert_equal(index.get("evidence_scope"),
                 "SYNTHETIC_FROZEN_TWO_REPOSITORY_CLI_API_HANDOFF_ONLY", "scope")
    assert_equal(index.get("registration_sha256"), registration_sha, "registration digest")
    assert_equal(index.get("observed_runner", {}).get("runner_image_label"), os_name, "runner")
    assert_equal(index.get("observed_runner", {}).get("observed_system"), OS_NAMES[os_name], "OS")
    for key, repo in (("meta_harness_commit", "meta-harness"),
                      ("rapidmeta_commit", "rapidmeta-kit")):
        assert_equal(index.get(key), registration["repositories"][repo]["commit"], key)
    assert_equal(index.get("source_sha256"), registration["frozen_source"]["sha256"], "source digest")
    assert_equal(index.get("python_runtime"), registration["runtime"]["python"], "Python version")
    assert_equal(index.get("node_runtime"), "v" + registration["runtime"]["node"], "Node version")
    assert_equal(index.get("external_R_oracle"), "NOT_TESTED", "R oracle scope")
    assert_equal(index.get("four_repo_suite"), "NOT_RUN", "ecosystem scope")
    assert_equal(index.get("human_adjudication"), "NOT_TESTED", "human adjudication scope")
    engine_sha = index.get("rapidmeta_engine_sha256")
    if not isinstance(engine_sha, str) or len(engine_sha) != 64 or any(ch not in "0123456789abcdef" for ch in engine_sha):
        raise ValueError("engine SHA256 is absent or malformed")

    scenarios = registration["scenarios"]
    expected_files = {"source.txt"} | {
        f"{folder}/{label}.json" for folder in ("inputs", "results") for label in scenarios
    }
    if not isinstance(index.get("digests"), dict) or set(index["digests"]) != expected_files:
        raise ValueError("incomplete or unexpected archive receipts")
    for name in sorted(expected_files):
        checksum = index["digests"][name]
        if not isinstance(checksum, str) or len(checksum) != 64 or digest((root / name).read_bytes()) != checksum:
            raise ValueError(f"archived SHA256 integrity failure: {os_name}/{name}")
    assert_equal(index["digests"]["source.txt"], index["source_sha256"], "archived source receipt")

    decisions = {}
    for label, expected in scenarios.items():
        raw = (root / "inputs" / f"{label}.json").read_bytes()
        result = load_json(root / "results" / f"{label}.json")
        input_sha = digest(raw)
        assert_equal(result.get("name"), label, "output case label")
        assert_equal(result.get("raw_sha256"), input_sha, "result/input digest")
        assert_equal(result.get("cli_status"), expected["importer"], "CLI decision")
        assert_equal(result.get("api_status"), expected["importer"], "API decision")
        consumer = result.get("consumer")
        if not isinstance(consumer, dict):
            raise ValueError(f"absent consumer result: {label}")
        assert_equal(consumer.get("input_sha256"), input_sha, "downstream input digest")
        assert_equal(consumer.get("status"), expected["consumer"], "consumer decision")
        allowed = label == "allow_rr_itt"
        assert_equal(consumer.get("engine_invoked"), allowed, "engine invocation")
        if allowed:
            summary = consumer.get("engine_output")
            if not isinstance(summary, dict):
                raise ValueError("missing real-engine smoke summary")
            assert_equal(summary.get("k_used"), 2, "pool study count")
            assert_equal(summary.get("measure"), "RR", "pooled measure")
            if any(not isinstance(summary.get(k), (float, int)) or
                   isinstance(summary.get(k), bool) or not math.isfinite(summary[k])
                   for k in ("mu_log", "tau2")):
                raise ValueError("non-finite pooled smoke output")
        elif consumer.get("status") != "REFUSED" or "engine_output" in consumer:
            raise ValueError(f"refused case pooled or published engine output: {label}")
        decisions[label] = {
            "raw_sha256": input_sha,
            "cli": result["cli_status"],
            "api": result["api_status"],
            "consumer": consumer["status"],
            "engine_invoked": consumer["engine_invoked"],
        }
    return {"runner": os_name, "index_sha256": digest((root / "index.json").read_bytes()),
            "source_sha256": index["source_sha256"],
            "rapidmeta_engine_sha256": engine_sha,
            "digest_receipts_verified": len(expected_files), "decisions": decisions}


def compare(registration_path: Path, ubuntu_dir: Path, windows_dir: Path) -> dict:
    registration_raw = registration_path.read_bytes()
    registration = load_json(registration_path)
    assert_equal(registration.get("case_id"), CASE_ID, "registration case")
    assert_equal(registration.get("registered_status"), "NOT_RUN", "preregistered status")
    assert_equal(registration.get("input_type"), "SYNTHETIC_FIXTURE_ONLY", "input type")
    assert_equal(registration.get("runtime", {}).get("os"), list(OS_NAMES), "frozen OS matrix")
    a = check_archive(registration, digest(registration_raw), ubuntu_dir, "ubuntu-24.04")
    b = check_archive(registration, digest(registration_raw), windows_dir, "windows-2025")
    for field in ("source_sha256", "rapidmeta_engine_sha256", "decisions"):
        assert_equal(a[field], b[field], f"cross-OS {field}")
    return {"record_version": "1.0.0", "case_id": CASE_ID,
            "evidence_scope": "FROZEN_SYNTHETIC_TWO_REPO_CROSS_OS_TRANSPORT_REFUSAL_PARITY_ONLY",
            "registration_sha256": digest(registration_raw), "overall": "PASS",
            "case_count": len(a["decisions"]),
            "refused_without_pooling": sum(not item["engine_invoked"] for item in a["decisions"].values()),
            "input_and_decision_parity": True,
            "numerical_output_cross_os_comparison": "NOT_TESTED",
            "real_R_oracle": "NOT_TESTED", "four_repository_suite": "NOT_RUN",
            "clinical_accuracy": "NOT_TESTED", "independent_human_adjudication": "NOT_TESTED",
            "archives": {a["runner"]: {k: a[k] for k in ("index_sha256", "digest_receipts_verified")},
                         b["runner"]: {k: b[k] for k in ("index_sha256", "digest_receipts_verified")}}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registration", required=True, type=Path)
    ap.add_argument("--ubuntu", required=True, type=Path)
    ap.add_argument("--windows", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    report = compare(args.registration, args.ubuntu, args.windows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"CROSS-EXCH-016 cross-OS archived parity PASS: {report['case_count']} registered cases, "
          f"{report['refused_without_pooling']} no-pool refusals, "
          f"{sum(a['digest_receipts_verified'] for a in report['archives'].values())} digest checks")


if __name__ == "__main__":
    main()
