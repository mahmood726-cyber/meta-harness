"""Mahmood's review of the served glp1 page (98726cc1 / 6f14b03a, 19 Sep 2026), increment 2 of the revision list:
(a) SOUL (PMID 40162642) is pooled as `UNBOUND_LEGACY` while marked verified, and its provenance says
`fulltext_verified` although the cited passage is the abstract -- the hand-verified route bypassed the endpoint-binding
safeguard, and `verify_pooled` checked the row's digits against the hand-written description that carries them;
(b) all eight primary rows list registry evidence of a PARALLEL design (`design.basis`: AACT designs.intervention_model
= PARALLEL) while the design decision says "no committed design evidence" -- the API-v2 enumeration was not mapped.

Requirements: a hand-verified row whose numbers locate a sentence in the held abstract is bound to its definition span,
classified, and labelled `abstract_verified` (its digits verified against the held abstract bytes); a row whose numbers
are not in the abstract keeps `fulltext_verified` + `unbound_legacy` and says `verified_passage_location:
not_in_abstract`; a registry intervention model of PARALLEL establishes the design, and a decision that finds no parallel
design names the evidence it did see. Plant: on bf2af50d the first three tests fail.
"""
import json
import pathlib

from harness import design_key, target_endpoint as te, verify

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _records(slug):
    return {str(r["id"]): r for r in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))["records"]}


def _spec(slug):
    return json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))["primary_outcome"]


def test_soul_is_bound_classified_and_labelled_by_where_its_passage_is():
    review = _review("glp1-ra-mace-t2d")
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    soul = next(t for t in primary["trials"] if t["label"] == "SOUL")
    assert soul["provenance"] == "abstract_verified", soul.get("provenance")
    assert soul["endpoint_binding"] != "unbound_legacy"
    assert soul["target_endpoint_class"] == te.EXACT_TARGET
    assert "0.86" in soul["endpoint_result_span"] and "0.77 to 0.96" in soul["endpoint_result_span"]
    assert "death from cardiovascular causes" in soul["endpoint_definition_span"]
    assert soul["verified_passage_location"] == "abstract"


def test_bind_verified_row_locates_by_numbers_and_never_guesses():
    abstract = _records("glp1-ra-mace-t2d")["40162642"]["abstract"]
    bound = te.bind_verified_row(_spec("glp1-ra-mace-t2d"), abstract, {"effect": 0.86, "ci_low": 0.77, "ci_high": 0.96})
    assert bound["target_endpoint_class"] == te.EXACT_TARGET and bound["passage_location"] == "abstract"
    elsewhere = te.bind_verified_row(_spec("glp1-ra-mace-t2d"), abstract, {"effect": 0.91, "ci_low": 0.80, "ci_high": 1.03})
    assert elsewhere["target_endpoint_class"] == te.ENDPOINT_UNBOUND and elsewhere["passage_location"] == "not_in_abstract"


def test_abstract_verified_digits_are_checked_against_the_held_abstract_not_the_description():
    abstract = _records("glp1-ra-mace-t2d")["40162642"]["abstract"]
    row = {"effect": 0.99, "ci_low": 0.77, "ci_high": 0.96, "provenance": "abstract_verified",
           "source": "description that carries 0.99 although the abstract says 0.86"}
    status, _ = verify.verify_pooled(row, abstract)
    assert status == "not-yet"


def test_registry_parallel_establishes_the_design_and_glp1_rows_carry_it():
    design, unit, basis = design_key._registry_basis("NCT01179048", {"NCT01179048": {"intervention_model": "PARALLEL"}})
    assert (design, unit) == ("PARALLEL", "INDIVIDUAL") and basis["span"] == "PARALLEL"
    review = _review("glp1-ra-mace-t2d")
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    contradictions = []
    for t in primary["trials"]:
        d = t.get("design") or {}
        registry_parallel = any(b.get("source") == "AACT designs.intervention_model" and b.get("span") == "PARALLEL"
                                for b in d.get("basis") or [])
        if registry_parallel and d.get("design") != "PARALLEL" and not d.get("conflict"):
            contradictions.append(t["label"])
    assert contradictions == [], contradictions


def test_design_unproven_reason_names_the_evidence_it_saw():
    trial = {"design": {"design": "UNKNOWN", "unit_of_randomisation": "UNKNOWN", "correlation_handling": {"method": "none", "evidence": []},
                        "basis": [{"source": "AACT designs.intervention_model", "span": "SINGLE_GROUP"}]}, "derivation": "reported"}
    action = design_key.decision_for_trial(trial)
    assert action["action"] == "DESIGN_UNPROVEN"
    assert "SINGLE_GROUP" in action["reason"] and "no committed design evidence" not in action["reason"]
