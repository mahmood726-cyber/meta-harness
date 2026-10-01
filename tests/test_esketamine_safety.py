"""Safety fixtures from the esketamine review (served review_sha256 f5b8f4cb..., pinned at 6260e70c).
  * TRANSFORM-1 Table 5 patient-level rows (nausea 68/231 vs 12/113, dissociation 62/231 vs 4/113, dizziness 58/231 vs 10/113): the
    safety denominator (231/113) is distinct from the efficacy denominator (209/108) and is never reused across; symptom rows are never
    summed into any-AE (one patient can appear in several rows).
  * Chen (PMID 37025256, held): >=1 TEAE 120/126 vs 89/126, patients not episodes; RR 1.3483 (1.1969-1.5189).
  * Harms are not in this protocol -> the harm outcome is EXPLORATORY."""
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, pipeline, reason_audit  # noqa: E402

SERVED, SLUG, CHEN = "6260e70c", "esketamine-trd-madrs", "37025256"
# TEST FIXTURE -- not a held source: TRANSFORM-1's publication is not in this corpus's cache (the review refuses its AE row
# SOURCE_NOT_RETRIEVED). The table carries the review's cited Table 5 rows under the safety set's arm N.
TRANSFORM1_TABLE5 = (
    "<table-wrap><label>Table 5</label><caption>Treatment-emergent adverse events in at least 5% of patients (safety analysis set)"
    "</caption><table><thead><tr><th>Preferred term, n (%)</th><th>Esketamine + AD (N = 231)</th><th>AD + placebo (N = 113)</th>"
    "</tr></thead><tbody>"
    "<tr><td>Nausea</td><td>68 (29.4)</td><td>12 (10.6)</td></tr>"
    "<tr><td>Dissociation</td><td>62 (26.8)</td><td>4 (3.5)</td></tr>"
    "<tr><td>Dizziness</td><td>58 (25.1)</td><td>10 (8.8)</td></tr>"
    "</tbody></table></table-wrap>")
TRANSFORM1_EFFICACY_NS, TRANSFORM1_SAFETY_NS = (209, 108), (231, 113)


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, check=True).stdout


def served():
    return json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/review.json"))


def _chen_rows():
    raw = open(os.path.join(ROOT, "cache", SLUG, f"ft_{CHEN}.txt"), encoding="utf-8").read()
    return ei.count_rows(raw, CHEN, f"fulltext:{CHEN}")


def test_served_review_is_the_one_the_fixture_names():
    cert = json.loads(_git("show", f"{SERVED}:docs/reviews/{SLUG}/CERTIFICATE.json"))
    assert cert["review_sha256"].startswith("f5b8f4cb")


# ---- Chen: >=1 TEAE, patients not episodes -------------------------------------------------------------------------------------
def test_PLANT_chen_teae_row_is_read_from_the_held_table():
    """Pre-fix the table's header had no cell over the label column, the arms shifted, and this row was never read."""
    rows = [r for r in _chen_rows() if r["label"] == "TEAEs"]
    assert len(rows) == 1
    assert [(a["events"], a["n_group"]) for a in rows[0]["arms"]] == [(120, 126), (89, 126)]


def test_chen_teae_counts_patients_not_episodes():
    row = next(r for r in _chen_rows() if r["label"] == "TEAEs")
    assert row["unit"] == "PATIENTS_WITH_EVENT"                  # 95.2 = 100*120/126 and 70.6 = 100*89/126: shares of the arm's patients
    assert ei.names_the_outcome(row["label"], "Adverse events")


def test_chen_rr_reproduces_the_served_result():
    (a, n1), (c, n2) = (120, 126), (89, 126)
    rr = (a / n1) / (c / n2)
    se = math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n2)
    got = [round(x, 4) for x in (rr, rr * math.exp(-1.959963984540054 * se), rr * math.exp(1.959963984540054 * se))]
    assert got == [1.3483, 1.1969, 1.5189]
    res = next(o for o in served()["outcomes"] if o["name"] == "Adverse events")["result"]
    assert [res["estimate"], res["ci_low"], res["ci_high"]] == got


