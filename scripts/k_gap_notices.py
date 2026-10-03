"""Draft RESULT-CHANGE NOTICES (harness/result_changes.py schema) for every served pooled result this branch moves.

This lane does not write docs/: a served number changes only through a notice in docs/result_changes.json that
Mahmood signs. This script derives each notice from the served review.json and the in-memory rebuild of the same topic
(scripts/k_gap_counterfactual.build), so the before/after are computed, not typed:

    python scripts/k_gap_notices.py SLUG [SLUG ...]   -> outputs/k_gap/notices_proposed.json (NOT_COUNTERSIGNED)
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import result_changes as rc  # noqa: E402
import k_gap_counterfactual as cfm  # noqa: E402

REASONS = {
    "semaglutide-obesity-weight": ("EXTRACTOR FIX 3: the trials' REPORTED mean difference (STEP 1 ETD -12.4 [-13.4, -11.5], "
                                   "STEP 3 -10.3 [-12.0, -8.6]) replaces CT.gov observed arm means, which are a different "
                                   "quantity; found by G1 result agreement with the comparator (now 2/2 AGREE)."),
    "probiotics-aad-prevention": ("EXTRACTOR FIX 4: McFarland 1995 (PMID 7872284) served a multivariable-ADJUSTED RR 0.29 from a "
                                  "risk-factor model; the randomised contrast is the crude 7/97 vs 14/96 (RR 0.49), the value "
                                  "the comparator pooled. Found by G1 forest-plot agreement. AND derived prevention screening "
                                  "(harness/screen.prevention_terms, ported from rescue 46c5f294): AAD is this topic's outcome, so "
                                  "a prevention trial's population is read from its abstract -- Hickson 2007 (PMID 17604300, "
                                  "7/57 vs 19/56) enters; exclusion terms stay on title/conditions, so no pooled trial is lost."),
}


def _prim(core):
    return next((o for o in core["outcomes"] if o.get("primary")), {})


def notice(slug):
    served = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    sp, cp = _prim(served), _prim(cfm.build(slug))
    before, after = rc.result_tuple(sp.get("result")), rc.result_tuple(cp.get("result"))
    if all(before[k] == after[k] for k in rc.RESULT_KEYS):
        return None
    ids = lambda p: {str(t.get("id")) for t in p.get("trials", [])}      # noqa: E731
    vals = lambda p: {str(t.get("id")): [t.get(k) for k in ("effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i",
                                                            "mean1", "mean2")] for t in p.get("trials", [])}  # noqa: E731
    scale = (sp.get("result") or {}).get("scale") or (cp.get("result") or {}).get("scale")
    changed = sorted(k for k in set(vals(sp)) & set(vals(cp)) if vals(sp)[k] != vals(cp)[k])
    return {"slug": slug, "outcome": sp.get("name"), "before": before, "after": after,
            "left_pool": sorted(ids(sp) - ids(cp)), "entered_pool": sorted(ids(cp) - ids(sp)),
            "values_changed_in_pool": changed, "reason": REASONS.get(slug, "rebuild on acq/k-gap"),
            "by": "acq/k-gap lane (derived; awaiting countersignature)",
            "when_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "conclusion_changed": rc.conclusion_changed(before, after, scale),
            "signature": {"state": "NOT_COUNTERSIGNED", "required_signer": "Mahmood"}}


def main(argv):
    slugs = argv or list(REASONS)
    out = [n for n in (notice(s) for s in slugs) if n]
    missing = [k for n in out for k in rc.REQUIRED if k not in n]
    assert not missing, f"notice schema incomplete: {missing}"
    p = os.path.join(ROOT, "outputs", "k_gap", "notices_proposed.json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"notices": out}, fh, indent=1, ensure_ascii=False)
    for n in out:
        print(n["slug"], n["before"], "->", n["after"], "| changed", n["values_changed_in_pool"], "| conclusion:",
              n["conclusion_changed"])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
