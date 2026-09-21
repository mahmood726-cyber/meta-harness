"""Admission shadow census: the bundle's admission decision applied, for P5 (family eligible) and P8 (endpoint bound)
only, to every pooled primary row of every topic -- because a bundle, and therefore a verdict, exists for one topic.

The build never reads the admission decision (scripts/build_bundle.py computes it AFTER the build from the built
review.json; harness/trial_family.py's screen is "additive; existing pooling membership is preserved"). This script
measures how many pooled rows that decision would refuse today, using the bundle's own rule and the authoritative copy
it reads (cache/<slug>/families.json, eligibility.state / absence_code; review.json endpoint_binding):

    P5 FAIL  iff eligibility.state != "ELIGIBLE"
    P8 FAIL  iff endpoint_binding != "named_endpoint_resolved_to_definition_span"
    final    = SHADOW_ADMISSIBLE (P5 and P8 pass)
             | MIGRATION_STATE_UNBOUND_LEGACY (P8 is the ONLY failing predicate and the binding is unbound_legacy)
             | SHADOW_INADMISSIBLE (P5 fails, whatever P8 says -- the bundle's rule: P8-alone is the only migration case)

LIMITS, printed with every run: only P5 and P8 are evaluated; the other eleven predicates (span located, effect tokens,
components, conflicts, coverage, ...) need the bundle's acquisition and are not shadowed here, so SHADOW_ADMISSIBLE is
an upper bound on admissible rows and SHADOW_INADMISSIBLE a lower bound on refusals. N = pooled primary rows
(outcome.primary, trials[]) across every topic with a review; hand rows and non-primary outcomes are not counted.

    python scripts/admission_shadow_census.py [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUND = "named_endpoint_resolved_to_definition_span"


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def census():
    rows, topics = [], 0
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        if not os.path.isfile(rp):
            continue
        topics += 1
        review = _load(rp)
        primary = next((o for o in review.get("outcomes") or [] if o.get("primary")), None)
        if not primary:
            continue
        fp = os.path.join(ROOT, "cache", slug, "families.json")
        fam_by_id = {f.get("family_id"): f for f in (_load(fp).get("families") if os.path.isfile(fp) else []) if isinstance(f, dict)}
        fam_rendered = {f.get("family_id"): f for f in review.get("trial_families") or [] if isinstance(f, dict)}   # absence_code lives here (the bundle reads it from this copy too)
        for t in primary.get("trials") or []:
            fam = fam_by_id.get(t.get("family_id")) or {}
            el = fam.get("eligibility") or {}
            el_r = (fam_rendered.get(t.get("family_id")) or {}).get("eligibility") or {}
            state = el.get("state") if fam else None
            p5 = state == "ELIGIBLE"
            binding = t.get("endpoint_binding")
            p8 = binding == BOUND
            failing = [k for k, ok in (("P5_family_eligible", p5), ("P8_endpoint_bound", p8)) if not ok]
            final = ("SHADOW_ADMISSIBLE" if not failing else
                     "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and binding == "unbound_legacy" else
                     "SHADOW_INADMISSIBLE")
            rows.append({"slug": slug, "trial": str(t.get("id")), "family_id": t.get("family_id"), "family_in_cache": bool(fam),
                         "eligibility_state": state, "rendered_state": el_r.get("state"), "absence_code": el_r.get("absence_code"), "endpoint_binding": binding,
                         "target_endpoint_class": t.get("target_endpoint_class"), "failing": failing, "final": final})
    return topics, rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    topics, rows = census()
    N = len(rows)
    fin = Counter(r["final"] for r in rows)
    inad = [r for r in rows if r["final"] == "SHADOW_INADMISSIBLE"]
    print(f"rule: P5 (families.json eligibility.state == ELIGIBLE) and P8 (endpoint_binding == {BOUND}); "
          f"final per the bundle's rule (P8-alone by unbound_legacy = migration state; a P5 failure = INADMISSIBLE)")
    print(f"N = {N} pooled primary rows across {topics} topics with a review (hand rows and non-primary outcomes not counted)")
    print(f"SHADOW_INADMISSIBLE: {fin['SHADOW_INADMISSIBLE']} of {N}")
    p5 = [r for r in inad if "P5_family_eligible" in r["failing"]]
    print(f"   P5 fails (family eligibility != ELIGIBLE): {len(p5)} of {N}")
    print(f"      of which P8 passes (row bound to a definition span): {sum(1 for r in p5 if r['failing'] == ['P5_family_eligible'])}")
    print(f"      of which P8 also fails, unbound_legacy:              {sum(1 for r in p5 if r['endpoint_binding'] == 'unbound_legacy')}")
    print(f"      of which P8 also fails, another binding route:       {sum(1 for r in p5 if len(r['failing']) == 2 and r['endpoint_binding'] != 'unbound_legacy')}")
    print(f"      by (state, absence_code): {dict(Counter((r['eligibility_state'], r['absence_code']) for r in p5))}")
    print(f"      copies disagree (cache vs rendered): {sum(1 for r in p5 if r['eligibility_state'] != r['rendered_state'])}")
    other = [r for r in inad if r["failing"] == ["P8_endpoint_bound"]]
    print(f"   P8 fails alone by a binding route the bundle's rule does not name (INADMISSIBLE as the rule is written, "
          f"not a pooling defect -- a rule limit to raise with the bundle lane): {len(other)} of {N} "
          f"{dict(Counter(r['endpoint_binding'] for r in other))}")
    print(f"MIGRATION_STATE_UNBOUND_LEGACY (P8 only): {fin['MIGRATION_STATE_UNBOUND_LEGACY']} of {N}")
    print(f"SHADOW_ADMISSIBLE (P5 and P8 pass): {fin['SHADOW_ADMISSIBLE']} of {N}")
    print(f"unbound_legacy overall: {sum(1 for r in rows if r['endpoint_binding'] == 'unbound_legacy')} of {N}; "
          f"family not in cache: {sum(1 for r in rows if not r['family_in_cache'])} of {N}")
    print("LIMITS: P5 and P8 only; the other eleven predicates are not shadowed (SHADOW_ADMISSIBLE is an upper bound, "
          "SHADOW_INADMISSIBLE a lower bound); a verdict from the bundle itself exists for "
          f"{sum(1 for s in os.listdir(os.path.join(ROOT, 'docs', 'reviews')) if os.path.isfile(os.path.join(ROOT, 'docs', 'reviews', s, 'BUNDLE.json')))} of {topics} topics")
    if a.json:
        json.dump({"N": N, "topics": topics, "finals": dict(fin), "rows": rows}, open(a.json, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
