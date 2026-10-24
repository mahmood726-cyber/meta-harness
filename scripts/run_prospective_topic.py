"""Externally triggered prospective topic runner.

Usage:
  python scripts/run_prospective_topic.py <batch_id> <topic-config.json> <out_dir>

The command checks the batch declaration before creating output, builds one
topic package, writes a run record inside the package, and exits non-zero when
the recorded outcome is not COMPLETED.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import datetime as dt
import io
import json
import os
import re
import shutil
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
from harness.census import build_review_dir, verify as census_verify  # noqa: E402
from harness.registration import protocol_sha as registered_protocol_sha  # noqa: E402
from harness.synth import method_text  # noqa: E402


FROZEN_OUT_DIRS = ("docs", "cache", "topics", "protocols", "harness", "registry")

# acquisition.write_snapshot joins root/cache/<slug> before the caller checks
# whether the resulting path escaped the run package. Held-out topic inputs
# must never influence that filesystem path with traversal or device aliases.
SAFE_TOPIC_SLUG_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
WINDOWS_DEVICE_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _require_topic_slug(value: Any) -> str:
    """Validate a prospective identity before ANY acquisition side effect."""
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


def _refuse_duplicate_topic_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse ambiguous raw held-out JSON at every object nesting level.

    Python's default JSON decoder silently keeps the last repeated member,
    which can switch a released slug, protocol or eligibility field without
    changing the visibly archived raw input. The original bytes are archived
    before this hook runs, including the refused malformed configuration.
    """
    seen: dict[str, Any] = {}
    for name, value in pairs:
        if name in seen:
            raise prospective.ProspectiveRefusal(
                f"duplicate JSON member in held-out topic configuration: {name!r}"
            )
        seen[name] = value
    return seen


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
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _copy_file(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return dst


def _claim_fresh_out_dir(out_dir: Path) -> None:
    """Atomically reserve a fresh package path; never overwrite earlier run evidence.

    Reusing even an empty directory is refused: another runner may already have
    reserved it. mkdir(exist_ok=False) makes the final-directory claim atomic.
    """
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



def _verify_prospective_raw_archive(
    snapshot_dir: Path, ledger: dict[str, Any] | None
) -> list[Path]:
    """Require byte-verifiable, locally preserved HTTP evidence before synthesis.

    acquisition.validate checks existence of raw/INDEX.json, not its digest or
    the referenced bodies. This gate is specific to prospective runs: an
    archive with zero recorded calls cannot substantiate live retrieval.
    It verifies *recorded* calls, not whether every external request was logged.
    """
    if not isinstance(ledger, dict):
        raise prospective.ProspectiveRefusal("prospective raw archive has no retrieval ledger")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("mode") != "REFRESH":
        raise prospective.ProspectiveRefusal("prospective raw archive requires REFRESH mode")
    raw_calls = snapshot.get("raw_calls")
    if type(raw_calls) is not int or raw_calls < 1:
        raise prospective.ProspectiveRefusal("prospective raw archive has no recorded API calls")
    expected_index = snapshot.get("raw_index_sha256")
    if type(expected_index) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_index) is None:
        raise prospective.ProspectiveRefusal("prospective raw archive lacks a valid index SHA256")

    index_path = snapshot_dir / "raw" / "INDEX.json"
    if index_path.is_symlink() or not index_path.is_file() or not _inside(index_path, snapshot_dir):
        raise prospective.ProspectiveRefusal("prospective raw archive index is missing or unsafe")
    index_bytes = index_path.read_bytes()
    if hashlib.sha256(index_bytes).hexdigest() != expected_index:
        raise prospective.ProspectiveRefusal("prospective raw archive index SHA256 mismatch")

    def unique_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise prospective.ProspectiveRefusal(
                    f"prospective raw archive duplicate JSON member: {key!r}"
                )
            obj[key] = value
        return obj

    try:
        entries = json.loads(index_bytes, object_pairs_hook=unique_members)
    except (ValueError, UnicodeError) as exc:
        raise prospective.ProspectiveRefusal("prospective raw archive index invalid JSON") from exc
    if not isinstance(entries, list) or len(entries) != raw_calls:
        raise prospective.ProspectiveRefusal("prospective raw archive call count mismatch")

    verified = [index_path]
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise prospective.ProspectiveRefusal("prospective raw archive entry is not an object")
        rel = entry.get("path")
        if (
            type(rel) is not str
            or len(rel.split("/")) != 3
            or rel.split("/")[0] != "raw"
            or any(part in {"", ".", ".."} for part in rel.split("/"))
            or not rel.endswith(".json")
            or rel in seen
        ):
            raise prospective.ProspectiveRefusal("prospective raw archive has unsafe/duplicate body path")
        seen.add(rel)
        body_path = snapshot_dir.joinpath(*rel.split("/"))
        if body_path.is_symlink() or not body_path.is_file() or not _inside(body_path, snapshot_dir):
            raise prospective.ProspectiveRefusal("prospective raw archive body missing or unsafe")
        body_file_sha = entry.get("file_sha256")
        if type(body_file_sha) is not str or re.fullmatch(r"[0-9a-f]{64}", body_file_sha) is None:
            raise prospective.ProspectiveRefusal("prospective raw archive missing file SHA256")
        body_file_bytes = body_path.read_bytes()
        if hashlib.sha256(body_file_bytes).hexdigest() != body_file_sha:
            raise prospective.ProspectiveRefusal("prospective raw archive file SHA256 mismatch")
        try:
            payload = json.loads(body_file_bytes, object_pairs_hook=unique_members)
            if not isinstance(payload, dict) or type(payload.get("body_bytes_b64")) is not str:
                raise ValueError("missing raw body")
            raw_body = base64.b64decode(payload["body_bytes_b64"], validate=True)
        except (ValueError, UnicodeError, binascii.Error) as exc:
            raise prospective.ProspectiveRefusal("prospective raw archive body invalid") from exc
        actual_body_sha = hashlib.sha256(raw_body).hexdigest()
        if (
            actual_body_sha != entry.get("body_sha256")
            or actual_body_sha != payload.get("body_sha256")
        ):
            raise prospective.ProspectiveRefusal("prospective raw archive body SHA256 mismatch")
        for key in (
            "source_id", "url", "params", "status", "fetched_utc",
            "adapter", "adapter_blob_sha",
        ):
            if key not in entry or key not in payload or entry[key] != payload[key]:
                raise prospective.ProspectiveRefusal(
                    f"prospective raw archive provenance mismatch: {key}"
                )
        verified.append(body_path)
    return verified

