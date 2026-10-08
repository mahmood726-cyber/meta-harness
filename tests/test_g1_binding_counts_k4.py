"""K4 (regulatory label / review TABLE, deterministic): the two FDA tables that print the sglt2-pp HHF arm counts, as
FIXED excerpts of the held US-government documents (8 Oct; D12 approved)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_binding_counts as bc  # noqa: E402

SPEC = {"name": "Hospitalization for heart failure", "keywords": ["hospitalization for heart failure",
                                                                   "heart failure hospitalization"]}
DECLARE = ("1 INDICATIONS AND USAGE FARXIGA (dapagliflozin) is a sodium-glucose cotransporter 2 inhibitor\n"
           "Table 14: Treatment Effects for the Primary Endpoints* and Their Components* in the \nDECLARE Study \n"
           "Patients with events n (%) \nEfficacy Variable \n(time to first occurrence) \nFARXIGA 10 mg \nN=8582 \nPlacebo \n"
           "N=8578 \nHazard ratio \n(95% CI) \nPrimary Endpoints \nComposite of Hospitalization for \n"
           "Heart Failure, CV Death† 417 (4.9) 496 (5.8) 0.83 (0.73, 0.95) \n"
           "Components of the composite endpoints‡ \nHospitalization for Heart Failure 212 (2.5) 286 (3.3) 0.73 (0.61, 0.88) \n"
           "CV Death 245 (2.9) 249 (2.9) 0.98 (0.82, 1.17) \n")
CANVAS = ("Table 30:  Time to First Hospitalization for Heart Failure in The CANVAS Program \n(ITT Analysis Set)\n"
          "Placebo Canagliflozin\nn/N (%) Rate* n/N (%) Rate* HR (95% CI) p-\nvalue**\nPooled DIA3008 & \nDIA4003\n"
          "120/4347 (2.8) 8.68 123/5795 (2.1) 5.50 0.67 (0.52, 0.87) 0.0021\n"
          "DIA3008 53/1442 (3.7) 6.71 85/2888 (2.9) 5.19 0.77 (0.55, 1.08)\n"
          "DIA4003 67/2905 (2.3) 11.29 38/2907 (1.3) 6.34 0.56 (0.38, 0.83)\n")
T = {"intervention_agents": {"dapagliflozin": ["dapagliflozin"], "canagliflozin": ["canagliflozin"]},
     "intervention_terms": ["dapagliflozin", "canagliflozin", "SGLT2"], "comparator_terms": ["placebo"]}


def test_k4_n_in_the_header_and_n_pct_rows_brand_named_by_the_document_itself():
    r, why = bc.regulatory_table(DECLARE, SPEC, T, names=["DECLARE"], codes=[])
    assert why is None and r["values"] == {"events_t": 212, "n_t": 8582, "events_c": 286, "n_c": 8578}


def test_k4_n_over_n_rows_placebo_first_and_a_program_row_naming_every_study():
    r, why = bc.regulatory_table(CANVAS, SPEC, T, names=["CANVAS"], codes=[["DIA3008", "CR016627"], ["DIA4003", "CR102647"]])
    assert why is None and r["values"] == {"events_t": 123, "n_t": 5795, "events_c": 120, "n_c": 4347}
    r, why = bc.regulatory_table(CANVAS, SPEC, T, names=["CANVAS"], codes=[["DIA3008", "CR016627"]])
    assert r["values"] == {"events_t": 85, "n_t": 2888, "events_c": 53, "n_c": 1442}


def test_k4_refuses_a_table_of_another_trial_and_an_unreadable_orientation():
    r, why = bc.regulatory_table(DECLARE, SPEC, T, names=["CREDENCE"], codes=[])
    assert r is None
    no_brand = DECLARE.replace("FARXIGA (dapagliflozin)", "this product")
    r, why = bc.regulatory_table(no_brand, SPEC, T, names=["DECLARE"], codes=[])
    assert r is None and "ORIENT" in why
