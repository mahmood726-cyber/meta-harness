"""Codex as the reviewer of a lane's merged range (Mahmood 5 Oct night: "codex as a reviewer of every lane PR before
you merge"). The CODE diff of base..head (scripts/, harness/, reproducible_ai/, kgap/ .py files; never data, never held
text) is sent in groups as RECORDED calls (reproducible_ai.model_call_live: licence guard and private-text redaction
apply). Each finding needs a CONCRETE failing input; a finding is a PROPOSAL, accepted only once it is reproduced here.

    python scripts/pr_codex_review.py --run --name <tag> --base <sha> --head <sha>   (concurrency 5)
    python scripts/pr_codex_review.py --run --reader agy --name <tag>-agy --base <sha> --head <sha>
        the same code-only groups read by agy routed to Gemini (second model family; recorded by mcl.agy_call)
    python scripts/pr_codex_review.py --show [--name <tag>]
Writes registry/model_proposals/pr_codex_review.json ({name: {runs, findings}}).
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
import g1_codex_review as base_review  # noqa: E402

PROP = os.path.join(ROOT, "registry", "model_proposals", "pr_codex_review.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
CODE_DIRS = ("scripts/", "harness/", "reproducible_ai/", "kgap/")
GROUP_CHARS = 60000


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout.decode("utf-8", "replace")


def groups(base, head):
    """[(group name, [(file, diff text)])]: every changed code file's diff, packed into groups of <= GROUP_CHARS."""
    files = [f for f in _git("diff", "--name-only", f"{base}..{head}").split()
             if f.endswith(".py") and f.startswith(CODE_DIRS) and not f.startswith("docs/")]
    out, cur, size = [], [], 0
    for f in files:
        d = _git("diff", f"{base}..{head}", "--", f)
        if not d.strip():
            continue
        d = d if len(d) <= GROUP_CHARS else d[:GROUP_CHARS] + "\n[... diff truncated; the reviewer saw the first part only]\n"
        if cur and size + len(d) > GROUP_CHARS:
            out.append(cur)
            cur, size = [], 0
        cur.append((f, d))
        size += len(d)
    if cur:
        out.append(cur)
    return [(f"g{i + 1}", g) for i, g in enumerate(out)]


def prompt(group):
    parts = [base_review.INSTR, "\nYou are reviewing a DIFF merged from a lane branch (lines starting '+' are new).\n"]
    for f, d in group:
        parts.append(f"\n=== DIFF {f} ===\n{d}\n")
    return "".join(parts).encode("utf-8")


def main(argv):
    name = argv[argv.index("--name") + 1] if "--name" in argv else None
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {}
    if "--run" in argv:
        base, head = argv[argv.index("--base") + 1], argv[argv.index("--head") + 1]
        reader = argv[argv.index("--reader") + 1] if "--reader" in argv else "codex"
        if reader not in ("codex", "agy"):
            raise SystemExit(f"unknown reader {reader}")
        gs = groups(base, head)
        entry = data.setdefault(name, {"base": base, "head": head, "runs": {}, "verdicts": {}})
        entry.update(base=base, head=head)

        def one(g):
            gname, files = g
            p = prompt(files)
            caller = {"file": "scripts/pr_codex_review.py", "line": "main", "lane": "captain",
                      "purpose": f"{reader} review of merged range {name} {base[:9]}..{head[:9]} ({gname})"}
            digests = [{"ref": f"git diff {base[:12]}..{head[:12]} -- {f}",
                        "sha256": hashlib.sha256(d.encode("utf-8")).hexdigest(), "what": "reviewed diff"} for f, d in files]
            if reader == "agy":
                rec = mcl.agy_call(p, schema=base_review.SCHEMA, caller=caller, input_digests=digests, timeout_s=1800)
            else:
                rec = mcl.call(p, schema=base_review.SCHEMA, model=base_review.MODEL, effort=base_review.EFFORT,
                               caller=caller, input_digests=digests, timeout_s=1800)
            ms.write_record(rec, REC_DIR)
            return gname, {"record_id": rec["record_id"], "state": rec["state"], "reader": reader,
                           "files": [f for f, _ in files],
                           "prompt_sha256": hashlib.sha256(p).hexdigest()}
        with cf.ThreadPoolExecutor(max_workers=5 if reader == "codex" else 2) as ex:
            for gname, r in ex.map(one, gs):
                entry["runs"][gname] = r
                print(name, gname, r["state"], r["record_id"], flush=True)
    for nm, entry in data.items():
        if name and nm != name:
            continue
        entry["findings"] = []
        for gname, r in entry["runs"].items():
            if r["state"] != "RAN_OK":
                continue
            raw = ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8")
            try:
                resp = json.loads(raw)
            except ValueError:
                # a reply outside the schema (agy sometimes answers in markdown) is kept WHOLE as one finding to
                # reproduce by hand -- never dropped, never read as "no findings"
                resp = {"findings": [{"severity": "UNSTRUCTURED", "file": "-", "function": "-", "claim": raw,
                                      "failing_input": "(see claim)", "expected": "-", "actual": "-"}]}
            if isinstance(resp, list):                 # agy may answer with the findings list itself
                resp = {"findings": resp}
            for i, f in enumerate(resp.get("findings") or []):
                f = f if isinstance(f, dict) else {"severity": "UNSTRUCTURED", "claim": str(f)}
                for k in ("severity", "file", "function", "claim", "failing_input", "expected", "actual"):
                    f.setdefault(k, "-")
                fid = f"{nm}:{gname}#{i + 1}"
                entry["findings"].append(dict(f, id=fid, record_id=r["record_id"], verdict=entry["verdicts"].get(fid)))
        for f in entry["findings"]:
            print(f"[{f['id']}] {f['severity']} {f['file']}::{f['function']} -- {f['claim'][:300]}\n    input: "
                  f"{f['failing_input'][:300]}\n    expected: {f['expected'][:160]} | actual: {f['actual'][:160]}\n")
    with open(PROP, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
