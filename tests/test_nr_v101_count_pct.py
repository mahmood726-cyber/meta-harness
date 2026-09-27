"""Percentage corroboration must fail in BOTH directions (lane NR, V1.0.1).

False refusal (fixed earlier): COCS '21 (18.6%)' of 113 -- genuine, 21/113 = 18.58% -> 18.6%, must be corroborated.
False acceptance (colchicine-secondary-cv-prevention review, 3eb69ba7): Akrami's control arm '3 (2.5%)' with denominator
129 was served as 'percentage-corroborated', but 3/129 = 2.326% -> 2.3%, not 2.5%. The old check accepted any percentage
within 1.0-1.5 points. Requirement: the stated percentage must be what count/denominator ROUNDS (or truncates) to at the
STATED precision; when count, denominator and percentage disagree the conflict is preserved (COUNT_PCT_CONFLICT), never a
success and never silently dropped.
"""
from __future__ import annotations

import pytest

from harness import absence, extract

AKRAMI = ("Evaluating adverse effects, gastrointestinal symptom was the most with the rate of 15 (12.5%) in the "
          "colchicine group and 3 (2.5%) in the controls.")
AKRAMI_SIZES = ("RESULTS: A total of 249 patients were recruited between October 2019-March 2020; 120 assigned to the "
                "colchicine group and 129 assigned to the placebo group. ")          # Akrami 34876021, as held
GI = ["gastrointestinal", "diarrh", "adverse effect", "adverse event", "side effect"]
INTERV, COMP = ["colchicine"], ["placebo", "control"]          # the topic's own terms


@pytest.mark.parametrize("ev,n,pct,ok", [
    (21, 113, "18.6", True),       # 18.584 -> 18.6
    (39, 127, "30.7", True),       # 30.709 -> 30.7
    (3, 129, "2.5", False),        # 2.326 -> 2.3 (the served false acceptance)
    (3, 129, "2.3", True),
    (3, 129, "2", True),           # integer precision: 2.33 -> 2
    (25, 400, "6.2", True),        # 6.25 -> 6.2 (half-even / truncation) and 6.3 (half-up) are both readings
    (25, 400, "6.3", True),
    (15, 120, "12.5", True),
    (1, 3, "33.3", True),
    (1, 3, "33.4", False),
    # found by the corpus radius: DOUBLE ROUNDING is a reporting artefact, not a disagreement
    (13, 81, "16.1", True),        # 16.049 -> 16.05 -> 16.1 (32720823, served in colchicine-postop-af)
    (711, 1005, "70.8", True),     # 70.746 -> 70.75 -> 70.8 (40961952)
    (62, 180, "34.8", False),      # 34.444 -> 34.44 -> 34.4: a real near-miss (38184150)
])
def test_the_stated_percentage_is_the_rounding_of_count_over_denominator(ev, n, pct, ok):
    assert extract.pct_consistent(ev, n, pct) is ok


def test_akrami_is_a_count_pct_conflict_not_a_success():
    ex = extract.extract_trial(AKRAMI_SIZES + AKRAMI, GI, INTERV, COMP, declared_composite=False, estimand="RR")
    assert ex.get("absent"), ex
    assert ex["reason"].startswith(extract.COUNT_PCT_CONFLICT), ex
    assert "3/129" in ex["reason"] and "2.5%" in ex["reason"]          # the conflict names its numbers


def test_an_explicit_fraction_that_disagrees_is_a_conflict():
    s = "Diarrhoea occurred in 15/120 (12.5%) with colchicine and 3/129 (2.5%) with placebo."
    ex = extract.extract_trial(s, GI + ["diarrhoea"], INTERV, COMP, declared_composite=False, estimand="RR")
    assert ex.get("absent") and ex["reason"].startswith(extract.COUNT_PCT_CONFLICT), ex


def test_cocs_still_corroborates():
    cocs = ("The final analysis included 240 study subjects: 113 in the colchicine group and 127 in the placebo group. "
            "POAF was observed in 21 (18.6%) patients of the colchicine group vs. 39 (30.7%) control patients.")
    ex = extract.extract_trial(cocs, ["poaf", "atrial fibrillation"], INTERV, COMP, declared_composite=False, estimand="RR")
    assert (ex.get("ai"), ex.get("n1i"), ex.get("ci"), ex.get("n2i")) == (21, 113, 39, 127), ex


def test_the_conflict_is_classified_under_its_own_code():
    row = {"reason": extract.COUNT_PCT_CONFLICT + ": 3/129 = 2.33% but the source states 2.5%", "absent_kind": "machine_absent"}
    out = absence.classify_reason(GI, AKRAMI_SIZES + AKRAMI, None, "Gastrointestinal adverse effects", "RR",
                                  reason=row["reason"], absent_kind=row["absent_kind"], row=row)
    assert out["reason_code"] == absence.COUNT_PCT_CONFLICT, out


def test_an_endpoint_component_excluded_refusal_keeps_its_code_in_the_audit_layer():
    row = {"endpoint_admissibility": "ENDPOINT_COMPONENT_EXCLUDED", "reason_code": "ENDPOINT_COMPONENT_EXCLUDED",
           "state": "REFUSED_ON_EVIDENCE", "source": "3-point MACE (nonfatal stroke excluded) (HR 0.87 ...)"}
    out = absence.classify_reason(["mace"], "abstract", None, "3-point MACE", "HR", reason="excluded", row=row)
    assert out["reason_code"] == "ENDPOINT_COMPONENT_EXCLUDED", out


def test_a_gross_mismatch_from_a_wrongly_inferred_size_is_not_a_source_conflict():
    # 35849787: '32 patients (13%)' against an inferred arm size of 492 -- the TOTAL (32/246 = 13%). The numbers never
    # claimed to agree with 492; that is a failed denominator inference (not corroborated), not a conflict in the source.
    conflicts = []
    extract.extract_arm_counts("Reintubation occurred in 32 patients (13%) with high-flow and 45 patients (18%) with "
                               "conventional oxygen.", ["high-flow"], ["conventional"], None, {"i": 492, "c": 492},
                               conflicts=conflicts)
    assert conflicts == []


def test_a_count_pct_conflict_is_not_relabelled_extraction_debt():
    # consumer_consistency.annotate_review relabelled the served Akrami row 'KNOWN_REPORTED_NOT_YET_EXTRACTED' (and showed
    # the MACE counts 8/120 vs 28/129 as its GI value); a typed finding about the value found must survive it
    import json
    from pathlib import Path
    from harness import consumer_consistency as cc
    root = Path(__file__).resolve().parents[1]
    slug = "colchicine-secondary-cv-prevention"
    cfg = json.loads((root / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    blob = json.loads((root / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    row = {"label": "34876021", "id": "PMID 34876021", "absent_kind": "machine_absent",
           "reason_code": absence.COUNT_PCT_CONFLICT, "state": absence.COUNT_PCT_CONFLICT,
           "reason": extract.COUNT_PCT_CONFLICT + ": 3/129 = 2.326% but the source states 2.5%"}
    review = {"slug": slug, "outcomes": [{"name": "Gastrointestinal adverse effects", "trials": [],
                                          "declared_absent_trials": [row]}]}
    cc.annotate_review(review, slug, cfg, blob)
    assert row["reason_code"] == absence.COUNT_PCT_CONFLICT and "8/120" not in str(row.get("state_basis")), row
