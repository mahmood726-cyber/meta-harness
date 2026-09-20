"""Exclusion is a RELATION, not a keyword: mentioning what is excluded must never make it included, and an exclusion inside a
component or of the population must never cut. The panel's fixtures E1-E10 (2026-09-20), each with the definition span set to the
fixture's own sentence as the panel did, plus the document-neighbourhood forms the row's spans cannot carry.

Measured pre-fix (3.14, clause-scoped cutting): E5 and E8 ADMITTED, E9 REFUSED -- 2 false admissions, 1 false refusal of 10.
3.15: row span + definition span, relational -- 10 of 10. 3.16: the document neighbourhood of the located span is searched too."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_bundle  # noqa: E402
import verify_bundle  # noqa: E402

CC = ["CARDIOVASCULAR_DEATH", "MYOCARDIAL_INFARCTION", "STROKE"]
DEFN = "The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke."
T = "(hazard ratio, 0.87; 95% CI, 0.78 to 0.97)"
V = [0.87, 0.78, 0.97]

FIXTURES = {
    "E1": ("The primary outcome was cardiovascular death only, excluding nonfatal myocardial infarction and nonfatal stroke, and occurred less often " + T + ".", "REFUSE"),
    "E2": ("The primary outcome was cardiovascular death and occurred less often " + T + ".", "REFUSE"),
    "E3": ("The primary composite outcome of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke occurred less often " + T + ".", "PASS"),
    "E4": ("The primary outcome was 3-point MACE excluding unstable angina and occurred less often " + T + ".", "PASS"),
    "E5": ("The primary outcome was cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke and occurred less often " + T + ". Nonfatal myocardial infarction and nonfatal stroke were not included in the primary analysis.", "REFUSE"),
    "E6": ("The primary outcome was any cardiovascular event other than nonfatal myocardial infarction or nonfatal stroke, namely cardiovascular death, and occurred less often " + T + ".", "REFUSE"),
    "E7": ("The primary outcome was cardiovascular death " + T + "; neither nonfatal myocardial infarction nor nonfatal stroke contributed.", "REFUSE"),
    "E8": ("The primary outcome of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke occurred less often " + T + ". *Nonfatal myocardial infarction and nonfatal stroke were excluded from the primary analysis.", "REFUSE"),
    "E9": ("The primary composite outcome of cardiovascular death, nonfatal myocardial infarction (excluding silent infarction), or nonfatal stroke occurred less often " + T + ".", "PASS"),
    "E10": ("Patients with a prior stroke were excluded from enrolment. The primary composite outcome of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke occurred less often " + T + ".", "PASS"),
}


def _verdict(r):
    return "PASS" if r["state"] == "PASS" else "REFUSE"


@pytest.mark.parametrize("impl", [build_bundle, verify_bundle], ids=["builder", "verifier"])
@pytest.mark.parametrize("name", list(FIXTURES))
def test_fixture_definition_is_the_fixture_itself(impl, name):
    span, expected = FIXTURES[name]
    r = impl.span_target_mention(span, V, span, CC)
    assert _verdict(r) == expected, (name, r)
    if name in ("E1", "E5", "E7", "E8"):
        assert r["excluded_components"] == ["MYOCARDIAL_INFARCTION", "STROKE"], r
    if name == "E6":
        assert {"MYOCARDIAL_INFARCTION", "STROKE"} <= set(r["excluded_components"]), r
    if name in ("E5", "E8"):
        assert r["exclusion_statements"], r                                   # the statement that cut is quoted
    if name in ("E3", "E4", "E9", "E10"):
        assert not r["excluded_components"], r                                # controls: nothing cut


@pytest.mark.parametrize("name", list(FIXTURES))
def test_fixture_with_the_composite_definition_span(name):
    """The same ten with the row's definition span set to the target composite (the production shape): the exclusion in the
    clause / span must not be rescued by the definition span."""
    span, expected = FIXTURES[name]
    r = build_bundle.span_target_mention(span, V, DEFN, CC)
    assert _verdict(r) == expected, (name, r)


RESULT_ONLY = "The primary outcome occurred less often " + T + "."


def test_exclusion_outside_both_spans_is_read_from_the_document_neighbourhood():
    """The row carries only the result sentence; the footnote lives in the document after it (E8's document form) or the sentence
    before it (E5's). Row-span scope alone cannot see it; the neighbourhood can."""
    doc_after = "The primary composite outcome was cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. " + RESULT_ONLY + " *Nonfatal myocardial infarction and nonfatal stroke were excluded from the primary analysis."
    doc_before = "Nonfatal myocardial infarction and nonfatal stroke were not included in the primary analysis. " + RESULT_ONLY
    for doc in (doc_after, doc_before):
        without = build_bundle.span_target_mention(RESULT_ONLY, V, DEFN, CC)
        assert without["state"] == "PASS"                                     # spans alone: invisible (the hole, stated)
        ctx = build_bundle.document_neighbourhood(RESULT_ONLY, doc)
        assert ctx and RESULT_ONLY in ctx
        with_ctx = build_bundle.span_target_mention(RESULT_ONLY, V, DEFN, CC, context=ctx)
        assert with_ctx["state"] == "ENDPOINT_INCOMPATIBLE" and with_ctx["excluded_components"] == ["MYOCARDIAL_INFARCTION", "STROKE"], with_ctx
        assert "document neighbourhood" in with_ctx["mention"] and with_ctx["exclusion_statements"]
        assert verify_bundle.span_target_mention(RESULT_ONLY, V, DEFN, CC, context=verify_bundle.document_neighbourhood(RESULT_ONLY, doc))["state"] == "ENDPOINT_INCOMPATIBLE"


def test_population_and_other_outcome_exclusions_in_the_neighbourhood_do_not_cut():
    docs = [
        "Patients with a prior stroke were excluded from enrolment. " + RESULT_ONLY,                                        # E10, document form
        RESULT_ONLY + " Participants with a history of myocardial infarction within 60 days were excluded from the trial.",  # population, after
        RESULT_ONLY + " For the secondary renal outcome, stroke was not included in the composite.",                        # another outcome's composite
    ]
    for doc in docs:
        r = build_bundle.span_target_mention(RESULT_ONLY, V, DEFN, CC, context=build_bundle.document_neighbourhood(RESULT_ONLY, doc))
        assert r["state"] == "PASS" and not r["excluded_components"], (doc, r)


def test_neighbourhood_is_none_when_the_span_is_not_located_and_scope_is_reported():
    assert build_bundle.document_neighbourhood("not in the document (hazard ratio, 0.87)", "some abstract text") is None
    r = build_bundle.span_target_mention(RESULT_ONLY, V, DEFN, CC)
    assert r["exclusion_scope_searched"] == ["clause", "row span", "row definition span"]
    r = build_bundle.span_target_mention(RESULT_ONLY, V, DEFN, CC, context=RESULT_ONLY)
    assert len(r["exclusion_scope_searched"]) == 4


def test_split_exclusions_parenthetical_scope_and_analysis_statements():
    inc, exc = build_bundle.split_exclusions("cardiovascular death, nonfatal myocardial infarction (excluding silent infarction), or nonfatal stroke")
    assert exc == "" and "nonfatal myocardial infarction" in inc and "stroke" in inc
    inc, exc = build_bundle.split_exclusions("cardiovascular death (excluding stroke), or nonfatal myocardial infarction")
    assert "stroke" in exc and "stroke" not in inc                                                    # a different component inside the parenthetical IS an exclusion
    ex, stmts = build_bundle.analysis_exclusions("patients with a prior stroke were excluded from enrolment. the primary outcome occurred.")
    assert ex == "" and stmts == []
    ex, stmts = build_bundle.analysis_exclusions("the primary outcome occurred (hazard ratio, 0.87). nonfatal stroke was not included in the primary analysis.")
    assert "stroke" in ex and len(stmts) == 1


def test_both_copies_of_the_binding_block_are_the_same_code():
    import inspect
    for fn in ("split_exclusions", "analysis_exclusions", "span_target_mention", "document_neighbourhood", "clauses", "clause_with_effect"):
        assert inspect.getsource(getattr(build_bundle, fn)) == inspect.getsource(getattr(verify_bundle, fn)), fn
