"""RESULT WITHDRAWN is a typed publishable state (Mahmood, 2026-09-19): dapagliflozin-hfpef-hosp and
empagliflozin-hfpef-hosp served a CV-death-only registry measure as their composite primary; the pages stayed up,
stated what was published, what the held evidence holds, why, and that the corrected estimate was not yet published --
and pooled nothing. The gate passes that state only when it is complete and uncontradicted.

V1.0.1 (lane NR) RESTORED both results (DELIVER HR 0.82; EMPEROR-Preserved HR 0.79 at 95.03%) through result-change
notices owed Mahmood's countersignature, and the topics keep the withdrawal as `withdrawal_history`. The live pages are
therefore no longer withdrawn; the MECHANISM is still tested, on the withdrawn pages exactly as V1.0 served them
(frozen at 3876a62d in tests/fixtures/result_withdrawn/)."""
import json
import shutil
from pathlib import Path

import pytest

from harness import gate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "result_withdrawn"
SLUGS = ("dapagliflozin-hfpef-hosp", "empagliflozin-hfpef-hosp")


@pytest.mark.parametrize("slug", SLUGS)
def test_withdrawn_page_pools_nothing_states_everything_and_passes_the_primary_check(slug):
    review = json.loads((FIXTURES / slug / "review.json").read_text(encoding="utf-8"))
    prim = review["outcomes"][0]
    assert prim["trials"] == [] and not (prim.get("result") or {}).get("k")
    withdrawn_rows = [t for t in prim["declared_absent_trials"] if t.get("absent_kind") == "result_withdrawn"]
    assert len(withdrawn_rows) == 1 and withdrawn_rows[0]["withdrawn_effect"]["effect"] in (0.88, 0.91)
    w = review["withdrawn"]
    joined = " ".join(w["statements"]).lower()
    for needle in ("what was published", "what the held evidence holds", "why", "not yet published", "clinicaltrials.gov"):
        assert needle in joined, needle
    assert "grade" not in review, "a withdrawn result carries no certainty rating"
    page = (FIXTURES / slug / "index.html").read_text(encoding="utf-8")
    assert "RESULT WITHDRAWN" in page
    assert gate.check_primary_result(str(FIXTURES / slug)) == []


@pytest.mark.parametrize("slug,estimate", [("dapagliflozin-hfpef-hosp", 0.82), ("empagliflozin-hfpef-hosp", 0.79)])
def test_the_restored_page_pools_its_result_and_keeps_the_withdrawal_as_history(slug, estimate):
    review = json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))
    prim = review["outcomes"][0]
    assert "withdrawn" not in review
    assert prim["result"]["k"] == 1 and prim["result"]["estimate"] == pytest.approx(estimate)
    topic = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))["primary_outcome"]
    hist = topic["withdrawal_history"]
    assert hist["resolved"] and len(hist["statements"]) >= 4 and "withdrawn" not in topic
    assert gate.check_primary_result(str(ROOT / "docs/reviews" / slug)) == []


def _copy(tmp_path, slug):
    d = tmp_path / slug
    shutil.copytree(FIXTURES / slug, d)
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
