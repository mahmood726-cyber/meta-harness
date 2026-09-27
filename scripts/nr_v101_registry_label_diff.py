"""Registry EXACT_TARGET labels that change between two full rebuilds (read-only).

  python scripts/nr_v101_registry_label_diff.py A_DIR B_DIR [--out REPORT.json]

Every registry-outcome classification a page carries:
  family   trial_families[].outcome_status[].registered_outcome_candidates[]   (AACT design_outcomes rows)
  pooled   target_endpoint_alternatives[] / selected rows whose candidate is a ClinicalTrials.gov results measure
Keyed by (slug, family or row, outcome, registry row id). Reports how many EXACT_TARGET labels in A are downgraded in B,
split into CONFLICT (-> DIFFERENT_OUTCOME, or the candidate dropped because it no longer matches at all) and UNCONFIRMED
(-> NEAR_MATCH), with the conflicting dimensions.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def _labels(rv):
    out = {}
    for f in rv.get("trial_families") or []:
        for st in f.get("outcome_status") or []:
            for c in st.get("registered_outcome_candidates") or []:
                row = c.get("row") or {}
                out[("family", f.get("family_id"), st.get("outcome"), str(row.get("id")))] = {
                    "class": c.get("target_endpoint_class"), "measure": row.get("measure"),
                    "registry_match": c.get("registry_match")}
    for o in rv.get("outcomes") or []:
        for kind in ("trials", "declared_absent_trials"):
            for t in o.get(kind) or []:
                for a in t.get("target_endpoint_alternatives") or []:
                    if str(a.get("candidate_id", "")).startswith("ctgov"):
                        out[("pooled", str(t.get("id")), o.get("name"), a.get("candidate_id"))] = {
                            "class": a.get("target_endpoint_class"), "measure": a.get("registry_title"),
                            "registry_match": a.get("registry_match")}
    return out


def main(argv):
    a, b = Path(argv[0]), Path(argv[1])
    rep = {"exact_before": 0, "downgraded": [], "by_kind": Counter(), "by_dimension": Counter()}
    for fb in sorted(b.glob("*.review.json")):
        fa = a / fb.name
        if not fa.exists():
            continue
        la = _labels(json.loads(fa.read_text(encoding="utf-8")))
        lb = _labels(json.loads(fb.read_text(encoding="utf-8")))
        for k, v in la.items():
            if v["class"] != "EXACT_TARGET":
                continue
            rep["exact_before"] += 1
            after = lb.get(k)
            if after and after["class"] == "EXACT_TARGET":
                continue
            rm = (after or {}).get("registry_match") or {}
            kind = ("UNCONFIRMED" if after and after["class"] == "NEAR_MATCH" and not rm.get("conflicts") else "CONFLICT")
            rep["by_kind"][kind] += 1
            for d in rm.get("conflicts") or rm.get("unconfirmed") or ["(no longer a candidate)"]:
                rep["by_dimension"][d] += 1
            rep["downgraded"].append({"slug": fb.name[:-len(".review.json")], "key": list(k), "measure": v["measure"],
                                      "after": (after or {}).get("class") or "DROPPED (DIFFERENT_OUTCOME)",
                                      "conflicts": rm.get("conflicts"), "unconfirmed": rm.get("unconfirmed"),
                                      "evidence": rm.get("evidence")})
    print(f"registry EXACT_TARGET labels downgraded: {len(rep['downgraded'])} of {rep['exact_before']}; "
          f"by kind {dict(rep['by_kind'])}; by dimension {dict(rep['by_dimension'])}")
    if "--out" in argv:
        rep["by_kind"], rep["by_dimension"] = dict(rep["by_kind"]), dict(rep["by_dimension"])
        Path(argv[argv.index("--out") + 1]).write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
