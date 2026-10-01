"""The effect measure is part of the identity match (DOAC-VTE review, AMPLIFY PMID 23808982). Major bleeding RR 0.31 (0.17-0.55) and
major/CRNM RR 0.44 (0.36-0.55) were refused EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH (RR held, HR requested); the pre-fix auditor called
both refusals FALSE because an RR exists. A valid disproof must show the REQUESTED measure, or that the committed analysis spec
permits the reported one. The review is read PINNED at the commit that served it (6260e70c); the pre-fix auditor from git."""
import copy
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, pipeline, reason_audit  # noqa: E402

SERVED, PREFIX_AUDITOR, SLUG, AMPLIFY = "6260e70c", "23642e0d", "doac-vte-recurrence", "23808982"
OUTCOMES = ("Major bleeding", "Major or clinically relevant nonmajor bleeding")


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def served():
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    srcs = reason_audit.sources_by_trial(SLUG, recs, ROOT)[AMPLIFY]
    rows = {}
    for o in rv["outcomes"]:
        if o["name"] in OUTCOMES:
            rows[o["name"]] = (o, next(a for a in o["declared_absent_trials"] if AMPLIFY in a["id"]), specs.get(o["name"]) or {})
    return rows, srcs


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX_AUDITOR}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_measure", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX_AUDITOR}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def test_served_rows_are_the_refusals_the_fixture_names(served):
    rows, _ = served
    for name in OUTCOMES:
        o, row, _ = rows[name]
        assert o["estimand"] == "HR" and row["reason_code"] == "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH"
        assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD"          # the defect, as served


def test_PLANT_prefix_auditor_calls_both_refusals_false_because_an_rr_exists(served, prefix_auditor):
    rows, srcs = served
    for name in OUTCOMES:
        o, row, spec = rows[name]
        assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


def test_an_rr_does_not_disprove_a_refusal_that_requests_an_hr(served):
    """Each outcome's OWN held RR (major bleeding 0.31; the major/CRNM composite 0.44) is examined and rejected on the measure. (The
    0.31 sentence is not evidence about the composite, and since naming needs half of the outcome's own words it is no longer
    examined for it -- the requirement is about each outcome's own result, not that every RR appears everywhere.)"""
    rows, srcs = served
    for name, own in (("Major bleeding", 0.31), ("Major or clinically relevant nonmajor bleeding", 0.44)):
        o, row, spec = rows[name]
        got = reason_audit.audit_reason_row(o, row, srcs, spec)
        assert got["verdict"] == "REASON_NOT_DISPROVED", got
        full = reason_audit.typed_candidates(o, row, srcs, spec)
        rr = [c for c in full if c.get("effect_measure") == "RR"]
        assert own in {c["estimate"] for c in rr}
        assert all("effect_measure:RR!=HR" in c["mismatch"] for c in rr)


def test_the_measure_rule_is_what_decides_not_a_masking_timepoint(served):
    """'trial-reported follow-up' defers to the trial and constrains nothing; it must not add a timepoint mismatch that would keep the
    verdict NOT_DISPROVED even if the measure rule were broken."""
    rows, srcs = served
    o, row, spec = rows["Major bleeding"]
    full = reason_audit.typed_candidates(o, row, srcs, spec)
    assert not [m for c in full for m in c["mismatch"] if m.startswith("timepoint")]
    assert ei._timepoint_in("trial-reported follow-up", None) and not ei._timepoint_in("28 days", None)


def test_the_requested_measure_would_disprove_it():
    """Same span with the REQUESTED measure: the measure mismatch disappears (the valid route to a disproof)."""
    claim = {"part": "COMPONENT", "timepoint": "trial-reported follow-up", "population": None, "effect_measure": "HR"}
    s = "Major bleeding occurred in 0.6% vs 1.8% of patients in the two groups ({m}, 0.31; 95% CI, 0.17 to 0.55)."
    rr = ei.from_sentence(s.format(m="relative risk"), "t", "x")
    hr = ei.from_sentence(s.format(m="hazard ratio"), "t", "x")
    assert "effect_measure:RR!=HR" in ei.mismatches(rr, claim, True)
    assert not [m for m in ei.mismatches(hr, claim, True) if m.startswith("effect_measure")]


def test_a_spec_that_permits_the_reported_measure_is_the_other_valid_route(served):
    rows, srcs = served
    o, row, spec = rows["Major bleeding"]
    permitting = copy.deepcopy(spec)
    permitting["permitted_measures"] = ["RR"]
    full = reason_audit.typed_candidates(o, row, srcs, permitting)
    rr = [c for c in full if c.get("effect_measure") == "RR"]
    assert rr and not [m for c in rr for m in c["mismatch"] if m.startswith("effect_measure")]
