"""Independent archived-artifact comparison for the frozen CROSS-EXCH-016 canary.

Compare *actual outputs from both CI matrix jobs*, not newly manufactured results.
Transport/refusal parity only: does not establish numerical or clinical accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

OS_NAMES = {"ubuntu-24.04": "Linux", "windows-2025": "Windows"}
CASE_ID = "CROSS-EXCH-016"
ENGINE_PATH = "template/assets/vendor/pairwise-pool.js"


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


def _archive_link(path: Path) -> bool:
    """Refuse POSIX symlinks and Windows NTFS junction aliases."""
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


def _archive_file(root: Path, relative: str) -> Path:
    """Only read a real in-archive file, never a link or traversal alias.

    Digest equality alone cannot establish custody when an archived path (or
    its parent directory) resolves through a symlink to external mutable bytes.
    This check is for downloaded CI artefacts, not historical clinical data.
    """
    parts = relative.split("/")
    if (not relative or "\\" in relative or
            any(part in {"", ".", ".."} for part in parts)):
        raise ValueError(f"invalid archived relative path: {relative}")
    if _archive_link(root) or not root.is_dir():
        raise ValueError("archive root is a symlink or not a directory")
    parent = root
    for segment in parts[:-1]:
        parent = parent / segment
        if _archive_link(parent) or not parent.is_dir():
            raise ValueError(f"archive parent is a symlink or not a directory: {relative}")
    path = parent / parts[-1]
    if _archive_link(path) or not path.is_file():
        raise ValueError(f"archive file is a symlink or not regular: {relative}")
    return path


def pinned_engine_digest(registration: dict, rapidmeta: Path) -> str:
    """Independently bind the archived engine identity to an immutable git blob.

    The CI comparator checks out the frozen RapidMeta commit separately from
    the producers. Two matching self-reported archive digests are insufficient.
    """
    rapidmeta = rapidmeta.resolve(strict=True)
    head = subprocess.check_output(
        ["git", "-C", str(rapidmeta), "rev-parse", "HEAD"],
        text=True, timeout=15,
    ).strip()
    assert_equal(head, registration["repositories"]["rapidmeta-kit"]["commit"],
                 "independent RapidMeta checkout pin")
    committed = subprocess.check_output(
        ["git", "-C", str(rapidmeta), "show", f"HEAD:{ENGINE_PATH}"],
        timeout=15,
    )
    worktree = (rapidmeta / ENGINE_PATH).read_bytes()
    assert_equal(digest(worktree), digest(committed),
                 "dirty RapidMeta engine worktree SHA256")
    return digest(committed)


def check_archive(registration: dict, registration_sha: str, root: Path,
                  os_name: str, expected_engine_sha256: str):
    """Rehash and inspect one real CI job archive without invoking a producer."""
    index = load_json(_archive_file(root, "index.json"))
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
    # An archived self-reported clinical status is not an independent verdict.
    # Refuse promotion even when both OS archives agree and rehash receipts.
    assert_equal(index.get("clinical_validation"), "NOT_TESTED", "clinical validation scope")
    engine_sha = index.get("rapidmeta_engine_sha256")
    if not isinstance(engine_sha, str) or len(engine_sha) != 64 or any(ch not in "0123456789abcdef" for ch in engine_sha):
        raise ValueError("engine SHA256 is absent or malformed")
    assert_equal(engine_sha, expected_engine_sha256, "pinned RapidMeta engine SHA256")

    scenarios = registration["scenarios"]
    frozen_raw = registration.get("negative_input_sha256")
    if (not isinstance(frozen_raw, dict) or
            set(frozen_raw) != {"refuse", "manual_review",
                                "source_trial_mismatch", "duplicate_shadow",
                                "estimand_mismatch", "source_sha_tamper"} or
            any(not isinstance(value, str) or len(value) != 64 or
                any(ch not in "0123456789abcdef" for ch in value)
                for value in frozen_raw.values())):
        raise ValueError("missing or malformed pre-registered negative input SHA256")
    # Bind accepted RR/ITT source/trial/estimand bytes to a digest registered
    # independently of both producer archives. Matching rehashed archives
    # alone cannot demonstrate that the pooled input remained frozen.
    allowed_raw = registration.get("allowed_input_sha256")
    allowed_labels = {label for label, expectation in scenarios.items()
                      if expectation["consumer"] == "SYNTHETIC_ENGINE_EXECUTED"}
    if (not isinstance(allowed_raw, dict) or
            set(allowed_raw) != allowed_labels or
            any(not isinstance(value, str) or len(value) != 64 or
                any(ch not in "0123456789abcdef" for ch in value)
                for value in allowed_raw.values())):
        raise ValueError("missing or malformed pre-registered allowed input SHA256")
    expected_files = {"source.txt"} | {
        f"{folder}/{label}.json" for folder in ("inputs", "results") for label in scenarios
    }
    if not isinstance(index.get("digests"), dict) or set(index["digests"]) != expected_files:
        raise ValueError("incomplete or unexpected archive receipts")
    for name in sorted(expected_files):
        checksum = index["digests"][name]
        if not isinstance(checksum, str) or len(checksum) != 64 or digest(_archive_file(root, name).read_bytes()) != checksum:
            raise ValueError(f"archived SHA256 integrity failure: {os_name}/{name}")
    assert_equal(index["digests"]["source.txt"], index["source_sha256"], "archived source receipt")

    decisions = {}
    numerical_controls = {}
    for label, expected in scenarios.items():
        raw = _archive_file(root, f"inputs/{label}.json").read_bytes()
        result = load_json(_archive_file(root, f"results/{label}.json"))
        assert_equal(result.get("clinical_validation"), "NOT_TESTED",
                     f"case clinical validation scope {label}")
        input_sha = digest(raw)
        # A hash receipt inside the same producer archive does not freeze the
        # expected raw input. Bind all three replayed no-pool cases to bytes
        # pre-registered in the independently versioned frozen specification.
        if label in frozen_raw:
            assert_equal(input_sha, frozen_raw[label],
                         f"registered negative input SHA256 {label}")
        if label in allowed_raw:
            assert_equal(input_sha, allowed_raw[label],
                         f"registered allowed input SHA256 {label}")
        assert_equal(result.get("name"), label, "output case label")
        assert_equal(result.get("raw_sha256"), input_sha, "result/input digest")
        assert_equal(result.get("cli_status"), expected["importer"], "CLI decision")
        assert_equal(result.get("api_status"), expected["importer"], "API decision")
        # Status-only parity can mask divergent or missing refusal provenance.
        # This diagnostic was archived by the frozen producer on each OS.
        api_refusal = result.get("api_refusal")
        if expected["importer"] == "REFUSED":
            if not isinstance(api_refusal, str) or not api_refusal.strip():
                raise ValueError(f"missing importer refusal reason: {label}")
            if label == "duplicate_shadow" and api_refusal != "duplicate JSON object member: decision":
                raise ValueError("shadowed decision was not rejected by raw duplicate-key preparse")
            if label == "estimand_mismatch" and api_refusal != (
                "row 0: estimand mismatch (measure/population/outcome/timepoint)"
            ):
                raise ValueError("estimand mismatch was not rejected at raw importer")
            if label == "source_sha_tamper" and api_refusal != "row 0: source SHA-256 mismatch":
                raise ValueError("source-hash tamper was not rejected at raw importer")
        elif api_refusal is not None:
            raise ValueError(f"accepted importer carried refusal reason: {label}")
        consumer = result.get("consumer")
        if not isinstance(consumer, dict):
            raise ValueError(f"absent consumer result: {label}")
        assert_equal(consumer.get("case"), label, "consumer case identity")
        assert_equal(consumer.get("input_sha256"), input_sha, "downstream input digest")
        assert_equal(consumer.get("status"), expected["consumer"], "consumer decision")
        allowed = label == "allow_rr_itt"
        # Python considers 0 == False and 1 == True. An archived JSON number
        # must not impersonate the producer's boolean engine-execution receipt,
        # even when both OS archives and their SHA receipts agree.
        if type(consumer.get("engine_invoked")) is not bool:
            raise ValueError(f"engine invocation must be JSON boolean: {label}")
        assert_equal(consumer["engine_invoked"], allowed, "engine invocation")
        downstream_refusal = consumer.get("refusal")
        if consumer.get("status") == "REFUSED":
            if not isinstance(downstream_refusal, str) or not downstream_refusal.strip():
                raise ValueError(f"missing downstream refusal reason: {label}")
        elif downstream_refusal is not None:
            raise ValueError(f"pooled result carried refusal reason: {label}")
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
            # This validates a reported output's domain, not its scientific
            # correctness. tau^2 is a variance and cannot be negative, even
            # if both rehashed CI archives report the same invalid number.
            if summary["tau2"] < 0:
                raise ValueError("negative heterogeneity variance in pinned synthetic smoke")
            numerical_controls[label] = {key: summary[key]
                                         for key in ("k_used", "measure", "mu_log", "tau2")}
        elif consumer.get("status") != "REFUSED" or "engine_output" in consumer:
            raise ValueError(f"refused case pooled or published engine output: {label}")
        decisions[label] = {
            "raw_sha256": input_sha,
            "cli": result["cli_status"],
            "api": result["api_status"],
            "api_refusal": api_refusal,
            "consumer": consumer["status"],
            "consumer_case": consumer["case"],
            "downstream_refusal": downstream_refusal,
            "engine_invoked": consumer["engine_invoked"],
        }
    return {"runner": os_name, "index_sha256": digest(_archive_file(root, "index.json").read_bytes()),
            "source_sha256": index["source_sha256"],
            "rapidmeta_engine_sha256": engine_sha,
            "digest_receipts_verified": len(expected_files),
            "decisions": decisions, "numerical_controls": numerical_controls}


def compare(registration_path: Path, ubuntu_dir: Path, windows_dir: Path,
            expected_engine_sha256: str) -> dict:
    registration_raw = registration_path.read_bytes()
    registration = load_json(registration_path)
    assert_equal(registration.get("case_id"), CASE_ID, "registration case")
    assert_equal(registration.get("registered_status"), "NOT_RUN", "preregistered status")
    assert_equal(registration.get("input_type"), "SYNTHETIC_FIXTURE_ONLY", "input type")
    assert_equal(registration.get("runtime", {}).get("os"), list(OS_NAMES), "frozen OS matrix")
    if (not isinstance(expected_engine_sha256, str) or
            len(expected_engine_sha256) != 64 or
            any(ch not in "0123456789abcdef" for ch in expected_engine_sha256)):
        raise ValueError("missing immutable RapidMeta engine SHA256")
    a = check_archive(registration, digest(registration_raw), ubuntu_dir,
                      "ubuntu-24.04", expected_engine_sha256)
    b = check_archive(registration, digest(registration_raw), windows_dir,
                      "windows-2025", expected_engine_sha256)
    for field in ("source_sha256", "rapidmeta_engine_sha256", "decisions"):
        assert_equal(a[field], b[field], f"cross-OS {field}")
    # Both independent OS jobs must archive comparable outputs from the actual
    # pinned RapidMeta engine, not merely matching status/k/measure flags.
    # This checks reproducibility of a SYNTHETIC smoke calculation only:
    # it is NOT independent R-oracle or clinical statistical validation.
    smoke_controls = {}
    for label, expectation in registration["scenarios"].items():
        if expectation["consumer"] != "SYNTHETIC_ENGINE_EXECUTED":
            continue
        linux = a["numerical_controls"].get(label)
        windows = b["numerical_controls"].get(label)
        if not isinstance(linux, dict) or not isinstance(windows, dict):
            raise ValueError(f"missing cross-OS pinned synthetic engine smoke: {label}")
        for field in ("k_used", "measure"):
            assert_equal(linux[field], windows[field],
                         f"cross-OS pinned synthetic engine smoke {label}/{field}")
        for field in ("mu_log", "tau2"):
            if not math.isclose(linux[field], windows[field],
                                rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError(
                    f"cross-OS pinned synthetic engine smoke drift: {label}/{field}: "
                    f"{linux[field]!r} != {windows[field]!r}"
                )
        smoke_controls[label] = {"ubuntu-24.04": linux, "windows-2025": windows}
    if not smoke_controls:
        raise ValueError("no registered pinned synthetic engine smoke scenario")
    return {"record_version": "1.0.0", "case_id": CASE_ID,
            "evidence_scope": "FROZEN_SYNTHETIC_TWO_REPO_CROSS_OS_TRANSPORT_REFUSAL_PARITY_ONLY",
            "registration_sha256": digest(registration_raw), "overall": "PASS",
            "independently_checked_engine_sha256": expected_engine_sha256,
            "case_count": len(a["decisions"]),
            "refused_without_pooling": sum(not item["engine_invoked"] for item in a["decisions"].values()),
            "input_and_decision_parity": True,
            "numerical_output_cross_os_comparison": "PINNED_SYNTHETIC_SMOKE_ONLY_PASS",
            "numerical_smoke_tolerance": {"rel_tol": 1e-12, "abs_tol": 1e-12},
            "numerical_smoke_controls": smoke_controls,
            "real_R_oracle": "NOT_TESTED", "four_repository_suite": "NOT_RUN",
            "clinical_accuracy": "NOT_TESTED", "independent_human_adjudication": "NOT_TESTED",
            "archives": {a["runner"]: {k: a[k] for k in ("index_sha256", "digest_receipts_verified")},
                         b["runner"]: {k: b[k] for k in ("index_sha256", "digest_receipts_verified")}}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registration", required=True, type=Path)
    ap.add_argument("--ubuntu", required=True, type=Path)
    ap.add_argument("--windows", required=True, type=Path)
    ap.add_argument("--rapidmeta", required=True, type=Path,
                    help="separately checked-out exact frozen RapidMeta git repository")
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    registration = load_json(args.registration)
    engine_sha = pinned_engine_digest(registration, args.rapidmeta)
    report = compare(args.registration, args.ubuntu, args.windows, engine_sha)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"CROSS-EXCH-016 cross-OS archived parity PASS: {report['case_count']} registered cases, "
          f"{report['refused_without_pooling']} no-pool refusals, "
          f"{sum(a['digest_receipts_verified'] for a in report['archives'].values())} digest checks")


if __name__ == "__main__":
    main()
