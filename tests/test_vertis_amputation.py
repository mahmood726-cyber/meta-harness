"""VERTIS CV amputation (PMID 32966714), SGLT2 review (served review_sha256 070466d62c..., pinned at 6260e70c): 54 at 5 mg, 57 at
15 mg vs 45 placebo, refused EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH for an HR analysis; the pre-fix auditor called the refusal false by
quoting the same counts. Patient counts never establish a time-to-event HR -> REASON_NOT_DISPROVED. Same class as AMPLIFY (the
measure is part of the identity); also: a three-arm sentence is never paired dose-against-dose."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import pipeline, reason_audit  # noqa: E402

SERVED, PREFIX, SLUG, VERTIS = "6260e70c", "23642e0d", "sglt2-primary-prevention-hf", "32966714"


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def served():
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    o = next(x for x in rv["outcomes"] if x["name"] == "Lower-limb amputation")
    row = next(a for a in o["declared_absent_trials"] if VERTIS in str(a.get("id")))
    spec = {**(specs.get(o["name"]) or {}), "target_population": rv.get("question")}
    return rv, o, row, spec, reason_audit.sources_by_trial(SLUG, recs, ROOT)[VERTIS]


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_vertis", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def test_served_refusal_and_its_audit(served):
    rv, o, row, _, _ = served
    cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/CERTIFICATE.json"))
    assert cert["review_sha256"].startswith("070466d62c")
    assert o["estimand"] == "HR" and row["reason_code"] == "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH"
    assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD" and "54 patients" in row["reason_code_audit"]["source_span"]


def test_PLANT_prefix_auditor_called_it_false_by_quoting_the_same_counts(served, prefix_auditor):
    _, o, row, spec, srcs = served
    assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


def test_patient_counts_never_establish_a_time_to_event_hr(served):
    _, o, row, spec, srcs = served
    assert reason_audit.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_NOT_DISPROVED"
    amp = [c for c in reason_audit.typed_candidates(o, row, srcs, spec) if "mputation" in c["span"]]
    assert amp and all(any(m.startswith("effect_measure:") and m.endswith("!=HR") for m in c["mismatch"]) for c in amp)


def test_a_three_arm_sentence_is_never_paired_dose_against_dose(served):
    _, o, row, spec, srcs = served
    pairs = [[a.get("events") for a in (c.get("arms") or [])] for c in reason_audit.typed_candidates(o, row, srcs, spec)
             if "mputation" in c["span"]]
    assert [54, 57] not in pairs and [57, 54] not in pairs
