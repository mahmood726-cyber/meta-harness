"""R4 AMBIGUITY plants: at every site where harness/extract.py takes ONE match while several could disagree, an input
whose candidates DISAGREE must be refused (the function's existing absent result), never resolved by taking the first.

Each plant first proves it is ambiguous (the regex_layer.ambiguity recorder sees >1 distinct candidate at that site),
then asserts harness.extract refuses it.
  * STEP sites (zero served radius) are fixed by r4_ambiguity_step.py: these plants FAIL on the unpatched tree and PASS
    after `python r4_ambiguity_step.py <root>`.
  * HELD sites (the change moves a served number) are NOT in the step script; their plants are strict xfail against
    harness.extract (the defect is live and documented), and a companion test proves the measured in-process change
    (regex_layer.ambiguity.change) refuses the same input.
"""
from __future__ import annotations

import pytest

from harness import extract
from regex_layer import ambiguity as A

I, C = ["colchicine"], ["placebo"]

PLANTS = {
    # site: (call, is_refused)
    "arm_pairs": (lambda: extract.extract_arm_counts(
        "Death occurred in 10 (5.0%) of 200 patients with colchicine, 20 (10.0%) of 200 with placebo and "
        "30 (7.5%) of 400 overall.", I, C), lambda r: r is None),
    "arm_den": (lambda: extract.extract_arm_counts(
        "Death occurred in 10 patients (10%) with colchicine and 20 patients (20%) with placebo.", I, C,
        denom_each=[100, 101]), lambda r: r is None),
    "arm_samepos": (lambda: extract.extract_arm_counts(
        "Death occurred in 10 (5.0%) of 201 colchicine patients and 20 patients (10.0%) with placebo.", I, C,
        denom_each=[200]), lambda r: r is None),
    "effect_first": (lambda: extract.extract_effect(
        "Colchicine reduced POAF (RR 0.62; 95% CI 0.52-0.74) and stroke (RR 0.48; 95% CI 0.30-0.76)."),
        lambda r: r is None),
    "eio_first": (lambda: extract.effect_in_outcome(
        "Mortality was lower (OR 0.80; 95% CI 0.70-0.90). In-hospital mortality was also lower "
        "(OR 0.92; 95% CI 0.85-0.99).", ["mortality"]), lambda r: r is None),
    "arm_ns": (lambda: extract._arm_ns(
        "Patients received colchicine (n=50) or placebo (n=50). In the analysis set, colchicine (n=45) and "
        "placebo (n=48).", I, C), lambda r: r == {}),
    "cont_pairs": (lambda: extract.extract_continuous(
        "Pain score was 3.1 (SD 1.2) with colchicine vs 4.2 (SD 1.5) with placebo at day 7 and 2.0 (SD 1.0) vs "
        "2.5 (SD 1.1) at day 30.", I, C, {"i": 50, "c": 50}), lambda r: r is None),
    "rate_pairs": (lambda: extract.extract_rate(
        "There were 120 exacerbations over 400 patient-years with colchicine and 180 exacerbations over 390 "
        "patient-years with placebo; in year two, 60 exacerbations over 200 patient-years and 90 exacerbations "
        "over 190 patient-years.", I, C), lambda r: r is None),
    "denom_each": (lambda: extract.extract_trial(
        "In stage one 100 patients were randomly assigned to each group; in stage two 120 were randomly assigned "
        "to each group. Death occurred in 10 patients (10.0%) with colchicine and 20 patients (20.0%) with placebo.",
        ["death"], I, C), lambda r: bool(r.get("absent"))),
    "k_first": (lambda: extract._parse_k("We included 12 RCTs. Of these, 9 RCTs reported mortality."),
                lambda r: r is None),
    "meta_primary": (lambda: extract.extract_meta(
        "Mortality was reduced (RR 0.80; 95% CI 0.70-0.90). In a sensitivity analysis mortality was reduced "
        "(RR 0.85; 95% CI 0.75-0.95).", ["mortality"])["primary"], lambda r: r is None),
    "sent_hr": (lambda: extract.extract_trial(
        "Mortality was lower with colchicine (HR 0.80; 95% CI 0.70-0.90). At five years mortality remained lower "
        "(HR 0.85; 95% CI 0.75-0.95).", ["mortality"], I, C, estimand="HR"), lambda r: bool(r.get("absent"))),
    "sent_arm": (lambda: extract.extract_trial(
        "Death occurred in 10 (5.0%) of 200 colchicine patients and 20 (10.0%) of 200 placebo patients. At one "
        "year, death occurred in 15 (7.5%) of 200 colchicine patients and 25 (12.5%) of 200 placebo patients.",
        ["death"], I, C), lambda r: bool(r.get("absent"))),
    "sent_effect": (lambda: extract.extract_trial(
        "Mortality was lower with colchicine (HR 0.80; 95% CI 0.70-0.90). At five years mortality remained lower "
        "(HR 0.85; 95% CI 0.75-0.95).", ["mortality"], I, C), lambda r: bool(r.get("absent"))),
    "sent_rate": (lambda: extract.extract_trial(
        "Exacerbations: 120 exacerbations over 400 patient-years with colchicine vs 180 exacerbations over 390 "
        "patient-years with placebo. In the extension, 60 exacerbations over 200 patient-years with colchicine vs "
        "90 exacerbations over 190 patient-years with placebo.", ["exacerbation"], I, C),
        lambda r: bool(r.get("absent"))),
    "sent_cont": (lambda: extract.extract_trial(
        "Patients received colchicine (n=50) or placebo (n=50). Pain score was 3.1 (SD 1.2) with colchicine vs "
        "4.2 (SD 1.5) with placebo at day 7. Pain score at day 30 was 2.0 (SD 1.0) with colchicine vs 2.5 (SD 1.1) "
        "with placebo.", ["pain score"], I, C), lambda r: bool(r.get("absent"))),
    "defn_window": (lambda: extract.composite_heterogeneity("MACE", [
        {"source": "The primary outcome was a composite of cardiovascular death, myocardial infarction, or stroke. "
                   "A secondary outcome was a composite of death, myocardial infarction, stroke, or unstable angina."},
        {"source": "The primary outcome was a composite of cardiovascular death, myocardial infarction, stroke, or "
                   "unstable angina."}]), lambda r: r == ""),
}

