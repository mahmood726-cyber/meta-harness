"""Plant: a withdrawal superseded by a signed correction stays stated in the OVERVIEW (review page AND the neutral
docs/m page). Before the fix the overview rendered only a live withdrawal, so the V7 corrections made the neutral pages
of dapagliflozin and empagliflozin go quiet: the corrected number with no trace of the withdrawn one."""
from harness import page

REV = {"title": "t", "question": "q",
       "withdrawal_superseded": {"date": "2026-09-19", "summary": "The result previously published was a component.",
                                 "statements": ["What was published: DELIVER HR 0.88 (0.74 to 1.05)",
                                                "The corrected estimate is not yet published: ..."],
                                 "superseded_by": {"rendered_sha256": "ea2d55e3759211f2de81", "notice_when_utc": "2026-10-05T17:01:45Z"}}}


def test_overview_states_the_corrected_withdrawal_on_both_renders():
    for neutral in (False, True):
        html = page.render_overview(REV, neutral=neutral)
        assert "RESULT CORRECTED" in html and "withdrew on 2026-09-19" in html
        assert "HR 0.88 (0.74 to 1.05)" in html and "ea2d55e3759211f2" in html
        assert "RESULT WITHDRAWN -- this page no longer states" not in html


def test_live_withdrawal_still_renders_withdrawn():
    r = dict(REV)
    r["withdrawn"] = r.pop("withdrawal_superseded")
    assert "RESULT WITHDRAWN" in page.render_overview(r) and "RESULT CORRECTED" not in page.render_overview(r)
