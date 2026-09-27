"""EFFECT IDENTITY BEFORE SOURCE PREFERENCE (external review of colchicine-recurrent-pericarditis, 2026-09-26).

Plants are the PRE-FIX producer's own served output at the pinned candidate 3876a62d (immutable; a missing commit is a failure,
never a skip): there, CORP-2's "relative risk 0.49 (0.24-0.65)" is ADMITTED over its counts, and CORP's RRR 0.56 is served as RR
0.44 with KEEP_REPORTED_EFFECT and reported_label RR. The tests assert the defect is present in those bytes, then that
harness.effect_identity detects it. Synthetic controls pin every mislabel hypothesis in both directions."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import effect_identity as ei   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "colchicine-recurrent-pericarditis"


def _git_json(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in this clone's history (never a skip)", pytrace=False)
    return json.loads(p.stdout)


def _row(outcome, pmid):
    rev = _git_json(f"docs/reviews/{SLUG}/review.json")
    o = next(x for x in rev["outcomes"] if x["name"] == outcome)
    return next(t for t in o["trials"] if t["id"] == f"PMID {pmid}")


def _abstract(pmid):
    return {str(r["id"]): r for r in _git_json(f"cache/{SLUG}/records.json")["records"]}[pmid]["abstract"]


# ------------------------------------------------------------------ (1) CORP-2: a published RRR under an RR label
def test_plant_fires_pre_fix_corp2_is_served_admitted_over_its_own_counts():
    t = _row("Recurrent pericarditis", "24694983")
    assert (t["effect"], t["ci_low"], t["ci_high"], t["scale"]) == (0.49, 0.24, 0.65, "RR")
    assert t["selection_rule"] == "PUBLISHED_EFFECT_TARGET_CLASS"                     # the hierarchy preferred it ...
    alt = next(a for a in t["alternatives"] if a.get("ai") is not None)
    assert (alt["ai"], alt["n1i"], alt["ci"], alt["n2i"]) == (26, 120, 51, 120)      # ... over counts it disagrees with
    assert "relative risk 0·49" in _abstract("24694983")                         # the SOURCE itself says "relative risk"


def test_corp2_conflict_names_the_rrr_hypothesis_and_holds():
    c = ei.conflict_check(_row("Recurrent pericarditis", "24694983"))
    assert c["state"] == "SOURCE_EFFECT_CONFLICT" and c["code"] == "SOURCE_EFFECT_CONFLICT"
    assert c["counts_implied"]["RR"] == {"estimate": 0.5098, "ci_low": 0.3421, "ci_high": 0.7596}      # the review's 0.342-0.760
    assert c["matching_hypotheses"] == ["RRR_AS_RR"] and c["resolution"] == "HOLD"
    assert not next(h for h in c["hypotheses"] if h["hypothesis"] == "AS_LABELLED")["matches"]


def test_a_held_row_stays_visible_and_is_never_relabelled():
    t = dict(_row("Recurrent pericarditis", "24694983"))
    t["effect_conflict"] = ei.conflict_check(t)
    a = ei.held_absence(t)
    assert a["state"] == "HELD_SOURCE_EFFECT_CONFLICT" and a["candidate_tuple"] == {"effect": 0.49, "ci_low": 0.24, "ci_high": 0.65, "scale": "RR"}
    assert t["effect"] == 0.49 and t["scale"] == "RR"                                 # nothing rewritten


# ------------------------------------------------------------------ synthetic controls: every hypothesis, both directions
def _pub(scale, est, lo, hi, counts=(30, 100, 50, 100), source=""):
    return {"effect": est, "ci_low": lo, "ci_high": hi, "scale": scale, "source": source,
            "alternatives": [{"ai": counts[0], "n1i": counts[1], "ci": counts[2], "n2i": counts[3]}]}


def _implied(measure, counts=(30, 100, 50, 100)):
    d = ei.counts_tuple(*counts, measure)
    return round(d["estimate"], 2), round(d["ci_low"], 2), round(d["ci_high"], 2)


def test_consistent_published_rr_is_kept():
    assert ei.conflict_check(_pub("RR", *_implied("RR")))["state"] == "CONSISTENT"


def test_each_mislabel_is_named():
    rr, orr = _implied("RR"), _implied("OR")
    assert ei.conflict_check(_pub("RR", round(1 - rr[0], 2), round(1 - rr[2], 2), round(1 - rr[1], 2)))["matching_hypotheses"] == ["RRR_AS_RR"]
    assert ei.conflict_check(_pub("RR", *orr))["matching_hypotheses"] == ["OR_AS_RR"]
    assert ei.conflict_check(_pub("OR", *rr))["matching_hypotheses"] == ["RR_AS_OR"]
    assert ei.conflict_check(_pub("RR", round(1 / rr[0], 2), round(1 / rr[2], 2), round(1 / rr[1], 2)))["matching_hypotheses"] == ["RECIPROCAL"]


def test_an_unexplained_conflict_holds_and_a_documented_adjusted_model_is_kept_disclosed():
    c = ei.conflict_check(_pub("RR", 0.30, 0.20, 0.45))
    assert c["state"] == "SOURCE_EFFECT_CONFLICT" and c["matching_hypotheses"] == [] and c["resolution"] == "HOLD"
    t = _pub("RR", 0.30, 0.20, 0.45, source="the adjusted relative risk was 0.30")
    assert ei.conflict_check(t, ei.adjusted_documented(t))["resolution"] == "KEEP_DISCLOSED"


def test_hr_is_not_comparable_to_crude_counts_and_a_zero_cell_is_not_guessed():
    assert ei.conflict_check(_pub("HR", 0.5, 0.3, 0.8))["state"] == "NOT_COMPARABLE"
    assert ei.conflict_check(_pub("RR", 0.5, 0.3, 0.8, counts=(0, 100, 5, 100)))["state"] == "NOT_COMPARABLE"


@pytest.mark.parametrize("text,expected", [("age-adjusted rate ratio 0.85", True), ("adjusted hazard ratio, 0.97", True),
                                           ("multivariate model to adjust for age", True),
                                           ("97.5% CI (multiplicity-adjusted for the two doses)", False),
                                           ("dose-adjusted apixaban", False), ("rate ratio 0.85; 95% CI 0.76-0.94", False)])
def test_adjusted_model_evidence_is_covariate_adjustment_only(text, expected):
    assert ei.adjusted_documented({"source": text}) is expected


# ------------------------------------------------------------------ (2) CORP: transformation provenance
def test_plant_fires_pre_fix_corp_rrr_is_served_as_a_reported_rr():
    for outcome in ("Recurrent pericarditis", "Symptom persistence at 72 hours"):
        t = _row(outcome, "21873705")
        assert t["selection_rule"] == "KEEP_REPORTED_EFFECT" and t["scale"] == "RR" and "effect_transform" not in t
        assert (t.get("effect_object") or {}).get("reported_label") == "RR"


def test_the_transform_is_recorded_from_the_source_including_the_symmetric_ci():
    ab = _abstract("21873705")
    rec = ei.transform_provenance(_row("Recurrent pericarditis", "21873705"), ab)
    assert rec["reported_measure"] == "RRR" and rec["reported"] == {"estimate": 0.56, "ci_low": 0.27, "ci_high": 0.73}
    assert rec["derived"] == {"measure": "RR", "estimate": 0.44, "ci_low": 0.27, "ci_high": 0.73}
    assert rec["read_from"] == "held abstract" and "symmetric" in rec["note"]       # the quotation is cut mid-CI
    sym = ei.transform_provenance(_row("Symptom persistence at 72 hours", "21873705"), ab)
    assert sym["reported"] == {"estimate": 0.56, "ci_low": 0.27, "ci_high": 0.74} and sym["derived"]["ci_low"] == 0.26 and sym["note"] is None


def test_a_nearby_effect_that_does_not_reproduce_the_served_tuple_is_never_taken():
    t = {"effect": 0.50, "ci_low": 0.30, "ci_high": 0.70, "scale": "RR",
         "source": "abstract effect+CI (RR): relative risk reduction, 0.56 [CI, 0.27 to 0.73]"}
    assert ei.transform_provenance(t) is None


def test_the_hold_reaches_the_reader_the_absence_layer_does_not_relabel_it():
    """The absence audit re-classified the held row as EXTRACTION_NOT_PERFORMED (seen in a real build): a hold read as 'not
    extracted'. A held row keeps its own state and code through absence.classify_reason."""
    from harness import absence
    t = dict(_row("Recurrent pericarditis", "24694983"))
    t["effect_conflict"] = ei.conflict_check(t)
    a = ei.held_absence(t)
    got = absence.classify_reason(["recurrent pericarditis"], _abstract("24694983"), row=a)
    assert got["reason_code"] == "SOURCE_EFFECT_CONFLICT" and got["state"] == "HELD_SOURCE_EFFECT_CONFLICT"


