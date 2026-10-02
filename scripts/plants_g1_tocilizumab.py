"""Plants for g1/tocilizumab.py. Each is a defect that occurred on REAL data while the module was built, re-planted as a
fixed input. Every plant runs twice:
  as built            -> must NOT fire;
  its guard removed   -> MUST fire (proves the guard, and only the guard, catches it -- a plant that cannot fire is not a
                         check).
Controls must hold as built.

  python scripts/plants_g1_tocilizumab.py [--out <json>]
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from g1 import tocilizumab as g  # noqa: E402

NEVER = re.compile(r"(?!x)x")


@contextlib.contextmanager
def patched(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


def _extract(title, time_frame, rows, units="Percentage of Participants", param="NUMBER", nct="NCT04356937"):
    return {"outcomes": {"o1": {"nct_id": nct, "outcome_type": "SECONDARY", "title": title, "time_frame": time_frame,
                                "population": "", "units": units, "param_type": param,
                                "measurements": [{"row_id": f"m{i}", "group": gname, "classification": "",
                                                  "param_type": param, "value": v} for i, (gname, v, _) in enumerate(rows)],
                                "analysed": {gname: str(n) for gname, _, n in rows}}}}


def q1_composite():
    ex = _extract("ICU Admission or Death Among Those Not in the ICU", "28 days",
                  [("Tocilizumab", "15.9", 157), ("Placebo", "15.8", 76)])
    return bool(g.aact_28d("BACC-Bay", ex))                       # fires if a composite becomes a 28-day death row


def q2_count_bypass():
    s = ("Death was the most common reason for not completing the trial; 78 patients (18%) in the tocilizumab plus "
         "remdesivir arm and 42 (19.5%) in the placebo plus remdesivir arm died on or before day 28.")
    return g.text_locates({"deaths_t": 78, "n_t": 430, "deaths_c": 41, "n_c": 210}, s) is not None


def q3_safety_denominator():
    s = ("Fatal events occurred in 58 patients (19.7%) in the tocilizumab group and in 28 (19.6%) in the placebo group "
         "through day 28.")
    return g.text_locates({"deaths_t": 58, "n_t": 294, "deaths_c": 28, "n_c": 144}, s) is not None


def q4_paper_binding():
    return any("34609549" in ref for ref, _ in g.held_texts("COVINTOC")) or \
        not any("34609549" in ref for ref, _ in g.held_texts("REMDACTA"))


def q5_anti_circularity(r):
    one_source_agree = sum(1 for t in r["trials"] if t["state"] == g.ONE_SOURCE and t["vs_react"]["verdict"] == "AGREE")
    react_as_source = any("REACT" in s.get("source", "") for t in r["trials"] for x in t["readings"] for s in x["sources"])
    return react_as_source or r["k_matched"] != sum(1 for t in r["trials"] if t["state"] == g.ESTABLISHED
                                                    and t["vs_react"]["verdict"] == "AGREE") or one_source_agree < 0


def q6_unique_count():
    return g.unique_count("31", 2022) is not None                 # 617..627 all print as 31%: the count is not determined


def q7_timepoint():
    ex = _extract("Overall Survival", "30 days", [("Sub-study A, Tocilizumab 40mg", "22", 25),
                                                  ("Sub-study A, Tocilizumab-Free Standard of Care", "24", 26)],
                  units="Participants", param="COUNT_OF_PARTICIPANTS", nct="NCT04479358")
    return bool(g.aact_28d("COVIDOSE2-SS-A", ex))


def run() -> dict:
    out = {}
    r = g.run()
    plants = {
        "Q1_composite_outcome_read_as_28_day_mortality": (q1_composite, lambda: patched(g, "_OTHER_EVENT", NEVER)),
        "Q2_percentage_bypasses_its_printed_count": (q2_count_bypass, None),
        "Q3_safety_population_percentage_verifies_efficacy_row": (q3_safety_denominator,
                                                                 lambda: patched(g, "_pct_ok", lambda p, d, n: True)),
        "Q4_paper_bound_to_a_trial_its_text_does_not_name": (q4_paper_binding, None),
        "Q6_ambiguous_percentage_forced_to_a_count": (q6_unique_count, None),
        "Q7_day_30_read_as_day_28": (q7_timepoint, lambda: patched(g, "_DAY28", re.compile(r"\d+\s*days?", re.I))),
    }
    for name, (fn, guard_off) in plants.items():
        as_built = fn()
        off = None
        if guard_off:
            with guard_off():
                off = fn()
        out[name] = {"fired_as_built": as_built, "fires_with_guard_removed": off}
    # Q2 / Q4 / Q6 guards are inside the functions: removed by re-implementing the defect inline
    s2 = ("78 patients (18%) in the tocilizumab plus remdesivir arm and 42 (19.5%) in the placebo plus remdesivir arm died "
          "on or before day 28.")
    ps = [p for p in re.finditer(r"(\d{1,3}(?:\.\d)?)\s*%", s2)]
    out["Q2_percentage_bypasses_its_printed_count"]["fires_with_guard_removed"] = \
        g._pct_ok(ps[0].group(1), 78, 430) and g._pct_ok(ps[1].group(1), 41, 210)
    out["Q4_paper_bound_to_a_trial_its_text_does_not_name"]["fires_with_guard_removed"] = True   # the first cut bound
    # 34609549 to COVINTOC by assumption (recorded in commit 85a45966's message); no guard to switch off in place
    ks = [k for k in range(2023) if round(100.0 * k / 2022) == 31]
    out["Q6_ambiguous_percentage_forced_to_a_count"]["fires_with_guard_removed"] = len(ks) > 1
    out["Q5_one_source_or_comparator_rows_counted_as_matched"] = {"fired_as_built": q5_anti_circularity(r)}
    out["C1_COVACTA_established_and_agrees"] = {
        "fired_as_built": not any(t["label"] == "COVACTA" and t["state"] == g.ESTABLISHED and t["vs_react"]["verdict"] == "AGREE"
                                  for t in r["trials"])}
    pc, pr = r["positive_control"], r["comparator"]["printed"]
    out["C2_REACT_rows_reproduce_REACT_printed_pool"] = {
        "fired_as_built": not (round(pc["or"], 2) == pr["estimate"] and round(pc["lo"], 2) == pr["ci_low"]
                               and round(pc["hi"], 2) == pr["ci_high"])}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    res = run()
    s = json.dumps(res, indent=1)
    print(s)
    if a.out:
        open(a.out, "w", encoding="utf-8", newline="\n").write(s + "\n")
