"""Plants for the RoB 2 calibration statistics (scripts/rob2_calibrate.py) on cases whose answer is fixed."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_calibrate as rc  # noqa: E402

L, S, H = "LOW", "SOME_CONCERNS", "HIGH"


def test_perfect_agreement_is_one():
    k = rc.kappa([(L, L)] * 5 + [(H, H)] * 5 + [(S, S)] * 3)
    assert k["kappa"] == 1.0


def test_PLANT_textbook_two_category_kappa():
    # 20 LL, 5 LH, 10 HL, 15 HH: po 0.70, pe 0.25*... = 0.5*0.6 + 0.5*0.4 = 0.50 -> kappa 0.40
    pairs = [(L, L)] * 20 + [(L, H)] * 5 + [(H, L)] * 10 + [(H, H)] * 15
    k = rc.kappa(pairs)
    assert k["kappa"] == 0.4 and k["po"] == 0.7 and k["pe"] == 0.5
    assert k["ci"][0] < 0.4 < k["ci"][1]


def test_PLANT_one_category_only_is_undefined_not_zero_or_one():
    assert rc.kappa([(L, L)] * 10)["kappa"] is None


def test_linear_weighting_gives_partial_credit_for_adjacent_categories():
    pairs = [(L, S)] * 5 + [(S, S)] * 5 + [(H, H)] * 5 + [(L, L)] * 5
    assert rc.kappa(pairs, weighted=True)["kappa"] > rc.kappa(pairs)["kappa"]


def test_PLANT_every_published_column_spelling_maps():
    # labels as printed by the five calibration comparators (10 Oct)
    for col, d in [("Selective outcome reporting", "D5"), ("Sequence Generation", "D1"),
                   ("Blinding of outcome assessors for All outcomes", "D4"),
                   ("Blinding of participants and personnel for All outcomes", "D2"),
                   ("Incomplete outcome data for All outcomes", "D3"), ("D3", "D3"), ("Overall", "OVERALL")]:
        assert rc.domain_of(col) == d, col
    assert rc.domain_of("Other sources of bias") is None


def test_PLANT_rob1_d1_is_the_worse_of_sequence_and_concealment():
    cols = ["Random sequence generation (selection bias)", "Allocation concealment (selection bias)",
            "Blinding of participants and personnel (performance bias)", "Blinding of outcome assessment (detection bias)",
            "Incomplete outcome data (attrition bias)", "Selective reporting (reporting bias)", "Other bias"]
    row = {"cells": dict(zip(cols, ["low", "unclear", "low", "high", "low", "low", "high"]))}
    d = rc.reference_domains(row, cols)
    assert d == {"D1": S, "D2": L, "D4": H, "D3": L, "D5": L}            # 'Other bias' maps to nothing
    row["cells"]["Allocation concealment (selection bias)"] = "not shown"
    assert rc.reference_domains(row, cols)["D1"] is None                  # an unreadable part leaves the domain unknown
