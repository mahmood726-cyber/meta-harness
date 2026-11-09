"""Direction and null conclusions are separate claims (fix114b plants)."""
import pytest

from harness import page, result_changes


@pytest.mark.parametrize("scale,before,after,word", [
    ("HR", 1.13, 0.97, "changed"),
    ("HR", 1.13, 1.05, "unchanged"),
    ("MD", -1.13, 0.97, "changed"),
    ("MD", -1.13, -1.05, "unchanged"),
    ("HR", 1.13, 1.0, "changed"),
])
def test_notice_direction_separate_from_null(scale, before, after, word):
    null = result_changes.null_value(scale)
    n = {"scale": scale, "rendering_version": 2,
         "before": {"k": 3, "estimate": before, "ci_low": null - 2, "ci_high": null + 2},
         "after": {"k": 3, "estimate": after, "ci_low": null - 2, "ci_high": null + 2}}
    html = page.result_change_block(n)
    assert f"The direction of the estimate is {word}." in html
    assert "The conclusion about no difference is unchanged: both intervals include the null." in html


def test_notice_missing_interval_is_not_claimed_to_include_null():
    n = {"rendering_version": 2, "scale": "HR",
         "before": {"k": 2, "estimate": 1.13},
         "after": {"k": 3, "estimate": 0.97, "ci_low": 0.4, "ci_high": 2.3}}
    html = page.result_change_block(n)
    assert "The direction of the estimate is changed." in html
    assert "an interval was not served" in html
    assert "both intervals include" not in html


def test_notice_v2_signature_binds_same_text_after_signing():
    n = {"rendering_version": 2, "scale": "HR",
         "before": {"k": 3, "estimate": 1.13, "ci_low": 0.9, "ci_high": 1.3},
         "after": {"k": 3, "estimate": 0.97, "ci_low": 0.9, "ci_high": 1.3}}
    def block(notice):
        return page.result_change_block(notice).split("<p class='muted'>Reviewer countersignature")[0]
    before = block(n)
    n["reviewer_countersignature"] = {"state": "SEEN_AND_SIGNED"}
    assert block(n) == before


@pytest.mark.parametrize("scale,estimate", [(None, 0.97), ("HR", None)])
def test_notice_direction_unavailable_is_not_unchanged(scale, estimate):
    n = {"rendering_version": 2, "scale": scale,
         "before": {"k": 3, "estimate": 1.13}, "after": {"k": 3, "estimate": estimate}}
    assert "direction of the estimate cannot be compared" in page.result_change_block(n)
