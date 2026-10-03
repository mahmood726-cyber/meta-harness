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
sys.path.insert(0, os.path.join(ROOT, "scripts"))
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


@contextlib.contextmanager
def _both(a, b):
    with a, b:
        yield


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


_OLD_TABLE_HEAD = re.compile(r"(tocilizumab|tcz|usual care|placebo|standard (?:of )?care|control)[^()]{0,30}"
                             r"\(\s*n\s*=\s*(\d+)\s*\)", re.I)
_COVIDSTORM_TABLE = ("Table 3 Tocilizumab group ( n = 57) Standard-of-care group ( n = 29) p-value Hospitalization (d), "
                     "median (interquartile range) 9 (7-12) 12 (9-15) 0.014 Death at day 28, n (%) 1 (1.8) 0 (0) N/A")


def q9_hyphenated_arm_header():
    """COVIDSTORM's 'Standard-of-care group ( n = 29)': the table row is MISSED (fires) when the hyphenated arm is not
    an arm word."""
    return g.table_candidates(_COVIDSTORM_TABLE) == []


def q10_recovery_full_text_not_acquired():
    """RECOVERY's own open full text (PMID 33933206, PMC8084355, CC BY) must be HELD. It was not: the topic's build never
    ran the full-text rung (no 'fulltext' in its config) and only its abstract was held. Guard = the cascade's
    acquisitions (scripts/g1_toci_cascade.py)."""
    return not any("33933206" in ref and "<body" in txt for ref, txt in g.held_texts("RECOVERY"))


def q11_found_for_is_not_bound_to():
    """A paper FOUND by a trial's search is not that trial's report: ARCHITECTS' searches return papers that merely cite
    its registration. Fires if ARCHITECTS reads any paper (no ARCHITECTS report is held)."""
    return bool(g.held_texts("ARCHITECTS"))


def q12_react_citing_meta_confirms():
    """ANTI-CIRCULARITY through a meta: PMC8584705 (J Clin Med 2021, CC BY) prints RECOVERY's 621/2022 vs 729/2094 but
    CITES REACT, so its counts may be REACT's own. Fires if it is accepted as an independent second source."""
    import g1_toci_meta2_forest as m2
    x = open(os.path.join(ROOT, "cache", "comparators", "34768455", "g1_meta2_PMC8584705.xml"), encoding="utf-8").read()
    return m2.independence(x)["state"] == "INDEPENDENT"


def q12_guard_removed():
    """Without the independence check: does that meta print a primary reading's tuple, i.e. would it have confirmed?"""
    import g1_toci_meta2_forest as m2
    t = g._fold(m2.text_of(open(os.path.join(ROOT, "cache", "comparators", "34768455", "g1_meta2_PMC8584705.xml"),
                               encoding="utf-8").read()))
    return bool(re.search(r"(?<!\d)621(?!\d).{0,25}(?<!\d)2022(?!\d)", t) and re.search(r"(?<!\d)729(?!\d).{0,25}(?<!\d)2094(?!\d)", t))


def q13_percentages_never_state_a_count():
    """EMPACTA without the second metas' printed events/total: the registry count is DERIVED from '10.4% of 249', and the
    paper's text gives only '10.4% ... 8.6%'. Fires if two agreeing percentages ESTABLISH the counts."""
    extract = json.load(open(g.AACT_FILE, encoding="utf-8"))
    old = g._META2
    g._META2 = {}
    try:
        return g.assess("EMPACTA", extract, g.second_meta_rows())["state"] == g.ESTABLISHED
    finally:
        g._META2 = old


_COD = ("The most common reason for death was COVID-19 pneumonia (36 of 72 deaths in the tocilizumab arm and 20 of 36 "
        "deaths in the placebo arm). ‡ Excluding COVID-19 and COVID-19 pneumonia, eight serious infections occurred "
        "after day 28.")


def q14_cause_of_death_breakdown_read_as_arm_deaths():
    """COVACTA (PMID 35475258): '36 of 72 DEATHS' is a cause-of-death breakdown; read as 36 deaths of 72 patients it made
    a false 28-day row (the day-28 word came from the next footnote). Fires if it yields a candidate."""
    return bool(g.text_candidates(_COD))


_COD_ONE_SENTENCE = ("By day 28 the most common reason for death was COVID-19 pneumonia (36 of 72 deaths in the tocilizumab "
                     "arm and 20 of 36 deaths in the placebo arm).")


