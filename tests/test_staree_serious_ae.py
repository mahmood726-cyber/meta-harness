"""STAREE (PMID 42670961), statins-older-adults review (pinned at 6260e70c): the muscle-symptom and incident-diabetes refusals were
marked REASON_FALSE_VALUE_HELD by citing the aggregate SERIOUS-AE sentence (131 vs 129) plus a qualitative 'diabetes-related events
more common'. All serious AEs are not muscle symptoms, and 'diabetes-related events' are not incident diabetes -> REASON_NOT_DISPROVED."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import pipeline, reason_audit  # noqa: E402

SERVED, PREFIX, SLUG, STAREE = "6260e70c", "23642e0d", "statins-primary-prevention-elderly", "42670961"
OUTCOMES = ("Muscle symptoms/myopathy", "New-onset diabetes")


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def served():
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    srcs = reason_audit.sources_by_trial(SLUG, recs, ROOT)[STAREE]
    rows = {}
    for name in OUTCOMES:
        o = next(x for x in rv["outcomes"] if x["name"] == name)
        row = next(a for a in o["declared_absent_trials"] if STAREE in str(a.get("id")))
        rows[name] = (o, row, {**(specs.get(name) or {}), "target_population": rv.get("question")})
    return rows, srcs


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_staree", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def test_served_audits_cite_the_serious_ae_sentence(served):
    rows, _ = served
    for name in OUTCOMES:
        _, row, _ = rows[name]
        au = row["reason_code_audit"]
        assert au["verdict"] == "REASON_FALSE_VALUE_HELD" and "Serious adverse events occurred in 131" in au["source_span"]


def test_PLANT_prefix_auditor_called_both_refusals_false(served, prefix_auditor):
    rows, srcs = served
    for name in OUTCOMES:
        o, row, spec = rows[name]
        assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


def test_all_serious_aes_are_not_muscle_symptoms_nor_incident_diabetes(served):
    rows, srcs = served
    for name in OUTCOMES:
        o, row, spec = rows[name]
        assert reason_audit.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_NOT_DISPROVED", name
        sae = [c for c in reason_audit.typed_candidates(o, row, srcs, spec) if "131" in c["span"]]
        assert sae and all(c["mismatch"] for c in sae), name              # the 131 vs 129 SAE totals are never a full match
        assert all(c.get("definition") in ("RESTRICTED",) or "outcome" in c["mismatch"] for c in sae), name


def test_a_qualitative_diabetes_related_statement_is_not_incident_diabetes(served):
    rows, srcs = served
    o, row, spec = rows["New-onset diabetes"]
    for c in reason_audit.typed_candidates(o, row, srcs, spec):
        if "diabetes-related" in c["span"] and not c["mismatch"]:
            raise AssertionError(f"a 'diabetes-related events' statement was accepted as incident diabetes: {c['span'][:120]}")
