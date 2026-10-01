"""ATTRIBUTION (+ window, safety population) is part of a safety outcome's identity -- finerenone review (served review_sha256
00a2b7e4..., pinned at 6260e70c). FIDELIO/FIGARO full texts are NOT held in this corpus (only abstracts), so Table 2 rows are TEST
FIXTURES carrying the review's cited values under the safety set's arm N.
  FIDELIO: investigator-reported hyperkalaemia 516/2,827 vs 255/2,831; 'related to the trial regimen' 333 vs 135 (a DIFFERENT
           outcome); leading to discontinuation 64/2,827 vs 25/2,831.
  FIGARO:  investigator-reported 396/3,683 vs 193/3,658; leading to discontinuation 46/3,683 vs 13/3,658.
Plants: 'related' never binds to a regardless-of-attribution target and vice versa; safety denominators are never borrowed from
efficacy. Note: FIVE-STAR's 'no hyperkalaemia leading to hospitalisation or death' must never become 'no hyperkalaemia'."""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, reason_audit  # noqa: E402

SERVED, SLUG, FIDELIO, FIGARO = "6260e70c", "finerenone-ckd-t2d-renal", "33264825", "34449181"


def _table(label, n1, n2, rows):
    body = "".join(f"<tr><td>{lab}</td><td>{a}</td><td>{b}</td></tr>" for lab, a, b in rows)
    return (f"<table-wrap><label>{label}</label><caption>Adverse events during the treatment period (safety population)</caption>"
            f"<table><thead><tr><th>Event, n (%)</th><th>Finerenone (N = {n1})</th><th>Placebo (N = {n2})</th></tr></thead>"
            f"<tbody>{body}</tbody></table></table-wrap>")


# TEST FIXTURES (not held sources): the review's cited Table 2 values
FIDELIO_T2 = _table("Table 2", 2827, 2831, [("Hyperkalemia", "516 (18.3)", "255 (9.0)"),
                                           ("Hyperkalemia related to trial regimen", "333 (11.8)", "135 (4.8)"),
                                           ("Hyperkalemia leading to permanent discontinuation of trial regimen", "64 (2.3)", "25 (0.9)")])
FIGARO_T2 = _table("Table 2", 3683, 3658, [("Hyperkalemia", "396 (10.8)", "193 (5.3)"),
                                          ("Hyperkalemia leading to permanent discontinuation of trial regimen", "46 (1.2)", "13 (0.4)")])


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


def served():
    return json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))


def _rows(raw, trial):
    return {r["label"]: r for r in ei.count_rows(raw, trial, f"fixture:{trial}")}


def test_served_review_and_its_defect():
    cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/CERTIFICATE.json"))
    assert cert["review_sha256"].startswith("00a2b7e4")
    rv = served()
    hk = next(o for o in rv["outcomes"] if o["name"] == "Hyperkalemia")
    row = next(a for a in hk["declared_absent_trials"] if FIDELIO in a["id"])
    assert "hyperkalemia-related discontinuation rather than all hyperkalemia" in row["reason"]   # the refusal IS about attribution


def test_PLANT_attribution_is_read_from_the_label():
    assert ei.attribution_of("Hyperkalemia") == "INVESTIGATOR_REPORTED_ANY"
    assert ei.attribution_of("Hyperkalemia related to trial regimen") == "TREATMENT_RELATED"
    assert ei.attribution_of("Hyperkalemia leading to permanent discontinuation of trial regimen") == "LEADING_TO_DISCONTINUATION"
    assert ei.attribution_of("hyperkalemia-related discontinuation of the trial regimen") == "LEADING_TO_DISCONTINUATION"
    assert ei.attribution_of("Serious hyperkalemia") == "SERIOUS"
    assert ei.attribution_of("Hyperkalemia-related treatment discontinuation") == "LEADING_TO_DISCONTINUATION"


