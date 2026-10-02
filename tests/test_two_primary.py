"""PLANT for scripts/g1_two_primary.regulator_tuple: a regulator's table read by regex, each triple bound to its column.
The two traps: an in-text cross-reference ('see Table 4 and Figure 1') taken for the table, and a triple bound to the
wrong arm (RE-LY prints 150 mg FIRST and 110 mg second; the comparator column carries no ratio)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_two_primary as tp  # noqa: E402

LABEL = """The primary endpoint was stroke or systemic embolism (see Table 4 and Figure 1).
Table 4 First Occurrence of Stroke or Systemic Embolism in the RE-LY Study
DRUG
150 mg twice daily
DRUG
110 mg twice daily
Warfarin
Patients randomized 6076 6015 6022
Patients (%) with events 134 (2.2%) 183 (3%) 202 (3.4%)
Hazard ratio vs. warfarin (95% CI) 0.65 (0.52, 0.81) 0.90 (0.74,1.10)
Figure 1 Kaplan-Meier curve
"""


def test_the_table_is_its_title_line_and_each_triple_binds_to_its_column():
    e, lo, hi, ev = tp.regulator_tuple(LABEL, "Table 4", r"150\s*mg", "warfarin")
    assert (e, lo, hi) == ("0.65", "0.52", "0.81")
    assert tp.regulator_tuple(LABEL, "Table 4", r"110\s*mg", "warfarin")[:3] == ("0.90", "0.74", "1.10")
    assert ev["columns"] == ["150 mg", "110 mg", "Warfarin"]
    # a 'Patients randomized' COUNT row is not a statement of the analysis population (codex review 3 Oct): reported as
    # counts, the population stays NOT_STATED (a silent axis in the verdict, never assumed ITT)
    assert ev["randomized_counts"] == "6076 6015 6022" and ev["population_class"] == "NOT_STATED"
    assert tp.regulator_tuple(LABEL, "Table 4", r"150\s*mg", "warfarin", outcome_re=r"major bleed") is None
    assert tp.regulator_tuple(LABEL.replace("Figure 1 Kaplan-Meier curve\n", ""), "Table 4", r"150\s*mg",
                              "warfarin")[:3] == ("0.65", "0.52", "0.81")      # a final table at the end of the text
    assert tp.regulator_tuple(LABEL, "Table 4", r"75\s*mg", "warfarin") is None      # no such column: refused


def test_a_held_text_with_a_different_hash_is_refused(monkeypatch):
    import pytest
    spec = dict(tp.SPECS[0]["regulator"], sha256="0" * 64)
    with pytest.raises(RuntimeError):
        tp.held_text(spec)