# ------------------------------------------------------------------ (3) an HR stays an HR; (4) OR reconstruction route; (5) definitions
def _snapshot_abstract(slug, snap, pmid):
    d = _git_json(f"cache/{slug}/snapshots/{snap}/records.json")
    rs = d["records"] if isinstance(d, dict) else d
    return next(r for r in rs if str(r.get("id") or r.get("pmid")) == pmid)["abstract"]


def test_sonia_hr_is_never_converted_and_routes_to_time_to_event():
    ab = _snapshot_abstract("corticosteroids-cap-mortality", "2026-09-15r2-search_v2", "41159889")
    assert "hazard ratio, 0.84; 95% confidence interval, 0.73 to 0.97" in ab and "246 patients (22.6%)" in ab
    sonia = {"id": "PMID 41159889", "effect": 0.84, "ci_low": 0.73, "ci_high": 0.97, "scale": "HR", "source": ab}
    r = ei.hr_route(sonia, "RR")                                        # not yet in any pool: judged alone
    assert r["route"] == "TIME_TO_EVENT_SEPARATE" and r["hr_retained"] == {"effect": 0.84, "ci_low": 0.73, "ci_high": 0.97}
    asc = dict(sonia, ascertained_denominators={"n1": 1089, "n2": 1092, "span": "day-30 vital status ascertained in ..."})
    assert ei.hr_route(asc, "RR")["route"] == "RISK_FROM_ASCERTAINED_DENOMINATORS"   # only with a typed, source-spanned record


