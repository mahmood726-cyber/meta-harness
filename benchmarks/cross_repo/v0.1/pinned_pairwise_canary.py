"""Scoped, synthetic-only Meta-Harness -> pinned RapidMeta executable handoff.

Not a clinical dataset, independent review, statistical oracle, or permission
for production pooling. This deliberately uses a single canary-only, text-
anchored binary-arm notation; other inputs are refused. Never feed the
production statistical engine a refused or unverified transport record.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from harness.exchange_v01 import validate_exchange_json  # noqa: E402

SOURCE = "benchmarks/cross_repo/v0.1/synthetic-binary-arms.txt"
SOURCE_SHA256 = "666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398"
ENGINE = "template/assets/vendor/pairwise-pool.js"
COUNTS = re.compile(r"(SYN-TRIAL-[0-9]{2}) tE=([0-9]+) tN=([0-9]+) cE=([0-9]+) cN=([0-9]+)\Z")
ESTIMAND = {"measure": "RR", "population": "ITT", "outcome": "synthetic event", "timepoint": "12 months"}
NODE = r"""
const fs = require('node:fs');
const engine = process.argv[1];
require(engine);
if (!globalThis.PairwisePool || typeof globalThis.PairwisePool.pool2x2 !== 'function') {
  throw new Error('Pinned RapidMeta engine missing pool2x2');
}
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = globalThis.PairwisePool.pool2x2(input.rows, {measure: input.measure});
if (result.error || result.k_used !== input.rows.length ||
    !Number.isFinite(result.mu_log) || !Number.isFinite(result.tau2)) {
  throw new Error('RapidMeta synthetic canary did not pool all validated rows');
}
process.stdout.write(JSON.stringify({k_used: result.k_used, measure: result.measure,
  mu_log: result.mu_log, tau2: result.tau2}));
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wire(payload: dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def git_head(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def preflight(rapidmeta: Path) -> tuple[str, str]:
    manifest = json.loads((ROOT / "benchmarks/cross_repo/v0.1/manifest.json").read_bytes())
    expected = manifest["repositories"]["rapidmeta-kit"]["commit"]
    actual = git_head(rapidmeta)
    if actual != expected:
        raise RuntimeError(f"RapidMeta checkout not at manifest-pinned SHA: expected {expected}, got {actual}")
    data = (ROOT / SOURCE).read_bytes()
    if sha(data) != SOURCE_SHA256:
        raise RuntimeError("Synthetic count-source digest drift; refuse to run")
    engine = rapidmeta / ENGINE
    if not engine.is_file():
        raise RuntimeError("Pinned RapidMeta production pairwise engine unavailable")
    return actual, sha(engine.read_bytes())


def produce(decision: str) -> dict:
    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    rows = []
    for number, line in enumerate(source_lines[1:], start=2):
        match = COUNTS.fullmatch(line)
        if match is None:
            raise ValueError("Synthetic source is not in the declared canary grammar")
        trial = match.group(1)
        rows.append({
            "study_id": f"SYN-STUDY-{number - 1:02d}", "trial_id": trial,
            "decision": decision, "estimand": copy.deepcopy(ESTIMAND),
            "source": {"path": SOURCE, "sha256": SOURCE_SHA256},
            "source_span": {"locator": f"line {number}", "verbatim": line},
        })
    if len(rows) != 2:
        raise ValueError("Canary expects exactly two synthetic source rows")
    return {"schema_version": "0.1.0", "review_id": "SYNTHETIC-PINNED-HANDOFF",
            "protocol_sha256": "0" * 64, "rows": rows,
            "proposed_pool": {"requested": True, "estimand": copy.deepcopy(ESTIMAND)}}


def counts_from_verified(payload: dict) -> list[dict]:
    """Not a general extractor: refuse all but the two hashed canary lines."""
    if payload["proposed_pool"]["estimand"] != ESTIMAND or len(payload["rows"]) != 2:
        raise ValueError("Canary estimand or row count is not the frozen synthetic specification")
    rows = []
    for expected_n, row in enumerate(payload["rows"], start=1):
        if row["source"]["path"] != SOURCE or row["source"]["sha256"] != SOURCE_SHA256:
            raise ValueError("Canary source identity mismatch")
        if row["source_span"]["locator"] != f"line {expected_n + 1}":
            raise ValueError("Canary source line order mismatch")
        match = COUNTS.fullmatch(row["source_span"]["verbatim"])
        if not match or match.group(1) != row["trial_id"]:
            raise ValueError("Declared trial_id does not match verbatim source")
        a, n1, c, n0 = map(int, match.groups()[1:])
        if not (0 < a < n1 and 0 < c < n0):
            raise ValueError("Canary source binary arms invalid")
        rows.append({"name": row["trial_id"], "tE": a, "tN": n1, "cE": c, "cN": n0})
    return rows


def consume(raw: bytes, rapidmeta: Path, label: str) -> dict:
    """Raw JSON is checked *before* starting Node or calling any pool engine."""
    result = {"case": label, "input_sha256": sha(raw), "engine_invoked": False}
    try:
        validate_exchange_json(raw, ROOT)
        # Only decode after duplicate-member checks have accepted the raw bytes.
        payload = json.loads(raw)
        rows = counts_from_verified(payload)
    except (ValueError, KeyError, TypeError) as exc:
        result.update(status="REFUSED", refusal=str(exc))
        return result
    process = subprocess.run(
        ["node", "-e", NODE, str((rapidmeta / ENGINE).resolve(strict=True))],
        input=json.dumps({"measure": "RR", "rows": rows}), text=True,
        capture_output=True, check=False, timeout=30,
    )
    result["engine_invoked"] = True
    if process.returncode != 0:
        raise RuntimeError(f"Pinned RapidMeta engine failed, exit={process.returncode}: {process.stderr[:600]}")
    summary = json.loads(process.stdout)
    if summary["k_used"] != 2 or summary["measure"] != "RR" or not all(
        math.isfinite(summary[k]) for k in ("mu_log", "tau2")
    ):
        raise RuntimeError("Real RapidMeta engine did not return the expected bounded smoke fields")
    result.update(status="SYNTHETIC_ENGINE_EXECUTED", engine_output=summary)
    return result


def run(rapidmeta: Path, output: Path) -> None:
    rapidmeta = rapidmeta.resolve(strict=True)
    rapidmeta_head, engine_sha = preflight(rapidmeta)
    output.mkdir(parents=True, exist_ok=False)
    inp, res = output / "inputs", output / "results"
    inp.mkdir()
    res.mkdir()

    baseline = produce("ALLOW")
    cases: dict[str, bytes] = {
        "allow_synthetic_control": wire(baseline),
        "refuse": wire(produce("REFUSE")),
        "manual_review": wire(produce("MANUAL_REVIEW")),
    }
    # Last-value-wins consumers would see ALLOW; this wire MUST fail closed.
    good = cases["allow_synthetic_control"]
    token = b'"decision":"ALLOW"'
    if token not in good:
        raise RuntimeError("Unable to construct strict duplicate-key negative case")
    cases["shadowed_refuse"] = good.replace(token, b'"decision":"REFUSE","decision":"ALLOW"', 1)
    wrong_source = copy.deepcopy(baseline)
    wrong_source["rows"][0]["source"]["sha256"] = "f" * 64
    cases["source_hash_drift"] = wire(wrong_source)
    wrong_trial = copy.deepcopy(baseline)
    wrong_trial["rows"][0]["trial_id"] = "SYN-TRIAL-99"
    cases["source_trial_mismatch"] = wire(wrong_trial)

    digests = {}
    for label, raw in cases.items():
        raw_path = inp / f"{label}.json"
        raw_path.write_bytes(raw)
        result = consume(raw_path.read_bytes(), rapidmeta, label)
        expected_success = label == "allow_synthetic_control"
        if expected_success != (result["status"] == "SYNTHETIC_ENGINE_EXECUTED"):
            raise RuntimeError(f"Unexpected handoff status for {label}: {result}")
        if not expected_success and (result["status"] != "REFUSED" or result["engine_invoked"]):
            raise RuntimeError(f"Refused input reached the RapidMeta engine: {label}")
        out_path = res / f"{label}.json"
        out_path.write_bytes(wire(result))
        digests[str(raw_path.relative_to(output))] = sha(raw_path.read_bytes())
        digests[str(out_path.relative_to(output))] = sha(out_path.read_bytes())
        print(f"{label}: {result['status']}, engine_invoked={result['engine_invoked']}")
    record = {
        "type": "synthetic_structural_cross_repo_canary_only",
        "runner_checkout_sha": git_head(ROOT),
        "manifest_meta_harness_source_sha_not_executed_as_runner": json.loads(
            (ROOT / "benchmarks/cross_repo/v0.1/manifest.json").read_bytes()
        )["repositories"]["meta-harness"]["commit"],
        "rapidmeta_pinned_sha": rapidmeta_head,
        "python_runtime": platform.python_version(),
        "node_runtime": subprocess.check_output(["node", "--version"], text=True).strip(),
        "rapidmeta_engine_sha256": engine_sha,
        "source_sha256": SOURCE_SHA256,
        "digests": digests,
        "clinical_validation": "NOT_TESTED",
        "external_R_oracle": "NOT_TESTED",
        "four_repository_benchmark": "NOT_RUN",
    }
    (output / "index.json").write_bytes(wire(record))
    print("CANARY COMPLETED: one synthetic engine smoke and five real no-pool refusals; no external R or clinical claim")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapidmeta", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.rapidmeta, args.output)
