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
    # PLANT: without the prevention flag, the population is sought in title/conditions only -> X2.
    d, rule, reason, span = S.screen_record(rec, _INC_NO_FLAG, [])
    assert d == "exclude" and rule == "X2", (d, rule)


def test_prevention_flag_includes_via_abstract_population():
    rec = _rec("Colchicine to Prevent Postoperative Arrhythmias",
               "In adults undergoing cardiac surgery, colchicine vs placebo reduced POAF.")
    d, rule, reason, span = S.screen_record(rec, _INC_PREVENTION, [])
    assert d == "include", (d, rule, reason)
    assert "cardiac surgery" in span.lower()  # span quotes the real abstract bytes


def test_intervention_anchor_still_blocks_incidental():
    # prevention override must NOT let in a trial that is not actually OF the intervention: the
    # intervention-in-title anchor still applies (drug not in title -> X3).
    rec = _rec("A Trial of Beta-Blockers After Cardiac Surgery",
               "Colchicine was mentioned as prior therapy; cardiac surgery patients enrolled.")
    d, rule, reason, span = S.screen_record(rec, _INC_PREVENTION, [])
    assert d == "exclude" and rule == "X3", (d, rule)


def test_colchicine_postop_config_models_enrolled_population():
    # the live topic must now model the ENROLLED population, not the prevented outcome
    inc = json.load(open(os.path.join(_ROOT, "topics", "colchicine-postop-af.json"), encoding="utf-8"))["include"]
    assert inc.get("prevention") is True
    assert "atrial fibrillation" not in inc["population_any"]
    assert any("cardiac surgery" in p or "CABG" in p or "bypass" in p for p in inc["population_any"])


def test_condition_as_outcome_real_trials():
    # Held PubMed records: Hickson prevents AAD; 22370839 treats existing AAD.
    from pathlib import Path
    root = Path(_ROOT)
    config = json.loads((root / "topics/probiotics-aad-prevention.json").read_text(encoding="utf-8"))
    records = json.loads((root / "cache/probiotics-aad-prevention/records.json").read_text(encoding="utf-8"))
    ids = {"111546", "17604300", "17900321", "19727002", "24291194", "22370839"}
    selected = [r for r in records["records"] if r["id"] in ids]
    assert {r["id"] for r in selected} == ids
    assert "prevention" not in config["include"]
    decisions = {d["id"]: d for d in S.run(selected, config)["decisions"]}
    for pid in sorted(ids - {"22370839"}):
        assert decisions[pid]["decision"] == "include", decisions[pid]
    assert decisions["22370839"]["decision"] == "exclude"
    assert decisions["22370839"]["rule_id"] == "X2"
    assert "diarrhea treatment" in decisions["22370839"]["reason"]
    assert "prevention" not in config["include"]


def test_prevention_derivation_is_event_specific_and_topic_independent():
    import copy
    cfg = {"include": {"population_any": ["infection"]},
           "primary_outcome": {"name": "At least one infection",
                               "keywords": ["at least one infection"], "estimand": "RR"}}
    original = copy.deepcopy(cfg)
    assert S.effective_include(cfg)["prevention"] is True
    assert cfg == original
    cfg["include"]["prevention"] = False
    assert S.effective_include(cfg)["prevention"] is True
    cfg["primary_outcome"]["name"] = "Mortality"
    assert not S.effective_include(cfg)["prevention"]
    cfg["primary_outcome"].update(name="Infection", estimand="MD")
    assert not S.effective_include(cfg)["prevention"]


def test_keyword_overlap_does_not_turn_treatment_into_prevention():
    cfg = {"include": {"population_any": ["appendicitis"]},
           "primary_outcome": {"name": "Treatment failure or complication at 1 year",
                               "keywords": ["appendicitis"], "estimand": "RR"}}
    assert not S.effective_include(cfg).get("prevention")
    cfg["primary_outcome"].update(name="Mortality", keywords=["appendicitis", "mortality"])
    assert not S.effective_include(cfg).get("prevention")
    cfg["include"]["population_any"] = ["infect*"]
    cfg["primary_outcome"].update(name="Infection mortality", keywords=["infection"])
    assert not S.effective_include(cfg).get("prevention")


def test_dual_screen_uses_derived_prevention():
    cfg = {"include": {"population_any": ["infection"]},
           "primary_outcome": {"name": "Infection", "keywords": ["infection"], "estimand": "RR"}}
    rec = _rec("A randomized prevention trial", "Treatment reduced infection versus placebo.")
    dual = S.run_dual([rec], cfg)
    assert dual["n"] == dual["agree"] == 1
    assert dual["disagree"] == 0


def test_prevention_widens_the_population_signal_not_the_exclusions():
    # PLANT (probiotics, derived prevention): exclusion terms matched over the ABSTRACT excluded real trials on incidental
    # words. They stay on title/conditions; a title that IS a subgroup report still excludes.
    inc = {"prevention": True, "population_any": ["antibiotic-associated diarr*"], "intervention_any": ["probiotic"],
           "comparator_any": ["placebo"], "population_none": ["model", "subgroup analysis", "treatment of AAD"]}
    rec = _rec("Probiotic for the prevention of antibiotic-associated diarrhoea: a randomized trial",
               "Patients were randomized to probiotic or placebo. Using a multivariate model to adjust for age, "
               "the adjusted risk of antibiotic-associated diarrhoea fell. Subgroup analysis of subjects with AAD "
               "showed shorter duration. There is interest in probiotics for the treatment of AAD.")
    d, rule, reason, span = S.screen_record(rec, inc, [])
    assert d == "include", (d, rule, reason)
    sub = _rec("A subgroup analysis of a probiotic trial for antibiotic-associated diarrhoea", rec["abstract"])
    d, rule, reason, span = S.screen_record(sub, inc, [])
    assert d == "exclude" and rule == "X2" and "subgroup analysis" in reason