def test_plant_pre_fix_balanced_pools_an_hr_with_a_count_rr_and_the_route_takes_the_hr_out():
    rev = _git_json("docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json")
    o = next(x for x in rev["outcomes"] if x.get("primary"))
    basics = next(t for t in o["trials"] if t["id"] == "PMID 34375394")
    assert basics["scale"] == "HR" and o["result"]["scale"] == "HR"          # served: HR pooled beside PLUS's counts
    assert ei.hr_route(basics, o["estimand"], o["trials"])["route"] == "TIME_TO_EVENT_SEPARATE"


def test_a_pool_of_hrs_alone_is_left_alone():
    o = next(x for x in _git_json("docs/reviews/omega3-cardiovascular-events/review.json")["outcomes"] if x.get("primary"))
    assert o["estimand"] == "RR" and all(t.get("scale") == "HR" for t in o["trials"])
    assert all(ei.hr_route(t, o["estimand"], o["trials"]) is None for t in o["trials"])


def _step():
    rev = _git_json("docs/reviews/corticosteroids-cap-mortality/review.json")
    o = next(x for x in rev["outcomes"] if x["name"].startswith("Hyperglyc"))
    recs = {str(r["id"]): r.get("abstract", "") for r in _git_json("cache/corticosteroids-cap-mortality/records.json")["records"]}
    return o, next(t for t in o["trials"] if t["id"] == "PMID 25608756"), recs


def test_plant_pre_fix_step_is_an_incompatible_or_and_the_pool_is_suppressed():
    o, t, _ = _step()
    assert (t["effect"], t["ci_low"], t["ci_high"], t["scale"]) == (1.96, 1.31, 2.93, "OR") and t["alternatives"] == []
    assert o["result"]["estmeasure"]["status"] == "incompatible"


