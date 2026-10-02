"""PLANTS for the tracker defects found by the cross-vendor reviews of 3 Oct (codex 8, agy/Gemini 2: one agy finding
refuted -- its excerpt lacked as_row) and by the 31-topic batch (an MD trial pooled from arm means read as 'not pooled').
Each test is the reproduction, asserting the requirement."""
import os
import sys

from harness import secondary_meta as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_tracker as gt  # noqa: E402

MORT = "28-day all-cause mortality"


def test_registry_binding_needs_the_outcome_named_not_just_no_extra_component():
    # a mortality topic must not bind 'Death or mechanical ventilation' merely because it is the PRIMARY outcome
    v = gt.binding_verdict(MORT, ["28-day mortality", "all-cause mortality", "death"], "Death or Mechanical Ventilation",
                           2, is_primary=True)
    assert v["verdict"] == "REFUSED" and v["gate"] == "ESTIMAND"
    v = gt.binding_verdict(MORT, ["28-day mortality", "all-cause mortality"], "Time to Recovery", 2, is_primary=True)
    assert v["verdict"] == "REFUSED" and v["gate"] == "OUTCOME_NOT_NAMED"
    v = gt.binding_verdict(MORT, ["all-cause mortality"], "All-cause Mortality at Day 28", 2, is_primary=False)
    assert v["verdict"] == "BINDABLE"


def test_one_estimand_refusal_does_not_name_a_trial_whose_matching_outcome_failed_elsewhere():
    x = {"registry_binding": {"state": "REFUSED", "candidates": [
        {"gate": "ESTIMAND", "verdict": "REFUSED", "reason": "4-point", "title": "4P", "arms": [], "analysis": None,
         "snapshot": {}},
        {"gate": "ARMS", "verdict": "REFUSED", "reason": "one group", "title": "3P MACE", "arms": [], "analysis": None,
         "snapshot": {}}]}}
    assert gt.scope_difference(x, {}, "s") is None


def test_a_screened_out_trial_is_never_named_by_the_estimand_path():
    est = {"state": "REFUSED", "candidates": [{"gate": "ESTIMAND", "verdict": "REFUSED", "reason": "r", "title": "t",
                                               "arms": [], "analysis": None, "snapshot": {}}]}
    for f in ({"stage": "SCREENED_OUT", "rule_id": "X2", "pmid": "999999999"},     # unaudited
              {"stage": "SCREENED_OUT", "rule_id": None, "pmid": "999999999"}):    # no rule id (agy)
        assert gt.scope_difference({"seeded_funnel": f, "registry_binding": est}, {}, "no-such-topic") is None


def test_agreement_on_counts_requires_the_same_measure():
    theirs = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="A",
                             measure="HR", outcome_definition="", effect="0.90", lower="0.80", upper="1.01",
                             events_t=10, n_t=100, events_c=20, n_c=100)
    ours = {"measure": "RR", "events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100}
    assert gt.agreement(ours, theirs).startswith("NOT_COMPARABLE")


def test_verdict_is_decided_on_unrounded_intervals():
    assert gt.result_verdict({"estimate": -0.1, "ci_low": -0.2, "ci_high": -0.00001},
                             {"estimate": -0.1, "ci_low": -0.2, "ci_high": 0.00001}, "MD")["verdict"] == \
        "DIFFERENT_CONCLUSION"
    seen = []
    real = gt.result_verdict
    gt.result_verdict = lambda o, t, m: seen.append((o, t)) or real(o, t, m)
    try:
        a = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="A",
                            measure="MD", outcome_definition="", effect="-0.123456", lower="-0.2", upper="-0.046912")
        gt.same_trials_pool([(a, a), (a, a)], "FE")
    finally:
        gt.result_verdict = real
    o, _ = seen[0]
    assert o["estimate"] != round(o["estimate"], 4)          # the verdict saw the UNROUNDED pool, not the display


def test_a_row_with_neither_effect_nor_counts_is_not_poolable_and_does_not_crash():
    r = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="A",
                        measure="RR", outcome_definition="")
    assert sm.row_yi_vi(r) is None


def test_pooled_membership_does_not_depend_on_the_value_format():
    # esketamine: an MD trial pooled from arm means carries no effect+CI and no 2x2 -> it read as 'not in our pool'
    assert gt.is_pooled({"id": "PMID 1", "primary": None}, {"PMID 1"})
    assert not gt.is_pooled({"id": "PMID 2", "primary": {"effect": "1"}}, {"PMID 1"})
    assert not gt.is_pooled(None, {"PMID 1"})


def test_the_seeded_report_is_the_result_typed_pmid_not_pmids_0():
    t = {"pmids": ["111", "222"], "ncts": [], "label": "X"}
    assert gt.report_pmid(t, shown=lambda r: "222") == "222"
    assert gt.report_pmid({"pmids": ["111"], "ncts": [], "label": "X"}, shown=lambda r: None) == "111"


