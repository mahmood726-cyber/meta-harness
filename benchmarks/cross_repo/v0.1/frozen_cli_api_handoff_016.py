"""Frozen CROSS-EXCH-016 raw CLI/API parity and real RapidMeta refusal handoff.

Synthetic text only. Produces archived raw JSON, outcomes, and SHA-256 receipts.
No R oracle, human review, clinical dataset, or independent validation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from unittest import mock


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def receipt_key(path: Path) -> str:
    """Archive index keys are portable POSIX paths, never OS-native separators."""
    return path.as_posix()


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


PRODUCER_CODE_PATHS = (
    "harness/exchange_v01.py",
    "benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py",
)


def pinned_meta_code_sha256(spec: dict, meta: Path) -> dict[str, str]:
    """Require the exact committed importer and producer bytes, not just HEAD.

    A checkout can report the frozen commit while locally modified code is
    executed. Compare both files against immutable Git blobs before any
    importer or RapidMeta engine is invoked. Symlink aliases fail closed.
    """
    expected = spec["repositories"]["meta-harness"]["commit"]
    actual = git_head(meta)
    if actual != expected:
        raise ValueError(f"frozen Meta-Harness checkout pin mismatch: {actual} != {expected}")
    digests = {}
    for relative in PRODUCER_CODE_PATHS:
        path = meta / relative
        if path.is_symlink():
            raise ValueError(f"symlinked frozen Meta-Harness code: {relative}")
        committed = subprocess.check_output(
            ["git", "-C", str(meta), "show", f"HEAD:{relative}"], timeout=15
        )
        if path.read_bytes() != committed:
            raise ValueError(f"dirty frozen Meta-Harness code: {relative}")
        digests[relative] = sha(committed)
    return digests


def no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate registration key: {key}")
        obj[key] = value
    return obj


def runner_image(spec: dict) -> dict:
    """Bind the declared GitHub Actions image to an observed runtime OS.

    A self-reported runner label alone cannot attest a Windows image build;
    Actions job metadata remains independent evidence of image identity.
    """
    label = os.environ.get("BENCHMARK_RUNNER_IMAGE")
    expected = spec.get("runtime", {}).get("os")
    if not isinstance(expected, list) or expected != ["ubuntu-24.04", "windows-2025"]:
        raise ValueError("frozen registration must explicitly list exact allowed OS runners")
    if label not in expected:
        raise ValueError("running CI image not in frozen benchmark registration")
    family = platform.system()
    if (label == "ubuntu-24.04" and family != "Linux") or (
        label == "windows-2025" and family != "Windows"
    ):
        raise ValueError("declared CI runner image inconsistent with local OS family")
    if label == "ubuntu-24.04":
        info = platform.freedesktop_os_release()
        if info.get("ID") != "ubuntu" or info.get("VERSION_ID") != "24.04":
            raise ValueError("Ubuntu runner distro/version disagrees with frozen registration")
    return {"runner_image_label": label, "observed_system": family,
            "observed_release": platform.release(), "observed_version": platform.version()}


def frozen_spec(path: Path, meta: Path, rapid: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    spec = json.loads(raw, object_pairs_hook=no_duplicates)
    if (spec.get("record_version"), spec.get("case_id"),
            spec.get("registered_status"), spec.get("input_type")) != (
            "1.0.0", "CROSS-EXCH-016", "NOT_RUN", "SYNTHETIC_FIXTURE_ONLY"):
        raise ValueError("invalid frozen CLI/API registration")
    roles = {
        "meta-harness": "EXECUTED_PINNED_PRODUCER_VALIDATOR_IMPORTER",
        "rapidmeta-kit": "EXECUTED_PINNED_CONSUMER",
        "e156": "NOT_EXECUTED",
        "e156-ecosystem-starter": "NOT_EXECUTED",
    }
    runner_image(spec)  # Refuse mismatched OS before executing producers.
    for name, role in roles.items():
        if spec["repositories"][name]["role"] != role:
            raise ValueError(f"unexpected execution role: {name}")
    for name, root in (("meta-harness", meta), ("rapidmeta-kit", rapid)):
        expected = spec["repositories"][name]["commit"]
        got = git_head(root)
        if got != expected:
            raise ValueError(f"PIN MISMATCH: {name} {got} != {expected}")
        print(f"FROZEN CHECKOUT {name}: {got}")
    if platform.python_version() != spec["runtime"]["python"]:
        raise ValueError("Python runtime not pinned")
    node = subprocess.check_output(["node", "--version"], text=True).strip().removeprefix("v")
    if node != spec["runtime"]["node"]:
        raise ValueError("Node runtime not pinned")
    source = (meta / spec["frozen_source"]["path"]).read_bytes()
    if sha(source) != spec["frozen_source"]["sha256"]:
        raise ValueError("source SHA-256 differs from frozen registration")
    return spec, raw


def make_cases(canary) -> dict[str, bytes]:
    good = canary.produce("ALLOW")
    good_wire = canary.wire(good)
    old = b'"decision":"ALLOW"'
    if old not in good_wire:
        raise RuntimeError("cannot construct shadowed decision negative")
    cases = {
        "allow_rr_itt": good_wire,
        "refuse": canary.wire(canary.produce("REFUSE")),
        "manual_review": canary.wire(canary.produce("MANUAL_REVIEW")),
        "duplicate_shadow": good_wire.replace(
            old, b'"decision":"REFUSE","decision":"ALLOW"', 1),
        "unicode_duplicate_shadow": good_wire.replace(
            old, b'"decision":"REFUSE","decisio' + bytes([92]) + b'u006e":"ALLOW"', 1),
        "malformed_json": b'{"schema_version":',
        "invalid_utf8": bytes([255]),
    }
    changes = {
        "duplicate_trial_id": lambda p: p["rows"][1].__setitem__("trial_id", p["rows"][0]["trial_id"]),
        "source_sha_tamper": lambda p: p["rows"][0]["source"].__setitem__("sha256", "f" * 64),
        "estimand_mismatch": lambda p: p["proposed_pool"]["estimand"].__setitem__("measure", "OR"),
        "wrong_locator": lambda p: p["rows"][0]["source_span"].__setitem__("locator", "line 1"),
        "source_trial_mismatch": lambda p: p["rows"][0].__setitem__("trial_id", "SYN-TRIAL-99"),
    }
    for name, mutate in changes.items():
        candidate = copy.deepcopy(good)
        mutate(candidate)
        cases[name] = canary.wire(candidate)
    return cases


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True, type=Path)
    ap.add_argument("--rapidmeta", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    meta = args.meta.resolve(strict=True)
    rapid = args.rapidmeta.resolve(strict=True)
    output = args.output.resolve()
    registration = Path(__file__).parent / "frozen-cli-api-016.json"
    spec, registration_bytes = frozen_spec(registration, meta, rapid)
    # git rev-parse HEAD alone does not establish which bytes Python executes.
    producer_code_sha256 = pinned_meta_code_sha256(spec, meta)

    producer_file = meta / "benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py"
    spec_module = importlib.util.spec_from_file_location("frozen_producer_016", producer_file)
    if spec_module is None or spec_module.loader is None:
        raise RuntimeError("missing frozen producer")
    canary = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(canary)
    # The module prepends the FROZEN producer root to sys.path.
    from harness.exchange_v01 import import_exchange_json
    _, engine_sha = canary.preflight(rapid)
    cases = make_cases(canary)
    if set(cases) != set(spec["scenarios"]):
        raise RuntimeError("scenario registry differs from executable cases")
    # Check the frozen ALLOW source/estimand/trial wire *before* running
    # any importer or statistical consumer, not solely in the OS comparator.
    allowed_labels = {name for name, expectation in spec["scenarios"].items()
                      if expectation["consumer"] == "SYNTHETIC_ENGINE_EXECUTED"}
    allowed_hashes = spec.get("allowed_input_sha256")
    if not isinstance(allowed_hashes, dict) or set(allowed_hashes) != allowed_labels:
        raise RuntimeError("missing pre-registered allowed input SHA256 map")
    for name in sorted(allowed_labels):
        if (not isinstance(allowed_hashes[name], str) or
                sha(cases[name]) != allowed_hashes[name]):
            raise RuntimeError(f"registered allowed input SHA256 drift: {name}")

    # Freeze the accepted-importer / refused-trial-bridge raw wire as well as
    # the generic-importer refusals, including shadowed raw JSON keys,
    # before any consumer is executed.
    # Receipts produced by this run cannot independently pin their own inputs.
    negative_labels = {"refuse", "manual_review", "source_trial_mismatch",
                       "duplicate_shadow"}
    negative_hashes = spec.get("negative_input_sha256")
    if not isinstance(negative_hashes, dict) or set(negative_hashes) != negative_labels:
        raise RuntimeError("missing registered no-pool negative input SHA256 map")
    for name in sorted(negative_labels):
        expected_sha = negative_hashes[name]
        if not isinstance(expected_sha, str) or sha(cases[name]) != expected_sha:
            raise RuntimeError(f"registered negative input SHA256 drift: {name}")

    output.mkdir(parents=True, exist_ok=False)
    (output / "inputs").mkdir()
    (output / "results").mkdir()
    digests = {}
    for name, raw in sorted(cases.items()):
        in_path = output / "inputs" / (name + ".json")
        out_path = output / "results" / (name + ".json")
        in_path.write_bytes(raw)
        try:
            payload = import_exchange_json(in_path.read_bytes(), meta)
            api_status, reason = "ACCEPTED", None
        except ValueError as exc:
            payload = None
            api_status, reason = "REFUSED", str(exc)

        # True subprocess entry point from the frozen checked-out producer;
        # not a shell wrapper that just calls the API on already decoded JSON.
        cli = subprocess.run(
            [sys.executable, "-m", "harness.exchange_v01", "--exchange",
             str(in_path), "--archive-root", str(meta)],
            cwd=meta, capture_output=True, text=True, check=False, timeout=20
        )
        cli_status = "ACCEPTED" if cli.returncode == 0 else "REFUSED"
        if cli_status != api_status:
            raise AssertionError(f"CLI/API acceptance diverged for {name}")
        if api_status == "REFUSED":
            if not reason or reason not in cli.stderr:
                raise AssertionError(f"CLI/API refusal reasons diverged for {name}")
        elif "EXCHANGE VERIFIED" not in cli.stdout or payload is None:
            raise AssertionError(f"CLI acceptance lacks verified import for {name}")
        if api_status != spec["scenarios"][name]["importer"]:
            raise AssertionError(f"unexpected importer status for {name}: {api_status}")

        if spec["scenarios"][name]["consumer"] == "REFUSED":
            with mock.patch.object(
                canary.subprocess, "run",
                side_effect=AssertionError("refused candidate attempted engine subprocess")
            ) as attempted:
                consumer = canary.consume(in_path.read_bytes(), rapid, name)
                attempted.assert_not_called()
        else:
            consumer = canary.consume(in_path.read_bytes(), rapid, name)
            if (consumer.get("engine_invoked") is not True or
                    consumer.get("engine_output", {}).get("k_used") != 2 or
                    consumer["engine_output"].get("measure") != "RR"):
                raise AssertionError("valid RR/ITT control did not execute pinned RapidMeta")
        if (consumer["status"] != spec["scenarios"][name]["consumer"] or
                consumer["engine_invoked"] != (name == "allow_rr_itt")):
            raise AssertionError(f"unexpected frozen downstream result {name}: {consumer}")
        result = {
            "name": name, "raw_sha256": sha(raw), "cli_status": cli_status,
            "api_status": api_status, "api_refusal": reason,
            "consumer": consumer, "clinical_validation": "NOT_TESTED",
        }
        out_path.write_bytes(canary.wire(result))
        for file in (in_path, out_path):
            digests[receipt_key(file.relative_to(output))] = sha(file.read_bytes())
        print(f"{name}: cli={cli_status} api={api_status} "
              f"consumer={consumer['status']} pool_invoked={consumer['engine_invoked']}")

    source_bytes = (meta / spec["frozen_source"]["path"]).read_bytes()
    (output / "source.txt").write_bytes(source_bytes)
    digests["source.txt"] = sha(source_bytes)
    index = {
        "case_id": "CROSS-EXCH-016",
        "observed_runner": runner_image(spec),
        "evidence_scope": "SYNTHETIC_FROZEN_TWO_REPOSITORY_CLI_API_HANDOFF_ONLY",
        "registration_sha256": sha(registration_bytes),
        "meta_harness_commit": git_head(meta),
        "meta_producer_code_sha256": producer_code_sha256,
        "rapidmeta_commit": git_head(rapid),
        "python_runtime": platform.python_version(),
        "node_runtime": subprocess.check_output(["node", "--version"], text=True).strip(),
        "rapidmeta_engine_sha256": engine_sha,
        "source_sha256": sha(source_bytes),
        "digests": digests,
        "external_R_oracle": "NOT_TESTED",
        "four_repo_suite": "NOT_RUN",
        "human_adjudication": "NOT_TESTED",
        "clinical_validation": "NOT_TESTED",
    }
    (output / "index.json").write_bytes(canary.wire(index))
    print(f"CROSS-EXCH-016 completed: {len(cases)} synthetic CLI/API checks, "
          f"{len(digests)} independently recheckable digests; "
          "not four-repo scientific validation")


if __name__ == "__main__":
    main()
