"""The one-sitting signing session: its identity and push guards, and the committed plan. No signature is made here;
the end-to-end run (TEST identity, throwaway clone, local push) is recorded in
outputs/handover/lanes/nr-2026-09-25/session/TEST_RUN_*."""
import json
from pathlib import Path

import pytest

from scripts import sign_session, sign_session_plan

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "registry/sign_session_plan.json"


@pytest.mark.parametrize("args,why", [
    (["--by", "Mahmood", "--test", "--push-remote", "C:/nowhere"], "never as Mahmood"),
    (["--by", "TEST-X", "--test"], "never to GitHub"),
    (["--by", "TEST-X"], "for --test rehearsals only"),
])
def test_identity_and_push_guards_refuse_before_anything_is_read(args, why):
    with pytest.raises(SystemExit, match=why):
        sign_session.main(["--plan", str(PLAN), "--push-branch", "x", *args])


def test_the_wrong_branch_refuses(monkeypatch):
    monkeypatch.setattr(sign_session, "git", lambda *a, check=True: "" if a[0] == "status" else "nr/notice-anchors")
    with pytest.raises(SystemExit, match="switch -c sign/mahmood"):
        sign_session.main(["--plan", str(PLAN), "--by", "Mahmood", "--push-branch", "sign/mahmood"])


def test_the_committed_plan_is_the_reviewed_one():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    kinds = [i["kind"] for i in plan["items"]]
    assert kinds.count("notice") == 19 and kinds.count("bundle") == 1 and kinds.count("ruling") == 3
    assert [i["id"] for i in plan["items"] if i["kind"] == "ruling"][0] == "R-DELIVER"
    assert set(plan["held_not_in_session"]) == {"N06", "N27", "N28", "N38"}
    assert len(plan["excluded_not_in_session"]) == 18
    audit = {r["audit_id"]: r for r in json.loads((ROOT / "registry/notice_adjudication.json").read_text(encoding="utf-8"))["notices"]}
    for i in plan["items"]:
        if i["kind"] == "notice":  # every command is bound to the current judgement
            assert i["judgement"] == audit[i["id"]]["judgements"][-1]["judgement_id"]
            assert i["expect_digest"] == audit[i["id"]]["judgements"][-1]["rendered_block_sha256"]
    bundle = next(i for i in plan["items"] if i["kind"] == "bundle")
    assert bundle["bundle_sha256"].startswith("170c6922")


def test_the_plan_builder_refuses_decisions_that_name_unknown_notices(tmp_path):
    sl = tmp_path / "sl.json"
    sl.write_text(json.dumps({"rows": []}))
    dec = tmp_path / "dec.json"
    dec.write_text(json.dumps({"hold": {"N99": "x"}}))
    with pytest.raises(SystemExit, match="not on the signing list"):
        sign_session_plan.main(["--signing-json", str(sl), "--decisions", str(dec), "--out", str(tmp_path / "p.json")])
