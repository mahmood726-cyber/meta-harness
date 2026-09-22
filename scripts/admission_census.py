"""Admission census: what the BUILD decided at pooling, read from the stamps it wrote -- never recomputed here.

Replaces scripts/admission_shadow_census.py (retired 2026-09-21 with the enforcement gate): the shadow census was a
second implementation of P5/P8 that measured a decision the build did not read. Now harness/admission.py is the one
implementation (read at the pooling convergence point, re-read by harness/gate.check_admission_enforced), and this
script only COUNTS its stamps. A pooled row with no stamp is a refusal here (exit 1): this script never computes a
verdict for it, because a census that fills gaps with its own arithmetic is the shadow census again.

Kinds counted, named before any number (a control is not data; a set-aside is not a pooled row):
  pooled rows            rows in outcome.trials, stamped ADMISSIBLE or MIGRATION_STATE_UNBOUND_LEGACY
  set-aside rows         declared_absent_trials whose state is FAMILY_ELIGIBILITY_NOT_ESTABLISHED / FAMILY_INELIGIBLE
  unstamped pooled rows  a pooled row without admission_verdict (a page built before the build read the decision)
  outcomes with no candidate rows   NO_CANDIDATE_ROWS (nothing reached the pool) -- not a zero of anything
Primary outcomes are reported separately from all outcomes. Topics without a review are named, not dropped.

LIMITS, printed with every run: in-build admission evaluates P5 (family eligibility) and P8 (endpoint bound) only;
the twelve other bundle predicates are evaluated by scripts/build_bundle.py for the topics that carry a bundle.

    python scripts/admission_census.py [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import admission  # noqa: E402


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def census():
    rows, topics, no_review = [], 0, []
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        if not os.path.isfile(rp):
            if os.path.isdir(os.path.join(ROOT, "docs", "reviews", slug)):
                no_review.append(slug)
            continue
        topics += 1
        review = _load(rp)
        for o in review.get("outcomes") or []:
            s = admission.summary(o)
            primary = bool(o.get("primary"))
            for t in o.get("trials") or []:
                v = t.get("admission_verdict") if isinstance(t.get("admission_verdict"), dict) else None
                rows.append({"slug": slug, "outcome": o.get("name"), "primary": primary, "kind": "pooled", "trial": str(t.get("id")),
                             "final": v.get("final") if v else None, "stamped": v is not None,
                             "bundle_rule_agreement": (v or {}).get("predicates", {}).get("P8_endpoint_bound", {}).get("bundle_rule_agreement") if v else None})
            for a in o.get("declared_absent_trials") or []:
                if a.get("state") in admission.ADMISSION_SET_ASIDE_STATES:
                    rows.append({"slug": slug, "outcome": o.get("name"), "primary": primary, "kind": "set_aside", "trial": str(a.get("id")),
                                 "final": "INADMISSIBLE", "stamped": isinstance(a.get("admission_verdict"), dict),
                                 "state": a.get("state"), "eligibility_state": a.get("eligibility_state"), "absence_code": a.get("absence_code")})
            rows.append({"slug": slug, "outcome": o.get("name"), "primary": primary, "kind": "outcome", "summary_state": s["state"]})
    return topics, no_review, rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    topics, no_review, rows = census()
    pooled = [r for r in rows if r["kind"] == "pooled"]
    aside = [r for r in rows if r["kind"] == "set_aside"]
    outcomes = [r for r in rows if r["kind"] == "outcome"]
    unstamped = [r for r in pooled if not r["stamped"]]
    print(f"rule: {admission.SCOPE['rule']}")
    print(f"topics with a review: {topics}; review dirs without review.json (named, not dropped): {no_review or 'none'}")
    for label, sel in (("PRIMARY outcomes", lambda r: r["primary"]), ("ALL outcomes", lambda r: True)):
        P = [r for r in pooled if sel(r)]; A = [r for r in aside if sel(r)]; O = [r for r in outcomes if sel(r)]
        N = len(P) + len(A)
        print(f"{label}: candidate rows that reached admission N = {N} = pooled {len(P)} + set aside {len(A)}; outcomes {len(O)} "
              f"{dict(Counter(r['summary_state'] for r in O))}")
        print(f"   pooled by verdict: {dict(Counter(r['final'] for r in P))}; unstamped pooled rows: {sum(1 for r in P if not r['stamped'])}")
        print(f"   pooled bound by a route the bundle's P8 does not name (OTHER_ROUTE): {sum(1 for r in P if r['bundle_rule_agreement'] == 'OTHER_ROUTE')}")
        print(f"   set aside by (state, eligibility, absence_code): {dict(Counter((r['state'], r['eligibility_state'], r['absence_code']) for r in A))}")
    print("LIMITS: counts read from the build's stamps (harness/admission.py); in-build admission evaluates "
          f"{', '.join(admission.SCOPE['evaluated_in_build'])} only; {', '.join(admission.SCOPE['not_evaluated_in_build'])} are "
          f"evaluated only by the bundle ({admission.SCOPE['where_the_rest_is_evaluated']}); "
          f"a verdict from the bundle itself exists for "
          f"{sum(1 for s in os.listdir(os.path.join(ROOT, 'docs', 'reviews')) if os.path.isfile(os.path.join(ROOT, 'docs', 'reviews', s, 'BUNDLE.json')))} of {topics} topics. "
          f"{admission.SCOPE['p8_divergence']}.")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"topics": topics, "no_review": no_review, "rows": rows}, fh, indent=1)
    bad = [r for r in pooled if r["stamped"] and r["final"] not in ("ADMISSIBLE", "MIGRATION_STATE_UNBOUND_LEGACY")]
    if unstamped:
        print(f"REFUSED: {len(unstamped)} pooled row(s) carry no admission verdict (this census does not compute one): "
              + "; ".join(f"{r['slug']}/{r['trial']}" for r in unstamped[:8]) + (" ..." if len(unstamped) > 8 else ""))
    if bad:
        print(f"REFUSED: {len(bad)} pooled row(s) carry a verdict that does not admit them (lane R finding R6): "
              + "; ".join(f"{r['slug']}/{r['trial']}={r['final']}" for r in bad[:8]) + (" ..." if len(bad) > 8 else ""))
    return 1 if (unstamped or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
