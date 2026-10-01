"""STEP 1 (PMID 33567185), semaglutide-weight review (served review_sha256 e209c1d519..., pinned at 6260e70c).
  * Auditor: for the aggregate-GI refusal the pre-fix auditor cited GI DISCONTINUATION (59 vs 5) and called the refusal false. A
    stopping-treatment result can never establish the total number of patients with the adverse event -> REASON_NOT_DISPROVED.
  * The real aggregate (969/1,306 vs 314/655, patients) resolves the extraction instead. STEP 1's own report is NOT held; the held
    corpus carries it only second-hand (42225300, an indirect comparison; 41778920, a forest table 'Wilding 2021'), so the plant uses a
    primary-style TEST FIXTURE.
  * Patients vs events vs event-rate COLUMNS of one table are different units (E and R values here are SYNTHETIC, not STEP 1's)."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, pipeline, reason_audit  # noqa: E402

SERVED, PREFIX, SLUG, STEP1 = "6260e70c", "23642e0d", "semaglutide-obesity-weight", "33567185"
# TEST FIXTURE -- not a held source. n (%) values are the review's cited STEP 1 aggregate; E and R columns are SYNTHETIC.
TABLE = ("<table-wrap><label>Table S1</label><caption>Adverse events, on-treatment period (safety analysis set)</caption><table>"
         "<thead><tr><th rowspan=\"2\">System organ class</th><th colspan=\"3\">Semaglutide (N = 1306)</th>"
         "<th colspan=\"3\">Placebo (N = 655)</th></tr>"
         "<tr><th>n (%)</th><th>E</th><th>R</th><th>n (%)</th><th>E</th><th>R</th></tr></thead><tbody>"
         "<tr><td>Gastrointestinal disorders</td><td>969 (74.2)</td><td>4000</td><td>150.0</td>"
         "<td>314 (47.9)</td><td>800</td><td>60.0</td></tr></tbody></table></table-wrap>")


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


@pytest.fixture(scope="module")
def served():
    rv = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    o = next(x for x in rv["outcomes"] if x["name"] == "Gastrointestinal adverse events")
    row = next(a for a in o["declared_absent_trials"] if STEP1 in str(a.get("id")))
    return o, row, specs.get(o["name"]) or {}, reason_audit.sources_by_trial(SLUG, recs, ROOT)[STEP1]


@pytest.fixture(scope="module")
def prefix_auditor():
    src = _git("show", f"{PREFIX}:harness/reason_audit.py").decode("utf-8")
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix_step1", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{PREFIX}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


def test_served_row_and_its_audit(served):
    o, row, _, _ = served
    cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/CERTIFICATE.json"))
    assert cert["review_sha256"].startswith("e209c1d519")
    assert "discontinuations due to gastrointestinal events rather than all patients" in row["reason"]
    assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD" and "59 [4.5%]" in row["reason_code_audit"]["source_span"]


def test_PLANT_prefix_auditor_called_the_refusal_false_on_discontinuation(served, prefix_auditor):
    o, row, spec, srcs = served
    assert prefix_auditor.audit_reason_row(o, row, srcs, spec)["verdict"] == "REASON_FALSE_VALUE_HELD"


def test_a_stopping_treatment_result_never_establishes_the_aggregate(served):
    o, row, spec, srcs = served
    got = reason_audit.audit_reason_row(o, row, srcs, spec)
    assert got["verdict"] == "REASON_NOT_DISPROVED"
    disc = [c for c in reason_audit.typed_candidates(o, row, srcs, spec) if "discontinued" in c["span"]]
    assert disc and all(c["attribution"] == "LEADING_TO_DISCONTINUATION" and
                        "attribution:LEADING_TO_DISCONTINUATION!=INVESTIGATOR_REPORTED_ANY" in c["mismatch"] for c in disc)


def test_the_real_aggregate_resolves_the_extraction(served):
    o, row, spec, _ = served
    got = reason_audit.audit_reason_row(o, row, [{"source_id": "fixture:step1-table", "text": "", "raw": TABLE}], spec)
    assert got["verdict"] == "REASON_FALSE_VALUE_HELD"
    assert [a["events"] for a in got["evidence_identity"]["arms"]] == [969, 314]
    assert got["evidence_identity"]["unit"] == "PATIENTS_WITH_EVENT"


def test_PLANT_patients_events_and_rate_columns_are_different_units():
    rows = ei.count_rows(TABLE, STEP1, "fixture")
    by_unit = {r["unit"]: r for r in rows}
    assert set(by_unit) == {"PATIENTS_WITH_EVENT", "EVENTS", "PATIENT_YEARS"}
    assert [(a["events"], a["n_group"]) for a in by_unit["PATIENTS_WITH_EVENT"]["arms"]] == [(969, 1306), (314, 655)]
    assert [a["events"] for a in by_unit["EVENTS"]["arms"]] == [4000, 800]              # never paired with a patient count
    assert [a["rate"] for a in by_unit["PATIENT_YEARS"]["arms"]] == [150.0, 60.0]


def test_only_the_patients_column_can_satisfy_a_patient_level_target(served):
    o, row, spec, _ = served
    cands = reason_audit.typed_candidates(o, row, [{"source_id": "fixture:step1-table", "text": "", "raw": TABLE}], spec)
    fits = {c["unit"] for c in cands if not c["mismatch"]}
    assert fits == {"PATIENTS_WITH_EVENT"}
    assert any("unit:EVENTS" in c["mismatch"] for c in cands) and any(c["effect_measure"] == "RATE" and c["mismatch"] for c in cands)
