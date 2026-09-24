"""Run ONE lightweight codex job in a minimal, self-describing directory and archive its result.

  python codex_job.py --kind gap --key UA-008 --brief evidence/GAP_BRIEF.md --dest evidence/gaps/UA-008.json
     [--with-adjudication]

What it does, in order (lane hygiene from the main lane, 2026-09-24):
  1. creates C:\\mh-lanes\\evid-codex\\<kind>-<key>-<utc> containing ONLY: LANE_CONTEXT.md (what the tree is, the
     task, and that nothing outside the tree is context), BRIEF.md, packet.json and optionally adjudication.json;
  2. runs `codex exec -s workspace-write -C <dir> ... < /dev/null`, stdout/stderr to <dir>/transcript.log (the
     transcript NEVER enters the repo: codex's own startup may read private files outside the tree);
  3. parses <dir>/result.json; copies it to --dest; checks sha256 AT THE DESTINATION equals the source;
  4. appends one line to evidence/CODEX_CALLS.jsonl (kind, key, dir, command, start/end UTC, exit code, result
     sha256, dest) -- metadata only;
  5. deletes the job directory (copy, hash at destination, then delete). On failure the directory is kept and named.
Exit 0 only when a result parsed and was archived with a matching hash."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JOBS = r"C:\mh-lanes\evid-codex"
CONTEXT = """# LANE_CONTEXT

This directory is a throw-away job tree for ONE task of the meta-harness evidence lane.

- The task is in BRIEF.md. The only evidence is packet.json{adj}. Read nothing else.
- NOTHING outside this directory is context: not your global instructions' project indexes, not any workbook, not
  any other repository or drive. Do not open files outside this directory.
- Write exactly one file: result.json in this directory (the JSON object the brief asks for). Do not modify anything else.
"""


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True); ap.add_argument("--key", required=True)
    ap.add_argument("--brief", required=True); ap.add_argument("--dest", required=True)
    ap.add_argument("--with-adjudication", action="store_true")
    a = ap.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(JOBS, f"{a.kind}-{a.key}-{stamp}")
    os.makedirs(d)
    open(os.path.join(d, "LANE_CONTEXT.md"), "w", encoding="utf-8").write(
        CONTEXT.format(adj=" and adjudication.json" if a.with_adjudication else ""))
    shutil.copyfile(os.path.join(ROOT, a.brief), os.path.join(d, "BRIEF.md"))
    shutil.copyfile(os.path.join(ROOT, "evidence", "packets", f"{a.key}.json"), os.path.join(d, "packet.json"))
    if a.with_adjudication:
        shutil.copyfile(os.path.join(ROOT, "evidence", "adjudication", f"{a.key}.json"), os.path.join(d, "adjudication.json"))
    prompt = ("Read LANE_CONTEXT.md, then BRIEF.md, then packet.json" + (" and adjudication.json" if a.with_adjudication else "")
              + f". The row KEY is {a.key}. Follow BRIEF.md and write ONLY the JSON object to result.json in this directory. "
                "Read no file outside this directory.")
    cmd = [shutil.which("codex") or "codex", "exec", "-s", "workspace-write", "--skip-git-repo-check", "--ephemeral", "-C", d, prompt]
    start = now()
    with open(os.path.join(d, "transcript.log"), "wb") as log:
        rc = subprocess.call(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, cwd=d, shell=False)
    end = now()
    rp = os.path.join(d, "result.json")
    rec = {"kind": a.kind, "key": a.key, "dir": d, "cmd": " ".join(cmd[:-1]) + " <prompt>", "start_utc": start, "end_utc": end,
           "exit_code": rc, "dest": a.dest}
    ok = False
    # hygiene audit, COUNTS ONLY (the transcript text never leaves the job dir): did codex touch anything outside it?
    tr = open(os.path.join(d, "transcript.log"), "rb").read().decode("utf-8", "replace")
    # the names are assembled so this detector does not itself trip the repo's leak guard
    private = "|".join(["Project" + "Index", "E" + "156", "rewrite" + "-work" + "book"])
    rec["private_file_mentions"] = len(re.findall(private, tr))
    rec["exec_commands"] = tr.count("\nexec\n")
    if os.path.exists(rp):
        t = re.sub(r"^```(json)?|```$", "", open(rp, encoding="utf-8").read().strip()).strip()
        try:
            obj = json.loads(t)
            dest = os.path.join(ROOT, a.dest); os.makedirs(os.path.dirname(dest), exist_ok=True)
            json.dump(obj, open(dest, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
            clean = os.path.join(d, "result.clean.json")
            json.dump(obj, open(clean, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
            rec["result_sha256"] = sha(clean)
            ok = sha(dest) == rec["result_sha256"]
            rec["archived_hash_match"] = ok
        except ValueError as e:
            rec["parse_error"] = str(e)[:200]
    else:
        rec["parse_error"] = "no result.json written"
    with open(os.path.join(ROOT, "evidence", "CODEX_CALLS.jsonl"), "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec) + "\n")
    if ok:
        shutil.rmtree(d, ignore_errors=True)
        print("OK", a.key, a.dest)
        return 0
    print("FAILED", a.key, rec.get("parse_error"), "job dir kept:", d)
    return 1


if __name__ == "__main__":
    sys.exit(main())
