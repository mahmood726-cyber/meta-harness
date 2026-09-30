"""MRA-HFrEF mortality fixtures, 2026-09-28: trial phases, a role anchor never names our outcome, population-specific
harms with typed definitions, a narrower zero is not a zero, Udelson screened (plants included)."""
import copy
import html
import json
import os
import re

import pytest

from harness import (extract, fetch, hand_binding as hb, pipeline, result_status as rs, screen,
                     source_hierarchy as sh, target_endpoint as te, trial_family as tf)

ROOT = pipeline.ROOT
SLUG = "spironolactone-hfref-mortality"
H = "evidence/acquisition_cascade/held"
_R = {}


def _cfg():
    return dict(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8")), slug=SLUG)


def _rv():
    if not _R:
        cfg = _cfg()
        _R["rv"] = pipeline.build_review_core(SLUG, cfg, fetch.ensure(cfg, ""), "test")
    return _R["rv"]


def _o(rv, name):
    return next(o for o in rv["outcomes"] if o["name"] == name)


def _row(o, pid, pooled):
    return next(t for t in (o["trials"] if pooled else o["declared_absent_trials"]) if pid in str(t["id"]))


# ------------------------------------------------------------------------------------------------ (1) phases
def test_emphasis_is_screened_on_its_randomised_phase_never_the_extensions_design():
    rv = _rv()
    f = next(x for x in rv["trial_families"] if x["family_id"] == "NCT00232180")
    assert f["eligibility"]["state"] == "ELIGIBLE"
    assert (f["registry_design"]["allocation"], f["registry_design"]["masking"], f["registry_design"]["basis"]) == \
        ("RANDOMIZED", "DOUBLE", "PHASE_WITNESS")
    # the latest registry field is kept, attributed to the extension -- never trusted as the trial's design
    assert (f["registry_design_latest"]["allocation"], f["registry_design_latest"]["intervention_model"]) == \
        ("NON_RANDOMIZED", "SINGLE_GROUP")
    ole = next(p for p in f["phases"] if p["kind"] == "EXTENSION")
    assert ole["comparisons"] == [] and ole["design"]["masking"] == "NONE"
    assert "NCT00232180" not in rv["family_count_chain"]["contributing_without_structural_eligibility"]
    mortality = _o(rv, "All-cause mortality")
    assert mortality['measure_mix']['classes'] == ['HAZARD_RATIO', 'RISK_RATIO']
    assert any(p['code'] == 'MEASURE_MIX_POOLED' and not p['blocking'] for p in mortality['lane_problems'])
    row = _row(mortality, "21073363", True)
    assert row["analysis_phase"] == {"phase": "DOUBLE_BLIND", "comparison": "eplerenone-vs-placebo",
                                     "analysis_period": "DB_TO_CUTOFF_2010-05-25"}


def _decl():
    d = json.load(open(os.path.join(ROOT, "docs", "trial_phases.json"), encoding="utf-8"))
    return copy.deepcopy(d["topics"][SLUG]["NCT00232180"])


def _fam():
    reg = tf.load_registry(ROOT, SLUG)["NCT00232180"]
    return {"family_id": "NCT00232180", "registry_design": dict(reg["design"]), "arms": reg["arms"]}


@pytest.mark.parametrize("mutate", [
    lambda d: d["phases"][1].__setitem__("comparisons", [{"comparison_id": "x", "arms": []}]),     # extension redefines
    lambda d: d["phases"][1]["design"].__setitem__("masking", "DOUBLE"),                          # inherits blinding
    lambda d: d["phases"][1]["arms"].append({"label": "Placebo", "interventions": ["Placebo"]}),  # inherits placebo
    lambda d: d.__setitem__("registry_design_field_describes", "DOUBLE_BLIND"),                   # field misattributed
])
def test_a_phase_declaration_that_lets_the_extension_touch_the_comparison_fails_closed(mutate):
    d = _decl()
    mutate(d)
    with pytest.raises(ValueError, match="PHASE_DECLARATION_INVALID"):
        tf.attach_phases(_fam(), d, ["eplerenone"], ["placebo"])


# ------------------------------------------------------------------------------------------------ role anchors
def test_a_role_anchor_never_makes_another_outcomes_effect_a_mortality_candidate():
    recs = {str(r["id"]): r for r in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"),
                                                    encoding="utf-8"))["records"]}
    spec = _cfg()["primary_outcome"]
    cands = lambda pid: {(c["effect"], c["ci_low"], c["ci_high"]) for c in
                         sh.source_effect_candidates(spec, abstract=recs[pid]["abstract"])}
    assert (0.85, 0.53, 1.36) not in cands("28824029")          # J-EMPHASIS composite primary
    assert (0.63, 0.54, 0.74) not in cands("21073363")          # EMPHASIS-HF composite primary
    assert (0.76, 0.62, 0.93) in cands("21073363")              # its all-cause mortality stays
    # plant: a trial whose primary IS death keeps the anchor
    ab = ("The primary end point was death from all causes. The primary end point occurred in fewer patients "
          "(hazard ratio, 0.70; 95% CI, 0.60 to 0.82).")
    assert {c["effect"] for c in sh.source_effect_candidates(spec, abstract=ab)} == {0.70}