def test_step_reconstructs_the_rr_from_its_held_counts_and_keeps_the_or():
    _, t, recs = _step()
    r = ei.reconstruct_from_counts(t, recs["25608756"], ["prednisone"], ["placebo"])
    assert r["state"] == "RECONSTRUCTED" and (r["ai"], r["n1i"], r["ci"], r["n2i"]) == (76, 392, 43, 393)
    assert r["rr"] == {"estimate": 1.772, "ci_low": 1.2526, "ci_high": 2.5066}                # the review's 1.772 (1.253-2.507)
    assert r["published_effect_retained"] == {"effect": 1.96, "ci_low": 1.31, "ci_high": 2.93, "scale": "OR"}


def test_step_reconstructs_with_the_topics_own_vocabulary():
    _, t, recs = _step()
    topic = _git_json("topics/corticosteroids-cap-mortality.json")
    interv = sorted(set(topic.get("intervention_terms") or []) | set(topic.get("intervention_class_terms") or []))
    assert ei.reconstruct_from_counts(t, recs["25608756"], interv, topic.get("comparator_terms") or [])["state"] == "RECONSTRUCTED"


def test_the_reconstruction_refuses_with_a_reason_it_never_guesses():
    _, t, recs = _step()
    r = ei.reconstruct_from_counts(t, recs["25608756"], ["dexamethasone"], ["placebo"])     # an arm term the sentence does not use
    assert r["state"] == "NOT_RECONSTRUCTED" and "vocabulary" in r["why"]
    bad = dict(t, source=t["source"].replace("76 [19%]", "76 [21%]"))
    assert "percentage" in ei.reconstruct_from_counts(bad, recs["25608756"], ["prednisone"], ["placebo"])["why"]


def test_endpoint_definitions_are_classified_not_assumed_compatible():
    o, _, _ = _step()
    classes = {t["id"]: ei.definition_class(t) for t in o["trials"]}
    assert classes["PMID 25608756"] == "INSULIN_REQUIRING" and classes["PMID 25688779"] == "DEFINITION_NOT_STATED_IN_QUOTATION"


# ------------------------------------------------------------------ COVID-corticosteroids: rate != risk; target from protocol;
# ------------------------------------------------------------------ outcome polarity; multi-arm shared control
from harness import extract, source_hierarchy   # noqa: E402

COVID = "corticosteroids-covid19-mortality"


def _covid():
    rev = _git_json(f"docs/reviews/{COVID}/review.json")
    o = next(x for x in rev["outcomes"] if x.get("primary"))
    recs = {str(r["id"]): r for r in _git_json(f"cache/{COVID}/records.json")["records"]}
    topic = _git_json(f"topics/{COVID}.json")
    interv = sorted(set(topic.get("intervention_terms") or []) | set(topic.get("intervention_class_terms") or [])
                    | {a for k, v in (topic.get("intervention_agents") or {}).items() for a in [k, *(v or [])]})
    return o, recs, interv, topic.get("comparator_terms") or []


def test_plant_pre_fix_recovery_rate_ratio_was_served_as_rr_and_moved_the_target_off_the_protocol():
    o, _, _, _ = _covid()
    assert o["estimand"] == "OR" and o["estimand_decision"]["target_scale"] == "RR" and o["estimand_decision"]["served_scale_changed"]
    t = o["trials"][0]
    assert t["scale"] == "RR" and "age-adjusted rate ratio, 0.83" in t["source"]


def test_a_rate_ratio_never_classifies_as_a_risk_ratio():
    e = extract.extract_effect("died within 28 days (age-adjusted rate ratio, 0.83; 95% confidence interval [CI], 0.75 to 0.93)")
    assert e.scale == "RATE_RATIO"
    from harness import estmeasure
    assert estmeasure.classify("RATE_RATIO")["canonical_estimand"] == "RATE_RATIO_FIRST_EVENT" != estmeasure.classify("RR")["canonical_estimand"]


