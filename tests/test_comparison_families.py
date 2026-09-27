"""Comparison-level families and recovered rows (V1.0.1), from the CAP- and COVID-corticosteroids reviews. Written
BEFORE harness/comparison_family.py and harness/acquisition_state.py.

REMAP-CAP (NCT02735707) was rejected in the CAP review because its REGISTRATION lists COVID-19 among its conditions;
the relevant report is the NON-pandemic corticosteroid domain, whose own exclusion criteria exclude known or presumed
COVID-19. COVIDICUS's comparator changed mid-trial (placebo, then standard-dose dexamethasone). Recovered rows:
CoDEX 28-day 85/151 vs 91/148 (Table 2, a secondary outcome), CAPE COVID deaths at DAY 21 (never substituted for 28),
METCOVID (mITT main table; ITT in a supplement; neither held). SONIA: open-label is RoB, not an exclusion.
"""
import copy
import json
import os

import pytest

from harness import fetch, pipeline

ROOT = pipeline.ROOT
CAP, COVID, FIN = "corticosteroids-cap-mortality", "corticosteroids-covid19-mortality", "finerenone-ckd-t2d-renal"


def _cf():
    from harness import comparison_family
    return comparison_family


def _config(slug):
    return json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))


_SCR = {}


def _screen(slug):
    if slug not in _SCR:
        config = _config(slug)
        _SCR[slug] = pipeline.outcome_inputs(slug, config, fetch.ensure(config, ""))
    return {str(d["id"]): d for d in _SCR[slug]["scr"]["decisions"]}


def _row(slug, nct):
    return next(d for k, d in _screen(slug).items() if nct in k)


# ------------------------------------------------------------------------------------------------ REMAP-CAP
def test_remap_cap_is_screened_per_domain_and_awaits_classification():
    d = _row(CAP, "NCT02735707")
    assert d["decision"] == "awaiting_classification" and d["rule_id"] == "A-COMPARISON-UNRESOLVED"
    assert "covid" not in d["reason"].lower().split("pending")[0] or "X2" != d["rule_id"]
    assert [p["decision"] for p in d["pending_decisions"]] == ["MIXED_POPULATION_STRATUM", "TIMEPOINT", "ADJUSTED_ESTIMATE"]
    assert d["screening_record"]["parent_eligibility"]["state"] == "UNRESOLVED"


def test_the_covid_label_is_carried_by_the_covid_domain_only():
    comps = {c["comparison_id"]: c for c in _row(CAP, "NCT02735707")["comparisons"]}
    npd = comps["REMAP-CAP:non-pandemic-corticosteroid:fixed-duration-hydrocortisone-vs-control"]
    assert npd["eligibility"] == "UNRESOLVED" and npd["fails"] == []
    assert comps["REMAP-CAP:COVID-19-corticosteroid"]["eligibility"] == "INELIGIBLE"


def test_registration_condition_labels_never_decide_a_declared_comparison():
    cf = _cf()
    rec = {"id": "NCT02735707", "id_type": "nct", "title": "REMAP-CAP", "conditions": ["COVID-19", "Influenza"]}
    a = cf.screen_registration(rec, _config(CAP))
    b = cf.screen_registration({**rec, "conditions": []}, _config(CAP))
    assert (a["decision"], a["rule_id"]) == (b["decision"], b["rule_id"]) == ("awaiting_classification", "A-COMPARISON-UNRESOLVED")


def test_a_tampered_witness_or_a_declared_timepoint_the_span_does_not_state_fails_closed(tmp_path):
    cf = _cf()
    fam = copy.deepcopy(cf.load(ROOT)[0])
    comp = fam["comparisons"][0]
    comp["population"]["witness"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="digest mismatch"):
        cf.evaluate(ROOT, comp, _config(CAP))
    comp = copy.deepcopy(cf.load(ROOT)[0]["comparisons"][0])
    comp["primary_timepoint"]["days"] = 28
    with pytest.raises(ValueError, match="not what its witnessed span states"):
        cf.evaluate(ROOT, comp, _config(CAP))


def test_a_declaration_cannot_add_a_term_its_span_does_not_contain():
    cf = _cf()
    comp = copy.deepcopy(cf.load(ROOT)[0]["comparisons"][0])
    comp["population"]["text"] = "patients with severe community-acquired pneumonia and influenza"
    out = cf.evaluate(ROOT, comp, _config(CAP))
    assert "influenza" not in (out["population"] or "")


