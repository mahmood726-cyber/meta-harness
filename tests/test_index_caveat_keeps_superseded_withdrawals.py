"""Plant: the index banner's 'Located is not correct' caveat keeps counting a withdrawal after a signed
correction supersedes it. Before the fix it read only rev['withdrawn'], so the V7 corrections (which turn the
withdrawal into withdrawal_superseded and move the withdrawn number onto the admitted row) erased it."""
import json

from harness.index import _verification_section


def _write(tmp_path, slug, rev):
    d = tmp_path / "reviews" / slug
    d.mkdir(parents=True)
    (d / "review.json").write_text(json.dumps(rev), encoding="utf-8")


def test_superseded_withdrawal_still_counted(tmp_path):
    _write(tmp_path, "dapa", {
        "slug": "dapa",
        "withdrawal_superseded": {"date": "2026-09-19", "superseded_by": {"rendered_sha256": "ea2d"}},
        "outcomes": [{"trials": [{"id": "PMID 36027570", "label": "DELIVER", "verified": "verified",
                                  "served_pool_admission": {"supersedes_absence": [
                                      {"id": "PMID 36027570", "state": "RESULT_WITHDRAWN",
                                       "withdrawn_effect": {"effect": 0.88, "ci_low": 0.74, "ci_high": 1.05,
                                                            "scale": "HR"}}]}}]}]})
    html = _verification_section(str(tmp_path))
    assert "1 number(s) that passed this check digit for digit were withdrawn as the wrong endpoint" in html
    assert "dapa (36027570: HR 0.88 (0.74-1.05), withdrawn 2026-09-19" in html


def test_live_withdrawal_still_counted(tmp_path):
    _write(tmp_path, "empa", {
        "slug": "empa", "withdrawn": {"date": "2026-09-19"},
        "outcomes": [{"trials": [{"id": "x", "verified": "verified"}],
                      "declared_absent_trials": [{"label": "34449189", "absent_kind": "result_withdrawn",
                                                  "withdrawn_effect": {"effect": 0.91, "ci_low": 0.76,
                                                                       "ci_high": 1.09, "scale": "HR"}}]}]})
    assert "empa (34449189: HR 0.91 (0.76-1.09)" in _verification_section(str(tmp_path))
