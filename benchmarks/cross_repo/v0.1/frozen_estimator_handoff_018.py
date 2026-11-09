"""CROSS-EXCH-018: executable synthetic-only frozen estimand refusal handoff.

The producer, validator and real pooling consumer are loaded from exact immutable
repository commits. This orchestrator is NOT a scientific validation or R oracle.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
from unittest import mock


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def head(path: pathlib.Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", type=pathlib.Path, required=True)
    ap.add_argument("--rapidmeta", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    args = ap.parse_args()
    meta = args.meta.resolve(strict=True)
    rapid = args.rapidmeta.resolve(strict=True)
    output = args.output.resolve()
    spec_bytes = (pathlib.Path(__file__).parent / "frozen-estimand-018.json").read_bytes()

    def unique_members(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate registration member")
            result[key] = value
        return result

    spec = json.loads(spec_bytes, object_pairs_hook=unique_members)
    if (spec["record_version"], spec["case_id"], spec["registered_status"], spec["input_type"]) != (
        "1.0.0", "CROSS-EXCH-018", "NOT_RUN", "SYNTHETIC_FIXTURE_ONLY"
    ):
        raise RuntimeError("unrecognised pre-execution benchmark registration")
    expected_roles = {
        "meta-harness": "EXECUTED_PINNED_PRODUCER_VALIDATOR",
        "rapidmeta-kit": "EXECUTED_PINNED_CONSUMER",
        "e156-ecosystem-starter": "NOT_EXECUTED",
        "e156": "NOT_EXECUTED",
    }
    for name, role in expected_roles.items():
        if spec["repositories"][name]["role"] != role:
            raise RuntimeError(f"unexpected repository execution role: {name}")
    for name, directory in (("meta-harness", meta), ("rapidmeta-kit", rapid)):
        observed = head(directory)
        required = spec["repositories"][name]["commit"]
        if observed != required:
            raise RuntimeError(f"unfrozen {name}: {observed} != {required}")
        print(f"FROZEN CHECKOUT {name}: {observed}")
    if ".".join(map(str, sys.version_info[:3])) != spec["runtime"]["python"]:
        raise RuntimeError("unfrozen Python runtime")
    node = subprocess.check_output(["node", "--version"], text=True).strip().removeprefix("v")
    if node != spec["runtime"]["node"]:
        raise RuntimeError("unfrozen Node runtime")
    source = meta / spec["frozen_source"]["path"]
    source_bytes = source.read_bytes()
    if digest(source_bytes) != spec["frozen_source"]["sha256"]:
        raise RuntimeError("synthetic source bytes differ from frozen SHA256")

    # Load production bridge and raw duplicate-key/estimand validator from the
    # frozen producer checkout, NEVER from the editable orchestration checkout.
    module_path = meta / "benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py"
    module_spec = importlib.util.spec_from_file_location("frozen_canary_018", module_path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("missing pinned Meta-Harness producer")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    module.preflight(rapid)

    original = module.produce("ALLOW")
    changed = copy.deepcopy(original)
    changed["proposed_pool"]["estimand"]["measure"] = "OR"
    # The two trial rows still declare RR. A permissive boundary would send
    # a mixed-effect-type pool into the real downstream engine.
    cases = {
        "allow_rr_itt": module.wire(original),
        "refuse_or_rr_type_mismatch": module.wire(changed),
    }
    if set(cases) != set(spec["scenarios"]):
        raise RuntimeError("canary scenarios disagree with registration")
    output.mkdir(parents=True, exist_ok=False)
    (output / "inputs").mkdir()
    (output / "results").mkdir()
    digests = {}
    for name, raw in cases.items():
        in_file = output / "inputs" / f"{name}.json"
        out_file = output / "results" / f"{name}.json"
        in_file.write_bytes(raw)
        if name == "refuse_or_rr_type_mismatch":
            # Tripwire: ANY attempted subprocess invocation by a refused
            # exchange must fail this CI step. The real frozen consumer is
            # used for the positive control outside the tripwire.
            with mock.patch.object(
                module.subprocess, "run",
                side_effect=AssertionError("REFUSED estimand reached pooling subprocess")
            ) as spawn:
                result = module.consume(in_file.read_bytes(), rapid, name)
                spawn.assert_not_called()
            if ("estimand mismatch" not in result.get("refusal", "")
                    or result.get("engine_invoked") is not False):
                raise AssertionError("typed estimand mismatch was not refused before pooling")
        else:
            result = module.consume(in_file.read_bytes(), rapid, name)
            if (result.get("status") != "SYNTHETIC_ENGINE_EXECUTED"
                    or result.get("engine_invoked") is not True
                    or result.get("engine_output", {}).get("k_used") != 2
                    or result.get("engine_output", {}).get("measure") != "RR"):
                raise AssertionError("pinned RapidMeta did not pool two synthetic RR rows")
        if result["status"] != spec["scenarios"][name]:
            raise AssertionError(f"unexpected {name} result: {result}")
        out_file.write_bytes(module.wire(result))
        for file in (in_file, out_file):
            digests[str(file.relative_to(output))] = digest(file.read_bytes())
        print(f"{name}: {result['status']}, pool_invoked={result['engine_invoked']}")
    source_copy = output / "source.txt"
    source_copy.write_bytes(source_bytes)
    digests["source.txt"] = digest(source_copy.read_bytes())
    record = {
        "case_id": "CROSS-EXCH-018",
        "evidence_scope": "SYNTHETIC_TWO_REPOSITORY_HANDOFF_ONLY",
        "registration_sha256": digest(spec_bytes),
        "meta_harness_commit": head(meta),
        "rapidmeta_commit": head(rapid),
        "source_sha256": digest(source_bytes),
        "digests": digests,
        "clinical_validation": "NOT_TESTED",
        "external_R_oracle": "NOT_TESTED",
        "four_repository_benchmark": "NOT_RUN",
    }
    (output / "index.json").write_bytes(module.wire(record))
    print("CROSS-EXCH-018: 2/2 frozen synthetic handoffs executed; 1 type mismatch refused before real pooling")


if __name__ == "__main__":
    main()
