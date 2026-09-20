"""RESULT WITHDRAWN is a typed publishable state (Mahmood, 2026-09-19): dapagliflozin-hfpef-hosp and
empagliflozin-hfpef-hosp served a CV-death-only registry measure as their composite primary; the pages stay up,
state what was published, what the held evidence holds, why, and that the corrected estimate is not yet
published -- and pool nothing. The gate passes that state only when it is complete and uncontradicted."""
import json
import shutil
from pathlib import Path

import pytest

from harness import gate

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ("dapagliflozin-hfpef-hosp", "empagliflozin-hfpef-hosp")


@pytest.mark.parametrize("slug", SLUGS)
def test_withdrawn_page_pools_nothing_states_everything_and_passes_the_gate(slug):
    review = json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))
    prim = review["outcomes"][0]
    assert prim["trials"] == [] and not (prim.get("result") or {}).get("k")
    withdrawn_rows = [t for t in prim["declared_absent_trials"] if t.get("absent_kind") == "result_withdrawn"]
    assert len(withdrawn_rows) == 1 and withdrawn_rows[0]["withdrawn_effect"]["effect"] in (0.88, 0.91)
    w = review["withdrawn"]
    joined = " ".join(w["statements"]).lower()
    for needle in ("what was published", "what the held evidence holds", "why", "not yet published", "clinicaltrials.gov"):
        assert needle in joined, needle
    assert "grade" not in review, "a withdrawn result carries no certainty rating"
    page = (ROOT / "docs/reviews" / slug / "index.html").read_text(encoding="utf-8")
    assert "RESULT WITHDRAWN" in page
    ok, reasons = gate.gate_page(str(ROOT / "docs/reviews" / slug))
    assert ok, reasons


def _copy(tmp_path, slug):
    d = tmp_path / slug
    shutil.copytree(ROOT / "docs/reviews" / slug, d)
    return d


def test_withdrawn_declared_with_a_number_still_pooled_is_refused(tmp_path):
    d = _copy(tmp_path, SLUGS[0])
    review = json.loads((d / "review.json").read_text(encoding="utf-8"))
    review["outcomes"][0]["result"] = {"present": True, "k": 1, "estimate": 0.88}
    (d / "review.json").write_text(json.dumps(review), encoding="utf-8")
    reasons = gate.check_primary_result(str(d))
    assert reasons and "still pools k=1" in reasons[0], reasons


def test_withdrawn_declared_without_its_statements_is_refused(tmp_path):
    d = _copy(tmp_path, SLUGS[0])
    review = json.loads((d / "review.json").read_text(encoding="utf-8"))
    review["withdrawn"] = {"date": "2026-09-19", "summary": "withdrawn", "statements": ["withdrawn"], "status": "x"}
    (d / "review.json").write_text(json.dumps(review), encoding="utf-8")
    reasons = gate.check_primary_result(str(d))
    assert reasons and "at least four" in reasons[0] and "what was published" in reasons[0], reasons


def test_withdrawn_declared_but_page_without_notice_is_refused(tmp_path):
    d = _copy(tmp_path, SLUGS[1])
    page = (d / "index.html").read_text(encoding="utf-8").replace("RESULT WITHDRAWN", "RESULT")
    (d / "index.html").write_text(page, encoding="utf-8")
    reasons = gate.check_primary_result(str(d))
    assert reasons and "no RESULT WITHDRAWN notice" in reasons[0], reasons


def test_absent_primary_without_withdrawal_is_still_refused(tmp_path):
    """The withdrawn state must not have loosened the original rule."""
    d = _copy(tmp_path, SLUGS[0])
    review = json.loads((d / "review.json").read_text(encoding="utf-8"))
    review.pop("withdrawn")
    (d / "review.json").write_text(json.dumps(review), encoding="utf-8")
    reasons = gate.check_primary_result(str(d))
    assert reasons and "must not publish" in reasons[0], reasons
