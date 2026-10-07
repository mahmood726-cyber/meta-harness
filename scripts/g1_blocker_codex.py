"""G1 finish line: a cross-vendor (codex) investigation of each target topic's OPEN GAPS and RESULT_AGREES blocker, as
RECORDED calls (reproducible_ai.model_call_live). The evidence goes inline -- the topic's open-gap trials as the tracker
holds them (label, family, blocker, our refusal, our screen's funnel, registry candidates with their gate, comparator
row and its provenance), the protocol's include rules and the same-trials state -- so the reviewer needs no file tools.
Every answer is a PROPOSAL: a HARNESS_DEFECT is accepted only after its failing input is reproduced here, a scope
difference only with its verbatim span found in a held record.

    python scripts/g1_blocker_codex.py --run SLUG [SLUG ...]   (recorded calls, concurrency 3)
    python scripts/g1_blocker_codex.py --show                  (replay records; print proposals)
-> registry/model_proposals/g1_blocker_codex.json
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

PROP = os.path.join(ROOT, "registry", "model_proposals", "g1_blocker_codex.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT = "gpt-6-astra", "high"
KINDS = ["HARNESS_DEFECT", "SCOPE_DIFFERENCE", "SOURCE_ABSENT", "COMPARATOR_ERROR", "IDENTITY_WRONG", "UNSURE"]
SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["gaps", "result_blocker", "harness_classes"],
    "properties": {
        "gaps": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["trial", "kind", "why", "evidence_quote", "fix"],
            "properties": {"trial": {"type": "string"}, "kind": {"type": "string", "enum": KINDS},
                           "why": {"type": "string"}, "evidence_quote": {"type": "string"}, "fix": {"type": "string"}}}},
        "result_blocker": {"type": "string"},
        "harness_classes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["name", "trials", "rule_to_change", "failing_input"],
            "properties": {"name": {"type": "string"}, "trials": {"type": "array", "items": {"type": "string"}},
                           "rule_to_change": {"type": "string"}, "failing_input": {"type": "string"}}}},
    },
}
INSTR = """You audit why a comparator meta-analysis's trials are NOT matched by our harness (G1). A trial is matched when our
own verified data for it exists (our pool, the trial's registry results bound to it, or its own open text), or it is
named out of scope by a protocol rule with a verbatim span from its own record. Rules: the comparator's own numbers are
never data for us (anti-circularity); a percentage is never a count; a registry result alone is one source.

For EACH open-gap trial below, classify it:
  HARNESS_DEFECT    our code mis-handles it (wrong join, wrong report chosen, a gate firing on the wrong text, a label
                    mismatch...). Name the defect CLASS and give a concrete failing input from the evidence.
  SCOPE_DIFFERENCE  the protocol excludes it; quote the rule key and a verbatim span that appears in the evidence.
  SOURCE_ABSENT     no open primary source we hold states the outcome (say what is missing).
  COMPARATOR_ERROR  the comparator's row or citation is wrong (quote both sides).
  IDENTITY_WRONG    the trial is bound to the wrong report or registration.
  UNSURE            the evidence does not decide it.
Quote only text that appears in the evidence (evidence_quote = exact substring or empty). Then state in one line what
blocks RESULT_AGREES, and list the HARNESS classes that recur across trials (rule_to_change = the function or rule).
Never invent sources. Be terse."""


def evidence(slug):
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    keep = ("label", "family", "route", "blocker", "our_refusal", "seeded_funnel", "comparator_row",
            "comparator_row_provenance", "agreement_with_comparator_row", "basis", "pmids", "ncts")
    gaps = []
    for x in o["trials"]:
        ag = str(x.get("agreement_with_comparator_row") or "")
        if x["label"] in (o.get("open_gaps") or []) or ag.startswith(("DISAGREE", "NOT_COMPARABLE")):
            d = {k: x.get(k) for k in keep if x.get(k) not in (None, [], {})}
            rb = x.get("registry_binding") or {}
            if rb:
                d["registry_binding"] = {"state": rb.get("state"), "candidates": [
                    {"title": c.get("title"), "gate": c.get("gate"), "reason": (c.get("reason") or "")[:200],
                     "arms": c.get("arms")} for c in (rb.get("candidates") or [])[:6]]}
            gaps.append(d)
    st = o.get("same_trials") or {}
    return {"slug": slug, "comparator_pmid": o.get("comparator_pmid"), "comparator_result": o.get("comparator"),
            "our_result": o.get("ours"), "same_trials": {k: st.get(k) for k in ("state", "k", "measures", "verdict")},
            "protocol": {"primary_outcome": cfg.get("primary_outcome"), "include": cfg.get("include"),
                         "eligibility_summary": cfg.get("eligibility_summary")},
            "named_differences": [{"trial": d.get("trial"), "rule": d.get("rule_id"), "span": (d.get("span") or {}).get("text")}
                                  for d in o.get("named_differences") or []],
            "trials_needing_explanation": gaps}


def main(argv):
    data = json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {"runs": {}}
    if "--run" in argv:
        slugs = [a for a in argv if not a.startswith("--")]

        def one(slug):
            ev = json.dumps(evidence(slug), ensure_ascii=False, indent=0)
            p = (INSTR + "\n\n=== EVIDENCE ===\n" + ev).encode("utf-8")
            src = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json")
            rec = mcl.call(p, schema=SCHEMA, model=MODEL, effort=EFFORT,
                           caller={"file": "scripts/g1_blocker_codex.py", "line": "main",
                                   "purpose": f"G1 finish line: open-gap investigation {slug} (g1/finish-line lane)"},
                           input_digests=[{"ref": f"outputs/k_gap/g1/{slug}.json",
                                           "sha256": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                                           "what": "tracker file the evidence was taken from"}],
                           timeout_s=1800)
            ms.write_record(rec, REC_DIR)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
            return slug, {"record_id": rec["record_id"], "state": rec["state"],
                          "prompt_sha256": hashlib.sha256(p).hexdigest(), "head": head}
        with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))) as ex:
            for slug, r in ex.map(one, slugs):
                data["runs"][slug] = r
                print(slug, r["state"], r["record_id"], flush=True)
        json.dump(data, open(PROP, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for slug, r in data["runs"].items():
        if r["state"] != "RAN_OK":
            print(slug, r["state"])
            continue
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
        print(f"===== {slug}\n  RESULT: {resp['result_blocker']}")
        for g in resp["gaps"]:
            print(f"  [{g['kind']}] {g['trial'][:40]}: {g['why'][:220]} | quote: {g['evidence_quote'][:120]} | fix: {g['fix'][:160]}")
        for h in resp["harness_classes"]:
            print(f"  CLASS {h['name']}: {h['trials']} -> {h['rule_to_change'][:160]} | input: {h['failing_input'][:200]}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
