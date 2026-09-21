"""Row census BEFORE / AFTER a change to the route to the pool: what every pooled and set-aside row of every served
review.json was at a base commit, and what it is in the working tree, by topic. This is a DIFFERENT quantity from
scripts/verify_label_census.py (which bytes a row's 'verified' label was checked against): that census reads one
tree; this one compares two, and its unit is pool MEMBERSHIP and ADMISSIBILITY, not the verify label.

Rule (read from the review.json objects, never from prose):
  pooled row       = an entry of outcome["trials"]                       (endpoint_admissibility names its class;
                                                                            hand_binding_state BOUND when the hand
                                                                            binder located it in held bytes)
  set-aside row    = an entry of outcome["declared_absent_trials"] with absent_kind == "machine_absent"
                       and reason_code == "ENDPOINT_UNBOUND"              (ABSTAIN: candidate tuple + reason carried)
  unresolved row   = any declared_absent_trials entry with absent_kind == "machine_absent" (no documented decision)
  reviewer rows    = unresolved rows + pooled rows still UNBOUND_LEGACY   (admitted with no binding = still to read)
  moved out        = pooled at base, not pooled after (named, with the after-state and its reason)
  moved in         = pooled after, not pooled at base (named; each one is inspected by hand before it is trusted)
  k / estimate     = outcome["result"]["k"] and ["estimate"] compared per outcome (a moved primary is a finding)

Populations (denominators printed, never only counts):
  topics   = every docs/reviews/<slug>/review.json present in BOTH the base commit and the working tree; a topic
             the working tree could not build is listed NOT MEASURED, never counted as unchanged
  rows     = every pooled row at base (pooled_before) and after (pooled_after); every declared-absent row

Usage: python scripts/m2_row_census.py <base_commit> [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _before(commit: str, slug: str):
    p = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:docs/reviews/{slug}/review.json"], capture_output=True)
    return json.loads(p.stdout.decode("utf-8")) if p.returncode == 0 else None


def _after(slug: str):
    p = ROOT / "docs" / "reviews" / slug / "review.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def _rows(rev):
    out = {}
    for o in rev["outcomes"]:
        pooled = {t["id"]: t for t in o.get("trials") or []}
        absent = {a["id"]: a for a in o.get("declared_absent_trials") or []}
        out[o["name"]] = (pooled, absent, (o.get("result") or {}), bool(o.get("primary")))
    return out


def census(commit: str) -> dict:
    tot = collections.Counter()
    report = {"base_commit": commit, "topics": {}, "not_measured": [], "moved_out_of_pool": [],
              "moved_into_pool": [], "k_or_estimate_moved": []}
    for slug in sorted(os.listdir(ROOT / "docs" / "reviews")):
        b, a = _before(commit, slug), _after(slug)
        if b is None:
            continue
        if a is None:
            report["not_measured"].append(slug)
            continue
        rb, ra = _rows(b), _rows(a)
        t = collections.Counter()
        for name, (pb, ab, resb, primary) in rb.items():
            pa, aa, resa, _ = ra.get(name, ({}, {}, {}, False))
            for tid, row in pb.items():
                t["pooled_before"] += 1
                if row.get("endpoint_admissibility") == "UNBOUND_LEGACY":
                    t["unbound_before"] += 1
            for tid, row in pa.items():
                t["pooled_after"] += 1
                adm = row.get("endpoint_admissibility")
                t[f"after_{adm}"] += 1
                if row.get("hand_binding_state"):
                    t[f"after_hand_{row['hand_binding_state']}"] += 1
                if tid not in pb:
                    report["moved_into_pool"].append({"slug": slug, "outcome": name, "trial": tid, "adm": adm,
                                                      "binding_reason": row.get("endpoint_binding_reason")})
            for tid, row in pb.items():
                if tid not in pa:
                    arow = aa.get(tid) or {}
                    report["moved_out_of_pool"].append({
                        "slug": slug, "outcome": name, "trial": tid, "before_adm": row.get("endpoint_admissibility"),
                        "before_prov": row.get("provenance"), "after_absent_kind": arow.get("absent_kind"),
                        "after_state": arow.get("state"), "after_reason_code": arow.get("reason_code"),
                        "reason": (arow.get("endpoint_binding_reason") or arow.get("reason") or "")[:240],
                        "candidate_tuple": arow.get("candidate_tuple"),
                        "candidates": [c.get("text", "")[:120] for c in (arow.get("candidate_locations") or [])][:3]})
            for tid, arow in aa.items():
                if arow.get("absent_kind") == "machine_absent":
                    t["unresolved_after"] += 1
                    if arow.get("reason_code") == "ENDPOINT_UNBOUND":
                        t["abstain_after"] += 1
            for tid, arow in ab.items():
                if arow.get("absent_kind") == "machine_absent":
                    t["unresolved_before"] += 1
            if (resb.get("k"), resb.get("estimate")) != (resa.get("k"), resa.get("estimate")):
                t["k_changed_outcomes"] += 1
                report["k_or_estimate_moved"].append({
                    "slug": slug, "outcome": name, "primary": primary, "k_before": resb.get("k"), "k_after": resa.get("k"),
                    "estimate_before": resb.get("estimate"), "estimate_after": resa.get("estimate"),
                    "ci_before": [resb.get("ci_low"), resb.get("ci_high")], "ci_after": [resa.get("ci_low"), resa.get("ci_high")]})
        t["reviewer_rows_before"] = t["unresolved_before"] + t["unbound_before"]
        t["reviewer_rows_after"] = t["unresolved_after"] + t.get("after_UNBOUND_LEGACY", 0)
        report["topics"][slug] = dict(t)
        tot.update(t)
    report["total"] = dict(tot)
    report["n_topics_measured"] = len(report["topics"])
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base_commit")
    ap.add_argument("--json", help="write the full report here")
    args = ap.parse_args(argv)
    rep = census(args.base_commit)
    tot = rep["total"]
    n = rep["n_topics_measured"]
    print(f"m2 row census: base {args.base_commit} vs working tree; topics measured {n}; "
          f"NOT MEASURED {len(rep['not_measured'])}: {', '.join(rep['not_measured']) or 'none'}")
    print(f"  pooled rows          {tot.get('pooled_before', 0)} -> {tot.get('pooled_after', 0)}")
    print(f"  UNBOUND_LEGACY rows  {tot.get('unbound_before', 0)} -> {tot.get('after_UNBOUND_LEGACY', 0)}   hand BOUND after: {tot.get('after_hand_BOUND', 0)}")
    print(f"  moved out of pool    {len(rep['moved_out_of_pool'])} of {tot.get('pooled_before', 0)};  moved in {len(rep['moved_into_pool'])}")
    print(f"  set aside (ABSTAIN)  {tot.get('abstain_after', 0)}   unresolved rows {tot.get('unresolved_before', 0)} -> {tot.get('unresolved_after', 0)}")
    print(f"  reviewer rows        {tot.get('reviewer_rows_before', 0)} -> {tot.get('reviewer_rows_after', 0)}")
    print(f"  outcomes whose k or estimate moved  {tot.get('k_changed_outcomes', 0)}  (primary: "
          f"{sum(1 for m in rep['k_or_estimate_moved'] if m['primary'])})")
    for m in rep["k_or_estimate_moved"]:
        if m["primary"]:
            print(f"    PRIMARY {m['slug']} | {m['outcome'][:40]} | k {m['k_before']} -> {m['k_after']} | "
                  f"estimate {m['estimate_before']} -> {m['estimate_after']}")
    for m in rep["moved_out_of_pool"]:
        print(f"  OUT {m['slug']} | {m['outcome'][:36]} | {m['trial']} | {m['before_prov']} -> "
              f"{m['after_absent_kind']}/{m['after_reason_code']} | {m['reason'][:120]}")
    for m in rep["moved_into_pool"]:
        print(f"  IN  {m['slug']} | {m['outcome'][:36]} | {m['trial']} | {m['adm']} | {str(m['binding_reason'])[:100]}")
    for slug, t in rep["topics"].items():
        print(f"  {slug:40s} pooled {t.get('pooled_before', 0)}->{t.get('pooled_after', 0)}  "
              f"unbound {t.get('unbound_before', 0)}->{t.get('after_UNBOUND_LEGACY', 0)}  "
              f"bound_hand {t.get('after_hand_BOUND', 0)}  abstain {t.get('abstain_after', 0)}  "
              f"reviewer {t['reviewer_rows_before']}->{t['reviewer_rows_after']}")
    if args.json:
        json.dump(rep, open(args.json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"written {args.json}")
    return 0


if __name__ == "__main__":
    # stdout re-wrap only when run as a script: at import time it would close the capture of any test importing this
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main())
