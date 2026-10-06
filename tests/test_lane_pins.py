"""Plant: a lane artefact is read at its PINNED commit, never the branch's moving tip (6 Oct: forest-reader pushed during
a regeneration -- de51fef34 -> 04885641e between passes -- and the regeneration never reached a fixed point)."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import lane_pins  # noqa: E402


def test_a_pinned_branch_reads_its_pin(tmp_path):
    head = os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip()
    p = tmp_path / "pins.json"
    p.write_text(json.dumps({"pins": {"g1/x": head}}), encoding="utf-8")
    assert lane_pins.commit_for("g1/x", str(p)) == head


def test_an_unpinned_branch_fails_closed(tmp_path):
    p = tmp_path / "pins.json"
    p.write_text(json.dumps({"pins": {}}), encoding="utf-8")
    with pytest.raises(lane_pins.LanePinMissing, match="no pin"):
        lane_pins.commit_for("g1/x", str(p))


def test_a_pin_the_repository_does_not_hold_fails_closed(tmp_path):
    p = tmp_path / "pins.json"
    p.write_text(json.dumps({"pins": {"g1/x": "0" * 40}}), encoding="utf-8")
    with pytest.raises(lane_pins.LanePinMissing, match="not in this repository"):
        lane_pins.commit_for("g1/x", str(p))


def test_no_reader_resolves_a_lane_branch_tip():
    for f in ("scripts/g1_tracker.py", "scripts/secondary_meta_build.py", "scripts/g1_import_lanes.py"):
        src = open(os.path.join(ROOT, f), encoding="utf-8").read()
        assert 'f"origin/{src[' not in src and "f\"origin/{spec[" not in src, f
