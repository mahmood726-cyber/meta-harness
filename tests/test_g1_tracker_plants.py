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
    # the REQUIREMENT: matched, once, to the CANVAS pool row. The route may be direct (since 4 Oct Radholm's own PubMed
    # record supplies NCT01032629) or via the other-report join; when it is the latter, its record must say so exactly.
    assert x["in_our_pool"] and x["route"] == "PRIMARY" and x["family"] == "PMID 28605608"
    if "matched_via_other_report" in x:
        assert x["matched_via_other_report"] == {"nct": "NCT01032629", "pool_row": "PMID 28605608", "comparator_cites": "29526832"}
    assert "PMID 28605608" not in o["ours_not_in_comparator"]
    fams = [t.get("family") for t in o["trials"] if t["in_our_pool"]]
    assert len(fams) == len(set(fams))                 # one pool row never matches two comparator trials


def test_the_screens_own_dedup_verdict_joins_a_comparator_trial_to_the_pooled_registration():
    # esketamine Trial D (PMID 31734084) was screened out X-DEDUP 'companion/duplicate report of TRANSFORM-3
    # (NCT02422186, already pooled)': the same trial; matched to the NCT02422186 pool row
    import json
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "esketamine-trd-madrs.json"), encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"].startswith("Trial D"))
    assert x["in_our_pool"] and x["matched_via_other_report"]["pool_row"] == "NCT02422186"
    assert "NCT02422186" not in o["ours_not_in_comparator"]


def test_a_comparator_only_row_never_stops_our_screen_from_seeing_the_trials_record():
    # OSLER-1 (pcsk9-mace, 3 Oct): the forest-reader dual read gave it a COMPARATOR-only row (route UNVERIFIED); the
    # seeding pass ran only for route NO_ROW, so our screen never saw its record and its spanned X3 exclusion vanished
    # (eligible 11 -> 12). Whether our screen sees a record is independent of what the comparator printed.
    unverified = {"in_our_pool": False, "route": "UNVERIFIED", "seeded_funnel": None}
    assert gt.needs_seed(unverified)
    assert gt.needs_seed({"in_our_pool": False, "route": "NO_ROW", "seeded_funnel": None})
    assert not gt.needs_seed({"in_our_pool": True, "route": "PRIMARY", "seeded_funnel": None})
    assert not gt.needs_seed({"in_our_pool": False, "route": "NO_ROW", "seeded_funnel": {"stage": "SCREENED_OUT"}})


def test_a_different_number_on_the_other_side_of_the_null_is_not_a_mirrored_orientation():
    # probiotics 4 Oct: Pozzoni -- another meta prints RR 1.14 [0.58, 2.24], the comparator 0.75 [0.38, 1.48] (13/106 vs
    # 16/98; its reciprocal is 1.33 [0.68, 2.63]). A discrepancy, not swapped arms: it must not DISPUTE an orientation
    # 13 shared trials establish (25 comparator rows were refused for it).
    ours = {"measure": "RR", "effect": "1.14", "lower": "0.58", "upper": "2.24"}
    theirs = {"measure": "RR", "effect": "0.75", "lower": "0.38", "upper": "1.48", "events_t": 13, "n_t": 106,
              "events_c": 16, "n_c": 98}
    assert not gt._mirrors(ours, theirs)
    # a TRUE mirror: the comparator printed the reciprocal (arms swapped)
    assert gt._mirrors({"measure": "RR", "effect": "1.33", "lower": "0.68", "upper": "2.63"}, theirs)
    assert gt._mirrors({"measure": "RR", "events_t": 16, "n_t": 98, "events_c": 13, "n_c": 106}, theirs)
    # differences: negated vs merely different
    assert gt._mirrors({"measure": "MD", "effect": "-17.4", "lower": "-25.0", "upper": "-9.8"},
                       {"measure": "MD", "effect": "17.4", "lower": "9.8", "upper": "25.0"})
    assert not gt._mirrors({"measure": "MD", "effect": "-17.4", "lower": "-25.0", "upper": "-9.8"},
                           {"measure": "MD", "effect": "8.9", "lower": "1.0", "upper": "16.8"})


def _r(label, comp="C"):
    return sm.SecondaryRow(meta_pmid=comp, meta_doi="", location={}, source_digest="", provenance="", trial_label=label,
                           measure="OR", outcome_definition="", effect="1.2", lower="0.9", upper="1.6")