# ------------------------------------------------------------------------------------------------ COVIDICUS
def test_covidicus_comparisons_by_recruitment_period():
    d = _row(COVID, "NCT04344730")
    assert d["decision"] == "include"
    comps = {c["comparison_id"]: c for c in d["comparisons"]}
    p1 = comps["COVIDICUS:P1:high-dose-dexamethasone-vs-placebo"]
    p2 = comps["COVIDICUS:P2:high-dose-vs-standard-dose-dexamethasone"]
    assert p1["eligibility"] == "ELIGIBLE" and p1["arms"] == {"high-dose dexamethasone": 36, "placebo": 37}
    assert [p["decision"] for p in p1["primary_pool_pending"]] == ["TIMEPOINT"]
    assert p1["result_state"] == "DISCOVERED_NOT_RETRIEVED"
    assert p2["eligibility"] == "INELIGIBLE" and p2["fails"][0]["rule"] == "X3" and "active dose" in p2["fails"][0]["why"]


def test_a_whole_trial_result_spanning_comparators_is_never_pooled():
    cf = _cf()
    keep, absent = cf.hold_whole_trial(COVID, "28-day all-cause mortality",
                                       [{"id": "NCT04344730", "effect": 0.96, "ci_low": 0.69, "ci_high": 1.33},
                                        {"id": "PMID 32678530", "effect": 0.83}])
    assert [t["id"] for t in keep] == ["PMID 32678530"]
    assert absent[0]["reason_code"] == "WHOLE_TRIAL_ACROSS_COMPARISONS" and absent[0]["held_out_row"]["effect"] == 0.96


# ------------------------------------------------------------------------------------------------ undeclared platforms
def test_undeclared_platforms_keep_their_own_rules_but_not_their_condition_labels():
    assert (_row(COVID, "NCT04746430")["rule_id"], _row(COVID, "NCT04488081")["rule_id"]) == ("X3", "X3")
    d = _row(FIN, "NCT07594145")
    assert d["decision"] == "awaiting_classification" and d["rule_id"] == "A-PLATFORM-DOMAINS-UNDECLARED"


def test_an_undeclared_platform_whose_own_title_names_an_excluded_population_is_still_excluded():
    cf = _cf()
    rec = {"id": "NCT00000001", "id_type": "nct", "title": "Adaptive platform trial in COVID-19 pneumonia"}
    assert cf.undeclared_platform_population(rec, ("exclude", "X2", "wrong population", ""), _config(CAP)) is None
    rec2 = {**rec, "title": "Adaptive platform trial in severe pneumonia"}
    assert cf.undeclared_platform_population(rec2, ("exclude", "X2", "wrong population", ""), _config(CAP))["rule_id"] \
        == "A-PLATFORM-DOMAINS-UNDECLARED"


# ------------------------------------------------------------------------------------------------ recovered rows
_OUT = {}


def _covid_primary():
    if "o" not in _OUT:
        config = _config(COVID)
        _screen(COVID)
        spec, kind = next((s, k) for s, k in pipeline._outcome_specs(config) if s.get("primary"))
        _OUT["o"] = pipeline.build_outcome_from_inputs(_SCR[COVID], spec, kind, COVID)
    return _OUT["o"]


def test_codex_28_day_row_is_bound_to_table_2_with_its_timepoint():
    row = next(t for t in _covid_primary()["trials"] if t["id"] == "PMID 32876695")
    assert (row["ai"], row["n1i"], row["ci"], row["n2i"]) == (85, 151, 91, 148)
    assert row["hand_binding_state"] == "BOUND" and row["timepoint"] == "28 days"
    assert row["endpoint_role_in_trial"] == "SECONDARY"


def test_a_timepoint_span_not_in_the_same_document_is_refused(tmp_path):
    from harness import verified_inputs as vi
    d = tmp_path / "cache" / "x"
    d.mkdir(parents=True)
    (d / "records.json").write_text(json.dumps({"records": [{"id": "1", "abstract": "At day 28, 5 of 10 died."}]}))
    (d / "verified_arms.json").write_text(json.dumps({"1": {
        "outcome": "m", "ai": 5, "n1i": 10, "ci": 1, "n2i": 10, "kind": "extracted_counts",
        "document_ref": "records.json", "source_span": "5 of 10 died", "timepoint": "28 days",
        "timepoint_span": "Day 90 results"}}))
    with pytest.raises(ValueError, match="timepoint_span absent"):
        vi.load("x", cache_root=str(tmp_path / "cache"))


