"""Plant: a signing packet must present EVERY served outcome that changes, never only the headline one.
6 Oct: V6-01 showed the signer dpp4's MACE change (k 3 -> 4) but the same change also withdrew the served
heart-failure-hospitalisation estimate; the guard now diffs every outcome of every topic named in the packet against
the served base and refuses an unlisted change."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import signing_packet as sp  # noqa: E402


def _review(mace, hhf):
    def res(k, est):
        return {"k": k, "estimate": est, "ci_low": est - 0.1, "ci_high": est + 0.1} if k else {"present": False}
    return {"outcomes": [
        {"name": "MACE", "primary": True, "result": res(*mace), "trials": [{"id": f"T{i}"} for i in range(mace[0])]},
        {"name": "HHF", "result": res(*hhf), "trials": [{"id": f"H{i}"} for i in range(hhf[0])]}]}


def _repo(tmp_path, base, cand):
    root = tmp_path / "r"
    d = root / "docs" / "reviews" / "t"
    d.mkdir(parents=True)
    (root / "docs" / "result_changes.json").write_text(json.dumps({"notices": []}), encoding="utf-8")
    run = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)  # noqa: E731
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    (d / "review.json").write_text(json.dumps(base), encoding="utf-8")
    run("add", "-A")
    run("commit", "-q", "-m", "base")
    run("branch", "-f", "basebr")
    (d / "review.json").write_text(json.dumps(cand), encoding="utf-8")
    return root


def test_every_changed_outcome_is_found(tmp_path):
    root = _repo(tmp_path, _review((3, 1.0), (1, 1.0)), _review((4, 0.9), (2, 1.1)))
    ch = {c["outcome"]: c for c in sp.served_outcome_changes(root, "t", "basebr")}
    assert set(ch) == {"MACE", "HHF"} and ch["HHF"]["before"]["k"] == 1 and ch["HHF"]["after"]["k"] == 2


def test_a_packet_listing_only_the_headline_outcome_is_refused(tmp_path):
    root = _repo(tmp_path, _review((3, 1.0), (1, 1.0)), _review((4, 0.9), (2, 1.1)))
    probs = sp.completeness_problems(root, [("t", "MACE")], "basebr")
    assert len(probs) == 1 and probs[0].startswith("UNLISTED CHANGE t / HHF")
    assert sp.completeness_problems(root, [("t", "MACE"), ("t", "HHF")], "basebr") == []


def test_an_unchanged_outcome_needs_no_entry(tmp_path):
    root = _repo(tmp_path, _review((3, 1.0), (1, 1.0)), _review((4, 0.9), (1, 1.0)))
    assert sp.completeness_problems(root, [("t", "MACE")], "basebr") == []
