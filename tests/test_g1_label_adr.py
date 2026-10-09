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
    assert p == [] and r[0]["why"].startswith("NOT_ONE_TRIAL:[]")


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


# ---------------------------------------------------------------------------------------- codex r9-4-label-r1
NAMES2 = {"ALPHA-ONE": "1", "BETA-TWO": "2"}


def _tab(trial, n, a, b, sep="\n \n"):
    return (f"Table 3: Adverse reactions in the phase 3 study {trial}{sep}Adverse reactions \nKerendia \nN = {n} \nn (%) \n"
            f"Placebo \nN = {n} \nn (%) \n")


def test_PLANT_r1_1_a_row_is_never_read_from_the_next_table():
    t = HEAD + _tab("ALPHA-ONE", 1000, 0, 0) + "Hypotension 5 (0.5) 4 (0.4) \n" + \
        _tab("BETA-TWO", 1001, 0, 0).replace("Table 3", "Table 4") + "Hyperkalemia 10 (1.0) 20 (2.0) \n"
    p, _r = prop(t, names=NAMES2)
    assert [(x["trial"], x["values"]["n_t"]) for x in p] == [("BETA-TWO", 1001)]


def test_PLANT_r1_2_a_caption_naming_another_trial_refuses_the_table():
    t = HEAD + _tab("ALPHA-ONE and GAMMA-THREE", 100, 0, 0) + "Hyperkalemia 10 (10.0) 20 (20.0) \n"
    p, r = prop(t, names=NAMES2)
    assert p == [] and r[0]["why"].startswith("NOT_ONE_TRIAL")


def test_PLANT_r1_3_a_table_stating_a_randomised_population_is_not_the_safety_contract():
    t = HEAD + _tab("ALPHA-ONE (all randomized patients)", 100, 0, 0) + "Hyperkalemia 10 (10.0) 20 (20.0) \n"
    p, r = prop(t, names=NAMES2)
    assert p == [] and r[0]["why"] == "POPULATION_NOT_SAFETY"


def test_PLANT_r1_4_reader_gate_integer_percentages_in_n_pct_cells_are_not_counts():
    win = "Kerendia N = 1000 n (%) Placebo N = 1000 n (%) Hyperkalemia 100 (10) 200 (20)"
    ans = {"state": "FOUND", "quote": win, "events_t": 10, "n_t": 1000, "events_c": 20, "n_c": 1000}
    assert L.reader_gate(ans, win).startswith("NUMBER_NOT_IN_QUOTE")
    ok = dict(ans, events_t=100, events_c=200)
    assert L.reader_gate(ok, win) == "GATED"


def test_PLANT_r1_5_a_caption_without_a_blank_line_still_finds_its_header():
    t = HEAD + _tab("ALPHA-ONE", 100, 0, 0, sep="\n") + "Hyperkalemia 10 (10.0) 20 (20.0) \n"
    p, _r = prop(t, names=NAMES2)
    assert [x["values"] for x in p] == [{"events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100}]


def test_PLANT_r1_6_a_zero_denominator_is_a_recorded_refusal():
    t = HEAD + _tab("ALPHA-ONE", 0, 0, 0) + "Hyperkalemia 10 (10.0) 20 (20.0) \n"
    p, r = prop(t, names=NAMES2)
    assert p == [] and r[0]["why"] == "INVALID_DENOMINATOR"


def test_PLANT_r1_7_a_failed_discovery_is_recorded_never_read_as_no_applications(monkeypatch):
    from harness import http
    import g1_regulatory_source as rs

    def boom(*a, **k):
        raise TimeoutError("read timed out")
    monkeypatch.setattr(http, "get_json", boom)
    assert rs.fda_review_urls("finerenone") == []
    assert len(rs.DISCOVERY_ERRORS.get("finerenone") or []) == 2
