"""Regression-corpus search recall -- not prospective validation.

WHY. The previous number (6 of 6, docs/search_recall.json) was measured on six trials hard-coded into the engine's
TARGETS table and already pooled before the engine was written; the next commit found the engine retrieved 0/64,
2/80, 6/80, 6/71 of held records on other topics. A recall measured on the development set is a fit statistic, not
a recall. An external auditor later disqualified all 32 current topics from prospective validation because they have
been exposed through audits, URLs, commit history, or regression work. This script therefore measures only a named
adversarial regression corpus in registry/regression_recall_topics.json; prospective validation uses topics held
outside the repository.

WHAT IS MEASURED (network; PubMed esearch, full pagination, no cap):
  for each regression-corpus topic: query = acquisition.concept_query(topic config) -- the engine as committed
  known-eligible set  = PMIDs of the pooled PRIMARY-outcome trials
                      + PMIDs of eligible-declared-absent trials on the primary outcome (eligible, not extractable)
                        (registry-only ids without a PMID are listed but cannot score)
  recall = |known-eligible PMIDs retrieved by the query| / |known-eligible PMIDs|
  and, per topic, the boolean hit count and the source state (a RAN_ERROR topic scores nothing and says so).

OUTPUT docs/search_recall_regression_corpus.json (appended history; engine_sha = git blob sha of
harness/acquisition.py at measurement). harness/heldout.measurement_current refuses the standard if the engine
changes without a re-measure, so every engine change publishes its regression-corpus number -- including a worse one.

Usage: python scripts/measure_regression_corpus_recall.py  (writes the artefact; prints the table)
"""
from __future__ import annotations
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
from harness import acquisition  # noqa: E402

TOPICS = os.path.join(ROOT, "registry", "regression_recall_topics.json")
OUT = os.path.join(ROOT, "docs", "search_recall_regression_corpus.json")
VALIDATION_STATUS = ("REGRESSION_CORPUS — not prospective validation: all 32 corpus topics are disqualified as "
                     "held-out (exposed through audits, URLs, commit history); measured on the 5 corpus topics "
                     "that had zero contact with engine tuning")


def _engine_sha() -> str:
    return subprocess.check_output(["git", "-C", ROOT, "hash-object", os.path.join("harness", "acquisition.py")],
                                   text=True).strip()


def _pmid(x) -> str | None:
    s = str(x or "").strip()
    if s.upper().startswith("PMID"):
        s = s[4:].strip(" :")
    return s if s.isdigit() else None


def known_eligible(slug: str) -> dict:
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None) or {}
    pooled, absent, unscorable = [], [], []
    for t in prim.get("trials") or []:
        p = _pmid(t.get("id"))
        (pooled if p else unscorable).append(p or str(t.get("id")))
    for t in prim.get("declared_absent_trials") or []:
        p = _pmid(t.get("id"))
        (absent if p else unscorable).append(p or str(t.get("id")))
    return {"pooled_primary": pooled, "eligible_declared_absent": absent, "unscorable_no_pmid": unscorable}


def measure(slug: str) -> dict:
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    q = acquisition.concept_query(cfg)
    res = acquisition.esearch_all(q, hard_cap=None)
    ke = known_eligible(slug)
    denom = ke["pooled_primary"] + ke["eligible_declared_absent"]
    got = set(res.get("ids") or [])
    hit = [p for p in denom if p in got]
    miss = [p for p in denom if p not in got]
    row = {"slug": slug, "query": q, "state": res.get("state"), "error": res.get("error"),
           "hits_in_boolean_set": res.get("count"), "fetched": len(got),
           "known_eligible": ke, "denominator": len(denom), "recalled": len(hit),
           "recalled_pmids": hit, "missed_pmids": miss,
           "recall": (round(len(hit) / len(denom), 3) if denom else None)}
    if res.get("state") != "RAN_OK" and res.get("state") != "RAN_ZERO":
        row["recall"] = None  # a failed search has no recall; it must not read as 0
    return row


def main() -> int:
    reg = json.load(open(TOPICS, encoding="utf-8"))
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")
    sha = _engine_sha()
    rows = [measure(s) for s in reg["slugs"]]
    scored = [r for r in rows if r["recall"] is not None]
    n_den = sum(r["denominator"] for r in scored)
    n_hit = sum(r["recalled"] for r in scored)
    summary = {"measured_utc": now, "engine_sha": sha, "topics": len(rows), "topics_scored": len(scored),
               "topics_not_scored": [r["slug"] for r in rows if r["recall"] is None],
               "trials_known_eligible": n_den, "trials_recalled": n_hit,
               "recall": (round(n_hit / n_den, 3) if n_den else None),
               "recall_text": f"{n_hit} of {n_den}" if n_den else "not measurable"}
    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
        except (OSError, ValueError):
            prev = {}
    history = list(prev.get("history") or [])
    history.append(summary)
    out = {"_doc": ("REGRESSION-CORPUS concept-query recall: measured on the named regression topics in "
                    "registry/regression_recall_topics.json, against each topic's pinned known-eligible set "
                    "(pooled primary trials + eligible-declared-absent trials with PMIDs). Published whatever it is. "
                    "engine_sha pins the engine that was measured; verify_all refuses the standard if "
                    "harness/acquisition.py changes without a new entry here. This is not prospective validation."),
           "validation_status": VALIDATION_STATUS,
           "engine_sha": sha, "measured_utc": now, "summary": summary, "per_topic": rows, "history": history}
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"REGRESSION-CORPUS RECALL {summary['recall_text']} over {len(scored)} scored topics (engine {sha[:12]}, {now})")
    for r in rows:
        print(f"  {r['slug']:42s} state={r['state']:9s} hits={str(r['hits_in_boolean_set']):>6s} "
              f"recalled {r['recalled']}/{r['denominator']}  missed={r['missed_pmids']}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
