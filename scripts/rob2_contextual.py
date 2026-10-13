"""The contextual pass (outputs/robgrade/CONTEXTUAL_POLICY.md): for each trial, the asked questions whose v3.1 answer
is NI are put to codex and agy (recorded, blind to each other), who may answer PY/PN ONLY with a verbatim context quote
from an open source (Handbook 8.2.3); a disagreement goes to the recorded adjudicator. The same open sources as the
dual reading (scripts/rob2_dual.evidence_block: D8 unchanged). Logic in robgrade/contextual.py.

    python scripts/rob2_contextual.py [--run] SLUG ...   -> outputs/robgrade/rob2_ctx/<slug>.json
Without --run nothing is called: recorded answers are replayed (a missing record leaves the question NI).
"""
import concurrent.futures as cf
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_dual as rd  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
from robgrade import contextual as cx  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402

OBJ_DIR = os.path.join(ROOT, "outputs", "robgrade", "rob2")
OUT_DIR = os.path.join(ROOT, "outputs", "robgrade", "rob2_ctx")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "rob2_ctx")
RUNS = os.path.join(ROOT, "registry", "model_proposals", "rob2_ctx_runs.json")


def schema(targets):
    return {"type": "object", "additionalProperties": False, "required": ["answers", "notes"], "properties": {
        "notes": {"type": "string"},
        "answers": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                    "required": ["qid", "answer", "quote", "source_id", "rationale"],
                    "properties": {"qid": {"type": "string", "enum": list(targets)},
                                   "answer": {"type": "string", "enum": ["PY", "PN", "NI"]},
                                   "quote": {"type": "string"}, "source_id": {"type": "string"},
                                   "rationale": {"type": "string"}}}}}}


INSTR = """You are assessing ONE randomised trial with the Cochrane RoB 2 tool (Handbook chapter 8), for ONE outcome
(effect of assignment). For each signalling question below, the sources do NOT state the answer directly; it is
currently "no information" (NI).

The Cochrane Handbook (8.2.3): "No information" should be used only when insufficient details are reported AND a
"probably yes" or "probably no" answer would be unreasonable without them. Where the sources give CONTEXT that makes a
probability judgement reasonable (e.g. for a large trial run by an experienced clinical trials unit, missing details
of the randomisation may still justify "probably yes"), answer PY or PN.

Rules -- checked mechanically; an answer that breaks them is discarded:
- Answer PY, PN or NI only (never Y or N: those need a direct statement, and there is none).
- A PY or PN answer must quote VERBATIM (copied exactly, 8 to 300 characters) the CONTEXT it rests on, from ONE source
  below, with that source's id in source_id. The rationale says, in one sentence, how the context supports the answer,
  USING WORDS FROM YOUR QUOTE (a rationale that does not refer to the quoted context is discarded).
- Use ONLY the sources below: not your memory of this trial, and not what trials usually do. If the sources give no
  such context, answer NI with an empty quote.
Reply with ONE JSON object with EXACTLY these keys, one element of "answers" per listed question:
{"answers": [{"qid": "1.2", "answer": "PY", "quote": "<verbatim context>", "source_id": "<a source id>",
  "rationale": "<one sentence>"}], "notes": ""}
"""

ADJ = """Two independent readers were asked, for the signalling questions below, whether the sources give CONTEXT that
supports a "probably yes" (PY) or "probably no" (PN) answer (Cochrane Handbook 8.2.3), and they DISAGREED. Decide for
each: PY or PN with a VERBATIM context quote (8-300 characters) from one source and its source_id, or NI if the sources
give no such context. Same rules: never Y or N; only the sources; the rationale must use words from the quote; never
reason from memory or from what trials usually do; either reader may be wrong.
Reply with ONE JSON object: {"answers": [{"qid": ..., "answer": ..., "quote": ..., "source_id": ..., "rationale": ...}],
"notes": ""}
"""


EVIDENCE_MARK = "\n=== EVIDENCE ===\n"


