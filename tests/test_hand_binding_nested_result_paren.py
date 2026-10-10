"""A result parenthesis that itself holds brackets still owns its clause (V14-02, CARMELINA hHF).

CARMELINA's hHF paper (PMID 30586723) prints three results in one sentence; the first parenthesis holds its own
brackets ('(209/3494 [6.0%] versus 226/3485 [6.5%], respectively; hazard ratio [HR], 0.90; 95% CI, 0.74-1.08)').
The result-parenthesis pattern refused nested brackets, so OUR result was never located, the whole sentence --
including 'the composite of cardiovascular death/hHF' -- was bound, and a first-event hHF HR was refused as a
superset composite. The owning clause is the text attached to our result only.
"""
from harness import hand_binding as hb
from harness import target_endpoint as te

SENTENCE = ("Linagliptin versus placebo did not affect the incidence of hHF (209/3494 [6.0%] versus 226/3485 [6.5%], "
            "respectively; hazard ratio [HR], 0.90; 95% CI, 0.74-1.08), the composite of cardiovascular death/hHF (HR, "
            "0.94; 95% CI, 0.82-1.08), or risk for recurrent hHF events (326 versus 359 events, respectively; rate ratio, "
            "0.94; 95% CI, 0.75-1.20).")
SPEC = {"name": "Hospitalization for heart failure", "estimand": "HR",
        "keywords": ["hospitalization for heart failure", "hospitalized for heart failure"]}


def _names(x):
    return bool(te._components_from_text(x, expand_named_composites=False) or te._NAMED_COMPOSITE_RX.search(x.lower())
                or hb._family_match_tolerant(SPEC, x))


def test_nested_bracket_result_owns_only_its_clause():
    tup = {"kind": "effect", "effect": 0.9, "ci_low": 0.74, "ci_high": 1.08, "scale": "HR"}
    clause = hb._owning_clause(SENTENCE, tup, _names)
    assert clause.startswith("Linagliptin versus placebo did not affect the incidence of hHF")
    assert clause.endswith("0.74-1.08)")
    assert "cardiovascular death" not in clause


def test_second_result_still_owned_by_the_composite():
    tup = {"kind": "effect", "effect": 0.94, "ci_low": 0.82, "ci_high": 1.08, "scale": "HR"}
    clause = hb._owning_clause(SENTENCE, tup, _names)
    assert clause.startswith("the composite of cardiovascular death/hHF")
    assert "incidence of hHF (209" not in clause


def test_ownership_classifies_the_hhf_result_exact():
    cand = {"kind": "sentence", "text": SENTENCE}
    tup = {"kind": "effect", "effect": 0.9, "ci_low": 0.74, "ci_high": 1.08, "scale": "HR"}
    out = hb._ownership(SPEC, cand, SENTENCE, tup)
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out


def test_enclosing_parenthesis_with_two_results_splits():
    """codex v14-apply-r1 g1#1: an ENCLOSING parenthesis holding two results is two results, not one."""
    s = ("Results (death decreased (HR 0.70; 95% CI 0.60-0.80), whereas stroke was unchanged "
         "(HR 1.00; 95% CI 0.90-1.10)).")
    assert [m.group(0) for m in hb._result_parens(s)] == ["(HR 0.70; 95% CI 0.60-0.80)", "(HR 1.00; 95% CI 0.90-1.10)"]


def test_split_enclosing_paren_keeps_point_estimate_outside_the_ci_bracket():
    """agy v14-apply-r1-agy #1: '(Trial A HR 1.0 [95% CI 0.5-2.0] and Trial B HR 1.2 [95% CI 0.6-2.4])' splits into
    the two CI brackets; the owning segment must still carry the point estimate printed before its bracket."""
    s = "Outcomes differed (Trial A HR 1.0 [95% CI 0.5-2.0] and Trial B HR 1.2 [95% CI 0.6-2.4])."
    tup = {"kind": "effect", "effect": 1.2, "ci_low": 0.6, "ci_high": 2.4, "scale": "HR"}
    clause = hb._owning_clause(s, tup, lambda x: "trial" in x.lower())
    assert "Trial B HR 1.2" in clause and "Trial A" not in clause, clause
