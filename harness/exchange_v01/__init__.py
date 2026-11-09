"""Versioned fail-closed evidence transport boundary; no statistical calculations.

This validates proposed pooled evidence only. It is not an eligibility adjudicator,
PDF parser, independent verifier, or endorsement of upstream extraction accuracy.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

VERSION = "0.1.0"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
LINE_REF = re.compile(r"line ([1-9][0-9]{0,8})|lines ([1-9][0-9]{0,8})-([1-9][0-9]{0,8})")
MIN_REGISTERED_CASES = 14
ESTIMAND_KEYS = ("measure", "population", "outcome", "timepoint")
VALID_DECISIONS = {"ALLOW", "ALLOW_WITH_LABEL", "ADJUST", "MANUAL_REVIEW", "REFUSE"}
VALID_BENCHMARK_STATES = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}


def _source(root: Path, relative: object) -> bytes:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("source.path must be a relative POSIX file path")
    p = Path(relative)
    if p.is_absolute() or any(piece in {"..", "."} for piece in p.parts):
        raise ValueError("source.path traverses or escapes archive root")
    base = root.resolve(strict=True)
    target = (base / p).resolve(strict=True)
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError("source.path outside archive root or not a regular file")
    return target.read_bytes()


def _required_text(obj: dict, key: str) -> str:
    s = obj.get(key)
    if not isinstance(s, str) or not s.strip():
        raise ValueError(f"{key} missing or empty")
    return s


def _reject_unexpected_keys(obj: dict, allowed: set[str], where: str) -> None:
    """Enforce the versioned schema's closed provenance objects."""
    unexpected = set(obj) - allowed
    if unexpected:
        names = ", ".join(sorted(str(key) for key in unexpected))
        raise ValueError(f"{where}: unsupported field(s): {names}")


def _canonical_identifier(obj: dict, key: str) -> str:
    """Reject boundary aliases without silently changing provenance identities."""
    value = _required_text(obj, key)
    # ECMAScript whitespace includes BOM; Python strip covers C0/NEL whitespace.
    # The schema explicitly covers their union, as does this refusal check.
    if value != value.strip() or value.startswith("\ufeff") or value.endswith("\ufeff"):
        raise ValueError(f"{key} has noncanonical leading or trailing whitespace")
    return value


def _verify_text_locator(content: str, locator: str, passage: str) -> None:
    """Verify a quotation within its claimed 1-based UTF-8 text line range.

    PDF coordinates and scientific eligibility require separate verification.
    """
    match = LINE_REF.fullmatch(locator)
    if match is None:
        raise ValueError("source_span locator must be 'line N' or 'lines N-M' for UTF-8 text")
    start = int(match.group(1) or match.group(2))
    end = int(match.group(1) or match.group(3))
    lines = content.splitlines(keepends=True)
    if start > end or end > len(lines):
        raise ValueError("source_span locator outside source line range")
    if passage not in "".join(lines[start - 1:end]):
        raise ValueError("source_span passage absent at cited source lines")


