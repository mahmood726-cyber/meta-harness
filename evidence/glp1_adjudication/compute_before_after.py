"""Derived before -> after for the GLP-1 MACE primary pool, computed through the PRODUCTION path only:
harness.known_missing._study_from_trial (the served rows -> Study) and harness.known_missing._pool_result
(harness.synth.pool: Paule-Mandel tau2, HKSJ on t_{k-1} with the max(1, Q/(k-1)) floor, PI on t_{k-1}), i.e. the
same functions the page uses for its primary result and its known-missing sensitivity panel.

Fails closed: the BEFORE pool is recomputed from the served rows and must reproduce the served primary result
(k, estimate, CI, PI to the served rounding) or nothing is written -- an 'after' is only meaningful against a
'before' proven to be the real one. Writes evidence/glp1_adjudication/BEFORE_AFTER.json.
  python evidence/glp1_adjudication/compute_before_after.py"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from harness import known_missing as KM   # noqa: E402
from harness.synth import Study           # noqa: E402

REVIEW = os.path.join(ROOT, "docs", "reviews", "glp1-ra-mace-t2d", "review.json")
# the bound results (evidence/glp1_adjudication/<TRIAL>.json carries every field's witness span)
ADD = {
    "FLOW": dict(effect=0.82, ci_low=0.68, ci_high=0.98),
    "ELIXA": dict(effect=1.02, ci_low=0.887, ci_high=1.172),          # FDA StatR unrounded text interval
    "ELIXA_table8_rendering": dict(effect=1.02, ci_low=0.89, ci_high=1.18),  # same doc, Table 8 rendering (conflict)
    "FREEDOM-CVO": dict(effect=1.24, ci_low=0.90, ci_high=1.70),
}


def main():
    r = json.load(open(REVIEW, encoding="utf-8"))
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    served = prim["result"]
    scale = served.get("scale") or "HR"
    base = [KM._study_from_trial(t, scale) for t in prim["trials"]]
    before = KM._pool_result(base, scale)
    for k in ("k", "estimate", "ci_low", "ci_high", "pi_low", "pi_high"):
        a, b = before.get(k), served.get(k)
        if (a != b) if k == "k" else abs(a - b) > 5e-5:
            sys.exit(f"REFUSED: recomputed BEFORE {k}={a} != served {b}; not the production path, nothing written")
    st = lambda name: Study(label=name, measure=scale, **ADD[name])
    # V1.0.1: the primary scenario takes its added rows from the ADMISSION MECHANISM itself (every witness, the endpoint
    # identity and the tuple re-verified), not from the typed ADD values, which remain only as the cross-check scenarios.
    from harness import result_adjudication as RA
    cfg = json.load(open(os.path.join(ROOT, "topics", "glp1-ra-mace-t2d.json"), encoding="utf-8"))
    admitted = RA.admitted_rows(dict(cfg["primary_outcome"], primary=True))
    if sorted(r["label"] for r in admitted) != ["ELIXA", "FLOW"]:
        sys.exit(f"REFUSED: the mechanism admits {[r['label'] for r in admitted]}, not exactly FLOW + ELIXA")
    for r in admitted:
        typed = ADD[r["label"]]
        if (r["effect"], r["ci_low"], r["ci_high"]) != (typed["effect"], typed["ci_low"], typed["ci_high"]):
            sys.exit(f"REFUSED: mechanism row {r['label']} {r['effect']} ({r['ci_low']}, {r['ci_high']}) != typed cross-check {typed}")
    mech = [KM._study_from_trial(r, scale) for r in admitted]
    scen = {
        "CONVENTIONAL_GLP1RA (primary strand): + FLOW + ELIXA": base + mech,
        "CONVENTIONAL_GLP1RA: + FLOW only": base + [st("FLOW")],
        "CONVENTIONAL_GLP1RA: + ELIXA only": base + [st("ELIXA")],
        "CONVENTIONAL_GLP1RA: + FLOW + ELIXA (ELIXA at its Table 8 rendering 0.89-1.18)": base + [st("FLOW"), st("ELIXA_table8_rendering")],
        "GLP1RA_ANY_DELIVERY (alongside): + FLOW + ELIXA + FREEDOM-CVO": base + [st("FLOW"), st("ELIXA"), st("FREEDOM-CVO")],
    }
    out = {"computed_by": "harness.known_missing._study_from_trial + _pool_result (harness.synth.pool); primary scenario rows from harness.result_adjudication.admitted_rows",
           "admitted_rows": [{k: r[k] for k in ("label", "id", "effect", "ci_low", "ci_high", "target_endpoint_class")} | {"identified_by": r["endpoint_identity"]["identified_by"], "decision_sha256": r["result_adjudication"]["decision_sha256"]} for r in admitted],
           "served_before": {k: served.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "tau2", "Q", "pi_low", "pi_high", "ci_provenance")},
           "recomputed_before": before, "before_reproduces_served": True, "inputs_added": ADD, "after": {}}
    for name, studies in scen.items():
        res = KM._pool_result(studies, scale)
        res["conclusion_effect_vs_served"] = KM.conclusion_effect(served, res)
        out["after"][name] = res
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "BEFORE_AFTER.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False, default=str)
    print(f"BEFORE (served, reproduced): k={before['k']} HR {before['estimate']} ({before['ci_low']}, {before['ci_high']}) PI ({before.get('pi_low')}, {before.get('pi_high')})")
    for name, res in out["after"].items():
        print(f"AFTER {name}: k={res['k']} HR {res['estimate']} ({res['ci_low']}, {res['ci_high']}) PI ({res.get('pi_low')}, {res.get('pi_high')}) tau2={res['tau2']} -> {res['conclusion_effect_vs_served']}")


if __name__ == "__main__":
    main()