def test_outcome_set_naming_needs_the_figure_to_be_the_compared_analysis():
    # metformin 4 Oct: the accepted figure pools OR 1.65 [1.35, 2.03] (21 studies) while the compared comparator result
    # is OR 2.64 [1.85, 3.75] -- another analysis; its trial set says nothing about the compared result's. A lane-read
    # comparator (forest-reader ACCEPTED) whose figure IS the compared result names the trials it does not contain.
    src = [{"branch": "g1/forest-reader", "commit": "e1543f18e8", "sha256": "d6937e9dbe7a", "figure": "F1",
            "acceptance": {"state": "ACCEPTED", "methods_reproducing": ["MH-FE"], "pooled_anchor": "PRINTED_IN_META_TEXT"},
            "pooled_agreed": {"effect": "1.65", "lower": "1.35", "upper": "2.03"}}]
    cm = gt.lane_comp_meta(src)
    assert cm["usable"] and cm["positive_control"]["reproduced"] and cm["pooled"]["effect"] == "1.65"

    def trials():
        return [{"label": "A", "in_our_pool": False, "comparator_row": {"effect": "1.2"}},
                {"label": "B", "in_our_pool": False, "comparator_row": None}]
    rows = [_r("A")]
    t = trials()
    assert gt.outcome_set_differences(t, cm, "C", rows, compared={"estimate": 1.65, "ci_low": 1.35, "ci_high": 2.03}) == ["B"]
    assert t[1]["scope_difference"]["rule_id"] == "G1-OUTCOME-SET"
    t = trials()
    assert gt.outcome_set_differences(t, cm, "C", rows, compared={"estimate": 2.64, "ci_low": 1.85, "ci_high": 3.75}) == []
    assert not t[1].get("scope_difference")


def test_one_comparator_row_joins_one_comparator_trial():
    # ticagrelor 4 Oct: 'Wallentin 2009' (PLATO) was the row of BOTH '9 [28]' (PLATO) and '1 [21]' (Cannon 2010, a PLATO
    # substudy sharing its NCT): the family route handed the family's row to both, 'Cannon 2010' stayed unjoined.
    plato, cannon = _r("Wallentin 2009"), _r("Cannon 2010")
    owner = {id(plato): "9 [28]", id(cannon): "1 [21]"}
    used = set()
    assert gt.pick_comparator_row([plato], "C", "9 [28]", owner, used, None) is plato
    used.add(id(plato))
    # '1 [21]' shares PLATO's family: the family row is owned by another trial and used -> its own label row
    assert gt.pick_comparator_row([plato], "C", "1 [21]", owner, used, cannon) is cannon
    # no label row of its own: nothing, never the other trial's row
    assert gt.pick_comparator_row([plato], "C", "1 [21]", owner, used, None) is None


def test_a_trial_whose_report_is_in_the_analysis_is_never_named_absent_from_it():
    # balanced-crystalloids 4 Oct: the comparator lists SMART twice ('Semler (SMART trial)', 'Semler [15]', both PMID
    # 29485925); the SMART row joins the first, and G1-OUTCOME-SET named the second 'not in the analysis'
    cm = {"usable": True, "positive_control": {"reproduced": True, "methods": ["DL"]}, "figure": "F", "pooled": None}
    t = [{"label": "Semler (SMART trial)", "family": "PMID 29485925", "in_our_pool": False, "comparator_row": {"e": 1}},
         {"label": "Semler [15]", "family": "PMID 29485925", "in_our_pool": False, "comparator_row": None},
         {"label": "Ratanarat [18]", "family": None, "in_our_pool": False, "comparator_row": None}]
    assert gt.outcome_set_differences(t, cm, "C", [_r("Semler (SMART trial) 2018")]) == ["Ratanarat [18]"]
    assert not t[1].get("scope_difference") and t[1]["same_report_as"] == "Semler (SMART trial)"


