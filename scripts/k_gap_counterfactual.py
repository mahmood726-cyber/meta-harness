"""COUNTERFACTUAL k: rebuild a topic's review core IN MEMORY from its pinned cache, optionally with extra records
appended, and report the primary pool. Writes nothing to cache/ or docs/.

Purpose: measure an acquisition adapter's conversion (identified -> admitted) topic by topic BEFORE any corpus-moving
pin. The added records go through the unchanged screen -> extract -> admission gate; nothing is admitted by this
script. A baseline run (no extra records) must reproduce the served k, or the counterfactual is not comparable and
the topic is refused.

    python scripts/k_gap_counterfactual.py --baseline [SLUG ...]
    python scripts/k_gap_counterfactual.py --members  [SLUG ...]   # + comparator members the k-gap table found
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "outputs", "k_gap")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def served_primary(slug):
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    prim = next((o for o in rev["outcomes"] if o.get("primary")), {})
    return {"k": (prim.get("result") or {}).get("k"), "trials": sorted(t.get("id") for t in prim.get("trials", []))}


def core_primary(core):
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    return {"k": (prim.get("result") or {}).get("k"), "trials": sorted(t.get("id") for t in prim.get("trials", [])),
            "declared_absent": sorted(d.get("id") for d in prim.get("declared_absent_trials", []))}


def funnel(core, pmids):
    """Where each added PMID ended: screen decision + rule id, then (if included) pooled / declared-absent reason."""
    scr = {r["id"]: r for r in core["screening"]["records"]}
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    pooled = {str(t.get("id", "")).replace("PMID ", "") for t in prim.get("trials", [])}
    absent = {str(d.get("id", "")).replace("PMID ", ""): d.get("reason_code") for d in prim.get("declared_absent_trials", [])}
    out = {}
    for p in pmids:
        r = scr.get(p)
        if r is None:
            out[p] = {"stage": "NOT_IN_SCREEN"}
        elif r["decision"] != "include":
            out[p] = {"stage": "SCREENED_OUT", "rule_id": r.get("rule_id"), "reason": (r.get("reason") or "")[:140]}
        elif p in pooled:
            out[p] = {"stage": "POOLED"}
        elif p in absent:
            out[p] = {"stage": "DECLARED_ABSENT", "reason_code": absent[p]}
        else:
            out[p] = {"stage": "INCLUDED_NOT_IN_PRIMARY", "family": r.get("trial_family_id")}
    return out


def build(slug, extra_records=None):
    from harness.pipeline import build_review_core
    from harness.registration import protocol_sha
    config = _j(os.path.join(ROOT, "topics", slug + ".json"))
    records = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    records = copy.deepcopy(records)
    if extra_records:
        have = {r.get("id") for r in records["records"]}
        records["records"] += [r for r in extra_records if r.get("id") not in have]
    return build_review_core(slug, config, records, protocol_sha(slug))


def member_pmids(slug):
    """Comparator members the k-gap table marks IDENTIFICATION (never in our corpus), confirmed-set only.

    The REPORT the comparator cited is added, not every PMID registered to the trial's NCT: adding all NCT-linked
    reports let dedup keep a design paper over the results paper (DECLARE-TIMI 58 -> X1 'not an RCT' on
    PMID 29693360), which measures our dedup, not the adapter. A member with no cited PMID (resolved by acronym or
    NCT only) contributes its NCT-linked PMIDs, and is counted apart as `nct_only`."""
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    cited, nct_only = [], []
    for r in t["trials"]:
        if (r["slug"] == slug and r["unit_source"] != "REFERENCE_SEED" and r["gap_class"] == "IDENTIFICATION"
                and r["drug"] != "OTHER_AGENT"):
            if r.get("cited_pmids"):
                cited += r["cited_pmids"]
            else:
                nct_only += r["pmids"]
    return sorted(set(cited) | set(nct_only)), sorted(set(nct_only))


def main(argv):
    mode = argv[0]
    slugs = argv[1:] or sorted(x["slug"] for x in _j(os.path.join(OUT, "k_gap_table.json"))["topics"])
    res = {}
    for slug in slugs:
        t0 = time.time()
        s = served_primary(slug)
        try:
            if mode == "--baseline":
                c = core_primary(build(slug))
                res[slug] = {"served_k": s["k"], "rebuilt_k": c["k"], "same_trials": s["trials"] == c["trials"],
                             "secs": round(time.time() - t0, 1)}
            else:
                from harness import fetch
                pm, nct_only = member_pmids(slug)
                recs = fetch._efetch(pm) if pm else []
                base = core_primary(build(slug))
                cfc = build(slug, recs)
                cf = core_primary(cfc)
                fn = funnel(cfc, [r["id"] for r in recs])
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "members_added": len(pm),
                             "nct_only_pmids": len(nct_only),
                             "records_fetched": len(recs), "counterfactual_k": cf["k"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "funnel": fn,
                             "secs": round(time.time() - t0, 1)}
        except Exception as exc:  # noqa: BLE001
            res[slug] = {"error": f"{type(exc).__name__}: {exc}"[:300]}
        print(slug, res[slug], flush=True)
    return res


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    r = main(sys.argv[1:])
    name = "counterfactual_baseline.json" if sys.argv[1] == "--baseline" else "counterfactual_members.json"
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, sort_keys=True)
