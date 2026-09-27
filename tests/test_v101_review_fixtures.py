"""V1.0.1 plants from the dapagliflozin-HFmrEF/HFpEF and denosumab reviews.

dapagliflozin: (1) COMORBIDITY IS NOT EXCLUSION -- CARDIA-STIFF (NCT04739215) requires T2D + LVEF >= 50% + HFpEF and
was excluded under X2 for mentioning diabetes; (2) DECLARE's "HF without known reduced EF" subgroup is
EF_UNMEASURED_OR_UNKNOWN, never HFpEF; (3) Banerjee's abstract states 6 RCTs / 15,769, so "count not stated" is false.
denosumab: (1) contributing trials get a source-backed structural decision (FREEDOM ESTABLISHED); (2) NCT01457950 is
resolved to Koh 2016 (PMID 27189284) before anything calls it results-only; (3) Wei 2023 is a network meta-analysis:
network counts are never the direct comparison's k, and its abstract 0.33 vs results 0.30 is kept as a mismatch.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import (comparator_models, comparator_network, extract, pipeline, population_witness as pw,  # noqa: E402
                     screen, trial_family)

ROOT = Path(__file__).resolve().parents[1]


def _topic(slug):
    return json.load(open(ROOT / "topics" / f"{slug}.json", encoding="utf-8"))


def _records(slug):
    return json.load(open(ROOT / "cache" / slug / "records.json", encoding="utf-8"))


def _decision(slug, key):
    data = _records(slug)
    recs = pipeline._dedup(data, _topic(slug).get("pivotal_trials"))
    rows = screen.run(recs, _topic(slug))["decisions"]
    return next(r for r in rows if str(key) in str(r.get("id")))


# ---------------------------------------------------------------- dapagliflozin (1) comorbidity is not exclusion
def test_CARDIA_STIFF_is_not_excluded_for_mentioning_diabetes():
    d = _decision("dapagliflozin-hfpef-hosp", "NCT04739215")
    assert not (d["decision"] == "exclude" and d.get("rule_id") == "X2"), d


def test_PLANT_entry_only_terms_come_from_the_X2_bullet_only():
    proto = ("## Eligibility\n- **X2** wrong population: diabetes-only, CKD-only populations\n"
             "## Outcomes\n- report the stroke-only subgroup separately\n")
    got = pw.entry_only_terms_from_protocol(proto, ["type 2 diabetes", "chronic kidney disease", "stroke", "women and men"])
    assert "type 2 diabetes" in got
    assert "stroke" not in got and "women and men" not in got


def test_PLANT_entry_only_is_applied_only_to_VALIDATED_topics():
    # doac-vte-recurrence: '-only' restricts VTE to a subgroup (cancer-associated VTE); lifting it would admit those
    cfg = screen.with_protocol_entry_only(_topic("doac-vte-recurrence"))
    assert cfg["include"].get("population_none_entry_condition_only_source") is None
    cfg = screen.with_protocol_entry_only(_topic("dapagliflozin-hfpef-hosp"))
    assert "protocols/dapagliflozin-hfpef-hosp.md" in cfg["include"]["population_none_entry_condition_only_source"]


def test_PLANT_diabetes_only_record_is_still_excluded():
    # synthetic control: a T2D population with no HF at all must still fall to the '-only' exclusion
    cfg = _topic("dapagliflozin-hfpef-hosp")
    rec = {"id": "__control_diabetes_only", "id_type": "pmid", "year": 2020, "title":
           "Dapagliflozin versus placebo on glycaemic control in type 2 diabetes: a randomized trial",
           "abstract": "Randomized, double-blind, placebo-controlled trial of dapagliflozin in adults with type 2 "
                       "diabetes mellitus. Primary outcome HbA1c.", "pubtypes": ["Randomized Controlled Trial"]}
    rows = screen.run([rec], cfg)["decisions"]
    assert rows[0]["decision"] == "exclude", rows[0]


# ---------------------------------------------------------------- dapagliflozin (2) EF unknown is not HFpEF
def test_DECLARE_HF_without_known_reduced_EF_is_EF_UNMEASURED():
    text = ("Of 17 160 patients, 671 (3.9%) had HFrEF, 1316 (7.7%) had HF without known reduced EF, and 15 173 "
            "(88.4%) had no history of HF.")
    state, quote = pw.ef_state(text, 1316)
    assert state == "EF_UNMEASURED_OR_UNKNOWN" and "without known reduced EF" in quote


def test_PLANT_a_measured_preserved_EF_sentence_is_HFpEF_evidence():
    state, _ = pw.ef_state("Patients with LVEF >= 45% (n = 500) were randomized.", 500)
    assert state == "EF_MEASURED_PRESERVED"


def test_served_dapagliflozin_comparator_member_is_EF_UNMEASURED():
    rev = json.load(open(ROOT / "docs/reviews/dapagliflozin-hfpef-hosp/review.json", encoding="utf-8"))
    mp = (rev["comparator"].get("member_populations") or [])
    assert any(m["report_pmid"] == "30882238" and m["ef_state"] == "EF_UNMEASURED_OR_UNKNOWN" for m in mp), mp


# ---------------------------------------------------------------- dapagliflozin (3) stated count is read
def test_Banerjee_states_six_RCTs():
    data = _records("dapagliflozin-hfpef-hosp")
    pm = str(data["comparator_pmid"])
    ab = next(str(r.get("abstract") or "") for r in data["records"] if str(r.get("id")) == pm)
    k, quote = extract.stated_trial_count(ab)
    assert k == 6 and "15" in quote, (k, quote)


def test_PLANT_stated_count_skips_another_reviews_count_and_hyphenated_numbers():
    assert extract.stated_trial_count("A recent meta-analysis by Smith et al. included 12 RCTs.")[0] is None
    assert extract.stated_trial_count("Fifty-five RCTs were included.")[0] != 5


# ---------------------------------------------------------------- denosumab (1) structural decision
def test_FREEDOM_contributes_with_a_source_backed_structural_decision():
    slug = "denosumab-vertebral-fracture"
    cfg = trial_family.population_witness_topic(ROOT, slug, trial_family.protocol_requirements(ROOT, slug, _topic(slug)))
    assert cfg.get("population_witness", {}).get("status") == "VALIDATED"
    rev = json.load(open(ROOT / "docs/reviews" / slug / "review.json", encoding="utf-8"))
    fam = next(f for f in rev["trial_families"] if f["family_id"] == "NCT00089791")
    g = copy.deepcopy(fam)
    trial_family.screen_family(g, cfg)
    pop = g["population_decision"]
    assert pop["state"] == "ESTABLISHED", pop
    assert any("osteoporosis" in str(w.get("quote") or "").lower() for w in pop["witnesses"])


def test_PLANT_later_phase_criteria_are_not_entry_criteria():
    inc, exc, _ = pw.split_criteria("Inclusion Criteria: - Postmenopausal women~Exclusion Criteria: - Prior fracture"
                                    "~Exclusion criteria for the extension phase: - New malignancy")
    assert "New malignancy" not in exc and "Prior fracture" in exc


# ---------------------------------------------------------------- denosumab (2) registry -> publication
def test_NCT01457950_is_resolved_to_Koh_2016_before_any_results_only_label():
    g = pipeline._load_ghost("denosumab-vertebral-fracture")
    assert "NCT01457950" not in (g.get("results_only_ncts") or [])
    pubs = g["publication_linking"]["relinked"]["NCT01457950"]["publications"]
    assert "27189284" in {p["pmid"] for p in pubs}
    assert "NCT01457950" in (g["as_census"]["results_only_ncts"] or [])  # the census's own label is kept beside it


# ---------------------------------------------------------------- denosumab (3) NMA comparator
def test_network_counts_are_never_the_direct_k():
    net = comparator_network.load(ROOT, "denosumab-vertebral-fracture")
    ov = comparator_network.apply({"ours_k": 1, "theirs_k": 55}, net, True)
    assert not isinstance(ov["theirs_k"], int) and ov["theirs_k"].startswith("not computed")
    assert ov["network"]["outcome_network"]["k"] == 55 and ov["network"]["whole_network"]["k"] == 92
    assert ov["network"]["direct_comparison"]["state"] == "NOT_ENUMERATED"


def test_PLANT_an_NMA_without_a_network_file_still_never_uses_its_stated_count():
    ov = comparator_network.apply({"ours_k": 3, "theirs_k": 40, "theirs_k_source": "abstract"}, None, True)
    assert ov["theirs_k"].startswith("not computed") and ov["network"]["stated_count_read"]["value"] == 40


def test_PLANT_network_quote_not_in_held_bytes_is_refused(tmp_path):
    slug = "__control_nma"
    (tmp_path / "cache" / slug).mkdir(parents=True)
    (tmp_path / "held.txt").write_text("This network meta-analysis included 12 RCTs.", encoding="utf-8")
    (tmp_path / "cache" / slug / "comparator_network.json").write_text(json.dumps({
        "design": "NETWORK_META_ANALYSIS",
        "whole_network": {"k": 13, "n": 1, "scope": "x", "quote": "included 13 RCTs", "document_ref": "held.txt"},
        "direct_comparison": {"state": "NOT_ENUMERATED", "k": None}}), encoding="utf-8")
    import pytest
    with pytest.raises(comparator_network.NetworkRefused):
        comparator_network.load(tmp_path, slug)


def test_Wei_abstract_vs_results_is_a_kept_mismatch():
    rev = json.load(open(ROOT / "docs/reviews/denosumab-vertebral-fracture/review.json", encoding="utf-8"))
    c = rev["comparator"]
    m = next(x for x in c["internal_mismatches"] if x["kind"] == "ABSTRACT_VS_RESULTS_TUPLE")
    assert [s["point"] for s in m["sides"]] == [0.33, 0.30]
    assert c["reported"][0]["estimate"] == 0.33 and c["reported"][0]["internal_mismatch"]["kind"] == "ABSTRACT_VS_RESULTS_TUPLE"


def test_PLANT_abstract_vs_results_detector():
    ab = "alpha (RR, 0.33; [95% CI, 0.14 to 0.61]) and beta (RR, 0.50; [95% CI, 0.40 to 0.60])"
    body = ("alpha (RR, 0.30; [95% CI, 0.14 to 0.61]); beta (RR, 0.50; [95% CI, 0.40 to 0.60]); "
            "in the long-term subgroup beta (RR, 0.20; [95% CI, 0.10 to 0.35])")
    got = comparator_models.abstract_body_mismatches(ab, body, "held.txt")
    assert [x["name"] for x in got] == ["alpha"]  # beta agrees; its subgroup tuple is another analysis, never compared


def test_PLANT_a_full_text_hit_that_merely_cites_a_trial_is_not_its_publication():
    # Europe PMC full-text search returns papers that NAME an NCT; the XANTUS design paper names SPARK's registration
    assert not pipeline._title_match("XANTUS: rationale and design of a noninterventional study of rivaroxaban for the "
                                     "prevention of stroke in patients with atrial fibrillation",
                                     ["SPARK: Safety Study of Pradaxa in Atrial Fibrillation Patients by Regulatory "
                                      "Requirement of Korea"])
    assert pipeline._title_match("Assessment of Denosumab in Korean Postmenopausal Women with Osteoporosis: Randomized, "
                                 "Double-Blind, Placebo-Controlled Trial with Open-Label Extension",
                                 ["A Study in Korean Postmenopausal Women With Osteoporosis to Evaluate the Efficacy and "
                                  "Safety of Denosumab"])


def test_colchicine_secondary_flip_is_deferred_until_Raju_harms_are_held():
    # the '-only' rule is checked for this topic, but Raju 2012 (21918905) would enter with a source-reported,
    # unextractable GI harm and the harms gate refuses such a page; the topic keeps its V1 screening until then
    reg = json.load(open(ROOT / "registry" / "population_witness_topics.json", encoding="utf-8"))
    e = reg["comorbidity_only_from_protocol"]["colchicine-secondary-cv-prevention"]
    assert e["status"] == "DEFERRED" and "diarrhoea" in e["deferred_why"]
    cfg = screen.with_protocol_entry_only(_topic("colchicine-secondary-cv-prevention"))
    assert cfg["include"].get("population_none_entry_condition_only_source") is None
    d = _decision("colchicine-secondary-cv-prevention", "21918905")
    assert d["decision"] == "exclude" and d["rule_id"] == "X2"


# ---------------------------------------------------------------- empagliflozin-HFpEF review
def test_NCT05139472_is_excluded_on_design_not_on_comparator():
    # an 8-person single-arm open-label pilot: allocation NA, SINGLE_GROUP -- excluded as not an RCT (X1), with that
    # reason, rather than falling to X3 ('no eligible comparator') or being included
    d = _decision("empagliflozin-hfpef-hosp", "NCT05139472")
    assert d["decision"] == "exclude" and d["rule_id"] == "X1", d


@pytest.mark.parametrize("alloc,is_rct", [("RANDOMIZED", True), ("NA", False), ("NON_RANDOMIZED", False), ("", True)])
def test_PLANT_registry_allocation_decides_the_design_axis(alloc, is_rct):
    rec = {"id": "NCT00000000", "id_type": "nct", "study_type": "INTERVENTIONAL", "allocation": alloc}
    assert screen._is_rct(rec) is is_rct


def test_empagliflozin_governing_comparator_is_the_protocols():
    from harness import comparator_identity as ci
    g = ci.check(str(ROOT), "empagliflozin-hfpef-hosp", "37773799")["governing"]
    assert g["state"] == "UNRECORDED_REPLACEMENT" and g["governing_pmid"] == "36914068" and g["served_pmid"] == "37773799"
    assert ci.check(str(ROOT), "dapagliflozin-hfpef-hosp", "36914068")["governing"]["state"] == "GOVERNING"


@pytest.mark.parametrize("item,excludes", [
    ("Myocardial infarction, acute heart failure or life-threatening arrhythmias in the preceding 15 days", False),
    ("Hospitalized for heart failure within 3 months", False),
    ("Heart failure", True),
])
def test_PLANT_a_recent_or_acute_event_is_a_qualified_subset_not_the_population(item, excludes):
    # found by the codex population-validation lane (IV iron, NCT04974021): the exclusion names the target term only
    # inside a time window, so it does not exclude the heart-failure population
    from harness import lexicon
    got = pw._exclusion_names_population(lexicon.fold(item), ["heart failure"])
    assert bool(got) is excludes, got
