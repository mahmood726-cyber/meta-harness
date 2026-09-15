"""Regression-corpus (sealed register) recall measured ON search_v2 -- compare within kind.

WHY. docs/search_recall_regression_corpus.json is measured by scripts/measure_regression_corpus_recall.py with the
LEGACY engine (acquisition.concept_query -> PubMed esearch, full pagination). The first search_v2 measurement bundle
quoted that 18 of 20 beside search_v2 numbers; a comparison across two engines is not a comparison. This script
scores the SAME five register topics and the SAME known-eligible denominator (known_eligible() imported from the
legacy script, so the denominator cannot drift between the two artefacts) against a search_v2 snapshot generation:

  (a) WITHIN KIND: PMIDs retrieved by search_v2's PUBMED_CONCEPT_QUERY source alone -- the direct analogue of the
      legacy number (one PubMed boolean concept query, full pagination, Cochrane RCT filter);
  (b) WHOLE ENGINE: PMIDs present in the snapshot by any route (concept queries on three sources, NCT identity links,
      citation chasing, comparator reference list).

Per topic the source state is reported; a topic whose snapshot is absent or whose PubMed concept source is not
RAN_OK/RAN_ZERO has recall None for (a) and says so (never 0). No network: reads committed snapshots only.

OUTPUT docs/search_recall_regression_corpus_search_v2.json (appended history; engine_sha = blob of harness/search_v2.py
of the snapshot's recorded engine, and the CURRENT blob beside it so a stale measurement is visible).

Usage: python scripts/measure_regression_corpus_recall_search_v2.py --snapshot 2026-09-15r2-search_v2
"""
from __future__ import annotations
import argparse
import datetime
import io
import json
import os
import subprocess
import sys

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts.measure_regression_corpus_recall import known_eligible, TOPICS, VALIDATION_STATUS  # noqa: E402

OUT = os.path.join(ROOT, "docs", "search_recall_regression_corpus_search_v2.json")


def _engine_sha_now() -> str:
    return subprocess.check_output(["git", "-C", ROOT, "hash-object", os.path.join("harness", "search_v2.py")], text=True).strip()


def _pmid_of(rec: dict) -> str | None:
    for key in ("pmid", "id"):
        s = str(rec.get(key) or "").strip()
        if s.isdigit():
            return s
    return None


