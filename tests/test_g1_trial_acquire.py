"""scripts/g1_trial_acquire.py gates (the 2 Oct one-primary-source decision) and g1_tracker.acquired_merge: a model's
answer is admitted only when a deterministic gate finds it in the trial's own source; never from the comparator; a scope
claim only under a protocol rule that is SET (iv-iron's design_double_blind is false: EFFECT-HF's 'open-label' names
nothing)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import g1_trial_acquire as ga  # noqa: E402

CFG = {"primary_outcome": {"name": "Heart-failure hospitalization", "estimand": "RR", "population": "intention-to-treat",
                           "keywords": ["hospitalization for worsening heart failure"]},
       "include": {"design_double_blind": False, "population_any": ["heart failure"]}}
REG = {"outcomes": {"1": {"title": "Number of Hospitalizations for Heart Failure", "type": "SECONDARY",
                          "time_frame": "12 months"}},
       "groups": {"1": [{"group": "g1", "count": 297, "n": 1532}, {"group": "g2", "count": 332, "n": 1533}]},
       "analyses": [], "group_titles": {}}
TEXT = ("Results. Hospitalization for worsening heart failure occurred in 12/80 patients assigned to ferric carboxymaltose "
        "and in 20/81 patients assigned to placebo during follow-up.")


def _held(text="", reg=None):
    return {"text": text, "sha": "x", "terms": ["hospitalization for worsening heart failure"], "comp": "39727669",
            "aact": {"NCT03037931": {"state": "POSTED", "_reg": reg, "snapshot": {"id": "AACT 2026-08-30"}}} if reg else {}}


def _resp(**kw):
    base = {"verdict": "FOUND", "source": "AACT", "source_ref": "NCT03037931", "aact_outcome_id": "1", "measure": "COUNTS",
            "events_t": 297, "n_t": 1532, "events_c": 332, "n_c": 1533, "effect": None, "lower": None, "upper": None,
            "quote": "297 1532 332 1533", "scope_rule_key": None, "scope_span": None}
    base.update(kw)
    return base


def test_posted_participant_counts_are_admitted():
    v, adm = ga.gate(_resp(), _held(reg=REG), CFG, "iv-iron-hfref-hosp")
    assert v == "ADMITTED" and adm["kind"] == "AACT"


def test_counts_that_are_not_the_posted_ones_are_refused():
    v, _ = ga.gate(_resp(events_t=290), _held(reg=REG), CFG, "iv-iron-hfref-hosp")
    assert v == "REFUSED:TUPLE_NOT_THE_POSTED_RESULT"


def test_text_counts_need_a_verbatim_quote_holding_every_number():
    ok = _resp(source="PMC_TEXT", source_ref="28701470", events_t=12, n_t=80, events_c=20, n_c=81,
               quote="occurred in 12/80 patients assigned to ferric carboxymaltose and in 20/81 patients")
    assert ga.gate(ok, _held(TEXT), CFG, "iv-iron-hfref-hosp")[0] == "ADMITTED"
    assert ga.gate(dict(ok, quote="occurred in 12 of 80 patients"), _held(TEXT), CFG, "x")[0] == \
        "REFUSED:QUOTE_NOT_VERBATIM_IN_WHOLE_TEXT"
    assert ga.gate(dict(ok, n_c=88), _held(TEXT), CFG, "x")[0] == "REFUSED:NUMBERS_NOT_IN_QUOTE"


def test_the_comparator_is_never_a_source_and_a_scope_rule_must_be_set():
    assert ga.gate(_resp(source="PMC_TEXT", source_ref="39727669"), _held(TEXT), CFG, "x")[0] == \
        "REFUSED:SOURCE_IS_COMPARATOR"
    sc = _resp(verdict="SCOPE_DIFFERENCE", scope_rule_key="design_double_blind", scope_span="assigned to placebo")
    assert ga.gate(sc, _held(TEXT), CFG, "x")[0] == "REFUSED:SCOPE_RULE_NOT_SET_IN_PROTOCOL"


def test_an_admitted_row_matches_the_trial_and_promotes_a_secondary_single(monkeypatch):
    row = {"label": "HEART-FID [11]", "verdict": "ADMITTED", "record_id": "mc-x",
           "admitted": {"kind": "AACT", "source": "AACT 2026-08-30 NCT03037931 outcome 1", "span": "s", "quote": "q",
                        "value": {"measure": "RR", "effect": None, "lower": None, "upper": None, "events_t": 297,
                                  "n_t": 1532, "events_c": 332, "n_c": 1533}}}
    monkeypatch.setattr(gt, "acquired_rows", lambda slug: {"HEART-FID [11]": row})
    cr = {"effect": None, "lower": None, "upper": None, "events_t": 297, "n_t": 1532, "events_c": 332, "n_c": 1533,
          "measure": "RR"}
    x = {"label": "HEART-FID [11]", "in_our_pool": False, "route": "UNVERIFIED", "g1_countable": False,
         "comparator_row": cr}
    from collections import Counter
    routes, pairs = Counter({"UNVERIFIED": 1}), []
    assert gt.acquired_merge("iv-iron-hfref-hosp", [x], routes, pairs, "39727669") == ["HEART-FID [11]"]
    assert x["route"] == "PRIMARY" and gt.is_matched(x) and x["agreement_with_comparator_row"] == "AGREE"
    assert len(pairs) == 1 and routes == Counter({"PRIMARY": 1})
    named = dict(x, route="UNVERIFIED", scope_difference={"kind": "X"})
    assert gt.acquired_merge("iv-iron-hfref-hosp", [named], None, None, "39727669") == []