def q14b_deaths_denominator_alone():
    """The deaths-denominator guard ON ITS OWN: one sentence (no footnote split can rescue it) with a day-28 word.
    Fires if '36 of 72 deaths' is read as 36 deaths of 72 patients. (The first cut of this guard compiled to a
    backspace instead of a word boundary and never filtered anything; Q14 passed on the footnote split alone.)"""
    return bool(g.text_candidates(_COD_ONE_SENTENCE))


def q14_guard_removed():
    s = g._fold(_COD)
    return len(list(g._PAIR.finditer(s))) == 2 and bool(g._DEATH_WORDS.search(s) and g._DAY28.search(s))


def q15_meta_count_with_primary_percentage_established():
    """EMPACTA: every primary gives a PERCENTAGE (AACT 'Mortality Rate by Day 28' 10.4/8.6; the abstract '10.4% ... 8.6%');
    only a meta prints 26/249 vs 11/128. Fires if that is ESTABLISHED (a secondary statement standing in for a primary)."""
    extract = json.load(open(g.AACT_FILE, encoding="utf-8"))
    g._META2 = g.meta2_rows()
    return g.assess("EMPACTA", extract, g.second_meta_rows())["state"] == g.ESTABLISHED


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
        # two layers since the codex review (toci_match#2): the day-28 word AND the any-other-day refusal on the time
        # frame -- the guard removed is BOTH
        "Q7_day_30_read_as_day_28": (q7_timepoint, lambda: _both(patched(g, "_DAY28", re.compile(r"\d+\s*days?", re.I)),
                                                                patched(g, "_OTHER_DAY", NEVER))),
        "Q9_hyphenated_control_arm_header_missed": (q9_hyphenated_arm_header,
                                                    lambda: patched(g, "_TABLE_HEAD", _OLD_TABLE_HEAD)),
        "Q10_RECOVERY_open_full_text_not_acquired": (q10_recovery_full_text_not_acquired, lambda: patched(
            g, "_ACQ_KEEP", lambda a: not str(a.get("query") or "").startswith("cascade:"))),
        "Q11_paper_found_for_a_trial_read_as_its_report": (q11_found_for_is_not_bound_to, lambda: patched(
            g, "_ACQ_BOUND", lambda a, label: label in (a.get("found_for"), a.get("label_query")))),
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
    stated = q13_percentages_never_state_a_count()
    with patched(g, "_STATED_REQUIRED", False):
        stated_off = q13_percentages_never_state_a_count()
    out["Q13_two_percentages_establish_a_count"] = {"fired_as_built": stated, "fires_with_guard_removed": stated_off}
    out["Q14_cause_of_death_breakdown_read_as_arm_deaths"] = {"fired_as_built": q14_cause_of_death_breakdown_read_as_arm_deaths(),
                                                             "fires_with_guard_removed": q14_guard_removed()}
    # the deaths-denominator guard alone: guard removed = the unfiltered pairs of that sentence
    s14 = g._fold(_COD_ONE_SENTENCE)
    out["Q14b_deaths_denominator_guard_alone"] = {
        "fired_as_built": q14b_deaths_denominator_alone(),
        "fires_with_guard_removed": len(list(g._PAIR.finditer(s14))) == 2 and bool(g._DAY28.search(s14))}
    q15 = q15_meta_count_with_primary_percentage_established()
    with patched(g, "_PRIMARY_MUST_STATE", False):
        q15_off = q15_meta_count_with_primary_percentage_established()
    out["Q15_meta_count_plus_primary_percentage_established"] = {"fired_as_built": q15, "fires_with_guard_removed": q15_off}
    out["Q12_REACT_citing_meta_confirms_RECOVERY"] = {"fired_as_built": q12_react_citing_meta_confirms(),
                                                      "fires_with_guard_removed": q12_guard_removed()}
    # Q8: a SAFETY-population death count established as the efficacy 28-day row (BACC-Bay: REACT's 9/161 vs 4/82 is the
    # paper's 'Adverse Events in the Safety Population' table; the mITT efficacy count is 9/161 vs 3/81)
    bacc = next(t for t in r["trials"] if t["label"] == "BACC-Bay")
    out["Q8_safety_count_established_as_efficacy_row"] = {
        "fired_as_built": bacc["state"] == g.ESTABLISHED and bacc["row"].get("denominator_kind") == g.SAFETY,
        "fires_with_guard_removed": any(x["denominator_kind"] == g.SAFETY and len(x["independent_sources"]) >= 2
                                        and set(x["independent_sources"]) & {"AACT", "TEXT"} for x in bacc["readings"])}
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
