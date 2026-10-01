"""The counting UNIT is part of the identity (DPP-4 review, CARMELINA PMID 30418475). Acute pancreatitis '9 (0.3%) vs 5 (0.1%) events'
was refused because events may count episodes, not patients; the pre-fix auditor challenged the refusal by pointing at the same
numbers. A refusal about the unit is disproved only by source evidence of the unit (e.g. a safety table's 'n (%)' patients header).
Also: serious and non-serious AE category totals are never summed into 'any AE'.
The review is read PINNED at the commit that served it (6260e70c); the pre-fix auditor from git."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, pipeline, reason_audit  # noqa: E402

SERVED, PREFIX_AUDITOR, SLUG, CARMELINA = "6260e70c", "23642e0d", "dpp4-mace-t2d", "30418475"
# TEST FIXTURE -- not a held source: the same CARMELINA numbers under a safety-table header that states the unit.
UNIT_TABLE = ("<table-wrap><label>Table 3</label><table><thead><tr><th>Adverse event, n (%)</th>"
              "<th>Linagliptin (n = 3494)</th><th>Placebo (n = 3485)</th></tr></thead><tbody>"
              "<tr><td>Acute pancreatitis (adjudication-confirmed)</td><td>9 (0.3)</td><td>5 (0.1)</td></tr>"
              "</tbody></table></table-wrap>")


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def served():
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    o = next(x for x in rv["outcomes"] if x["name"] == "Acute pancreatitis")
    row = next(a for a in o["declared_absent_trials"] if CARMELINA in str(a.get("id")))
    return o, row, specs.get(o["name"]) or {}, reason_audit.sources_by_trial(SLUG, recs, ROOT)[CARMELINA]


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX_AUDITOR}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_unit", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX_AUDITOR}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def test_served_row_is_a_refusal_about_the_unit_and_was_audited_false(served):
    o, row, _, _ = served
    cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/CERTIFICATE.json"))
    assert cert["review_sha256"].startswith("8883510e")
    assert "events, rather than unique patients" in row["reason"]
    assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD"               # the defect, as served


def test_PLANT_prefix_auditor_challenges_the_refusal_with_the_same_numbers(served, prefix_auditor):
    o, row, spec, srcs = served
    assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


def test_the_same_event_counts_cannot_disprove_a_refusal_about_the_unit(served):
    o, row, spec, srcs = served
    got = reason_audit.audit_reason_row(o, row, srcs, spec)
    assert got["verdict"] == "REASON_NOT_DISPROVED", got
    nine_five = [c for c in reason_audit.typed_candidates(o, row, srcs, spec) if "9 (0.3%) vs 5 (0.1%)" in c["span"]]
    assert nine_five and all(c["unit"] == "EVENTS" and "unit:EVENTS" in c["mismatch"] for c in nine_five)


def test_source_evidence_of_the_unit_is_what_would_disprove_it(served):
    """The same numbers under a table header that says 'n (%)' patients: the unit is established, so the refusal is disproved."""
    o, row, spec, _ = served
    got = reason_audit.audit_reason_row(o, row, [{"source_id": "fixture:table", "text": "", "raw": UNIT_TABLE}], spec)
    assert got["verdict"] == "REASON_FALSE_VALUE_HELD", got
    assert got["evidence_identity"]["unit"] == "PATIENTS_WITH_EVENT"


@pytest.mark.parametrize("text, unit", [
    ("and there were 9 (0.3%) vs 5 (0.1%) events of adjudication-confirmed acute pancreatitis.", "EVENTS"),
    ("Adverse events occurred in 2697 (77.2%) and 2723 (78.1%) patients in the linagliptin and placebo groups", "PATIENTS_WITH_EVENT"),
    ("12 of 300 participants vs 20 of 298 participants", "PATIENTS_WITH_EVENT"),
    ("1.2 vs 1.9 per 100 patient-years", "PATIENT_YEARS"),
    ("there were 33 episodes of hypoglycaemia", "EVENTS"),
    ("acute pancreatitis 9 vs 5", None),
])
def test_unit_is_read_from_the_words_next_to_the_numbers(text, unit):
    assert ei.unit_of(text) == unit


def test_serious_and_nonserious_category_totals_are_never_summed_into_any_ae():
    s = ("Serious adverse events occurred in 120 (12.0%) and 110 (11.0%) patients in the linagliptin and placebo groups, and "
         "non-serious adverse events in 300 (30.0%) and 290 (29.1%) patients, respectively.")
    outcome = {"name": "Any adverse events", "estimand": "RR", "timepoint": None, "population": None}
    cands = reason_audit.typed_candidates(outcome, {"id": "t", "reason": "no deduplicated all-AE count"},
                                          [{"source_id": "fixture:s", "text": s}], {"keywords": ["adverse events"]})
    assert cands and all(c["mismatch"] for c in cands)                  # neither category is 'any AE'
    assert {c.get("definition") for c in cands} == {"RESTRICTED"}
    events = {a["events"] for c in cands for a in (c.get("arms") or [])}
    assert events <= {120, 110, 300, 290} and not events & {420, 400}  # never 120+300 / 110+290
