"""Seal each topic's search vocabulary at a named commit -- the registration behind the search_v2 guard exemption.

WHY (2026-09-15, docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md). search_v2 refuses any query that looks
name-seeded (a capitalised token with a hyphen or digit, or all-caps >= 4). Drug codes, targets, procedures and
syndromes in the registered topic vocabulary trip the same heuristic (CABG, BAY94-8862, PCSK9, LCZ696, NSTE-ACS:
5 of 21 MEASUREMENT topics RAN_ERROR). The exemption is by PROVENANCE, not by lexical judgement: a token is exempt
only if it is covered by a vocabulary term that was registered BEFORE the engine existed. This script records what
"before" means -- the sha256 of the canonical JSON of exactly the vocabulary fields the builder reads, taken from
`git show <commit>:topics/<slug>.json`, never from the working tree. harness/search_v2.sealed_vocabulary refuses
the exemption for any slug whose working-tree vocabulary hashes differently, and tests/test_search_v2_guard.py
refuses the suite. Re-sealing is therefore an explicit, named commit.

BENCHMARK-ACRONYM COLLISION CHECK lives HERE, not in the engine: harness/ query builders must never open the
benchmark (tests/test_search_benchmark_isolation.py). At seal time every vocabulary term is compared (lower-cased,
whole term) with the registered acronym of every benchmark positive that can be resolved -- the CT.gov `acronym`
field of a cached record sharing the positive's NCT or PMID, or an acronym-shaped `trial` name. A collision is
recorded in the seal row and harness/search_v2 then grants that slug NO exemption. Coverage is reported n of N;
positives with no resolvable acronym are NOT covered by this check and the seal says so.

Usage: python scripts/seal_search_vocabulary.py --at <commit> [--out registry/search_vocabulary_seal.json]
       python scripts/seal_search_vocabulary.py --check      (working tree vs seal; exit 1 on any drift)
"""
from __future__ import annotations
import argparse
import datetime
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import search_v2  # noqa: E402

SPLIT = os.path.join(ROOT, "registry", "search_benchmark_split.json")
BENCHMARK = os.path.join(ROOT, "registry", "search_benchmark.json")
OUT = os.path.join(ROOT, "registry", "search_vocabulary_seal.json")


def _git_show(commit: str, relpath: str) -> str:
    return subprocess.check_output(["git", "-C", ROOT, "show", f"{commit}:{relpath}"], text=True, encoding="utf-8")


def _blob(commit: str, relpath: str) -> str:
    return subprocess.check_output(["git", "-C", ROOT, "rev-parse", f"{commit}:{relpath}"], text=True).strip()


def _acronym_shaped(name) -> bool:
    text = str(name or "").strip()
    return 0 < len(text) <= 20 and text.upper() == text and " " not in text and not any(c.isdigit() for c in text)


def _cached_records() -> list[str]:
    paths = []
    cache_root = os.path.join(ROOT, "cache")
    if not os.path.isdir(cache_root):
        return paths
    for slug in sorted(os.listdir(cache_root)):
        direct = os.path.join(cache_root, slug, "records.json")
        if os.path.exists(direct):
            paths.append(direct)
        snaps = os.path.join(cache_root, slug, "snapshots")
        if os.path.isdir(snaps):
            for name in sorted(os.listdir(snaps)):
                rp = os.path.join(snaps, name, "records.json")
                if name.endswith("-" + search_v2.SNAPSHOT_SUFFIX) and os.path.exists(rp):
                    paths.append(rp)
    return paths


def benchmark_acronyms(benchmark_path: str = BENCHMARK, record_paths: list[str] | None = None) -> dict:
    """Registered acronyms of benchmark positives -> {acronym_lower: [slug:trial, ...]}, with coverage n of N."""
    by_nct: dict[str, str] = {}
    by_pmid: dict[str, str] = {}
    for path in (record_paths if record_paths is not None else _cached_records()):
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for rec in (payload.get("records") if isinstance(payload, dict) else payload) or []:
            acronym = str(rec.get("acronym") or "").strip()
            if not acronym:
                continue
            nct = str(rec.get("nct") or "").strip().upper()
            if nct:
                by_nct.setdefault(nct, acronym)
            pmid = str(rec.get("pmid") or rec.get("id") or "").strip()
            if pmid.isdigit():
                by_pmid.setdefault(pmid, acronym)
    topics = (json.load(open(benchmark_path, encoding="utf-8")).get("topics") or {}) if os.path.exists(benchmark_path) else {}
    resolved: dict[str, list[str]] = {}
    total = unresolved = 0
    for slug, topic in topics.items():
        for pos in topic.get("positives") or []:
            total += 1
            acronym = None
            nct = str(pos.get("nct") or "").strip().upper()
            if nct:
                acronym = by_nct.get(nct)
            if not acronym and pos.get("pmid"):
                acronym = by_pmid.get(str(pos["pmid"]))
            if not acronym and _acronym_shaped(pos.get("trial")):
                acronym = str(pos["trial"]).strip()
            if acronym:
                resolved.setdefault(acronym.lower(), []).append(f"{slug}:{pos.get('trial')}")
            else:
                unresolved += 1
    return {"acronyms": resolved, "positives": total, "resolved": total - unresolved, "unresolved": unresolved,
            "coverage_text": f"{total - unresolved} of {total} benchmark positives have a resolvable registered acronym"}


