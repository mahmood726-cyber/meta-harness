"""V1.0.1 plants from the esketamine review (Xie 2026, PMID 42490943).

(1) SET INVARIANT: the V1 manifest served ours=3, theirs=4, shared=4. Every served overlap must satisfy
    shared <= min(ours, theirs) and ours_only + shared = ours; a generic row label ('Trial A') is never an identity.
    Expected here, at outcome level (Day-28 MADRS, '937 (4 RCTs)'): shared = TRANSFORM-2, TRANSFORM-3, Chen; theirs
    only = TRANSFORM-1.
(2) ROW PLAUSIBILITY: Xie's 'Trial A' (cites TRANSFORM-2) prints 172/174 vs 227 randomised; its older-adult MD +0.50
    vs TRANSFORM-3's -3.6 (-7.20 to 0.07); 'Trial E' prints double-blind randomised withdrawal for SUSTAIN-2, whose own
    reference title says open-label -> COMPARATOR_ROW_IMPLAUSIBLE, numerical validation withheld.
(3) SEARCH CLASSIFIER: '"esketamine"[Title] AND ...' is a title-restricted CONCEPT query, not known-item seeding.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import comparator_rows as cr, gate, overlap_relation as orl, pipeline  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "esketamine-trd-madrs"
Q = '"esketamine"[Title] AND "treatment-resistant depression" AND placebo AND randomized'


def _served():
    return json.load(open(ROOT / "docs/reviews" / SLUG / "review.json", encoding="utf-8"))


# ---------------------------------------------------------------- (1) set invariant
@pytest.mark.parametrize("ours,theirs,shared,only_ours,bad", [
    (3, 4, 4, 0, True),       # the V1 manifest
    (3, 4, 3, 0, False),
    (3, 4, 2, 0, True),       # ours_only + shared != ours
    (3, 6, 3, 0, False),
])
def test_PLANT_set_invariant(ours, theirs, shared, only_ours, bad):
    assert bool(orl.set_invariant(ours, theirs, shared, only_ours)) is bad


def test_PLANT_an_impossible_set_is_never_served_as_a_relation():
    out = orl._finish({"ours_k": 3, "theirs_k": 4, "shared_k": 4, "shared": ["a", "b", "c", "d"], "only_ours": [],
                       "only_theirs": [], "constraints": []}, "SUBSET", "x")
    assert out["relation"] == "NOT_ENUMERABLE" and out["shared_k"] is None
    assert any(c.startswith("SET_INVARIANT_VIOLATED") for c in out["constraints"])


@pytest.mark.parametrize("name,generic", [("Trial A (2019)", True), ("Trial A", True), ("Study 2", True),
                                          ("TRANSFORM-2", False), ("Trial of esketamine", False)])
def test_PLANT_generic_labels_are_never_an_identity(name, generic):
    assert orl.generic_label(name) is generic


def test_esketamine_outcome_level_overlap():
    rel = _served()["comparator"]["overlap_relation"]
    assert (rel["ours_k"], rel["theirs_k"], rel["shared_k"]) == (3, 4, 3)
    assert rel["only_ours"] == [] and rel["only_theirs"] == ["Trial B (2019) 2019 [B20]"]   # TRANSFORM-1 (PMID 31290965)
    assert set(rel["shared"]) == {"NCT02418585", "NCT02422186", "NCT03434041"}           # TRANSFORM-2, TRANSFORM-3, Chen


def test_every_served_overlap_satisfies_the_invariant():
    for d in sorted((ROOT / "docs" / "reviews").iterdir()):
        if (d / "review.json").exists():
            assert [x for x in gate.check_comparator_sets_and_rows(str(d)) if "overlap" in x or "relation" in x] == [], d.name


# ---------------------------------------------------------------- (2) row plausibility
def test_xie_rows_are_implausible_and_validation_is_withheld():
    a = _served()["comparator"]["row_checks"]
    st = {r["row"]: (r["state"], {c["check"]: c["state"] for c in r["checks"]}) for r in a["rows"]}
    assert st["Trial A (2019) 2019 [B19]"] == ("COMPARATOR_ROW_IMPLAUSIBLE", {"n": "FAIL", "design": "PASS"})
    assert st["Trial D (2020) 2020 [B21]"] == ("COMPARATOR_ROW_IMPLAUSIBLE", {"direction": "FAIL"})
    assert st["Trial E (2020) 2020 [B25]"] == ("COMPARATOR_ROW_IMPLAUSIBLE", {"design": "FAIL"})
    assert a["numerical_validation"]["state"] == "WITHHELD"
    html = open(ROOT / "docs/reviews" / SLUG / "index.html", encoding="utf-8").read()
    assert "Numerical validation against this comparator is WITHHELD" in html
    assert gate.check_comparator_sets_and_rows(str(ROOT / "docs/reviews" / SLUG), html) == []


def test_PLANT_a_plausible_row_passes_every_check():
    r = {"row": "x", "printed": {"n": {"value": 200}, "design": {"value": "PARALLEL_RANDOMISED"},
                                 "effect": {"point": -3.0}},
         "cited": {"randomised_n": {"value": 227}, "design": {"value": "PARALLEL_RANDOMISED"},
                   "effect": {"point": -3.6, "ci_low": -7.2, "ci_high": 0.07}}}
    assert cr.assess({"rows": [r]})["rows"][0]["state"] == "PLAUSIBLE"
    assert cr.assess({"rows": [r]})["numerical_validation"]["state"] == "ALLOWED"


def test_PLANT_a_quote_not_in_held_bytes_refuses_the_record(tmp_path):
    (tmp_path / "cache" / "x").mkdir(parents=True)
    (tmp_path / "held.txt").write_text("227 underwent randomization", encoding="utf-8")
    doc = {"rows": [{"row": "r", "cited": {"randomised_n": {"value": 227, "evidence": [
        {"document_ref": "held.txt", "quote": "272 underwent randomization"}]}}}]}
    (tmp_path / "cache" / "x" / "comparator_row_checks.json").write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(cr.RowsRefused, match="not located"):
        cr.load(tmp_path, "x")


def test_PLANT_outcome_membership_needs_its_arithmetic():
    doc = json.load(open(ROOT / "cache" / SLUG / "comparator_row_checks.json", encoding="utf-8"))
    bad = copy.deepcopy(doc)
    bad["outcome_membership"]["stated_participants"] = 936
    a = cr.assess(bad)
    assert a["outcome_membership"]["arithmetic"] == "MISMATCH"
    panel = {"trial_set": [{"family_id": "Trial B (2019) 2019 [B20]"}]}
    cr.apply_to_panel(panel, a, "o")
    assert "outcome_endpoints" not in panel                    # never applied without the arithmetic


# ---------------------------------------------------------------- (3) search classifier
def test_a_treatment_concept_in_a_title_field_is_a_concept_search():
    assert pipeline.classify_query(Q) == "TITLE_RESTRICTED_CONCEPT"
    rc = _served()["search"]["retrieval_class"]
    assert rc["class"] == "HAND_WRITTEN_KEYWORD_SEARCH"
    assert rc["axes"]["can_retrieve_unknown_trial"]["answer"] == "YES"
    assert rc["axes"]["execution_documented"]["answer"] == "PARTIAL"
    assert rc["axes"]["coverage_adequate"]["answer"] == "NOT_ESTABLISHED"


def test_PLANT_an_unseen_eligible_title_is_retrievable_by_the_query():
    unseen = {"title": "Esketamine nasal spray added to an oral antidepressant: a new randomized trial",
              "abstract": "Adults with treatment-resistant depression were randomized to esketamine or placebo."}
    assert pipeline.query_matches(Q, unseen)
    # and the title restriction is real: the term only in the abstract is not retrieved
    assert not pipeline.query_matches(Q, {"title": "Ketamine analogues in depression",
                                          "abstract": "esketamine treatment-resistant depression placebo randomized"})


@pytest.mark.parametrize("q,kind", [
    ('"PARADIGM-HF"[Title]', "TITLE_ANCHORED"),
    ('"Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes"[Title]', "TITLE_ANCHORED"),
    ("denosumab[Title] AND prevention[Title] AND fractures[Title] AND postmenopausal[Title] AND osteoporosis[Title]",
     "TITLE_ANCHORED"),
    ("Dexamethasone[Title] AND Covid-19[Title]", "TITLE_RESTRICTED_CONCEPT"),
])
def test_PLANT_seeding_is_decided_by_what_the_title_field_holds(q, kind):
    assert pipeline.classify_query(q) == kind


# ---------------------------------------------------------------- found by the row lane: citation-bound rows
def _row(name, ref_text, rid):
    return {"family_id": name, "name_in_source": name,
            "aliases": [{"id": "1", "linked_rid": rid, "span": {"quote": f'<ref id="{rid}">{ref_text}</ref>'}}]}


def test_PLANT_a_row_citing_another_author_is_refused_and_accents_are_folded():
    from harness import comparator_panel as cp
    c = {"trial_set": [_row("Burr 1989", "[23] Begg CB Mazumdar M . Operating characteristics", "R23"),
                       _row("Garzón C 2009", "26 Garzon C , Guerrero JM", "R26"),
                       _row("HEART-FID 2023", "11. Mentz R.J. Garg J.", "R11")]}
    cp.refuse_misbound_rows(c)
    by = {m["family_id"]: m for m in c["trial_set"]}
    assert by["Burr 1989"]["aliases"] == [] and by["Burr 1989"]["binding_refused"]
    assert by["Garzón C 2009"]["aliases"] and not by["Garzón C 2009"].get("binding_refused")   # accent folded
    assert by["HEART-FID 2023"]["aliases"]                                                     # acronym: not a surname


def test_PLANT_a_mostly_misbound_citation_column_refuses_every_row():
    from harness import comparator_panel as cp
    c = {"trial_set": [_row("Burr 1989", "[23] Begg CB", "R23"), _row("Eritsland 1996", "[24] Burr ML", "R24"),
                       _row("Nilsen 2001", "[26] GISSI-Prevenzione", "R26"), _row("GISSI-P 1999", "[25] Eritsland J", "R25")]}
    cp.refuse_misbound_rows(c)
    assert c["citation_column"]["state"] == "UNRELIABLE"
    assert all(m["aliases"] == [] for m in c["trial_set"])                                    # the acronym row too


def test_omega3_comparator_rows_are_not_bound_through_its_shifted_citations():
    rev = json.load(open(ROOT / "docs/reviews/omega3-cardiovascular-events/review.json", encoding="utf-8"))
    panel = rev["comparator_panel"][0]
    assert panel["citation_column"]["state"] == "UNRELIABLE"
    assert any(m["kind"] == "TABLE_CITATIONS_OFF_BY_ONE" for m in rev["comparator"]["internal_mismatches"])
