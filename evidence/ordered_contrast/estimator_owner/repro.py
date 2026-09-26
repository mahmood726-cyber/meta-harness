"""Reproduce the auditor's estimator-provenance findings on the REAL code, before any fix (lane OC, 2026-09-25).

Findings under test:
  F1 (estimator owner): estimand_evidence scans the WHOLE abstract for estimator words and, when all hits share one type, takes
     hits[0]; for LEADER that is the methods / noninferiority-margin sentence, which does not hold 0.87. A served estimator VALUE of
     'odds ratio' with that span passes, because P10 checks the span reproduces and the STATE matches, and P11 ignores the estimator.
  F2 (HR -> RR): only the stored estimator label changed HR -> RR (same span, estimate, CI, endpoint, arms). harness/estmeasure.py
     maps both to FIRST_EVENT_RATIO, so compatibility says 'compatible_labels' and nothing refuses.

Routes, each run on (a) the verifier blob at c9d665e0 (origin/main when this lane branched) and (b) the verifier on this branch
BEFORE the estimator-owner fix (blob named on the command line), and, for F2, (c) the real publication gate:
  - served-bundle plants: only docs/reviews/<slug>/BUNDLE.json is edited, IN PLACE (disk is too tight for a copy), and restored
    from git after every run;
  - the gate: harness.gate.gate_page on the page whose review.json row is relabelled RR, certificate digests recomputed so the
    integrity layer cannot be the refusal ("never credit an unrelated first blocker"); compared DIFFERENTIALLY with the canonical
    page, because in this sparse clone the gate already refuses the canonical page on a census re-render (environmental).

usage: python evidence/ordered_contrast/estimator_owner/repro.py <branch_prefix_verifier.py> <out.json>"""
import copy
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SLUG = "glp1-ra-mace-t2d"
LEADER = "PMID 27295427"
BUNDLE = os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json")
BASE = "c9d665e022a36111f31cb9e1d7b5867fe6e8fb2d"


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)


def verifier_blob(ref, dst):
    p = git("show", f"{ref}:scripts/verify_bundle.py")
    assert p.returncode == 0, p.stderr
    open(dst, "wb").write(p.stdout)
    return dst


