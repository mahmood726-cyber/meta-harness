"""V1.0.1 plants from the finerenone review.

(1) ARTS-DN Japan (NCT01968668) was registry-only; Katayama 2017 (PMID 28025025) is its report, bound by the acronym
    both held texts print; population established from the sponsor's registry record ('Diabetic Nephropathies').
(2) Ghosal & Sinha 2023: attribution mismatch (protocol says Sarafidis); hyperkalaemia 2.22 (1.93-2.24) vs forest plot
    2.54 -> COMPARATOR_INTERNAL_MISMATCH (+ log-scale asymmetry); Fig 3B mixes treatment-related with
    investigator-reported hyperkalaemia -> COMPARATOR_DEFINITION_MIX, validation withheld for that outcome only; the
    kidney overlap (2 shared: FIDELIO, FIGARO) is kept.
(3) FIDELITY (0.85, 0.77-0.93) is an external checkpoint: never a target, never a third input.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import (comparator_models as cm, comparator_rows as cr, external_checkpoints as ec,  # noqa: E402
                     family_pub_links as fpl, trial_family as tf)

ROOT = Path(__file__).resolve().parents[1]
SLUG = "finerenone-ckd-t2d-renal"


def _served():
    return json.load(open(ROOT / "docs/reviews" / SLUG / "review.json", encoding="utf-8"))


# ---------------------------------------------------------------- (1) registry -> publication
def test_ARTS_DN_Japan_is_linked_to_Katayama_and_eligible_on_its_sponsor_record():
    f = next(f for f in _served()["trial_families"] if f["family_id"] == "NCT01968668")
    assert ("28025025", "PRIMARY") in {(r["report_id"], r["role"]) for r in f["reports"]}
    assert f["eligibility"]["state"] == "ELIGIBLE"


def test_PLANT_a_link_whose_token_is_not_in_both_texts_is_refused():
    recs = json.load(open(ROOT / "cache" / SLUG / "records.json", encoding="utf-8"))
    links = fpl.links(ROOT, SLUG)
    bad = copy.deepcopy(links)
    bad[0]["binding_token"] = "ARTS-DN Korea"
    import unittest.mock as um
    with um.patch.object(fpl, "links", return_value=bad):
        with pytest.raises(fpl.LinkRefused):
            fpl.merge(ROOT, SLUG, recs)


def test_ARTS_DN_Japan_harms_are_a_sourced_typed_refusal_not_an_unresolved_gap():
    # linking the report made its hyperkalaemia statement visible to the harm panel; it reports zero events in every
    # arm of a seven-dose design, so it is recorded (RETRIEVED_INCOMPATIBLE_STRUCTURE, like ARTS-DN), never silently
    # dropped and never an open HARMS_INCOMPLETE that refuses the page
    from harness import gate
    for o in _served()["outcomes"]:
        if o.get("kind") == "harm" and o["name"].startswith("Hyperkalemia"):
            row = next(t for t in o["declared_absent_trials"] if "28025025" in str(t.get("id")))
            assert row["harm_absence_state"] == "RETRIEVED_INCOMPATIBLE_STRUCTURE"
            assert "no patients developed hyperkalemia" in row.get("harm_source_span", "") + json.dumps(row)
    assert gate.check_harms_complete(str(ROOT / "docs/reviews" / SLUG)) == []


@pytest.mark.parametrize("terms,conds,ok", [
    (["diabetic nephropathy"], ["Diabetic Nephropathies"], True),
    (["kidney disease"], ["Kidney Diseases"], True),
    (["diabetic nephropathy"], ["Hypertension"], False),
])
def test_PLANT_registry_conditions_match_the_terms_regular_plural(terms, conds, ok):
    assert tf.population_matches(terms, conds) is ok


# ---------------------------------------------------------------- (2) comparator
def test_identity_mismatch_names_the_resolved_authors():
    ident = _served()["comparator"]["identity"]
    assert ident["state"] == "COMPARATOR_IDENTITY_MISMATCH"
    assert ident["protocol"]["named_author"] == "Sarafidis" and ident["resolved"]["first_author"].startswith("Ghosal")


def test_hyperkalaemia_ci_is_an_internal_mismatch_twice_over():
    kinds = [m["kind"] for m in _served()["comparator"]["internal_mismatches"]]
    assert "ABSTRACT_VS_FOREST_PLOT_CI" in kinds and "CI_ASYMMETRIC_ON_LOG_SCALE" in kinds


@pytest.mark.parametrize("row,flag", [
    ({"outcome": "x", "scale": "RR", "estimate": 2.22, "ci_low": 1.93, "ci_high": 2.24}, True),
    ({"outcome": "x", "scale": "RR", "estimate": 2.22, "ci_low": 1.93, "ci_high": 2.54}, False),
    ({"outcome": "x", "scale": "MD", "estimate": 2.22, "ci_low": 1.93, "ci_high": 2.24}, False),   # not a ratio
])
def test_PLANT_log_scale_asymmetry(row, flag):
    assert bool(cm.log_scale_asymmetry([row])) is flag


def test_definition_mix_withholds_only_that_outcome_and_keeps_the_kidney_overlap():
    c = _served()["comparator"]
    rc = c["row_checks"]
    assert rc["numerical_validation"]["state"] == "ALLOWED"
    assert rc["numerical_validation_by_outcome"]["Hyperkalemia"]["state"] == "WITHHELD"
    ov = c["overlap_relation"]
    assert ov["relation"] == "IDENTICAL_SET" and ov["shared_k"] == 2
    assert set(ov["shared"]) == {"NCT02540993", "NCT02545049"}                    # FIDELIO, FIGARO
    html = open(ROOT / "docs/reviews" / SLUG / "index.html", encoding="utf-8").read()
    assert "is WITHHELD for Hyperkalemia" in html


def test_PLANT_one_definition_across_rows_is_not_a_mix():
    doc = {"rows": [], "definition_checks": [{"outcome": "H", "rows": [
        {"row": "a", "matched_definition": "INVESTIGATOR_REPORTED"}, {"row": "b", "matched_definition": "INVESTIGATOR_REPORTED"}]}]}
    assert "definition_mixes" not in cr.assess(doc)
    doc["definition_checks"][0]["rows"][0]["matched_definition"] = "TREATMENT_RELATED"
    assert cr.assess(doc)["numerical_validation_by_outcome"]["H"]["state"] == "WITHHELD"


# ---------------------------------------------------------------- (3) external checkpoint
def test_FIDELITY_is_a_checkpoint_not_a_target_and_not_an_input():
    cp = _served()["external_checkpoints"][0]
    assert cp["name"] == "FIDELITY" and cp["role"] == "EXTERNAL_CHECKPOINT"
    assert (cp["estimate"], cp["ci_low"], cp["ci_high"]) == (0.85, 0.77, 0.93)
    assert "no pass/fail" in cp["comparison"]["reading"]
    prim = next(o for o in _served()["outcomes"] if o.get("primary"))
    assert len(prim["trials"]) == 2 and "35023547" not in {str(t.get("label")) for t in prim["trials"]}


def test_PLANT_a_checkpoint_in_the_pool_refuses_the_build():
    rev = copy.deepcopy(_served())
    prim = next(o for o in rev["outcomes"] if o.get("primary"))
    prim["trials"].append({"label": "35023547", "id": "PMID 35023547"})
    with pytest.raises(ec.CheckpointRefused, match="never be an input"):
        ec.attach(rev, ec.load(ROOT, SLUG))
