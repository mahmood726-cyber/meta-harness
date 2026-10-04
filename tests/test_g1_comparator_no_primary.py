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
    o = json.load(open(os.path.join(gt.G1_DIR, "dpp4-mace-t2d.json"), encoding="utf-8"))
    g = o["g1_status"]
    assert g["state"] == "COMPARATOR_NO_PRIMARY_RESULT" and g["unmet"] == ["COMPARATOR_PRIMARY_RESULT"]
    assert g["comparator_stated_trials"] == 6 and g["comparator_trials_listed"] == 5
    assert any("myocardial infarction" in p["sentence"] for p in g["comparator_pools"])
    assert not any("MACE" in p["sentence"] or "major adverse" in p["sentence"].lower() for p in g["comparator_pools"])


def test_an_extraction_miss_is_never_read_as_an_absence():
    for s in ("esketamine-trd-madrs", "melatonin-primary-insomnia-sol"):
        cfg = _cfg(s)
        assert gt.comparator_primary_absence(s, cfg, str(cfg["comparator_pmid"])) is None, s


def test_a_comparator_text_that_may_be_another_paper_never_shows_an_absence(monkeypatch):
    from kgap import k_gap
    cfg = _cfg("dpp4-mace-t2d")
    monkeypatch.setattr(k_gap, "held_text_identity", lambda a, h: {"state": "HELD_TEXT_NOT_NAMED_ARTICLE"})
    assert gt.comparator_primary_absence("dpp4-mace-t2d", cfg, str(cfg["comparator_pmid"])) is None