def test_the_target_measure_comes_from_the_protocol_not_from_the_first_input():
    d = source_hierarchy.estimand_decision({"estimand": "OR"}, [{"effect": 0.83, "scale": "RATE_RATIO"}])
    assert d["target_scale"] == "OR" and d["served_scale_changed"] is False and d["protocol_measure_departures"] == ["RATE_RATIO"]
    d = source_hierarchy.estimand_decision({"estimand": "RR"}, [{"effect": 0.9, "scale": "HR"}])
    assert d["target_scale"] == "RR" and d["protocol_measure_departures"] == ["HR"]


def test_recovery_reconstructs_the_protocol_or_and_rr_from_held_counts():
    o, recs, interv, comp = _covid()
    t = o["trials"][0]
    r = ei.reconstruct_from_counts(t, recs["32678530"]["abstract"], interv, comp, "OR")
    assert (r["ai"], r["n1i"], r["ci"], r["n2i"]) == (482, 2104, 1110, 4321)
    assert r["or"] == {"estimate": 0.8596, "ci_low": 0.7606, "ci_high": 0.9716}                 # the review's OR
    assert ei.reconstruct_from_counts(t, recs["32678530"]["abstract"], interv, comp, "RR")["rr"] == {"estimate": 0.8918, "ci_low": 0.8123, "ci_high": 0.9791}


def test_plant_remap_cap_or_models_a_benefit_event_and_is_refused_for_a_death_pool():
    _, recs, _, _ = _covid()
    ab = recs["32876697"]["abstract"]
    clause = next(s for s in ab.split(". ") if "1.43 (95% credible interval, 0.91-2.27)" in s) + ". " + \
        next(s for s in ab.split(". ") if "odds of improvement" in s)
    row = {"effect": 1.43, "ci_low": 0.91, "ci_high": 2.27, "scale": "OR", "source": clause}
    assert ei.event_modelled(clause) == "BENEFIT_EVENT"
    assert ei.polarity_check(row, "28-day all-cause mortality", {})["state"] == "EVENT_POLARITY_MISMATCH"
    n = ei.polarity_check(row, "28-day all-cause mortality", {"polarity_normalisation": {"reciprocal_for_benefit_event": True}})
    assert n["state"] == "NORMALISED" and n["normalised"] == {"effect": 0.6993, "ci_low": 0.4405, "ci_high": 1.0989}
    assert ei.polarity_check({**row, "source": "482 died (22.9%) ... odds ratio 0.86"}, "28-day all-cause mortality", {})["state"] == "CONSISTENT"


# the REMAP-CAP arm counts below are the REVIEW'S (the held abstract gives only 30% / 26% / 33% over 137 / 146 / 101): a synthetic fixture
_ARMS = [{"id": "PMID 32876697#fixed", "trial_family_id": "PMID:32876697", "label": "REMAP-CAP fixed", "ai": 41, "n1i": 137, "ci": 33, "n2i": 99},
         {"id": "PMID 32876697#shock", "trial_family_id": "PMID:32876697", "label": "REMAP-CAP shock", "ai": 37, "n1i": 141, "ci": 33, "n2i": 99}]


def test_plant_two_arms_sharing_one_control_are_held_unless_a_rule_is_declared():
    out, held = ei.apply_multi_arm_rule([dict(a) for a in _ARMS], {})
    assert out == [] and held[0]["state"] == "MULTI_ARM_SHARED_CONTROL_UNDECLARED"


@pytest.mark.parametrize("rule,expected", [("COMBINE_ARMS", [(78, 278, 33, 99)]), ("SPLIT_CONTROL", [(41, 137, 16.5, 49.5), (37, 141, 16.5, 49.5)])])
def test_a_declared_multi_arm_rule_counts_the_control_once(rule, expected):
    out, held = ei.apply_multi_arm_rule([dict(a) for a in _ARMS], {"multi_arm_rule": rule})
    assert [(r["ai"], r["n1i"], r["ci"], r["n2i"]) for r in out] == expected and held == []
    assert sum(r["n2i"] for r in out) == 99                                                       # the control enters ONCE


