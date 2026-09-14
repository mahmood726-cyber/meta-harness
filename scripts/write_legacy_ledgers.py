"""Write explicit LEGACY_UNRECORDED ledgers for pre-ledger committed caches."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import acquisition as acq  # noqa: E402


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _none_cap() -> dict:
    return {"kind": "none", "n": None, "remainder": None}


def _record_ids(records: dict) -> list[str]:
    out = []
    for record in records.get("records") or []:
        rid = record.get("id") if isinstance(record, dict) else None
        if rid is not None:
            out.append(str(rid))
    return out


def _pubmed_status(records: dict) -> str:
    # A pre-ledger cache may carry an aggregate pubmed status but never a per-query yield. RAN_OK is kept only when
    # the cache recorded it; otherwise the query was attempted (the fetch ran every committed query) with an
    # unrecorded outcome -- RAN_UNRECORDED, the legacy-only state. NOT_RUN would assert "not attempted", which is false.
    status = (records.get("source_status") or {}).get("pubmed")
    return "RAN_OK" if status == "RAN_OK" else "RAN_UNRECORDED"


def build_legacy_ledger(slug: str, config: dict, records: dict) -> dict:
    record_ids = _record_ids(records)
    queries = [str(q) for q in (config.get("pubmed_queries") or records.get("pubmed_queries") or [])]
    run_utc = records.get("fetched_utc") or ""
    ledger = acq.new_ledger(slug)

    for query in queries:
        kind = acq.classify_query(query)
        acq.add_source(
            ledger,
            kind,
            query,
            run_utc,
            _pubmed_status(records),
            None,
            {"hits": None, "fetched": 0, "retained": 0, "cap": _none_cap()},
            [],
            kind != "PUBMED_PMID_ENUMERATION",
        )

    legacy_id = acq.add_source(
        ledger,
        "LEGACY_UNRECORDED",
        " || ".join(queries),
        run_utc,
        "RAN_OK",
        None,
        {"hits": None, "fetched": len(record_ids), "retained": len(record_ids), "cap": _none_cap()},
        record_ids,
        False,
    )
    for rid in record_ids:
        ledger.setdefault("records", {})[rid] = {"found_by": [legacy_id]}
    ledger["snapshot"] = {
        "records_sha256": acq.records_sha256(records.get("records") or []),
        "retrieved_utc": run_utc,
        "mode": "LEGACY_UNRECORDED",
        "engine_sha": acq._engine_sha(),
        "raw_calls": 0,
    }
    return ledger


def candidate_slugs(root: Path = ROOT) -> list[str]:
    reviews = root / "docs" / "reviews"
    out = []
    for review_dir in sorted(p for p in reviews.iterdir() if p.is_dir()):
        slug = review_dir.name
        records_path = root / "cache" / slug / "records.json"
        ledger_path = root / "cache" / slug / acq.LEDGER_FILENAME
        if records_path.exists() and not ledger_path.exists():
            out.append(slug)
    return out


def _summaries(root: Path = ROOT) -> tuple[list[dict], list[str]]:
    rows = []
    errors = []
    for slug in candidate_slugs(root):
        records_path = root / "cache" / slug / "records.json"
        topic_path = root / "topics" / f"{slug}.json"
        if not topic_path.exists():
            errors.append(f"{slug}: missing {topic_path.relative_to(root)}")
            continue
        records = _load_json(records_path)
        config = _load_json(topic_path)
        ledger = build_legacy_ledger(slug, config, records)
        violations = acq.validate(ledger, records.get("records") or [])
        if violations:
            errors.append(f"{slug}: " + "; ".join(violations))
            continue
        rows.append({
            "slug": slug,
            "records": len(records.get("records") or []),
            "pubmed_queries": len(config.get("pubmed_queries") or records.get("pubmed_queries") or []),
            "fetched_utc": records.get("fetched_utc") or "",
            "ledger": ledger,
        })
    return rows, errors


def write_ledgers(rows: list[dict], root: Path = ROOT) -> None:
    for row in rows:
        out = root / "cache" / row["slug"] / acq.LEDGER_FILENAME
        with out.open("w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(row["ledger"], ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print the ledgers that would be written")
    args = parser.parse_args(argv)

    rows, errors = _summaries(ROOT)
    if errors:
        for err in errors:
            print(f"ERROR {err}")
        return 1

    verb = "would write" if args.dry_run else "wrote"
    if not args.dry_run:
        write_ledgers(rows, ROOT)
    print(f"{'DRY-RUN ' if args.dry_run else ''}LEGACY LEDGERS: {verb} {len(rows)} topics")
    total_records = 0
    for row in rows:
        total_records += row["records"]
        print(
            f"{row['slug']}\trecords={row['records']}\t"
            f"pubmed_queries={row['pubmed_queries']}\tfetched_utc={row['fetched_utc']}"
        )
    print(f"TOTAL topics={len(rows)} records={total_records}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
