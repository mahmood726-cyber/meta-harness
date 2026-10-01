"""The audit evidence must match the refusal's outcome / measure / unit, or the verdict is REASON_NOT_DISPROVED (Mahmood, from the
STAREE fixture: an aggregate serious-AE sentence cited against muscle-symptom and incident-diabetes refusals). Pinned to the served
reviews (6260e70c); the pre-fix auditor is loaded from git (23642e0d). Each row below is a served REASON_FALSE_VALUE_HELD whose cited
evidence is an AGGREGATE (any-AE / serious-AE / non-serious-AE total) for a specific outcome, or a single symptom that read as any-AE
through a glued section heading. The corpus-wide count is outputs/refusal_audit/FALSE_AUDIT_BASIS (scripts/false_audit_basis.py)."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import pipeline, reason_audit  # noqa: E402

SERVED, PREFIX = "6260e70c", "23642e0d"
CASES = [  # (review, outcome, trial, what the served audit cited)
    ("statins-primary-prevention-elderly", "Muscle symptoms/myopathy", "42670961", "serious-AE total"),
    ("statins-primary-prevention-elderly", "New-onset diabetes", "42670961", "serious-AE total"),
    ("colchicine-postop-af", "Treatment discontinuation", "25172965", "any-AE total"),
    ("colchicine-postop-af", "Gastrointestinal adverse effects", "25172965", "any-AE total"),
    ("dpp4-mace-t2d", "Acute pancreatitis", "30418475", "any-AE total"),
    ("probiotics-aad-prevention", "Serious adverse events", "22371721", "non-serious-AE total"),
    ("tocilizumab-covid19-mortality", "Serious adverse events", "40232661", "any-AE total"),
    ("tocilizumab-covid19-mortality", "Serious adverse events", "33472855", "any-AE total"),
    ("probiotics-aad-prevention", "Any adverse events", "21165295", "one symptom under a glued 'Adverse events' heading"),
]


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_match", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def _case(slug, outcome, trial):
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{slug}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    o = next(x for x in rv["outcomes"] if x["name"] == outcome)
    row = next(a for a in o["declared_absent_trials"] if reason_audit.canonical_trial_id(a.get("id") or a.get("label")) == trial)
    spec = {**(specs.get(outcome) or {}), "target_population": rv.get("question")}
    return o, row, spec, reason_audit.sources_by_trial(slug, recs, ROOT).get(trial, [])


@pytest.mark.parametrize("slug, outcome, trial, cited", CASES)
def test_PLANT_served_and_prefix_auditor_call_it_false_on_non_matching_evidence(slug, outcome, trial, cited, prefix_auditor):
    o, row, spec, srcs = _case(slug, outcome, trial)
    assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD"            # as served
    assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


@pytest.mark.parametrize("slug, outcome, trial, cited", CASES)
def test_evidence_that_does_not_match_the_refusal_is_not_disproof(slug, outcome, trial, cited):
    o, row, spec, srcs = _case(slug, outcome, trial)
    assert reason_audit.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_NOT_DISPROVED", cited
    # and the span the served audit cited is never a full match on its own
    cited_span = row["reason_code_audit"]["source_span"].rstrip(".").removesuffix("...")
    cands = reason_audit.typed_candidates(o, row, [{"source_id": "served-citation", "text": cited_span}], spec)
    assert not [c for c in cands if not c["mismatch"]], cited