def run(verifier):
    p = subprocess.run([sys.executable, verifier, "--root", "docs", "--slug", SLUG, "--json"], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    rep = json.loads(p.stdout)
    row = next((r for r in rep.get("rows", []) if r["pmid"] == LEADER.split()[1]), {})
    return {"verdict": rep["verdict"], "leader_final": row.get("final"),
            "leader_failed_predicates": sorted(k for k, v in (row.get("predicates") or {}).items() if not v),
            "failures": [f[:200] for f in rep.get("failures", [])]}


def served_row(b):
    return next(r for r in b["verification_rows"] if r["trial"]["id"] == LEADER)


def plant_f1_odds_ratio(b):
    """The paired test: the claimed estimator VALUE only, with the span the recomputation selects (served as-is)."""
    est = served_row(b)["analysis_identity"]["estimator"]
    est["value"] = "odds ratio"
    if isinstance(est.get("observed"), dict):
        est["observed"]["value"] = "odds ratio"


def plant_f2_rr_label(b):
    """Only the stored estimator label: effect.scale HR -> RR (estimate, CI, span, endpoint, arms untouched)."""
    served_row(b)["effect"]["scale"] = "RR"


def plant_f2_rr_label_and_field(b):
    r = served_row(b)
    r["effect"]["scale"] = "RR"
    est = r["analysis_identity"]["estimator"]
    est["value"] = "risk ratio"
    if isinstance(est.get("observed"), dict):
        est["observed"]["value"] = "risk ratio"


PLANTS = {"F1_claimed_odds_ratio_value": plant_f1_odds_ratio, "F2_label_HR_to_RR": plant_f2_rr_label,
          "F2_label_and_field_HR_to_RR": plant_f2_rr_label_and_field}


def gate_differential():
    """F2 through the real publication gate: relabel LEADER's review.json row RR, recompute every digest, compare reasons."""
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    from harness.gate import gate_page
    from harness import estmeasure
    review_dir = os.path.join(ROOT, "docs", "reviews", SLUG)
    ok0, r0 = gate_page(review_dir)
    rev_path = os.path.join(review_dir, "review.json")
    rev = json.load(open(rev_path, encoding="utf-8"))
    prim = next(o for o in rev["outcomes"] if o.get("primary"))
    t = next(x for x in prim["trials"] if str(x["id"]) == LEADER)
    before = {"scale": t.get("scale"), "effect_object": t.get("effect_object")}
    t["scale"] = "RR"
    if isinstance(t.get("effect_object"), dict):
        t["effect_object"] = estmeasure.classify("RR", t.get("source", "") or "")
    compat = estmeasure.pool_compatibility([x.get("effect_object") or estmeasure.classify(x.get("scale")) for x in prim["trials"]])
    open(rev_path, "wb").write(json.dumps(rev, ensure_ascii=False, indent=2).encode("utf-8"))
    from test_bundle_verifier import _recompute_everything          # the suite's own digest recomputation (review_sha256, release)
    _recompute_everything(os.path.join(ROOT, "docs"), (LEADER.split()[1],))
    ok1, r1 = gate_page(review_dir)
    return {"canonical": {"ok": ok0, "reasons": r0}, "leader_relabelled_RR": {"ok": ok1, "reasons": r1},
            "row_before": before, "estmeasure_after_relabel": {"row": estmeasure.classify("RR"), "pool": compat},
            "new_reasons": sorted(set(r1) - set(r0)), "reasons_gone": sorted(set(r0) - set(r1))}


def main():
    branch_verifier, out = sys.argv[1], sys.argv[2]
    tmp = os.path.join(os.path.dirname(out), "_verify_bundle_c9d665e0.py")
    verifiers = {"prefix_c9d665e0": verifier_blob(BASE, tmp), "branch_before_owner_fix": branch_verifier}
    canonical = json.load(open(BUNDLE, encoding="utf-8"))
    raw = open(BUNDLE, "rb").read()
    res = {"bundle_sha256": hashlib.sha256(raw).hexdigest(), "runs": {}}
    try:
        for vname, v in verifiers.items():
            res["runs"][vname] = {"baseline": run(v)}
            for pname, edit in PLANTS.items():
                b = copy.deepcopy(canonical)
                edit(b)
                open(BUNDLE, "wb").write(json.dumps(b, ensure_ascii=False, indent=1).encode("utf-8"))
                res["runs"][vname][pname] = run(v)
                open(BUNDLE, "wb").write(raw)
            res["runs"][vname]["restore"] = run(v)
        # what the served (pre-fix) estimator witness for LEADER actually is
        est = served_row(canonical)["analysis_identity"]["estimator"]
        res["served_leader_estimator_witness"] = {"value": est.get("value"), "basis": est.get("basis"), "span": est.get("span"),
                                                  "span_holds_0.87": "0.87" in (est.get("span") or "")}
        res["gate"] = gate_differential()
    finally:
        open(BUNDLE, "wb").write(raw)
        git("checkout", "--", "docs/reviews/" + SLUG, "docs/cache/" + SLUG)
        if os.path.exists(tmp):
            os.remove(tmp)
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for vname, runs in res["runs"].items():
        for k, v in runs.items():
            print(f"{vname:26s} {k:30s} {v['verdict']:4s} LEADER {v['leader_final']} {v['leader_failed_predicates']} {[f[:60] for f in v['failures']][:3]}")
    g = res["gate"]
    print("gate canonical ok", g["canonical"]["ok"], "| relabelled ok", g["leader_relabelled_RR"]["ok"], "| new reasons", g["new_reasons"],
          "| pool", g["estmeasure_after_relabel"]["pool"]["status"])
    print("served LEADER estimator witness holds 0.87:", res["served_leader_estimator_witness"]["span_holds_0.87"])


if __name__ == "__main__":
    main()
