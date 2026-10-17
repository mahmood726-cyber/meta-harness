"""D04 option 1 as amended: fill an abstention, never overturn a finding.

Every test here fails before `harness/p5_admission.py` exists. The pair that matters is
`test_fills_an_unknown_cell` and `test_never_overturns_a_proven_exclusion`: they pass the SAME
admission row and differ only in the state of the cell, so the only thing they can be measuring is
the distinction Dispatch ruled on. If the state guard is deleted, the second one fails and the
first still passes.

The guards are tested INDEPENDENTLY on purpose. P53-49 -- the row the ruling names -- happens to
carry no `p5_absence_code`, so `load()` drops it before `fill()` is ever reached. A test that only
checked "P53-49 is not admitted" would therefore pass even with the amendment removed: it would be
passing for the wrong reason. `test_never_overturns_a_proven_exclusion` uses a synthetic row that
DOES carry a matching code, so it exercises the amendment itself.

The synthetic cells are synthetic deliberately. A control anchored to a live corpus retires itself
the moment the corpus is fixed: if these asserted the current state of a real family, repairing
that family's randomisation evidence would turn a correct repair into a red test.
"""
import json
import pathlib

from harness import p5_admission

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "evidence" / "p5_populations" / "ledger.json"

CODE = "ENTRY_POPULATION_NOT_ESTABLISHED"
ADMISSION = {
    "FAM-1": {
        "row_key": "P53-TEST",
        "p5_absence_code": CODE,
        "recovered_fact_ids": ["entry_population"],
        "ledger_sha256": "0" * 64,
    }
}


def test_fills_an_unknown_cell():
    """An abstention whose exact code the ledger recovered is filled, and says so."""
    out = p5_admission.fill({"state": "UNKNOWN", "absence_code": CODE}, "FAM-1", ADMISSION)
    assert out["state"] == "ELIGIBLE"
    assert out["span"]["eligibility_basis"] == p5_admission.FILLED_BASIS
    assert out["span"]["row_key"] == "P53-TEST"
    assert out["span"]["filled_absence_code"] == CODE
    assert out["span"]["decision"] == "D04-OPT1-AMENDED"
    # A filled cell must be distinguishable from one the structural screen established, or the page
    # cannot tell a reader which it is looking at.
    assert "absence_code" not in out


def test_never_overturns_a_proven_exclusion():
    """THE AMENDMENT, isolated so that only the state can be what stops the fill.

    The cell carries the SAME absence_code the admission recovered, so the code check cannot be
    what declines it. The first draft of this test used a cell shaped the way `cell('INELIGIBLE',
    span)` really builds one -- a span and no absence_code -- and a mutation probe showed it passed
    with the state guard DELETED, because the code check was quietly doing the work. It was
    measuring the wrong guard. Both guards are now pinned separately, below.
    """
    proven = {"state": "INELIGIBLE", "absence_code": CODE,
              "span": {"source": "AACT.designs", "row": {"allocation": "NON_RANDOMIZED"}}}
    out = p5_admission.fill(proven, "FAM-1", ADMISSION)
    assert out == proven, "a proven exclusion was overturned by a P5 admission"
    assert out["state"] == "INELIGIBLE"


def test_a_real_shaped_ineligible_cell_is_also_declined():
    """Defense in depth: the cell `cell('INELIGIBLE', span)` actually produces, with no code.

    This one is declined by the code check rather than the state check. Both layers are required:
    if the cell factory ever starts emitting an absence_code alongside a span, this test would
    still pass while only the state guard stood between a proven exclusion and an admission.
    """
    proven = {"state": "INELIGIBLE",
              "span": {"source": "AACT.designs", "row": {"allocation": "NON_RANDOMIZED"}}}
    assert p5_admission.fill(proven, "FAM-1", ADMISSION) == proven


def test_leaves_an_established_cell_untouched():
    """ELIGIBLE has no gap to fill; filling it again would restate its basis as an admission."""
    established = {"state": "ELIGIBLE", "span": {"design": {"allocation": "RANDOMIZED"}}}
    assert p5_admission.fill(established, "FAM-1", ADMISSION) == established


def test_requires_the_recovered_CODE_to_match_the_abstention():
    """A recovered entry-population span does not answer an abstention about the contrast."""
    other = {"state": "UNKNOWN", "absence_code": "INTERVENTION_CONTRAST_NOT_PROVEN"}
    assert p5_admission.fill(other, "FAM-1", ADMISSION) == other