def prompt_head(pmid, nct, outcome, targets, kind="reader", readings=None):
    """Everything in a contextual prompt BEFORE its evidence block: the registered instruction, the trial, the outcome,
    the targets with their registered question text, and (adjudicator) the two readings. The scorer rebuilds this with
    the same function and requires byte equality (codex round 4): nothing can be inserted, and no question reworded."""
    qs = "\n".join(f"{q} {rf.QUESTIONS[q]}" for q in targets)
    body = f"\nTRIAL: {pmid} ({nct or 'no registry id'})\nOUTCOME: {outcome}\n\nSIGNALLING QUESTIONS:\n{qs}\n"
    if kind == "adjudicator":
        body += "\nTHE TWO READINGS:\n" + json.dumps(readings, indent=1, ensure_ascii=False) + "\n"
    return (INSTR if kind == "reader" else ADJ) + body


def prompt(item, targets, kind="reader", readings=None):
    return (prompt_head(item["pmid"], item["nct"], item["outcome"], targets, kind, readings) + EVIDENCE_MARK +
            json.dumps({"sources": rd.evidence_block(item)}, ensure_ascii=False)).encode("utf-8")


def call(item, who, p, targets):
    from reproducible_ai import model_call_live as mcl
    caller = {"file": "scripts/rob2_contextual.py", "line": f"call:{who}", "lane": rd.LANE,
              "purpose": f"RoB 2 contextual pass ({who}) {item['slug']} PMID {item['pmid']} questions {','.join(targets)}"}
    for attempt in range(4):
        if who == "agy":
            rec = mcl.agy_call(p, schema=schema(targets), caller=caller, input_digests=rd.digests(item), timeout_s=900)
        else:
            rec = mcl.call(p, schema=schema(targets), model=rd.CODEX_MODEL,
                           effort=rd.ADJ_EFFORT if who == "adjudicator" else rd.CODEX_EFFORT, caller=caller,
                           input_digests=rd.digests(item), timeout_s=1200)
        ms.write_record(rec, REC_DIR)
        if rec["state"] == "RAN_OK" or attempt == 3:
            break
        time.sleep(30 * 3 ** attempt)
    return {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": hashlib.sha256(p).hexdigest()}


def _reading(run):
    """The recorded reply of a CONTEXTUAL call (this pass's own record store), parsed; None when absent or failed."""
    if not run or run.get("state") != "RAN_OK":
        return None
    return rd.parse(ms.replay(ms.load_record(os.path.join(REC_DIR, run["record_id"] + ".json"))))


def record_prompt_sha256(rid):
    """The sha256 of the prompt a held record ACTUALLY carries (model_source re-derives it), None when not held."""
    p = os.path.join(REC_DIR, rid + ".json")
    if not os.path.exists(p):
        return None
    return hashlib.sha256(ms._unblob(ms.load_record(p)["prompt"], "prompt")).hexdigest()


def fresh(run, prompt_bytes):
    """A recorded call used only for the EXACT prompt it answered (codex rounds 1-2): the run file's hash AND the held
    record's own prompt must both equal the current prompt's -- another outcome, target list, evidence or set of
    readings is stale, and is not replayed."""
    want = hashlib.sha256(prompt_bytes).hexdigest()
    if not run or run.get("state") != "RAN_OK" or run.get("prompt_sha256") != want:
        return None
    if record_prompt_sha256(run["record_id"]) != want:
        return None
    return run


MAX_PASSES = 3


def pass_decisions(a, b, adj, targets):
    """The pass's decisions. A reader whose record is missing or failed (None) VOIDS the pass: no contextual answer,
    and never an adjudication between one reader and nobody (codex round 5)."""
    if a is None or b is None:
        return {q: {"answer": "NI", "decided_by": "a reader's record is missing or failed: no contextual answer"}
                for q in targets}
    return cx.combine(a, b, adj)


def _one_pass(item, obj, targets, run, live, pools, srcs):
    """One contextual pass over `targets`: two blind readers, the adjudicator on a real disagreement, applied."""
    p = prompt(item, targets)
    if live:                                           # re-call whatever is not FRESH (agy round 4)
        futs = {w: pools[w].submit(call, item, w, p, targets) for w in ("codex", "agy") if not fresh(run.get(w), p)}
        for w, f in futs.items():
            run[w] = f.result()
    fc, fa = fresh(run.get("codex"), p), fresh(run.get("agy"), p)
    a = cx.verify(_reading(fc), srcs, targets) if fc else None
    b = cx.verify(_reading(fa), srcs, targets) if fa else None
    # a disagreement is two DIFFERENT verified answers of two PRESENT readers; agreement (PY/PN or NI) never goes to the
    # adjudicator, and a missing reader voids the pass (pass_decisions)
    dis = {q: {"reader 1": a[q], "reader 2": b[q]} for q in targets if a[q]["answer"] != b[q]["answer"]} \
        if a is not None and b is not None else {}
    adj = {}
    if dis:
        pa = prompt(item, sorted(dis), "adjudicator", dis)
        if live and not fresh(run.get("adjudicator"), pa):
            run["adjudicator"] = pools["codex"].submit(call, item, "adjudicator", pa, sorted(dis)).result()
        adj_run = fresh(run.get("adjudicator"), pa)
        adj = cx.verify(_reading(adj_run), srcs, sorted(dis)) if adj_run else {}   # no record: nothing is the adjudicator's
    c = pass_decisions(a, b, adj, targets)
    recs = {q: [run[w]["record_id"] for w in ("codex", "agy") if fresh(run.get(w), p)] +
               ([run["adjudicator"]["record_id"]] if c[q].get("decided_by") == "adjudicator" else []) for q in c}
    # the records this pass actually READ (codex round 6): the scorer requires every post-registration RAN_OK record
    # to be one of these, so a decision record parked where the replay never reads it cannot hide an omission
    consumed = [x["record_id"] for x in (fc, fa) if x] + \
        ([run["adjudicator"]["record_id"]] if dis and fresh(run.get("adjudicator"), pa) else [])
    return cx.apply(obj, c, recs), c, consumed


def process(item, obj, runs, live, pools):
    """Up to MAX_PASSES contextual passes (codex round 4): a contextual answer can OPEN a branch, and a newly asked
    question that is NI gets its own pass rather than a fixed NI. A question decided in a pass is never re-asked."""
    r = dict(runs.get(item["key"]) or {})
    passes = list(r.get("passes") or [])
    srcs = rd.open_sources(item)
    cur, decided, audit, c_all, consumed, executed = obj, set(), {}, {}, [], 0
    for k in range(MAX_PASSES):
        targets = [q for q in cx.ni_targets(cur) if q not in decided]
        if not targets:
            break
        run = dict(passes[k]) if k < len(passes) else {}
        cur, c, used = _one_pass(item, cur, targets, run, live, pools, srcs)
        audit.update(cur["contextual_audit"])
        c_all.update(c)
        consumed += used
        decided |= set(targets)
        passes = passes[:k] + [run] + passes[k + 1:]
        executed = k + 1
    cur = dict(cur, contextual_audit=audit)
    r["passes"] = passes[:executed]                     # a pass the replay does not execute is not kept (codex round 6)
    r["consumed"] = consumed
    return cur, r, c_all


def main(argv):
    live = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")]
    runs = rd._j(RUNS) if os.path.exists(RUNS) else {}
    pools = {"codex": cf.ThreadPoolExecutor(rd.CODEX_WORKERS), "agy": cf.ThreadPoolExecutor(rd.AGY_WORKERS)}
    driver = cf.ThreadPoolExecutor(rd.CODEX_WORKERS)
    docs = {s: rd._j(os.path.join(OBJ_DIR, f"{s}.json")) for s in slugs}
    rd.prefetch_registry([(s, sorted(docs[s]["trials"])) for s in slugs])
    jobs = []
    for slug in slugs:
        doc = docs[slug]
        items = {it["pmid"]: it for it in rd.items(slug, sorted(doc["trials"]))}
        jobs.append((slug, doc, [(items[p], o, driver.submit(process, items[p], o, runs, live, pools))
                                 for p, o in sorted(doc["trials"].items()) if p in items]))
    for slug, doc, js in jobs:
        out, ctx = {}, {}
        for it, o, f in js:
            new, r, c = f.result()
            runs[it["key"]] = r
            rd.redact_closed_spans(new, it)
            out[it["pmid"]] = new
            ctx[it["pmid"]] = {q: x["answer"] for q, x in c.items()}
            print(slug, it["pmid"], {q: x for q, x in ctx[it["pmid"]].items() if x != "NI"},
                  [{w: (x or {}).get("state") for w, x in run.items()} for run in r.get("passes") or []], flush=True)
        rd._save(RUNS, runs)
        rd._save(os.path.join(OUT_DIR, f"{slug}.json"), dict(doc, trials=out, contextual=ctx,
                                                             family=rf.FAMILY + "+contextual"))
    for p in pools.values():
        p.shutdown()
    driver.shutdown()


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
