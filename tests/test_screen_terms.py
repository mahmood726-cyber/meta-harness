"""12-01 class fix + review 27-B: typed development codes, population synonyms, and the ROLE-AWARE placebo comparator.
Real held record text where one exists (Legro 17287476 metformin; ARTS-DN Japan NCT01968668)."""
from __future__ import annotations

import os

from harness import screen_terms as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEGRO = ("We randomly assigned 626 infertile women with the polycystic ovary syndrome to receive clomiphene citrate plus "
         "placebo, extended-release metformin plus placebo, or a combination of metformin and clomiphene for up to 6 months.")
MET_INC = {"intervention_any": ["metformin"], "comparator_any": ["placebo group", "placebo-controlled", "placebo alone"]}


def test_PLANT_development_code_is_the_drug():
    inc = st.expand({"intervention_any": ["finerenone"]})
    assert "BAY94-8862" in inc["intervention_any"] and "BAY 94-8862" in inc["intervention_any"]
    # only for an INN the protocol already names: a code never widens another topic
    assert "BAY94-8862" not in st.expand({"intervention_any": ["melatonin"]}).get("intervention_any", [])


def test_PLANT_population_registry_label_is_the_concept():
    inc = st.expand({"population_any": ["type 2 diabetes"]})
    assert "diabetes mellitus, type 2" in inc["population_any_extra"]
    assert "population_any_extra" not in st.expand({"population_any": ["insomnia in children"], "x": 1}) or \
        "diabetes mellitus, type 2" not in st.expand({"population_any": ["insomnia"]}).get("population_any_extra", [])


def test_PLANT_legro_placebo_masks_metformin_on_a_clomiphene_background():
    got = st.placebo_masks_intervention({"title": "Clomiphene, metformin, or both for infertility in the polycystic "
                                                  "ovary syndrome."}, MET_INC, LEGRO)
    assert got and "clomiphene" in got["term"] and "plus placebo" in got["span"]


def test_PLANT_a_placebo_masking_another_agent_stays_out():
    # metformin is in BOTH arms; the placebo masks clomiphene: not a metformin-v-placebo contrast
    text = "Women were randomised to metformin plus placebo or metformin plus clomiphene."
    assert st.placebo_masks_intervention({}, MET_INC, text) is None
    # unequal background: clomiphene + placebo against metformin ALONE (no combination arm)
    text = "Women were randomised to clomiphene citrate plus placebo or metformin alone."
    assert st.placebo_masks_intervention({}, MET_INC, text) is None


def test_role_aware_rule_applies_only_when_the_protocol_comparator_is_placebo():
    assert st.placebo_masks_intervention({}, {"intervention_any": ["metformin"], "comparator_any": ["clomiphene"]},
                                         LEGRO) is None


def test_explicit_placebo_for_the_intervention():
    got = st.placebo_masks_intervention({"interventions": ["Potassium Chloride + Placebo for Empagliflozin"]},
                                        {"intervention_any": ["empagliflozin"], "comparator_any": ["placebo group"]}, "")
    assert got and "masks the intervention" in got["term"]


# ---------------------------------------------------------------- codex pr65-cap-r1 (each failed on 3560d2a6d)
def test_PLANT_explicit_placebo_needs_the_same_background():
    from harness.screen_terms import placebo_masks_intervention as pm
    inc = {"intervention_any": ["metformin"], "comparator_any": ["matching placebo"]}
    assert pm({"interventions": ["clomiphene plus metformin", "letrozole plus placebo for metformin"]}, inc, "") is None
    # the same background on both arms still masks
    assert pm({"interventions": ["clomiphene plus metformin", "clomiphene plus placebo for metformin"]}, inc, "") is not None


def test_PLANT_a_shared_salt_word_is_not_a_shared_background():
    from harness.screen_terms import placebo_masks_intervention as pm
    inc = {"intervention_any": ["metformin"], "comparator_any": ["matching placebo"]}
    assert pm({"interventions": ["clomiphene citrate plus placebo", "tamoxifen citrate plus metformin"]}, inc, "") is None
    assert pm({"interventions": ["clomiphene citrate plus placebo", "clomiphene citrate plus metformin"]}, inc, "") is not None


def test_PLANT_a_compound_population_is_never_split_by_a_synonym():
    from harness.screen_terms import expand
    extra = expand({"population_any": ["type 2 diabetes with chronic kidney disease"]}).get("population_any_extra") or []
    assert "t2dm" not in extra
    assert "t2dm with chronic kidney disease" in extra                 # the conjunction survives
    assert "t2dm" in (expand({"population_any": ["type 2 diabetes"]}).get("population_any_extra") or [])


def test_PLANT_expand_reads_the_current_content_not_a_stale_cache():
    from harness.screen_terms import expand
    inc = {"intervention_any": ["finerenone"]}
    expand(inc)
    inc["intervention_any"] = ["dapagliflozin"]
    assert not any("BAY" in t for t in expand(inc)["intervention_any"])


def test_PLANT_sweep_diff_compares_whole_error_strings(capsys, tmp_path):
    import importlib.util
    s = importlib.util.spec_from_file_location("gss", os.path.join(ROOT, "scripts", "g1_screen_sweep.py"))
    gss = importlib.util.module_from_spec(s)
    s.loader.exec_module(gss)
    (tmp_path / "o.json").write_text('{"topic": {"__error__": "ValueError: missing population"}}', encoding="utf-8")
    (tmp_path / "n.json").write_text('{"topic": {"__error__": "ValueError: invalid comparator"}}', encoding="utf-8")
    gss.diff(str(tmp_path / "o.json"), str(tmp_path / "n.json"))
    out = capsys.readouterr().out
    assert out.startswith("1 changed") and "invalid comparator" in out and "missing population" in out


# ---------------------------------------------------------------- codex pr65-cap-r2 (each failed on 20105a0ce)
def test_PLANT_a_qualified_population_keeps_its_qualifier():
    from harness.screen_terms import expand
    extra = expand({"population_any": ["type 2 diabetes requiring insulin"]}).get("population_any_extra") or []
    assert "t2dm" not in extra and "t2dm requiring insulin" in extra


def test_PLANT_a_drug_combination_keeps_its_partner_in_the_code_alternative():
    from harness.screen_terms import expand
    ia = expand({"intervention_any": ["finerenone plus spironolactone"]})["intervention_any"]
    assert "BAY94-8862" not in ia and "BAY94-8862 plus spironolactone" in ia
    assert "BAY94-8862" in expand({"intervention_any": ["finerenone"]})["intervention_any"]     # a bare INN still expands


def test_PLANT_implicit_placebo_needs_the_whole_background_equal():
    from harness.screen_terms import placebo_masks_intervention as pm
    inc = {"intervention_any": ["metformin"], "comparator_any": ["matching placebo"]}
    assert pm({"arms": ["clomiphene plus placebo", "clomiphene plus metformin plus letrozole"]}, inc, "") is None
    assert pm({"arms": ["clomiphene plus placebo", "clomiphene plus metformin"]}, inc, "") is not None


def test_PLANT_a_double_dummy_arm_is_still_an_intervention_arm():
    from harness.screen_terms import placebo_masks_intervention as pm
    inc = {"intervention_any": ["metformin"], "comparator_any": ["matching placebo"]}
    assert pm({"arms": ["clomiphene plus metformin plus placebo for letrozole", "letrozole plus placebo for metformin"]},
              inc, "") is None
