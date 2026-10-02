"""Tracker entry for tocilizumab-covid19-mortality vs WHO REACT 2021, in the G1 tracker schema (kgap/G1_INTERFACES.md
section 4, schema_version 1), built from g1/tocilizumab.py -- the topic's own G1 lane -- instead of the served pool
(which pools k=1) and the secondary tier (which refused REACT: no open JATS). The basis is stated in the file.

  python scripts/g1_toci_tracker.py   -> outputs/k_gap/g1/tocilizumab-covid19-mortality.json, then g1_tracker.py --table
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from g1 import tocilizumab as g  # noqa: E402

SLUG = "tocilizumab-covid19-mortality"
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{SLUG}.json")
ROUTE = {g.ESTABLISHED: "PRIMARY", g.ONE_SOURCE: "UNVERIFIED", g.CONFLICT: "UNVERIFIED", g.NO_SOURCE: "NO_ROW"}


def _route(t, best):
    """ESTABLISHED by two primaries (AACT + the trial's own text) -> PRIMARY; by one primary plus the second meta ->
    TWO_SOURCE (G1_INTERFACES section 2); anything less is not countable."""
    if t["state"] == g.ESTABLISHED:
        return "PRIMARY" if {"AACT", "TEXT"} <= set(best["independent_sources"]) else "TWO_SOURCE"
    return ROUTE[t["state"]]


def _row(d):
    return {"measure": "OR", "effect": None, "lower": None, "upper": None, "events_t": d["deaths_t"], "n_t": d["n_t"],
            "events_c": d["deaths_c"], "n_c": d["n_c"]} if d else None


def build():
    r = g.run()
    rx = g.react()
    trials = []
    for t in r["trials"]:
        rv = t["react_row"]
        best = next((x for x in t["readings"] if x["values"] == {k: (t["row"] or {}).get(k) for k in g._KEY}), None) \
            if t["row"] else None
        basis = ("two independent sources: " + " + ".join(best["independent_sources"]) if t["state"] == g.ESTABLISHED else
                 "one primary source: " + " + ".join(best["independent_sources"]) + "; no independent second source held"
                 if t["state"] == g.ONE_SOURCE and best else
                 "primary sources disagree" if t["state"] == g.CONFLICT else
                 "only a SAFETY-population count is held (" + "; ".join(sorted({s["source"] for x in t["readings"]
                 for s in x["sources"]})) + "); no efficacy-population 28-day count stated"
                 if t["readings"] and all(x["denominator_kind"] == g.SAFETY for x in t["readings"]) else
                 "no open primary source states 28-day deaths (" + "; ".join(t["texts_held"]) + ")" if t["texts_held"]
                 else "no open primary source held")
        verdict = t["vs_react"]["verdict"]
        trials.append({
            "label": t["label"], "family": t["registration"], "in_our_pool": None, "route": _route(t, best),
            "basis": basis, "g1_state": t["state"], "identity": t["identity"],
            "comparator_row": _row(rv), "comparator_row_findings": (
                [{"finding": "COMPARATOR_ROW_IS_SAFETY_POPULATION", "source": t["vs_react"].get("safety_source")}]
                if verdict == "REACT_ROW_IS_SAFETY_POPULATION" else []),
            "our_value": _row(t["row"]), "our_denominator_kind": (t["row"] or {}).get("denominator_kind"),
            "readings": t["readings"], "g1_countable": t["state"] == g.ESTABLISHED,
            "agreement_with_comparator_row": ("AGREE" if verdict == "AGREE" else "DISAGREE"
                                              if verdict in ("DIFFER", "DENOMINATOR_KIND_DIFFERS") else verdict)
            if t["row"] else "NO_PRIMARY_ROW"})
    est = [t for t in trials if t["g1_state"] == g.ESTABLISHED]
    pe, pr = r["pool_ours_established"], r["pool_react_same_trials"]
    rows_any = [x for x in r["trials"] if x["row"]]
    pa = g.pool_fe([x["row"] for x in rows_any])
    pra = g.pool_fe([x["react_row"] for x in rows_any])
    gv = rx["governing"]
    return {
        "schema_version": 1, "slug": SLUG, "comparator_pmid": rx["comparator_pmid"],
        "basis": ("g1/tocilizumab.py (lane g1/tocilizumab): k matched = trials whose 28-day deaths per arm are ESTABLISHED "
                  "by two independent sources (at least one primary: posted AACT results or the trial's own open text; a "
                  "second meta, 34019122, may confirm counts but never supply them) and equal REACT's row. REACT's rows "
                  "are the comparator only (anti-circularity)."),
        "N_comparator_trials": len(trials), "k_matched": sum(1 for t in est if t["agreement_with_comparator_row"] == "AGREE"),
        "N_eligible": len(trials), "named_differences": [],
        "open_gaps": [t["label"] for t in trials if t["g1_state"] != g.ESTABLISHED],
        "comparator_findings": [{"trial": t["label"], "finding": f["finding"], "comparator_row": t["comparator_row"],
                                 "trial_report": next((x["values"] for x in t["readings"] if x["denominator_kind"] == g.SAFETY), None),
                                 "detail": "the comparator's row equals the trial report's SAFETY-population death count",
                                 "basis": f["source"]} for t in trials for f in t["comparator_row_findings"]],
        "k_ours_total": None, "routes": dict(Counter(t["route"] for t in trials)), "trials": trials,
        "per_trial_agreement": dict(Counter(t["agreement_with_comparator_row"] for t in est)),
        "same_trials": {"state": "POOLED" if pe else "NOT_POOLED", "k": pe and pe["k_informative"], "measure": "OR",
                        "method": "FE",
                        "ours": {"estimate": pe and pe["or"], "ci_low": pe and pe["lo"], "ci_high": pe and pe["hi"]},
                        "theirs": {"estimate": pr and pr["or"], "ci_low": pr and pr["lo"], "ci_high": pr and pr["hi"]},
                        "verdict": {"verdict": "AGREE" if pe == pr else "DIFFER",
                                    "conclusion": "NO_CLEAR_EFFECT" if pe and pe["lo"] < 1 < pe["hi"] else "EFFECT",
                                    "estimate_gap_over_ci_halfwidth": round(abs(pe["or"] - pr["or"]) / ((pr["hi"] - pr["lo"]) / 2), 3) if pe else None},
                        "method_basis": f"comparator positive control reproduced FE: REACT's 19 rows -> OR "
                                        f"{r['positive_control']['or']} ({r['positive_control']['lo']}-{r['positive_control']['hi']})"},
        "same_trials_incl_one_source": {"k": pa and pa["k_informative"], "ours": pa, "theirs": pra,
                                        "note": "established + one-source rows; one-source rows are NOT counted in k"},
        "ours": {"k": len(est), "estimate": pe and pe["or"], "ci_low": pe and pe["lo"], "ci_high": pe and pe["hi"], "scale": "OR"},
        "comparator": {"outcome": "28-day all-cause mortality (Figure 1, tocilizumab)", "estimate": gv["estimate"],
                       "ci_low": gv["ci_low"], "ci_high": gv["ci_high"], "scale": "OR"},
        "comparator_basis": "REACT abstract/results text (VERIFIED_NOT_HELD, PMC8261689) and Figure 1 rows",
        "ours_not_in_comparator": [], "ours_not_in_comparator_detail": [],
        "secondary_tally": {}, "secondary_skipped": {}, "registry": {"snapshot": json.load(open(g.AACT_FILE, encoding="utf-8"))["snapshot"]},
    }


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d = build()
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    s = d["same_trials"]
    print(f"k matched {d['k_matched']} of {d['N_comparator_trials']} | routes {d['routes']} | same trials k={s['k']}: "
          f"ours {s['ours']} vs REACT {s['theirs']} -> {s['verdict']}")
    print("incl. one-source rows:", d["same_trials_incl_one_source"]["k"], d["same_trials_incl_one_source"]["ours"],
          "vs", d["same_trials_incl_one_source"]["theirs"])


if __name__ == "__main__":
    main()
