"""Wrong-endpoint acceptance (external review of served glp1 edaf5f6b, defect 1).

Plant: an abstract whose PRIMARY outcome is 3-point MACE, which reports NO composite result,
and which reports CV death ALONE as HR 0.50.  The outcome builder must not certify that
component-only number as the 3-point MACE effect.  Root cause on the pre-fix tree: the
selector classified the WHOLE abstract (which mentions the 3-point definition) and attached
that classification to a number extracted from a single component sentence.

Same family: `eligible = exact or near` admitted a 4-point MACE composite (extra component)
with no composite-mismatch refusal on the target-endpoint route.

Every plant here was run against the pre-fix tree (main 3f8add72) and ACCEPTED; the
assertions below encode the requirement, not the behaviour the code happened to have.
Synthetic identifiers and numbers are fixtures, not research findings.  Fixture syntax: the
component sentence uses the topic keyword phrase "death from cardiovascular causes" so that the
legacy sentence selector reaches it (a "died from" phrasing is never selected and so never
reaches the classifier -- a parser miss, not a refusal).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _families import eligible_by_construction  # noqa: E402  (families ELIGIBLE by construction: the admission gate is on by default)

from harness import pipeline  # noqa: E402
from harness import target_endpoint as TE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _json(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _glp1_spec():
    topic = _json("topics/glp1-ra-mace-t2d.json")
    return topic, topic["primary_outcome"], topic["intervention_terms"], topic["comparator_terms"]


COMPONENT_ONLY_ABSTRACT = (
    "BACKGROUND: The cardiovascular effect of examplutide, a glucagon-like peptide 1 receptor "
    "agonist, in patients with type 2 diabetes is unknown. METHODS: In this double-blind trial, we "
    "randomly assigned patients with type 2 diabetes and high cardiovascular risk to receive "
    "examplutide or placebo. The primary outcome was 3-point MACE, a composite of death from "
    "cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke. RESULTS: A total of "
    "4000 patients underwent randomization. The rate of death from cardiovascular causes was lower in "
    "the examplutide group than in the placebo group (hazard ratio, 0.50; 95% CI, 0.30 to 0.80; P=0.001). "
    "CONCLUSIONS: Examplutide reduced death from cardiovascular causes among patients with type 2 "
    "diabetes. (Funded by Example Pharma; EXAMPLE ClinicalTrials.gov number, NCT09999901.)"
)

FOUR_POINT_ABSTRACT = (
    "BACKGROUND: The cardiovascular effect of examplutide, a glucagon-like peptide 1 receptor "
    "agonist, in patients with type 2 diabetes is unknown. METHODS: In this double-blind trial, we "
    "randomly assigned patients with type 2 diabetes to receive examplutide or placebo. The primary "
    "composite outcome was the first occurrence of death from cardiovascular causes, nonfatal "
    "myocardial infarction, nonfatal stroke, or hospitalization for unstable angina. RESULTS: A total "
    "of 4000 patients underwent randomization. The primary outcome occurred in 200 of 2000 patients in "
    "the examplutide group and in 250 of 2000 in the placebo group (hazard ratio, 0.80; 95% CI, 0.66 "
    "to 0.96). CONCLUSIONS: Examplutide reduced major adverse cardiovascular events. (Funded by "
    "Example Pharma; EXAMPLE ClinicalTrials.gov number, NCT09999902.)"
)


def _build(abstract, pmid="99999901"):
    topic, spec, interv, comp = _glp1_spec()
    included = [{"id": pmid, "id_type": "pmid", "label": "PLANT"}]
    rec_by_id = {pmid: {"id": pmid, "abstract": abstract, "acronym": "PLANT"}}
    return pipeline._build_outcome(spec, "primary", included, rec_by_id, interv, comp, family_nodes=eligible_by_construction(rec_by_id))


def _pooled_rows(outcome):
    return outcome.get("trials") or []


def _refused_rows(outcome):
    return outcome.get("declared_absent_trials") or []


# --- plant 1: component-only result certified as the composite -------------------------------

def test_component_only_result_is_not_selected_as_target_endpoint():
    _, spec, interv, comp = _glp1_spec()
    pick = TE.select_target_endpoint(spec, COMPONENT_ONLY_ABSTRACT, None, interv, comp)
    sel = pick.get("selected")
    # pre-fix: sel == {'effect': 0.5, 'target_endpoint_class': 'EXACT_TARGET', components CV death/MI/stroke}
    assert sel is None or sel.get("effect") != 0.5, sel
    assert not pick.get("exact_target_in_held_source")


def test_component_only_result_is_refused_by_the_outcome_builder():
    outcome = _build(COMPONENT_ONLY_ABSTRACT)
    pooled = _pooled_rows(outcome)
    assert pooled == [], pooled  # pre-fix: one row, effect 0.5, EXACT_TARGET, verified
    refused = _refused_rows(outcome)
    assert len(refused) == 1, refused
    reason = json.dumps(refused[0]).lower()
    assert "cardiovascular death" in reason or "component" in reason, refused[0]


# --- plant 2: 4-point composite admitted as 3-point via `exact or near` ----------------------

def test_four_point_composite_is_not_pooled_under_the_three_point_label():
    outcome = _build(FOUR_POINT_ABSTRACT, pmid="99999902")
    pooled = _pooled_rows(outcome)
    assert pooled == [], pooled  # pre-fix: one row, effect 0.80, NEAR_MATCH (extra: unstable angina)
    refused = _refused_rows(outcome)
    assert len(refused) == 1, refused
    reason = json.dumps(refused[0]).lower()
    assert "unstable angina" in reason or "4-point" in reason or "extra" in reason, refused[0]


# --- the two served rows whose class was polluted by the whole-document classification -------

def test_leader_and_exscel_bind_to_their_own_definition_span():
    """LEADER (27295427) and EXSCEL (28910237) both define the primary composite as CV death /
    nonfatal MI / nonfatal stroke and report the composite HR (0.87 / 0.91).  Their abstracts also
    mention hospitalization for heart failure as a SECONDARY outcome, which the whole-document
    classification read as an extra component (served class NEAR_MATCH).  Bound to the definition
    span they are EXACT_TARGET with the same numbers."""
    _, spec, interv, comp = _glp1_spec()
    records = _json("cache/glp1-ra-mace-t2d/records.json")
    by_id = {str(r["id"]): r for r in records["records"]}
    expected = {"27295427": (0.87, 0.78, 0.97), "28910237": (0.91, 0.83, 1.00)}
    for pmid, (eff, lo, hi) in expected.items():
        sel = TE.select_target_endpoint(spec, by_id[pmid]["abstract"], None, interv, comp)["selected"]
        assert sel is not None, pmid
        assert (sel["effect"], sel["ci_low"], sel["ci_high"]) == (eff, lo, hi), (pmid, sel)
        assert sel["target_endpoint_class"] == TE.EXACT_TARGET, (pmid, sel)
        assert sel["target_endpoint_extra_components"] == [], (pmid, sel)
        assert sel.get("endpoint_definition_span"), (pmid, sel)
        assert sel.get("endpoint_result_span"), (pmid, sel)


def test_glp1_served_primary_rows_unchanged_in_number():
    """The seven abstract-route glp1 rows keep their numbers; only the two polluted classes move."""
    _, spec, interv, comp = _glp1_spec()
    records = _json("cache/glp1-ra-mace-t2d/records.json")
    by_id = {str(r["id"]): r for r in records["records"]}
    served = _json("docs/reviews/glp1-ra-mace-t2d/review.json")
    rows = [t for t in served["outcomes"][0]["trials"] if t.get("provenance") == "abstract"]
    from _contracts import partition
    outcome = served["outcomes"][0]
    partition(ROOT, "glp1-ra-mace-t2d", outcome)
    assert rows, "keep a controlled abstract-route fixture if the admitted pool empties"
    for absent in outcome.get("declared_absent_trials", []):
        if absent.get("provenance") == "abstract" and absent.get("admission_verdict"):
            pmid = absent["id"].replace("PMID ", "")
            sel = TE.select_target_endpoint(spec, by_id[pmid]["abstract"], None, interv, comp)["selected"]
            assert sel is not None and sel["target_endpoint_class"] == TE.EXACT_TARGET
            assert all(absent["candidate_tuple"][key] == sel[key] for key in ("effect", "ci_low", "ci_high"))
    for row in rows:
        pmid = row["id"].replace("PMID ", "")
        sel = TE.select_target_endpoint(spec, by_id[pmid]["abstract"], None, interv, comp)["selected"]
        assert sel is not None, pmid
        assert (sel["effect"], sel["ci_low"], sel["ci_high"]) == (row["effect"], row["ci_low"], row["ci_high"]), pmid
        assert sel["target_endpoint_class"] == TE.EXACT_TARGET, (pmid, sel)


# --- typing rules added alongside the binding (each had a live instance on the iv-iron page) -------

def test_registry_count_of_participants_under_an_event_count_title_is_a_typed_unit_conflict():
    """HEART-FID (NCT03037931): CT.gov declares COUNT_OF_PARTICIPANTS for 'Number of Hospitalizations for
    Heart Failure' (297/1532 vs 332/1533) while the publication reports the same integers as
    hospitalisations. A recurrent-event count must not be reconstructed as a binary participant count."""
    from harness.ctgov_results import _registry_measure_type
    om = {"paramType": "COUNT_OF_PARTICIPANTS", "title": "Number of Hospitalizations for Heart Failure"}
    assert _registry_measure_type(om, None, [], "") == "UNIT_CONFLICT_EVENTS_VS_PARTICIPANTS"
    om2 = {"paramType": "COUNT_OF_PARTICIPANTS", "title": "Number of Participants With Hospitalization for Heart Failure"}
    assert _registry_measure_type(om2, None, [], "") == "COUNT_OF_PARTICIPANTS"


def test_registry_measure_analysed_as_recurrent_event_is_a_recurrent_event_estimand():
    """AFFIRM-AHF (NCT02937454) row #2: 'HF hospitalisations ... analysed as recurrent event' is a
    recurrent-event estimand, not a first-event count, and must classify as a different component set."""
    comps = TE._components_from_text("HF Hospitalisations HF = Heart Failure HF hospitalisations up to 52 weeks "
                                     "after randomisation analysed as recurrent event.")
    assert "recurrent events" in comps
    assert "recurrent events" not in TE._components_from_text(
        "HF Hospitalisations Number of participants with at least one HF Hospitalisation up to 52 weeks")


# --- correction of increment 1 (237e9094): a named endpoint with no definition span must be UNBOUND -------------

def test_strength_five_point_primary_is_not_bound_to_the_conclusions_sentence():
    """STRENGTH (omega3, PMID 33190147): 'The primary efficacy MEASURE was a composite of cardiovascular death, nonfatal
    myocardial infarction, nonfatal stroke, coronary revascularization, or unstable angina requiring hospitalization.'
    The 237e9094 binder did not recognise 'measure' as a definition and FELL BACK to every definition sentence, binding
    the 'primary end point' result (HR 0.99) to the CONCLUSIONS sentence that names MACE -- served as EXACT_TARGET 3-point.
    Post-fix: the definition is the 5-point sentence (NEAR_MATCH, extra components) and the abstract row is refused; the
    registry's 3-point 'Composite of CV Events' (its own definition names CV death / MI / stroke) is the exact target."""
    topic = _json("topics/omega3-cardiovascular-events.json")
    records = _json("cache/omega3-cardiovascular-events/records.json")
    rec = next(r for r in records["records"] if str(r["id"]) == "33190147")
    spec, interv, comp = topic["primary_outcome"], topic["intervention_terms"], topic["comparator_terms"]
    b = TE.bind_result_span(rec["abstract"], next(s for s in rec["abstract"].split(". ") if s.startswith("The primary end point occurred")))
    assert b["binding"] != TE.BINDING_NONE
    assert "unstable angina" in b["components"] and "coronary revascularization" in b["components"], b
    assert "CONCLUSIONS" not in (b["endpoint_definition_span"] or ""), b
    pick = TE.select_target_endpoint(spec, rec["abstract"], (records.get("ctgov_results") or {}).get(rec.get("nct")), interv, comp)
    sel = pick["selected"]
    assert sel and sel["provenance"] == "ctgov_results" and sel["target_endpoint_class"] == TE.EXACT_TARGET, sel
    assert sel["effect"] != 0.99
    abstract_alts = [a for a in pick["candidates"] if a.get("source_type") == "abstract"]
    assert abstract_alts and all(a.get("target_endpoint_class") == TE.NEAR_MATCH for a in abstract_alts), abstract_alts


def test_named_endpoint_without_definition_is_unbound_not_borrowed():
    """ORIGIN-style: primary = CV death; result sentence reports 'major vascular events'. Pre-fix the binder borrowed the
    CV-death definition (a component) and refused the composite; post-fix the result is UNBOUND on the abstract route."""
    abstract = ("METHODS: We randomly assigned patients to n-3 fatty acids or placebo. The primary outcome was death from "
                "cardiovascular causes. RESULTS: The use of n-3 fatty acids had no significant effect on the rates of major "
                "vascular events (1034 patients [16.5%] vs. 1017 patients [16.3%]; hazard ratio, 1.01; 95% CI, 0.93 to 1.10).")
    b = TE.bind_result_span(abstract, "The use of n-3 fatty acids had no significant effect on the rates of major vascular events (1034 patients [16.5%] vs. 1017 patients [16.3%]; hazard ratio, 1.01; 95% CI, 0.93 to 1.10).")
    assert b["binding"] == TE.BINDING_NONE and "no definition span" in b["binding_reason"], b
