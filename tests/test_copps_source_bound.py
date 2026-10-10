"""r24 COPPS: per-arm counts are SOURCE-BOUND or refused -- never reconstructed from percentages and a pooled total.
The 20/169 v 37/167 that stood in harness/known_missing.py were inferred (the auditor's source has 35 placebo events).

A claim that a source does NOT state a value is a recorded verification bound to the sha256 of the exact held text
(registry/source_absence_verifications.json). Codex copps-r11..r13 showed that no pattern over prose can prove absence:
each round found a new way to write counts ('20/100', 'deaths numbered 5 ... denominators were 100') or a new false
count ('5 of 10 centres'). So no text variant may produce SOURCE_ABSENT; only the verified held text does."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import known_missing as km  # noqa: E402

OUTCOME = {"name": "Postoperative atrial fibrillation", "estimand": "RR"}


def _held_copps():
    recs = json.load(open(os.path.join(ROOT, "cache", "colchicine-postop-af", "records.json"), encoding="utf-8"))
    return next(r for r in recs["records"] if str(r.get("id")) == "22090167")["abstract"]


def _value(text, pid="22090167"):
    return km._source_value("colchicine-postop-af", OUTCOME, {"id": f"PMID {pid}", "label": "x", "reason": "not pooled"},
                            {pid: {"id": pid, "abstract": text}}, {})


def test_PLANT_the_verified_held_copps_text_is_refused_never_inferred():
    out = _value(_held_copps())
    assert out["value_status"] == km.REFUSED_DENOMINATORS_NOT_STATED and out["missing_class"] == "SOURCE_ABSENT"
    assert not any(out.get(k) is not None for k in ("ai", "n1i", "ci", "n2i"))
    assert "336 patients" in out["source_span"] and "never reconstructed" in out["verify_basis"]
    assert "recorded verification" in out["verify_basis"]


def test_PLANT_no_literal_copps_counts_remain_in_the_harness():
    src = open(os.path.join(ROOT, "harness", "known_missing.py"), encoding="utf-8").read()
    for literal in ('"ai": 20', '"n1i": 169', '"ci": 37', '"n2i": 167'):
        assert literal not in src, literal


def test_a_refused_row_is_never_pooled_into_the_sensitivity():
    # build() pools only IN_COMMITTED_SOURCE rows: the refusal keeps COPPS out of the combined estimate
    assert km.REFUSED_DENOMINATORS_NOT_STATED != km.IN_COMMITTED_SOURCE


@pytest.mark.parametrize("text", [
    # codex r11#1: per-arm numbers stated, same record id
    "200 patients were randomized: 100 to colchicine and 100 to placebo. POAF occurred in 10 and 20 patients.",
    # r12#1 / r13#1: other ways of stating counts
    "Deaths were 20/100 versus 30/100 (20% versus 30%).",
    "Mortality was 5% versus 10%. Deaths numbered 5 in the treatment arm and 10 in the placebo arm; the randomized "
    "denominators were 100 and 100, respectively.",
    # r12#2 / r13#2: percentage-only texts that are NOT the verified held text are not certified absent either
    "Recruitment was completed at 5/10 centres. Mortality was 12.0% versus 22.0% among 336 patients.",
    "Of 200 participants, 5 of 10 centres were rural. Deaths were 20% versus 30%.",
])
def test_PLANT_codex_r11_r13_no_text_variant_is_certified_absent(text):
    out = _value(text)
    assert out["value_status"] != km.REFUSED_DENOMINATORS_NOT_STATED and out["missing_class"] != "SOURCE_ABSENT"


def test_PLANT_the_verification_is_bound_to_the_text_version_not_the_record_id():
    held = _held_copps()
    assert km.absence_verification("22090167", held)
    assert km.absence_verification("22090167", held + " ") is None          # a changed text inherits nothing
    assert km.absence_verification("1", held) is None                       # another record inherits nothing
