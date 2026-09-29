"""SECOND READER on the screening exclusions that decide most of the k gap (step-2 finding, 2026-09-29).

Adapter 1's counterfactual put the 71 never-identified comparator members through our unchanged screener: 61 were
EXCLUDED by a rule. Most are real scope differences (the comparator is broader than our registered PICO), but some
look like screener false negatives (omega-3: two ICD-arrhythmia trials 'population not cardiovascular'). Which is
which decides whether the gap is closable at all, so each exclusion gets a recorded model reading.

Same instrument as scripts/model_source_pilot.py's screening task -- its SCREEN_INSTR prompt, registered criteria,
schema, held-text format and reproducible_ai.model_source.verify_screening gate (per-axis MET / NOT_MET / NOT_STATED,
each MET/NOT_MET quoting the held record; the decision is DERIVED by the verifier, never taken from the model).
A RULE_MODEL_DISAGREE is a candidate screener defect for adjudication. Nothing here changes a screening decision.

    python scripts/k_gap_screen_recheck.py --run      # live, concurrency 3, one recorded call per batch of <=6
    python scripts/k_gap_screen_recheck.py --verify   # re-derive every verification from stored records (no network)
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import importlib.util
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
PROP = os.path.join(ROOT, "registry", "model_proposals", "k_gap_screen_recheck.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT, BATCH = "gpt-6-astra", "medium", 6
TASK = "screening_excluded"          # the pilot task whose prompt/schema this reuses


def _pilot():
    spec = importlib.util.spec_from_file_location("model_source_pilot", os.path.join(ROOT, "scripts", "model_source_pilot.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def items() -> list[dict]:
    """One item per comparator member the counterfactual screener EXCLUDED: its surviving record, rule id, reason."""
    from harness import fetch
    pilot = _pilot()
    cfm = _j(os.path.join(OUT, "counterfactual_members.json"))
    want = []
    for slug, v in sorted(cfm.items()):
        for pmid, f in sorted((v.get("funnel") or {}).items()):
            if f.get("stage") == "SCREENED_OUT":
                want.append((slug, pmid, f))
    cache_p = os.path.join(OUT, "member_records.json")
    cache = _j(cache_p) if os.path.exists(cache_p) else {}
    todo = sorted({p for _, p, _ in want if p not in cache})
    if todo:
        for r in fetch._efetch(todo):
            cache[r["id"]] = r
        with open(cache_p, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    out = []
    for slug, pmid, f in want:
        rec = cache.get(pmid)
        it = {"slug": slug, "item_id": f"{slug}::pmid:{pmid}", "pmid": pmid, "rule_decision": "exclude",
              "rule_id": f.get("rule_id"), "rule_reason": f.get("reason"),
              "held_ref": f"outputs/k_gap/member_records.json#{pmid}"}
        if rec:
            t = pilot.held_text_screening(rec)
            it.update(held_text=t, held_sha256=_sha(t.encode("utf-8")))
        out.append(it)
    return out


def table_items() -> list[dict]:
    """--table: the k-gap table's confirmed-member SCREEN_OR_ELIGIBILITY rows (screen_audit.json), i.e. comparator
    trials our screener excluded from a corpus we ALREADY held -- the record is the topic's own pinned one."""
    pilot = _pilot()
    audit = _j(os.path.join(OUT, "screen_audit.json"))
    recs = {}
    out = []
    for r in audit["rows"]:
        if not r.get("confirmed_member") or not r.get("rule_id"):
            continue
        s = r["slug"]
        if s not in recs:
            rj = _j(os.path.join(ROOT, "cache", s, "records.json"))
            recs[s] = {x.get("id"): x for x in rj.get("records", []) + rj.get("ctgov", [])}
        pmid = next((p for p in r["pmids"] if p in recs[s]), None)
        it = {"slug": s, "item_id": f"{s}::table:{r['label'][:40]}", "pmid": pmid, "rule_decision": "exclude",
              "rule_id": r["rule_id"], "rule_reason": r.get("reason"), "audit_class": r.get("class"),
              "held_ref": f"cache/{s}/records.json#{pmid}"}
        if pmid:
            t = pilot.held_text_screening(recs[s][pmid])
            it.update(held_text=t, held_sha256=_sha(t.encode("utf-8")))
        out.append(it)
    return out


