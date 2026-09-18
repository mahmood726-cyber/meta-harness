"""Independent read (agy, Gemini 3.1 Pro, 18 Sep 2026 21:46) of the served omega3 page at 237e9094 -- the first page rebuilt
under the endpoint-binding harness of e3014d02: Alpha Omega (PMID 20929341) is pooled as EXACT_TARGET with components
{CV death, MI, stroke} and no extra component, while its own bound definition span reads "The primary end point was the rate
of major cardiovascular events, which comprised fatal and nonfatal cardiovascular events and cardiac interventions."

Root cause (harness/target_endpoint.py::_components_from_text): the vocabulary recognises none of the enumerated items, so
`comps` is empty, and the named-composite expansion ("a bare MACE with no enumerated components expands to the 3-point set")
fires on a span that DOES enumerate its components -- an unrecognised enumerated component is silently dropped and the family
phrase is expanded into an exact match. Same defect class as ASCEND (refused on the same page for adding TIA) and as the
component-only / superset acceptance the landing closed: the enumeration in the definition span governs; a component the
vocabulary cannot read is an unrecognised EXTRA component, never nothing.

Requirement: when a definition span enumerates components and any enumerated item is unrecognised, the class is not
EXACT_TARGET; the unrecognised items are carried as extra components so the existing admissibility verdict refuses (or admits
only under the outcome's explicit near-match declaration). Plant: on 237e9094 the first two tests fail.
"""
import json
import pathlib

from harness import target_endpoint as te

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALPHA_OMEGA_DEF = ("The primary end point was the rate of major cardiovascular events, which comprised fatal and nonfatal "
                   "cardiovascular events and cardiac interventions.")


def _spec(slug):
    return json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))["primary_outcome"]


def test_alpha_omega_definition_span_is_not_exact_target():
    cls = te._classify(_spec("omega3-cardiovascular-events"), ALPHA_OMEGA_DEF)
    assert cls["target_endpoint_class"] != te.EXACT_TARGET, cls
    extras = " ".join(cls.get("extra_components") or [])
    assert "cardiac interventions" in extras, cls


def test_served_omega3_page_does_not_pool_alpha_omega():
    review = json.loads((ROOT / "docs/reviews/omega3-cardiovascular-events/review.json").read_text(encoding="utf-8"))
    outcome = review["outcomes"][0]
    pooled = {t["label"] for t in outcome["trials"]}
    assert "20929341" not in pooled, "Alpha Omega pooled under the 3-point label"
    refused = {t.get("label") or t.get("id") for t in outcome.get("declared_absent_trials") or []}
    assert any("20929341" in str(x) for x in refused)


def test_unrecognised_enumerated_item_beside_recognised_triple_is_not_exact():
    spec = {"name": "3-point MACE", "components": ["cardiovascular death", "myocardial infarction", "stroke"]}
    span = ("The primary outcome was major adverse cardiovascular events, a composite of cardiovascular death, "
            "myocardial infarction, stroke, and limb amputation.")
    cls = te._classify(spec, span)
    assert cls["target_endpoint_class"] != te.EXACT_TARGET, cls
    assert any("limb amputation" in x for x in cls.get("extra_components") or []), cls


def test_recognised_enumeration_still_classifies_as_before():
    spec = {"name": "3-point MACE", "components": ["cardiovascular death", "myocardial infarction", "stroke"]}
    exact = ("The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, "
             "or nonfatal stroke.")
    assert te._classify(spec, exact)["target_endpoint_class"] == te.EXACT_TARGET
    superset = ("The primary outcome was a composite of cardiovascular death, myocardial infarction, stroke, or "
                "coronary revascularization.")
    cls = te._classify(spec, superset)
    assert cls["target_endpoint_class"] == te.NEAR_MATCH and cls["extra_components"] == ["coronary revascularization"]
    bare = "The primary outcome was 3-point MACE."
    assert te._classify(spec, bare)["target_endpoint_class"] == te.EXACT_TARGET