def validate_exchange(payload: object, archive_root: Path) -> None:
    """Raise ValueError unless all proposed rows have source and compatible estimands.

    A successful return permits structural handoff only, not a scientific pool or
    independent source verification. Consumers must additionally enforce method gates.
    """
    if not isinstance(payload, dict) or payload.get("schema_version") != VERSION:
        raise ValueError("unsupported evidence schema_version")
    _reject_unexpected_keys(
        payload, {"schema_version", "review_id", "protocol_sha256", "rows", "proposed_pool"},
        "exchange",
    )
    _required_text(payload, "review_id")
    if not HEX64.fullmatch(str(payload.get("protocol_sha256", ""))):
        raise ValueError("protocol_sha256 must be a SHA-256 digest")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be non-empty")
    target = payload.get("proposed_pool")
    if not isinstance(target, dict) or target.get("requested") is not True:
        raise ValueError("this handoff only accepts explicit proposed pooling")
    _reject_unexpected_keys(target, {"requested", "estimand"}, "proposed_pool")
    declared = target.get("estimand")
    if not isinstance(declared, dict) or set(declared) != set(ESTIMAND_KEYS):
        raise ValueError("proposed_pool.estimand keys missing or unknown")
    if any(not isinstance(v, str) or not v.strip() for v in declared.values()):
        raise ValueError("proposed_pool.estimand has empty member")
    seen = set()
    seen_trials = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"row {i}: not an object")
        _reject_unexpected_keys(
            row, {"study_id", "trial_id", "decision", "estimand", "source", "source_span"},
            f"row {i}",
        )
        study = _canonical_identifier(row, "study_id")
        trial = _canonical_identifier(row, "trial_id")
        if study in seen:
            raise ValueError(f"duplicate study_id: {study}")
        if trial in seen_trials:
            # Distinct reports or subgroups from one trial cannot enter a naive pool
            # as independent studies. Require upstream deduplication/adjudication.
            raise ValueError(f"duplicate trial_id: {trial}; requires manual review before pooling")
        seen.add(study)
        seen_trials.add(trial)
        decision = row.get("decision")
        if decision not in VALID_DECISIONS:
            raise ValueError(f"row {i}: unknown decision")
        # Never treat a labelled or adjusted candidate as an unconditional ALLOW.
        # Another lane must supply a separate, independently reviewed promotion.
        if decision != "ALLOW":
            raise ValueError(f"row {i}: {decision} cannot be pooled at this boundary")
        if row.get("estimand") != declared:
            raise ValueError(f"row {i}: estimand mismatch (measure/population/outcome/timepoint)")
        source = row.get("source")
        if not isinstance(source, dict):
            raise ValueError(f"row {i}: source missing")
        _reject_unexpected_keys(source, {"path", "sha256"}, f"row {i}.source")
        sha = source.get("sha256")
        if not isinstance(sha, str) or not HEX64.fullmatch(sha):
            raise ValueError(f"row {i}: source.sha256 missing or invalid")
        try:
            content = _source(archive_root, source.get("path"))
        except (OSError, ValueError) as exc:
            raise ValueError(f"row {i}: inaccessible source: {exc}") from exc
        if hashlib.sha256(content).hexdigest() != sha:
            raise ValueError(f"row {i}: source SHA-256 mismatch")
        span = row.get("source_span")
        if not isinstance(span, dict):
            raise ValueError(f"row {i}: source_span missing")
        _reject_unexpected_keys(span, {"locator", "verbatim"}, f"row {i}.source_span")
        passage = _required_text(span, "verbatim")
        locator = _required_text(span, "locator")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"row {i}: source is not text; requires external PDF/text span checker") from exc
        _verify_text_locator(text, locator, passage)
    # This code does NOT call a meta-analysis engine or independently confirm eligibility.


