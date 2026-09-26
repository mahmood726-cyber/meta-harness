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


def test_the_committed_plan_runs_in_the_ordered_sections():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    secs = [i["section"] for i in plan["items"]]
    assert secs == sorted(secs, key=lambda x: x[0])  # 1 GLP-1, 2 re-derived, 3 evid2, 4 PRESERVED-HF
    assert plan["items"][0]["kind"] == "bundle" and plan["items"][0]["bundle_sha256"].startswith("170c6922")
    assert plan["items"][0]["intent"]["quote"] == "ten trials please with old k on same page"
    assert any("prespecified" in line for line in plan["items"][0]["lines"])  # the ELIXA dispute is stated
    ph = [i for i in plan["items"] if i["section"].startswith("4")]
    assert ph[0]["kind"] == "ruling" and ph[0]["id"] == "R-PRESERVED-HF" and "NCT03030235" in ph[0]["question"]
    assert "DELIVER" not in json.dumps([i for i in plan["items"] if i["id"] == "R-PRESERVED-HF"]).replace(
        "not DELIVER, which is NCT03619213", "").replace("first mislabelled DELIVER", "")
    assert set(plan["held_not_in_session"]) == {"N06", "N27", "N28", "N38"}
    audit = {r["audit_id"]: r for r in json.loads((ROOT / "registry/notice_adjudication.json").read_text(encoding="utf-8"))["notices"]}
    for i in plan["items"]:
        if i["kind"] == "notice":  # every command is bound to the current judgement
            assert i["judgement"] == audit[i["id"]]["judgements"][-1]["judgement_id"]
            assert i["expect_digest"] == audit[i["id"]]["judgements"][-1]["rendered_block_sha256"]


def test_the_plan_builder_refuses_decisions_that_name_unknown_notices(tmp_path):
    sl = tmp_path / "sl.json"
    sl.write_text(json.dumps({"rows": []}))
    dec = tmp_path / "dec.json"
    dec.write_text(json.dumps({"hold": {"N99": "x"}}))
    with pytest.raises(SystemExit, match="not on the signing list"):
        sign_session_plan.main(["--signing-json", str(sl), "--decisions", str(dec), "--out", str(tmp_path / "p.json"),
                                "--config", str(ROOT / "outputs/handover/lanes/nr-2026-09-25/session/session_config.json")])


def test_a_bundle_stale_on_main_is_refused_even_if_it_matches_its_own_commit(monkeypatch):
    item = {"source_commit": "a" * 40, "bundle_sha256": "b" * 64}
    files = lambda h: [{"path": "docs/reviews/glp1-ra-mace-t2d/review.json", "sha256": h}]  # noqa: E731
    calls = {"a" * 40: ("b" * 64, files("1")), "origin/main": ("c" * 64, files("2"))}
    monkeypatch.setattr(sign_session.planmod, "glp1_bundle", lambda ref: calls[ref])
    monkeypatch.setattr(sign_session.subprocess, "run", lambda *a, **k: None)
    why = sign_session.bundle_problem(item)
    assert why and "STALE" in why and "review.json" in why
    calls["origin/main"] = ("b" * 64, files("1"))
    assert sign_session.bundle_problem(item) is None
