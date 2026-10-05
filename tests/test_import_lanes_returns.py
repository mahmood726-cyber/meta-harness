"""Plant (5 Oct, forest lane): apply_resolutions must return the lane object even when the resolutions file exists --
g1/forest-reader had lost its `return o` (the consolidation keeps it), so every lane import crashed on None."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_import_lanes as gil  # noqa: E402


def test_apply_resolutions_returns_the_object_with_a_resolutions_file(tmp_path):
    p = tmp_path / "res.json"
    p.write_text(json.dumps({"resolutions": {}}), encoding="utf-8")
    o = {"trials": [{"label": "X", "agreement_with_comparator_row": "AGREE", "in_our_pool": True}]}
    out = gil.apply_resolutions("s", o, path=str(p))
    assert out is o and out["per_trial_agreement"] == {"AGREE": 1}