# ---- TRANSFORM-1: safety denominators, never reused; symptom rows never summed -----------------------------------------------
def test_transform1_table5_rows_carry_the_safety_set_denominators():
    rows = ei.count_rows(TRANSFORM1_TABLE5, "NCT02417064", "fixture:table5")
    got = {r["label"]: [(a["events"], a["n_group"]) for a in r["arms"]] for r in rows}
    assert got == {"Nausea": [(68, 231), (12, 113)], "Dissociation": [(62, 231), (4, 113)], "Dizziness": [(58, 231), (10, 113)]}
    assert {r["unit"] for r in rows} == {"PATIENTS_WITH_EVENT"}


def test_the_efficacy_denominator_is_never_reused_for_harms():
    from harness import safety_rules
    assert safety_rules.denominator_problem(TRANSFORM1_EFFICACY_NS, TRANSFORM1_EFFICACY_NS, TRANSFORM1_SAFETY_NS) == \
        "DENOMINATOR_REUSED_ACROSS_ANALYSIS_SETS"
    assert safety_rules.denominator_problem(TRANSFORM1_SAFETY_NS, TRANSFORM1_EFFICACY_NS, TRANSFORM1_SAFETY_NS) is None
    assert safety_rules.denominator_problem((230, 113), TRANSFORM1_EFFICACY_NS, TRANSFORM1_SAFETY_NS) == "DENOMINATOR_NOT_FROM_SAFETY_SET"


def test_symptom_rows_are_never_summed_into_any_ae():
    rv = served()
    o = next(x for x in rv["outcomes"] if x["name"] == "Adverse events")
    cands = reason_audit.typed_candidates(o, {"id": "NCT02417064"}, [{"source_id": "fixture:table5", "text": "", "raw": TRANSFORM1_TABLE5}],
                                          {"keywords": ["adverse event", "adverse events"]})
    assert all(c["mismatch"] for c in cands)                        # no symptom row stands for the any-AE total
    bound = ei.bind_labelled_count_row(TRANSFORM1_TABLE5, "NCT02417064", "fixture:table5", ["adverse event"],
                                       lambda label, terms: any(t in label.lower() for t in terms), "Adverse events")
    assert bound["state"] == "NOT_FOUND"
    events = {a["events"] for c in cands for a in (c.get("arms") or [])}
    assert not events & {68 + 62 + 58, 12 + 4 + 10}                 # 188 / 26: never a sum


# ---- protocol status ------------------------------------------------------------------------------------------------------------
def test_PLANT_harms_are_not_in_this_protocol_so_the_harm_outcome_is_exploratory():
    from harness import safety_rules
    rv = served()
    o = next(x for x in rv["outcomes"] if x["name"] == "Adverse events")
    assert "protocol_status" not in o                              # as served: unlabelled
    md = open(os.path.join(ROOT, "protocols", f"{SLUG}.md"), encoding="utf-8").read()
    assert safety_rules.protocol_status(o, md)["status"] == "EXPLORATORY"
    primary = next(x for x in rv["outcomes"] if x.get("primary"))
    assert safety_rules.protocol_status(primary, md)["status"] == "PRESPECIFIED_PRIMARY"


def test_a_harm_named_in_the_protocols_outcome_sections_is_prespecified_and_a_mention_elsewhere_is_not():
    from harness import safety_rules
    md = ("# P\n## PICO\n- **O (harms)** - hearing impairment and gastrointestinal adverse effects.\n"
          "## Eligibility\n- exclude open-label safety studies reporting adverse events\n")
    assert safety_rules.protocol_status({"name": "Gastrointestinal adverse effects", "kind": "harm"}, md)["status"] == "PRESPECIFIED"
    md2 = "# P\n## PICO\n- **O:** mortality\n## Eligibility\n- exclude studies reporting only adverse events\n"
    assert safety_rules.protocol_status({"name": "Adverse events", "kind": "harm"}, md2)["status"] == "EXPLORATORY"