def batches(its: list[dict]) -> list[dict]:
    pilot = _pilot()
    by = {}
    for i in its:
        if "held_text" in i:
            by.setdefault(i["slug"], []).append(i)
    out = []
    for slug in sorted(by):
        g = by[slug]
        crit, cd = pilot.criteria(slug)
        for k in range(0, len(g), BATCH):
            keyed = [(f"R{n + 1}", i) for n, i in enumerate(g[k:k + BATCH])]
            body = pilot.SCREEN_INSTR + "\n=== REGISTERED CRITERIA ===\n" + crit + "\n"
            for key, i in keyed:
                body += f"\n=== RECORD item={key} ===\n{i['held_text']}\n"
            out.append({"slug": slug, "batch": f"{slug}#{k // BATCH + 1}", "prompt": body.encode("utf-8"),
                        "keyed": keyed, "digests": cd + [{"ref": i["held_ref"], "sha256": i["held_sha256"],
                                                          "what": "held record quoted by the item"} for _, i in keyed]})
    return out


def run_one(b) -> dict:
    from reproducible_ai import model_call_live
    pilot = _pilot()
    rec = model_call_live.call(b["prompt"], schema=pilot._schema(TASK), model=MODEL, effort=EFFORT,
                               caller={"file": "scripts/k_gap_screen_recheck.py", "line": "run_one",
                                       "purpose": f"k-gap screening second reader {b['batch']} (acq/k-gap lane)"},
                               input_digests=b["digests"], timeout_s=1200)
    ms.write_record(rec, REC_DIR)
    return {"batch": b["batch"], "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": _sha(b["prompt"])}


def verify(its, bs, runs) -> dict:
    by_prompt = {r["prompt_sha256"]: r for r in runs.values()}
    rows = []
    for b in bs:
        run = by_prompt.get(_sha(b["prompt"]))
        if not run or run["state"] != "RAN_OK":
            for key, i in b["keyed"]:
                rows.append({"item_id": i["item_id"], "state": "NO_RAN_OK_RECORD"})
            continue
        rec = ms.load_record(os.path.join(REC_DIR, run["record_id"] + ".json"))
        try:
            resp = json.loads(ms.replay(rec).decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            for key, i in b["keyed"]:
                rows.append({"item_id": i["item_id"], "state": "UNPARSEABLE", "error": str(exc)[:120]})
            continue
        got = {x.get("item"): x for x in resp.get("items", [])}
        for key, i in b["keyed"]:
            claim = got.get(key)
            v = ms.verify_screening(claim or {}, i["held_text"], i["rule_decision"])
            rows.append({"item_id": i["item_id"], "slug": i["slug"], "pmid": i["pmid"], "rule_id": i["rule_id"],
                         "audit_class": i.get("audit_class"),
                         "rule_reason": i["rule_reason"], "record_id": run["record_id"], "response_item": key,
                         "verification": v, "claim": claim})
    from collections import Counter
    agr = Counter((r.get("verification") or {}).get("agreement", r.get("state", "?")).split("(")[0] for r in rows)
    return {"task": "k_gap_screen_recheck", "instrument": f"scripts/model_source_pilot.py task={TASK} prompt/schema + "
            "reproducible_ai.model_source.verify_screening", "N_items": len(its),
            "N_callable": sum("held_text" in i for i in its), "agreement": dict(agr), "rows": rows}


def main(argv):
    global PROP
    if "--table" in argv:
        PROP = PROP.replace(".json", ".table.json")
    its = table_items() if "--table" in argv else items()
    bs = batches(its)
    data = _j(PROP) if os.path.exists(PROP) else {}
    runs = data.get("runs", {})
    if "--run" in argv:
        done = {r["prompt_sha256"] for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [b for b in bs if _sha(b["prompt"]) not in done]
        print(f"items {len(its)}, batches {len(bs)}, to run {len(todo)}", flush=True)
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(run_one, todo):
                runs[r["batch"]] = r
                print(r["batch"], r["state"], r["record_id"], flush=True)
    out = verify(its, bs, runs)
    out["runs"] = runs
    os.makedirs(os.path.dirname(PROP), exist_ok=True)
    with open(PROP, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print(json.dumps({k: out[k] for k in ("N_items", "N_callable", "agreement")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
