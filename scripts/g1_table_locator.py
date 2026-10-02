"""TABLE LOCATOR for the class EXTRACTION:OUTCOME_NOT_IN_SOURCE with an open text HELD but not admitted
(outputs/k_gap/extraction_diagnosis.json route TEXT_HELD_NOT_ADMITTED): mostly Unpaywall HTML/PDF copies whose tables
are flattened, where the full-text rung admits only a prose effect+CI by design.

One RECORDED, replayable model call per trial (reproducible_ai.model_call_live.call; Mahmood 2 Oct: model calls only
for forest plots and TABLE LOCATION). The model only LOCATES: it quotes the passage/table row with the topic outcome's
between-arm result and copies its numbers. A number is ACCEPTED only through harness.secondary_meta.gate_table_location (accepted = a gated PROPOSAL; there is no
admission path into a pool yet -- one must bind it to a held document first, codex review 3 Oct):
the quote is verbatim in the held text, every copied number is printed in the quote, the quote names the topic outcome
(non-generic keyword), and a single declared outcome is never bound to a composite. Calls run 3 at a time; each record is
written to evidence/model_calls/table_locator/ and ledgered in registry/secondary_meta/runs/<slug>.json under
'locate::<slug>::<pmid>::table'. Re-runs replay records; a changed prompt makes a new call.

    python scripts/g1_table_locator.py [--run]      -> outputs/k_gap/table_locator.json
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402
from kgap import runs_store  # noqa: E402
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
import k_gap_forest_plot as fp  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "table_locator")
MAX_CHARS = 150000
INSTR = """You are given the held open-access text of ONE randomised trial report and ONE outcome, with the words this
review uses for it. Find where the report gives the BETWEEN-ARM RESULT for exactly that outcome -- often a row of a
results table that has been flattened into text. Quote, character for character, the shortest passage (or table row,
with its row label) that contains it. Copy the numbers exactly as printed in your quote: per-arm events and totals
(events_t/n_t for the intervention, events_c/n_c for the control), and/or the effect measure with its point estimate and
confidence limits. Use null for anything not printed in your quote; never compute or convert. Do not quote a composite
or a different endpoint. If the text does not report this outcome by arm, state=NOT_REPORTED.
"""


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def targets():
    D = _j(os.path.join(OUT, "extraction_diagnosis.json"))
    return [r for r in D["rows"] if r["route"] == "TEXT_HELD_NOT_ADMITTED"]


def item(r):
    import g1_extraction_diagnosis as dg
    cfg = _j(os.path.join(ROOT, "topics", r["slug"] + ".json"))
    po = cfg["primary_outcome"]
    recs = {str(x.get("id")): x for x in _j(os.path.join(ROOT, "cache", r["slug"], "records.json")).get("records", [])}
    rec = recs.get(r["pmid"]) or _j(os.path.join(OUT, "member_records.json")).get(r["pmid"])
    texts = dg.held_texts(r["slug"], r["pmid"], rec)
    body = "\n\n".join(f"=== {ref} ===\n{t}" for ref, t in texts)[:MAX_CHARS]
    want_counts = (po.get("estimand") or "").upper() in ("RR", "OR", "RD")
    wanted = ("\nWANTED: events and totals in EACH arm (events_t, n_t, events_c, n_c), as printed.\n" if want_counts else
              f"\nWANTED: the {po.get('estimand') or 'effect'} with its 95% confidence interval, as printed.\n")
    p = (INSTR + wanted + f"\nOUTCOME: {po['name']}\nWORDS FOR IT: {', '.join(po.get('keywords') or [])}\n"
         f"INTERVENTION: {', '.join(cfg.get('intervention_terms') or [])}\n"
         f"CONTROL: {', '.join(cfg.get('comparator_terms') or [])}\n<<<TEXT\n{body}\nTEXT>>>\n").encode("utf-8")
    return {"slug": r["slug"], "pmid": r["pmid"], "label": r["label"], "outcome": po["name"], "spec": po,
            "interv": cfg.get("intervention_terms") or [], "comp": cfg.get("comparator_terms") or [],
            "prefer": "counts" if want_counts else None, "prompt": p, "text": body,
            "key": f"locate::{r['slug']}::{r['pmid']}::table", "sources": [ref for ref, _ in texts]}


def call(it):
    rec = mcl.call(it["prompt"], schema=json.loads(json.dumps(__import__("secondary_meta_build").LOCATE_SCHEMA)),
                   model=fp.MODEL, effort=fp.EFFORT,
                   caller={"file": "scripts/g1_table_locator.py", "line": "call",
                           "purpose": f"G1 table location {it['slug']} PMID {it['pmid']} (acq/k-gap lane)"},
                   input_digests=[{"ref": f"held open text PMID {it['pmid']} ({'+'.join(it['sources'])})",
                                   "sha256": hashlib.sha256(it["text"].encode("utf-8")).hexdigest(),
                                   "what": f"held text shown, first {MAX_CHARS} chars"}],
                   timeout_s=1200)
    ms.write_record(rec, REC_DIR)
    return it["key"], {"record_id": rec["record_id"], "state": rec["state"],
                       "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}


def main(argv):
    run = "--run" in argv
    runs = runs_store.load()
    items = [item(r) for r in targets()]
    todo = [it for it in items if (runs.get(it["key"]) or {}).get("prompt_sha256") != hashlib.sha256(it["prompt"]).hexdigest()
            or (runs.get(it["key"]) or {}).get("state") != "RAN_OK"]
    if run and todo:
        with cf.ThreadPoolExecutor(max_workers=3) as ex:           # codex concurrency 3
            for key, r in ex.map(call, todo):
                runs[key] = r
                print(key, r["state"], r["record_id"], flush=True)
        runs_store.save(runs, slugs={it["slug"] for it in todo})
    rows, tally = [], Counter()
    for it in items:
        r = runs.get(it["key"])
        if not r or r.get("prompt_sha256") != hashlib.sha256(it["prompt"]).hexdigest() or r.get("state") != "RAN_OK":
            verdict, val, why, rid = "NOT_RUN", None, "no recorded call for this prompt", (r or {}).get("record_id")
        else:
            rid = r["record_id"]
            claim = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, rid + ".json"))).decode("utf-8"))
            val, why = sm.gate_table_location(claim, it["text"], it["spec"].get("keywords") or [], it["outcome"],
                                              prefer=it["prefer"], interv=it["interv"], comp=it["comp"])
            verdict = "ACCEPTED" if val else "REFUSED"
        tally[verdict if verdict != "REFUSED" else f"REFUSED:{why}"] += 1
        rows.append({"slug": it["slug"], "pmid": it["pmid"], "label": it["label"], "outcome": it["outcome"],
                     "verdict": verdict, "reason": why, "record_id": rid,
                     "value": ({k: val.get(k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t",
                                                         "events_c", "n_c", "span", "named_by")} if val else None)})
    out = {"n": len(rows), "tally": dict(tally), "rows": rows}
    with open(os.path.join(OUT, "table_locator.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({"n": out["n"], "tally": out["tally"]}))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
