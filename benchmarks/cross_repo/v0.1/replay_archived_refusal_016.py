"""Re-run archived CROSS-EXCH-016 MANUAL_REVIEW through the frozen importer.

This is a scoped synthetic two-repository transport gate, not clinical accuracy,
an independent R oracle, or the complete four-repository/Sentinel canary.
The consumer's statistical subprocess MUST NOT run on refusal.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

from compare_cross_os_016 import compare, digest, load_json, assert_equal

REPLAY_CASE = "manual_review"
ENGINE_PATH = "template/assets/vendor/pairwise-pool.js"

# Separate Python interpreter imports the exact-pinned producer, rather than
# candidate-head importer functions; the refusal is checked with a tripwire.
FROZEN_RUNNER = r'''
import importlib.util
import json
from pathlib import Path
import sys
from unittest import mock
meta = Path(sys.argv[1]).resolve(strict=True)
rapid = Path(sys.argv[2]).resolve(strict=True)
source = meta / 'benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py'
sys.path.insert(0, str(meta))
spec = importlib.util.spec_from_file_location('pinned_refusal_replay', source)
if spec is None or spec.loader is None:
    raise RuntimeError('frozen canary module not importable')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
raw = sys.stdin.buffer.read()
with mock.patch.object(module.subprocess, 'run', side_effect=AssertionError('NO_POOL: subprocess invoked')) as tripwire:
    result = module.consume(raw, rapid, 'manual_review')
    tripwire.assert_not_called()
if result.get('status') != 'REFUSED' or result.get('engine_invoked') is not False:
    raise RuntimeError('frozen importer did not refuse MANUAL_REVIEW without pooling')
if not isinstance(result.get('refusal'), str) or not result['refusal'].strip():
    raise RuntimeError('frozen refusal has no diagnostic')
print(json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False))
'''


def git_head(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True, timeout=15
    ).strip()


def exact_checkout_checks(spec: dict, meta: Path, rapid: Path,
                          ubuntu: Path, windows: Path) -> dict:
    meta_sha, rapid_sha = git_head(meta), git_head(rapid)
    assert_equal(meta_sha, spec["repositories"]["meta-harness"]["commit"],
                 "frozen producer commit")
    assert_equal(rapid_sha, spec["repositories"]["rapidmeta-kit"]["commit"],
                 "frozen consumer commit")
    engine_sha = digest((rapid / ENGINE_PATH).read_bytes())
    for archive in (ubuntu, windows):
        index = load_json(archive / "index.json")
        assert_equal(index["rapidmeta_engine_sha256"], engine_sha,
                     "archived engine SHA against frozen source checkout")
    source = (meta / spec["frozen_source"]["path"]).read_bytes()
    assert_equal(digest(source), spec["frozen_source"]["sha256"],
                 "frozen source SHA256")
    assert_equal(platform.python_version(), spec["runtime"]["python"],
                 "replay Python runtime")
    node = subprocess.check_output(
        ["node", "--version"], text=True, timeout=15
    ).strip()
    assert_equal(node, "v" + spec["runtime"]["node"], "replay Node runtime")
    return {"producer_commit": meta_sha, "consumer_commit": rapid_sha,
            "engine_sha256": engine_sha,
            "frozen_source_sha256": digest(source)}


def _unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate replay result member: {key}")
        obj[key] = value
    return obj


def _reject_nonfinite(value):
    raise ValueError(f"nonfinite replay result: {value}")


def replay_frozen_bytes(meta: Path, rapid: Path, raw: bytes) -> tuple[dict, str]:
    """Invoke actual frozen canary in a new Python process; no Node execution."""
    process = subprocess.run(
        [sys.executable, "-I", "-c", FROZEN_RUNNER, str(meta), str(rapid)],
        input=raw, capture_output=True, timeout=25, check=False
    )
    if process.returncode:
        raise RuntimeError(
            f"frozen no-pool replay failed (exit={process.returncode}): "
            + process.stderr.decode("utf-8", errors="replace")[:900]
        )
    decoded = json.loads(
        process.stdout, object_pairs_hook=_unique, parse_constant=_reject_nonfinite
    )
    if not isinstance(decoded, dict):
        raise ValueError("frozen replay output not a JSON object")
    return decoded, digest(process.stdout)


def verify_replay_observation(observed: dict, archived: dict, raw: bytes):
    """Recomputed archive hashes must not substitute for observed refusal."""
    for name, value in (
        ("case", REPLAY_CASE), ("input_sha256", digest(raw)),
        ("status", "REFUSED"), ("engine_invoked", False)
    ):
        assert_equal(observed.get(name), value, f"frozen replay {name}")
        assert_equal(archived.get(name), value, f"archived consumer {name}")
    reason = observed.get("refusal")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("frozen replay missing refusal provenance")
    assert_equal(archived.get("refusal"), reason,
                 "archived/frozen refusal provenance")
    if "engine_output" in archived or "engine_output" in observed:
        raise ValueError("refused replay contains pool output")


def run(registration: Path, ubuntu: Path, windows: Path,
        meta: Path, rapid: Path) -> dict:
    # Existing comparator verifies all 12 cases and 50 SHA receipts first.
    prior = compare(registration, ubuntu, windows)
    spec = load_json(registration)
    pins = exact_checkout_checks(spec, meta, rapid, ubuntu, windows)
    replays = {}
    for os_label, archive in (
        ("ubuntu-24.04", ubuntu), ("windows-2025", windows)
    ):
        raw = (archive / "inputs" / f"{REPLAY_CASE}.json").read_bytes()
        result_path = archive / "results" / f"{REPLAY_CASE}.json"
        archived = load_json(result_path)["consumer"]
        observed, stdout_sha = replay_frozen_bytes(meta, rapid, raw)
        verify_replay_observation(observed, archived, raw)
        replays[os_label] = {
            "input_sha256": digest(raw),
            "archived_result_sha256": digest(result_path.read_bytes()),
            "replay_stdout_sha256": stdout_sha,
            "status": observed["status"], "engine_invoked": False,
            "refusal": observed["refusal"]
        }
    assert_equal(replays["ubuntu-24.04"]["input_sha256"],
                 replays["windows-2025"]["input_sha256"],
                 "cross-OS replayed raw input")
    assert_equal(replays["ubuntu-24.04"]["refusal"],
                 replays["windows-2025"]["refusal"],
                 "cross-OS replayed refusal provenance")
    return {
        "record_version": "1.0.0", "case_id": "CROSS-EXCH-016",
        "subcase": "frozen_archived_manual_review_no_pool_replay",
        "result": "PASS", "evidence_scope": "SYNTHETIC_TWO_REPO_NO_POOL_ONLY",
        "registration_sha256": digest(registration.read_bytes()),
        "pins": pins, "original_archive_parity": prior["overall"],
        "replays": replays, "clinical_accuracy": "NOT_TESTED",
        "external_R_oracle": "NOT_TESTED", "four_repo_suite": "NOT_RUN",
        "independent_human_adjudication": "NOT_TESTED"
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registration", type=Path, required=True)
    ap.add_argument("--ubuntu", type=Path, required=True)
    ap.add_argument("--windows", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--rapidmeta", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()
    report = run(a.registration, a.ubuntu, a.windows, a.meta, a.rapidmeta)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("CROSS-EXCH-016 ARCHIVED MANUAL_REVIEW REPLAY: two actual archived "
          "inputs refused through frozen code, zero engine subprocess calls; "
          "synthetic transport scope only")


if __name__ == "__main__":
    main()
