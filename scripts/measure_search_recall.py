"""Score an engine candidate set against the sealed search benchmark.

This script never runs a search engine. It reads a candidate-set artifact from
an engine run, refuses unpinned inputs, and scores against the MEASUREMENT
topics by default. DEVELOPMENT topics are printed only with
``--include-development`` and are labelled as fit statistics.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import gitblob, heldout  # noqa: E402
from scripts import measure_regression_corpus_recall as regression_recall  # noqa: E402


DEFAULT_BENCHMARK = Path("registry") / "search_benchmark.json"
DEFAULT_SPLIT = Path("registry") / "search_benchmark_split.json"
DEFAULT_FIXES = Path("registry") / "fixes.json"
SPLIT_FIX_ID = "TRANCHE-search-benchmark"

PMID_RE = re.compile(r"^(?:PMID[:\s]*)?(\d{1,9})$", re.I)
NCT_RE = re.compile(r"\b(NCT\d{8})\b", re.I)
DOI_RE = re.compile(r"\b(10\.\S+/\S+)\b", re.I)


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _norm_title(text: str | None) -> str:
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _pmid(value: Any) -> str | None:
    raw = str(value or "").strip()
    match = PMID_RE.match(raw)
    return match.group(1) if match else None


def _nct(value: Any) -> str | None:
    match = NCT_RE.search(str(value or ""))
    return match.group(1).upper() if match else None


def _doi(value: Any) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    match = DOI_RE.search(raw)
    if not match:
        return None
    return match.group(1).rstrip(".,;").lower()


def _positive_key(row: dict[str, Any]) -> tuple[str, str]:
    pmid = _pmid(row.get("pmid"))
    if pmid:
        return "pmid", pmid
    nct = _nct(row.get("nct"))
    if nct:
        return "nct", nct
    doi = _doi(row.get("doi"))
    if doi:
        return "doi", doi
    return "title", _norm_title(row.get("trial"))


def _candidate_keys(item: Any) -> tuple[list[tuple[str, str]], str, str]:
    route = "unrouted"
    label = ""
    keys: list[tuple[str, str]] = []
    if isinstance(item, dict):
        route = str(item.get("route") or item.get("found_by") or item.get("source") or "unrouted")
        label = str(item.get("trial") or item.get("title") or item.get("name") or item.get("id") or "")
        for field in ("pmid", "id"):
            pmid = _pmid(item.get(field))
            if pmid:
                keys.append(("pmid", pmid))
        for field in ("nct", "id"):
            nct = _nct(item.get(field))
            if nct:
                keys.append(("nct", nct))
        for field in ("doi", "id"):
            doi = _doi(item.get(field))
            if doi:
                keys.append(("doi", doi))
        title = _norm_title(item.get("trial") or item.get("title") or item.get("name"))
        if title:
            keys.append(("title", title))
    else:
        label = str(item)
        pmid = _pmid(label)
        if pmid:
            keys.append(("pmid", pmid))
        nct = _nct(label)
        if nct:
            keys.append(("nct", nct))
        doi = _doi(label)
        if doi:
            keys.append(("doi", doi))
        title = _norm_title(label)
        if title and not keys:
            keys.append(("title", title))

    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for key in keys:
        if key[1] and key not in seen:
            seen.add(key)
            deduped.append(key)
    return deduped, route, label


def _candidate_map(items: list[Any]) -> tuple[dict[tuple[str, str], list[dict[str, str]]], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, str]]] = {}
    parsed: list[dict[str, Any]] = []
    for item in items:
        keys, route, label = _candidate_keys(item)
        parsed.append({"keys": keys, "route": route, "label": label})
        for key in keys:
            index.setdefault(key, []).append({"route": route, "label": label})
    return index, parsed


def _candidate_payload(data: dict[str, Any]) -> tuple[str | None, dict[str, list[Any]]]:
    engine_sha = data.get("engine_sha")
    raw = data.get("candidates")
    if raw is None:
        raw = {
            key: value
            for key, value in data.items()
            if key not in {"engine_sha", "generated_utc", "metadata", "_doc"}
        }
    if not isinstance(raw, dict):
        raise ValueError("candidate file must contain a candidates object or slug keys")
    candidates: dict[str, list[Any]] = {}
    for slug, items in raw.items():
        if isinstance(items, list):
            candidates[str(slug)] = items
        else:
            raise ValueError(f"{slug}: candidate set must be a list")
    return str(engine_sha) if engine_sha else None, candidates


def _split_refusal(split_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not split_path.is_file():
        return None, f"split file missing: {_posix(split_path)}"
    try:
        split = _load_json(split_path)
    except Exception as exc:  # noqa: BLE001
        return None, f"split file unreadable: {exc}"
    for key in ("sealed_utc", "commit", "rule", "assignments", "fixstate"):
        if key not in split:
            return split, f"split file unsealed: missing {key}"
    fix = split.get("fixstate") or {}
    if fix.get("fix_id") != SPLIT_FIX_ID:
        return split, f"split file unsealed: fixstate.fix_id must be {SPLIT_FIX_ID}"
    fixes_path = ROOT / DEFAULT_FIXES
    try:
        fixes = _load_json(fixes_path)
    except Exception as exc:  # noqa: BLE001
        return split, f"fixstate registry unreadable: {exc}"
    entry = next((e for e in fixes.get("entries", []) if e.get("fix_id") == SPLIT_FIX_ID), None)
    if not isinstance(entry, dict):
        return split, f"split file unsealed: {SPLIT_FIX_ID} missing from registry/fixes.json"
    rel = _posix(split_path.relative_to(ROOT) if split_path.is_absolute() else split_path)
    recorded = ((entry.get("seal") or {}).get("dependencies") or {}).get(rel)
    observed = gitblob.blob_sha(ROOT, rel)
    if not recorded or observed != recorded:
        return split, f"split file unsealed: fixstate seal mismatch for {rel}"
    return split, None


def _format_positive(row: dict[str, Any]) -> str:
    kind, value = _positive_key(row)
    suffix = f"{kind}:{value}" if value else "title:<blank>"
    note = row.get("note")
    return f"{row.get('trial')} [{suffix}]" + (f" - {note}" if note else "")


def _score_topic(slug: str, positives: list[dict[str, Any]], candidates: list[Any]) -> dict[str, Any]:
    cindex, parsed_candidates = _candidate_map(candidates)
    found = []
    missed = []
    benchmark_keys = set()
    for row in positives:
        key = _positive_key(row)
        benchmark_keys.add(key)
        hits = cindex.get(key) or []
        if hits:
            found.append({"positive": row, "match_key": f"{key[0]}:{key[1]}", "routes": sorted({h["route"] for h in hits})})
        else:
            missed.append(row)
    reverse = []
    for item in parsed_candidates:
        if not item["keys"]:
            reverse.append(item)
            continue
        if not any(key in benchmark_keys for key in item["keys"]):
            reverse.append(item)
    return {
        "slug": slug,
        "N": len(positives),
        "found": found,
        "missed": missed,
        "reverse": reverse,
    }


def _print_section(title: str, rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    print(title)
    total_n = total_found = total_reverse = 0
    for row in rows:
        total_n += row["N"]
        total_found += len(row["found"])
        total_reverse += len(row["reverse"])
        print(
            f"{row['slug']}: N={row['N']} found={len(row['found'])} "
            f"missed={len(row['missed'])} reverse_not_in_benchmark={len(row['reverse'])}"
        )
        if row["found"]:
            print("  found:")
            for hit in row["found"]:
                print(f"    - {_format_positive(hit['positive'])} via {', '.join(hit['routes'])}; match_key={hit['match_key']}")
        if row["missed"]:
            print("  missed:")
            for miss in row["missed"]:
                print(f"    - {_format_positive(miss)}")
        if row["reverse"]:
            print("  reverse candidates not in benchmark (not an eligibility judgement):")
            for item in row["reverse"]:
                keys = ", ".join(f"{k}:{v}" for k, v in item["keys"]) or "<no key>"
                print(f"    - {item['label']} via {item['route']} [{keys}]")
    print(f"TOTAL: found {total_found} of {total_n}; reverse_not_in_benchmark={total_reverse}")
    return total_found, total_n, total_reverse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_file")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--split-file", default=str(DEFAULT_SPLIT))
    parser.add_argument("--include-development", action="store_true")
    args = parser.parse_args(argv)

    candidate_path = Path(args.candidate_file)
    benchmark_path = Path(args.benchmark)
    split_path = Path(args.split_file)
    if not benchmark_path.is_absolute():
        benchmark_path = ROOT / benchmark_path
    if not split_path.is_absolute():
        split_path = ROOT / split_path

    split, refusal = _split_refusal(split_path)
    if refusal:
        print(f"SEARCH-RECALL: REFUSED - {refusal}")
        return 2
    assert split is not None

    try:
        engine_sha, candidates = _candidate_payload(_load_json(candidate_path))
    except Exception as exc:  # noqa: BLE001
        print(f"SEARCH-RECALL: REFUSED - candidate file unreadable: {exc}")
        return 2
    if not engine_sha:
        print("SEARCH-RECALL: REFUSED - candidate file missing engine_sha")
        return 2

    dev_topics = {
        slug for slug, row in (split.get("assignments") or {}).items()
        if row.get("set") == "DEVELOPMENT"
    }
    passed_dev = sorted(set(candidates) & dev_topics)
    if passed_dev and not args.include_development:
        print(
            "SEARCH-RECALL: REFUSED - DEVELOPMENT topic(s) passed without "
            f"--include-development: {', '.join(passed_dev)}"
        )
        return 2

    benchmark = _load_json(benchmark_path)
    topics = benchmark.get("topics") or {}
    assignments = split.get("assignments") or {}
    measurement_slugs = [
        slug for slug in sorted(topics)
        if (assignments.get(slug) or {}).get("set") == "MEASUREMENT"
    ]
    development_slugs = [
        slug for slug in sorted(topics)
        if (assignments.get(slug) or {}).get("set") == "DEVELOPMENT"
    ]

    print("SEARCH-RECALL BENCHMARK")
    print(f"engine_sha: {engine_sha}")
    print(f"benchmark: {_posix(benchmark_path.relative_to(ROOT))}")
    print(f"split: {_posix(split_path.relative_to(ROOT))} sealed_utc={split.get('sealed_utc')}")
    print(regression_recall.describe_measurement_target())
    registry = heldout.load(ROOT)
    ok, detail = heldout.measurement_current(ROOT, registry)
    print(f"existing sealed/regression guard: {'PASS' if ok else 'REFUSED'} - {detail}")
    print("")

    measurement_rows = [
        _score_topic(slug, topics[slug].get("positives") or [], candidates.get(slug, []))
        for slug in measurement_slugs
    ]
    _print_section("MEASUREMENT TOPICS", measurement_rows)
    if args.include_development:
        print("")
        dev_rows = [
            _score_topic(slug, topics[slug].get("positives") or [], candidates.get(slug, []))
            for slug in development_slugs
        ]
        _print_section("DEVELOPMENT TOPICS - fit statistic, not capability", dev_rows)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
