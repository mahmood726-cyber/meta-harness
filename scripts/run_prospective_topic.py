"""Externally triggered prospective topic runner.

Usage:
  python scripts/run_prospective_topic.py <batch_id> <topic-config.json> <out_dir>

The command checks the batch declaration before creating output, builds one
topic package, writes a run record inside the package, and exits non-zero when
the recorded outcome is not COMPLETED.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import acquisition  # noqa: E402
from harness import pipeline as pipeline_mod  # noqa: E402
from harness import prospective  # noqa: E402
from harness.prospective_checks.discovery import concept_discovery_failures  # noqa: E402
from harness.prospective_checks.raw_integrity import verify_raw_record  # noqa: E402
from harness.census import build_review_dir, verify as census_verify  # noqa: E402
from harness.registration import protocol_sha as registered_protocol_sha  # noqa: E402
from harness.synth import method_text  # noqa: E402


FROZEN_OUT_DIRS = ("docs", "cache", "topics", "protocols", "harness", "registry")
SAFE_TOPIC_SLUG_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
WINDOWS_DEVICE_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _require_topic_slug(value: Any) -> str:
    """Reject unsafe identities before acquisition can join root/cache/slug."""
    if (
        type(value) is not str
        or SAFE_TOPIC_SLUG_RE.fullmatch(value) is None
        or ".." in value
        or value.split(".", 1)[0].upper() in WINDOWS_DEVICE_NAMES
    ):
        raise prospective.ProspectiveRefusal(
            "prospective topic slug must be a single safe ASCII path component"
        )
    return value


def _utc_now() -> str:
    return (
        dt.datetime.now(dt.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _refuse_frozen_out_dir(out_dir: Path) -> None:
    for rel in FROZEN_OUT_DIRS:
        if _inside(out_dir, ROOT / rel):
            raise prospective.ProspectiveRefusal(
                f"out_dir may not be inside frozen path {rel}/"
            )


def _rel_to_out(out_dir: Path, path: Path) -> str:
    return path.resolve().relative_to(out_dir.resolve()).as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    data = prospective._parse_strict_prospective_json(
        path.read_text(encoding="utf-8"), str(path)
    )
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _claim_fresh_out_dir(out_dir: Path) -> None:
    """Atomically reserve a new package, including refusal of empty directories."""
    try:
        out_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise prospective.ProspectiveRefusal(
            f"out_dir already exists; use a new, run-specific package path: {out_dir}"
        ) from exc


def _cache_candidates(out_dir: Path, slug: str) -> list[Path]:
    return [
        out_dir / "cache" / slug / "records.json",
        out_dir / "records.json",
    ]


def _safe_archive_file(path: Path, snapshot_dir: Path) -> bool:
    """Require a local regular file, refusing symlinked archive ancestors too."""
    try:
        relative = path.relative_to(snapshot_dir)
        cursor = snapshot_dir
        if cursor.is_symlink():
            return False
        for part in relative.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                return False
        return path.is_file() and _inside(path, snapshot_dir)
    except (OSError, ValueError, RuntimeError):
        return False


def _verify_prospective_raw_archive(
    snapshot_dir: Path, ledger: dict[str, Any] | None,
    *, raw_rows: list[dict[str, Any]] | None = None,
) -> list[Path]:
    """Verify recorded HTTP custody and optionally return the same decoded rows.

    This binds index, envelope, body and metadata before discovery/synthesis.
    It cannot establish that all external requests were recorded.
    """
    if not isinstance(ledger, dict):
        raise prospective.ProspectiveRefusal("prospective raw archive has no retrieval ledger")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("mode") != "REFRESH":
        raise prospective.ProspectiveRefusal("prospective retrieval must carry a REFRESH snapshot")

    raw_calls = snapshot.get("raw_calls")
    if type(raw_calls) is not int or raw_calls < 1:
        raise prospective.ProspectiveRefusal(
            "prospective retrieval has no archived raw HTTP calls; completeness is unverified"
        )
    raw_index = snapshot_dir / "raw" / "INDEX.json"
    if not _safe_archive_file(raw_index, snapshot_dir):
        raise prospective.ProspectiveRefusal("prospective retrieval has no raw/INDEX.json")
    expected_index = snapshot.get("raw_index_sha256")
    if type(expected_index) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_index) is None:
        raise prospective.ProspectiveRefusal("prospective raw archive lacks a valid index SHA256")
    index_bytes = raw_index.read_bytes()
    if hashlib.sha256(index_bytes).hexdigest() != expected_index:
        raise prospective.ProspectiveRefusal("prospective raw index SHA256 differs from ledger")
    try:
        rows = prospective._parse_strict_prospective_json(
            index_bytes.decode("utf-8"), "prospective raw index"
        )
    except (ValueError, UnicodeDecodeError) as exc:
        raise prospective.ProspectiveRefusal(f"prospective raw index is not valid JSON: {exc}") from exc
    if not isinstance(rows, list) or len(rows) != raw_calls:
        raise prospective.ProspectiveRefusal("prospective raw index count differs from ledger")
    verified = [raw_index]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise prospective.ProspectiveRefusal("prospective raw index contains an invalid path")
        rel = row["path"]
        parts = rel.split("/")
        if (
            len(parts) != 3 or parts[0] != "raw" or not rel.endswith(".json")
            or any(part in {"", ".", ".."} for part in parts)
            or "\\" in rel or ":" in rel or rel in seen
        ):
            raise prospective.ProspectiveRefusal(
                "prospective raw response missing or outside snapshot: unsafe/duplicate body path"
            )
        seen.add(rel)
        body_file = snapshot_dir.joinpath(*parts)
        if not _safe_archive_file(body_file, snapshot_dir):
            raise prospective.ProspectiveRefusal("prospective raw response missing or outside snapshot")
        file_sha = row.get("file_sha256")
        if type(file_sha) is not str or re.fullmatch(r"[0-9a-f]{64}", file_sha) is None:
            raise prospective.ProspectiveRefusal("prospective raw archive missing file SHA256")
        body_bytes = body_file.read_bytes()
        if hashlib.sha256(body_bytes).hexdigest() != file_sha:
            raise prospective.ProspectiveRefusal("prospective raw response SHA256 differs from index")
        try:
            verify_raw_record(row, body_bytes)
        except ValueError as exc:
            raise prospective.ProspectiveRefusal(f"prospective raw response integrity: {exc}") from exc
        verified.append(body_file)
    if raw_rows is not None:
        raw_rows.extend(rows)
    return verified


def _load_or_refresh(
    config: dict[str, Any], out_dir: Path, now_day: str,
    *, artefacts: list[Path] | None = None,
) -> tuple[dict[str, Any], Path | None, bool]:
    """Require live discovery and retain its archive even when verification fails.

    The optional inventory is populated as evidence arrives, so a refusal cannot
    discard the snapshot reference before run_topic records the failed attempt.
    """
    slug = _require_topic_slug(config.get("slug"))
    for records_path in _cache_candidates(out_dir, slug):
        if records_path.exists() or records_path.is_symlink():
            raise prospective.ProspectiveRefusal(
                "prospective validation refuses pre-existing records: "
                f"{records_path}; start a fresh run directory (legacy replay is not validation)"
            )

    snapshot_dir = Path(acquisition.refresh(config, now_day, root=str(out_dir))).resolve()
    if not _inside(snapshot_dir, out_dir):
        raise prospective.ProspectiveRefusal("acquisition refresh escaped out_dir")
    if artefacts is not None:
        artefacts.append(snapshot_dir)
    ledger_path = snapshot_dir / acquisition.LEDGER_FILENAME
    if not _safe_archive_file(ledger_path, snapshot_dir):
        raise prospective.ProspectiveRefusal("fresh retrieval is missing its retrieval ledger")
    if artefacts is not None:
        artefacts.append(ledger_path)
    ledger = _read_json(ledger_path)
    rows: list[dict[str, Any]] = []
    raw_artefacts = _verify_prospective_raw_archive(snapshot_dir, ledger, raw_rows=rows)
    if artefacts is not None:
        artefacts.extend(raw_artefacts)
    failures = concept_discovery_failures(ledger, rows)
    if failures:
        raise prospective.ProspectiveRefusal(
            "prospective concept discovery failed: " + "; ".join(failures)
        )
    records_path = snapshot_dir / "records.json"
    if not _safe_archive_file(records_path, snapshot_dir):
        raise prospective.ProspectiveRefusal("prospective records missing or outside snapshot")
    if artefacts is not None:
        artefacts.append(records_path)

    return _read_json(records_path), snapshot_dir, False


def _ledger_from(cache_dir: Path | None) -> dict[str, Any] | None:
    if cache_dir is None:
        return None
    path = cache_dir / acquisition.LEDGER_FILENAME
    if not path.is_file():
        return None
    return _read_json(path)


def _write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _package_review(
    config: dict[str, Any],
    records: dict[str, Any],
    out_dir: Path,
    now_utc: str,
    from_cache: bool,
    ledger: dict[str, Any] | None,
) -> list[Path]:
    slug = str(config["slug"])
    proto_sha = config.get("protocol_sha") or registered_protocol_sha(slug)
    if not proto_sha:
        raise prospective.ProspectiveRefusal(
            f"no registered protocol SHA for topic {slug!r}"
        )

    old_loader = pipeline_mod._load_retrieval_ledger
    if ledger is not None:
        pipeline_mod._load_retrieval_ledger = (
            lambda requested_slug: ledger if requested_slug == slug else old_loader(requested_slug)
        )
    try:
        core = pipeline_mod.build_review_core(slug, config, records, proto_sha)
    finally:
        pipeline_mod._load_retrieval_ledger = old_loader

    primary = [outcome for outcome in core["outcomes"] if outcome.get("primary")][0]
    declared_method = core.get("method_declared")
    served_scale = (primary.get("result") or {}).get("scale")
    served_method = method_text(served_scale) if served_scale else declared_method
    manifest_meta = {
        "slug": slug,
        "declared_method": declared_method,
        "served_method": served_method,
        "generator": "harness-prospective",
        "build_utc": now_utc,
        "comparator": {
            key: core["comparator"][key]
            for key in ("name", "year", "journal", "pmid", "doi", "url", "open_access", "overlap")
        },
    }
    review_dir = out_dir / "review"
    build_review_dir(core, manifest_meta, str(review_dir), proto_sha, from_cache=from_cache)
    comp_core = pipeline_mod.build_comparator_core(slug, config, records)
    return [
        _write_json(out_dir / "review_core.json", core),
        _write_json(out_dir / "comparator_core.json", comp_core),
        review_dir / "index.html",
        review_dir / "review.json",
        review_dir / "manifest.json",
        review_dir / "REPRODUCTION.json",
    ]


def _invariant_failures(invariants: list[str], review_dir: Path) -> list[str]:
    failures: list[str] = []
    for invariant in invariants:
        label = str(invariant).lower()
        if label in {"census", "review_census", "reproduction_census"}:
            result = census_verify(str(review_dir))
            if result.get("failures"):
                failures.append(f"{invariant}: {result}")
            continue
        if label in {"gate", "publication_gate"}:
            from harness.gate import gate_page

            ok, reasons = gate_page(str(review_dir))
            if not ok:
                failures.append(f"{invariant}: {'; '.join(reasons)}")
            continue
        failures.append(f"{invariant}: unknown invariant")
    return failures


def run_topic(
    batch_id: str,
    topic_config_path: str,
    out_dir_path: str,
    *,
    rerun_of: str | None = None,
    rerun_justification: str | None = None,
) -> dict[str, Any]:
    decl = prospective.load_declaration(ROOT, batch_id)
    prospective.check_declaration_frozen(ROOT, decl)

    out_dir = Path(out_dir_path).absolute()
    _refuse_frozen_out_dir(out_dir)
    _claim_fresh_out_dir(out_dir)
    out_dir = out_dir.resolve()

    started_utc = _utc_now()
    t0 = time.perf_counter()
    topic_identifier = topic_config_path
    artefacts: list[Path] = []
    error_detail: dict[str, Any] | None = None
    outcome = "COMPLETED"

    try:
        config_path = Path(topic_config_path)
        config_bytes = config_path.read_bytes()
        archived_config = out_dir / "topic-config.json"
        archived_config.write_bytes(config_bytes)
        artefacts.append(archived_config)
        config = prospective._parse_strict_prospective_json(
            config_bytes.decode("utf-8"), "held-out topic configuration"
        )
        if not isinstance(config, dict):
            raise ValueError(f"{config_path} must contain a JSON object")
        topic_identifier = str(config.get("topic_identifier") or config.get("slug") or topic_config_path)
        _require_topic_slug(config.get("slug"))
        records, cache_dir, from_cache = _load_or_refresh(
            config, out_dir, started_utc[:10], artefacts=artefacts
        )
        if cache_dir is not None:
            records_path = cache_dir / "records.json"
            if records_path.is_file() and not _inside(records_path, out_dir):
                raise prospective.ProspectiveRefusal("records cache escaped out_dir")
        package_records = out_dir / "records.json"
        if not package_records.exists():
            artefacts.append(_write_json(package_records, records))
        else:
            artefacts.append(package_records)
        ledger = _ledger_from(cache_dir)
        if ledger is not None:
            artefacts.append(_write_json(out_dir / acquisition.LEDGER_FILENAME, ledger))
        artefacts.extend(
            _package_review(
                config,
                records,
                out_dir,
                started_utc,
                from_cache=from_cache,
                ledger=ledger,
            )
        )
        invariant_failures = _invariant_failures(
            list(decl.get("invariants") or []), out_dir / "review"
        )
        elapsed = time.perf_counter() - t0
        if elapsed > float(decl["time_limit_s"]):
            outcome = "FAILED_TIMEOUT"
        elif invariant_failures:
            outcome = "FAILED_INVARIANT"
            error_detail = {"invariant_failures": invariant_failures}
    except TimeoutError as exc:
        outcome = "FAILED_TIMEOUT"
        error_detail = {"error": str(exc)}
    except prospective.ProspectiveRefusal as exc:
        outcome = "FAILED_INVARIANT"
        error_detail = {"type": type(exc).__name__, "message": str(exc)}
    except Exception as exc:  # noqa: BLE001 - failures must be retained as run records.
        outcome = "FAILED_CRASH"
        error_detail = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

    if error_detail is not None:
        artefacts.append(_write_json(out_dir / "failure.json", error_detail))

    finished_utc = _utc_now()
    record = prospective.run_record(
        ROOT,
        batch_id,
        topic_identifier,
        started_utc,
        finished_utc,
        outcome,
        [_rel_to_out(out_dir, path) for path in artefacts if _inside(path, out_dir)],
        rerun_of=rerun_of,
        rerun_justification=rerun_justification,
    )
    record_path = prospective.write_run_record(out_dir / "run_record.json", record)
    return {
        "package": str(out_dir),
        "run_record": str(record_path),
        "outcome": outcome,
        "run_id": record["run_id"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_id")
    parser.add_argument("topic_config_json")
    parser.add_argument("out_dir")
    parser.add_argument("--rerun-of", default=None)
    parser.add_argument("--rerun-justification", default=None)
    args = parser.parse_args(argv)
    try:
        result = run_topic(
            args.batch_id,
            args.topic_config_json,
            args.out_dir,
            rerun_of=args.rerun_of,
            rerun_justification=args.rerun_justification,
        )
    except prospective.ProspectiveRefusal as exc:
        print(f"PROSPECTIVE RUN REFUSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["outcome"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