def test_the_new_holds_reach_the_reader_with_their_own_codes():
    from harness import absence
    _, held = ei.apply_multi_arm_rule([dict(a) for a in _ARMS], {})
    assert absence.classify_reason(["mortality"], "", row=held[0])["reason_code"] == "MULTI_ARM_SHARED_CONTROL_UNDECLARED"


# ------------------------------------------------------------------ dapagliflozin HFpEF: counts under an HR target; k=1 CI provenance
from harness import synth   # noqa: E402

# PRESERVED-HF's HF events (9/162 vs 9/162) are the REVIEW'S counts: the held abstract reports KCCQ-CS and adverse events only, so
# the served row is (correctly) OUTCOME_NOT_IN_SOURCE for the held bytes. This is a synthetic fixture for the rule.
_PHF = {"id": "PMID 34711976", "label": "PRESERVED-HF", "ai": 9, "n1i": 162, "ci": 9, "n2i": 162}


def test_counts_under_an_hr_target_are_never_an_hr_and_never_enter_the_hr_primary():
    c = ei.count_only_under_hr(dict(_PHF), "HR", {})
    assert c["state"] == "CLINICAL_EVENT_COUNTS_RECOVERED_HR_NOT_ESTABLISHED" and c["is_hazard_ratio"] is False
    assert c["count_rr"] == {"estimate": 1.0, "ci_low": 0.4074, "ci_high": 2.4545} and c["allowed_in"] is None   # review: 1.000 (0.407-2.454)
    defined = {"secondary_count_analysis": {"definition": "HF hospitalisation or urgent HF visit, count-based RR"}}
    assert ei.count_only_under_hr(dict(_PHF), "HR", defined)["allowed_in"] == "SECONDARY_COUNT_ANALYSIS"
    assert ei.count_only_under_hr(dict(_PHF), "RR", {}) is None                               # an RR target is not this rule


def test_plant_the_served_k1_single_study_rr_carries_the_pm_hksj_token():
    rev = _git_json("docs/reviews/dapagliflozin-hfpef-hosp/review.json")
    res = next(o for o in rev["outcomes"] if o["name"] == "Adverse events")["result"]
    assert res["k"] == 1 and res["ci_provenance"].startswith("synth.pool:PM-tau2+HKSJ")        # the defect, in the served bytes


def test_k1_ci_provenance_names_the_single_study_wald_computation():
    r = synth.pool([synth.Study(label="AE", ai=44, n1i=162, ci=38, n2i=162, measure="RR")], scale="RR")
    assert (round(r.estimate, 6), round(r.ci_low, 6), round(r.ci_high, 6)) == (1.157895, 0.795441, 1.685505)
    assert r.ci_provenance == synth.CI_PROVENANCE_K1_RATIO and "HKSJ" not in r.ci_provenance.replace("no-HKSJ", "")
    two = synth.pool([synth.Study(label="a", ai=44, n1i=162, ci=38, n2i=162, measure="RR"),
                      synth.Study(label="b", ai=30, n1i=150, ci=35, n2i=150, measure="RR")], scale="RR")
    assert two.ci_provenance == synth.CI_PROVENANCE
    from harness import census
    assert synth.CI_PROVENANCE_K1_RATIO in census._VALID_CI_PROVENANCE and "made-up-token" not in census._VALID_CI_PROVENANCE


# ------------------------------------------------------------------ denosumab: double-zero; prefer the published model
_NAKAMURA = {"id": "Nakamura", "label": "Nakamura", "ai": 0, "n1i": 50, "ci": 0, "n2i": 50}   # synthetic: the review's double-zero trial


def test_double_zero_has_no_conventional_log_ratio_and_the_engine_refuses_pseudo_events():
    with pytest.raises(synth.DoubleZero):
        synth.Study(label="Nakamura", ai=0, n1i=50, ci=0, n2i=50).yi_vi()
    with pytest.raises(synth.DoubleZero):
        synth.Study(label="Nakamura", e1i=0, t1i=100, e2i=0, t2i=100).yi_vi()
    assert synth.zero_cell_state(0, 50, 0, 50) == "DOUBLE_ZERO"
    y, v = synth.Study(label="sens", ai=0, n1i=50, ci=0, n2i=50, zero_event_method="CC_0.5").yi_vi()   # ONLY when declared
    assert y == 0.0 and v > 0


