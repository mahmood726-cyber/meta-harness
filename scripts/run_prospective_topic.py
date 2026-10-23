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
from harness import prospective_discovery  # noqa: E402
from harness import prospective_raw_integrity  # noqa: E402
from harness.census import build_review_dir, verify as census_verify  # noqa: E402
from harness.registration import protocol_sha as registered_protocol_sha  # noqa: E402
from harness.synth import method_text  # noqa: E402


FROZEN_OUT_DIRS = ("docs", "cache", "topics", "protocols", "harness", "registry")


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


def _cache_candidates(out_dir: Path, slug: str) -> list[Path]:
    return [
        out_dir / "cache" / slug / "records.json",
        out_dir / "records.json",
    ]


def _load_or_refresh(config: dict[str, Any], out_dir: Path, now_day: str) -> tuple[dict[str, Any], Path | None, bool]:
    """Require a new live, raw-archived retrieval for each prospective run.

    The ordinary harness can legitimately replay caches. A prospective run cannot:
    accepting pre-seeded records here previously bypassed acquisition altogether and
    still let the resulting review be counted as COMPLETED.
    """
    slug = str(config["slug"])
    for records_path in _cache_candidates(out_dir, slug):
        if records_path.exists():
            raise prospective.ProspectiveRefusal(
                "prospective validation refuses pre-existing records: "
                f"{records_path}; start a fresh run directory (legacy replay is not validation)"
            )

    snapshot_dir = Path(acquisition.refresh(config, now_day, root=str(out_dir))).resolve()
    if not _inside(snapshot_dir, out_dir):
        raise prospective.ProspectiveRefusal("acquisition refresh escaped out_dir")

    ledger_path = snapshot_dir / acquisition.LEDGER_FILENAME
    if not ledger_path.is_file():
        raise prospective.ProspectiveRefusal("fresh retrieval is missing its retrieval ledger")
    ledger = _read_json(ledger_path)
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("mode") != "REFRESH":
        raise prospective.ProspectiveRefusal("prospective retrieval must carry a REFRESH snapshot")

    raw_calls = snapshot.get("raw_calls")
    if type(raw_calls) is not int or raw_calls < 1:
        raise prospective.ProspectiveRefusal(
            "prospective retrieval has no archived raw HTTP calls; completeness is unverified"
        )
    raw_index = snapshot_dir / "raw" / "INDEX.json"
    if not raw_index.is_file():
        raise prospective.ProspectiveRefusal("prospective retrieval has no raw/INDEX.json")
    index_bytes = raw_index.read_bytes()
    if hashlib.sha256(index_bytes).hexdigest() != snapshot.get("raw_index_sha256"):
        raise prospective.ProspectiveRefusal("prospective raw index SHA256 differs from ledger")
    try:
        rows = json.loads(index_bytes)
    except (ValueError, UnicodeDecodeError) as exc:
        raise prospective.ProspectiveRefusal("prospective raw index is not valid JSON") from exc
    if not isinstance(rows, list) or len(rows) != raw_calls:
        raise prospective.ProspectiveRefusal("prospective raw index count differs from ledger")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise prospective.ProspectiveRefusal("prospective raw index contains an invalid path")
        body_file = (snapshot_dir / row["path"]).resolve()
        if not _inside(body_file, snapshot_dir / "raw") or not body_file.is_file():
            raise prospective.ProspectiveRefusal("prospective raw response missing or outside snapshot")
        raw_bytes = body_file.read_bytes()
        if hashlib.sha256(raw_bytes).hexdigest() != row.get("file_sha256"):
            raise prospective.ProspectiveRefusal("prospective raw response SHA256 differs from index")
        try:
            prospective_raw_integrity.verify_raw_record(row, raw_bytes)
        except ValueError as exc:
            raise prospective.ProspectiveRefusal(
                "prospective raw response has inconsistent archived body: " + str(exc)
            ) from exc

    # A hashed API call can be a seeded PMID lookup, not a prospective study search.
    # Refuse title/identifier-only discovery, failed concept searches and capped results.
    discovery_failures = prospective_discovery.concept_discovery_failures(ledger, rows)
    if discovery_failures:
        raise prospective.ProspectiveRefusal(
            "prospective concept discovery refused: " + "; ".join(discovery_failures)
        )

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
    out_dir.mkdir(parents=True, exist_ok=True)

    started_utc = _utc_now()
    t0 = time.perf_counter()
    topic_identifier = topic_config_path
    artefacts: list[Path] = []
    error_detail: dict[str, Any] | None = None
    outcome = "COMPLETED"

    try:
        config_path = Path(topic_config_path)
        config = _read_json(config_path)
        topic_identifier = str(config.get("topic_identifier") or config.get("slug") or topic_config_path)
        if "slug" not in config:
            raise prospective.ProspectiveRefusal("topic config must provide slug")
        artefacts.append(_copy_file(config_path, out_dir / "topic-config.json"))
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
