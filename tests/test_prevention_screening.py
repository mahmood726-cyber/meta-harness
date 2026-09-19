"""PREVENTION_TRIAL_TITLE_OMITS_OUTCOME: a prevention trial names the ENROLLED population, not the
prevented outcome, so requiring the population/outcome term in the TITLE structurally fails. For a
topic flagged `prevention`, a positive population signal in structured fields or the abstract
overrides a negative title signal (the intervention-in-title anchor still blocks incidental
mentions). Verified live on colchicine-postop-af, whose population_any was the OUTCOME
('atrial fibrillation') and is corrected to the enrolled population (cardiac surgery/CABG),
recovering the source-verified Post-CABG RCT 42132185 (RR 0.37).
"""
import json
import os

import harness.screen as S

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rec(title, abstract, conditions=""):
    return {"id": "999", "id_type": "pmid", "title": title, "abstract": abstract,
            "conditions": conditions, "pubtypes": ["Randomized Controlled Trial"],
            "masking": "double"}


_INC_PREVENTION = {"prevention": True, "population_any": ["cardiac surgery", "CABG"],
                   "intervention_any": ["colchicine"], "intervention_in_title": True,
                   "comparator_any": ["placebo"]}
_INC_NO_FLAG = {"population_any": ["cardiac surgery", "CABG"],
                "intervention_any": ["colchicine"], "intervention_in_title": True,
                "comparator_any": ["placebo"]}


def test_PLANT_title_omits_population_excluded_without_flag():
    # A trial whose title names only the drug, with the enrolled population in the ABSTRACT only.
    rec = _rec("Colchicine to Prevent Postoperative Arrhythmias",
               "In adults undergoing cardiac surgery, colchicine vs placebo reduced POAF.")
    # Preserve the pre-fix plant: title omission alone used to produce X2.
    from test_week_regressions_audit import load_pin
    assert load_pin('base/harness/screen.py').screen_record(rec, _INC_NO_FLAG, [])[:2] == ('exclude', 'X2')
    # Without the prevention flag, abstract-only eligibility now requires adjudication.
    d, rule, reason, span = S.screen_record(rec, _INC_NO_FLAG, [])
    assert d == "review" and rule == "MANUAL_REVIEW", (d, rule)


def test_prevention_flag_includes_via_abstract_population():
    rec = _rec("Colchicine to Prevent Postoperative Arrhythmias",
               "In adults undergoing cardiac surgery, colchicine vs placebo reduced POAF.")
    d, rule, reason, span = S.screen_record(rec, _INC_PREVENTION, [])
    assert d == "include", (d, rule, reason)
    assert "cardiac surgery" in span.lower()  # span quotes the real abstract bytes


def test_intervention_anchor_still_blocks_incidental():
    # prevention override must NOT let in a trial that is not actually OF the intervention: the
    # intervention-in-title anchor still prevents automatic inclusion. An abstract-only
    # mention now requires adjudication rather than establishing an exclusion.
    rec = _rec("A Trial of Beta-Blockers After Cardiac Surgery",
               "Colchicine was mentioned as prior therapy; cardiac surgery patients enrolled.")
    d, rule, reason, span = S.screen_record(rec, _INC_PREVENTION, [])
    assert d == "review" and rule == "MANUAL_REVIEW", (d, rule)


def test_colchicine_postop_config_models_enrolled_population():
    # the live topic must now model the ENROLLED population, not the prevented outcome
    inc = json.load(open(os.path.join(_ROOT, "topics", "colchicine-postop-af.json"), encoding="utf-8"))["include"]
    assert inc.get("prevention") is True
    assert "atrial fibrillation" not in inc["population_any"]
    assert any("cardiac surgery" in p or "CABG" in p or "bypass" in p for p in inc["population_any"])
