"""Unpaywall funnel step S4, re-read: is the primary outcome's result IN the parsed OA text our extractor did not use?

For each funnel row at S4 (OA text parsed, our pipeline found no admissible value), one recorded model call reads
the SAME held text our pipeline was given and QUOTES where the trial reports its result for the topic's primary
outcome -- or says it does not. The deterministic gate then decides, and nothing is admitted to any pool:

  quote       must occur verbatim (whitespace-normalised) in the held text, or the answer is refused
  numbers     every number the model copies (arm events / totals, effect, limits) must occur inside its own quote
  where       PROSE if the quote reads as a sentence (a verb and no run of >=4 bare numbers), else TABLE_LIKE
  verdict     LOCATED_IN_PROSE / LOCATED_TABLE_LIKE / MODEL_SAYS_NOT_REPORTED / REFUSED

This separates 'the outcome is not in the text' (a true S4) from 'it is there and our extractor did not take it'
(an extraction defect, or the deliberate refusal of flattened tables), which the reason code cannot.

    python scripts/k_gap_upw_locate.py --run     (recorded calls, concurrency 3)
    python scripts/k_gap_upw_locate.py           (replay + gate)
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
PROP = os.path.join(ROOT, "registry", "model_proposals", "k_gap_upw_locate.json")
REC_DIR = os.path.join(ROOT, "registry", "model_calls")
MODEL, EFFORT = "gpt-6-astra", "medium"
_S = {"type": ["string", "null"]}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["state", "quote", "events_t", "n_t",
          "events_c", "n_c", "measure", "point", "lower", "upper", "notes"],
          "properties": {"state": {"type": "string", "enum": ["REPORTED", "NOT_REPORTED"]}, "quote": _S,
                         "events_t": _S, "n_t": _S, "events_c": _S, "n_c": _S, "measure": _S, "point": _S,
                         "lower": _S, "upper": _S, "notes": {"type": "string"}}}
INSTR = """You are given the full text of ONE randomised trial report and the name of ONE outcome. Find where the trial
reports its RESULT for that outcome, comparing the intervention arm with the control arm.

- quote: copy, character for character, the shortest passage (a sentence or a table row) that states that result.
- Copy the numbers as printed: events and totals per arm if given (events_t/n_t for the intervention arm, events_c/n_c
  for the control arm), and/or the effect measure with its point estimate and confidence limits. Use null for any
  value that is not printed in your quote. Never compute a value.
- If the text does not report a between-arm result for this outcome, state=NOT_REPORTED and quote=null.
- notes: anything a checker needs (e.g. the only result is for a subgroup; the outcome is defined differently).
"""


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _norm(t):
    return re.sub(r"\s+", " ", (t or "").replace("−", "-")).strip()


def items():
    f = _j(os.path.join(OUT, "unpaywall_funnel.json"))
    out = []
    for r in f["rows"]:
        if not r["stage"].startswith("S4"):
            continue
        u = k_gap.unpaywall_text(r["doi"], os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"),
                                 offline=True)
        text = u.get("text") or ""
        if not text:
            continue
        cfg = _j(os.path.join(ROOT, "topics", r["slug"] + ".json"))
        po = cfg.get("primary_outcome") or {}
        out.append({"slug": r["slug"], "label": r["label"], "pmid": r.get("pmid"), "doi": r["doi"], "stage": r["stage"],
                    "outcome": po.get("name"), "keywords": po.get("keywords") or [], "text": text,
                    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    return out


def prompt(it):
    return (INSTR + f"\nOUTCOME: {it['outcome']} (also written as: {', '.join(it['keywords'][:8])})\n"
            + "<<<TEXT\n" + it["text"] + "\nTEXT>>>\n").encode("utf-8")


def run_one(it):
    from reproducible_ai import model_call_live
    p = prompt(it)
    rec = model_call_live.call(p, schema=SCHEMA, model=MODEL, effort=EFFORT,
                               caller={"file": "scripts/k_gap_upw_locate.py", "line": "run_one",
                                       "purpose": f"Unpaywall S4 re-read {it['slug']} {it['pmid']} (acq/k-gap lane)"},
                               input_digests=[{"ref": f"outputs/k_gap/_upw (DOI {it['doi']})", "sha256": it["text_sha256"],
                                               "what": "held Unpaywall OA text shown whole"}], timeout_s=1500)
    ms.write_record(rec, REC_DIR)
    return {"key": f"{it['slug']}::{it['pmid']}", "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": hashlib.sha256(p).hexdigest()}


def gate(claim, text):
    if not isinstance(claim, dict) or claim.get("state") not in ("REPORTED", "NOT_REPORTED"):
        return {"verdict": "REFUSED", "problems": ["UNTYPED"]}
    if claim["state"] == "NOT_REPORTED":
        return {"verdict": "MODEL_SAYS_NOT_REPORTED", "problems": []}
    q = _norm(claim.get("quote"))
    probs = []
    if not q or q not in _norm(text):
        probs.append("QUOTE_NOT_IN_TEXT")
    for k in ("events_t", "n_t", "events_c", "n_c", "point", "lower", "upper"):
        v = claim.get(k)
        if v and not re.search(r"(?<![\d.])" + re.escape(_norm(str(v))) + r"(?![\d])", q):
            probs.append(f"{k.upper()}_NOT_IN_QUOTE")
    if not any(claim.get(k) for k in ("events_t", "point")):
        probs.append("NO_RESULT_NUMBERS")
    if probs:
        return {"verdict": "REFUSED", "problems": probs}
    bare_run = re.search(r"(?:\b\d+(?:\.\d+)?\b[\s%()\[\],;|/-]*){4,}", q)
    verb = re.search(r"\b(?:was|were|occurred|developed|reduced|had|experienced|compared|versus|vs\.?|died)\b", q, re.I)
    where = "LOCATED_IN_PROSE" if verb and not (bare_run and len(bare_run.group(0)) > len(q) * 0.5) else "LOCATED_TABLE_LIKE"
    return {"verdict": where, "problems": []}


def main(argv):
    its = items()
    data = _j(PROP) if os.path.exists(PROP) else {}
    runs = data.get("runs", {})
    if "--run" in argv:
        done = {r["prompt_sha256"] for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [i for i in its if hashlib.sha256(prompt(i)).hexdigest() not in done]
        print(f"S4 rows with text {len(its)}, to run {len(todo)}", flush=True)
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(run_one, todo):
                runs[r["key"]] = r
                print(r["key"], r["state"], r["record_id"], flush=True)
    rows = []
    for it in its:
        run = runs.get(f"{it['slug']}::{it['pmid']}")
        if not run or run["state"] != "RAN_OK" or run["prompt_sha256"] != hashlib.sha256(prompt(it)).hexdigest():
            rows.append({"slug": it["slug"], "label": it["label"], "verdict": "NO_RECORDED_CALL"})
            continue
        claim = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, run["record_id"] + ".json"))).decode("utf-8"))
        g = gate(claim, it["text"])
        rows.append({"slug": it["slug"], "label": it["label"], "pmid": it["pmid"], "stage": it["stage"],
                     "record_id": run["record_id"], "claim": claim, **g})
    out = {"n": len(rows), "tally": dict(Counter(r["verdict"] for r in rows)), "runs": runs, "rows": rows}
    json.dump(out, open(PROP, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({"n": out["n"], "tally": out["tally"]}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
