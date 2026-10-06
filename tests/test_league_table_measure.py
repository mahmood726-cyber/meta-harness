"""Plant (codex P0, merge-ede33d9b2:g1#1): read_league returned every league table as odds ratios. The measure must
come from the table's own words; a table naming none, or several, gives no result; the orientation check quotes the
abstract on the same measure. The dpp4 comparator 31462224 (odds ratios, OR 0.87 GLP-1 check) still reads as OR."""
import importlib.util
import os

_P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "comparator_league_result.py")
_spec = importlib.util.spec_from_file_location("comparator_league_result", _P)
clr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clr)

ORIENT = "Comparisons should be read from left to right. {measure} in the column-defining therapy compared with the row-defining therapy."


def _jats(measure_sentence, abstract):
    rows = [["MACE"], ["DPP-4 inhibitor", "1.15 (1.06-1.25)", "1.00 (0.93-1.07)"],
            ["1.00 (0.94-1.07)", "GLP-1 RA", "1.15 (1.08-1.22)"],
            ["1.00 (0.94-1.07)", "0.87 (0.82-0.93)", "Placebo"]]
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f"<article><abstract><p>{abstract}</p></abstract><table-wrap><label>Table 2</label>"
            f"<caption><p>Network meta-analysis</p></caption><table>{trs}</table>"
            f"<table-wrap-foot><p>{ORIENT.format(measure=measure_sentence)}</p></table-wrap-foot></table-wrap></article>")


def test_risk_ratio_table_is_not_returned_as_odds_ratio():
    res, why = clr.read_league(_jats("Results are the risk ratios (95% CI)", "GLP-1 RA OR 0.87, 95% CI 0.82-0.93"),
                               "DPP-4 inhibitor", "Placebo", "MACE")
    assert res is None or res["scale"] != "OR"


def test_risk_ratio_table_reads_as_rr_with_rr_check():
    res, why = clr.read_league(_jats("Results are the risk ratios (95% CI)", "GLP-1 RA RR 0.87, 95% CI 0.82-0.93"),
                               "DPP-4 inhibitor", "Placebo", "MACE")
    assert why is None and res["scale"] == "RR" and res["estimate"] == 1.00


def test_no_measure_named_refuses():
    res, why = clr.read_league(_jats("Results are shown", "GLP-1 RA OR 0.87, 95% CI 0.82-0.93"),
                               "DPP-4 inhibitor", "Placebo", "MACE")
    assert res is None and why == "MEASURE_NOT_STATED_BY_THE_TABLE"


def test_two_measures_named_refuses():
    res, why = clr.read_league(_jats("Results are odds ratios; HR: hazard ratio", "GLP-1 RA OR 0.87, 95% CI 0.82-0.93"),
                               "DPP-4 inhibitor", "Placebo", "MACE")
    assert res is None and why.startswith("MEASURE_AMBIGUOUS_IN_THE_TABLE")


def test_odds_ratio_table_still_reads_as_or():
    res, why = clr.read_league(_jats("Results are the odds ratios (95% confidence interval)",
                                     "GLP-1 RA OR 0.87, 95% CI 0.82-0.93"), "DPP-4 inhibitor", "Placebo", "MACE")
    assert why is None and res["scale"] == "OR" and res["estimate"] == 1.00
