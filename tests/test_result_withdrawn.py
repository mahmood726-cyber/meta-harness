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


# Packet V7 ('yes v7', 5/6 Oct 2026) is the corrected selection the withdrawal waited for: dapagliflozin -> DELIVER's
# posted composite HR 0.82 (0.73-0.92); empagliflozin -> EMPEROR-Preserved's HR 0.79 (0.69-0.90). The served page now
# pools exactly that signed row; the withdrawal stays on the record (withdrawal_superseded, naming the signature) and
# the withdrawn value stays disclosed on the row that replaced it. The withdrawn-state gate rules below are unchanged.
CORRECTED = {"dapagliflozin-hfpef-hosp": ("PMID 36027570", 0.82, "ea2d55e3759211f2de812f18d4d5644c76e97de716565dcc4c4e5a53f84a347c"),
             "empagliflozin-hfpef-hosp": ("PMID 34449189", 0.79, "9aa0336c4b75225dcc61539026f1d4bce9fa9de405bd30cf4f76c93259c26db3")}


@pytest.mark.parametrize("slug", SLUGS)
def test_a_signed_corrected_selection_ends_the_withdrawal_and_keeps_it_on_the_record(slug):
    rid, est, sha = CORRECTED[slug]
    review = json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))
    prim = review["outcomes"][0]
    assert [t["id"] for t in prim["trials"]] == [rid] and prim["result"]["k"] == 1 and prim["result"]["estimate"] == est
    sup = prim["trials"][0]["served_pool_admission"]["supersedes_absence"]
    assert any(x["state"] == "RESULT_WITHDRAWN" and (x.get("withdrawn_effect") or {}).get("effect") in (0.88, 0.91) for x in sup)
    assert "withdrawn" not in review and review["withdrawal_superseded"]["superseded_by"]["rendered_sha256"] == sha
    joined = " ".join(review["withdrawal_superseded"]["statements"]).lower()
    for needle in ("what was published", "what the held evidence holds", "why", "clinicaltrials.gov"):
        assert needle in joined, needle
    ok, reasons = gate.gate_page(str(ROOT / "docs/reviews" / slug))
    assert ok, reasons


def _copy(tmp_path, slug):
    """A copy of the served page put back in the WITHDRAWN state (the corrected page carries the withdrawal as
    withdrawal_superseded): pools nothing, declares the withdrawal, and the page states RESULT WITHDRAWN."""
    d = tmp_path / slug
    shutil.copytree(ROOT / "docs/reviews" / slug, d)
    review = json.loads((d / "review.json").read_text(encoding="utf-8"))
    if "withdrawal_superseded" in review:
        w = dict(review.pop("withdrawal_superseded"))
        w.pop("superseded_by", None)
        review["withdrawn"] = w
        review["outcomes"][0]["trials"] = []
        review["outcomes"][0]["result"] = {"present": False}
        (d / "review.json").write_text(json.dumps(review), encoding="utf-8")
        page = (d / "index.html").read_text(encoding="utf-8")
        (d / "index.html").write_text(page + "<div id='result-withdrawn'>RESULT WITHDRAWN</div>", encoding="utf-8")
    return d


def test_the_withdrawn_state_itself_still_passes_its_gate_rule(tmp_path):
    for slug in SLUGS:
        assert gate.check_primary_result(str(_copy(tmp_path, slug))) == []


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
