"""Failure classes found by codex pr99-cap-r1 (13 Oct) in the regex readers V15-B lands, each executed and confirmed.
LOGGED, NOT FIXED (V1 freeze, Mahmood 13 Oct ruling 6: no regex rewrite for V1; every new failure class logged with a
plant; the typed / recorded reader is the first post-V1 item). None moves a served number: the V15-B render is
identical to the signed preview (16 of 32 topics, 0 pooled results moved). Each is a strict xfail: when the typed reader
fixes it, the xfail turns red and must be removed."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as g  # noqa: E402
from harness import screen_terms as st  # noqa: E402

FREEZE = "FAILURE CLASS (logged, V1 freeze, ruling 6; codex pr99-cap-r1 #{}): "


@pytest.mark.xfail(strict=True, reason=FREEZE.format(1) + "a thousands-separated count is cut at the comma")
def test_known_limit_thousands_separated_count():
    assert g.stated_k_from_text("We included 1,200 studies.")[0] == 1200


@pytest.mark.xfail(strict=True, reason=FREEZE.format(2) + "a spaced phase slash ('Phase 2 / 3') becomes a count")
def test_known_limit_spaced_phase_slash():
    assert g.stated_k_from_text("Phase 2 / 3 studies were included.") == (None, None)


@pytest.mark.xfail(strict=True, reason=FREEZE.format(3) + "'never included' is not read as a negation")
def test_known_limit_never_included():
    assert g.stated_k_from_text("Ten studies were never included. Five trials were included.")[0] == 5


@pytest.mark.xfail(strict=True, reason=FREEZE.format(4) + "comma-separated background drugs are dropped, so unequal "
                                                          "backgrounds compare equal")
def test_known_limit_comma_separated_backgrounds():
    assert st.placebo_masks_intervention({"arms": ["metformin, clomiphene", "placebo for metformin, letrozole"]},
                                         {"intervention_any": ["metformin"], "comparator_any": ["placebo"]}, "") is None


@pytest.mark.xfail(strict=True, reason=FREEZE.format(5) + "any comparator naming placebo overrides the protocol's "
                                                          "other comparator requirements")
def test_known_limit_placebo_override_drops_required_background():
    assert st.placebo_masks_intervention({"arms": ["letrozole plus metformin", "letrozole plus placebo for metformin"]},
                                         {"intervention_any": ["metformin"],
                                          "comparator_any": ["clomiphene plus placebo"]}, "") is None
