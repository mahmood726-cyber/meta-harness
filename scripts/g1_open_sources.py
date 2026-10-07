"""OPEN SEARCH SOURCES for the active G1 topics (decision 7 Oct, Mahmood: open sources only -- no CENTRAL, no Embase):
OpenAlex (CC0 bibliographic index, api.openalex.org) and WHO ICTRP (trial registrations).

OpenAlex, per topic:
  proposal   one recorded BLIND Codex job writes an OpenAlex title_and_abstract.search boolean for the registered PICO
             (it sees the question, eligibility, PICO and the registered PubMed queries -- never a comparator trial)
  volume     GET /works?filter=title_and_abstract.search:<q> -> meta.count
  recall     every PMID of every comparator trial in ONE batched call, with and without the query:
             indexed = the work exists in OpenAlex; abstract = its abstract_inverted_index is present; matched = the
             query returns it. Recall gain = an ELIGIBLE trial OpenAlex identifies that the current registered PubMed
             queries do not (outputs/search_audit/active/ACTIVE_AUDIT.json search_current).
  miss type  for every ELIGIBLE trial OpenAlex does not identify: IDENTITY_NO_PMID (no PMID for the trial),
             NOT_INDEXED (no OpenAlex work for any of its PMIDs), INDEXED_TITLE_ONLY (indexed, no abstract in OpenAlex,
             title does not match), QUERY_GAP (indexed with abstract, the query does not match)
  Every HTTP call is recorded (url, status, sha256 of the body, count, the API's own cost header).

WHO ICTRP: trialsearch.who.int/robots.txt is 'User-agent: * / Disallow: /' and WHO offers its web service and crawling
service to agreed partners only; the open route is the Search Portal's CSV/XML export or the full-dataset request form,
both a PERSON's action. This script therefore never queries ICTRP; each topic is typed NOT_RUN_ACCESS (the robots.txt
body and its sha256 are recorded) until an export is supplied (--ictrp-export <csv>), which it then measures.

  python scripts/g1_open_sources.py [--run]   -> outputs/search_audit/active/open_sources.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_query_audit as Q  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

SA = ROOT / "outputs" / "search_audit" / "active"
OUT = SA / "open_sources.json"
IDX = SA / "open_sources_records.json"
OA = "https://api.openalex.org/works"
MAILTO = "meta-harness@example.org"
UA = {"User-Agent": f"meta-harness/1.0 (mailto:{MAILTO})"}
ICTRP_ROBOTS = "https://trialsearch.who.int/robots.txt"
MODEL = "gpt-6-astra"

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["openalex_search", "concepts", "rationale"],
          "properties": {"openalex_search": {"type": "string"}, "rationale": {"type": "string"},
                         "concepts": {"type": "array", "items": {"type": "string"}}}}

INSTR = """You are an information specialist adding an OPEN bibliographic source to the registered search of one
systematic review. Do not run any commands or read any files. Use only the text given here.
Write ONE OpenAlex search for this question, for the API filter title_and_abstract.search (it searches titles and
abstracts; Boolean operators AND, OR, NOT in upper case; double quotes for exact phrases; parentheses for grouping; NO
wildcards or truncation -- OpenAlex stems words itself; no field tags). Combine the population/condition concept and the
intervention concept (synonyms, drug and brand names, spelling variants) and a randomised-trial concept (random*, written
out as words such as randomized OR randomised OR randomly OR placebo OR trial). Do NOT restrict by outcome, date or
language. Do NOT name or target specific trials. Return only the JSON object.
"""


def get(params):
    u = OA + "?" + urllib.parse.urlencode({**params, "mailto": MAILTO})
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r:
                b = r.read()
                cost = r.headers.get("X-RateLimit-Cost-USD")
                time.sleep(0.3)
                return r.status, b, u, cost
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < 4:
                time.sleep(3 * (i + 1) ** 2)
                continue
            return e.code, e.read() if hasattr(e, "read") else b"", u, None
        except Exception:  # noqa: BLE001 -- retried, then reported as a failed request
            time.sleep(3 * (i + 1))
    return None, b"", u, None


def rec(st, b, u, cost, **kw):
    return {"url": u, "http": st, "sha256": hashlib.sha256(b).hexdigest(), "cost_usd": cost, **kw}


def prompt(slug):
    pb, dg = Q.prompt(slug, json.load(open(Q.VOL, encoding="utf-8")))
    body = pb.decode("utf-8").replace(Q.INSTR, INSTR, 1)
    assert INSTR in body
    return body.encode("utf-8"), dg


def call(pb, dg, slug):
    from reproducible_ai import model_call_live
    r = model_call_live.call(pb, schema=SCHEMA, model=MODEL, effort="high",
                             caller={"file": "scripts/g1_open_sources.py", "lane": "search-screen-audit", "line": "call",
                                     "purpose": f"G1 open sources: blind OpenAlex search proposal, {slug}"},
                             input_digests=dg)
    return ms.write_record(r, Q.REC_DIR).name, r


def works_by_pmid(pmids, query=None):
    """{pmid: {'abstract': bool, 'title': str}} for the PMIDs OpenAlex holds (matched by the query when given)."""
    f = "ids.pmid:" + "|".join(pmids) + (f",title_and_abstract.search:{query}" if query else "")
    st, b, u, cost = get({"filter": f, "select": "id,ids,display_name,abstract_inverted_index", "per-page": 200})
    out = {}
    try:
        for w in json.loads(b)["results"]:
            pm = str((w.get("ids") or {}).get("pmid") or "").rstrip("/").split("/")[-1]
            if pm:
                out[pm] = {"abstract": bool(w.get("abstract_inverted_index")), "title": w.get("display_name") or ""}
        ok = True
    except Exception:  # noqa: BLE001
        ok = False
    return (out if ok else None), rec(st, b, u, cost, n=len(out) if ok else None)


def openalex_topic(t, q):
    calls = []
    st, b, u, cost = get({"filter": f"title_and_abstract.search:{q}", "select": "id", "per-page": 1})
    try:
        vol = json.loads(b)["meta"]["count"]
    except Exception:  # noqa: BLE001
        vol = None
    calls.append(rec(st, b, u, cost, count=vol))
    pms = sorted({p for r in t["trials"] for p in r["pmids"]})
    held, matched = {}, {}
    for i in range(0, len(pms), 40):
        h, c1 = works_by_pmid(pms[i:i + 40])
        m, c2 = works_by_pmid(pms[i:i + 40], q)
        calls += [c1, c2]
        if h is None or m is None:
            return {"state": "RAN_ERROR", "calls": calls}
        held.update(h)
        matched.update(m)
    rows = []
    for r in t["trials"]:
        hit = sorted(set(r["pmids"]) & set(matched))
        idx = sorted(set(r["pmids"]) & set(held))
        miss = None
        if not hit:
            miss = ("IDENTITY_NO_PMID" if not r["pmids"] else "NOT_INDEXED" if not idx else
                    "INDEXED_TITLE_ONLY" if not any(held[p]["abstract"] for p in idx) else "QUERY_GAP")
        rows.append({"label": r["label"], "kind": r["kind"], "pmids": r["pmids"], "indexed": idx,
                     "abstract_in_openalex": [p for p in idx if held[p]["abstract"]], "openalex_hits": hit,
                     "search_current": r["search_current"], "openalex_identifies": bool(hit),
                     "gain": bool(hit) and r["search_current"] != "IDENTIFIED", "miss_type": miss})
    el = [x for x in rows if x["kind"] == "ELIGIBLE"]
    return {"state": "RAN_OK", "volume": vol, "calls": calls, "trials": rows,
            "recall_openalex": {"n": sum(x["openalex_identifies"] for x in el), "N": len(el)},
            "recall_current_pubmed": {"n": sum(x["search_current"] == "IDENTIFIED" for x in el), "N": len(el)},
            "recall_union": {"n": sum(x["openalex_identifies"] or x["search_current"] == "IDENTIFIED" for x in el),
                             "N": len(el)},
            "gain": [x["label"] for x in el if x["gain"]],
            "miss_types": {k: [x["label"] for x in el if x["miss_type"] == k]
                           for k in ("IDENTITY_NO_PMID", "NOT_INDEXED", "INDEXED_TITLE_ONLY", "QUERY_GAP")}}


def ictrp_state(export_csv=None):
    req = urllib.request.Request(ICTRP_ROBOTS, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            st, b = r.status, r.read()
    except Exception as e:  # noqa: BLE001
        st, b = None, repr(e).encode()
    robots = {"url": ICTRP_ROBOTS, "http": st, "sha256": hashlib.sha256(b).hexdigest(),
              "body": b.decode("utf-8", "replace")[:200]}
    if not export_csv:
        return {"state": "NOT_RUN_ACCESS", "robots": robots,
                "why": "automated access disallowed (robots.txt Disallow: /); web service and crawling service are for "
                       "agreed partners; the open route is a person's Search Portal CSV/XML export or the WHO "
                       "full-dataset request form"}
    rows = list(csv.DictReader(open(export_csv, encoding="utf-8-sig")))
    return {"state": "EXPORT_SUPPLIED", "robots": robots, "export_sha256": hashlib.sha256(Path(export_csv).read_bytes()).hexdigest(),
            "n_rows": len(rows), "trial_ids": sorted({(r.get("TrialID") or "").strip() for r in rows if r.get("TrialID")})}


PRECISE = ("\nPRECISION TARGET: an earlier blind OpenAlex proposal for this question returned {n} records, too many to "
           "screen (the budget is 10,000). Write a search that keeps the population and intervention concepts complete "
           "but stays under about 9,000 records. Still do NOT name or target specific trials.\n")


def main(argv):
    global OUT, IDX
    from g1_active_recall import active_topics
    live = "--run" in argv
    slugs, _ = active_topics()
    base = None
    if "--precise" in argv:                     # over-cap topics only; the first round's volumes are the only input
        base = json.load(open(OUT, encoding="utf-8"))["topics"]
        slugs = [s for s in slugs if ((base.get(s) or {}).get("openalex") or {}).get("volume", 0) > 10000]
        OUT, IDX = OUT.with_name("open_sources_precise.json"), IDX.with_name("open_sources_precise_records.json")
    act = {t["slug"]: t for t in json.load(open(SA / "ACTIVE_AUDIT.json", encoding="utf-8"))["topics"]}
    idx = json.load(open(IDX, encoding="utf-8")) if IDX.exists() else {}
    prompts = {s: prompt(s) for s in slugs}
    if base:
        for s_ in slugs:
            pb, dg = prompts[s_]
            pb = pb.replace(b"Return only the JSON object.\n", (PRECISE.format(n=base[s_]["openalex"]["volume"])
                                                                 + "Return only the JSON object.\n").encode("utf-8"), 1)
            assert b"PRECISION TARGET" in pb
            prompts[s_] = (pb, dg + [{"ref": "outputs/search_audit/active/open_sources.json",
                                      "sha256": Q._sha((SA / "open_sources.json").read_bytes()),
                                      "what": "the first blind OpenAlex proposal's measured volume (no trial information)"}])
    if live:
        import concurrent.futures as cf
        todo = [(s, pb, dg) for s, (pb, dg) in prompts.items() if Q._sha(pb) not in idx]
        with cf.ThreadPoolExecutor(5) as ex:
            futs = {ex.submit(call, pb, dg, s): (s, pb) for s, pb, dg in todo}
            for f in cf.as_completed(futs):
                s, pb = futs[f]
                try:
                    name, r = f.result()
                    if r.get("state") == "RAN_OK":
                        idx[Q._sha(pb)] = name
                    print(f"  {s}: {r['state']}", flush=True)
                except Exception as exc:  # noqa: BLE001
                    print(f"  {s}: FAILED {exc}", flush=True)
        json.dump(idx, open(IDX, "w", encoding="utf-8", newline="\n"), indent=0)
    prev = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else {"topics": {}}
    ex_csv = argv[argv.index("--ictrp-export") + 1] if "--ictrp-export" in argv else None
    ictrp = ictrp_state(ex_csv)
    res = {}
    for s in slugs:
        name = idx.get(Q._sha(prompts[s][0]))
        if not name:
            res[s] = {"state": "NO_PROPOSAL"}
            continue
        claim = json.loads(ms.replay(ms.load_record(Q.REC_DIR / name)).decode("utf-8"))
        old = (prev["topics"].get(s) or {})
        if live or old.get("record") != name:
            oa = openalex_topic(act[s], claim["openalex_search"])
        else:
            oa = old.get("openalex")
        res[s] = {"record": name, "proposal": claim, "openalex": oa, "ictrp": {"state": ictrp["state"]}}
        o = oa or {}
        print(s, "| OpenAlex", o.get("state"), "vol", o.get("volume"), "| openalex", o.get("recall_openalex"), "pubmed",
              o.get("recall_current_pubmed"), "union", o.get("recall_union"), "| gain", o.get("gain"),
              "| misses", {k: len(v) for k, v in (o.get("miss_types") or {}).items() if v}, flush=True)
    el = lambda k: {"n": sum((v.get("openalex") or {}).get(k, {}).get("n", 0) for v in res.values()),  # noqa: E731
                    "N": sum((v.get("openalex") or {}).get(k, {}).get("N", 0) for v in res.values())}
    out = {"schema": 1, "decision": "open sources only (Mahmood 7 Oct): OpenAlex + WHO ICTRP, additive", "ictrp": ictrp,
           "totals": {k: el(k) for k in ("recall_openalex", "recall_current_pubmed", "recall_union")},
           "topics": res}
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps(out["totals"]))


if __name__ == "__main__":
    main(sys.argv[1:])
