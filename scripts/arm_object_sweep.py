"""Measure the canonical arm object over committed topic pages.

Writes docs/arm_object_sweep.json.  No network: reads topics/*.json,
cache/<slug>/records.json, and docs/reviews/<slug>/review.json.
"""
from __future__ import annotations

from collections import Counter
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness import arm_object  # noqa: E402


def _norm(value):
    s = str(value or "").strip()
    for sep in ("Â·", "·"):
        if sep in s:
            s = s.split(sep)[-1].strip()
    return s.replace("PMID ", "").replace("PMID:", "").strip()


def _records(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return {}
    data = json.load(open(p, encoding="utf-8"))
    out = {}
    for rec in list(data.get("records") or []) + list(data.get("ctgov") or []):
        for key in (rec.get("id"), rec.get("nct"), rec.get("acronym")):
            nk = _norm(key)
            if nk:
                out[nk] = rec
    return out


def _screened_records(review):
    return ((review.get("screening") or {}).get("records") or [])


def measure_slug(slug):
    cfg_p = os.path.join(ROOT, "topics", slug + ".json")
    rev_p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if not (os.path.exists(cfg_p) and os.path.exists(rev_p)):
        return None
    cfg = json.load(open(cfg_p, encoding="utf-8"))
    review = json.load(open(rev_p, encoding="utf-8"))
    recs = _records(slug)
    refused = Counter()
    refused_rows = []
    hidden = []
    nd = total_fields = 0
    included = [r for r in _screened_records(review) if r.get("decision") == "include"]
    screened = list(_screened_records(review))
    for row in screened:
        rec = recs.get(_norm(row.get("id")))
        if not rec:
            continue
        obj = arm_object.build(rec, cfg)
        a, b = arm_object.not_derivable_counts(obj)
        nd += a
        total_fields += b
        for h in arm_object.hidden_eligible_contrasts(obj, cfg):
            hidden.append({
                "id": row.get("id"),
                "code": h.get("code"),
                "drug": (h.get("drug") or {}).get("value"),
                "comparator": (h.get("comparator") or {}).get("value"),
            })
        if row.get("decision") == "include":
            refusal = arm_object.assess(obj, cfg)
            if refusal:
                refused[refusal["rule_id"]] += 1
                refused_rows.append({
                    "id": row.get("id"),
                    "rule_id": refusal["rule_id"],
                    "reason": refusal["reason"],
                })
    return {
        "slug": slug,
        "included_refused_by_arm_object": {
            "n": sum(refused.values()),
            "N": len(included),
            "N_name": "screened-in records on the committed review page",
            "by_reason": dict(sorted(refused.items())),
            "records": refused_rows,
        },
        "hidden_eligible_contrast": {
            "n": len(hidden),
            "N": len(screened),
            "N_name": "screened records on the committed review page",
            "records": hidden,
        },
        "not_derivable_fields": {
            "n": nd,
            "N": total_fields,
            "N_name": "canonical arm-object field values derived across screened records",
        },
    }


def main():
    topics = sorted(os.path.splitext(p)[0] for p in os.listdir(os.path.join(ROOT, "topics"))
                    if p.endswith(".json"))
    rows = [r for slug in topics if (r := measure_slug(slug))]
    totals = {
        "topics_measured": len(rows),
        "included_refused_by_arm_object": {
            "n": sum(r["included_refused_by_arm_object"]["n"] for r in rows),
            "N": sum(r["included_refused_by_arm_object"]["N"] for r in rows),
            "N_name": "screened-in records across measured committed review pages",
        },
        "hidden_eligible_contrast": {
            "n": sum(r["hidden_eligible_contrast"]["n"] for r in rows),
            "N": sum(r["hidden_eligible_contrast"]["N"] for r in rows),
            "N_name": "screened records across measured committed review pages",
        },
        "not_derivable_fields": {
            "n": sum(r["not_derivable_fields"]["n"] for r in rows),
            "N": sum(r["not_derivable_fields"]["N"] for r in rows),
            "N_name": "canonical arm-object field values across measured committed review pages",
        },
    }
    out = {
        "source": "scripts/arm_object_sweep.py",
        "measurement": "MEASURED from committed cache/review objects; no network",
        "totals": totals,
        "topics": rows,
    }
    path = os.path.join(ROOT, "docs", "arm_object_sweep.json")
    json.dump(out, open(path, "w", encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
    print(json.dumps(totals, indent=2))
    print("wrote docs/arm_object_sweep.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
