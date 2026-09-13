"""NOT_RUN-as-paywalled gate limb (audit 22).

A review must not assert a full-text ACCESS OUTCOME (re-tested at full text / publisher-blocked / access-blocked
/ paywalled / confirmed at full-text level) when the PMC full-text adapter never ran (source_status == NOT_RUN):
the adapter established nothing about access, so the claim is manufactured — and it is used to justify excluding
poolable trials. Stating the adapter did not run and a count is absent from the committed abstract is honest and
must pass; asserting a tested access barrier we never tested must fail closed.

The synthetic cases are PLANTS: the offending review has poolable-looking content and only the fabricated access
phrase + NOT_RUN adapter distinguishes it — without the limb it would sail through the gate."""
import glob
import json
import os
import tempfile

from harness.gate import check_access_claim_supported

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")


def _write_review(tmp, source_status, reason):
    d = os.path.join(tmp, "rv")
    os.makedirs(d, exist_ok=True)
    rev = {"topic": "__plant__",
           "search": {"source_status": source_status},
           "reproduction": {"refusals": [{"trial": "X", "not_pooled_because": reason}]}}
    with open(os.path.join(d, "review.json"), "w", encoding="utf-8") as f:
        json.dump(rev, f)
    return d


def test_gate_refuses_access_claim_when_fulltext_adapter_not_run():
    with tempfile.TemporaryDirectory() as tmp:
        d = _write_review(tmp, {"PMC full text": "NOT_RUN"},
                          "counts are full-text only and the publisher pages are access-blocked / paywalled")
        r = check_access_claim_supported(d)
        assert r, "gate did not fire on a paywalled/access-blocked claim while the adapter was NOT_RUN"
        assert "access outcome" in r[0].lower()


def test_gate_passes_honest_not_run_wording():
    with tempfile.TemporaryDirectory() as tmp:
        d = _write_review(tmp, {"PMC full text": "NOT_RUN"},
                          "the count is absent from the committed abstract; the PMC full-text adapter did not "
                          "run in this build, so full-text access was not established")
        assert check_access_claim_supported(d) == [], "honest NOT_RUN wording must pass"


def test_gate_passes_access_claim_when_adapter_ran():
    # If the full-text adapter actually ran, an access finding is not manufactured — not this limb's business.
    with tempfile.TemporaryDirectory() as tmp:
        d = _write_review(tmp, {"PMC full text": "RAN_OK"},
                          "re-tested at full text: the counts are paywalled")
        assert check_access_claim_supported(d) == [], "an access claim with the adapter RAN_OK must not fail here"


def test_corpus_no_unsupported_access_claims():
    """Every shipped review must pass the limb: no topic asserts a tested full-text access outcome while its
    full-text adapter is NOT_RUN. (corticosteroids-covid and sglt2-ckd were the two that did.)"""
    offenders = []
    for p in glob.glob(os.path.join(DOCS, "reviews", "*", "review.json")):
        d = os.path.dirname(p)
        if check_access_claim_supported(d):
            offenders.append(os.path.basename(d))
    assert not offenders, f"unsupported full-text access claims remain in: {offenders}"
