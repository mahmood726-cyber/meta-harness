"""Estimator provenance: the witness of an effect's estimator must OWN that effect (lane OC, 2026-09-25; external audit).

The finding, reproduced on the real verifier before the fix (evidence/ordered_contrast/estimator_owner/repro_before_fix.json):
estimand_evidence scanned the WHOLE abstract and, when every mention shared one type, took hits[0]. For LEADER that is the
methods / noninferiority-margin sentence ('... the upper boundary of the 95% confidence interval of the hazard ratio'), which does
not hold 0.87 -- and P10 checked only that the span reproduced and the state matched, so a served 'odds ratio' with that span passed.
The auditor's follow-up: HR relabelled RR passes TWO layers for the wrong reason, because harness/estmeasure.py classifies the
CLAIMED label and puts HR and RR in one class ('compatible_labels'). Estimator identity is now its own source-bound predicate (P15),
decided before any class is consulted."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import verify_bundle as vb   # noqa: E402

SLUG = "glp1-ra-mace-t2d"
REC = {str(r["id"]): r for r in json.load(open(os.path.join(ROOT, "docs", "cache", SLUG, "records.json"), encoding="utf-8"))["records"]}
LEADER_CLAUSE = ("The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) than in "
                 "the placebo group (694 of 4672 [14.9%]) (hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97; P<0.001 for "
                 "noninferiority; P=0.01 for superiority).")


def test_leader_estimator_is_owned_by_the_clause_that_holds_0_87_not_by_the_first_mention():
    parsed = REC["27295427"]["abstract"]
    assert parsed.count("hazard ratio") >= 3                                          # the auditor's three mentions
    first = parsed.index("hazard ratio")
    assert "0.87" not in parsed[parsed.rfind(". ", 0, first):parsed.find(". ", first)]  # hits[0] is the methods sentence
    est = vb.estimand_evidence(parsed, LEADER_CLAUSE)["estimator"]
    assert est["state"] == "STATED_IN_OWNING_EVIDENCE" and est["value"] == "hazard ratio" and est["owner"] == "EFFECT_CLAUSE"
    assert est["span"] == LEADER_CLAUSE and parsed[est["start"]:est["end"]] == LEADER_CLAUSE and "0.87" in est["span"]
    # the methods sentence names the primary outcome, so it is a LINKED candidate -- but the clause states the estimator, and the
    # clause is resolved first: the linked sentence is only a fallback, and here it is not the witness
    assert not (est["start"] <= first < est["end"])


def test_a_linked_method_span_owns_the_estimator_only_when_the_clause_names_none():
    parsed = REC["27295427"]["abstract"].replace("(hazard ratio, 0.87;", "(0.87;")
    clause = LEADER_CLAUSE.replace("(hazard ratio, 0.87;", "(0.87;")
    est = vb.estimand_evidence(parsed, clause)["estimator"]
    assert est["owner"] == "LINKED_METHOD_SPAN" and est["value"] == "hazard ratio"
    assert est["link"]["kind"] == "SAME_RESULT_OBJECT" and "primary outcome" in est["link"]["named_in_method_span"]
    # an arbitrary other mention never qualifies: the CV-death sentence names no primary outcome and is not a candidate
    assert "cardiovascular causes" not in est["span"]
    # with no result object named in the clause there is no link, so nothing owns it
    bare = vb.estimand_evidence(parsed, "Fewer events occurred with liraglutide than placebo (0.87; 95% CI, 0.78 to 0.97).")["estimator"]
    assert bare["state"] == "REGISTERED_DEFAULT"


def test_an_unowned_departing_strategy_fails_closed_instead_of_vanishing():
    """Effect-scoping must never make a stated departure disappear: an on-treatment analysis mentioned outside the owning evidence
    cannot witness the effect, and cannot be ignored either."""
    parsed = ("METHODS: Patients were randomized. A sensitivity on-treatment analysis was also performed. RESULTS: " + LEADER_CLAUSE)
    win = vb.estimand_evidence(parsed, LEADER_CLAUSE)["analysis_window"]
    assert win["state"] == "UNRESOLVED" and win["values"] == ["on-treatment"]
    owned = vb.estimand_evidence("The primary outcome was analysed on-treatment. RESULTS: " + LEADER_CLAUSE, LEADER_CLAUSE)["analysis_window"]
    assert owned["state"] == "STATED_IN_OWNING_EVIDENCE" and owned["value"] == "on-treatment" and owned["owner"] == "LINKED_METHOD_SPAN"


def test_two_estimators_in_the_clause_itself_are_unresolved_but_a_different_estimator_elsewhere_is_not():
    two = "The primary outcome occurred less often (hazard ratio, 0.87; odds ratio, 0.85; 95% CI, 0.78 to 0.97)."
    assert vb.estimand_evidence(two, two)["estimator"]["state"] == "UNRESOLVED"
    elsewhere = "Retinopathy was reported (odds ratio, 1.2). " + LEADER_CLAUSE
    est = vb.estimand_evidence(elsewhere, LEADER_CLAUSE)["estimator"]
    assert est["state"] == "STATED_IN_OWNING_EVIDENCE" and est["value"] == "hazard ratio"     # the old whole-document scan said UNRESOLVED


def test_the_producer_and_the_verifier_carry_the_same_estimand_rules():
    v = open(os.path.join(ROOT, "scripts", "verify_bundle.py"), encoding="utf-8").read()
    p = open(os.path.join(ROOT, "scripts", "build_bundle.py"), encoding="utf-8").read()

    def span(src):
        i = src.index("_ESTIMAND = {")
        return src[i:src.index("\n# ---- ", src.index("def estimand_evidence("))]
    assert span(v) == span(p)


def test_every_served_estimator_witness_holds_its_own_effect_tuple():
    b = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    for r in b["verification_rows"]:
        est = r["analysis_identity"]["estimator"]
        tok = str(r["effect"]["estimate"])
        assert est["owner"] == "EFFECT_CLAUSE" and tok in est["span"], (r["trial"]["id"], est.get("span", "")[:80])
        assert r["admission"]["predicates"]["P15_estimator_source_bound"]["state"] == "PASS"
    assert b["registered_estimand"]["estimators_permitted"] == ["HR"]