def test_our_counts_are_compared_with_the_comparators_printed_ratio():
    # COPPS-2 (colchicine-postop-af): ours 61/180 vs 75/180 (RR 0.81); the comparator prints RR 0.66 (0.45-0.96)
    theirs = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="I",
                             measure="RR", outcome_definition="", effect="0.66", lower="0.45", upper="0.96")
    ours = {"measure": "RR", "events_t": 61, "n_t": 180, "events_c": 75, "n_c": 180}
    assert gt.agreement(ours, theirs) == "DISAGREE:our_counts_imply_0.81_vs_printed_0.66"
    theirs.effect = "0.81"
    assert gt.agreement(ours, theirs) == "AGREE_ON_POINT"


def _o(**kw):
    o = {"N_eligible": 2, "k_matched": 2, "open_gaps": [], "named_differences": [],
         "same_trials": {"verdict": {"verdict": "AGREE"}},
         "trials": [{"label": "A", "in_our_pool": True, "route": "PRIMARY", "agreement_with_comparator_row": "AGREE"},
                    {"label": "B", "in_our_pool": True, "route": "PRIMARY", "agreement_with_comparator_row": "AGREE"}]}
    o.update(kw)
    return o


def test_g1_matched_needs_every_criterion():
    assert gt.g1_status(_o())["state"] == "G1_MATCHED"
    assert gt.g1_status(_o(k_matched=1, open_gaps=["B"]))["unmet"] == ["ALL_ELIGIBLE_MATCHED"]
    assert gt.g1_status(_o(same_trials={"state": "FEWER_THAN_2_SHARED_TRIALS"}))["unmet"] == ["RESULT_AGREES"]
    o = _o()
    o["trials"][1]["route"] = "UNVERIFIED"
    assert gt.g1_status(o)["unmet"] == ["MATCHED_ARE_VERIFIED"]
    o = _o(named_differences=[{"trial": "C", "kind": "PROTOCOL_SCOPE_DIFFERENCE", "protocol_rule": None}])
    assert gt.g1_status(o)["unmet"] == ["DIVERGENCES_NAMED"]          # a named difference must cite its rule or gate
    o = _o()
    o["trials"][0]["agreement_with_comparator_row"] = "DISAGREE:our_counts_imply_0.81_vs_printed_0.66"
    assert gt.g1_status(o)["unmet"] == ["DIVERGENCES_NAMED"]          # a disagreement needs its side established
    o["trials"][0]["disagreement_side"] = "SECONDARY_WRONG"
    assert gt.g1_status(o)["state"] == "G1_MATCHED"


def test_the_comparators_own_row_never_gives_an_unpooled_trial_a_counted_route():
    # ELIXA: the comparator's 4-point row, verified against ELIXA's own text, made the trial route PRIMARY -> counted
    import json
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "glp1-ra-mace-t2d.json"), encoding="utf-8"))
    elixa = next(x for x in o["trials"] if x["label"] == "ELIXA")
    assert not elixa["in_our_pool"] and elixa["route"] not in ("PRIMARY", "TWO_SOURCE") and not elixa["g1_countable"]
    assert any(f["finding"] == "COMPARATOR_POOLED_A_DIFFERENT_ESTIMAND" and f["trial"] == "ELIXA"
               for f in o["comparator_findings"])


def test_a_year_glued_to_an_acronym_still_joins_the_family():
    # the forest reader's spironolactone rows are labelled 'RALES2000', 'EMPHASIS-HF2011': 0 of 3 joined
    import secondary_meta_build as smb
    ours = [{"id": "PMID 10471456", "acronyms": ["RALES"], "label": "RALES", "author_year": None},
            {"id": "PMID 21073363", "acronyms": ["EMPHASIS-HF"], "label": "EMPHASIS-HF", "author_year": None}]
    fam = smb.family_of_factory(ours)
    row = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T",
                          trial_label="RALES2000", measure="HR", outcome_definition="")
    assert fam(row) == "PMID 10471456"
    row.trial_label = "EMPHASIS-HF2011"
    assert fam(row) == "PMID 21073363"


def test_a_comparator_citing_another_report_of_a_trial_we_pool_is_matched_to_that_pool_row():
    # sglt2-primary-prevention: the comparator cites Radholm 2018 (CANVAS heart-failure outcomes, PMID 29526832, no NCT
    # in its row); our pool holds CANVAS under Neal 2017 (PMID 28605608), same NCT01032629. Matched -- once, to that row.
    import json
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "sglt2-primary-prevention-hf.json"), encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"].startswith("Radholm"))
    assert x["in_our_pool"] and x["route"] == "PRIMARY"
    assert x["matched_via_other_report"] == {"nct": "NCT01032629", "pool_row": "PMID 28605608", "comparator_cites": "29526832"}
    assert "PMID 28605608" not in o["ours_not_in_comparator"]
    fams = [t.get("family") for t in o["trials"] if t["in_our_pool"]]
    assert len(fams) == len(set(fams))                 # one pool row never matches two comparator trials
