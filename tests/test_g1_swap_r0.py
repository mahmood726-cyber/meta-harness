"""PLANT: rule R0 (pre-registered 6 Oct) -- the current comparator is KEPT (NO_SWAP) when it passes every criterion,
and when it fails one it is excluded and the failing criterion + evidence is recorded as its retirement reason."""
import json
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_comparator_select as cs  # noqa: E402

RULE = {"criteria": [{"id": "C1"}, {"id": "C2"}], "tie_breaks": [{"id": "T2_MOST_RECENT"}],
        "if_none_pass": "NO_ACHIEVABLE_COMPARATOR: x", "R0_current_comparator": {"comparator_pmid": "100"}}


def _cand(pmid, c1, c2, year):
    return {"pmid": pmid, "criteria": {"C1": {"verdict": c1, "evidence": f"e1 {pmid}"}, "C2": {"verdict": c2, "evidence": f"e2 {pmid}"}},
            "tie_breaks": {"T2_MOST_RECENT": year}}


def _run(tmp_path, cands):
    (tmp_path / "x.rule.json").write_text(json.dumps(RULE), encoding="utf-8")
    (tmp_path / "x.candidates.json").write_text(json.dumps({"candidates": cands}), encoding="utf-8")
    with patch.object(cs, "SEL", str(tmp_path)), patch.object(cs, "rule_sha", lambda s: "sha"):
        cs.main(["x"])
    return json.load(open(tmp_path / "x.selection.json", encoding="utf-8"))


def test_current_passing_every_criterion_is_kept(tmp_path):
    out = _run(tmp_path, [_cand("100", "PASS", "PASS", 2019), _cand("200", "PASS", "PASS", 2025)])
    assert out["result"] == "NO_SWAP_CURRENT_COMPARATOR_PASSES" and out["pick"]["pmid"] == "100"


def test_current_failing_a_criterion_is_retired_with_its_evidence(tmp_path):
    out = _run(tmp_path, [_cand("100", "FAIL", "PASS", 2019), _cand("200", "PASS", "PASS", 2025)])
    assert out["pick"]["pmid"] == "200" and out["result"] == "PICKED"
    assert out["R0"]["verdict"] == "RETIRE" and out["R0"]["failing"] == [{"criterion": "C1", "verdict": "FAIL", "evidence": "e1 100"}]


def test_current_failing_and_nothing_else_passes_keeps_it_as_no_achievable(tmp_path):
    out = _run(tmp_path, [_cand("100", "FAIL", "PASS", 2019), _cand("200", "PASS", "UNCLEAR", 2025)])
    assert out["pick"] is None and out["result"] == "NO_ACHIEVABLE_COMPARATOR" and out["R0"]["verdict"] == "RETIRE"


def test_swap_screen_ledger_keys_belong_to_their_topic():
    from kgap import runs_store
    assert runs_store.topic_of("swapscreen::pcsk9-mace::12345678") == "pcsk9-mace"
    assert runs_store.topic_of("swapscreenA::pcsk9-mace::12345678") == "pcsk9-mace"
    assert runs_store.topic_of("audit::pcsk9-mace::FOURIER") == "pcsk9-mace"