def validate_manifest(payload: object, manifest_dir: Path) -> None:
    """Check closed provenance, complete case IDs, pins and status-bound evidence.

    This verifies local structure and fixture bytes, never remote run truth.
    """
    if not isinstance(payload, dict) or payload.get("benchmark_version") != VERSION:
        raise ValueError("unsupported benchmark_version")
    _reject_unexpected_keys(
        payload, {"benchmark_version", "purpose", "repositories", "cases", "coverage"},
        "benchmark manifest",
    )
    _required_text(payload, "purpose")
    pins = payload.get("repositories")
    expected = {"meta-harness", "rapidmeta-kit", "e156-ecosystem-starter", "e156"}
    if not isinstance(pins, dict) or set(pins) != expected:
        raise ValueError("exactly four repository pins required")
    for name, pin in pins.items():
        if not isinstance(pin, dict):
            raise ValueError(f"{name}: repository pin must be an object")
        _reject_unexpected_keys(
            pin, {"commit", "dependency_identity", "dependency_lock_git_blob"},
            f"{name} repository pin",
        )
        _required_text(pin, "dependency_identity")
        if not isinstance(pin.get("commit"), str) or not HEX40.fullmatch(pin["commit"]):
            raise ValueError(f"{name}: exact Git commit pin required")
        if "dependency_lock_git_blob" in pin and (
            not isinstance(pin["dependency_lock_git_blob"], str)
            or not HEX40.fullmatch(pin["dependency_lock_git_blob"])
        ):
            raise ValueError(f"{name}: invalid dependency_lock_git_blob")
        # The entire pinned commit includes its dependency files. Do not claim it
        # proves runtime installation or resolves mutable remote services.
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases missing")
    coverage = payload.get("coverage")
    expected_cov = {"CROSS-CANARY-001", "CROSS-R-001", "CROSS-DISCOVERY-001",
                    "CROSS-ADJUDICATION-001", "CROSS-USABILITY-001"}
    if not isinstance(coverage, list) or len(coverage) != len(expected_cov):
        raise ValueError("coverage matrix must account for every unexecuted discipline exactly once")
    for c in coverage:
        if not isinstance(c, dict):
            raise ValueError("coverage entry must be an object")
        _reject_unexpected_keys(c, {"id", "category", "status", "reason"}, "benchmark coverage")
        _required_text(c, "id")
        _required_text(c, "category")
        _required_text(c, "reason")
        if not isinstance(c.get("status"), str) or c["status"] not in {"NOT_RUN", "BLOCKED"}:
            raise ValueError(f"{c.get('id')}: coverage requires actual external evidence and v0.2 schema before PASS")
    if {c["id"] for c in coverage} != expected_cov:
        raise ValueError("coverage matrix must account for every unexecuted discipline exactly once")
    ids = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case must be object")
        _reject_unexpected_keys(
            case, {"id", "description", "input", "input_sha256", "input_type", "status", "run_evidence"},
            "benchmark case",
        )
        _required_text(case, "description")
        cid = _required_text(case, "id")
        if not re.fullmatch(r"CROSS-EXCH-(?!000\Z)[0-9]{3}", cid):
            raise ValueError(f"{cid}: unsupported CROSS-EXCH case namespace")
        if cid in ids:
            raise ValueError("duplicate case id")
        ids.add(cid)
        status = case.get("status")
        if not isinstance(status, str) or status not in VALID_BENCHMARK_STATES:
            raise ValueError(f"{cid}: unknown status")
        if case.get("input_type") != "SYNTHETIC_FIXTURE_ONLY":
            raise ValueError(f"{cid}: only synthetic test fixtures permitted in v0.1")
        if status in {"PASS", "FAIL"}:
            ev = case.get("run_evidence")
            if not isinstance(ev, dict) or not all(
                isinstance(ev.get(k), str) and ev[k].strip()
                for k in ("action_run_url", "commit_sha", "input_sha256", "job_name")
            ) or not HEX40.fullmatch(ev["commit_sha"]) or ev["input_sha256"] != case.get("input_sha256"):
                raise ValueError(f"{cid}: {status} without matching, complete run evidence")
            _reject_unexpected_keys(
                ev, {"action_run_url", "commit_sha", "input_sha256", "job_name"},
                f"{cid} run_evidence",
            )
            # A well-formed fictional URL can still pass: this is an offline
            # consistency check, not an assertion that an Actions job ran.
            run_path = re.fullmatch(
                r"https://github[.]com/mahmood726-cyber/([a-z0-9-]+)/actions/runs/([1-9][0-9]*)",
                ev["action_run_url"],
            )
            if run_path is None or run_path.group(1) not in pins:
                raise ValueError(f"{cid}: {status} workflow URL is not from a pinned repository")
            run_repo = run_path.group(1)
            if ev["commit_sha"] != pins[run_repo]["commit"]:
                raise ValueError(f"{cid}: {status} workflow commit is not the pinned {run_repo} commit")
        elif "run_evidence" in case:
            raise ValueError(f"{cid}: run_evidence requires PASS or FAIL status")
        h = case.get("input_sha256")
        if not isinstance(h, str) or not HEX64.fullmatch(h):
            raise ValueError(f"{cid}: missing input_sha256")
        try:
            data = _source(manifest_dir, case.get("input"))
        except (OSError, ValueError) as exc:
            raise ValueError(f"{cid}: inaccessible input: {exc}") from exc
        if hashlib.sha256(data).hexdigest() != h:
            raise ValueError(f"{cid}: benchmark input SHA-256 mismatch")
    # Preserve every registered case; future three-digit additions must have
    # no gaps. This checks registration, not successful benchmark execution.
    last = max(MIN_REGISTERED_CASES, max(int(cid.rsplit("-", 1)[1]) for cid in ids))
    expected_ids = {f"CROSS-EXCH-{i:03d}" for i in range(1, last + 1)}
    missing = sorted(expected_ids - ids)
    if missing:
        raise ValueError(f"benchmark case registry missing required IDs: {', '.join(missing[:8])}")


def main() -> int:
    """Compatibility entrypoint: raw JSON must never bypass strict wire checks."""
    from .wire import main as strict_main
    return strict_main()


if __name__ == "__main__":
    raise SystemExit(main())
