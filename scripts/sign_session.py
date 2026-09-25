"""ONE sitting: Mahmood reads and signs, item by item, then pushes once. Run it YOURSELF in your signing clone.

  python scripts/sign_session.py --plan PLAN.json --by "Mahmood" --push-branch sign/mahmood-v1

For every item in the plan (built by scripts/sign_session_plan.py) it shows the plain before -> after, then asks:
  y  sign / accept this item        n  skip it (nothing written)        r  read the full notice (sign_walk)
  q  stop here (what you signed so far is kept and can still be pushed)
Nothing is ever signed without your explicit "y" for that item. You are asked ONCE, in your own words, how these
items reached you (how_it_reached_the_reviewer); press Enter at any item to reuse it or type a new one.

  notice  signed with scripts/countersign_result_change.py sign --expect-digest ... --judgement ... (the same guarded
          command as the list): it refuses, writing nothing, if the notice's hash or version anchor has moved.
          After each signature the ledger BYTES are re-read to confirm it is there (never an exit code alone).
  bundle  the GLP-1 bundle sha256 is recomputed from the committed bound files first; a stale bundle refuses.
          Your signature is recorded in signatures/GLP1_MACE_FLOW_ELIXA.json with the request's own line
          "SIGNED-BY: ... BUNDLE: ... DATE: ...".
  ruling  your yes/no and your words are recorded in signatures/RULINGS.json; a ruling is never a signature.
At the end: one commit, then scripts/verify_notice_signatures.py on that commit, then -- only after a final "y" --
git push. The push is proven by comparing the remote branch's sha and the pushed ledger's bytes with yours.

--test (for rehearsals ONLY): --by must start with "TEST-", the name Mahmood is refused, and --push-remote must
name a local repository; nothing test-signed can reach GitHub from this script.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import countersign_result_change as cli  # noqa: E402
from scripts import sign_session_plan as planmod  # noqa: E402

LEDGER = "docs/result_changes.json"


def git(*a: str, check=True) -> str:
    p = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit(f"refused: git {' '.join(a)}: {p.stderr.strip()}")
    return p.stdout.strip()


def ask(prompt: str, allowed: str) -> str:
    while True:
        try:
            a = input(prompt).strip().lower()
        except EOFError:
            raise SystemExit("stopped: no more input (nothing further signed)")
        if a in allowed:
            return a
        print(f"  please answer one of: {', '.join(allowed)}")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def signature_in_ledger(item: dict, by: str) -> bool:
    n = json.loads((ROOT / LEDGER).read_text(encoding="utf-8"))["notices"][item["ledger_index"]]
    s = n.get("reviewer_countersignature") or {}
    return (s.get("by") == by and s.get("rendered_sha256") == item["expect_digest"]
            and s.get("judgement_id") == item["judgement"] and bool(str(s.get("how_it_reached_the_reviewer")).strip()))


def record(path: str, entry: dict) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"records": []}
    data["records"].append(entry)
    p.write_bytes((json.dumps(data, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", required=True)
    ap.add_argument("--by", required=True, help="your name, exactly as it should appear on each signature")
    ap.add_argument("--push-branch", required=True)
    ap.add_argument("--push-remote", default="origin")
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args(argv)
    if args.test:
        if not args.by.startswith("TEST-") or "mahmood" in args.by.lower():
            raise SystemExit("refused: --test signs only as a TEST- identity, never as Mahmood")
        if args.push_remote == "origin" or "github.com" in git("remote", "get-url", args.push_remote, check=False):
            raise SystemExit("refused: --test pushes only to a local repository, never to GitHub")
    elif args.by.startswith("TEST-"):
        raise SystemExit("refused: a TEST- identity is for --test rehearsals only")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("refused: this clone has uncommitted changes; start from a clean checkout of the sign branch")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != args.push_branch:
        raise SystemExit(f"refused: you are on {branch!r}; run `git switch -c {args.push_branch}` first")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    items = plan["items"]
    print(f"\n{len(items)} items. Nothing is signed without your 'y'. "
          f"{len(plan.get('held_not_in_session') or {})} notices are held and not in this session.\n")
    default_basis = ""
    while not default_basis:
        default_basis = input("First, in your own words: how did these items reach you, and what did you read?\n> ").strip()
    done = {"notice": [], "bundle": [], "ruling": [], "skipped": [], "refused": []}
    for k, it in enumerate(items, 1):
        print("\n" + "=" * 78 + f"\n[{k}/{len(items)}] {it['kind'].upper()} {it['id']}: {it['label']}\n")
        print(it.get("plain") or "\n".join("- " + line for line in it.get("lines", [])) or it.get("question", ""))
        if it["kind"] == "notice":
            print(f"- Hash: {it['expect_digest']}\n- Version anchor: judgement {it['judgement']}")
        elif it["kind"] == "bundle":
            print(f"- Bundle sha256: {it['bundle_sha256']}")
        else:
            print(f"- If yes: {it['if_yes']}\n- If no: {it['if_no']}")
        while True:
            a = ask("\nSign/accept this item? [y]es / [n]o, skip / [r]ead full / [q]uit: ", ("y", "n", "r", "q"))
            if a == "r" and it["kind"] == "notice":
                subprocess.run([sys.executable, "scripts/sign_walk.py", "--notice", it["id"]], cwd=ROOT)
                continue
            if a == "r":
                print("(the full text is named above; open it, then answer)")
                continue
            break
        if a == "q":
            print("Stopping. What you signed so far is kept.")
            break
        if a == "n":
            done["skipped"].append(it["id"])
            continue
        typed = input("How did this one reach you? [Enter = your words above]\n> ").strip()
        basis = typed or default_basis
        if it["kind"] == "notice":
            proc = subprocess.run([sys.executable, "scripts/countersign_result_change.py", "sign", it["slug"],
                                   it["outcome"], "--notice-index", str(it["ledger_index"]), "--expect-digest",
                                   it["expect_digest"], "--by", args.by, "--judgement", it["judgement"],
                                   "--basis", basis], cwd=ROOT, capture_output=True, text=True)
            if signature_in_ledger(it, args.by):
                done["notice"].append(it["id"])
                print(f"  SIGNED (confirmed in the ledger bytes): {it['id']}")
            else:
                done["refused"].append(it["id"])
                print(f"  NOT SIGNED -- the command refused: {(proc.stderr or proc.stdout).strip()[:400]}")
        elif it["kind"] == "bundle":
            bundle, _ = planmod.glp1_bundle(it["source_commit"])
            if bundle != it["bundle_sha256"]:
                done["refused"].append(it["id"])
                print(f"  NOT RECORDED -- the bound bytes now hash to {bundle}, not {it['bundle_sha256']}")
                continue
            when = now()
            record(it["record_path"], {"SIGNED-BY": args.by, "BUNDLE": bundle, "DATE": when,
                                       "line": f"SIGNED-BY: {args.by}  BUNDLE: {bundle}  DATE: {when[:10]}",
                                       "request_commit": it["source_commit"], "how_it_reached_the_reviewer": basis})
            done["bundle"].append(it["id"])
            print(f"  RECORDED: {it['record_path']}")
        else:
            decision = ask(f"  Your ruling on {it['id']}: accept (y) or decline (n)? ", ("y", "n"))
            record(it["record_path"], {"ruling": it["id"], "question": it["question"],
                                       "decision": "ACCEPTED" if decision == "y" else "DECLINED", "by": args.by,
                                       "when_utc": now(), "how_it_reached_the_reviewer": basis})
            done["ruling"].append(it["id"])
            print(f"  RECORDED: {'ACCEPTED' if decision == 'y' else 'DECLINED'}")
    print("\n" + "=" * 78)
    print(f"Signed notices: {len(done['notice'])}; bundle: {len(done['bundle'])}; rulings: {len(done['ruling'])}; "
          f"skipped: {len(done['skipped'])}; refused by a guard: {len(done['refused'])} {done['refused']}")
    changed = git("status", "--porcelain")
    if not changed:
        print("Nothing was written, so there is nothing to push.")
        return 0
    git("add", LEDGER)
    if (ROOT / "signatures").exists():
        git("add", "--sparse", "signatures")  # a sparse clone may not list signatures/ in its patterns
    git("-c", f"user.name={args.by}", "commit", "-q", "-m",
        f"Countersignatures by {args.by}: {len(done['notice'])} notices, {len(done['bundle'])} bundle, "
        f"{len(done['ruling'])} rulings (scripts/sign_session.py)")
    head = git("rev-parse", "HEAD")
    v = subprocess.run([sys.executable, "scripts/verify_notice_signatures.py", "--ref", "HEAD", "--base", "HEAD~1"],
                       cwd=ROOT, capture_output=True, text=True)
    print(v.stdout.strip())
    if ask(f"\nPush {head[:12]} to {args.push_remote} {args.push_branch}? [y/n]: ", ("y", "n")) != "y":
        print("Not pushed. Your commit is kept; push later with: git push -u "
              f"{args.push_remote} {args.push_branch}")
        return 0
    git("push", "-u", args.push_remote, f"HEAD:refs/heads/{args.push_branch}")
    remote_sha = git("ls-remote", args.push_remote, f"refs/heads/{args.push_branch}").split()[0]
    git("fetch", "-q", args.push_remote, f"refs/heads/{args.push_branch}")
    fetched = hashlib.sha256(subprocess.run(["git", "show", f"FETCH_HEAD:{LEDGER}"], cwd=ROOT,
                                            capture_output=True).stdout).hexdigest()
    # compare COMMITTED bytes (git stores the ledger with LF; the working copy may carry CRLF on Windows)
    mine = hashlib.sha256(subprocess.run(["git", "show", f"{head}:{LEDGER}"], cwd=ROOT,
                                         capture_output=True).stdout).hexdigest()
    if remote_sha == head and fetched == mine:
        print(f"PUSHED and proven: {args.push_branch} = {head[:12]} on {args.push_remote}; the pushed ledger's "
              f"bytes equal your commit's (sha256 {mine[:12]}). Say 'pushed'.")
        return 0
    print(f"PUSH NOT PROVEN: remote {remote_sha[:12]} vs yours {head[:12]}; ledger {fetched[:12]} vs {mine[:12]}")
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