def test_no_admissions_is_a_no_op():
    """With no ledger, or no row for this family, the corpus is unchanged."""
    cell = {"state": "UNKNOWN", "absence_code": CODE}
    assert p5_admission.fill(cell, "FAM-1", {}) == cell
    assert p5_admission.fill(cell, "FAM-1", None) == cell
    assert p5_admission.fill(cell, "SOMEONE-ELSE", ADMISSION) == cell


def test_load_admits_only_ALL_RECOVERED_rows_and_only_this_topic():
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    rows = doc["rows"]
    recovered = [r for r in rows if r["row_state"] == "ALL_RECOVERED"]
    coded = [r for r in recovered if r.get("p5_absence_code")]
    # measured on the committed ledger, not asserted from memory
    assert len(rows) == 53
    assert len(recovered) == 38
    assert len(coded) == 37

    total = sum(len(p5_admission.load(ROOT, slug)) for slug in sorted({r["slug"] for r in rows}))
    assert total == len(coded) == 37

    one = p5_admission.load(ROOT, "balanced-crystalloids-vs-saline-mortality")
    assert set(one) == {"NCT02721654", "NCT02875873"}
    assert one["NCT02721654"]["row_key"] == "P53-01"
    # measured from the committed ledger: P53-01 recovered BOTH facts, not the entry population
    # alone. If the ledger changes this fires, and it should -- the admission set changed.
    assert one["NCT02721654"]["recovered_fact_ids"] == ["entry_population", "randomized_contrast"]
    # every admission carries the digest of the bytes it came from
    assert len({a["ledger_sha256"] for a in one.values()}) == 1
    assert len(one["NCT02721654"]["ledger_sha256"]) == 64


def test_P53_49_is_admissible_by_the_ledger_and_still_not_admitted():
    """The row the ruling names. The ledger says ALL_RECOVERED; the rule still declines it.

    Documented here because the two reasons are independent and both must hold: the row names no
    abstention to fill (no p5_absence_code), and its family's cell is a proven exclusion, which
    test_never_overturns_a_proven_exclusion covers on a synthetic row.
    """
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    row = next(r for r in doc["rows"] if r["key"] == "P53-49")
    assert row["row_state"] == "ALL_RECOVERED"
    assert row["p5_absence_code"] is None
    assert row["slug"] == "spironolactone-hfref-mortality"
    assert "ALLOCATION_NOT_RANDOMIZED" in {b for f in row["facts"] for b in (f.get("blockers") or [])}
    assert p5_admission.load(ROOT, "spironolactone-hfref-mortality") == {}


def test_the_decision_is_recorded_with_its_signer():
    """The rule is a decision, not a preference: it carries who ruled and what they ruled."""
    d = p5_admission.DECISION
    assert d["id"] == "D04-OPT1-AMENDED"
    assert d["signer"] == "Dispatch, on Mahmood's delegation"
    assert "never overturns a fact proven INELIGIBLE" in d["ruling"]
    assert d["admits_row_state"] == "ALL_RECOVERED"


def test_the_served_sentence_says_which_families_are_eligible_by_ADMISSION():
    """A count cannot distinguish an admitted family from a screened one; the sentence must.

    Without this the page says 'eligible 3 of 23' and a reader has no way to learn that one of the
    three is eligible because a ledger row filled an abstention rather than because the structural
    screen established it. The gate does not catch that: the honest-state ratchet compares BLOCKS,
    and no block disappears when a number inside one moves.
    """
    from harness.trial_family import count_sentence

    base = {"trial_families": 23, "eligible_families": 3, "contributing": 2, "pooled": 2,
            "eligibility_unresolved": 19, "unresolved_report_candidates": 0,
            "contributing_without_structural_eligibility": []}

    with_admission = count_sentence(dict(base, eligible_by_p5_admission=["P53-01:NCT02721654"]))
    assert "Eligible by D04 ledger admission" in with_admission
    assert "P53-01:NCT02721654" in with_admission
    assert "never overturned" in with_admission

    without = count_sentence(dict(base, eligible_by_p5_admission=[]))
    assert "Eligible by D04 ledger admission rather than by the structural screen: none" in without
    assert "NCT02721654" not in without