def test_a_row_refused_only_for_our_identity_bookkeeping_is_admissible_comparator_coverage():
    # omega3 4 Oct: GISSI-P, GISSI-HF, ORIGIN, Risk & Prevention, ASCEND -- the comparator's own rows, joined to the
    # comparator's own trials by its labels, refused ONLY 'FAMILY_NOT_RESOLVED' (our identity, not the typed tuple)
    base = {"label": "ORIGIN 2012 [40]", "in_our_pool": False, "route": "UNVERIFIED",
            "comparator_row": {"measure": "RR", "effect": "1.01", "lower": "0.94", "upper": "1.10"},
            "comparator_row_provenance": {"meta_pmid": "C", "location": {"kind": "figure", "id": "F2"}, "digest": "d",
                                          "read": "MODEL_PROPOSAL:mc-x", "row_label": "ORIGIN 2012"}}
    ok, why = gt.comparator_sourced(dict(base, comparator_row_state="REFUSED", comparator_row_reasons=["FAMILY_NOT_RESOLVED"]),
                                    "REPRODUCED", "ESTABLISHED")
    assert ok and why is None
    # any TYPED refusal (measure / outcome / timepoint) still refuses
    ok, why = gt.comparator_sourced(dict(base, comparator_row_state="REFUSED",
                                         comparator_row_reasons=["FAMILY_NOT_RESOLVED", "OUTCOME_NOT_THE_TOPICS"]),
                                    "REPRODUCED", "ESTABLISHED")
    assert ok is None and why == "COMPARATOR_ROW_REFUSED"


def test_a_reference_number_label_takes_its_author_year_from_the_comparators_own_reference_list():
    # ticagrelor 4 Oct: the comparator's trial '10 [29]' has no PMID; its forest row 'Liu 2014' never joined, so the
    # comparator's MACE analysis was never complete and its outcome-set rule never ran
    refs = {"r29": {"label": "29", "ordinal": 29, "first_author": "Liu", "year": "2014", "pmid": None},
            "r30": {"label": "30", "ordinal": 30, "first_author": "Wang", "year": "2014", "pmid": None}}
    assert gt.ref_author_year("10 [29]", refs) == ("liu", "2014")
    assert gt.ref_author_year("11 [30]", refs) == ("wang", "2014")
    assert gt.ref_author_year("12 [99]", refs) is None              # a number the list does not carry: nothing


def test_a_row_of_the_comparators_other_agent_trial_is_accounted_for_in_completeness():
    # semaglutide-mace 4 Oct: the comparator's MACE figure (pool = the compared 0.79 [0.71, 0.89]) carries SCALE /
    # SURMOUNT rows -- the comparator's own trials of OTHER agents, never in our trial list -- so 'every row joined'
    # never held and the STEP trials absent from the figure were never named
    cm = {"usable": True, "positive_control": {"reproduced": True, "methods": ["DL"]}, "figure": "F", "pooled": None}
    t = [{"label": "SELECT", "family": "P1", "in_our_pool": False, "comparator_row": {"e": 1}},
         {"label": "STEP 3", "family": "P3", "in_our_pool": False, "comparator_row": None}]
    rows = [_r("SELECT, 2023"), _r("SCALE Maintenance, 2013"), _r("SURMOUNT-1, 2022")]
    assert gt.outcome_set_differences([dict(x) for x in t], cm, "C", rows) == []
    assert gt.outcome_set_differences(t, cm, "C", rows, accounted_other=2) == ["STEP 3"]


def test_a_registry_title_names_our_outcome_in_its_own_wording():
    # dapagliflozin-hfpef 5 Oct: DELIVER's posted PRIMARY composite 'Subjects Included in the Composite Endpoint of CV
    # Death, Hospitalization Due to Heart Failure or Urgent Visit Due to Heart Failure' (HR 0.82 [0.73, 0.92]) was
    # refused OUTCOME_NOT_NAMED: the keywords say 'cardiovascular death or hospitalization for heart failure'
    title = ("Subjects Included in the Composite Endpoint of CV Death, Hospitalization Due to Heart Failure or Urgent "
             "Visit Due to Heart Failure")
    assert gt.keyword_named("cardiovascular death or hospitalization for heart failure", title)
    assert gt.keyword_named("cardiovascular death or hospitalisation for heart failure", title)
    # a COMPONENT-only title never names the composite keyword
    assert not gt.keyword_named("cardiovascular death or hospitalization for heart failure",
                                "Subjects With Hospitalization Due to Heart Failure")
    assert not gt.keyword_named("primary outcome", title)          # generic anchors never name


def test_a_secondary_registry_outcome_in_its_own_wording_is_a_binding_candidate():
    # tocilizumab 5 Oct: 'Mortality Rate at Day 28' (a SECONDARY posted outcome) was never even a candidate -- the
    # candidate filter still matched keywords as literal substrings ('mortality at day 28' is not in it)
    kws = ["28-day all-cause mortality", "mortality at day 28", "28-day mortality"]
    assert gt.binding_candidate("Mortality Rate at Day 28", kws, is_primary=False)
    assert gt.binding_candidate("Time to Clinical Improvement", kws, is_primary=True)        # primary: always examined
    assert not gt.binding_candidate("Time to Clinical Improvement", kws, is_primary=False)
