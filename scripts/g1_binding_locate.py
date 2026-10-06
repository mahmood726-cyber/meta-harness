"""G1 BINDING LANE (Mahmood 4 Oct, goal 1): one RECORDED, replayable codex call per named comparator trial, through the
EXISTING table-location machinery -- the same prompt (g1_table_locator.INSTR), schema (secondary_meta_build.
LOCATE_SCHEMA), recorder (reproducible_ai.model_call_live.call: `codex exec` with stdin </dev/null), record directory
(evidence/model_calls/table_locator), runs ledger key 'locate::<slug>::<pmid>::table', and GATE
(harness.secondary_meta.gate_table_location: quote verbatim in the held text, every copied number printed in the quote,
topic outcome named by a non-generic keyword, never a composite for a declared single outcome, no subgroup quote, arms by
their own labels). Concurrency 3. A model answer is a PROPOSAL; only the gate's output is a value.

Difference from g1_table_locator: the target list is the lane's named trials (outputs/k_gap/g1_binding/targets.json),
and the trial's ABSTRACT is part of the held text when no open full text is held (the cascade's own abstract record).
Source order (Mahmood): AACT first (scripts/g1_binding_findings.py, posted results), then the held open text here, then
SECONDARY_SINGLE (the tracker's own rule). Anti-circularity: the comparator's numbers are never shown to the model.

    python scripts/g1_binding_locate.py [--run] [--model M]   -> outputs/k_gap/g1_binding/locate.json
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
import g1_extraction_diagnosis as dg  # noqa: E402
import g1_table_locator as tl  # noqa: E402
import k_gap_forest_plot as fp  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
BOUT = os.path.join(OUT, "g1_binding")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def item(t, pmid):
    cfg = _j(os.path.join(ROOT, "topics", t["slug"] + ".json"))
    po = cfg["primary_outcome"]
    recs = {str(x.get("id")): x for x in _j(os.path.join(ROOT, "cache", t["slug"], "records.json")).get("records", [])}
    rec = recs.get(pmid) or _j(os.path.join(OUT, "member_records.json")).get(pmid)
    texts = dg.held_texts(t["slug"], pmid, rec)
    if rec and (rec.get("abstract") or "").strip():
        texts.append(("ABSTRACT", ((rec.get("title") or "") + "\n" + (rec.get("abstract") or "")).strip()))
    # LICENCE GATE (6 Oct incident): a recorded prompt is committed evidence -- full text only under CC BY / CC0
    import g1_licence as _lic
    texts, dropped = _lic.gate(pmid, texts, offline=os.environ.get("G1_LICENCE_OFFLINE") == "1")
    body ="\n\n".join(f"=== {ref} ===\n{x}" for ref, x in texts)[:tl.MAX_CHARS]
    want_counts = (po.get("estimand") or "").upper() in ("RR", "OR", "RD")
    wanted = ("\nWANTED: events and totals in EACH arm (events_t, n_t, events_c, n_c), as printed.\n" if want_counts else
              f"\nWANTED: the {po.get('estimand') or 'effect'} with its 95% confidence interval, as printed.\n")
    p = (tl.INSTR + wanted + f"\nOUTCOME: {po['name']}\nWORDS FOR IT: {', '.join(po.get('keywords') or [])}\n"
         f"INTERVENTION: {', '.join(cfg.get('intervention_terms') or [])}\n"
         f"CONTROL: {', '.join(cfg.get('comparator_terms') or [])}\n<<<TEXT\n{body}\nTEXT>>>\n").encode("utf-8")
    return {"slug": t["slug"], "pmid": pmid, "label": t["label"], "outcome": po["name"], "spec": po,
            "interv": cfg.get("intervention_terms") or [], "comp": cfg.get("comparator_terms") or [],
            "prefer": "counts" if want_counts else None, "prompt": p, "text": body,
            "key": f"locate::{t['slug']}::{pmid}::table", "sources": [ref for ref, _ in texts], "licence_dropped": dropped}


def call(it, model):
    rec = mcl.call(it["prompt"], schema=json.loads(json.dumps(smb.LOCATE_SCHEMA)), model=model, effort=fp.EFFORT,
                   caller={"file": "scripts/g1_binding_locate.py", "line": "call",
                           "purpose": f"G1 binding lane: locate {it['slug']} PMID {it['pmid']} ({it['label']})"},
                   # declared in the form the recorder's licence guard resolves (record_licence.ref_licences)
                   input_digests=[{"ref": f"held open text PMID {it['pmid']} ({'+'.join(it['sources'])})",
                                   "sha256": hashlib.sha256(it["text"].encode("utf-8")).hexdigest(),
                                   "what": f"held text shown, first {tl.MAX_CHARS} chars"}],
                   timeout_s=1200)
    ms.write_record(rec, tl.REC_DIR)
    return it["key"], {"record_id": rec["record_id"], "state": rec["state"],
                       "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}


def main(argv):
    run = "--run" in argv
    model = argv[argv.index("--model") + 1] if "--model" in argv else fp.MODEL
    targets = _j(os.path.join(BOUT, "targets.json"))
    items = [item(t, p) for t in targets for p in t["pmids"][:1]]
    items = [it for it in items if it["text"].strip()]
    runs = runs_store.load()
    # a ledger entry whose RECORD is gone (removed for licence, 6 Oct: mc-60163e27) is not a run: re-run it
    def _rec_ok(it):
        rid = (runs.get(it["key"]) or {}).get("record_id")
        return bool(rid) and os.path.exists(os.path.join(tl.REC_DIR, rid + ".json"))
    todo = [it for it in items if (runs.get(it["key"]) or {}).get("prompt_sha256") != hashlib.sha256(it["prompt"]).hexdigest()
            or (runs.get(it["key"]) or {}).get("state") != "RAN_OK" or not _rec_ok(it)]
    if run and todo:
        with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G1_CODEX_CONCURRENCY", "3"))) as ex:
            for key, r in ex.map(lambda it: call(it, model), todo):
                runs[key] = r
                print(key, r["state"], r["record_id"], flush=True)
        runs_store.save(runs, slugs={it["slug"] for it in todo})
    rows, tally = [], Counter()
    for it in items:
        r = runs.get(it["key"])
        if not r or r.get("prompt_sha256") != hashlib.sha256(it["prompt"]).hexdigest() or r.get("state") != "RAN_OK" \
                or not os.path.exists(os.path.join(tl.REC_DIR, str(r.get("record_id")) + ".json")):
            verdict, val, why, rid, claim = "NOT_RUN", None, "no recorded call for this prompt", (r or {}).get("record_id"), None
        else:
            rid = r["record_id"]
            claim = json.loads(ms.replay(ms.load_record(os.path.join(tl.REC_DIR, rid + ".json"))).decode("utf-8"))
            val, why = sm.gate_table_location(claim, it["text"], it["spec"].get("keywords") or [], it["outcome"],
                                              prefer=it["prefer"], interv=it["interv"], comp=it["comp"])
            verdict = "ACCEPTED" if val else ("NOT_REPORTED" if claim.get("state") == "NOT_REPORTED" else "REFUSED")
        tally[verdict if verdict != "REFUSED" else f"REFUSED:{why}"] += 1
        rows.append({"slug": it["slug"], "pmid": it["pmid"], "label": it["label"], "outcome": it["outcome"],
                     "sources": it["sources"], "verdict": verdict, "reason": why, "record_id": rid,
                     "claim": claim,
                     "value": ({k: val.get(k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t",
                                                         "events_c", "n_c", "span", "named_by")} if val else None)})
    out = {"n": len(rows), "tally": dict(tally), "rows": rows}
    with open(os.path.join(BOUT, "locate.json.tmp"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(os.path.join(BOUT, "locate.json.tmp"), os.path.join(BOUT, "locate.json"))
    print(json.dumps({"n": out["n"], "tally": out["tally"]}))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