def test_j_emphasis_mortality_is_its_own_table3_hr_bound_by_its_row_label():
    rv = _rv()
    o = _o(rv, "All-cause mortality")
    assert 'PMID 28824029' in o['measure_mix']['inputs_by_class']['HAZARD_RATIO']
    row = _row(o, "28824029", True)
    assert (row["effect"], row["ci_low"], row["ci_high"], row["scale"]) == (1.77, 0.81, 3.87, "HR")
    assert o["result"]["k"] == 3
    # plant: a row label naming a DIFFERENT single outcome under the same caption does not bind as ours
    spec = _cfg()["primary_outcome"]
    cand = {"kind": "table_row", "label": "Hospitalization for any cause", "section_heading": "",
            "caption": "Table 3. Primary and Secondary Outcomes in the J-EMPHASIS-HF Study", "text": "x", "xml": "x"}
    assert hb._ownership(spec, cand, "")["target_endpoint_class"] != te.EXACT_TARGET


# ------------------------------------------------------------------------------------------------ (2) safety
def test_hyperkalaemia_definitions_stay_distinct_and_no_count_is_computed_from_percentages():
    rv = _rv()
    o = _o(rv, "Hyperkalemia")
    j = _row(o, "28824029", True)
    assert (j["ai"], j["n1i"], j["ci"], j["n2i"]) == (8, 111, 6, 110)
    assert j["harm_definition_key"] == "HYPERKALAEMIA_INVESTIGATOR_REPORTED"
    assert len(o["trials"]) == 1                                   # never pooled across definitions
    rales, emph = _row(o, "10471456", False), _row(o, "21073363", False)
    assert rales["result_status"]["state"] == emph["result_status"]["state"] == "REPORTED_UNRESOLVED"
    assert "14/822" in rales["relayed_not_held"]["value"] and "10/841" in rales["relayed_not_held"]["value"]
    # EMPHASIS-HF's laboratory-threshold counts are not held: its pinned refusal stands, and no count is computed
    assert emph.get("ai") is None and emph["reason_code"] == "REFUSED_ON_EVIDENCE" and "percentages only" in emph["reason"]


def test_gynaecomastia_alone_is_not_a_zero_for_the_composite_and_rales_is_men_only():
    rv = _rv()
    o = _o(rv, "Gynecomastia or breast pain")
    j = _row(o, "28824029", False)
    assert j["result_status"]["state"] == "EXTRACTED_NOT_ADMITTED"
    r = _row(o, "10471456", False)
    assert "61/603 vs 9/614" in r["relayed_not_held"]["value"] and "men-only" in r["relayed_not_held"]["value"]
    # plant: the same 0 vs 0 WITHOUT a reason it is not this outcome's IS a zero-event report
    plain = {"id": "PMID 1", "held_out_row": {"ai": 0, "n1i": 10, "ci": 0, "n2i": 10}, "reason_code": "X"}
    assert rs.status_of(plain, pooled=False, pending_ids=set())["state"] == "REPORTED_ZERO_EVENTS"
    assert rs.status_of(dict(plain, not_admitted_because="narrower"), pooled=False, pending_ids=set())["state"] == "EXTRACTED_NOT_ADMITTED"


# ------------------------------------------------------------------------------------------------ (3) Udelson
def test_udelson_is_screened_by_the_harness_and_supplies_no_mortality_hr():
    d = json.load(open(os.path.join(ROOT, H, "Udelson-2010", "europepmc_record_20299607.json"), encoding="utf-8"))
    r = (d.get("resultList") or {}).get("result", [d])[0] if "resultList" in d else d
    ab = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", r["abstractText"]))).strip()
    rec = {"id": "20299607", "id_type": "pmid", "title": r["title"], "abstract": ab,
           "pubtypes": list((r.get("pubTypeList") or {}).get("pubType") or [])}
    cfg = _cfg()
    assert screen.screen_record(rec, cfg["include"], set(cfg.get("negative_control_pmids") or [])).decision == "include"
    k = json.load(open(os.path.join(ROOT, "docs", "known_eligible_missing.json"), encoding="utf-8"))["topics"][SLUG]
    u = next(e for e in k if e["pmid"] == "20299607")
    assert u["screening"]["decision"] == "include"
    assert u["result_states"]["All-cause mortality"]["state"] == "NOT_YET_RETRIEVED"
    assert not any("20299607" in str(t["id"]) for t in _o(_rv(), "All-cause mortality")["trials"])
