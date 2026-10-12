"""Ask codex (recorded) to PROPOSE typed RoB 2 regex rules from the DEV recall gaps (outputs/robgrade/dev/rule_eval.json).

DEV only: every quote comes from a DEV trial's CC BY / CC0 full text (robgrade/prompt_licence), as the readers quoted it.
A proposal is NOT a rule. A rule enters robgrade/rob2_typed.REGEX_RULES only after it is reviewed and planted (a positive
and a negative test). It must keep DEV precision at 0 disagreements (scripts/rob2_rule_eval.py). TEST
(outputs/robgrade/split.json) is never read here.

    python scripts/rob2_propose_rules.py   -> outputs/robgrade/dev/rule_proposals.json (+ the record in evidence/)
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402
from robgrade import rob2_typed as rt  # noqa: E402
import rob2_dual as rd  # noqa: E402

EVAL = os.path.join(ROOT, "outputs", "robgrade", "dev", "rule_eval.json")
OUT = os.path.join(ROOT, "outputs", "robgrade", "dev", "rule_proposals.json")

# round 2 (2026-10-12): round 1 (record mc-bcba1341c139cdccd11363141aac09ff, rule_proposals.json) proposed 2 rules, each
# anchored start-to-end to ONE DEV sentence: memorising DEV, not a rule. None was accepted.
ROUND2 = r"""
## Feedback on your first proposal (round 2)
Your first answer proposed two rules anchored with \A...\Z to the exact gap sentence. That memorises these reports and
would never fire on another trial. Propose patterns that match the RECURRING PHRASING across reports (they are run with
re.search over one sentence, not a whole-sentence match), still with explicit negation exclusions and bounded gaps.
Consider in particular (outcome-independent):
- 1.3: baseline characteristics / demographic and clinical characteristics were similar / comparable / (generally) well
  balanced between the (treatment) groups.
- 4.3: outcome assessors / adjudicators / cardiologists / committee members who were blinded or unaware of / masked to
  the treatment allocation (assignment) -> N. An existing rule may cover part of this: extend it, do not duplicate it.
- 3.1: follow-up (data) was complete / available for N% of randomised participants, with N >= 95 -> Y.
Say nothing about questions whose answer depends on the outcome (4.1, 4.2, 2.7, 3.2), and give each rule the answer
the gap readers gave for that phrasing.
"""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["rules"], "properties": {"rules": {
    "type": "array", "items": {"type": "object", "additionalProperties": False,
                               "required": ["rule_id", "question", "answer", "pattern", "rationale", "fires_on",
                                            "must_not_fire_on"],
                               "properties": {"rule_id": {"type": "string"}, "question": {"type": "string"},
                                              "answer": {"type": "string", "enum": ["Y", "PY", "PN", "N"]},
                                              "pattern": {"type": "string"}, "rationale": {"type": "string"},
                                              "fires_on": {"type": "array", "items": {"type": "string"}},
                                              "must_not_fire_on": {"type": "array", "items": {"type": "string"}}}}}}}

INSTR = """You write typed regular-expression rules for the Cochrane RoB 2 tool (Handbook chapter 8). Each rule answers ONE
signalling question with ONE fixed answer whenever its pattern matches a sentence of a trial report. A wrong answer is far
worse than no answer: the rules today have 0 disagreements with expert-style readings, and that must stay true.

Below: the RoB 2 questions; the EXISTING rules (do not duplicate them); and GAPS -- sentences from trial reports where two
independent readers answered a question but no rule fired, with their answer. Propose rules that would answer these gaps
AND generalise to other trial reports. Rules:
- Python `re` syntax, matched case-insensitively against one sentence; bounded repetition only ({0,60}, never .* or .+);
  no lookbehind of variable width.
- A rule must not fire on negations ("not blinded", "no independent committee") or on statements about OTHER trials.
- Only propose a rule whose answer follows from the matched words alone, for ANY outcome. If the right answer depends on
  the outcome or on facts outside the sentence, do not propose it.
- For each rule give 2+ sentences it must fire on (from the gaps or close paraphrases) and 2+ near-miss sentences it must
  NOT fire on (negations, other trials, a different question).
Reply ONLY with JSON matching the schema in schema.json: {"rules": [{"rule_id": "regex:<name>_v1", "question": "4.2",
"answer": "PN", "pattern": "...", "rationale": "...", "fires_on": [...], "must_not_fire_on": [...]}]}.
"""


def main():
    ev = json.load(open(EVAL, encoding="utf-8"))
    dev = set(json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))["dev"])
    gaps = []
    for q, v in sorted(ev["recall_gaps"].items()):
        for g in v:
            if g["pmid"] not in dev:
                raise SystemExit(f"REFUSED: gap from PMID {g['pmid']}, not DEV")
            gaps.append({"question": q, "answer": g["answer"], "sentence": g["quote"]})
    existing = [{"question": q, "answer": a, "rule_id": rid, "pattern": getattr(p, "pattern", p)} for q, a, rid, p in rt.REGEX_RULES]
    r2 = "--round2" in sys.argv
    body = (INSTR + (ROUND2 if r2 else "") + "\n## RoB 2 questions\n" + json.dumps(rf.QUESTIONS, indent=1, ensure_ascii=False) +
            "\n\n## Existing rules\n" + json.dumps(existing, indent=1, ensure_ascii=False) +
            "\n\n## Gaps (DEV trials, CC BY/CC0 full texts)\n" + json.dumps(gaps, indent=1, ensure_ascii=False) + "\n")
    prompt = body.encode("utf-8")
    digests = [{"ref": "outputs/robgrade/dev/rule_eval.json", "sha256": hashlib.sha256(open(EVAL, "rb").read()).hexdigest(),
                "what": "DEV recall gaps (quotes from CC BY / CC0 DEV full texts)"}]
    caller = {"file": "scripts/rob2_propose_rules.py", "line": "main", "lane": rd.LANE,
              "purpose": "propose typed RoB 2 regex rules from DEV recall gaps (proposals are reviewed and planted)"}
    rec = mcl.call(prompt, schema=SCHEMA, model=rd.CODEX_MODEL, effort="high", caller=caller, input_digests=digests,
                   timeout_s=1800)
    ms.write_record(rec, rd.REC_DIR)
    if rec["state"] != "RAN_OK":
        raise SystemExit(f"codex call failed: {rec.get('error')}")
    props = json.loads(ms.replay(rec).decode("utf-8"))
    out = OUT.replace(".json", "_r2.json") if r2 else OUT
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"record_id": rec["record_id"], "n_gaps": len(gaps), **props}, fh, indent=1, ensure_ascii=False)
    for r in props["rules"]:
        print(r["question"], r["answer"], r["rule_id"], r["pattern"])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
