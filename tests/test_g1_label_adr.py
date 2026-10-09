"""R9-4: the FDA label adverse-reaction adapter (scripts/g1_label_adr.py). Synthetic label text in the shape of the
KERENDIA 2021 label (Table 3, FIDELIO-DKD), page-footer noise included; never a live corpus."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_label_adr as L  # noqa: E402

CFG = {"intervention_agents": {"finerenone": ["finerenone"]}, "comparator_terms": ["placebo"],
       "harm_outcomes": [{"name": "Hyperkalemia", "keywords": ["hyperkalemia", "hyperkalaemia"]},
                         {"name": "Hyperkalemia-related treatment discontinuation",
                          "keywords": ["hyperkalemia leading to discontinuation"]}]}
NAMES = {"FIDELIO-DKD": "33264825", "FIGARO-DKD": "34449181"}
HEAD = "KERENDIA (finerenone) tablets, for oral use\n"
TABLE = ("Table 3: Adverse reactions reported in ≥ 1% of patients on Kerendia and more frequently than placebo \n"
         "in the phase 3 study FIDELIO-DKD \nReference ID: 4823818 \n3 \nThis label may not be the latest approved by FDA.\n"
         " \n \n   \n \nAdverse reactions \nKerendia \nN = 2827 \nn (%) \nPlacebo \nN = 2831 \nn (%) \n"
         "Hyperkalemia 516 (18.3) 255 (9.0) \nHypotension 135 (4.8) 96 (3.4) \nHyponatremia 40 (1.4) 19 (0.7) \n")


def prop(text, names=NAMES):
    return L.propose("fin", CFG, "https://www.accessdata.fda.gov/x/lbl.pdf", text, names)


def test_the_fidelio_table_row_is_proposed_as_its_own_adr_endpoint():
    p, r = prop(HEAD + TABLE)
    assert len(p) == 1 and p[0]["values"] == {"events_t": 516, "n_t": 2827, "events_c": 255, "n_c": 2831}
    assert p[0]["trial"] == "FIDELIO-DKD" and p[0]["pmid"] == "33264825"
    assert p[0]["endpoint"] == "Hyperkalemia (FDA label adverse reaction, FIDELIO-DKD safety population)"
    # an outcome with no row in the table is refused by name, never guessed
    assert any(x.get("harm") == "Hyperkalemia-related treatment discontinuation" and x["why"] == "ROWS_MATCHING:0"
               for x in r)


def test_PLANT_a_pooled_table_is_no_single_trials_tuple():
    t = TABLE.replace("in the phase 3 study FIDELIO-DKD", "(Pooled analysis of FIDELIO-DKD and FIGARO-DKD)")
    p, r = prop(HEAD + t)
    assert p == [] and r[0]["why"] == "NOT_ONE_TRIAL:POOLED"
    t2 = TABLE.replace("in the phase 3 study FIDELIO-DKD", "in FIDELIO-DKD and FIGARO-DKD")
    p, r = prop(HEAD + t2)
    assert p == [] and r[0]["why"].startswith("NOT_ONE_TRIAL")


def test_PLANT_a_trial_not_among_the_topics_pivotal_trials_names_nothing():
    p, r = prop(HEAD + TABLE, names={"FIGARO-DKD": "34449181"})
    assert p == [] and r[0]["why"] == "NOT_ONE_TRIAL:[]"


def test_PLANT_a_percentage_that_is_not_n_over_N_refuses_the_row():
    p, r = prop(HEAD + TABLE.replace("516 (18.3)", "516 (19.3)"))
    assert p == [] and any(x.get("why") == "PERCENT_NOT_N_OVER_N" for x in r)


def test_PLANT_the_arm_order_comes_from_the_header():
    t = TABLE.replace("Kerendia \nN = 2827 \nn (%) \nPlacebo \nN = 2831", "Placebo \nN = 2831 \nn (%) \nKerendia \nN = 2827") \
             .replace("516 (18.3) 255 (9.0)", "255 (9.0) 516 (18.3)")
    p, _ = prop(HEAD + t)
    assert p[0]["values"] == {"events_t": 516, "n_t": 2827, "events_c": 255, "n_c": 2831}


def test_PLANT_an_arm_named_by_neither_the_labels_brand_nor_the_agent_is_refused():
    p, r = prop("ZYXOR (otherdrug) tablets\n" + TABLE)
    assert p == [] and r[0]["why"].startswith("ARMS_NOT_ORIENTED")


def test_PLANT_a_row_label_that_only_contains_the_keyword_is_not_the_outcome():
    p, r = prop(HEAD + TABLE.replace("Hyperkalemia 516", "Hyperkalemia leading to hospitalization 516"))
    assert all(x["harm_outcome"] != "Hyperkalemia" for x in p)
