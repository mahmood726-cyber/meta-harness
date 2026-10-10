"""agy (Gemini) as the SECOND, adversarial reviewer of each codex-implemented class patch. Recorded through
reproducible_ai.model_call_live.agy_call (chunked transport with canaries; licence guard; record + lane log), run from the
sparse worktree C:/mh-lanes/wt-agy. The prompt carries CODE ONLY (the patch + the class rule) -- no held text."""
import concurrent.futures as cf
import json
import os
import sys
from pathlib import Path

WT = Path("C:/mh-lanes/wt-agy")
sys.path.insert(0, str(WT))
from reproducible_ai import model_call_live as mcl, model_source as ms  # noqa: E402

EV = Path("C:/mh-lanes/tmp-pva/pva-1010-evidence/codex_classes")
CLASSES = json.loads((EV / "classes.json").read_text(encoding="utf-8"))
OUT = Path("C:/mh-lanes/tmp-pva/agy_reviews")
OUT.mkdir(exist_ok=True)
SCHEMA = {"type": "object", "required": ["verdict", "findings", "parts_read"],
          "properties": {"verdict": {"type": "string", "enum": ["ACCEPT", "ACCEPT_WITH_CHANGES", "REJECT"]},
                         "findings": {"type": "array", "items": {"type": "object",
                                      "required": ["severity", "file", "issue", "evidence", "fix"],
                                      "properties": {"severity": {"type": "string", "enum": ["P0", "P1", "P2"]},
                                                     "file": {"type": "string"}, "issue": {"type": "string"},
                                                     "evidence": {"type": "string"}, "fix": {"type": "string"}}}},
                         "parts_read": {"type": "array", "items": {"type": "string"}}}}

PROMPT = """You are an adversarial code reviewer. Below is a patch to a reproducible meta-analysis harness that is meant to
fix ONE class of generated-text defect. Find what is WRONG with it. Be concrete: name the file and the changed lines.

Class {cid}: {name}
Rule: {rule}

Check, in this order:
1. Does it fix the GENERATOR so the rule holds for every review, or only the instances seen?
2. Could it change a SERVED NUMBER (an estimate, CI, count, k, trial membership, pooling decision), or add a new number?
   That is not allowed in this patch.
3. Does it say anything the review object does not support (an invented claim, an over-broad rewording)?
4. Does the test's plant really fail on the old code, and does its sweep assert a denominator?
5. Regressions: code paths it breaks, exceptions on missing fields.

Severity: P0 = wrong output served or a number could change; P1 = rule not met for some input; P2 = style or minor.
Verdict ACCEPT only if you find no P0/P1.

Answer with ONE JSON object matching this schema (and nothing else): {schema}

===== THE PATCH =====
{patch}
"""


def review(cid):
    patch = (EV / "impl" / f"{cid}.patch").read_text(encoding="utf-8")
    patch = "\n".join(chunk for chunk in patch.split("diff --git") if "__pycache__" not in chunk.split("\n", 1)[0])
    c = CLASSES[cid]
    prompt = PROMPT.format(cid=cid, name=c["name"], rule=c["rule"], schema=json.dumps(SCHEMA), patch=patch).encode("utf-8")
    rec = mcl.agy_call(prompt, schema=SCHEMA, timeout_s=3600, chunk_chars=60000,
                       caller={"file": "C:/mh-lanes/tmp-pva/agy_patch_review.py", "line": "review", "lane": "pva",
                               "purpose": f"agy adversarial review of codex class patch {cid}"},
                       input_digests=[{"ref": f"outputs/pva-2026-10-10/codex_classes/impl/{cid}.patch",
                                       "sha256": __import__("hashlib").sha256(patch.encode()).hexdigest(),
                                       "what": "codex-implemented class patch (code only)"}])
    path = ms.write_record(rec, WT / ms.RECORD_DIR)
    res = {"class": cid, "record_id": rec["record_id"], "state": rec["state"], "error": rec.get("error")}
    if rec["state"] == "RAN_OK":
        import re
        txt = ms.replay(ms.load_record(path)).decode("utf-8")
        m = re.search(r"\{.*\}", txt, re.S)
        try:
            res["review"] = json.loads(m.group(0) if m else txt)
        except ValueError as e:
            res["parse_error"] = str(e)
    (OUT / f"{cid}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


if __name__ == "__main__":
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(review, sys.argv[1:]):
            rv = r.get("review") or {}
            print(r["class"], r["state"], rv.get("verdict"), len(rv.get("findings") or []), (r.get("error") or "")[:160], flush=True)
