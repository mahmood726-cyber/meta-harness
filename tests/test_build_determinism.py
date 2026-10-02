"""A review core must be the same BYTES whatever the interpreter's hash seed.

2026-10-02 (incremental-rebuild proof): a full rebuild of main rewrote review.json on 11 topics with nothing changed
but key order. harness/pipeline._apply_trial_annotations iterated its whitelist `allowed`, a SET, so per-trial keys
(endpoint_definition, follow_up_window, analysis_set, ...) were inserted in PYTHONHASHSEED order. review_sha256 is
canonical and the pages did not move, but the served review.json bytes did -- so "unchanged inputs -> unchanged
outputs" was false, and no incremental build could be proven equal to a full one.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(seed: int, code: str) -> str:
    env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True,
                       encoding="utf-8", stdin=subprocess.DEVNULL, timeout=600)
    assert p.returncode == 0, p.stderr[-2000:]
    return p.stdout


def test_PLANT_trial_annotation_keys_do_not_follow_the_hash_seed():
    code = (
        "import json; from harness.pipeline import _apply_trial_annotations as a\n"
        "ann = {'endpoint_definition': 'e', 'follow_up_window': 'f', 'analysis_set': 'a', 'background_therapy': 'b',"
        " 'components': ['x'], 'dose_regimen': 'd', 'prior_disease_stage': 'p', 'not_allowed': 1}\n"
        "t = [{'id': 'PMID 1', 'study_effect': 0}]\n"
        "a({'trial_annotations': {'1': ann}}, t)\n"
        "print(json.dumps(list(t[0])))\n")
    orders = {_run(seed, code) for seed in (0, 1, 2, 3)}
    assert len(orders) == 1, orders
    assert json.loads(orders.pop()) == ["id", "study_effect", "endpoint_definition", "follow_up_window",
                                        "analysis_set", "background_therapy", "components", "dose_regimen",
                                        "prior_disease_stage"]


def test_PLANT_a_whole_review_core_is_byte_identical_across_hash_seeds():
    # colchicine-postop-af carries trial_annotations (its review.json moved under a different seed before the fix)
    code = (
        "import hashlib, json, sys; sys.path.insert(0, 'scripts')\n"
        "from harness import fetch; from harness.pipeline import build_review_core\n"
        "import build_topic\n"
        "slug = 'colchicine-postop-af'\n"
        "config = json.load(open(f'topics/{slug}.json', encoding='utf-8'))\n"
        "records = fetch.ensure(config, '2026-09-11')\n"
        "core = build_review_core(slug, config, records, build_topic._protocol_sha(slug))\n"
        "print(hashlib.sha256(json.dumps(core, ensure_ascii=False, indent=2).encode('utf-8')).hexdigest())\n")
    digests = {_run(seed, code).strip().splitlines()[-1] for seed in (0, 1)}
    assert len(digests) == 1, digests