def collision_row(cfg: dict, bench: dict) -> dict:
    hits = []
    for term in search_v2.registered_vocabulary(cfg):
        owners = bench["acronyms"].get(str(term).strip().lower())
        if owners:
            hits.append({"term": term, "benchmark_positive": owners[0]})
    return {"coverage_text": bench["coverage_text"], "resolved": bench["resolved"], "positives": bench["positives"],
            "collisions": hits}


def seal(commit: str, out: str) -> dict:
    split = json.load(open(SPLIT, encoding="utf-8"))
    full = subprocess.check_output(["git", "-C", ROOT, "rev-parse", commit], text=True).strip()
    bench = benchmark_acronyms()
    rows = {}
    for slug, assignment in sorted((split.get("assignments") or {}).items()):
        rel = f"topics/{slug}.json"
        cfg = json.loads(_git_show(full, rel))
        rows[slug] = {
            "split": assignment.get("set"),
            "config_blob_at_seal": _blob(full, rel),
            "vocabulary_sha256": search_v2.vocabulary_sha(cfg),
            "terms_n": len(search_v2.registered_vocabulary(cfg)),
            "benchmark_acronym_collision": collision_row(cfg, bench),
        }
    payload = {
        "schema_version": 2,
        "_doc": ("Sealed search vocabulary per topic: sha256(canonical_json(vocabulary_fields(config))) read from the "
                 "named commit, not the working tree. harness/search_v2 grants the acronym-heuristic exemption only to "
                 "a slug whose working-tree vocabulary hashes to this value AND whose benchmark_acronym_collision list is "
                 "empty; drift withdraws the exemption and fails tests/test_search_v2_guard.py. Re-seal with "
                 "scripts/seal_search_vocabulary.py --at <commit> in its own commit. Protocol: "
                 "docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md"),
        "vocabulary_fields": list(search_v2.VOCABULARY_FIELDS) + ["include." + k for k in search_v2.VOCABULARY_INCLUDE_FIELDS],
        "sealed_from_commit": full,
        "sealed_utc": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "benchmark_acronym_registry": {"coverage_text": bench["coverage_text"], "resolved": bench["resolved"],
                                       "positives": bench["positives"], "acronyms": sorted(bench["acronyms"])},
        "slugs": rows,
    }
    io.open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    return payload


def check() -> int:
    payload = json.load(open(OUT, encoding="utf-8"))
    drift = []
    collisions = []
    for slug, row in sorted((payload.get("slugs") or {}).items()):
        path = os.path.join(ROOT, "topics", slug + ".json")
        if not os.path.exists(path):
            drift.append(f"{slug}: topic config missing")
            continue
        cfg = json.load(open(path, encoding="utf-8"))
        working = search_v2.vocabulary_sha(cfg)
        if working != row.get("vocabulary_sha256"):
            drift.append(f"{slug}: working {working[:12]} != seal {str(row.get('vocabulary_sha256'))[:12]}")
        if (row.get("benchmark_acronym_collision") or {}).get("collisions"):
            collisions.append(f"{slug}: {row['benchmark_acronym_collision']['collisions']}")
    n = len(payload.get("slugs") or {})
    reg = payload.get("benchmark_acronym_registry") or {}
    print(f"collision registry: {reg.get('coverage_text', 'absent')}")
    if drift or collisions:
        print(f"SEAL DRIFT {len(drift)} of {n}; COLLISIONS {len(collisions)} of {n}:")
        for line in drift + collisions:
            print("  " + line)
        return 1
    print(f"SEAL OK: {n} of {n} sealed vocabularies match the working tree, 0 of {n} collide (sealed from {payload.get('sealed_from_commit')})")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", help="commit to seal from")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    if not args.at:
        ap.error("--at <commit> or --check")
    payload = seal(args.at, args.out)
    print(f"sealed {len(payload['slugs'])} slugs from {payload['sealed_from_commit']} -> {args.out}; "
          f"{payload['benchmark_acronym_registry']['coverage_text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