def test_related_never_binds_to_a_regardless_of_attribution_target_and_vice_versa():
    rv = served()
    hk = next(o for o in rv["outcomes"] if o["name"] == "Hyperkalemia")
    row = next(a for a in hk["declared_absent_trials"] if FIDELIO in a["id"])
    cands = {c["label"]: c for c in reason_audit.typed_candidates(hk, row, [{"source_id": "fixture:fidelio", "text": "", "raw": FIDELIO_T2}], {})}
    assert cands["Hyperkalemia"]["attribution"] == "INVESTIGATOR_REPORTED_ANY"
    assert not [m for m in cands["Hyperkalemia"]["mismatch"] if m.startswith("attribution")]
    assert "attribution:TREATMENT_RELATED!=INVESTIGATOR_REPORTED_ANY" in cands["Hyperkalemia related to trial regimen"]["mismatch"]
    # and the reverse: a treatment-related target is never satisfied by the regardless-of-attribution row
    related_target = {**hk, "name": "Treatment-related hyperkalemia"}
    c2 = {c["label"]: c for c in reason_audit.typed_candidates(related_target, row, [{"source_id": "fixture:fidelio", "text": "", "raw": FIDELIO_T2}], {})}
    assert "attribution:INVESTIGATOR_REPORTED_ANY!=TREATMENT_RELATED" in c2["Hyperkalemia"]["mismatch"]


def test_the_investigator_reported_rows_carry_the_cited_values_on_the_safety_set():
    fid, fig = _rows(FIDELIO_T2, FIDELIO), _rows(FIGARO_T2, FIGARO)
    assert [(a["events"], a["n_group"]) for a in fid["Hyperkalemia"]["arms"]] == [(516, 2827), (255, 2831)]
    assert [(a["events"], a["n_group"]) for a in fig["Hyperkalemia"]["arms"]] == [(396, 3683), (193, 3658)]
    assert [a["events"] for a in fid["Hyperkalemia related to trial regimen"]["arms"]] == [333, 135]
    assert {r["unit"] for r in fid.values()} | {r["unit"] for r in fig.values()} == {"PATIENTS_WITH_EVENT"}
    assert fid["Hyperkalemia"]["window"] == "TREATMENT_EMERGENT"


def test_discontinuation_binds_only_to_the_discontinuation_outcome():
    rv = served()
    dc = next(o for o in rv["outcomes"] if o["name"] == "Hyperkalemia-related treatment discontinuation")
    for trial, raw, want in ((FIDELIO, FIDELIO_T2, [64, 25]), (FIGARO, FIGARO_T2, [46, 13])):
        row = next(a for a in dc["declared_absent_trials"] if trial in a["id"])
        cands = reason_audit.typed_candidates(dc, row, [{"source_id": f"fixture:{trial}", "text": "", "raw": raw}], {})
        fits = [c for c in cands if not [m for m in c["mismatch"] if m.split(":")[0] in ("attribution", "definition", "outcome")]]
        assert [[a["events"] for a in c["arms"]] for c in fits] == [want]


def test_safety_denominators_are_never_borrowed_from_efficacy():
    from harness import safety_rules
    rv = served()
    eff = next(o for o in rv["outcomes"] if o["name"] == "Kidney composite outcome")
    src = next(t for t in eff["trials"] if FIDELIO in t["id"])["source"]
    n1, n2 = (int(x) for x in re.findall(r"of (\d{4}) patients", src)[:2])      # efficacy N from the HELD abstract as served
    assert (n1, n2) == (2833, 2841)
    safety = (2827, 2831)
    assert safety_rules.denominator_problem((n1, n2), (n1, n2), safety) == "DENOMINATOR_REUSED_ACROSS_ANALYSIS_SETS"
    assert safety_rules.denominator_problem(safety, (n1, n2), safety) is None


def test_note_five_star_qualified_negative_never_becomes_an_unqualified_absence():
    s = "There were no cases of hyperkalemia leading to hospitalization or death."
    assert ei.definition_of(s, "Hyperkalemia") == "RESTRICTED"
    assert ei.definition_of(s, "Hyperkalemia leading to hospitalization or death") == "AS_NAMED"
