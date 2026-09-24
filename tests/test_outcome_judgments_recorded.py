"""scripts/outcome_judgments.py -- the legacy codex caller, routed through the recorded path.

Before (main 9fc4518a): `--codex` called codex directly (unrecorded), took the model's stdout, silently SKIPPED any
candidate whose answer did not parse (the denominator shrank), and wrote model='codex-default' when no model was
given; `--write` labelled hand judgments 'hand/model via --write'. Each property below plants one of those.
Runs on a temporary copy of one topic with a fake client: no model is called, nothing is written into the repo.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from reproducible_ai import model_inventory as mi
from reproducible_ai import model_source as ms

ROOT = Path(__file__).resolve().parents[1]
SLUG = "balanced-crystalloids-vs-saline-mortality"
HEADER = (b"OpenAI Codex v0.0\n--------\nmodel: planted-model\nprovider: planted\nreasoning effort: medium\n"
          b"--------\n")
GOOD = {"candidate_population": "p", "candidate_timepoint": "t", "candidate_definition": "d", "is_match": True,
        "rationale": "r"}


@pytest.fixture
def oj(tmp_path, monkeypatch):
    for rel in (f"topics/{SLUG}.json", f"cache/{SLUG}/records.json"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, tmp_path / rel)
    spec = importlib.util.spec_from_file_location("_oj", ROOT / "scripts" / "outcome_judgments.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ROOT", str(tmp_path))
    return mod, tmp_path


def _runner(answers):
    it = iter(answers)

    def run(prompt, schema, model, effort, timeout_s):
        rc, body = next(it)
        return {"rc": rc, "stdout": b"", "stderr": HEADER, "last_message": body, "argv": ["fake"]}
    return run


def test_codex_without_a_pinned_model_is_refused(oj):
    mod, tmp = oj
    assert mod.main([SLUG, "--codex"]) == 2
    assert not (tmp / "cache" / SLUG / "outcome_judgments.json").exists()


def test_every_candidate_is_recorded_and_a_failure_is_listed_not_dropped(oj):
    mod, tmp = oj
    _, cands = mod.collect_candidates(SLUG)
    assert len(cands) >= 2, "the fixture topic must offer at least two candidates for this property"
    answers = [(0, json.dumps(GOOD).encode()), (0, b"not json at all")] + [(1, b"")] * (len(cands) - 2)
    mod.RUNNER = _runner(answers)
    assert mod.main([SLUG, "--codex", "--model", "planted-model"]) == 0
    out = json.loads((tmp / "cache" / SLUG / "outcome_judgments.json").read_text(encoding="utf-8"))
    judged, not_judged = out["judgments"], out["not_judged"]
    assert len(judged) + len(not_judged) == len(cands)             # the denominator never shrinks
    assert {n["state"] for n in not_judged} <= {"RESPONSE_NOT_A_CLAIM", "RAN_ERROR", "INVALID"}
    assert "model" not in out and out["provenance"]["kind"] == "RECORDED_MODEL_CALLS"
    recs = {p.stem: ms.load_record(p) for p in (tmp / "registry" / "model_calls").glob("mc-*.json")}
    assert len(recs) == len(cands)                                  # one record per call, failures included
    for title, j in judged.items():                                 # a judgment IS its record's replayed answer
        claim = ms.extract_claim("outcome", ms.replay(recs[j["record_id"]]))
        assert {k: j[k] for k in GOOD} == claim
    # the repo-wide inventory classifies this cache as RECORDED (every judgment names a stored record)
    assert [o["state"] for o in mi.model_outputs(tmp)] == ["RECORDED"]


def test_hand_judgments_need_a_named_author_and_are_not_labelled_model_output(oj, tmp_path):
    mod, tmp = oj
    src = tmp_path / "hand.json"
    src.write_text(json.dumps({"Some measure": GOOD}), encoding="utf-8")
    assert mod.main([SLUG, "--write", str(src)]) == 2
    assert mod.main([SLUG, "--write", str(src), "--author", "Reviewer Fixture"]) == 0
    out = json.loads((tmp / "cache" / SLUG / "outcome_judgments.json").read_text(encoding="utf-8"))
    assert out["provenance"] == {"kind": "HAND", "author": "Reviewer Fixture"}
    assert out["judgments"]["Some measure"]["author"] == "Reviewer Fixture"
    assert "model" not in out and "model" not in out["judgments"]["Some measure"]
