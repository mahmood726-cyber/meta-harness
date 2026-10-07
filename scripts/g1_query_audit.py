"""PER-TOPIC QUERY AUDIT (search+screen audit): one recorded Codex job per G1 topic proposes a CONCEPT search (PubMed +
CT.gov) for the topic's registered PICO; the harness then VALIDATES the proposal by recorded probes. Nothing is applied
here: an accepted proposal becomes a dated protocol amendment (scripts/g1_search_amend.py), never a silent edit.

BLIND BY DESIGN: the model sees the topic's question, registered eligibility, PICO and its current registered queries
with their measured volumes -- NEVER the comparator's trials, their titles or identifiers, nor which trials our search
missed. Recall is then measured on the comparator's eligible trials, which the proposal was not tuned on (the model may
still know famous trials from training: stated as a limitation, not hidden).

Validation (recorded: URL, HTTP, count, sha256), per proposal:
  volume     esearch count of the proposed PubMed query; CT.gov totalCount of the proposed cond/intr
  recall     for every ELIGIBLE comparator trial with a PMID: does '(<query>) AND <pmid>[uid]' match? (same for NCTs
             against the proposed CT.gov query) -- current registered queries probed the same way, so the two are compared
             on identical trials
  accept     ACCEPT when recall(proposed OR current) > recall(current) with no trial lost and volume <= VOLUME_CAP;
             else KEEP_CURRENT with the reason. Proposed queries are ADDED to the registered ones (union), never replace them.

  python scripts/g1_query_audit.py --run [--workers 5] [SLUG ...]   (live model calls + probes)
  python scripts/g1_query_audit.py                                    (offline: re-derive from records + probes)
  -> outputs/search_audit/query_audit.json
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from reproducible_ai import model_source as ms  # noqa: E402
import g1_search_miss_probe as probe  # noqa: E402

AUDIT = ROOT / "outputs" / "search_audit" / "SEARCH_SCREEN_AUDIT.json"
VOL = ROOT / "outputs" / "search_audit" / "search_volume_probe.json"
OUT = ROOT / "outputs" / "search_audit" / "query_audit.json"
IDX = ROOT / "outputs" / "search_audit" / "query_audit_records.json"
REC_DIR = ROOT / ms.RECORD_DIR
MODEL, EFFORT = "gpt-6-astra", "high"
VOLUME_CAP = 5000

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["pubmed_query", "ctgov_cond", "ctgov_intr", "concepts", "rationale", "weaknesses_of_current"],
          "properties": {"pubmed_query": {"type": "string"}, "ctgov_cond": {"type": "string"},
                         "ctgov_intr": {"type": "string"}, "rationale": {"type": "string"},
                         "concepts": {"type": "array", "items": {"type": "string"}},
                         "weaknesses_of_current": {"type": "array", "items": {"type": "string"}}}}

INSTR = """You are an information specialist auditing the registered literature search of one systematic review.
Do not run any commands or read any files. Use only the text given here.
Write ONE PubMed search that a Cochrane information specialist would register for this question: combine the
population/condition concept and the intervention concept (each as MeSH terms OR title/abstract synonyms, including
drug names, brand names, class names and spelling variants), AND a randomised-trial filter (the Cochrane Highly
Sensitive Search Strategy, sensitivity-maximising version, or an equivalent). Do NOT restrict by outcome, by publication
date, or by language. Do NOT name or target specific trials. Also give the ClinicalTrials.gov condition and intervention
terms (query.cond, query.intr) for the same concepts. List the weaknesses of the CURRENT registered queries.
Return only the JSON object.
"""


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def prompt(slug, vol):
    cfg = json.load(open(ROOT / "topics" / f"{slug}.json", encoding="utf-8"))
    pico = {t["id"]: t for t in json.load(open(ROOT / "pico.json", encoding="utf-8"))["topics"]}.get(slug) or {}
    v = vol["topics"].get(slug) or {}
    cur = "\n".join(f"  PubMed: {q['query']}  (returns {q['count_today']} records today)" for q in v.get("pubmed_queries") or [])
    cur += f"\n  ClinicalTrials.gov: {json.dumps(v.get('ctgov_query'))}  (returns {v.get('ctgov_count_today')} studies today)"
    lines = [INSTR, "=== REVIEW ===", f"Title: {cfg.get('title')}", f"Question: {cfg.get('question')}",
             f"Registered eligibility: {cfg.get('eligibility_summary')}"]
    for k, lab in (("P", "Population"), ("I", "Intervention"), ("C", "Comparator"), ("O", "Outcome")):
        if pico.get(k):
            lines.append(f"{lab}: {pico[k]}")
    lines += ["", "=== CURRENT REGISTERED QUERIES ===", cur]
    digests = [{"ref": f"topics/{slug}.json", "sha256": _sha((ROOT / "topics" / f"{slug}.json").read_bytes()),
                "what": "topic config"},
               {"ref": "outputs/search_audit/search_volume_probe.json", "sha256": _sha(VOL.read_bytes()),
                "what": "measured volumes of the current queries"}]
    return "\n".join(lines).encode("utf-8"), digests


def _claim(rec):
    return json.loads(ms.replay(rec).decode("utf-8"))


PRECISE = ("\nPRECISION TARGET: an earlier blind proposal for this question returned {n} PubMed records, too many to "
           "screen. Write a search that keeps the population and intervention concepts complete but stays under about "
           "4,000 records (e.g. a precision-maximising RCT filter, the intervention as a focused MeSH/major-topic concept). "
           "Still do NOT name or target specific trials.\n")


def _round(argv):
    """(tag, model, out, idx): r1 (default, gpt-6-astra), r2 (independent proposer, gpt-5.5), precise (over-cap topics)."""
    if "--precise" in argv:
        return "precise", "gpt-6-astra", OUT.with_name("query_audit_precise.json"), IDX.with_name("query_audit_precise_records.json")
    if "--round" in argv and argv[argv.index("--round") + 1] == "r2":
        return "r2", "gpt-5.5", OUT.with_name("query_audit_r2.json"), IDX.with_name("query_audit_r2_records.json")
    return "r1", MODEL, OUT, IDX


def current_queries(slug):
    """The queries registered NOW (topics config, after the dated amendments): a later round's gain is measured against
    these, so a query an earlier round already added is not counted again."""
    cfg = json.load(open(ROOT / "topics" / f"{slug}.json", encoding="utf-8"))
    return {"pubmed": cfg.get("pubmed_queries") or [], "ctgov": cfg.get("ctgov") or {}}


def call(pb, dg, slug, model=None):
    from reproducible_ai import model_call_live
    rec = model_call_live.call(pb, schema=SCHEMA, model=model or MODEL, effort=EFFORT,
                               caller={"file": "scripts/g1_query_audit.py", "lane": "search-screen-audit", "line": "call",
                                       "purpose": f"G1 query audit (blind concept search proposal), {slug}"},
                               input_digests=dg)
    return ms.write_record(rec, REC_DIR).name, rec


def ctgov_match(nct, cond, intr):
    p = {"filter.ids": nct, "fields": "protocolSection.identificationModule.nctId", "pageSize": 5}
    if cond:
        p["query.cond"] = cond
    if intr:
        p["query.intr"] = intr
    st, b, u = probe.get(probe.CTG, p)
    try:
        ok = any(x["protocolSection"]["identificationModule"]["nctId"] == nct for x in json.loads(b).get("studies") or [])
    except Exception:  # noqa: BLE001
        ok = None
    return ok, probe.rec(st, b, u, matched=ok)


def validate(slug, claim, trials, current):
    calls, rows = [], []
    n, c = probe.esearch_count(claim["pubmed_query"])
    calls.append(c)
    ct_total, c2 = __import__("g1_search_volume_probe").ctgov_total({"cond": claim["ctgov_cond"], "intr": claim["ctgov_intr"]})
    calls.append(c2)
    for r in trials:
        cur = new = False
        for pm in r["pmids"]:
            m, c = probe.esearch_count(f"({claim['pubmed_query']}) AND {pm}[uid]")
            calls.append(c)
            new = new or bool(m)
            for q in current.get("pubmed") or []:
                m2, c = probe.esearch_count(f"({q}) AND {pm}[uid]")
                calls.append(c)
                cur = cur or bool(m2)
        for nc in r["ncts"]:
            m, c = ctgov_match(nc, claim["ctgov_cond"], claim["ctgov_intr"])
            calls.append(c)
            new = new or bool(m)
            cq = current.get("ctgov") or {}
            if cq:
                m2, c = ctgov_match(nc, cq.get("cond"), cq.get("intr"))
                calls.append(c)
                cur = cur or bool(m2)
        rows.append({"label": r["label"], "current_matches": cur, "proposed_matches": new})
    cur_n = sum(r["current_matches"] for r in rows)
    union_n = sum(r["current_matches"] or r["proposed_matches"] for r in rows)
    lost = [r["label"] for r in rows if r["current_matches"] and not r["proposed_matches"]]
    vol_ok = n is not None and n <= VOLUME_CAP
    verdict = ("ACCEPT" if union_n > cur_n and vol_ok else
               "KEEP_CURRENT: " + ("no recall gain" if union_n <= cur_n else f"volume {n} > cap {VOLUME_CAP}"))
    return {"proposed_pubmed_count": n, "proposed_ctgov_count": ct_total, "per_trial": rows,
            "recall_current": {"n": cur_n, "N": len(rows)}, "recall_union": {"n": union_n, "N": len(rows)},
            "proposed_alone_loses": lost, "verdict": verdict, "calls": calls}


def main(argv):
    live = "--run" in argv
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 5
    tag, model, out_p, idx_p = _round(argv)
    slugs_arg = [a for a in argv if not a.startswith("--") and not a.isdigit() and a != "r2"]
    a = json.load(open(AUDIT, encoding="utf-8"))
    vol = json.load(open(VOL, encoding="utf-8"))
    idx = json.load(open(idx_p, encoding="utf-8")) if idx_p.exists() else {}
    prev = json.load(open(out_p, encoding="utf-8")) if out_p.exists() else {"topics": {}}
    r1 = json.load(open(OUT, encoding="utf-8"))["topics"] if OUT.exists() else {}
    topics = [t for t in a["topics"] if not slugs_arg or t["slug"] in slugs_arg]
    if tag == "precise":
        topics = [t for t in topics if "volume" in str(((r1.get(t["slug"]) or {}).get("validation") or {}).get("verdict", ""))]
    prompts = {}
    for t in topics:
        pb, dg = prompt(t["slug"], vol)
        if tag == "precise":
            n = r1[t["slug"]]["validation"]["proposed_pubmed_count"]
            pb = pb.replace(b"Return only the JSON object.\n", (PRECISE.format(n=n) + "Return only the JSON object.\n").encode("utf-8"), 1)
            dg = dg + [{"ref": "outputs/search_audit/query_audit.json", "sha256": _sha(OUT.read_bytes()),
                        "what": "the earlier blind proposal's measured volume (no trial information)"}]
        prompts[t["slug"]] = (pb, dg)
    if live:
        todo = [(s, pb, dg) for s, (pb, dg) in prompts.items() if _sha(pb) not in idx]
        print(f"query audit: {len(todo)} topics to call", flush=True)
        with cf.ThreadPoolExecutor(workers) as ex:
            futs = {ex.submit(call, pb, dg, s, model): (s, pb) for s, pb, dg in todo}
            for f in cf.as_completed(futs):
                s, pb = futs[f]
                try:
                    name, rec = f.result()
                    if rec.get("state") == "RAN_OK":
                        idx[_sha(pb)] = name
                    print(f"  {s}: {rec['state']}", flush=True)
                except Exception as exc:  # noqa: BLE001
                    print(f"  {s}: FAILED {exc}", flush=True)
        json.dump(idx, open(idx_p, "w", encoding="utf-8", newline="\n"), indent=0)
    for t in topics:
        pb, _ = prompts[t["slug"]]
        name = idx.get(_sha(pb))
        if not name:
            continue
        rec = ms.load_record(REC_DIR / name)
        claim = _claim(rec)
        entry = {"record": name, "proposal": claim}
        old = prev["topics"].get(t["slug"]) or {}
        if live or old.get("record") != name:
            trials = [r for r in t["trials"] if r["kind"] == "ELIGIBLE" and (r["pmids"] or r["ncts"])]
            cur = t["registered_queries"] if tag == "r1" else current_queries(t["slug"])
            entry["validation"] = validate(t["slug"], claim, trials, cur)
            entry["round"], entry["model"] = tag, model
        else:
            entry["validation"] = old.get("validation")
        prev["topics"][t["slug"]] = entry
        v = entry["validation"] or {}
        print(t["slug"], "|", v.get("verdict"), "| current", v.get("recall_current"), "union", v.get("recall_union"),
              "| volume", v.get("proposed_pubmed_count"), flush=True)
    json.dump(prev, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1:])
