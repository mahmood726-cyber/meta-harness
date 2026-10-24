"""Versioned fail-closed evidence transport boundary; no statistical calculations.

This validates proposed pooled evidence only. It is not an eligibility adjudicator,
PDF parser, independent verifier, or endorsement of upstream extraction accuracy.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

VERSION = "0.1.0"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
# Text-only handoff: only concrete 1-based line locators can be checked here.
LINE_REF = re.compile(r"line ([1-9][0-9]{0,8})\Z|lines ([1-9][0-9]{0,8})-([1-9][0-9]{0,8})\Z")
ESTIMAND_KEYS = ("measure", "population", "outcome", "timepoint")
VALID_DECISIONS = {"ALLOW", "ALLOW_WITH_LABEL", "ADJUST", "MANUAL_REVIEW", "REFUSE"}
VALID_BENCHMARK_STATES = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}



def _unique_json_members(pairs: list[tuple[str, object]]) -> dict:
    """Reject repeated keys before JSON parsing discards the earlier value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object member: {key}")
        result[key] = value
    return result


def validate_exchange_json(raw: str | bytes, archive_root: Path) -> None:
    """Validate wire JSON without Python's last-key-wins ambiguity.

    Raw-input consumers must call this function, not json.loads followed by
    validate_exchange: a decoded dict cannot reveal duplicate JSON keys.
    This remains a structural transport check, not clinical validation.
    """
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("exchange JSON must be UTF-8") from exc
    if not isinstance(raw, str) or raw.startswith("\ufeff"):
        raise ValueError("exchange JSON must be UTF-8 without a BOM")
    try:
        payload = json.loads(raw, object_pairs_hook=_unique_json_members)
    except json.JSONDecodeError as exc:
        raise ValueError("malformed exchange JSON") from exc
    validate_exchange(payload, archive_root)



def validate_manifest_json(raw: str | bytes, manifest_dir: Path) -> None:
    """Validate the benchmark manifest at the raw JSON boundary.

    Duplicate keys can otherwise shadow NOT_RUN/FAIL statuses, repository pins
    or input hashes before validate_manifest sees the decoded dictionary.
    This checks *syntax and structure*, not whether an Actions run occurred.
    """
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("benchmark manifest JSON must be UTF-8") from exc
    if not isinstance(raw, str) or raw.startswith("\ufeff"):
        raise ValueError("benchmark manifest JSON must be UTF-8 without a BOM")
    try:
        payload = json.loads(raw, object_pairs_hook=_unique_json_members)
    except json.JSONDecodeError as exc:
        raise ValueError("malformed benchmark manifest JSON") from exc
    validate_manifest(payload, manifest_dir)


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
    """Keep the Python importer aligned with JSON Schema additionalProperties=false.

    Unknown fields cannot carry unversioned gate, provenance or estimand
    overrides into a downstream consumer with different interpretation.
    """
    unexpected = set(obj) - allowed
    if unexpected:
        names = ", ".join(sorted(str(key) for key in unexpected))
        raise ValueError(f"{where}: unsupported field(s): {names}")


def _canonical_identifier(obj: dict, key: str) -> str:
    """Require already-trimmed IDs; reject aliases before deduplication.

    Normalizing silently would change incoming provenance identifiers. This
    transport only rejects outer whitespace; it does not resolve real-world
    registry aliases, case variants, or distinct reports of one trial.
    """
    value = _required_text(obj, key)
    # Python str.strip() and ECMAScript JSON Schema whitespace classes differ
    # on U+FEFF; reject the BOM explicitly for schema/runtime consistency.
    if value != value.strip() or value.startswith("\ufeff") or value.endswith("\ufeff"):
        raise ValueError(f"{key} has noncanonical leading or trailing whitespace")
    return value


