"""Plants for the v3 sentence-scoped RoB 2 rules (robgrade/rob2_typed.SENTENCE_RULES). Each rule must fire on its
recorded positive sentences and on them INSIDE a longer text (the engine splits sentences; a whole-text match with the
\\A...\\Z guard would never fire); and must not fire on its recorded near-misses (negation, hedge, other trial)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import rob2_typed as rt  # noqa: E402

PROPS = {r["rule_id"]: r for r in json.load(open(os.path.join(ROOT, "outputs", "robgrade", "dev", "rule_proposals_r2.json"),
                                                 encoding="utf-8"))["rules"]}


def _src(text):
    return [{"id": "fulltext:PMID 1", "kind": "fulltext", "text": text, "sha256": "0" * 64, "open_for_prompt": True}]


def test_every_sentence_rule_is_a_reviewed_proposal_verbatim():
    assert len(rt.SENTENCE_RULES) == 3
    for q, a, rid, pat in rt.SENTENCE_RULES:
        p = PROPS[rid]
        assert (q, a, pat) == (p["question"], p["answer"], p["pattern"])


def test_PLANT_fires_on_its_positives_inside_a_longer_text():
    for q, a, rid, _ in rt.SENTENCE_RULES:
        for pos in PROPS[rid]["fires_on"]:
            text = "Methods were as published.\nPatients were enrolled at 12 sites. " + pos + " Results follow."
            got = rt.sentence_answers(_src(text))
            assert q in got and got[q]["answer"] == a and got[q]["rule_id"] == rid, (rid, pos)


def test_PLANT_never_fires_on_its_near_misses():
    for q, a, rid, _ in rt.SENTENCE_RULES:
        for neg in PROPS[rid]["must_not_fire_on"]:
            got = rt.sentence_answers(_src("Patients were enrolled at 12 sites. " + neg + " Results follow."))
            assert got.get(q, {}).get("rule_id") != rid, (rid, neg)


def test_PLANT_an_answered_question_is_not_overridden():
    q, a, rid, _ = rt.SENTENCE_RULES[0]
    got = rt.sentence_answers(_src(PROPS[rid]["fires_on"][0]), answered={q: {}})
    assert q not in got


def test_PLANT_typed_answers_uses_sentence_rules():
    pos = PROPS["regex:assessors_blinded_relative_clause_v1"]["fires_on"][1]
    typed, _ = rt.typed_answers(_src("We did a trial. " + pos))
    assert typed["4.3"]["answer"] == "N"