def test_cape_covid_day_21_is_never_silently_substituted_for_day_28():
    o = _covid_primary()
    assert "PMID 32876689" not in [t["id"] for t in o["trials"]]
    a = next(x for x in o["declared_absent_trials"] if x["id"] == "PMID 32876689")
    assert (a.get("reason_code") or a.get("state") or a.get("provenance")) == "TIMEPOINT_MISMATCH" \
        or "TIMEPOINT_MISMATCH" in json.dumps(a)
    assert "DAY 21" in a["reason"] and "window policy" in a["reason"]


def test_metcovid_carries_its_acquisition_state():
    a = next(x for x in _covid_primary()["declared_absent_trials"] if x["id"] == "PMID 32785710")
    assert a["acquisition_state"]["states"] == ["MAIN_RESULT_NOT_HELD", "PROTOCOL_PREFERRED_ANALYSIS_IN_SUPPLEMENT",
                                                "SUPPLEMENT_NOT_HELD"]


def test_sonia_primary_row_is_found_and_open_label_is_rob_not_exclusion():
    from harness import provenance_tiers as pt
    kem = json.load(open(os.path.join(ROOT, "docs", "known_eligible_missing.json"), encoding="utf-8"))
    s = next(r for r in kem["topics"][CAP] if r["trial"] == "SONIA")
    trial = {"trial": "SONIA", "arm_sizes": [1089, 1091]}
    target = {"outcome": "All-cause mortality", "row_label_must_match": "died|mortality"}
    c = [{"trial": "SONIA", "tier": pt.PRIMARY, "where": "text", "sentence": s["acquisition"]["primary_row_span"],
          "document": s["acquisition"]["held_path"], "document_sha256": s["acquisition"]["held_sha256"]}]
    r = pt.evaluate(trial, target, c)
    assert r["status"] == "FOUND_PRIMARY" and r["served_counts"] == [[246, 1089], [284, 1091]]
    assert "RISK-OF-BIAS" in s["design_note"] and _config(CAP)["include"]["design_double_blind"] is False


def test_prisma_flow_shows_awaiting_classification_and_the_comparisons():
    from harness import page
    rev = {"screening": {"records": [{"id": "NCT02735707", "decision": "awaiting_classification",
                                      "rule_id": "A-COMPARISON-UNRESOLVED", "reason": "r", "span": "s"}]},
           "outcomes": [], "comparison_families": [{"registration": "NCT02735707", "decision": "awaiting_classification",
                                                    "rule_id": "A-COMPARISON-UNRESOLVED", "comparisons": [
                                                        {"comparison_id": "X:domain", "population": "p", "eligibility": "UNRESOLVED",
                                                         "primary_pool_eligibility": "UNRESOLVED",
                                                         "primary_pool_pending": [{"decision": "TIMEPOINT", "detail": "d"}]}]}]}
    html = page._screening(rev, False)
    assert "Awaiting classification" in html and "data-comparison='X:domain'" in html and "pending TIMEPOINT" in html


def test_the_served_reviews_carry_the_comparison_tables():
    # the ledger copies screening rows through a key whitelist; a hand-built review cannot catch a key it drops
    for slug, reg in ((CAP, "NCT02735707"), (COVID, "NCT04344730")):
        rev = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
        fams = {f["registration"].split(" · ")[-1]: f for f in rev.get("comparison_families") or []}
        assert reg in fams and len(fams[reg]["comparisons"]) == 2, slug
        html = open(os.path.join(ROOT, "docs", "reviews", slug, "index.html"), encoding="utf-8").read()
        assert "data-comparison=" in html, slug


@pytest.mark.parametrize("slug", ["corticosteroids-cap-mortality", "corticosteroids-covid19-mortality",
                                  "dapagliflozin-hfpef-hosp", "doac-vte-recurrence", "denosumab-vertebral-fracture"])
def test_new_renderers_do_not_depend_on_dict_key_order(slug):
    # the census renders the in-memory core and its canonical (sorted-key) JSON and requires equal bytes; the comparison,
    # multi-trial, acquisition-state and version-chain renderers once iterated dicts in insertion order and failed it
    from harness.canonical import canonical_json
    from harness.page import render_page
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    rev.pop("reproduction", None)

    def reverse_keys(x):
        if isinstance(x, dict):
            return {k: reverse_keys(x[k]) for k in reversed(list(x))}
        if isinstance(x, list):
            return [reverse_keys(v) for v in x]
        return x
    assert render_page(reverse_keys(rev)) == render_page(json.loads(canonical_json(rev)))
