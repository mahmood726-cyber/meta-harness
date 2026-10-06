"""The commit a lane artefact is read at: outputs/k_gap/lane_pins.json, never the lane branch's moving tip (a lane that
pushed during a regeneration made it never converge, 6 Oct). A branch with no pin, or a pin this repository does not
hold, raises -- fail closed."""
from __future__ import annotations

import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINS = os.path.join(ROOT, "outputs", "k_gap", "lane_pins.json")


class LanePinMissing(RuntimeError):
    pass


def commit_for(branch: str, pins_path: str | None = None) -> str:
    p = pins_path or PINS
    pins = (json.load(open(p, encoding="utf-8")).get("pins") or {}) if os.path.exists(p) else {}
    sha = pins.get(branch)
    if not sha:
        raise LanePinMissing(f"lane branch {branch!r} has no pin in outputs/k_gap/lane_pins.json: pin the commit to read "
                             "(the captain sets it at a consolidation), never the moving tip")
    r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise LanePinMissing(f"pinned commit {sha[:12]} for {branch!r} is not in this repository: fetch it")
    return sha
