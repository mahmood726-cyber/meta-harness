"""G1 tracker page (scripts/render_g1_tracker.py): the count rule Mahmood set, and the page's currency.

Rule (2026-10-02): count PRIMARY and TWO_SOURCE rows; exclude anything sourced only from the comparator itself. Each
plant below would pass a renderer that copied the lane's route tally instead of applying the rule.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("render_g1_tracker", ROOT / "scripts" / "render_g1_tracker.py")
g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g1)

COMP = "34526024"


def _rec(trials, routes=None):
    return {"schema_version": 1, "slug": "glp1-ra-mace-t2d", "comparator_pmid": COMP, "N_comparator_trials": len(trials),
            "k_matched": len(trials), "N_eligible": len(trials), "trials": trials,
            "routes": routes if routes is not None else {}, "same_trials": {}}


def test_primary_counts_and_unverified_or_no_row_never_count():
    s = g1.topic_summary(_rec([{"label": "A", "route": "PRIMARY"}, {"label": "B", "route": "UNVERIFIED"},
                               {"label": "C", "route": "NO_ROW"}]))
    assert s["g1_count"] == 1 and [r["counted"] for r in s["rows"]] == [True, False, False]


def test_PLANT_a_two_source_pair_containing_the_comparator_does_not_count():
    s = g1.topic_summary(_rec([{"label": "A", "route": "TWO_SOURCE", "independent_pair_ids": ["PMID 34526024", "11111111"]}]))
    assert s["g1_count"] == 0 and "anti-circularity" in s["rows"][0]["why"]


def test_PLANT_a_two_source_row_with_an_unknown_pair_does_not_count():
    s = g1.topic_summary(_rec([{"label": "A", "route": "TWO_SOURCE"}]))
    assert s["g1_count"] == 0 and "fail-closed" in s["rows"][0]["why"]


def test_an_independent_pair_without_the_comparator_counts():
    s = g1.topic_summary(_rec([{"label": "A", "route": "TWO_SOURCE",
                                "verification": {"independent_pair_ids": ["22222222", "10.1000/xyz"]}}]))
    assert s["g1_count"] == 1


def test_PLANT_a_lane_tally_that_disagrees_with_the_rule_is_printed_not_adopted(tmp_path):
    (tmp_path / g1.SRC).mkdir(parents=True)
    rec = _rec([{"label": "A", "route": "TWO_SOURCE", "independent_pair_ids": [COMP, "1"]}], routes={"TWO_SOURCE": 1})
    (tmp_path / g1.SRC / "glp1-ra-mace-t2d.json").write_text(json.dumps(rec), encoding="utf-8")
    page = g1.render(tmp_path)
    assert "<strong>0</strong> of 1" in page and "recounted under the G1 rule" in page
    assert page.count("NOT YET LANDED") == 3


def test_the_committed_page_is_current():
    assert (ROOT / g1.OUT).read_bytes() == g1.render().encode("utf-8")
