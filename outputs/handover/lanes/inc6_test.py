"""Independent read (agy, 18 Sep 2026 21:46) of the served omega3 page at 237e9094: REDUCE-IT (PMID 30415628) is pooled at
HR 0.74 (0.65-0.83) from ClinicalTrials.gov, but its bound `endpoint_result_span` is the outcome-measure TITLE
("ClinicalTrials.gov outcome measure #1: Composite of CV Death, Nonfatal MI ...") -- a span that carries no number. The
e3014d02 rule is that every effect is bound to its OWN result span; a registry row's result is the registry ANALYSIS
(param type, value, CI, method -- verbatim strings), or, for a reconstruction, the arm counts it is derived from. Six
registry-bound pooled rows across the corpus carried a number their span does not (census on 237e9094: dapagliflozin-hfpef,
empagliflozin-hfpef, omega3 REDUCE-IT, pcsk9 FOURIER, sacubitril PARALLEL-HF, sglt2-hfref DAPA-HF).

Requirement: for every pooled row bound as `registry_outcome_measure`, the displayed estimate and both CI bounds appear
verbatim in `endpoint_result_span` (analysis rows), or the span carries the arm counts the effect is reconstructed from
(reconstruction rows). Plant: on 237e9094 the corpus test fails with those six rows; the unit test fails on the title-only span.
"""
import json
import pathlib
import re

from harness import target_endpoint as te

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _num_in(value, span):
    if value is None:
        return True
    f = float(value)
    forms = {f"{f:g}", f"{f:.1f}", f"{f:.2f}", f"{f:.3f}", f"{f:.4f}"}
    return any(re.search(r"(?<![\d.])" + re.escape(x) + r"(?![\d])", span) for x in forms)


def _registry_rows():
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        for outcome in review.get("outcomes") or []:
            for row in outcome.get("trials") or []:
                if row.get("endpoint_binding") == te.BINDING_REGISTRY:
                    yield path.parent.name, row


def test_every_pooled_registry_row_shows_its_number_in_its_result_span():
    bad = []
    for slug, row in _registry_rows():
        span = row.get("endpoint_result_span") or ""
        if row.get("source_kind") == te.RECONSTRUCTION:
            ok = all(str(row.get(k)) in span for k in ("ai", "n1i", "ci", "n2i") if row.get(k) is not None)
        else:
            ok = all(_num_in(row.get(k), span) for k in ("effect", "ci_low", "ci_high"))
        if not ok:
            bad.append((slug, row.get("label"), span[:80]))
    assert bad == [], bad


def test_registry_analysis_candidate_binds_the_analysis_not_the_title():
    spec = {"name": "3-point MACE", "components": ["cardiovascular death", "myocardial infarction", "stroke"],
            "keywords": ["MACE", "major adverse cardiovascular"]}
    om = {"type": "PRIMARY", "title": "Composite of CV Death, Nonfatal MI, or Nonfatal Stroke", "paramType": "NUMBER",
          "analyses": [{"groupIds": ["OG000", "OG001"], "groupDescription": "For Primary Composite",
                        "statisticalMethod": "Regression, Cox", "paramType": "Hazard Ratio (HR)", "paramValue": "0.74",
                        "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "0.65", "ciUpperLimit": "0.83"}]}
    cands = te._ctgov_candidates([om], spec, ["icosapent"], ["placebo"])
    assert len(cands) == 1
    span = cands[0]["endpoint_result_span"]
    assert "0.74" in span and "0.65" in span and "0.83" in span and "For Primary Composite" in span
    assert "Hazard Ratio (HR)" in span and "Regression, Cox" in span
    assert cands[0]["endpoint_definition_span"].startswith("Composite of CV Death")
