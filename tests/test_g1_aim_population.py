"""G1 tranexamic-acid-pph: WOMAN-2 (PMID 39461792) is a PREVENTION trial ('We examined whether giving tranexamic acid
shortly after birth can prevent postpartum haemorrhage in women with moderate or severe anaemia'); the registered
protocol is treatment of PPH (population_none: prevent / prevention / prophylaxis). The audit had only a recorded
reader's non-verbatim quote (INSUFFICIENT_RECORD:POPULATION_OUTSIDE_PROTOCOL_NO_SPAN). A first-person AIM sentence states
what THIS study did even when a structured abstract files it under BACKGROUND; a population term NEGATED where it occurs
('adults without diabetes', 'with or without type 2 diabetes') is never an excluding span -- on the first regeneration
SELECT (semaglutide-obesity-mace 37385278) was wrongly named 'type 2 diabetes' that way; caught by the radius check."""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import k_gap_exclusion_audit as au  # noqa: E402


def _cfg(slug):
    return json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))


def _rec(title, abstract):
    return {"id": "1", "id_type": "pmid", "title": title, "abstract": abstract, "pubtypes": ["Randomized Controlled Trial"]}


def test_a_background_aim_sentence_states_this_studys_population():
    r = _rec("The effect of tranexamic acid on postpartum bleeding in women with anaemia: a randomised trial.",
             "BACKGROUND: Tranexamic acid reduces bleeding deaths in women with postpartum haemorrhage. We examined whether "
             "giving tranexamic acid shortly after birth can prevent postpartum haemorrhage in women with anaemia. METHODS: "
             "We randomly assigned women who had given birth vaginally to tranexamic acid or matching placebo.")
    cls, sub, d = au.classify(r, _cfg("tranexamic-acid-pph"))
    assert (cls, sub.split(":")[0]) == ("TRUE_SCOPE_DIFFERENCE", "PROTOCOL_EXCLUDES_POPULATION_STATED_FOR_THIS_STUDY")
    assert d["span"]["text"].startswith("We examined whether")


def test_a_background_statement_about_the_field_is_never_a_span():
    assert not au.AIM_THIS_STUDY.search("Tranexamic acid, given within 3 h of birth, reduces bleeding deaths.")


def test_a_negated_population_term_is_never_an_excluding_span():
    for s in ("This randomised trial enrolled adults with a BMI of at least 30 without diabetes.",
              "Adults with overweight or obesity, with or without type 2 diabetes, were randomly assigned to semaglutide.",
              "Patients with no history of diabetes were randomly assigned.", "free of type 2 diabetes were randomized"):
        m = au._terms_rx(["type 2 diabetes", "diabetes"]).search(s)
        assert au._negated(s, m.group(0)), s
    assert not au._negated("Adults with type 2 diabetes were randomly assigned.", "type 2 diabetes")


def test_the_committed_audit_names_woman2_and_never_select():
    rows = {(r["slug"], r["pmid"]): r for r in json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.json"),
                                                               encoding="utf-8"))["rows"]}
    w = rows[("tranexamic-acid-pph", "39461792")]
    assert w["class"] == "TRUE_SCOPE_DIFFERENCE" and "prevent postpartum haemorrhage" in w["span"]["text"]
    s = rows[("semaglutide-obesity-mace", "37385278")]
    assert not s["subclass"].startswith("PROTOCOL_EXCLUDES_POPULATION_STATED_FOR_THIS_STUDY")


def test_pre_fix_woman2_was_an_open_gap_without_a_span():
    base = json.loads(subprocess.check_output(["git", "show", "17fb03ab:outputs/k_gap/g1/tranexamic-acid-pph.json"], cwd=ROOT))
    assert "WOMAN-210" in base["open_gaps"]


# --- plants from cross-vendor review NR-C25 (Codex; artefact F:/mh-nr101-codex/c25-g1-aim-negation/last_message.txt):
# every one of these named an IN-SCOPE trial out of the denominator before the fix
SEMA = ["type 2 diabetes", "diabetes", "heart failure"]
EMPA = ["type 2 diabetes", "myocardial infarction"]


def _named(text, none, anyp=("obesity",)):
    return au.stated_excluded_population({"abstract": text}, {"population_none": none, "population_any": list(anyp)})


def test_c25_negation_exclusion_and_option_never_name():
    for s in ["Adults with obesity and cardiovascular disease, excluding those with type 2 diabetes, were randomized to semaglutide or placebo.",
              "We assessed semaglutide in adults with obesity and cardiovascular disease other than those with type 2 diabetes.",
              "Adults with obesity and cardiovascular disease were randomized unless they had type 2 diabetes.",
              "We evaluated semaglutide in adults with obesity and cardiovascular disease who did not have type 2 diabetes.",
              "We evaluated semaglutide in patients without prior type 2 diabetes who had obesity and cardiovascular disease.",
              "Adults with obesity and cardiovascular disease, excluding anyone with a documented or clinically confirmed previous diagnosis of type 2 diabetes, were randomly assigned.",
              "We evaluated semaglutide in adults with obesity and cardiovascular disease; type 2 diabetes was an exclusion criterion."]:
        assert _named(s, SEMA) is None, s


def test_c25_subgroups_outcomes_and_secondary_aims_never_name():
    assert _named("Patients with HFpEF, including a subgroup with type 2 diabetes, were randomized to empagliflozin or placebo.",
                  EMPA, ("HFpEF",)) is None
    assert _named("We also examined whether empagliflozin prevents myocardial infarction in patients with HFpEF.", EMPA,
                  ("HFpEF",)) is None
    assert _named("We examined whether semaglutide reduces hospitalisation for heart failure in adults with obesity and "
                  "cardiovascular disease without diabetes.", SEMA) is None


def test_c25_prevention_binds_to_the_protocols_condition_not_another_object():
    txa = (["prevent", "prevention", "prophylactic", "prophylaxis"], ("postpartum haemorrhage", "postpartum hemorrhage"))
    assert _named("We examined whether tranexamic acid could prevent death due to bleeding in women with established "
                  "postpartum haemorrhage.", *txa) is None
    assert _named("BACKGROUND: We examined whether giving tranexamic acid shortly after birth can prevent postpartum "
                  "haemorrhage in women with anaemia.", *txa) is not None


def test_c25_other_studies_aims_and_contradicted_abstracts_never_name():
    txa = (["prevent", "prevention"], ("postpartum haemorrhage",))
    assert _named("BACKGROUND: The authors of an earlier trial reported: We examined whether tranexamic acid could prevent "
                  "postpartum haemorrhage. METHODS: Women with established postpartum haemorrhage received treatment.", *txa) is None
    assert _named("Previous trials examined cardiovascular outcomes in adults with type 2 diabetes who were randomized to "
                  "semaglutide or placebo.", SEMA) is None
    assert _named("BACKGROUND: We enrolled patients with type 2 diabetes. METHODS: All participants had obesity and established "
                  "cardiovascular disease and none had diabetes; they were randomized to semaglutide or placebo.", SEMA) is None
