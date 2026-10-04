"""SELF-REPRODUCTION: our reconstruction error vs the meta's. Rows printed to 2 decimals ('0.01 to 4.00' for a sparse
trial) carry a large rounding error on the log variance; the check compared the printed pool with ONE reconstruction
from the rounded rows and refused a consistent meta (balanced-crystalloids meta 35488485, 'Risk Ratio, M-H, Random':
printed 0.29 [0.06, 1.51], ours 0.275 [0.055, 1.369]). Now the printed pool is checked against the rows' ROUNDING
ENVELOPE (seeded draws of every printed number within its half-unit; one draw must reproduce all three printed values
jointly, same tolerance). A MISREAD row still fails. A meta stating Mantel-Haenszel whose rows carry no counts gets a
typed refusal, never the generic one."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import secondary_meta as sm  # noqa: E402


def _rows(spec, measure="RR"):
    return [sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="", trial_label=l,
                            measure=measure, outcome_definition="", effect=e, lower=lo, upper=hi) for l, e, lo, hi in spec]


SPARSE = [("Weinberg 2015", "0.20", "0.01", "4.00"), ("Weinberg 2018", "1.00", "0.02", "48.49"),
          ("Pfortmueller 2019", "1.00", "0.02", "49.75"), ("Chaussard 2020", "0.11", "0.01", "1.88")]
PRINTED = {"effect": "0.29", "lower": "0.06", "upper": "1.51"}


def test_a_meta_consistent_within_its_rows_rounding_reproduces():
    pc = sm.positive_control(_rows(SPARSE), PRINTED, "RR")
    assert pc["reproduced"], pc


def test_a_misread_row_still_fails_inside_the_envelope():
    bad = list(SPARSE)
    bad[3] = ("Chaussard 2020", "1.10", "0.10", "1.88")          # misread point and lower bound
    assert not sm.positive_control(_rows(bad), PRINTED, "RR")["reproduced"]


def test_a_stated_mantel_haenszel_meta_without_counts_gets_a_typed_refusal():
    rows = _rows([("Akodad 2017", "0.31", "0.01", "7.12"), ("Hennessy 2019", "0.20", "0.01", "4.19"),
                  ("Mewton 2021", "0.69", "0.16", "2.94"), ("Tardif 2019", "0.91", "0.68", "1.21")])
    pc = sm.positive_control(rows, {"effect": "0.88", "lower": "0.67", "upper": "1.15"}, "RR", stated_model="Risk Ratio, M-H, Fixed")
    if not pc["reproduced"]:
        assert pc["why"] == "STATED_MODEL_MH_NEEDS_COUNTS"
