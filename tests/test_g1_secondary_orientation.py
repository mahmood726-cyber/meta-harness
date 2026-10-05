"""PLANT (5 Oct, melatonin Dawson 1998): a SECONDARY_SINGLE MD row from a meta whose OWN text states that a positive
difference is a REDUCTION with the intervention (rule F2) is mirrored into our convention (intervention minus control)
before it is compared; a meta that states nothing, a missing held text, or a ratio measure leave the row unchanged."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_tracker as gt  # noqa: E402


def _row(meta, measure="MD", effect="1.7", lower="-12.71", upper="16.11"):
    return gt.sm.SecondaryRow(meta_pmid=meta, meta_doi="", location={}, source_digest="", provenance="x",
                              trial_label="Dawson D, 1998 [35]", measure=measure, outcome_definition="",
                              effect=effect, lower=lower, upper=upper)


def test_neg_keeps_printed_precision():
    assert [gt._neg(x) for x in ("1.7", "-12.71", "16.11", "0.00", None)] == ["-1.7", "12.71", "-16.11", "0.00", None]


def test_a_meta_stating_positive_is_reduction_is_mirrored():
    r, o = gt.oriented_secondary_row(_row("23691095"))          # its own sentence: 'efficacy in reducing sleep latency (WMD = 7.06'
    assert (r.effect, r.lower, r.upper) == ("-1.7", "-16.11", "12.71")
    assert o["convention"] == "POSITIVE_IS_REDUCTION_WITH_INTERVENTION" and "reducing sleep latency" in o["span"]
    assert o["printed"] == {"effect": "1.7", "lower": "-12.71", "upper": "16.11"}
    # the comparator 35691474 prints Dawson -1.70: the mirrored row now agrees on the point
    v = gt.result_verdict({"estimate": -1.7, "ci_low": -16.11, "ci_high": 12.71}, {"estimate": -1.70, "ci_low": -5.86, "ci_high": 2.46}, "MD")
    assert v["verdict"] == "AGREE"


def test_rows_left_unchanged():
    r, o = gt.oriented_secondary_row(_row("23691095", measure="RR", effect="0.8", lower="0.6", upper="1.1"))
    assert (r.effect, o) == ("0.8", None)                         # a ratio has no mirrored convention
    r, o = gt.oriented_secondary_row(_row("99999999"))
    assert r.effect == "1.7" and o["convention"] == "NOT_STATED"  # no held text: never guessed
