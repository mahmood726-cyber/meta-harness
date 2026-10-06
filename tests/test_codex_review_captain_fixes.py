"""Plants from the 6 Oct codex review of the night's merges (scripts/pr_codex_review.py; records in
registry/model_proposals/pr_codex_review.json). Each was reproduced on its exact input before the fix, and fails at
the previous commit."""
import os
import sys
from types import SimpleNamespace as NS
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def test_acquired_merge_prefers_the_trials_own_registration_over_a_shared_pmid():
    # merge-ede33d9b2:g2#1: PMID 123 reports trials A and B; trial B's own NCT must win, never A's counts by the PMID
    import g1_tracker as g
    va = dict(events_t=1, n_t=100, events_c=2, n_c=100)
    vb = dict(events_t=30, n_t=200, events_c=40, n_c=200)
    a = dict(label="Trial A", admitted=dict(kind="TEXT", source="s", value=va))
    b = dict(label="Trial B", admitted=dict(kind="TEXT", source="s", value=vb))
    x = dict(label="Renamed Trial B", family="PMID 123", route="SECONDARY_SINGLE", g1_countable=True, in_our_pool=False,
             registry_binding={"candidates": [{"nct": "NCT00000002"}]})
    with patch.object(g, "acquired_rows", return_value={"PMID 123": a, "NCT00000001": a, "NCT00000002": b}):
        g.acquired_merge("test", [x])
    assert x["our_value"] == vb


def test_a_pmid_two_admitted_rows_share_resolves_to_neither(tmp_path):
    import json
    import g1_tracker as g
    rows = [{"label": "A", "pmid": "123", "ncts": [], "verdict": "ADMITTED", "admitted": {"value": {}}},
            {"label": "B", "pmid": "123", "ncts": [], "verdict": "ADMITTED", "admitted": {"value": {}}}]
    os.makedirs(tmp_path / "registry" / "g1_acquired")
    (tmp_path / "registry" / "g1_acquired" / "t.json").write_text(json.dumps({"rows": rows}), encoding="utf-8")
    with patch.object(g, "ROOT", str(tmp_path)):
        acq = g.acquired_rows("t")
    assert acq["PMID 123"] is g.AMBIGUOUS_ACQUIRED and acq["A"]["label"] == "A"


def test_served_pool_notice_control_compares_the_interval_and_every_served_row():
    from scripts import g1_served_pool_notices as m
    from harness import pipeline
    x = dict(label="new", family="new", route="PRIMARY")
    common = dict(served_identity=(set(), set()))
    # merge-5824d5844:g1#1: the engine reproduces the estimate but NOT the interval -> refused
    before = dict(k=1, estimate=1.0, ci_low=0.8, ci_high=1.2)
    with patch.object(m, "candidates", return_value=([x], [])), patch.object(m.fn, "served", return_value={"result": before}), \
            patch.object(m.rc, "result_tuple", side_effect=lambda r: r), patch.object(m.fn, "served_studies", return_value=[NS()]), \
            patch.object(m.synth, "pool", return_value=NS(k=1, estimate=1.0, ci_low=0.1, ci_high=10.0)), \
            patch.object(m, "served_identity", return_value=common["served_identity"]), \
            patch.object(m.fn, "fill_study", return_value=(NS(), None)), \
            patch.object(pipeline, "_pool_result", return_value=dict(k=2, estimate=1.0, ci_low=0.1, ci_high=10.0)):
        notice, excluded = m.topic_notice({"slug": "test"})
    assert notice is None and "control failed" in excluded[-1]["why"]
    # merge-5824d5844:g1#2: served k=2 but no served row rebuilt -> refused (never a notice that drops served trials)
    before = dict(k=2, estimate=1.0, ci_low=0.8, ci_high=1.2)
    with patch.object(m, "candidates", return_value=([x], [])), patch.object(m.fn, "served", return_value={"result": before}), \
            patch.object(m.rc, "result_tuple", side_effect=lambda r: r), patch.object(m.fn, "served_studies", return_value=[]), \
            patch.object(m, "served_identity", return_value=common["served_identity"]), \
            patch.object(m.fn, "fill_study", return_value=(NS(), None)):
        notice, excluded = m.topic_notice({"slug": "test"})
    assert notice is None and "served rows rebuilt" in excluded[-1]["why"]
