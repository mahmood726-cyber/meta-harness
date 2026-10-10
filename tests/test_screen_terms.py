"""12-01 class fix + review 27-B: typed development codes, population synonyms, and the ROLE-AWARE placebo comparator.
Real held record text where one exists (Legro 17287476 metformin; ARTS-DN Japan NCT01968668)."""
from __future__ import annotations

from harness import screen_terms as st

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
