"""Independent downloaded Ubuntu/Windows candidate-PR59 synthetic handoff comparison.

Not a registered CROSS-EXCH case, clinical validation, R/metafor oracle, or
signed four-repository execution. Never trust self-reported artifact receipts
without independent frozen-input identities and raw-byte rechecks.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

from compare_cross_os_016 import _archive_file, digest, load_json

RAPIDMETA_SHA = "9549a59ad77000781df23577680bcb1adb7334b6"
RAPIDMETA_BLOB = "3dafd0ab344cb305da1d6a77ff3c22faae8f7551"
REGISTERED_SHA = "368137dc437543c721b98be39c14282c338f7797"
SOURCE_SHA = "666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398"
ENGINE = "template/assets/vendor/pairwise-pool.js"
# Precomputed from exact frozen synthetic source and canonical producer wire
# independently of either runner's generated index or result receipts.
RAW_SHA = {
    "allow_synthetic_control": "514f659d51fd477f702cc25303d45c3a440c5282324de287ba1fab8d30385ce0",
    "refuse": "7889d8e96a54b4d7dece681be11d1746eaa32cbaa4e2335a4a934c511ebff86d",
    "manual_review": "20e51ea4525053d8eb4f3d2656d5eac2c35ac0c489ca4b5d60a2fdd7c88cd5a6",
    "shadowed_refuse": "b37876be986b1b648307f670414fbb559523324e2424444ff643181563c1d0e7",
    "source_hash_drift": "d7527284c97d43b3d758c31afaed717788437fa4f0bf6ac13dc9788ff35d8cb2",
    "source_trial_mismatch": "a4817e7478833a42d4db0f4ac111b278929104b059cfad9169e7529bd623a982",
}
SCOPES = {
    "clinical_validation": "NOT_TESTED",
    "external_R_oracle": "NOT_TESTED",
    "four_repository_benchmark": "NOT_RUN",
    "common_cross_exch_001_015": "NOT_RUN",
    "common_four_repository_test": "NOT_RUN",
    "candidate_scope": "SYNTHETIC_DEVELOPMENT_HEAD_COMPATIBILITY_ONLY",
}


def must_equal(observed, expected, label):
    if observed != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {observed!r}")


def independently_pinned_engine(rapidmeta: Path) -> str:
    """Check a fresh comparator checkout, not either producer's engine claim."""
    head = subprocess.check_output(["git", "-C", str(rapidmeta), "rev-parse", "HEAD"],
                                   text=True, timeout=15).strip()
    must_equal(head, RAPIDMETA_SHA, "independent consumer Git HEAD")
    blob = subprocess.check_output(
        ["git", "-C", str(rapidmeta), "rev-parse", f"HEAD:{ENGINE}"],
        text=True, timeout=15).strip()
    must_equal(blob, RAPIDMETA_BLOB, "independent engine Git blob")
    expected = subprocess.check_output(
        ["git", "-C", str(rapidmeta), "show", f"HEAD:{ENGINE}"], timeout=15)
    path = rapidmeta
    for segment in Path(ENGINE).parts:
        path = path / segment
        if path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)()):
            raise ValueError("linked independent engine path")
    must_equal(digest(path.read_bytes()), digest(expected),
               "independent executable worktree SHA256")
    return digest(expected)


