"""Recorded, blind review of the NI policy by codex (OpenAI) and agy (Gemini) BEFORE its pre-registration commit.
Each reviewer sees the same prompt (policy + code + tests; no trial text) and not the other's answer.

    python scripts/rob2_ni_review.py   -> outputs/robgrade/ni_policy_review/{codex,agy}.json (+ records in evidence/)
"""
import concurrent.futures as cf
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

FILES = ["outputs/robgrade/NI_POLICY.md", "robgrade/rob2_formal.py", "robgrade/ni_policy.py", "scripts/rob2_ni_score.py",
         "scripts/rob2_calibrate.py", "tests/test_rob2_ni_policy.py"]
ROUND = next((int(a[7:]) for a in sys.argv if a.startswith("--round")), 1)
OUT = os.path.join(ROOT, "outputs", "robgrade", "ni_policy_review", *([f"round{ROUND}"] if ROUND > 1 else []))
# ONE level, as the store contract requires (scripts/provenance_census.held_record_ids reads evidence/model_calls/*/mc-*.json):
# the round is in each record's caller purpose, not in a sub-folder
REC = os.path.join(ROOT, "evidence", "model_calls", "robgrade_ni")
if ROUND > 1:
    FILES = FILES + ["tests/test_rob2_algorithm_guidance.py", "outputs/robgrade/ni_policy_review/RESPONSES.md"]

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdict", "findings"], "properties": {
    "verdict": {"type": "string", "enum": ["ACCEPT", "REVISE"]},
    "findings": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                 "required": ["severity", "where", "claim", "guidance_basis", "failing_test"],
                 "properties": {"severity": {"type": "string", "enum": ["BLOCKER", "MAJOR", "MINOR"]},
                                "where": {"type": "string"}, "claim": {"type": "string"},
                                "guidance_basis": {"type": "string"}, "failing_test": {"type": "string"}}}}}}

INSTR = """You are an independent methods reviewer for a Cochrane RoB 2 implementation. Review the "No information" (NI)
policy below, and its code and tests, against the Cochrane Handbook (chapter 8) and the RoB 2 guidance (Sterne et al.,
BMJ 2019; the riskofbias.info full guidance and algorithms). The guidance decides every point; where they disagree,
say so.

Check in particular:
1. The Table 1 lower-risk response used for each signalling question (FAVOURABLE), and the exclusion of 3.2.
2. That the domain algorithms (judge_d1..judge_d5) and overall() match the RoB 2 algorithms, NI mappings included --
   a wrong algorithm makes every NI-driven label wrong.
3. Whether "NI-driven = resolving the domain's NI answers to the lower-risk response gives a less severe judgement" is
   a faithful reading of "a judgement driven mainly by NI answers", and its edge cases (branch questions, NA, a domain
   where NI both raises and could lower severity, the overall).
4. Whether the scoring (all / excluding NI-driven / NI-driven only) is pre-registered soundly, and any way it could
   mislead.
5. Whether each test's expected value is right by the guidance (they claim to be hand-derived).

Report only real defects. For each: severity (BLOCKER = wrong by the guidance; MAJOR = misleading or untested; MINOR),
where (file:function), the claim, its guidance basis, and a failing test that would expose it (input -> expected).
Reply ONLY with JSON matching schema.json: {"verdict": "ACCEPT" | "REVISE", "findings": [...]}.
"""


ROUND2 = """
REVIEW OF A REVISION. This version follows earlier review rounds (blind, two reviewers). RESPONSES.md answers
every earlier finding: ACCEPTED (fixed, with a test) or DECLINED with the RoB 2 full-guidance table row that decides
it. Check above all: (a) each fix is right and its test's expected value matches the guidance tables; (b) each DECLINED
finding -- if the guidance supports the finding rather than the decline, report it as a BLOCKER citing the table row;
(c) anything new the revision broke. Report only real defects.
""" + ("""Report at most 8 findings, the most serious first, each field under 500 characters.
""" if ROUND >= 5 else "")


def prompt():
    parts = [INSTR] + ([ROUND2] if ROUND > 1 else [])
    for f in FILES:
        parts.append(f"\n\n===== FILE {f} =====\n" + open(os.path.join(ROOT, f), encoding="utf-8").read())
    return "".join(parts).encode("utf-8")


def digests():
    return [{"ref": f, "sha256": hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest(),
             "what": "reviewed file"} for f in FILES]


def run(who, p):
    caller = {"file": "scripts/rob2_ni_review.py", "line": f"run:{who}", "lane": rd.LANE,
              "purpose": f"blind review (round {ROUND}) of the RoB 2 NI policy ({who}) before pre-registration"}
    if who == "codex":
        rec = mcl.call(p, schema=SCHEMA, model=rd.CODEX_MODEL, effort="high", caller=caller, input_digests=digests(),
                       timeout_s=1800)
    else:
        rec = mcl.agy_call(p, schema=SCHEMA, caller=caller, input_digests=digests(), timeout_s=1800)
        if rec["state"] != "RAN_OK" and ROUND >= 5:
            # agy's client stops with status ERROR after ~100k thinking tokens on some runs (rounds 2 and 4): one retry,
            # BOTH attempts recorded
            ms.write_record(rec, REC)
            rec = mcl.agy_call(p, schema=SCHEMA, caller=dict(caller, line="run:agy:retry"), input_digests=digests(),
                               timeout_s=1800)
    ms.write_record(rec, REC)
    return rec


def _parse(text):
    """The JSON object in a reply. agy may put a line of prose before it; the record keeps the raw bytes either way."""
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def from_records():
    """Re-derive the review outputs from the existing records (replay; no model call)."""
    import glob
    recs = {}
    for f in sorted(glob.glob(os.path.join(REC, "mc-*.json"))):
        r = json.load(open(f, encoding="utf-8"))
        purpose = r["caller"].get("purpose", "")
        if (f"(round {ROUND})" in purpose) != (ROUND > 1) or (ROUND == 1 and "(round " in purpose):
            continue                                       # round 1's purpose names no round
        who = "agy" if r["client"]["name"].startswith("agy") else "codex"
        if who not in recs or recs[who]["state"] != "RAN_OK":          # a retry: the successful attempt wins
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
