"""Recorded, blind review of the contextual-answer rule by codex (OpenAI) and agy (Gemini) BEFORE its pre-registration
commit. The same prompt (policy + code + tests; no trial text) goes to both; neither sees the other.

    python scripts/rob2_ctx_review.py [--roundN] [--replay]   -> outputs/robgrade/ctx_review/[roundN/]{codex,agy}.json
Records: evidence/model_calls/robgrade_ctx/ (one level -- the store contract); the round is in the caller's purpose.
"""
import concurrent.futures as cf
import glob
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
import rob2_dual as rd  # noqa: E402

ROUND = next((int(a[7:]) for a in sys.argv if a.startswith("--round")), 1)
FILES = ["outputs/robgrade/CONTEXTUAL_POLICY.md", "robgrade/contextual.py", "scripts/rob2_contextual.py",
         "scripts/rob2_ctx_score.py", "tests/test_rob2_contextual.py", "robgrade/rob2_tab.py", "tests/test_rob2_tab.py"]
if ROUND > 1:
    FILES.append("outputs/robgrade/ctx_review/RESPONSES.md")
OUT = os.path.join(ROOT, "outputs", "robgrade", "ctx_review", *([f"round{ROUND}"] if ROUND > 1 else []))
REC = os.path.join(ROOT, "evidence", "model_calls", "robgrade_ctx")

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdict", "findings"], "properties": {
    "verdict": {"type": "string", "enum": ["ACCEPT", "REVISE"]},
    "findings": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                 "required": ["severity", "where", "claim", "guidance_basis", "failing_test"],
                 "properties": {"severity": {"type": "string", "enum": ["BLOCKER", "MAJOR", "MINOR"]},
                                "where": {"type": "string"}, "claim": {"type": "string"},
                                "guidance_basis": {"type": "string"}, "failing_test": {"type": "string"}}}}}}

INSTR = """You are an independent methods reviewer for a Cochrane RoB 2 implementation. Review the rule below that
allows documented contextual "probably yes / probably no" answers (Cochrane Handbook 8.2.3), and its code and tests.
The Handbook and the RoB 2 guidance decide every point. The decision being implemented: allow documented contextual
PY/PN answers per Handbook 8.2.3; each carries its quoted context and is labelled as contextual, never silent; NI
remains where no context exists; the rule is pre-registered before re-scoring.

Check in particular:
1. Faithfulness to Handbook 8.2.3: when context justifies PY/PN, and when it must stay NI. Is restricting contextual
   answers to PY/PN (never Y/N) and to questions that are NI right?
2. Leakage and inference risk: can a model answer from memory or from "what trials usually do" and still pass the
   checks? Is the verbatim-quote check enough to tie the answer to its context?
3. Isolation: is the effect really limited to NI -> contextual PY/PN, with every direct answer unchanged? Does the
   scorer enforce that, and the pre-registration?
4. "Never silent": is every contextual answer stored and shown as such?
5. Each test's expected value, by the guidance.
Report only real defects, at most 8, the most serious first, each field under 500 characters. For each: severity
(BLOCKER = wrong by the guidance or unsafe; MAJOR = misleading or untested; MINOR), where (file:function), the claim,
its guidance basis, and a failing test (input -> expected).
Reply ONLY with JSON matching schema.json: {"verdict": "ACCEPT" | "REVISE", "findings": [...]}.
"""
REVISION = """
REVIEW OF A REVISION. This version follows earlier blind review rounds; RESPONSES.md answers every earlier finding:
ACCEPTED (fixed, with a test) or DECLINED with its guidance basis. Check each fix and each decline, and anything the
revision broke.
"""


def prompt():
    parts = [INSTR] + ([REVISION] if ROUND > 1 else [])
    for f in FILES:
        parts.append(f"\n\n===== FILE {f} =====\n" + open(os.path.join(ROOT, f), encoding="utf-8").read())
    return "".join(parts).encode("utf-8")


def digests():
    return [{"ref": f, "sha256": hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest(),
             "what": "reviewed file"} for f in FILES]


def purpose(who):
    return f"blind review (round {ROUND}) of the RoB 2 contextual-answer rule ({who}) before pre-registration"


def run(who, p):
    caller = {"file": "scripts/rob2_ctx_review.py", "line": f"run:{who}", "lane": rd.LANE, "purpose": purpose(who)}
    if who == "codex":
        rec = mcl.call(p, schema=SCHEMA, model=rd.CODEX_MODEL, effort="high", caller=caller, input_digests=digests(),
                       timeout_s=1800)
    else:
        rec = mcl.agy_call(p, schema=SCHEMA, caller=caller, input_digests=digests(), timeout_s=1800)
        if rec["state"] != "RAN_OK":       # agy's client can stop after ~100k thinking tokens: one retry, both recorded
            ms.write_record(rec, REC)
            rec = mcl.agy_call(p, schema=SCHEMA, caller=dict(caller, line="run:agy:retry"), input_digests=digests(),
                               timeout_s=1800)
    ms.write_record(rec, REC)
    return rec


def _parse(text):
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def from_records():
    recs = {}
    for f in sorted(glob.glob(os.path.join(REC, "mc-*.json"))):
        r = json.load(open(f, encoding="utf-8"))
        if f"(round {ROUND})" not in r["caller"].get("purpose", ""):
            continue
        who = "agy" if r["client"]["name"].startswith("agy") else "codex"
        if who not in recs or recs[who]["state"] != "RAN_OK":
            recs[who] = r
    return recs


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--replay" in sys.argv:
        recs = from_records()
    else:
        p = prompt()
        with cf.ThreadPoolExecutor(2) as ex:
            recs = dict(zip(("codex", "agy"), ex.map(lambda w: run(w, p), ("codex", "agy"))))
    for who, rec in recs.items():
        body = _parse(ms.replay(rec).decode("utf-8")) if rec["state"] == "RAN_OK" else {"error": rec.get("error")}
        with open(os.path.join(OUT, f"{who}.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"record_id": rec["record_id"], "state": rec["state"], **body}, fh, indent=1, ensure_ascii=False)
        print(who, rec["state"], body.get("verdict"), len(body.get("findings") or []))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
