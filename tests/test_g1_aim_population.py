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