def _load_or_refresh(config: dict[str, Any], out_dir: Path, now_day: str) -> tuple[dict[str, Any], Path | None, bool]:
    slug = _require_topic_slug(config.get("slug"))
    # A prospective run must not silently replay preseeded/cached records.
    # Such inputs can encode known trials, study selections or past outputs.
    # Refuse even a dangling symlink rather than accepting an ambiguous cache.
    for records_path in _cache_candidates(out_dir, slug):
        if records_path.exists() or records_path.is_symlink():
            raise prospective.ProspectiveRefusal(
                f"prospective run refuses pre-existing cached records: {records_path}"
            )

    snapshot_dir = Path(acquisition.refresh(config, now_day, root=str(out_dir))).resolve()
    if not _inside(snapshot_dir, out_dir):
        raise prospective.ProspectiveRefusal("acquisition refresh escaped out_dir")
    return _read_json(snapshot_dir / "records.json"), snapshot_dir, False


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

    out_dir = Path(out_dir_path).resolve()
    _refuse_frozen_out_dir(out_dir)
    _claim_fresh_out_dir(out_dir)

    started_utc = _utc_now()
    t0 = time.perf_counter()
    topic_identifier = topic_config_path
    artefacts: list[Path] = []
    error_detail: dict[str, Any] | None = None
    outcome = "COMPLETED"

    try:
        config_path = Path(topic_config_path)
        # Capture the externally supplied topic exactly once. Parsing the first
        # read and then copying the path a second time permits an intervening
        # edit to make the archived config differ from the config actually run.
        # Archive even malformed input so failures retain their original bytes.
        config_bytes = config_path.read_bytes()
        archived_config = out_dir / "topic-config.json"
        archived_config.write_bytes(config_bytes)
        artefacts.append(archived_config)
        config = json.loads(
            config_bytes.decode("utf-8"), object_pairs_hook=_refuse_duplicate_topic_members
        )
        if not isinstance(config, dict):
            raise ValueError(f"{config_path} must contain a JSON object")
        topic_identifier = str(config.get("topic_identifier") or config.get("slug") or topic_config_path)
        _require_topic_slug(config.get("slug"))
        records, cache_dir, from_cache = _load_or_refresh(
            config, out_dir, started_utc[:10]
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
        if cache_dir is None:
            raise prospective.ProspectiveRefusal("prospective retrieval snapshot is missing")
        artefacts.extend(_verify_prospective_raw_archive(cache_dir, ledger))
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
