"""PLANTS for the own-tuple table binder (scripts/g1_binding_bind.table_own_tuples). The positives are the real shapes of
COLCHICINE-PCI (Shah 2020, PMC OA Table 2) and Akrami 2021 (BMC, Table 2 with N only in Table 1's header)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_binding_bind as bb  # noqa: E402

TERMS = ["MACE", "major adverse cardiovascular", "primary outcome"]
IV, CP = ["colchicine"], ["placebo"]
SHAH = ("TABLE Table 3.: Outcomes in patients undergoing PCI randomized to colchicine or placebo\n"
        " | Colchicine (n=206) | Placebo (n=194) | p-value\n"
        "Access site, % |  |  | 0.96\n"
        "30-day major adverse cardiovascular events | 24 (11.7) | 25 (12.9) | 0.82\n")
AKRAMI = ("TABLE Table 1: Baseline characteristics of the patients\n"
          "Characteristics | Colchicine (n = 120) | Placebo (n = 129) | P value\n"
          "Age, year | 56.9 | 56.9 | 0.99\n"
          "TABLE Table 2: Major clinical end points (intention-to-treat population)\n"
          "Endpoint | Colchicine | Placebo | Hazard ratio (95%CI) | P value\n"
          "Total MACE | 8 (6.7) | 28 (21.7) | 3.52 (1.60–7.74) | 0.001\n")


def own(text, terms=TERMS):
    return bb.table_own_tuples(text, terms, IV, CP)


def test_header_n_row_binds():
    c = own(SHAH)
    assert [x["tuple"] for x in c] == [(24, 206, 25, 194)] and c[0]["n_from"] == []


def test_n_borrowed_from_the_same_arm_label_in_another_table():
    c = own(AKRAMI)
    assert [x["tuple"] for x in c] == [(8, 120, 28, 129)]
    assert c[0]["n_from"] == ["Characteristics | Colchicine (n = 120) | Placebo (n = 129) | P value"]


def test_percent_inconsistent_with_n_refused():
    assert own(SHAH.replace("24 (11.7)", "24 (14.7)")) == []


def test_baseline_table_row_refused():
    t = SHAH.replace("Outcomes in patients undergoing PCI", "Baseline characteristics of subjects")
    assert own(t) == []


def test_generic_only_row_label_refused():
    t = SHAH.replace("30-day major adverse cardiovascular events", "Primary outcome")
    assert own(t) == []


def test_conflicting_borrowed_n_refused():
    t = AKRAMI + ("TABLE Table 4: Follow-up\nItem | Colchicine (n = 99) | Placebo (n = 129)\nVisits | 1 | 1\n")
    assert own(t) == []


def test_no_comparator_column_refused():
    t = SHAH.replace("Placebo (n=194)", "Overall (n=194)")
    assert own(t) == []


# ---- P1: the trial-defined primary in prose (LoDoCo 2013, PMID 23265346 abstract) ---------------------------------------
LODOCO = ("The primary outcome was the composite incidence of acute coronary syndrome, out-of-hospital cardiac arrest, or "
          "noncardioembolic ischemic stroke. The primary outcome occurred in 15 of 282 patients (5.3%) who received "
          "colchicine and 40 of 250 patients (16.0%) assigned no colchicine (hazard ratio: 0.33; 95% CI 0.18 to 0.59).")
KW = ["coronary", "primary outcome", "MACE"]


def test_p1_binds_the_defined_primary_with_arm_labels():
    got = bb.prose_trial_defined(LODOCO, KW, ["colchicine"], ["placebo"])
    assert [g[2] for g in got] == [(15, 282, 40, 250)]


def test_p1_needs_a_definition_naming_a_non_generic_term():
    t = LODOCO.replace("acute coronary syndrome, out-of-hospital cardiac arrest, or noncardioembolic ischemic stroke",
                       "several events")
    assert bb.prose_trial_defined(t, KW, ["colchicine"], ["placebo"]) == []


def test_p1_refuses_an_on_treatment_analysis():
    t = LODOCO.replace("The primary outcome occurred", "In a prespecified on-treatment analysis the primary outcome occurred")
    assert bb.prose_trial_defined(t, KW, ["colchicine"], ["placebo"]) == []


def test_p1_refuses_inconsistent_percent_and_swapped_labels():
    assert bb.prose_trial_defined(LODOCO.replace("(5.3%)", "(9.3%)"), KW, ["colchicine"], ["placebo"]) == []
    t = LODOCO.replace("who received colchicine and", "assigned no colchicine and").replace(
        "(16.0%) assigned no colchicine", "(16.0%) who received colchicine")
    assert bb.prose_trial_defined(t, KW, ["colchicine"], ["placebo"]) == []