# sites whose refuse change moves a served number (regex_layer.radius / scripts/radius_r4_comparator.py): NOT in
# r4_ambiguity_step.py; filled in from the measured radii
HELD: set[str] = {
    "effect_first",   # regex_layer.radius r4_effect_first: 175 of 10,098 differ, 6 served
    "sent_hr",        # r4_sent_hr: 51 differ, 10 served
    "sent_effect",    # r4_sent_effect: 51 differ, 2 served
    "arm_pairs",      # r4_arm_pairs: 14 differ, 2 served
    "eio_first",      # extract_trial 0, but scripts/radius_r4_comparator.py: 16 comparator effects differ, 14 on pages
    "k_first",        # scripts/radius_r4_comparator.py: 2 comparator k differ, both served
    "arm_ns",         # r4_arm_ns: 4 differ, 0 served -- but omitting the ambiguous arm lets the flat denom_each fallback
                      # read a DIFFERENT denominator (tocilizumab 33085857 full text 14/82 -> 14/81): a new guess
    "defn_window",    # the radius said 0 served, but the 32-page rebuild (base 9ee0b06b) showed a served change:
                      # statins-primary-prevention-elderly loses its 'Composite heterogeneity' note and its
                      # compatibility-audit 'Endpoint definition' row (radius measured extract_trial, not the pipeline)
}


def _recorded(site):
    """The plant is genuinely ambiguous at `site`: the recorder (installed, nothing enabled) sees >1 candidate."""
    A.HITS.clear(); A.RECORD.clear(); A.RECORD.add(site); A.ENABLED.clear()
    attrs = A.SITES[site]
    old = {a: getattr(extract, a) for a in attrs}
    try:
        for a in attrs:
            setattr(extract, a, A.replacement(a, old[a]))
        PLANTS[site][0]()
    finally:
        for a, v in old.items():
            setattr(extract, a, v)
        A.RECORD.clear()
    return [h for h in A.HITS if h["site"] == site]


@pytest.mark.parametrize("site", sorted(PLANTS))
def test_plant_is_ambiguous(site):
    assert _recorded(site), f"plant for {site} has no disagreeing candidates -- it cannot test refusal"


@pytest.mark.parametrize("site", sorted(set(PLANTS) - HELD))
def test_step_site_refuses_ambiguity(site):
    call, refused = PLANTS[site]
    r = call()
    assert refused(r), f"{site}: ambiguous input was resolved to {r!r} instead of refused"


@pytest.mark.parametrize("site", sorted(HELD))
@pytest.mark.xfail(strict=True, reason="HELD: refusing here moves a served number; change measured, not applied")
def test_held_site_refuses_ambiguity(site):
    call, refused = PLANTS[site]
    assert refused(call())


@pytest.mark.parametrize("site", sorted(PLANTS))
def test_measured_change_refuses(site):
    call, refused = PLANTS[site]
    with A.change(site):
        r = call()
    assert refused(r), f"{site}: the in-process change did not refuse ({r!r})"
