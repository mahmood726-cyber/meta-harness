"""Regression tests for the published-rate arm-count verification path (metformin-PCOS under-inclusion:
trials reporting '64% of 111' rather than a raw count). A count recovered from a published percentage
is `verified_handchecked` only when it round-trips to a '<x>%' token in the committed abstract AND the
denominator (or the equally-allocated total) is grounded there -- a wrong count or denominator must be
rejected, never trusted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import verify  # noqa: E402

_MOLL = ("111 women were allocated to clomifene citrate plus metformin (metformin group) and 114 women "
         "were allocated to clomifene citrate plus placebo (placebo group). The ovulation rate in the "
         "metformin group was 64% compared with 72% in the placebo group.")
_BEN = ("32 PCOS women were recruited in the study and equally allocated to the two groups. The ovulation "
        "rate in the metformin group was 62.5% compared with 37.5% in the placebo group.")


def test_published_rate_moll_round_trips():
    # 71/111 -> 63.96% -> '64%'; 82/114 -> 71.9% -> '72%'; denominators 111/114 literal.
    t = {"provenance": "published_rate", "ai": 71, "n1i": 111, "ci": 82, "n2i": 114}
    status, basis = verify.verify_pooled(t, _MOLL)
    assert status == "verified_handchecked", basis
    assert "round-trip" in basis


def test_published_rate_ben_ayed_uses_equal_allocation_total():
    # denominators 16/16 are not literal; the equally-allocated total 32 grounds them; 10/16=62.5%, 6/16=37.5%.
    t = {"provenance": "published_rate", "ai": 10, "n1i": 16, "ci": 6, "n2i": 16}
    status, _ = verify.verify_pooled(t, _BEN)
    assert status == "verified_handchecked"


def test_published_rate_rejects_wrong_count():
    # a count that does NOT round-trip to a published percentage must be rejected (not a trusted pass).
    t = {"provenance": "published_rate", "ai": 55, "n1i": 111, "ci": 82, "n2i": 114}  # 55/111=49.5%, not in text
    status, basis = verify.verify_pooled(t, _MOLL)
    assert status == "not-yet", basis
    assert "do not round-trip" in basis


def test_published_rate_rejects_when_denominator_absent():
    # right percentage but an ungrounded denominator (999 nowhere in the abstract, no matching total) -> reject.
    t = {"provenance": "published_rate", "ai": 640, "n1i": 999, "ci": 720, "n2i": 999}  # 640/999=64.06%->'64%'
    text = "ovulation rate in the metformin group was 64% compared with 72% in the placebo group."
    status, _ = verify.verify_pooled(t, text)
    assert status == "not-yet"


def test_literal_count_path_unchanged():
    # ordinary abstract provenance still requires literal digits (no behavioural change to the default path).
    t = {"provenance": "abstract", "ai": 9, "n1i": 12, "ci": 4, "n2i": 15}
    status, _ = verify.verify_pooled(t, "9 of 12 (75%) and 4 of 15 (27%) ovulated")
    assert status == "verified"