def _verify_text_locator(content: str, locator: str, passage: str) -> None:
    """Check that the archived verbatim passage occurs at the *claimed* lines.

    This verifier cannot validate PDF page numbers, table cells, or scientific
    eligibility. Those require a separate source-aware checker.
    """
    m = LINE_REF.fullmatch(locator)
    if m is None:
        raise ValueError("source_span locator must be 'line N' or 'lines N-M' for UTF-8 text")
    start = int(m.group(1) or m.group(2))
    end = int(m.group(1) or m.group(3))
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
        seen.add(study)
        # v0.1 permits one pooled row per declared trial. Multiple reports and
        # multi-arm comparisons require explicit study-level reconciliation; a
        # different study_id must not bypass the unit-of-analysis guard.
        if trial in seen_trials:
            raise ValueError(f"duplicate trial_id: {trial} (requires reconciliation before pooling)")
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
        _required_text(span, "locator")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"row {i}: source is not text; requires external PDF/text span checker") from exc
        _verify_text_locator(text, span["locator"], passage)
    # This code does NOT call a meta-analysis engine or independently confirm eligibility.


def validate_manifest(payload: object, manifest_dir: Path) -> None:
    """Fail closed on missing Git pins, fixture hash drift and unsupported PASS claims."""
    if not isinstance(payload, dict) or payload.get("benchmark_version") != VERSION:
        raise ValueError("unsupported benchmark_version")
    # Match the published JSON Schema's closed manifest shape. Otherwise a
    # second consumer can assign meaning to extra gate/provenance fields.
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
        if not re.fullmatch(r"[0-9a-f]{40}", str(pin.get("commit", ""))):
            raise ValueError(f"{name}: exact Git commit pin required")
        if "dependency_lock_git_blob" in pin and not re.fullmatch(
            r"[0-9a-f]{40}", str(pin["dependency_lock_git_blob"])
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
    if {c.get("id") for c in coverage} != expected_cov:
        raise ValueError("coverage matrix must account for every unexecuted discipline exactly once")
    for c in coverage:
        _reject_unexpected_keys(
            c, {"id", "category", "status", "reason"}, "benchmark coverage",
        )
        _required_text(c, "category")
        _required_text(c, "reason")
        if c.get("status") not in {"NOT_RUN", "BLOCKED"}:
            raise ValueError(f"{c.get('id')}: coverage requires actual external evidence and v0.2 schema before PASS")
    ids = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case must be object")
        _reject_unexpected_keys(
            case,
            {"id", "description", "input", "input_sha256", "input_type",
             "status", "run_evidence"},
            "benchmark case",
        )
        _required_text(case, "description")
        cid = _required_text(case, "id")
        if not re.fullmatch(r"CROSS-EXCH-(?!000$)[0-9]{3}", cid):
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
            ) or not re.fullmatch(r"[0-9a-f]{40}", ev["commit_sha"]) or ev["input_sha256"] != case.get("input_sha256"):
                raise ValueError(f"{cid}: {status} without matching, complete run evidence")
            _reject_unexpected_keys(
                ev, {"action_run_url", "commit_sha", "input_sha256", "job_name"},
                f"{cid} run_evidence",
            )
            # A plausible workflow URL and SHA are not enough: provenance must
            # identify one of the four pinned source snapshots. This check is
            # offline/structural only; it never claims the remote job was run.
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
    # An editable manifest must not silently omit established negative gates.
    # v0.1 requires CROSS-EXCH-001 through -015; later IDs are allowed only
    # without gaps. This checks registry completeness, NOT that tests ran.
    last = max(15, max(int(cid.rsplit("-", 1)[1]) for cid in ids))
    expected_ids = {f"CROSS-EXCH-{i:03d}" for i in range(1, last + 1)}
    missing = sorted(expected_ids - ids)
    if missing:
        raise ValueError(
            f"benchmark case registry missing required IDs: {', '.join(missing[:8])}"
        )


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Check versioned benchmark manifest (no science claimed)")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    validate_manifest_json(args.manifest.read_bytes(), args.manifest.parent)
    print("MANIFEST VERIFIED: pins and fixture SHA-256; cases retain their stated statuses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
