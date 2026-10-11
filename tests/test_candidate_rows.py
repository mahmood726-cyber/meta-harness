"""Plants (D3, 11 Oct; r26-01 ESCAPe): a refusal on WINDOW grounds is complete only when every candidate row of the
outcome in the held full text has been assessed. Nothing is admitted by this check."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import candidate_rows as cr  # noqa: E402

SLUG, PID = "corticosteroids-cap-mortality", "35723686"


def _escape_row():
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    return next(t for o in r["outcomes"] if o["name"] == "All-cause mortality"
                for t in o["declared_absent_trials"] if PID in str(t["id"]))


def test_PLANT_escape_hospital_mortality_is_an_unassessed_candidate():
    po = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))["primary_outcome"]
    a = cr.audit_refusal(SLUG, PID, _escape_row(), po["keywords"], po["name"], po["timepoint"])
    assert a["state"] == "CANDIDATE_ROW_UNASSESSED"
    [u] = a["unassessed"]
    assert u["assessment"] == "IN_HOSPITAL_MATCH" and u["cells"][:2] == ["34/291 (12)", "28/281 (10)"]
    by = {c["label"][:20]: c["assessment"] for c in a["candidates"]}
    assert by["Died on or prior to "] == "WINDOW_MISMATCH" and by["Died by 1 year—no./t"] == "WINDOW_MISMATCH"


def test_a_stub_has_no_tables_to_assess():
    a = cr.audit_refusal("metformin-pcos-ovulation", "16769748", {}, ["ovulation"], "Ovulation", "")
    assert a["state"] == "NOT_A_FULLTEXT" and a["coverage"] == "STUB"


def test_row_windows_come_from_the_row_label():
    assert cr.row_window("Died on or prior to study day 60") == ("DAYS", 60)
    assert cr.row_window("Died by 1 year") == ("DAYS", 365)
    assert cr.row_window("Hospital Mortality") == ("IN_HOSPITAL", None)
    assert cr.row_window("28-day mortality") == ("DAYS", 28)
    assert cr.row_window("Mortality") == ("UNSTATED", None)


def test_only_outside_window_candidates_complete_the_refusal():
    x = ('<article><body><table-wrap id="t2"><caption><p>Outcomes</p></caption><table>'
         '<tr><td>Died by day 60</td><td>10/100</td><td>12/100</td></tr>'
         '<tr><td>Died by day 90</td><td>15/100</td><td>16/100</td></tr></table></table-wrap></body></article>')
    c = cr.candidates(x, ["mortality"], "All-cause mortality", "30-day")
    assert [k["assessment"] for k in c] == ["WINDOW_MISMATCH", "WINDOW_MISMATCH"]


def test_a_baseline_table_is_never_a_candidate_source():
    x = ('<article><body><table-wrap id="t1"><caption><p>Baseline characteristics</p></caption><table>'
         '<tr><td>Prior 30-day mortality risk</td><td>10/100</td><td>12/100</td></tr></table></table-wrap></body></article>')
    assert cr.candidates(x, ["mortality"], "All-cause mortality", "30-day") == []
