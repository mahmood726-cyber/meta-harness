"""Corpus-wide screening contradictions, n of N: for every served review, every disagreement between the screening
ledger, the per-report screening record, the family object, the narrative and the adjudicator
(harness.screening_record.consistency_problems). n = reports with >=1 BLOCKING contradiction; N = screened reports
(every ledger row of every topic, read in full, never sampled). Advisory adjudicator disagreements are counted apart.
  python scripts/screening_contradictions.py [--ref <git sha>] [--out <json>]
With --ref the reviews are read from that commit (git show), otherwise from the working tree."""
from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import screening_record  # noqa: E402


def _slugs(ref):
    if ref:
        out = subprocess.run(["git", "ls-tree", "--name-only", f"{ref}:docs/reviews"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split()
        return sorted(out)
    d = os.path.join(ROOT, "docs", "reviews")
    return sorted(x for x in os.listdir(d) if os.path.isfile(os.path.join(d, x, "review.json")))


def _review(ref, slug):
    if ref:
        p = subprocess.run(["git", "show", f"{ref}:docs/reviews/{slug}/review.json"], cwd=ROOT, capture_output=True)
        return json.loads(p.stdout) if p.returncode == 0 else None
    p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def report(ref=None):
    topics, kinds, N, n_block, n_adv, missing = {}, collections.Counter(), 0, 0, 0, []
    for slug in _slugs(ref):
        rev = _review(ref, slug)
        if rev is None:
            missing.append(slug)
            continue
        rows = (rev.get("screening") or {}).get("records") or []
        probs = screening_record.consistency_problems(rev)
        blocking = sorted({p["report_id"] for p in probs if p["blocking"]})
        advisory = sorted({p["report_id"] for p in probs if not p["blocking"]})
        N += len(rows)
        n_block += len(blocking)
        n_adv += len(advisory)
        kinds.update(p["kind"] for p in probs)
        topics[slug] = {"screened_reports": len(rows), "reports_with_blocking_contradiction": blocking,
                        "reports_with_advisory_adjudicator_disagreement": advisory,
                        "problems": probs}
    return {"ref": ref or "WORKING_TREE", "topics_read": len(topics), "topics_unreadable": missing,
            "N_screened_reports": N, "n_reports_with_blocking_contradiction": n_block,
            "n_reports_with_advisory_adjudicator_disagreement": n_adv,
            "headline": f"{n_block} of {N} screened reports carry a blocking screening contradiction "
                        f"(ledger / record / family / narrative); {n_adv} more carry only an adjudicator disagreement",
            "by_kind": dict(sorted(kinds.items())), "topics": topics}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    r = report(a.ref)
    if a.out:
        open(a.out, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
    print(r["headline"], "| topics", r["topics_read"], "| by kind", r["by_kind"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
