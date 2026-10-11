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


# ---- PR2 review round 1 (codex e1p2-r1 mc-3d452b1d, agy e1p2-r1-agy mc-936c03ad): plants that failed first ----
def test_plain_integer_arm_counts_are_candidates():
    from harness.candidate_rows import candidates
    jats = ('<table-wrap><table><tr><th>Outcome</th><th>Treatment (n=100)</th><th>Control (n=100)</th></tr>'
            '<tr><td>30-day mortality, n</td><td>10</td><td>12</td></tr></table></table-wrap>')
    c = candidates(jats, [], "Mortality", "30-day")
    assert len(c) == 1 and c[0]["cells"] == ["10", "12"] and c[0]["assessment"] == "WINDOW_MATCH"


def test_declared_year_and_month_windows_are_read():
    from harness.candidate_rows import candidates
    for label, declared in (("1-year mortality", "1 year"), ("Mortality at 1 year", "12 months"),
                            ("6-month mortality", "6 months")):
        jats = f'<table-wrap><table><tr><td>{label}</td><td>10/100</td><td>12/100</td></tr></table></table-wrap>'
        assert candidates(jats, [], "Mortality", declared)[0]["assessment"] == "WINDOW_MATCH", (label, declared)


def test_out_of_hospital_is_not_in_hospital():
    from harness.candidate_rows import candidates
    for label in ("Out-of-hospital mortality", "Out of hospital death", "Pre-hospital mortality"):
        jats = f'<table-wrap><table><tr><td>{label}</td><td>10/100</td><td>12/100</td></tr></table></table-wrap>'
        r = candidates(jats, [], "Mortality", "in-hospital")[0]
        assert r["window"]["kind"] != "IN_HOSPITAL" and r["assessment"] != "IN_HOSPITAL_MATCH", label


def test_one_shared_cell_does_not_make_a_row_the_witness(tmp_path):
    from unittest.mock import patch
    from harness import candidate_rows as cr
    jats = ('<table-wrap><table><tr><td>60-day mortality</td><td>40/291</td><td>28/281</td></tr>'
            '<tr><td>Hospital mortality</td><td>34/291</td><td>28/281</td></tr></table></table-wrap>')
    d = tmp_path / "cache" / "s"
    d.mkdir(parents=True)
    (d / "ft_1.xml").write_text(jats, encoding="utf-8")
    with patch.object(cr.sc, "coverage_for", return_value={"fulltext": "FULLTEXT"}):
        out = cr.audit_refusal("s", "1", {"source_span": "60-day mortality 40/291 v 28/281"}, [], "Mortality",
                               "30-day or in-hospital", root=str(tmp_path))
    assert [c["is_refusal_witness"] for c in out["candidates"]] == [True, False]
    assert out["state"] == "CANDIDATE_ROW_UNASSESSED"
    assert [c["label"] for c in out["unassessed"]] == ["Hospital mortality"]


def test_section_heading_names_the_outcome():
    from harness.candidate_rows import candidates
    jats = ('<table-wrap><caption>Outcomes</caption><table><tr><td>Mortality</td></tr>'
            '<tr><td>28 days</td><td>10/100</td><td>20/100</td></tr></table></table-wrap>')
    c = candidates(jats, [], "mortality", "28 days")
    assert len(c) == 1 and c[0]["section"] == "Mortality" and c[0]["assessment"] == "WINDOW_MATCH"
