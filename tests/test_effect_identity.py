"""EFFECT IDENTITY BEFORE SOURCE PREFERENCE (external review of colchicine-recurrent-pericarditis, 2026-09-26).

Plants are the PRE-FIX producer's own served output at the pinned candidate 3876a62d (immutable; a missing commit is a failure,
never a skip): there, CORP-2's "relative risk 0.49 (0.24-0.65)" is ADMITTED over its counts, and CORP's RRR 0.56 is served as RR
0.44 with KEEP_REPORTED_EFFECT and reported_label RR. The tests assert the defect is present in those bytes, then that
harness.effect_identity detects it. Synthetic controls pin every mislabel hypothesis in both directions."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import effect_identity as ei   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "colchicine-recurrent-pericarditis"


def _git_json(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in this clone's history (never a skip)", pytrace=False)
    return json.loads(p.stdout)


def _row(outcome, pmid):
    rev = _git_json(f"docs/reviews/{SLUG}/review.json")
    o = next(x for x in rev["outcomes"] if x["name"] == outcome)
    return next(t for t in o["trials"] if t["id"] == f"PMID {pmid}")


def _abstract(pmid):
    return {str(r["id"]): r for r in _git_json(f"cache/{SLUG}/records.json")["records"]}[pmid]["abstract"]


# ------------------------------------------------------------------ (1) CORP-2: a published RRR under an RR label
def test_plant_fires_pre_fix_corp2_is_served_admitted_over_its_own_counts():
    t = _row("Recurrent pericarditis", "24694983")
    assert (t["effect"], t["ci_low"], t["ci_high"], t["scale"]) == (0.49, 0.24, 0.65, "RR")
    assert t["selection_rule"] == "PUBLISHED_EFFECT_TARGET_CLASS"                     # the hierarchy preferred it ...
    alt = next(a for a in t["alternatives"] if a.get("ai") is not None)
    assert (alt["ai"], alt["n1i"], alt["ci"], alt["n2i"]) == (26, 120, 51, 120)      # ... over counts it disagrees with
    assert "relative risk 0·49" in _abstract("24694983")                         # the SOURCE itself says "relative risk"


def test_corp2_conflict_names_the_rrr_hypothesis_and_holds():
    c = ei.conflict_check(_row("Recurrent pericarditis", "24694983"))
    assert c["state"] == "SOURCE_EFFECT_CONFLICT" and c["code"] == "SOURCE_EFFECT_CONFLICT"
    assert c["counts_implied"]["RR"] == {"estimate": 0.5098, "ci_low": 0.3421, "ci_high": 0.7596}      # the review's 0.342-0.760
    assert c["matching_hypotheses"] == ["RRR_AS_RR"] and c["resolution"] == "HOLD"
    assert not next(h for h in c["hypotheses"] if h["hypothesis"] == "AS_LABELLED")["matches"]


def test_a_held_row_stays_visible_and_is_never_relabelled():
    t = dict(_row("Recurrent pericarditis", "24694983"))
    t["effect_conflict"] = ei.conflict_check(t)
    a = ei.held_absence(t)
    assert a["state"] == "HELD_SOURCE_EFFECT_CONFLICT" and a["candidate_tuple"] == {"effect": 0.49, "ci_low": 0.24, "ci_high": 0.65, "scale": "RR"}
    assert t["effect"] == 0.49 and t["scale"] == "RR"                                 # nothing rewritten


# ------------------------------------------------------------------ synthetic controls: every hypothesis, both directions
def _pub(scale, est, lo, hi, counts=(30, 100, 50, 100), source=""):
    return {"effect": est, "ci_low": lo, "ci_high": hi, "scale": scale, "source": source,
            "alternatives": [{"ai": counts[0], "n1i": counts[1], "ci": counts[2], "n2i": counts[3]}]}


def _implied(measure, counts=(30, 100, 50, 100)):
    d = ei.counts_tuple(*counts, measure)
    return round(d["estimate"], 2), round(d["ci_low"], 2), round(d["ci_high"], 2)


def test_consistent_published_rr_is_kept():
    assert ei.conflict_check(_pub("RR", *_implied("RR")))["state"] == "CONSISTENT"


def test_each_mislabel_is_named():
    rr, orr = _implied("RR"), _implied("OR")
    assert ei.conflict_check(_pub("RR", round(1 - rr[0], 2), round(1 - rr[2], 2), round(1 - rr[1], 2)))["matching_hypotheses"] == ["RRR_AS_RR"]
    assert ei.conflict_check(_pub("RR", *orr))["matching_hypotheses"] == ["OR_AS_RR"]
    assert ei.conflict_check(_pub("OR", *rr))["matching_hypotheses"] == ["RR_AS_OR"]
    assert ei.conflict_check(_pub("RR", round(1 / rr[0], 2), round(1 / rr[2], 2), round(1 / rr[1], 2)))["matching_hypotheses"] == ["RECIPROCAL"]


def test_an_unexplained_conflict_holds_and_a_documented_adjusted_model_is_kept_disclosed():
    c = ei.conflict_check(_pub("RR", 0.30, 0.20, 0.45))
    assert c["state"] == "SOURCE_EFFECT_CONFLICT" and c["matching_hypotheses"] == [] and c["resolution"] == "HOLD"
    t = _pub("RR", 0.30, 0.20, 0.45, source="the adjusted relative risk was 0.30")
    assert ei.conflict_check(t, ei.adjusted_documented(t))["resolution"] == "KEEP_DISCLOSED"


def test_hr_is_not_comparable_to_crude_counts_and_a_zero_cell_is_not_guessed():
    assert ei.conflict_check(_pub("HR", 0.5, 0.3, 0.8))["state"] == "NOT_COMPARABLE"
    assert ei.conflict_check(_pub("RR", 0.5, 0.3, 0.8, counts=(0, 100, 5, 100)))["state"] == "NOT_COMPARABLE"


@pytest.mark.parametrize("text,expected", [("age-adjusted rate ratio 0.85", True), ("adjusted hazard ratio, 0.97", True),
                                           ("multivariate model to adjust for age", True),
                                           ("97.5% CI (multiplicity-adjusted for the two doses)", False),
                                           ("dose-adjusted apixaban", False), ("rate ratio 0.85; 95% CI 0.76-0.94", False)])
def test_adjusted_model_evidence_is_covariate_adjustment_only(text, expected):
    assert ei.adjusted_documented({"source": text}) is expected


# ------------------------------------------------------------------ (2) CORP: transformation provenance
def test_plant_fires_pre_fix_corp_rrr_is_served_as_a_reported_rr():
    for outcome in ("Recurrent pericarditis", "Symptom persistence at 72 hours"):
        t = _row(outcome, "21873705")
        assert t["selection_rule"] == "KEEP_REPORTED_EFFECT" and t["scale"] == "RR" and "effect_transform" not in t
        assert (t.get("effect_object") or {}).get("reported_label") == "RR"


def test_the_transform_is_recorded_from_the_source_including_the_symmetric_ci():
    ab = _abstract("21873705")
    rec = ei.transform_provenance(_row("Recurrent pericarditis", "21873705"), ab)
    assert rec["reported_measure"] == "RRR" and rec["reported"] == {"estimate": 0.56, "ci_low": 0.27, "ci_high": 0.73}
    assert rec["derived"] == {"measure": "RR", "estimate": 0.44, "ci_low": 0.27, "ci_high": 0.73}
    assert rec["read_from"] == "held abstract" and "symmetric" in rec["note"]       # the quotation is cut mid-CI
    sym = ei.transform_provenance(_row("Symptom persistence at 72 hours", "21873705"), ab)
    assert sym["reported"] == {"estimate": 0.56, "ci_low": 0.27, "ci_high": 0.74} and sym["derived"]["ci_low"] == 0.26 and sym["note"] is None


def test_a_nearby_effect_that_does_not_reproduce_the_served_tuple_is_never_taken():
    t = {"effect": 0.50, "ci_low": 0.30, "ci_high": 0.70, "scale": "RR",
         "source": "abstract effect+CI (RR): relative risk reduction, 0.56 [CI, 0.27 to 0.73]"}
    assert ei.transform_provenance(t) is None


def test_the_hold_reaches_the_reader_the_absence_layer_does_not_relabel_it():
    """The absence audit re-classified the held row as EXTRACTION_NOT_PERFORMED (seen in a real build): a hold read as 'not
    extracted'. A held row keeps its own state and code through absence.classify_reason."""
    from harness import absence
    t = dict(_row("Recurrent pericarditis", "24694983"))
    t["effect_conflict"] = ei.conflict_check(t)
    a = ei.held_absence(t)
    got = absence.classify_reason(["recurrent pericarditis"], _abstract("24694983"), row=a)
    assert got["reason_code"] == "SOURCE_EFFECT_CONFLICT" and got["state"] == "HELD_SOURCE_EFFECT_CONFLICT"
