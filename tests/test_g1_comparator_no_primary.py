"""G1 dpp4-mace-t2d: the registered comparator (PMID 34754403) pools NO result for the topic's primary outcome
(3-point MACE). Every effect it reports -- abstract and its held full text, verified as the named article -- is for a
component or another outcome (MI, stroke, HF hospitalisation, CV death, revascularisation, unstable angina,
arrhythmias). So no number on our side can 'agree' with it: the topic is COMPARATOR_NO_PRIMARY_RESULT, not NOT_YET.
An extraction miss (esketamine, melatonin: comparator estimate also None) must NOT be read as this."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import g1_tracker as gt  # noqa: E402


def _cfg(s):
    return json.load(open(os.path.join(ROOT, "topics", s + ".json"), encoding="utf-8"))


def test_dpp4_comparator_pools_no_primary_result():
    # Until 5 Oct dpp4's comparator (34754403) pooled no MACE result and the topic read COMPARATOR_NO_PRIMARY_RESULT. The
    # binding lane retired it under the pre-registered rule (85de6a23: NOT_ENUMERABLE_OPEN) and adopted 31462224, whose
    # league table states MACE (registry/comparator_results.json, read with the table's own measure). Restated: the
    # retirement carries that fact with a span verified in the held source, and the adopted comparator's result is what
    # the topic is judged on.
    import hashlib
    a = json.load(open(os.path.join(ROOT, "registry", "comparator_selection", "dpp4-mace-t2d.adoption.json"), encoding="utf-8"))
    r = a["retired"]
    assert a["comparator_pmid"] == "31462224" and r["comparator_pmid"] == "34754403" and r["reason_code"] == "NOT_ENUMERABLE_OPEN"
    src = os.path.join(ROOT, r["source"]["path"])
    assert hashlib.sha256(open(src, "rb").read()).hexdigest() == r["source"]["sha256"]
    held = open(src, encoding="utf-8").read()
    assert r["spans"] and all(sp in held for sp in r["spans"])
    res = json.load(open(os.path.join(ROOT, "registry", "comparator_results.json"), encoding="utf-8"))["dpp4-mace-t2d"]
    assert res["scale"] == "OR" and res["outcome"] == "MACE" and res["orientation_check"]["abstract_quote"]
    g = json.load(open(os.path.join(gt.G1_DIR, "dpp4-mace-t2d.json"), encoding="utf-8"))["g1_status"]
    assert g["state"] != "COMPARATOR_NO_PRIMARY_RESULT" and g["criteria"]["RESULT_AGREES"] is True


def test_an_extraction_miss_is_never_read_as_an_absence():
    for s in ("esketamine-trd-madrs", "melatonin-primary-insomnia-sol"):
        cfg = _cfg(s)
        assert gt.comparator_primary_absence(s, cfg, str(cfg["comparator_pmid"])) is None, s


def test_a_comparator_text_that_may_be_another_paper_never_shows_an_absence(monkeypatch):
    from kgap import k_gap
    cfg = _cfg("dpp4-mace-t2d")
    monkeypatch.setattr(k_gap, "held_text_identity", lambda a, h: {"state": "HELD_TEXT_NOT_NAMED_ARTICLE"})
    assert gt.comparator_primary_absence("dpp4-mace-t2d", cfg, str(cfg["comparator_pmid"])) is None