def test_plant_pre_fix_engine_silently_gave_a_double_zero_study_pseudo_events():
    src = subprocess.run(["git", "show", f"{PINNED}:harness/synth.py"], cwd=ROOT, capture_output=True).stdout.decode()
    ns = {}
    exec(compile(src, "synth_prefix.py", "exec"), ns)
    y, v = ns["Study"](label="Nakamura", ai=0, n1i=50, ci=0, n2i=50).yi_vi()                      # no refusal: 0.5 in every cell
    assert y == 0.0 and v > 0


def test_a_double_zero_row_is_eligible_observed_and_reaches_the_reader():
    from harness import absence
    row = {"label": "Nakamura", "id": "Nakamura", "absent_kind": "observed_no_estimable_effect", "state": "DOUBLE_ZERO",
           "reason_code": "DOUBLE_ZERO", "endpoint_admissibility": "DOUBLE_ZERO", "eligible": True, "outcome_observed": True}
    assert absence.classify_reason(["fracture"], "", row=row)["reason_code"] == "DOUBLE_ZERO"


def test_a_single_zero_cell_correction_is_disclosed_on_the_row():
    """The one served single-zero row (COVID serious adverse events, a HARM) was already disclosed by harms.py -- a first claim that
    it was silent was wrong, and this test caught it. The pipeline now writes the same disclosure for EVERY outcome kind."""
    o = next(x for x in _git_json("docs/reviews/corticosteroids-covid19-mortality/review.json")["outcomes"] if x["name"].startswith("Serious"))
    t = next(x for x in o["trials"] if x["id"] == "PMID 34138478")
    assert (t["ai"], t["n1i"], t["ci"], t["n2i"]) == (1, 16, 0, 14)
    assert "0.5 continuity correction" in t["continuity_correction"]
    assert synth.zero_cell_state(t["ai"], t["n1i"], t["ci"], t["n2i"]) == "SINGLE_ZERO_CELL"


def _freedom():
    rev = _git_json("docs/reviews/denosumab-vertebral-fracture/review.json")
    ab = {str(r["id"]): r.get("abstract", "") for r in _git_json("cache/denosumab-vertebral-fracture/records.json")["records"]}["19671655"]
    return rev, ab


def test_freedom_published_estimates_are_kept_and_the_model_is_never_asserted_from_nothing():
    rev, ab = _freedom()
    for o in rev["outcomes"][:3]:
        t = o["trials"][0]
        assert t["selection_rule"] == "KEEP_REPORTED_EFFECT" and t["derivation"] == "reported"
        assert ei.published_model(t, ab)["model"] == "NOT_STATED_IN_HELD_TEXT"          # the abstract does not state MH / Cox


def test_a_typed_model_record_is_used_and_crude_counts_are_corroboration_only():
    rev, ab = _freedom()
    fr = dict(rev["outcomes"][0]["trials"][0], alternatives=[{"ai": 86, "n1i": 3702, "ci": 264, "n2i": 3691}],
              published_model={"model": "MANTEL_HAENSZEL+STRATIFIED (age)", "span": "age-stratified Mantel-Haenszel (FREEDOM full text)"})
    assert ei.published_model(fr, ab)["basis"] == "typed record"
    cor = ei.crude_corroboration(fr)
    assert cor["role"] == "CORROBORATION_ONLY" and cor["crude"] == {"estimate": 0.32479, "ci_low": 0.25573, "ci_high": 0.41249}
    assert fr["effect"] == 0.32                                                            # the published estimate is untouched