def measure(slug: str, snapshot: str) -> dict:
    snap_dir = os.path.join(ROOT, "cache", slug, "snapshots", snapshot)
    ke = known_eligible(slug)
    denom = ke["pooled_primary"] + ke["eligible_declared_absent"]
    row = {"slug": slug, "snapshot": f"cache/{slug}/snapshots/{snapshot}", "known_eligible": ke, "denominator": len(denom)}
    rec_path = os.path.join(snap_dir, "records.json")
    led_path = os.path.join(snap_dir, "retrieval_ledger.json")
    if not (os.path.exists(rec_path) and os.path.exists(led_path)):
        row.update({"state": "NOT_RUN", "error": "no search_v2 snapshot of this generation for the topic",
                    "concept": {"recall": None, "recalled": 0, "state": "NOT_RUN"},
                    "engine": {"recall": None, "recalled": 0, "state": "NOT_RUN"}})
        return row
    records = json.load(open(rec_path, encoding="utf-8"))
    ledger = json.load(open(led_path, encoding="utf-8"))
    row["snapshot_engine_sha"] = (ledger.get("snapshot") or {}).get("engine_sha")
    recs = records.get("records") or []
    by_id = {str(r.get("id")): r for r in recs}
    all_pmids = {p for r in recs if (p := _pmid_of(r))}
    concept_src = [s for s in ledger.get("sources") or [] if s.get("kind") == "PUBMED_CONCEPT_QUERY"]
    concept_state = concept_src[0].get("state") if concept_src else "NOT_RUN"
    concept_pmids = set()
    for s in concept_src:
        for rid in s.get("record_ids") or []:
            r = by_id.get(str(rid)) or {}
            p = _pmid_of(r) or (str(rid) if str(rid).isdigit() else None)
            if p:
                concept_pmids.add(p)
    src_states = {}
    for s in ledger.get("sources") or []:
        src_states[s.get("state")] = src_states.get(s.get("state"), 0) + 1

    def _score(got: set[str], state: str) -> dict:
        hit = [p for p in denom if p in got]
        miss = [p for p in denom if p not in got]
        ok = state in ("RAN_OK", "RAN_ZERO")
        return {"state": state, "fetched": len(got), "recalled": len(hit) if ok else 0,
                "recalled_pmids": hit if ok else [], "missed_pmids": miss if ok else denom,
                "recall": (round(len(hit) / len(denom), 3) if (ok and denom) else None)}

    engine_state = "RAN_OK_WITH_SOURCE_ERRORS" if src_states.get("RAN_ERROR") else "RAN_OK"
    row.update({
        "state": engine_state,
        "source_states": src_states,
        "concept": _score(concept_pmids, concept_state),
        "engine": _score(all_pmids, "RAN_OK"),  # whole-engine membership is well defined whenever the snapshot exists
        "engine_note": ("whole-engine recall counts a PMID present by ANY route; RAN_OK_WITH_SOURCE_ERRORS means some routes "
                        "did not run (named in source_states) so this is a lower bound on the engine, not on the corpus"),
    })
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True, help="snapshot generation name, e.g. 2026-09-15r2-search_v2")
    args = ap.parse_args(argv)
    reg = json.load(open(TOPICS, encoding="utf-8"))
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")
    rows = [measure(s, args.snapshot) for s in reg["slugs"]]
    engine_shas = sorted({r.get("snapshot_engine_sha") for r in rows if r.get("snapshot_engine_sha")})

    def _summ(key: str) -> dict:
        scored = [r for r in rows if r[key]["recall"] is not None]
        n_den = sum(r["denominator"] for r in scored)
        n_hit = sum(r[key]["recalled"] for r in scored)
        return {"topics": len(rows), "topics_scored": len(scored),
                "topics_not_scored": [r["slug"] for r in rows if r[key]["recall"] is None],
                "trials_known_eligible": n_den, "trials_recalled": n_hit,
                "recall": (round(n_hit / n_den, 3) if n_den else None),
                "recall_text": f"{n_hit} of {n_den}" if n_den else "not measurable"}

    summary = {"measured_utc": now, "snapshot": args.snapshot, "snapshot_engine_shas": engine_shas,
               "engine_sha_now": _engine_sha_now(),
               "within_kind_pubmed_concept_query": _summ("concept"), "whole_engine_any_route": _summ("engine")}
    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
        except (OSError, ValueError):
            prev = {}
    history = list(prev.get("history") or [])
    history.append(summary)
    out = {"_doc": ("REGRESSION-CORPUS recall measured ON search_v2, same five register topics and the same known-eligible "
                    "denominator as docs/search_recall_regression_corpus.json (legacy engine). within_kind = search_v2's "
                    "PubMed concept-query source alone (the legacy analogue); whole_engine = any route. Published whatever it "
                    "is. Not prospective validation."),
           "validation_status": VALIDATION_STATUS, "summary": summary, "per_topic": rows, "history": history}
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    wk = summary["within_kind_pubmed_concept_query"]
    we = summary["whole_engine_any_route"]
    print(f"REGRESSION-CORPUS RECALL ON search_v2 ({args.snapshot}, engine {','.join(s[:12] for s in engine_shas) or 'none'}, {now})")
    print(f"  within kind (PubMed concept query alone): {wk['recall_text']} over {wk['topics_scored']} of {wk['topics']} topics; not scored: {wk['topics_not_scored']}")
    print(f"  whole engine (any route):                 {we['recall_text']} over {we['topics_scored']} of {we['topics']} topics; not scored: {we['topics_not_scored']}")
    for r in rows:
        c, e = r["concept"], r["engine"]
        print(f"  {r['slug']:42s} topic={r['state']:26s} concept[{c['state']}] {c['recalled']}/{r['denominator']} missed={c['missed_pmids']}  engine {e['recalled']}/{r['denominator']} missed={e['missed_pmids']}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
