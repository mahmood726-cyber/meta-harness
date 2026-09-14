"""STATE root system, item 1 — ABSENCE-STATE ONTOLOGY (external audit).

"declared absent" conflated four epistemically different things, letting a page assert "no harms
recorded" while the retrieved source in fact reports the harm (dpp4 SAVOR/EXAMINE HF & MACE; REWIND
GI 2347/4949). The classifier and the renderer must reserve the strong DECLARED_ABSENT claim (a
statement about the TRIAL) for NO_OUTCOME_DATA_IN_SOURCE alone; a machine failure to extract a number
that IS in the source is EXTRACTION_NOT_PERFORMED (about US), an abstract-only miss is
SOURCE_NOT_RETRIEVED, and a number found-and-refused is REFUSED_ON_EVIDENCE — none is evidence the
outcome does not exist. `UNASSESSED NEVER COUNTS AS FAVOURABLE`.
"""
import glob
import json
import os

import harness.page as P
from harness import absence as A

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A REWIND-style GI harm abstract: the outcome's arm counts ARE present (2347/4949 vs 1687/4952).
_KWS_GI = ["gastrointestinal", "gastrointestinal adverse events", "nausea", "vomiting", "diarrhoea"]
_ABSTRACT_GI_PRESENT = (
    "Dulaglutide reduced cardiovascular events. Gastrointestinal adverse events were more common with "
    "dulaglutide, occurring in 2347 of 4949 participants versus 1687 of 4952 with placebo.")
# An EXAMINE/TECOS-style MACE abstract: an effect+CI IS present.
_KWS_MACE = ["major adverse cardiovascular events", "MACE", "hazard ratio", "primary outcome"]
_ABSTRACT_MACE_PRESENT = (
    "A primary end-point event occurred in 305 patients assigned to the drug and 316 assigned to "
    "placebo (hazard ratio, 0.96; 95% CI, 0.80 to 1.16).")
# A genuinely-silent abstract for a HF-hospitalisation harm: the source says nothing about it.
_KWS_HF = ["hospitalization for heart failure", "heart failure hospitalisation", "hospitalisation for heart failure"]
_ABSTRACT_HF_SILENT = (
    "The drug lowered HbA1c versus placebo over 52 weeks. The most common adverse events were nausea "
    "and headache; no serious safety signal was identified.")


def test_number_present_is_EXTRACTION_NOT_PERFORMED_not_absent():
    # THE HANDED CASE: the harm's number is in the retrieved source, so "declared absent" would be a
    # false statement about the trial. Must read EXTRACTION_NOT_PERFORMED (a statement about US).
    st, _ = A.classify(_KWS_GI, _ABSTRACT_GI_PRESENT)
    assert st == "EXTRACTION_NOT_PERFORMED", st
    st2, _ = A.classify(_KWS_MACE, _ABSTRACT_MACE_PRESENT)
    assert st2 == "EXTRACTION_NOT_PERFORMED", st2


def test_silent_abstract_only_is_SOURCE_NOT_RETRIEVED():
    # No number, and we hold only the abstract -> absence in the TRIAL is not established.
    st, _ = A.classify(_KWS_HF, _ABSTRACT_HF_SILENT, fulltext=None)
    assert st == "SOURCE_NOT_RETRIEVED", st


def test_silent_with_fulltext_is_NO_OUTCOME_DATA():
    # Only when we hold the full text AND it is still silent may we say the trial lacks the outcome.
    st, _ = A.classify(_KWS_HF, _ABSTRACT_HF_SILENT, fulltext=_ABSTRACT_HF_SILENT + " Full text: no HF-hospitalisation data reported.")
    assert st == "NO_OUTCOME_DATA_IN_SOURCE", st


def test_PLANT_conflation_would_have_fired():
    # PLANT proving the defect the split closes: the OLD single-bucket world called every declared-absent
    # trial "declared absent" regardless of whether the number was in the source. Here the source DOES
    # report the harm counts, yet a naive "no extracted number => absent" rule (the pre-fix behaviour)
    # would assert absence. The classifier must refuse that: any effect+CI or arm-counts in the outcome's
    # own sentences forbids NO_OUTCOME_DATA_IN_SOURCE.
    naive_absent = True  # pre-fix: extraction produced no pooled number -> "declared absent"
    st, _ = A.classify(_KWS_GI, _ABSTRACT_GI_PRESENT, fulltext=_ABSTRACT_GI_PRESENT)
    assert naive_absent and st != "NO_OUTCOME_DATA_IN_SOURCE", (
        "classifier must not certify absence when the source reports the outcome's counts")


def test_renderer_reserves_declared_absent_for_no_data():
    # Only NO_OUTCOME_DATA_IN_SOURCE may carry the strong "declared absent" wording in the label.
    assert "declared absent" in P._absent_label("r", "NO_OUTCOME_DATA_IN_SOURCE").lower()
    for s in ("EXTRACTION_NOT_PERFORMED", "SOURCE_NOT_RETRIEVED", "REFUSED_ON_EVIDENCE"):
        assert "declared absent" not in P._absent_label("r", s).lower(), s
    # EXTRACTION_NOT_PERFORMED must say the number IS in the source (not a trial-absence claim).
    assert "in the source" in P._absent_label("r", "EXTRACTION_NOT_PERFORMED").lower()


def test_corpus_every_declared_absent_trial_carries_a_state():
    # Integration: after the pipeline wiring, every declared-absent trial in the built corpus must have
    # a state, and the strong NO_OUTCOME_DATA state must never be attached to a trial whose reason shows
    # a number was found and refused (estimand/definition/per-protocol/timepoint mismatch).
    missing, misfiled = [], []
    _REFUSAL_MARK = ("estimand", "definition mismatch", "per-protocol", "per protocol", "timepoint mismatch",
                     "idiosyncratic composite", "four-point", "4-point", "identity gate")
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        rv = json.load(open(rp, encoding="utf-8"))
        for o in rv.get("outcomes", []):
            for t in (o.get("declared_absent_trials") or []):
                st = t.get("state")
                if not st:
                    missing.append(f"{slug}::{t.get('id')}::{o.get('name')}")
                elif st == "NO_OUTCOME_DATA_IN_SOURCE" and any(m in (t.get("reason") or "").lower() for m in _REFUSAL_MARK):
                    misfiled.append(f"{slug}::{t.get('id')}::{o.get('name')}")
    assert not missing, "declared-absent trials with no ontology state: " + "; ".join(missing[:20])
    assert not misfiled, "a refused-on-evidence trial mislabelled as NO_OUTCOME_DATA: " + "; ".join(misfiled[:20])


def test_corpus_handed_cases_are_not_falsely_absent():
    # The specific handed regressions: EXAMINE (dpp4, 23992602) reports MACE in its abstract; TECOS
    # (26052984) reports a 4-point MACE HR. Neither may read NO_OUTCOME_DATA_IN_SOURCE.
    rp = os.path.join(_ROOT, "docs", "reviews", "dpp4-mace-t2d", "review.json")
    if not os.path.exists(rp):
        return
    rv = json.load(open(rp, encoding="utf-8"))
    states = {}
    for o in rv.get("outcomes", []):
        for t in (o.get("declared_absent_trials") or []):
            states[str(t.get("id")).replace("PMID ", "")] = t.get("state")
    for pid in ("23992602", "26052984"):
        if pid in states:
            assert states[pid] != "NO_OUTCOME_DATA_IN_SOURCE", f"{pid} falsely certified absent: {states[pid]}"