def inspect(root: Path, meta_sha: str, engine_sha: str) -> dict:
    index = load_json(_archive_file(root, "index.json"))
    expected = {
        "runner_checkout_sha": meta_sha,
        "rapidmeta_pinned_sha": RAPIDMETA_SHA,
        "consumer_profile": "rapidmeta-pr59-20261026",
        "consumer_engine_git_blob": RAPIDMETA_BLOB,
        "registered_manifest_rapidmeta_sha_unchanged": REGISTERED_SHA,
        "source_sha256": SOURCE_SHA,
        "rapidmeta_engine_sha256": engine_sha,
        "python_runtime": "3.13.7",
        "node_runtime": "v22.14.0",
        **SCOPES,
    }
    for key, value in expected.items():
        must_equal(index.get(key), value, f"index {key}")
    required = {
        f"{folder}/{label}.json"
        for folder in ("inputs", "results") for label in RAW_SHA
    }
    receipts = index.get("digests")
    if not isinstance(receipts, dict) or set(receipts) != required:
        raise ValueError("missing or unregistered digest receipts")
    actual_files = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*") if p.is_file() or p.is_symlink()
    }
    if actual_files != required | {"index.json"}:
        raise ValueError("unexpected or missing archived files")
    for rel in sorted(required):
        declared = receipts[rel]
        if (not isinstance(declared, str) or len(declared) != 64
                or any(c not in "0123456789abcdef" for c in declared)):
            raise ValueError(f"malformed digest receipt {rel}")
        must_equal(digest(_archive_file(root, rel).read_bytes()), declared,
                   f"archived input/result digest {rel}")
    seen = {}
    for label, immutable_sha in RAW_SHA.items():
        inp = _archive_file(root, f"inputs/{label}.json")
        must_equal(digest(inp.read_bytes()), immutable_sha,
                   f"independently frozen raw input {label}")
        if label == "shadowed_refuse":
            try:
                load_json(inp)
            except ValueError as exc:
                if "duplicate archived JSON member: decision" not in str(exc):
                    raise ValueError("shadow refusal has wrong raw JSON failure") from exc
            else:
                raise ValueError("duplicate-key shadow case not actually duplicated")
        else:
            decoded = load_json(inp)
            if not isinstance(decoded, dict) or len(decoded.get("rows", [])) != 2:
                raise ValueError(f"malformed synthetic exchange {label}")
        result = load_json(_archive_file(root, f"results/{label}.json"))
        must_equal(result.get("case"), label, f"output case identity {label}")
        must_equal(result.get("input_sha256"), immutable_sha,
                   f"output/input binding {label}")
        actual_invoked = result.get("engine_invoked")
        if type(actual_invoked) is not bool:
            raise ValueError(f"engine_invoked is not a strict JSON boolean: {label}")
        allowed = label == "allow_synthetic_control"
        must_equal(actual_invoked, allowed, f"no-pool execution decision {label}")
        must_equal(result.get("status"),
                   "SYNTHETIC_ENGINE_EXECUTED" if allowed else "REFUSED",
                   f"output status {label}")
        if allowed:
            if "refusal" in result:
                raise ValueError("allowed synthetic smoke reports refusal")
            numerical = result.get("engine_output")
            if not isinstance(numerical, dict):
                raise ValueError("missing synthetic statistical smoke output")
            must_equal(numerical.get("k_used"), 2, "pooled synthetic trial count")
            must_equal(numerical.get("measure"), "RR", "synthetic measure")
            for k in ("mu_log", "tau2"):
                v = numerical.get(k)
                if (isinstance(v, bool) or not isinstance(v, (int, float))
                        or not math.isfinite(v)):
                    raise ValueError(f"nonfinite or nonnumeric output {label}/{k}")
            if numerical["tau2"] < 0:
                raise ValueError("negative synthetic heterogeneity variance")
            seen[label] = {"status": result["status"], "invoked": True,
                           "numerical": numerical}
        else:
            if ("engine_output" in result or not isinstance(result.get("refusal"), str)
                    or not result["refusal"].strip()):
                raise ValueError(f"pooled output or missing refusal provenance {label}")
            seen[label] = {"status": result["status"], "invoked": False,
                           "reason": result["refusal"]}
    return {"index_sha256": digest(_archive_file(root, "index.json").read_bytes()),
            "receipts": len(required), "inputs": {k: receipts[f"inputs/{k}.json"]
                                               for k in RAW_SHA},
            "cases": seen}


def compare(ubuntu: Path, windows: Path, meta_sha: str, engine_sha: str) -> dict:
    if len(meta_sha) != 40 or any(c not in "0123456789abcdef" for c in meta_sha):
        raise ValueError("full immutable Meta-Harness HEAD required")
    linux = inspect(ubuntu, meta_sha, engine_sha)
    win = inspect(windows, meta_sha, engine_sha)
    must_equal(linux["inputs"], win["inputs"], "cross-platform raw input identity")
    for label in RAW_SHA:
        a, b = linux["cases"][label], win["cases"][label]
        must_equal(a["status"], b["status"], f"cross-platform outcome {label}")
        must_equal(a["invoked"], b["invoked"], f"cross-platform no-pool {label}")
        if not a["invoked"]:
            must_equal(a["reason"], b["reason"],
                       f"cross-platform refusal provenance {label}")
        else:
            for field in ("k_used", "measure"):
                must_equal(a["numerical"][field], b["numerical"][field],
                           f"cross-platform synthetic calculation {field}")
            for field in ("mu_log", "tau2"):
                if not math.isclose(a["numerical"][field], b["numerical"][field],
                                    rel_tol=1e-12, abs_tol=1e-12):
                    raise ValueError(f"cross-platform synthetic numerical drift: {field}")
    return {
        "version": "1.0.0", "type": "CANDIDATE_ONLY_NOT_REGISTERED",
        "status": "PASS", "meta_harness_commit": meta_sha,
        "rapidmeta_commit": RAPIDMETA_SHA, "independent_engine_sha256": engine_sha,
        "precomputed_input_sha256": RAW_SHA, "scenario_count": 6,
        "no_pool_count": 5, "archived_receipts_verified": linux["receipts"] + win["receipts"],
        "cross_os_synthetic_numerical_parity": "PASS", **SCOPES,
        "cross_exch_016": "UNCHANGED_SEPARATE_SYNTHETIC_PASS",
        "archives": {"ubuntu-24.04": {"index_sha256": linux["index_sha256"]},
                     "windows-2025": {"index_sha256": win["index_sha256"]}},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ubuntu", required=True, type=Path)
    parser.add_argument("--windows", required=True, type=Path)
    parser.add_argument("--meta-head", required=True)
    parser.add_argument("--rapidmeta", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    report = compare(args.ubuntu, args.windows, args.meta_head,
                     independently_pinned_engine(args.rapidmeta))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print("CANDIDATE-ONLY downloaded cross-OS comparison PASS: "
          "six synthetic scenarios, five no-pool refusals, 24 digest checks")


if __name__ == "__main__":
    main()
