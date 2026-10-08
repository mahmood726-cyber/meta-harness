"""Cross-vendor (codex) adversarial review of this lane's new code, as RECORDED calls (reproducible_ai.model_call_live).
Each group of files is sent inline (the diff since a base commit, plus the full current text of the key functions) and
the reviewer returns findings, each with a CONCRETE failing input. A finding is a PROPOSAL: it is accepted only after
it is reproduced on that input in this repository (scripts/g1_codex_review.py --show lists them for that).

    python scripts/g1_codex_review.py --run [--base <sha>]   (recorded calls, concurrency 3)
    python scripts/g1_codex_review.py --show                 (replay the records; print the findings)
Writes registry/model_proposals/g1_codex_review.json.
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

PROP = os.path.join(ROOT, "registry", "model_proposals", "g1_codex_review.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT = "gpt-6-astra", "high"
BASE = "46cc6a7f"          # the parent of this lane's first commit (85a45966)
GROUPS = {
    "toci_match": ["g1/tocilizumab.py"],
    "cascade_and_meta2": ["scripts/g1_toci_cascade.py", "scripts/g1_toci_meta2_forest.py"],
    "exclusion_audit_and_screen": ["scripts/g1_exclusion_audit_tracker.py", "harness/screen.py"],
}
SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["findings"],
    "properties": {"findings": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["file", "function", "severity", "claim", "failing_input", "expected", "actual"],
        "properties": {k: {"type": "string"} for k in ("file", "function", "severity", "claim", "failing_input",
                                                        "expected", "actual")}}}},
}
INSTR = """You are an adversarial reviewer of research-harness code that extracts per-arm death counts from clinical-trial
reports and registries, binds papers to trials, classifies screening exclusions, and screens records for RCT status.
Correctness standards: a number must come from held text by rule; a percentage or Kaplan-Meier estimate is never a
count; denominator kinds (randomised / analysed / safety) are never mixed; a paper binds to a trial only on its own
evidence; a gate that can only pass is a defect; silent fallbacks that turn failure into "absent" are defects.

Review the code below. Report only REAL defects you can demonstrate: for each, give the file, the function, a severity
(P0 wrong number reaches a result / P1 wrong classification or binding / P2 robustness), the claim, a CONCRETE failing
input (an exact string, record or call that a reader can run), the expected output, and the actual output the code
gives. Do not report style. Do not speculate without an input. If you find nothing real, return an empty list.
"""


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8", "replace")


def prompt(group, base):
    parts = [INSTR]
    for f in GROUPS[group]:
        diff = _git("diff", f"{base}..HEAD", "--", f)
        src = open(os.path.join(ROOT, f), encoding="utf-8").read()
        body = src if len(src) < 60000 else diff
        parts.append(f"\n=== FILE {f} ({'full current text' if body is src else 'diff since ' + base}) ===\n{body}\n")
    return "".join(parts).encode("utf-8")


def main(argv):
    base = argv[argv.index("--base") + 1] if "--base" in argv else BASE
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {"runs": {}}
    if "--run" in argv:
        def one(gname):
            p = prompt(gname, base)
            rec = mcl.call(p, schema=SCHEMA, model=MODEL, effort=EFFORT,
                           caller={"file": "scripts/g1_codex_review.py", "line": "main",
                                   "purpose": f"G1 lane cross-vendor code review: {gname} (g1/tocilizumab lane)"},
                           input_digests=[{"ref": f, "sha256": hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest(),
                                           "what": "reviewed file"} for f in GROUPS[gname]],
                           timeout_s=1800)
            ms.write_record(rec, REC_DIR)
            return gname, {"record_id": rec["record_id"], "state": rec["state"], "base": base,
                           "head": _git("rev-parse", "HEAD").strip(), "prompt_sha256": hashlib.sha256(p).hexdigest()}
        with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))) as ex:
            for gname, r in ex.map(one, list(GROUPS)):
                data["runs"][gname] = r
                print(gname, r["state"], r["record_id"], flush=True)
    out = {"runs": data["runs"], "findings": []}
    for gname, r in data["runs"].items():
        if r["state"] != "RAN_OK":
            continue
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
        for i, f in enumerate(resp.get("findings") or []):
            out["findings"].append(dict(f, group=gname, id=f"{gname}#{i + 1}", record_id=r["record_id"],
                                        verdict=(data.get("verdicts") or {}).get(f"{gname}#{i + 1}")))
    out["verdicts"] = data.get("verdicts") or {}
    json.dump(out, open(PROP, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for f in out["findings"]:
        print(f"[{f['id']}] {f['severity']} {f['file']}::{f['function']} -- {f['claim'][:300]}\n    input: "
              f"{f['failing_input'][:300]}\n    expected: {f['expected'][:160]} | actual: {f['actual'][:160]}"
              f"\n    verdict: {f['verdict']}\n")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
