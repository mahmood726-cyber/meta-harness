"""Nested-terminology screening guard (audit 16): an excluded phenotype term that is a substring of an
included phenotype must not exclude a record that is actually the included phenotype. "reduced ejection
fraction" (HFrEF, excluded) is nested inside "mildly reduced ejection fraction" (HFmrEF, included); a
bare-HFmrEF record matches both and X2 would fire first. The guard suppresses the exclusion only when
EVERY occurrence of the term is qualified into the included variant; a genuine HFrEF still excludes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import screen  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_all_occurrences_qualified_helper():
    q = ("mildly ", "or preserved ")
    assert screen._all_occurrences_qualified("heart failure with mildly reduced ejection fraction",
                                             "reduced ejection fraction", q) is True
    assert screen._all_occurrences_qualified("with reduced ejection fraction, LVEF <=40%",
                                             "reduced ejection fraction", q) is False
    # mixed: one qualified + one bare -> a genuine HFrEF mention exists -> not all qualified
    assert screen._all_occurrences_qualified("mildly reduced ejection fraction; also reduced ejection fraction arm",
                                             "reduced ejection fraction", q) is False


def test_hfmref_included_hfref_excluded():
    t = json.load(open(os.path.join(ROOT, "topics", "dapagliflozin-hfpef-hosp.json"), encoding="utf-8"))
    inc = t["include"]
    neg = set(t.get("negative_control_pmids") or [])
    hfmref = {"id": "T1", "id_type": "pmid",
              "title": "Dapagliflozin in heart failure with mildly reduced ejection fraction",
              "abstract": "A randomized, double-blind, placebo-controlled trial of dapagliflozin versus "
                          "placebo in mildly reduced ejection fraction.",
              "conditions": ["heart failure with mildly reduced ejection fraction"],
              "pubtypes": ["Randomized Controlled Trial"]}
    # HFmrEF must NOT be excluded as wrong-population (X2) — the nested HFrEF substring is suppressed
    d, rule = screen.screen_record(hfmref, inc, neg)[:2]
    assert rule != "X2", f"HFmrEF wrongly population-excluded: {rule}"
    hfref = {"id": "T2", "id_type": "pmid",
             "title": "Dapagliflozin in heart failure with reduced ejection fraction",
             "abstract": "randomized double-blind placebo-controlled; reduced ejection fraction, LVEF <=40%.",
             "conditions": ["heart failure with reduced ejection fraction"],
             "pubtypes": ["Randomized Controlled Trial"]}
    d2, rule2 = screen.screen_record(hfref, inc, neg)[:2]
    assert (d2, rule2) == ("exclude", "X2"), f"genuine HFrEF must still be X2-excluded: {(d2, rule2)}"
