"""From a release CANDIDATE sha to a tested one-sitting signing session for Mahmood, in three commands.

  python scripts/v1_prepare_session.py prepare  --cand <sha> [--prev <served sha>] --work DIR
  python scripts/v1_prepare_session.py finalize --work DIR --judged-by TEXT [--push]
  python scripts/v1_prepare_session.py test-sitting --work DIR

prepare   (run in a tree of nr/notice-anchors) re-derives every served-number change of the candidate against PREV
          (default: the newest ATTESTED production record) -- stops with the blockers named if anything is UNNOTICED,
          AMBIGUOUS or ORPHAN -- builds the candidate's audit registry and the sign branch nr/v1-sign-<c12>, makes a
          SPARSE worktree of it (patterns written before checkout), re-derives there with the candidate's own
          renderer, builds packets and mechanical checks, and drafts verdicts: a notice carried unchanged from the
          21 Sep audit inherits its last judgement's findings; a new or re-issued notice is listed in
          DIR/NEEDS_LANE_READ.md for the lane's hostile read before finalize.
finalize  appends judgement B3 (bound to the pinned anchors), commits, builds the signing list, derives the hold
          list from the data (a notice whose current judgement carries a wording defect is held), the withdrawn list
          (old notices GONE in the candidate) and the ruling-dependent notices (config), builds the one-sitting plan
          (registry/sign_session_plan.json: GLP-1, re-derived, evid2, PRESERVED-HF) and FINAL_SIGNING_LIST.md,
          commits, and with --push pushes the sign branch and proves it by fetched bytes.
test-sitting  clones the pushed sign branch sparse into DIR/tclone, runs the whole sitting as TEST-NR-LANE (--test:
          never Mahmood, never GitHub) with answers generated from the plan, pushes to the local repository, runs the
          verifier on the pushed commit, and deletes the test ref and clone.
Nothing here signs as, or for, Mahmood.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SPARSE = ["/*", "!/*/", "/harness/", "/scripts/", "/tests/", "/registry/", "/topics/", "/protocols/", "/.githooks/",
          "/docs/result_changes.json", "/docs/reviews/*/review.json", "/docs/reviews/*/index.html",
          "/cache/spironolactone-hfref-mortality/records.json", "/signatures/"]
CONFIG = "outputs/handover/lanes/nr-2026-09-25/session/session_config.json"
REPO_URL = "https://github.com/mahmood726-cyber/meta-harness.git"
ENV = dict(os.environ, PYTHONUTF8="1", MSYS_NO_PATHCONV="1")


def run(args, cwd=ROOT, check=True, **kw) -> subprocess.CompletedProcess:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=ENV, **kw)
    if check and p.returncode != 0:
        raise SystemExit(f"refused: {' '.join(map(str, args))[:200]}\n{(p.stderr or p.stdout)[-2000:]}")
    return p


def git(*a, cwd=ROOT, check=True) -> str:
    return run(["git", *a], cwd=cwd, check=check).stdout.strip()


def attested_prev() -> str:
    subj = git("log", "-1", "--format=%s", "origin/production-records")
    sha = subj.split("production record ", 1)[1].split(":", 1)[0]
    return git("rev-parse", "--verify", f"{sha}^{{commit}}")


def sparse_worktree(path: Path, ref: str) -> None:
    git("worktree", "add", "--no-checkout", str(path), ref)
    git("sparse-checkout", "init", "--no-cone", cwd=path)
    sc = Path(git("rev-parse", "--git-path", "info/sparse-checkout", cwd=path))
    sc = sc if sc.is_absolute() else path / sc
    sc.write_text("\n".join(SPARSE) + "\n", encoding="utf-8")
    git("checkout", "-q", ref.split("refs/heads/")[-1], cwd=path)


def cmd_prepare(a) -> int:
    work = Path(a.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    cand = git("rev-parse", "--verify", f"{a.cand}^{{commit}}")
    prev = git("rev-parse", "--verify", f"{a.prev}^{{commit}}") if a.prev else attested_prev()
    fix = git("show", f"{cand}:harness/trial_family.py").count("def population_matches")
    oc = run(["git", "merge-base", "--is-ancestor", "origin/oc/V1-READY-p10-p11", cand], check=False).returncode == 0
    status = {"cand": cand, "prev": prev, "p5_fix_in_candidate": bool(fix), "oc_v1_ready_in_candidate": oc}
    print(json.dumps(status))
    r = run([sys.executable, "scripts/rederive_notices.py", "--prev", prev, "--cand", cand, "--out", str(work / "rd")],
            check=False)
    print(r.stdout.strip())
    if r.returncode != 0:
        print("BLOCKED: the candidate's ledger does not cover its served-number changes; see", work / "rd/rederived.md")
        return 1
    run([sys.executable, "scripts/v1_notice_registry.py", "--rederived", str(work / "rd/rederived.json"),
         "--out", str(work / "registry.json"), "--audit-ref", "HEAD"])
    branch = a.branch or f"nr/v1-sign-{cand[:12]}"
    out = run([sys.executable, "scripts/v1_sign_branch.py", "--cand", cand, "--registry", str(work / "registry.json"),
               "--branch", branch, "--tools-ref", "HEAD"]).stdout
    print(out.strip())
    wt = work / "signwt"
    if wt.exists():
        raise SystemExit(f"refused: {wt} exists; remove it (git worktree remove) first")
    sparse_worktree(wt, branch)
    r2 = run([sys.executable, "scripts/rederive_notices.py", "--prev", prev, "--cand", cand, "--out", str(work / "rd2"),
              "--audit-ref", "HEAD"], cwd=wt, check=False)
    if r2.returncode != 0:
        raise SystemExit("refused: the re-derivation inside the sign branch is not clean:\n" + r2.stdout)
    run([sys.executable, "scripts/notice_rejudge.py", "packets", "--served", prev, "--proposed", cand,
         "--out", str(work / "packets")], cwd=wt)
    run([sys.executable, "scripts/v1_prepare_session.py", "_draft", "--work", str(work), "--prev", prev,
         "--cand", cand], cwd=wt)
    (work / "status.json").write_text(json.dumps(dict(status, branch=branch), indent=1), encoding="utf-8")
    print(f"prepared: {branch}; read {work / 'NEEDS_LANE_READ.md'}, then run finalize")
    return 0


def cmd_draft(a) -> int:
    """(inside the sign-branch worktree) draft verdicts bound to the anchors notice_rejudge will pin."""
    from scripts import notice_anchor as anchor
    from scripts import notice_rejudge as rj
    work = Path(a.work)
    checks = {c["audit_id"]: c for c in json.loads((work / "packets/checks.json").read_text(encoding="utf-8"))["checks"]}
    audit = json.loads(rj.AUDIT.read_text(encoding="utf-8"))
    out, needs = [], []
    for row in audit["notices"]:
        c = checks[row["audit_id"]]
        failing = [k for k, v in c.items() if v is False]
        anchors = rj.anchors_for(row, a.prev, a.cand)
        if row["audit_id"] in audit.get("specific_conflicts", {}):
            anchors.append(anchor.make(rj.ROOT, "held", a.cand, audit["specific_conflicts"][row["audit_id"]]["cache_path"]))
        last = (row.get("judgements") or [{}])[-1]
        carried = bool(row.get("judgements"))
        v = {"audit_id": row["audit_id"], "anchors": {x["ref"]: x["sha256"] for x in anchors},
             "rendered_block_sha256": c.get("rendered_block_sha256"),
             "before_after": last.get("before_after") or f"{row['before']} -> {row['after']}",
             "bulk_reader": last.get("bulk_reader") if carried else "PENDING: lane read of a new/re-issued notice",
             "bulk_verdict": last.get("bulk_verdict", "HOLDS") if carried else "HOLDS",
             "lane_verdict": last.get("lane_verdict", "HOLDS") if carried else "HOLDS",
             "defects": last.get("defects", []) if carried else [],
             "lane_notes": (last.get("lane_notes", "") if carried else "NEW OR RE-ISSUED in the V1 candidate: "
                            "mechanical checks pass; read by the lane before finalize"),
             "bulk_concerns": last.get("bulk_concerns", []), "departure_binding": last.get("departure_binding", [])}
        out.append(v)
        if failing or not carried:
            needs.append(f"- {row['audit_id']} {row['slug']} / {row['outcome']}: "
                         + (f"FAILING CHECKS {failing}" if failing else "new/re-issued -- read packets/"
                            f"{row['audit_id']}.json"))
    (work / "verdicts.json").write_text(json.dumps({"served": a.prev, "proposed": a.cand, "verdicts": out},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    (work / "NEEDS_LANE_READ.md").write_text("# Needs the lane's read before finalize\n\n" + ("\n".join(needs) or
                                             "(nothing: every notice is carried unchanged and passes)") + "\n",
                                             encoding="utf-8")
    print(f"draft verdicts: {len(out)}; needing a read: {len(needs)}")
    return 0


def cmd_finalize(a) -> int:
    work = Path(a.work).resolve()
    st = json.loads((work / "status.json").read_text(encoding="utf-8"))
    wt = work / "signwt"
    run([sys.executable, "scripts/notice_rejudge.py", "append", "--served", st["prev"], "--proposed", st["cand"],
         "--verdicts", str(work / "verdicts.json"), "--judgement-prefix", "B3", "--judged-by", a.judged_by], cwd=wt)
    git("-c", "user.name=lane NR", "-c", "user.email=nr@lanes.invalid", "commit", "-q", "-am",
        f"Judgement B3 against the V1 candidate {st['cand'][:12]} (served {st['prev'][:12]})", cwd=wt)
    run([sys.executable, "scripts/notice_signing_list.py", "--out-md", str(work / "signing_list.md"),
         "--out-json", str(work / "signing_list.json")], cwd=wt)
    rd = json.loads((work / "rd2/rederived.json").read_text(encoding="utf-8"))
    audit = json.loads((wt / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / CONFIG).read_text(encoding="utf-8"))
    hold = {r["audit_id"]: "its rendered wording carries a defect: " + "; ".join(r["judgements"][-1]["defects"])[:300]
            for r in audit["notices"] if (r.get("judgements") or [{}])[-1].get("defects")}
    ruling = {k: v for k, v in (cfg.get("ruling_notices") or {}).items()
              if any(r["audit_id"] == k for r in audit["notices"]) and k not in hold}
    withdrawn = [o["audit_id"] for o in rd["old_41"] if o["fate"] == "GONE"]
    (work / "decisions.json").write_text(json.dumps({"hold": hold, "ruling": ruling, "exclude": {}}, indent=1),
                                         encoding="utf-8")
    shutil.copyfile(ROOT / CONFIG, work / "session_config.json")
    run([sys.executable, "scripts/sign_session_plan.py", "--signing-json", str(work / "signing_list.json"),
         "--decisions", str(work / "decisions.json"), "--config", str(work / "session_config.json"),
         "--withdrawn", ",".join(withdrawn), "--out", "registry/sign_session_plan.json"], cwd=wt)
    branch = st["branch"]
    run([sys.executable, "scripts/v1_final_list.py", "--signing-json", str(work / "signing_list.json"),
         "--decisions", str(work / "decisions.json"), "--branch", branch, "--out", str(work / "FINAL_SIGNING_LIST.md"),
         "--clone", r"C:\mh-sign-v1", "--push-branch", "sign/mahmood-v1"], cwd=wt)
    git("add", "registry/sign_session_plan.json", cwd=wt)
    git("-c", "user.name=lane NR", "-c", "user.email=nr@lanes.invalid", "commit", "-q", "-m",
        "One-sitting plan for the V1 candidate", cwd=wt)
    head = git("rev-parse", "HEAD", cwd=wt)
    print(f"finalized {branch} at {head[:12]}; hold {sorted(hold)}; ruling {sorted(ruling)}; withdrawn {withdrawn}")
    if a.push:
        git("push", "-q", "origin", f"{branch}:refs/heads/{branch}", cwd=wt)
        git("fetch", "-q", "origin", f"refs/heads/{branch}", cwd=wt)
        fetched = git("rev-parse", "FETCH_HEAD", cwd=wt)
        same = run(["git", "diff", "--quiet", head, fetched, "--", "registry/sign_session_plan.json",
                    "registry/notice_adjudication.json"], cwd=wt, check=False).returncode == 0
        print(f"pushed {branch}: remote {fetched[:12]} == local {head[:12]}: {fetched == head}; plan+registry bytes "
              f"equal: {same}")
        if fetched != head or not same:
            return 1
    return 0


def cmd_test_sitting(a) -> int:
    work = Path(a.work).resolve()
    st = json.loads((work / "status.json").read_text(encoding="utf-8"))
    tc = work / "tclone"
    if tc.exists():
        shutil.rmtree(tc)
    git("clone", "-q", "--filter=blob:none", "--no-checkout", "--branch", st["branch"], REPO_URL, str(tc))
    git("sparse-checkout", "set", "--no-cone", *SPARSE, cwd=tc)
    git("checkout", "-q", st["branch"], cwd=tc)
    git("switch", "-q", "-c", "test/sign-session", cwd=tc)
    plan = json.loads((tc / "registry/sign_session_plan.json").read_text(encoding="utf-8"))
    ans = ["TEST sitting on the V1 sign branch"]
    for i in plan["items"]:
        ans += ([""] if i["kind"] == "info" else ["y", "", "y"] if i["kind"] == "ruling" else ["y", ""])
    ans.append("y")
    p = subprocess.run([sys.executable, "scripts/sign_session.py", "--plan", "registry/sign_session_plan.json",
                        "--by", "TEST-NR-LANE", "--push-branch", "test/sign-session", "--push-remote", str(ROOT),
                        "--test"], cwd=tc, input="\n".join(ans) + "\n", capture_output=True, text=True, env=ENV)
    log = p.stdout + p.stderr
    (work / "test_sitting.log").write_text(log, encoding="utf-8")
    keep = [ln for ln in log.splitlines() if any(k in ln for k in ("# SECTION", "Signed notices", "HEAD:", "PUSHED",
                                                                   "PUSH NOT", "NOT SIGNED", "NOT RECORDED"))]
    print("\n".join(keep))
    git("update-ref", "-d", "refs/heads/test/sign-session", check=False)
    shutil.rmtree(tc, ignore_errors=True)
    return p.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--cand", required=True); p.add_argument("--prev"); p.add_argument("--work", required=True)
    p.add_argument("--branch")
    p.set_defaults(fn=cmd_prepare)
    d = sub.add_parser("_draft")
    d.add_argument("--work", required=True); d.add_argument("--prev", required=True); d.add_argument("--cand", required=True)
    d.set_defaults(fn=cmd_draft)
    f = sub.add_parser("finalize")
    f.add_argument("--work", required=True); f.add_argument("--judged-by", required=True)
    f.add_argument("--push", action="store_true")
    f.set_defaults(fn=cmd_finalize)
    t = sub.add_parser("test-sitting")
    t.add_argument("--work", required=True)
    t.set_defaults(fn=cmd_test_sitting)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
