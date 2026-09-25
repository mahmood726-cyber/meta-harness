"""V1 re-derivation tooling. The control is the real pair the 41 notices were raised on: served main c9d665e0 against
the enforcement gate 1fa77f2c must re-derive exactly the 41 notices, with nothing unnoticed and nothing orphaned."""
import copy
import json
import subprocess
from pathlib import Path

import pytest

from scripts import rederive_notices as rd
from scripts import v1_notice_registry as reg

ROOT = Path(__file__).resolve().parents[1]
PREV = "c9d665e022a36111f31cb9e1d7b5867fe6e8fb2d"
GATE = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"


def _have(sha):
    return subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT).returncode == 0


needs_history = pytest.mark.skipif(not (_have(PREV) and _have(GATE)), reason="PREV / gate commits not in this clone")


@pytest.fixture(scope="module")
def control():
    return rd.rederive(PREV, GATE, "HEAD")


@needs_history
def test_the_control_pair_re_derives_exactly_the_41(control):
    c = control["counts"]
    assert c["served_number_changes"] == c["noticed"] == 41
    assert c["unnoticed"] == c["ambiguous"] == c["orphans"] == c["membership_mismatch"] == 0
    assert c["old_41"] == {"SAME": 41, "CHANGED": 0, "GONE": 0}


@needs_history
def test_the_registry_rebuilt_from_the_control_keeps_every_row_and_judgement(control):
    built = reg.build(control, "HEAD")
    head = json.loads((ROOT / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
    old = {r["audit_id"]: r for r in head["notices"]}
    assert {r["audit_id"] for r in built["notices"]} == set(old)
    for r in built["notices"]:
        assert r["judgements"] == old[r["audit_id"]]["judgements"]
        assert [t["current_pointer"] for t in r["departing_trials"]] == \
               [t["current_pointer"] for t in old[r["audit_id"]]["departing_trials"]]


@pytest.mark.parametrize("field", ["unnoticed", "ambiguous", "orphans"])
def test_the_registry_refuses_an_unclean_re_derivation(control, field):
    dirty = copy.deepcopy(control)
    dirty["counts"][field] = 1
    with pytest.raises(SystemExit, match="not clean"):
        reg.build(dirty, "HEAD")


@needs_history
def test_a_changed_transition_gets_a_new_row_that_supersedes_the_old(control, monkeypatch):
    # in-memory: the candidate's ledger and page move N28's after 0.85 -> 0.84 (the shape of a notice the fix changes)
    changed = copy.deepcopy(control)
    row = next(x for x in changed["changes"] if x["slug"] == "pcsk9-mace")
    row["after"] = dict(row["after"], estimate=0.84)
    original_show = reg.show

    def show(ref, path):
        raw = original_show(ref, path)
        if ref == GATE and path == "docs/result_changes.json":
            data = json.loads(raw)
            data["notices"][row["ledger_index"]]["after"]["estimate"] = 0.84
            return json.dumps(data).encode()
        return raw
    monkeypatch.setattr(reg, "show", show)
    built = reg.build(changed, "HEAD")
    new = [r for r in built["notices"] if r["audit_id"].startswith("V1-")]
    assert len(new) == 1 and new[0]["supersedes_audit_id"] == "N28" and new[0]["after"]["estimate"] == 0.84
    assert new[0]["individual_review_required_by_lane"] and not new[0].get("judgements")
    assert built["v1_candidate"]["new_or_changed"] == 1
