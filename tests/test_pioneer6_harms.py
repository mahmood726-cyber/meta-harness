"""Harms fixture from the GLP-1 review (served review_sha256 7d15dfd97f..., pinned at 6260e70c): PIONEER 6 (PMID 31185157) Table 3,
patients, treatment-period safety window. PIONEER 6's full text is NOT held here (abstract only), so Table 3 is a TEST FIXTURE with
the review's cited values: AE leading to permanent discontinuation 184/1,591 vs 104/1,592; GI AE leading to permanent discontinuation
108/1,591 vs 26/1,592. Plants: the 108 vs 26 row binds ONLY to 'GI adverse event leading to discontinuation', never to 'any GI adverse
event' (nor to all-cause AE discontinuation); the safety window is preserved, not replaced with efficacy follow-up."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, held_rows, reason_audit  # noqa: E402

SERVED, SLUG, PIONEER6 = "6260e70c", "glp1-ra-mace-t2d", "31185157"
# TEST FIXTURE -- not a held source
TABLE3 = ("<table-wrap><label>Table 3</label><caption>Adverse events during the on-treatment period (safety analysis set)</caption>"
          "<table><thead><tr><th>Patients, n (%)</th><th>Oral semaglutide (N = 1591)</th><th>Placebo (N = 1592)</th></tr></thead><tbody>"
          "<tr><td>Adverse events leading to permanent discontinuation of trial product</td><td>184 (11.6)</td><td>104 (6.5)</td></tr>"
          "<tr><td>Gastrointestinal adverse events leading to permanent discontinuation of trial product</td><td>108 (6.8)</td><td>26 (1.6)</td></tr>"
          "</tbody></table></table-wrap>")
SRC = [{"source_id": "fixture:pioneer6-table3", "text": "", "raw": TABLE3}]
GI_DISC_ROW = "Gastrointestinal adverse events leading to permanent discontinuation of trial product"
AE_DISC_ROW = "Adverse events leading to permanent discontinuation of trial product"


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


def served():
    return json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))


def _outcome(name):
    return next(o for o in served()["outcomes"] if o["name"] == name)


def _cands(outcome):
    row = next((a for a in outcome.get("declared_absent_trials") or [] if PIONEER6 in str(a.get("id"))), {"id": PIONEER6})
    return {c["label"]: c for c in reason_audit.typed_candidates(outcome, row, SRC, {})}


def _binds(c):
    return not [m for m in c["mismatch"] if m.split(":")[0] in ("outcome", "definition", "attribution", "part", "window")]


def test_served_review_is_the_one_the_fixture_names():
    cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/CERTIFICATE.json"))
    assert cert["review_sha256"].startswith("7d15dfd97f")
    gi = _outcome("Gastrointestinal adverse events")
    assert next(a for a in gi["declared_absent_trials"] if PIONEER6 in a["id"])["reason_code"] == "REFUSED_ON_EVIDENCE"


def test_table3_rows_count_patients_on_the_safety_set():
    rows = {r["label"]: r for r in ei.count_rows(TABLE3, PIONEER6, "fixture")}
    assert [(a["events"], a["n_group"]) for a in rows[AE_DISC_ROW]["arms"]] == [(184, 1591), (104, 1592)]
    assert [(a["events"], a["n_group"]) for a in rows[GI_DISC_ROW]["arms"]] == [(108, 1591), (26, 1592)]
    assert {r["unit"] for r in rows.values()} == {"PATIENTS_WITH_EVENT"}


def test_PLANT_gi_discontinuation_never_binds_to_any_gi_adverse_event():
    c = _cands(_outcome("Gastrointestinal adverse events"))
    assert not _binds(c[GI_DISC_ROW])
    assert "attribution:LEADING_TO_DISCONTINUATION!=INVESTIGATOR_REPORTED_ANY" in c[GI_DISC_ROW]["mismatch"]


def test_PLANT_gi_discontinuation_never_binds_to_all_cause_ae_discontinuation():
    c = _cands(_outcome("Adverse events leading to discontinuation"))
    assert _binds(c[AE_DISC_ROW])                                    # 184 vs 104 IS that outcome
    assert not _binds(c[GI_DISC_ROW]) and c[GI_DISC_ROW]["definition"] == "RESTRICTED"


def test_gi_discontinuation_binds_to_its_own_outcome():
    target = {"name": "Gastrointestinal adverse events leading to discontinuation", "kind": "harm", "estimand": "RR"}
    c = _cands(target)
    assert _binds(c[GI_DISC_ROW]) and [a["events"] for a in c[GI_DISC_ROW]["arms"]] == [108, 26]
    assert not _binds(c[AE_DISC_ROW])                                # and the all-cause row is not it


def test_PLANT_the_safety_window_is_preserved_not_replaced_with_efficacy_follow_up():
    row = next(r for r in ei.count_rows(TABLE3, PIONEER6, "fixture") if r["label"] == GI_DISC_ROW)
    assert row["window"] == "TREATMENT_EMERGENT"                     # from the table: the on-treatment period
    assert held_rows.ascertained_counts(row)["window"] == "TREATMENT_EMERGENT"   # the counts carry it
    assert ei.window_of("during a median follow-up of 15.9 months") is None      # efficacy follow-up is not a safety window
