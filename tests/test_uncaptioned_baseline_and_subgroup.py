"""Two ways a wrong number entered probiotics-aad-prevention the moment its held full texts were enabled.

Found by replaying the topic with pipeline.HELD_FULLTEXT_ENABLED = {probiotics-aad-prevention} (2026-10-01): k went
11 -> 14 and the pooled estimate disappeared (pool suppressed: INCOMPATIBLE (MEAN_DIFFERENCE + RISK_RATIO)). The
suppression was not a property of the evidence. Two of the three entering rows were defects:

  PMID 39497860  an UNCAPTIONED baseline table ("Characteristic | Probiotic Group (n=170) | Placebo Group (n=170) |
                 Age Groups ...") read as per-arm mean+/-SD -- a mean difference of patient ages entered an RR pool and
                 forced the estimand-mix suppression. table_role_refusal keyed only on a 'Table N:' caption, which an
                 inline table does not have.
  PMID 34541475  RR 0.53 "in the group of patients who were on regular PPI ... at 7 days" -- a SUBGROUP result,
                 harvested as the trial's effect. Nothing in the harness refused a subgroup.

The third (PMID 39529939, RR 0.36 for the primary outcome in all randomised participants) is a real result and must
still be admitted. Each guard has a positive and a negative plant so it cannot degenerate.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import extract, source_hierarchy  # noqa: E402

UNCAPTIONED_BASELINE = (
    "abstract mean+/-SD per arm (mean difference): Characteristic Probiotic Group (n=170) Placebo Group (n=170) "
    "Age Groups (n;%) 18-30 years 25 (14.71) 30 (17.65) 31-45 years 50 (29.41) 45 (26.47) 46-60 years 60 (35.29) "
    "55 (32.35) 61+ years 35 (20.59)")
PPI_SUBGROUP = (
    "However, in the group of patients who were on regular PPI, LcS use was associated with a lower risk of AAD at 7 "
    "(19% v 35.7%, RR: 0.53, 95% CI: 0.29-0.99, p = 0.040) and 30 days follow up (28% v 52.2%, RR: 0.54, 95% CI: "
    "0.32-0.91, p = 0.024).")
PRIMARY_ALL_RANDOMISED = (
    "Primary Outcome: Incidence of AAD Of the participants receiving the studied probiotic mix, 9.2% (26/282) "
    "developed AAD, whereas 25.3% (69/273) of the participants receiving placebo developed AAD (RR = 0.36 [95% CI, "
    "0.24-0.55]; OR = 0.30 [95% CI, 0-0.79]; P < .001) ( Figure 2 ).")
JEMPHASIS = ("abstract effect+CI (HR): Death from any cause occurred in 17 patients (15.3%) in the eplerenone group and "
             "10 patients (9.1%) in the placebo group (hazard ratio, 1.77; 95% CI, 0.81-3.87; P=0.15) (Table 3, "
             "Figure 1D)")
CHARACTERISTICS_WORD_IN_A_RESULT = (
    "Mortality did not differ by baseline characteristics; death occurred in 40 of 300 (n=300) patients given "
    "drug and 45 of 298 given placebo (RR 0.89, 95% CI 0.60-1.32).")
CONSISTENT_ACROSS_SUBGROUPS = (
    "Death from any cause occurred in 120 patients in the drug group and 150 in the placebo group (HR 0.80, 95% CI "
    "0.63-1.01); the effect was consistent across prespecified subgroups.")


def test_uncaptioned_baseline_table_is_refused():
    why = extract.table_role_refusal(UNCAPTIONED_BASELINE)
    assert why, "an uncaptioned baseline-characteristics table was read as an effect and not refused"
    assert "baseline" in why


def test_uncaptioned_guard_does_not_refuse_real_results():
    assert extract.table_role_refusal(JEMPHASIS) == ""
    assert extract.table_role_refusal(PRIMARY_ALL_RANDOMISED) == ""
    assert extract.table_role_refusal(CHARACTERISTICS_WORD_IN_A_RESULT) == ""


def test_subgroup_result_is_refused():
    why = extract.subgroup_refusal(PPI_SUBGROUP)
    assert why, "a result restricted to a subgroup (patients on regular PPI) was not refused"
    assert "subgroup" in why


def test_subgroup_guard_admits_whole_population_results():
    assert extract.subgroup_refusal(PRIMARY_ALL_RANDOMISED) == ""
    assert extract.subgroup_refusal(JEMPHASIS) == ""
    # 'consistent across subgroups' describes the overall result; it is not a subgroup estimate
    assert extract.subgroup_refusal(CONSISTENT_ACROSS_SUBGROUPS) == ""


def test_candidate_harvest_drops_the_subgroup_candidate_and_keeps_the_primary():
    """Both defective rows entered through the source-hierarchy candidate harvest (provenance pmc_fulltext_effect),
    which the row-level guards never see. The guard must apply where the candidate is harvested."""
    spec = {"name": "Antibiotic-associated diarrhoea", "keywords": ["AAD", "antibiotic-associated diarrhoea"]}
    refused: list[str] = []
    got = source_hierarchy.effect_candidates_for_outcome(spec, PPI_SUBGROUP + " " + PRIMARY_ALL_RANDOMISED, refused)
    effects = sorted(round(float(c["effect"]), 2) for c in got if c.get("effect") is not None)
    assert 0.53 not in effects and 0.54 not in effects, f"the PPI subgroup RR was harvested: {effects}"
    assert 0.36 in effects, f"the all-randomised primary RR was lost: {effects}"
    assert any("subgroup" in r for r in refused), refused


def test_both_guards_are_wired_into_both_row_routes():
    src = open(os.path.join(ROOT, "harness", "pipeline.py"), encoding="utf-8").read()
    assert src.count("extract.subgroup_refusal(") >= 2, "subgroup guard not applied on both abstract and full-text routes"


def test_held_fulltexts_opt_in_is_read_from_the_topic_config(tmp_path, monkeypatch):
    """The per-topic opt-in lives in topics/<slug>.json, so enabling one topic re-pins only that topic's certificate.
    Plant both ways: the config flag enables; its absence (or any value other than literal true) does not."""
    from harness import pipeline
    monkeypatch.setattr(pipeline, "ROOT", str(tmp_path))
    monkeypatch.setattr(pipeline, "HELD_FULLTEXT_ENABLED", frozenset())
    cache = tmp_path / "cache" / "t"
    cache.mkdir(parents=True)
    (cache / "ft_1.txt").write_text("held", encoding="utf-8")
    rec = {"records": [{"id": "1"}]}
    assert pipeline.held_fulltexts("t", rec, config={"held_fulltexts_enabled": True})[0] == {"1": "held"}
    assert pipeline.held_fulltexts("t", rec, config={})[0] == {}
    assert pipeline.held_fulltexts("t", rec, config={"held_fulltexts_enabled": "yes"})[0] == {}


def test_PLANT_an_incomplete_harms_outcome_still_states_that_its_pool_is_suppressed():
    """corticosteroids-cap Hyperglycaemia, 2026-10-01: enabling its held full text revealed a fifth reporting trial,
    the outcome became HARMS_INCOMPLETE, and page._outcome_block's early return for an incomplete harms synthesis
    dropped 'Pooled result SUPPRESSED (estimand-incompatible)' -- the honest-state ratchet caught the page getting
    quieter. Both states are true and both must be rendered."""
    import json as _json
    from harness import page
    rv = _json.load(open(os.path.join(ROOT, "docs", "reviews", "corticosteroids-cap-mortality", "review.json"),
                         encoding="utf-8"))
    o = next(x for x in rv["outcomes"] if x["name"] == "Hyperglycaemia")
    assert (o.get("result") or {}).get("suppressed_incompatible"), "fixture changed: Hyperglycaemia is no longer suppressed"
    html = page._outcome_block(o, show_inputs=False)
    assert "Pooled result SUPPRESSED (estimand-incompatible)" in html
    assert "HARMS" in html or "harm" in html.lower()
