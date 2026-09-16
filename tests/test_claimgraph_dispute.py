"""A refusal row that names a POOLED trial is a contradiction (REFUSED_AND_POOLED) unless it carries a
complete, signed dispute; the dispute is then rendered and counted, never silent. Integrator plant
for the metformin-pcos-ovulation instance the merged claim graph caught on 2026-09-16."""
from harness import claimgraph


def _review(pooled_ids=("PMID 16769748", "PMID 11172832")):
    return {
        "slug": "metformin-pcos-ovulation",
        "outcomes": [{"name": "Ovulation rate", "primary": True,
                      "trials": [{"id": i, "label": i.split()[-1], "ai": 1, "ci": 1, "n1i": 2, "n2i": 2}
                                 for i in pooled_ids]}],
    }


def _row(disputed=None):
    row = {"trial": "Moll (16769748)", "verified": "ovulation %s located",
           "not_pooled_because": "background clomifene; treatment-naive population"}
    if disputed is not None:
        row["disputed"] = disputed
    return row


FULL = {"pooled_trial_keys": ["16769748"], "decision_owed_to": "Mahmood",
        "signed_by": "integrator", "date": "2026-09-16", "reason": "both policies declared on purpose"}


def _codes(review, rows):
    return [v["code"] for v in claimgraph.check(review, {"refusals": rows})]


def test_refusal_naming_pooled_trial_fires_without_dispute():
    assert _codes(_review(), [_row()]) == ["REFUSED_AND_POOLED"]


def test_complete_signed_dispute_clears_violation_and_is_counted():
    review = _review()
    assert _codes(review, [_row(FULL)]) == []
    ds = claimgraph.disputes(review, {"refusals": [_row(FULL)]})
    assert len(ds) == 1 and ds[0]["code"] == "POOL_SCOPE_DISPUTE" and ds[0]["trial_keys"] == ["16769748"]


def test_unsigned_or_partial_dispute_still_fires():
    for missing in ("signed_by", "decision_owed_to", "reason", "date"):
        d = {k: v for k, v in FULL.items() if k != missing}
        assert _codes(_review(), [_row(d)]) == ["REFUSED_AND_POOLED"], missing
    # a dispute that names a DIFFERENT trial than the one pooled does not cover the hit
    d = dict(FULL, pooled_trial_keys=["11172832"])
    assert _codes(_review(), [_row(d)]) == ["REFUSED_AND_POOLED"]


def test_dispute_on_unpooled_trial_is_not_a_dispute():
    review = _review(pooled_ids=("PMID 11172832",))
    assert _codes(review, [_row(FULL)]) == []
    assert claimgraph.disputes(review, {"refusals": [_row(FULL)]}) == []