def test_a_documented_model_keeps_a_published_estimate_that_crude_counts_disagree_with():
    row = {"effect": 0.30, "ci_low": 0.20, "ci_high": 0.45, "scale": "RR", "source": "risk ratio 0.30 (Mantel-Haenszel, stratified by age)",
           "alternatives": [{"ai": 30, "n1i": 100, "ci": 50, "n2i": 100}]}
    assert ei.conflict_check(row, ei.model_documented(row))["resolution"] == "KEEP_DISCLOSED"
    bare = dict(row, source="risk ratio 0.30")
    assert ei.conflict_check(bare, ei.model_documented(bare))["resolution"] == "HOLD"


# ------------------------------------------------------------------ DPP-4: typed uncertainty; a one-sided / repeated bound never becomes a 95% CI
DPP4 = "dpp4-mace-t2d"


def _dpp4():
    rev = _git_json(f"docs/reviews/{DPP4}/review.json")
    o = next(x for x in rev["outcomes"] if x.get("primary"))
    recs = {str(r["id"]): r for r in _git_json(f"cache/{DPP4}/records.json")["records"]}
    return o, recs


def test_plant_pre_fix_examine_is_served_as_outcome_not_in_source():
    o, recs = _dpp4()
    row = next(a for a in o["declared_absent_trials"] if "23992602" in str(a["id"]))
    assert row["state"] == "OUTCOME_NOT_IN_SOURCE"
    assert "upper boundary of the one-sided repeated confidence interval, 1.16" in recs["23992602"]["abstract"]   # it IS reported


def test_examine_is_typed_one_sided_repeated_and_its_state_is_unresolved_not_absent():
    _, recs = _dpp4()
    s = ei.uncertainty_state(recs["23992602"]["abstract"])
    assert s["state"] == "UNCERTAINTY_REPRESENTATION_UNRESOLVED" and s["statement"] == "outcome reported; required uncertainty representation unresolved"
    assert s["ci"] == {"sidedness": "one-sided-upper", "repeated": True, "level": None, "bound": 1.16, "point": 0.96,
                       "text": "upper boundary of the one-sided repeated confidence interval, 1.16"}      # level: not stated in the abstract
    assert not ei.se_permitted(s["ci"])


@pytest.mark.parametrize("text,permitted", [
    ("hazard ratio, 1.02; 95% CI, 0.89 to 1.17", True),
    ("hazard ratio 0.9; repeated 95% confidence interval 0.8 to 1.1", False),
    ("hazard ratio, 0.96; upper boundary of the one-sided 99% confidence interval, 1.16", False),
])
def test_only_a_two_sided_non_repeated_interval_at_a_stated_level_supports_an_se(text, permitted):
    assert ei.se_permitted(ei.ci_representation(text)[0]) is permitted


def test_a_non_positive_lower_limit_is_never_logged_and_no_limit_is_reflected():
    for lo in (0, 0.0, -0.1):
        with pytest.raises(ValueError, match="non-positive ratio limit"):
            synth.Study(label="x", effect=0.96, ci_low=lo, ci_high=1.16).yi_vi()
    # a reflected lower limit (0.96**2/1.16) is exactly what must never be manufactured from a one-sided bound
    reflected = round(0.96 ** 2 / 1.16, 4)
    s = ei.uncertainty_state("hazard ratio, 0.96; upper boundary of the one-sided repeated confidence interval, 1.16")
    assert "lower" not in s["ci"] and str(reflected) not in json.dumps(s)


def test_examines_count_rr_is_a_different_measure_and_needs_denominators_the_abstract_does_not_hold():
    _, recs = _dpp4()
    ab = recs["23992602"]["abstract"]
    sent = next(x for x in ab.split(". ") if "305 patients assigned to alogliptin" in x)
    r = ei.reconstruct_from_counts({"source": sent}, ab, ["alogliptin"], ["placebo"], "RR")
    assert r["state"] == "NOT_RECONSTRUCTED"                              # per-arm n (2701 / 2679) are in the full text, not held
    fixture = ei.counts_tuple(305, 2701, 316, 2679, "RR")                # the review's counts: a synthetic fixture
    assert (round(fixture["estimate"], 4), round(fixture["ci_low"], 4), round(fixture["ci_high"], 4)) == (0.9573, 0.8257, 1.11)
