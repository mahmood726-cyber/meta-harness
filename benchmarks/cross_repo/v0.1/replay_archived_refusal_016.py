"""Re-run archived CROSS-EXCH-016 refusals through the exact frozen importer.

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

from compare_cross_os_016 import (compare, digest, load_json, assert_equal,
                                  pinned_engine_digest, _archive_file)
from frozen_cli_api_handoff_016 import pinned_meta_code_sha256

REPLAY_CASES = ("refuse", "manual_review", "source_trial_mismatch",
                "duplicate_shadow", "estimand_mismatch", "source_sha_tamper")
ROW_DECISIONS = {"refuse": "REFUSE", "manual_review": "MANUAL_REVIEW",
                 "source_trial_mismatch": "ALLOW", "estimand_mismatch": "ALLOW",
                 "source_sha_tamper": "ALLOW"}
TRIAL_BRIDGE_REFUSAL = "Declared trial_id does not match verbatim source"
DUPLICATE_KEY_REFUSAL = "duplicate JSON object member: decision"
# Registered from the frozen producer bytes, not derived from archive receipts.
SHADOWED_REFUSAL_SHA256 = "b37876be986b1b648307f670414fbb559523324e2424444ff643181563c1d0e7"
# Canonical frozen producer: RR rows with an OR proposed-pool measure.
# Registered on 25 October 2026 after prior runs; NOT a prospective prior freeze.
ESTIMAND_MISMATCH_SHA256 = "2409fd53c04c5a58649a1f37deaadcd048db7ef46ed7cfc5fda069332891d5f2"
ESTIMAND_MISMATCH_REFUSAL = "row 0: estimand mismatch (measure/population/outcome/timepoint)"
# Derived on 25 October 2026 from the existing pinned synthetic producer; not an
# earlier prospectively registered source-custody receipt.
SOURCE_TAMPER_SHA256 = "d7527284c97d43b3d758c31afaed717788437fa4f0bf6ac13dc9788ff35d8cb2"
FROZEN_SOURCE_SHA256 = "666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398"
SOURCE_TAMPER_REFUSAL = "row 0: source SHA-256 mismatch"

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
# Install before executing even the frozen module's top-level code.
# A module import can spawn a process before consume() is called; refusal
# replay must not rely on a guard installed after import side effects.
def refuse_process_audit(event, _args):
    if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn',
                 'os.exec', 'os.spawn', 'os.fork', 'os.forkpty',
                 'os.startfile', 'os.startfile/2'):
        raise AssertionError('NO_POOL: external process invoked')
sys.addaudithook(refuse_process_audit)
spec.loader.exec_module(module)
label = sys.argv[3]
if label not in ('refuse', 'manual_review', 'source_trial_mismatch',
                 'duplicate_shadow', 'estimand_mismatch', 'source_sha_tamper'):
    raise RuntimeError('unregistered negative replay label')
raw = sys.stdin.buffer.read()
# Fail closed for both subprocess.run and direct subprocess.Popen routes.
# These guards are active only within the isolated frozen-source replay child.
with mock.patch.object(module.subprocess, 'run', side_effect=AssertionError('NO_POOL: subprocess invoked')) as run_tripwire, \
     mock.patch.object(module.subprocess, 'Popen', side_effect=AssertionError('NO_POOL: subprocess invoked')) as popen_tripwire:
    result = module.consume(raw, rapid, label)
    run_tripwire.assert_not_called()
    popen_tripwire.assert_not_called()
if result.get('status') != 'REFUSED' or result.get('engine_invoked') is not False:
    raise RuntimeError('frozen importer did not refuse negative case without pooling')
if not isinstance(result.get('refusal'), str) or not result['refusal'].strip():
    raise RuntimeError('frozen refusal has no diagnostic')
if label == 'source_trial_mismatch' and result['refusal'] != 'Declared trial_id does not match verbatim source':
    raise RuntimeError('source/trial bridge did not supply expected specific refusal')
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
    # Derive the engine identity from the frozen *Git blob*, refusing dirty
    # worktree bytes. Archive-to-archive agreement alone is not sufficient.
    engine_sha = pinned_engine_digest(spec, rapid)
    producer_code_sha256 = pinned_meta_code_sha256(spec, meta)
    for archive in (ubuntu, windows):
        index = load_json(_archive_file(archive, "index.json"))
        assert_equal(index["rapidmeta_engine_sha256"], engine_sha,
                     "archived engine SHA against frozen source checkout")
        # Recompute from an independent exact-pinned Git checkout. Two OS
        # archives agreeing on an altered interpreter are not sufficient.
        assert_equal(index.get("meta_producer_code_sha256"),
                     producer_code_sha256,
                     "archived producer/importer SHA against frozen Git blobs")
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
            "producer_importer_code_sha256": producer_code_sha256,
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


def assert_registered_refusal_input(raw: bytes, label: str) -> None:
    """Bind a scenario label to its actual raw wire decisions before replay."""
    if label not in REPLAY_CASES:
        raise ValueError(f"unregistered negative replay label: {label}")
    if label == "duplicate_shadow":
        # This wire intentionally has repeated raw object members; it must be
        # rejected by the *strict raw parser*, never pre-decoded or normalized.
        # A matching producer receipt alone would not freeze this attack input.
        if digest(raw) != SHADOWED_REFUSAL_SHA256:
            raise ValueError("registered shadowed-decision input SHA256 mismatch")
        try:
            json.loads(raw.decode("utf-8"), object_pairs_hook=_unique,
                       parse_constant=_reject_nonfinite)
        except ValueError as exc:
            if str(exc) != "duplicate replay result member: decision":
                raise ValueError("shadowed-decision raw JSON lacked decision-key collision") from exc
        else:
            raise ValueError("shadowed-decision raw JSON was accepted by strict preparse")
        return
    if label == "estimand_mismatch" and digest(raw) != ESTIMAND_MISMATCH_SHA256:
        raise ValueError("registered estimand-mismatch input SHA256 mismatch")
    if label == "source_sha_tamper" and digest(raw) != SOURCE_TAMPER_SHA256:
        raise ValueError("registered source-tamper input SHA256 mismatch")
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("replay wire input must be UTF-8") from exc
    if decoded.startswith("\ufeff"):
        raise ValueError("replay wire input must not carry a BOM")
    try:
        payload = json.loads(decoded, object_pairs_hook=_unique,
                             parse_constant=_reject_nonfinite)
    except json.JSONDecodeError as exc:
        raise ValueError("malformed replay wire input") from exc
    rows = payload.get("rows") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not rows or any(
        not isinstance(row, dict) or row.get("decision") != ROW_DECISIONS[label]
        for row in rows
    ):
        raise ValueError(f"archived replay label/decision mismatch: {label}")
    if label == "source_sha_tamper":
        # Establish that this is the declared single-source-digest attack,
        # rather than an unrelated failure masquerading as source refusal.
        if (len(rows) != 2 or
                not all(isinstance(row.get("source"), dict) for row in rows) or
                rows[0]["source"].get("sha256") != "f" * 64 or
                rows[1]["source"].get("sha256") != FROZEN_SOURCE_SHA256 or
                any(row["source"].get("path") !=
                    "benchmarks/cross_repo/v0.1/synthetic-binary-arms.txt"
                    for row in rows)):
            raise ValueError("source-tamper replay lacks one deliberately corrupt archived source digest")
    if label == "estimand_mismatch":
        # The negative control must be a pure estimand inconsistency, never
        # a concealed REFUSE row or an unrelated importer failure.
        target = payload.get("proposed_pool")
        pooled = target.get("estimand") if isinstance(target, dict) else None
        if (len(rows) != 2 or not isinstance(pooled, dict) or
                pooled.get("measure") != "OR" or
                any(not isinstance(row.get("estimand"), dict) or
                    row["estimand"].get("measure") != "RR" or
                    {**row["estimand"], "measure": "OR"} != pooled
                    for row in rows)):
            raise ValueError("estimand replay lacks registered RR-row versus OR-pool mismatch")
    # Distinguish the harder accepted-importer / refused-consumer bridge from
    # the two cases refused at the generic importer. Replays must contain the
    # intended source/trial discrepancy, not merely any ALLOW input which
    # happens to fail somewhere downstream.
    if label == "source_trial_mismatch":
        mismatches = 0
        for row in rows:
            span = row.get("source_span")
            if (not isinstance(row.get("trial_id"), str) or
                    not isinstance(span, dict) or
                    not isinstance(span.get("verbatim"), str) or
                    not span["verbatim"].startswith("SYN-TRIAL-")):
                raise ValueError("trial-bridge replay missing source/trial identity")
            if span["verbatim"].split(" ", 1)[0] != row["trial_id"]:
                mismatches += 1
        if mismatches != 1:
            raise ValueError("trial-bridge replay requires exactly one source/trial mismatch")


def replay_frozen_bytes(meta: Path, rapid: Path, raw: bytes,
                        label: str = "manual_review") -> tuple[dict, str]:
    """Invoke actual frozen canary on one registered refusal; no Node execution."""
    assert_registered_refusal_input(raw, label)
    process = subprocess.run(
        [sys.executable, "-I", "-c", FROZEN_RUNNER, str(meta), str(rapid), label],
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


def verify_replay_observation(observed: dict, archived: dict, raw: bytes,
                              label: str = "manual_review"):
    """Recomputed archive hashes must not substitute for observed refusal."""
    assert_registered_refusal_input(raw, label)
    # bool and int compare equal in Python (0 == False). A numeric archived
    # no-pool receipt must never masquerade as an actual JSON boolean.
    for provenance, result in (("replayed", observed), ("archived", archived)):
        if not isinstance(result, dict) or type(result.get("engine_invoked")) is not bool:
            raise ValueError(f"{provenance} engine_invoked must be JSON boolean")
    for name, value in (
        ("case", label), ("input_sha256", digest(raw)),
        ("status", "REFUSED"), ("engine_invoked", False)
    ):
        assert_equal(observed.get(name), value, f"frozen replay {name}")
        assert_equal(archived.get(name), value, f"archived consumer {name}")
    reason = observed.get("refusal")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("frozen replay missing refusal provenance")
    assert_equal(archived.get("refusal"), reason,
                 "archived/frozen refusal provenance")
    if label == "source_trial_mismatch":
        assert_equal(reason, TRIAL_BRIDGE_REFUSAL,
                     "accepted-importer source/trial bridge refusal")
    if label == "duplicate_shadow":
        assert_equal(reason, DUPLICATE_KEY_REFUSAL,
                     "shadowed-decision raw duplicate-key refusal")
    if label == "estimand_mismatch":
        assert_equal(reason, ESTIMAND_MISMATCH_REFUSAL,
                     "frozen RR-row versus OR-pool importer refusal")
    if label == "source_sha_tamper":
        assert_equal(reason, SOURCE_TAMPER_REFUSAL,
                     "frozen source SHA mismatch importer refusal")
    if "engine_output" in archived or "engine_output" in observed:
        raise ValueError("refused replay contains pool output")



def assert_registered_replay_sha256(raw: bytes, label: str, registration: dict) -> None:
    """Recheck the frozen raw input at point of use, after archive comparison.

    A valid ordinary file can change after the comparator's SHA-256 pass
    without becoming a symlink. Never replay alternative REFUSE/MANUAL_REVIEW
    bytes merely because the substituted input still produces a refusal.
    """
    expected = registration.get("negative_input_sha256")
    if not isinstance(expected, dict) or not isinstance(expected.get(label), str):
        raise ValueError(f"missing registered negative replay input SHA256: {label}")
    if digest(raw) != expected[label]:
        raise ValueError(f"post-comparison registered negative input SHA256 drift: {label}")



def verified_archived_consumer(archive: Path, label: str,
                               expected_index_sha256: str) -> tuple[dict, str]:
    """Bind a replayed decision to the originally compared archive bytes.

    A regular result file (or its index) can change after cross-OS comparison.
    Read each exactly once, verify against the original checked index digest
    and its recorded file receipt, and parse/report the same result bytes.
    """
    index_raw = _archive_file(archive, "index.json").read_bytes()
    assert_equal(digest(index_raw), expected_index_sha256,
                 "post-comparison archived index SHA256 drift")
    index = json.loads(index_raw.decode("utf-8"), object_pairs_hook=_unique,
                       parse_constant=_reject_nonfinite)
    rel = f"results/{label}.json"
    raw = _archive_file(archive, rel).read_bytes()
    receipts = index.get("digests") if isinstance(index, dict) else None
    expected = receipts.get(rel) if isinstance(receipts, dict) else None
    if not isinstance(expected, str) or digest(raw) != expected:
        raise ValueError(f"post-comparison archived result SHA256 drift: {label}")
    result = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique,
                        parse_constant=_reject_nonfinite)
    if not isinstance(result, dict) or not isinstance(result.get("consumer"), dict):
        raise ValueError(f"post-comparison archived consumer missing: {label}")
    return result["consumer"], digest(raw)


def run(registration: Path, ubuntu: Path, windows: Path,
        meta: Path, rapid: Path) -> dict:
    # Freeze source/consumer identities before replay. Pass the independently
    # derived committed engine digest into the archive comparator, rather than
    # accidentally omitting its required fail-closed fourth argument.
    spec = load_json(registration)
    pins = exact_checkout_checks(spec, meta, rapid, ubuntu, windows)
    prior = compare(registration, ubuntu, windows, pins["engine_sha256"])
    replays = {}
    for os_label, archive in (
        ("ubuntu-24.04", ubuntu), ("windows-2025", windows)
    ):
        os_replays = {}
        for label in REPLAY_CASES:
            raw = _archive_file(archive, f"inputs/{label}.json").read_bytes()
            assert_registered_replay_sha256(raw, label, spec)
            archived, result_sha = verified_archived_consumer(
                archive, label, prior["archives"][os_label]["index_sha256"])
            observed, stdout_sha = replay_frozen_bytes(meta, rapid, raw, label)
            verify_replay_observation(observed, archived, raw, label)
            os_replays[label] = {
                "input_sha256": digest(raw),
                "archived_result_sha256": result_sha,
                "replay_stdout_sha256": stdout_sha,
                "status": observed["status"], "engine_invoked": False,
                "refusal": observed["refusal"]
            }
        replays[os_label] = os_replays
    for label in REPLAY_CASES:
        assert_equal(replays["ubuntu-24.04"][label]["input_sha256"],
                     replays["windows-2025"][label]["input_sha256"],
                     f"cross-OS replayed raw input: {label}")
        assert_equal(replays["ubuntu-24.04"][label]["refusal"],
                     replays["windows-2025"][label]["refusal"],
                     f"cross-OS replayed refusal provenance: {label}")
    return {
        "record_version": "1.1.0", "case_id": "CROSS-EXCH-016",
        "subcase": "frozen_archived_importer_trial_bridge_and_duplicate_key_no_pool_replay",
        "refusal_replay_count": len(REPLAY_CASES) * 2,
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
    print(f"CROSS-EXCH-016 ARCHIVED NO-POOL REPLAY: {len(REPLAY_CASES) * 2} "
          "actual archived synthetic inputs refused through frozen code, "
          "including accepted-importer/source-trial bridge; zero engine "
          "subprocess calls; synthetic transport scope only")


if __name__ == "__main__":
    main()
