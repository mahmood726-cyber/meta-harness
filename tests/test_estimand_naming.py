"""Estimand naming / compatibility-dimension plants for lane EN.

Each plant loads the committed pre-fix review object from aa8ed28a and proves the
defect is detectable there, then checks the rebuilt live object carries the new
typed disclosure. The pre-fix object is read with git show only; no checkout.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import harness.compat as CM

ROOT = Path(__file__).resolve().parents[1]
BASE = "aa8ed28a"


def _committed_review(slug: str) -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{BASE}:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
    )
    return json.loads(raw.decode("utf-8"))


def _committed_records(slug: str) -> dict[str, dict]:
    raw = subprocess.check_output(
        ["git", "show", f"{BASE}:cache/{slug}/records.json"],
        cwd=ROOT,
    )
    data = json.loads(raw.decode("utf-8"))
    return {str(r.get("id")): r for r in data.get("records", [])}


def _live_review(slug: str) -> dict:
    return json.load(open(ROOT / "docs" / "reviews" / slug / "review.json", encoding="utf-8"))


def _primary(review: dict) -> dict:
    return next(o for o in review["outcomes"] if o.get("primary"))


def _pooled_trials(review: dict) -> list[dict]:
    return _primary(review).get("trials") or []


def _row_texts(review: dict, records: dict[str, dict] | None = None) -> list[str]:
    rows = []
    records = records or {}
    for t in _pooled_trials(review):
        pid = str(t.get("id", "")).replace("PMID ", "")
        rec = records.get(pid) or {}
        rows.append(" ".join([rec.get("title", ""), rec.get("abstract", ""), t.get("source", "")]))
    return rows


def _declare_reason_contradicts_pool(review: dict, records: dict[str, dict] | None = None) -> bool:
    declare = next(
        x for x in review.get("estimand_exclusions", [])
        if x.get("trial") == "DECLARE-TIMI 58"
    )
    reason_blames_cvdeath = "Composite includes CV death" in declare.get("reason", "")
    all_pooled_cvdeath = all(
        ("cv death" in text.lower()) or ("cardiovascular causes" in text.lower())
        for text in _row_texts(review, records)
    )
    return reason_blames_cvdeath and all_pooled_cvdeath


def test_sglt2_ckd_composite_name_components_and_declare_plant():
    pre = _committed_review("sglt2-ckd-progression")
    pre_records = _committed_records("sglt2-ckd-progression")
    pre_primary = _primary(pre)
    assert pre_primary["name"] == "CKD progression / kidney composite outcome"
    assert not any(t.get("components") for t in _pooled_trials(pre))
    assert _declare_reason_contradicts_pool(pre, pre_records)

    live = _live_review("sglt2-ckd-progression")
    live_primary = _primary(live)
    assert live_primary["name"] == (
        "Trial-defined major kidney / cardiorenal composite (components differ by trial)"
    )
    assert all(t.get("components") for t in _pooled_trials(live))
    assert not _declare_reason_contradicts_pool(live)


def test_metformin_background_therapy_dimension_plant():
    pre = _committed_review("metformin-pcos-ovulation")
    clomifene_rows = [
        t for t in _pooled_trials(pre)
        if "clomifene" in (t.get("source", "") or "").lower()
        or "clomiphene" in (t.get("source", "") or "").lower()
    ]
    assert len(clomifene_rows) >= 2
    assert "background_therapy" not in (_primary(pre).get("compat_key") or {})

    live_key = _primary(_live_review("metformin-pcos-ovulation")).get("compat_key") or {}
    assert live_key["background_therapy"]["matched"] is True
    assert live_key["background_therapy"]["values"] == ["clomifene"]


def test_pericarditis_prior_disease_stage_dimension_plant():
    pre = _committed_review("colchicine-recurrent-pericarditis")
    pre_records = _committed_records("colchicine-recurrent-pericarditis")
    pre_sources = " ".join(_row_texts(pre, pre_records)).lower()
    assert "first recurrence" in pre_sources
    assert "multiple recurrence" in pre_sources or "multiple recurrences" in pre_sources
    assert "prior_disease_stage" not in (_primary(pre).get("compat_key") or {})

    live_key = _primary(_live_review("colchicine-recurrent-pericarditis")).get("compat_key") or {}
    dim = live_key["prior_disease_stage"]
    assert dim["matched"] is False
    assert sorted(dim["values"]) == ["first_recurrence", "multiple_recurrences"]
    assert any(
        m.get("code") == "COMPAT_DIMENSION_HETEROGENEOUS"
        and m.get("dimension") == "prior_disease_stage"
        for m in live_key.get("limitations", [])
    )


def test_statins_subgroup_evidence_unit_plant():
    pre = _committed_review("statins-primary-prevention-elderly")
    pre_jupiter = next(t for t in _pooled_trials(pre) if t.get("id") == "PMID 20404379")
    assert pre_jupiter.get("evidence_unit") is None

    live = _live_review("statins-primary-prevention-elderly")
    live_primary = _primary(live)
    live_jupiter = next(t for t in _pooled_trials(live) if t.get("id") == "PMID 20404379")
    assert live_jupiter["evidence_unit"] == "prespecified_subgroup"
    assert "subgroup" in live_primary["population"].lower()
    page = open(ROOT / "docs" / "reviews" / "statins-primary-prevention-elderly" / "index.html",
                encoding="utf-8").read()
    assert "k = 2 (1 trial + 1 pre-specified subgroup of JUPITER)" in page


def test_synthetic_prior_stage_and_background_dimension_controls():
    base = {
        "name": "x",
        "primary": True,
        "population": "intention-to-treat",
        "timepoint": "trial end",
        "result": {
            "k": 2,
            "scale": "RR",
            "estmeasure": {
                "status": "homogeneous",
                "classes": ["FIRST_EVENT_RATIO"],
                "labels": ["RR"],
                "canonicals": ["RISK_RATIO"],
            },
        },
        "trials": [
            {"id": "PMID 1", "prior_disease_stage": "recurrent", "background_therapy": "standard_care"},
            {"id": "PMID 2", "prior_disease_stage": "recurrent", "background_therapy": "standard_care"},
        ],
    }
    matched = CM.outcome_key(base, {"outcomes": [base]})
    assert matched["prior_disease_stage"]["matched"] is True
    assert matched["background_therapy"]["matched"] is True
    assert matched.get("limitations") == []
    assert CM.check({"outcomes": [base]}) == []

    mixed = dict(base)
    mixed["trials"] = [
        {"id": "PMID 1", "prior_disease_stage": "first_recurrence", "background_therapy": "none/placebo"},
        {"id": "PMID 2", "prior_disease_stage": "multiple_recurrences", "background_therapy": "clomifene"},
    ]
    unmatched = CM.outcome_key(mixed, {"outcomes": [mixed]})
    assert unmatched["prior_disease_stage"]["matched"] is False
    assert unmatched["background_therapy"]["matched"] is False
    assert {
        (m["dimension"], m["code"]) for m in unmatched["limitations"]
    } == {
        ("prior_disease_stage", "COMPAT_DIMENSION_HETEROGENEOUS"),
        ("background_therapy", "COMPAT_DIMENSION_HETEROGENEOUS"),
    }
    assert CM.check({"outcomes": [mixed]}) == []
