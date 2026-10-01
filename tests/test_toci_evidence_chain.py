"""REASON_NOT_DISPROVED fixtures from the tocilizumab COVID review (pinned at 6260e70c; pre-fix auditor from git 23642e0d).
The evidence must match the refusal's OUTCOME + TIMEPOINT + AGGREGATION LEVEL:
  (a) TOCIBRAS (33472855) 28-day secondary-infection refusal 'disproved' by 'Death at 15 days ... 11 vs 2' -> wrong outcome AND timepoint;
  (b) TOCIBRAS SAE refusal 'disproved' by 'adverse events ... 29 of 67 vs 21 of 62' -> an any-AE total, not the serious aggregate;
  (c) another trial (33085857) SAE refusal 'disproved' by neutropenia / serious infections -> components, not the aggregate.
A correct recovery route elsewhere (WHO REACT: TOCIBRAS secondary infections 10/65 vs 10/64, OR 0.9818 (0.3784-2.5477)) does NOT
validate the wrong evidence chain: it is reported as a recovery route, beside a chain verdict that stays NOT_DISPROVED."""
import importlib.util
import json
import math
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, pipeline, reason_audit  # noqa: E402

SERVED, PREFIX, SLUG = "6260e70c", "23642e0d", "tocilizumab-covid19-mortality"
CASES = {"a": ("Secondary infections by 28 days", "33472855", {"outcome", "timepoint"}),
         "b": ("Serious adverse events", "33472855", {"outcome", "attribution"}),
         "c": ("Serious adverse events", "33085857", {"outcome"})}
# TEST FIXTURE -- the WHO REACT route as a sentence (the plot itself is not a held source here)
WHO_REACT_ROUTE = ("Secondary infections by day 28 occurred in 10 of 65 patients in the tocilizumab group and in 10 of 64 patients in the "
                   "standard care group (odds ratio, 0.98; 95% CI, 0.38 to 2.55).")


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def ctx():
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    srcs = reason_audit.sources_by_trial(SLUG, recs, ROOT)
    out = {}
    for k, (name, trial, _) in CASES.items():
        o = next(x for x in rv["outcomes"] if x["name"] == name)
        row = next(a for a in o["declared_absent_trials"] if reason_audit.canonical_trial_id(a.get("id") or a.get("label")) == trial)
        out[k] = (o, row, {**(specs.get(name) or {}), "target_population": rv.get("question")}, srcs.get(trial, []))
    return out


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_toci", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


@pytest.mark.parametrize("case", sorted(CASES))
def test_PLANT_served_and_prefix_auditor_call_it_false(ctx, prefix_auditor, case):
    o, row, spec, srcs = ctx[case]
    assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD"
    assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_cited_chain_does_not_match_outcome_timepoint_or_aggregation(ctx, case):
    o, row, spec, srcs = ctx[case]
    chain = reason_audit.audit_cited_chain(o, row, row["reason_code_audit"]["source_span"], spec)
    assert chain["chain_verdict"] == "REASON_NOT_DISPROVED"
    assert CASES[case][2] <= set(chain["fails_on"]), chain
    assert reason_audit.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_NOT_DISPROVED"


def test_a_correct_recovery_route_elsewhere_does_not_validate_the_wrong_chain(ctx):
    o, row, spec, _ = ctx["a"]
    routes = reason_audit.recovery_routes(o, row, [{"source_id": "fixture:who-react", "text": WHO_REACT_ROUTE}], spec,
                                          row["reason_code_audit"]["source_span"])
    assert routes and "10 of 65" in routes[0]["span"]                               # the route exists and is reported ...
    chain = reason_audit.audit_cited_chain(o, row, row["reason_code_audit"]["source_span"], spec)
    assert chain["chain_verdict"] == "REASON_NOT_DISPROVED"                        # ... and the served chain is still not disproof


def test_the_route_numbers_reproduce():
    a, n1, c, n2 = 10, 65, 10, 64
    b, d = n1 - a, n2 - c
    or_ = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    z = 1.959963984540054
    assert [round(x, 4) for x in (or_, or_ * math.exp(-z * se), or_ * math.exp(z * se))] == [0.9818, 0.3784, 2.5477]


def test_PLANT_a_component_class_never_names_the_serious_ae_aggregate():
    assert not ei.names_the_outcome("serious infections occurred in 13 of 161 patients vs 14 of 81", "Serious adverse events")
    assert not ei.names_the_outcome("Neutropenia developed in 22 patients vs 1 patient", "Serious adverse events")
    assert ei.names_the_outcome("serious adverse events occurred in 25 vs 16 patients", "Serious adverse events")
    assert ei.names_the_outcome("SAEs were reported in 25 vs 16 patients", "Serious adverse events")
