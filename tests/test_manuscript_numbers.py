"""Manuscript numerals are object-derived."""
from harness import manuscript


def test_PLANT_stale_membership_count_is_an_object_numeral():
    """iv-iron-hfref-hosp (2026-09-20): with CONFIRM-HF set aside the page said 'STALE: pooled membership known
    incomplete (10 eligible families not in the pool)' and the gate withheld the page -- the count is derived
    from the object by grade.missing_family_count but was never registered; the gate scans integers >= 10, so the
    defect was latent while the count was 9. The numeral is registered by the same derivation the sentence uses."""
    rows = [{"trial_key": f"T{i}"} for i in range(10)]
    review = {"outcomes": [{"primary": True, "result": {"k": 1}, "trials": [{"id": "PMID 1"}],
                            "declared_absent_trials": [{"id": f"PMID {i}"} for i in range(11)],
                            "known_missing_sensitivity": {"rows": rows}}],
              "invalidation": {"reasons": [{"code": "known_eligible_missing"}]}}
    from harness import grade
    assert grade.missing_family_count(review) == 10
    assert "10" in manuscript.object_numerals(review)
