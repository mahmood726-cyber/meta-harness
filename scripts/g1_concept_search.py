"""CONCEPT SEARCHES for the active topics (external audit R5-4 / R9b F9-2: recall misses BOTTICELLI DVT and J-EINSTEIN (doac),
FIVE-STAR 41351003 (finerenone) appear in no cache, ledger or page; GLP-1's retrieval ledger is a PMID enumeration only).
Mahmood 9 Oct: "work hard on evidence completeness".

Per topic, concept queries built from the protocol's OWN terms (topics/<slug>.json include.intervention_any +
population_any), widened by the same typed tables the shadow re-screen uses (development codes; population synonyms):
  PUBMED      esearch: (intervention concept) AND (population concept) AND RCT filter
              (randomized controlled trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab])
  CTGOV       API v2: query.intr + query.cond, interventional + randomized, all statuses (paged to its own count)
  EUROPEPMC   REST search: same concepts, SRC:MED OR SRC:PPR, with an RCT clause (paged to its own count)
  EUCTR       EU Clinical Trials Register search on the intervention concept (EudraCT numbers; results flag)
Every query is RECORDED: text, date, the source's own hit count, every returned id, a sha256 of each response page.
A source paged short of its own count is written TRUNCATED, never complete.

DEDUP against everything the harness already holds for the topic: cache/<slug>/records.json (records + ctgov),
cache/<slug>/retrieval_ledger.json, docs/reviews/<slug>/review.json screening ids, the G1 tracker's trial units.
NEW ids -> their records (PubMed efetch / CT.gov API v2), held at outputs/k_gap/concept/<slug>.records.json.

    python scripts/g1_concept_search.py SLUG [SLUG ...] -> outputs/k_gap/concept/<slug>.json
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "concept")
CAP = 5000
RCT_PM = "(randomized controlled trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab])"
KNOWN_MISSES = {"doac-vte-recurrence": ["BOTTICELLI", "J-EINSTEIN"], "finerenone-ckd-t2d-renal": ["41351003", "NCT05887817"]}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, params=None, tries=4):
    """(status, bytes) with bounded retry and backoff; a failure is returned typed, never raised into a 'no hits'."""
    from harness import http
    last = None
    for i in range(tries):
        try:
            st, b = http.get_raw(url, params, tries=1, timeout=90)
            if st in (429, 500, 502, 503, 504):
                raise RuntimeError(f"HTTP {st}")
            return st, b
        except Exception as exc:  # noqa: BLE001 - retried, then typed
            last = exc
            time.sleep(1.5 * (2 ** i))
    return "FETCH_FAILED", str(last).encode()


def concepts(cfg):
    import g1_shadow_rescreen as sh
    inc = cfg.get("include") or {}
    ints = list(dict.fromkeys([t for t in (inc.get("intervention_any") or []) if len(t) >= 3]))
    for inn, codes in sh.DEV_CODES.items():
        if any(inn in t.lower() or t.lower() in inn for t in ints):
            ints += codes
    pops = list(dict.fromkeys([t for t in (inc.get("population_any") or []) + (inc.get("population_any_extra") or [])
                               if len(t) >= 3]))
    pa = " ".join(p.lower() for p in pops)
    for concept, syns in sh.POP_SYNONYMS.items():
        if concept in pa or any(s in pa for s in syns):
            pops += [concept] + syns
    return list(dict.fromkeys(ints)), list(dict.fromkeys(pops))


def _q(terms, field):
    return "(" + " OR ".join(f'"{t}"{field}' for t in terms) + ")"


def pubmed(ints, pops):
    q = f"{_q(ints, '[tiab]')} AND {_q(pops, '[tiab]')} AND {RCT_PM}"
    st, b = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                {"db": "pubmed", "term": q, "retmax": CAP, "retmode": "json", "tool": "meta-harness",
                 "email": "meta-harness@example.org"})
    time.sleep(0.4)
    rec = {"source": "PUBMED", "query": q, "run_utc": now(), "status": st, "pages_sha256": [hashlib.sha256(b).hexdigest()]}
    if st != 200:
        return dict(rec, state="FETCH_FAILED", error=b[:200].decode("utf-8", "replace"), ids=[])
    d = json.loads(b)["esearchresult"]
    n, ids = int(d.get("count") or 0), d.get("idlist") or []
    return dict(rec, state="COMPLETE" if len(ids) >= n else "TRUNCATED", hits=n, ids=ids)


def ctgov(ints, pops):
    q_i, q_c = " OR ".join(ints), " OR ".join(pops)
    ids, shas, token, n = [], [], None, None
    while True:
        params = {"query.intr": q_i, "query.cond": q_c, "pageSize": 1000, "countTotal": "true", "fields": "NCTId",
                  "filter.advanced": "AREA[StudyType]INTERVENTIONAL AND AREA[DesignAllocation]RANDOMIZED"}
        if token:
            params["pageToken"] = token
        st, b = get("https://clinicaltrials.gov/api/v2/studies", params)
        shas.append(hashlib.sha256(b).hexdigest())
        if st != 200:
            return {"source": "CTGOV", "query": {"intr": q_i, "cond": q_c, "filter": params["filter.advanced"]},
                    "run_utc": now(), "state": "FETCH_FAILED", "error": b[:200].decode("utf-8", "replace"), "ids": ids,
                    "pages_sha256": shas}
        d = json.loads(b)
        n = d.get("totalCount", n)
        ids += [s["protocolSection"]["identificationModule"]["nctId"] for s in d.get("studies") or []]
        token = d.get("nextPageToken")
        if not token or len(ids) >= CAP:
            break
    return {"source": "CTGOV", "query": {"intr": q_i, "cond": q_c, "filter": "INTERVENTIONAL AND RANDOMIZED"},
            "run_utc": now(), "state": "COMPLETE" if n is None or len(ids) >= n else "TRUNCATED", "hits": n, "ids": ids,
            "pages_sha256": shas}


def europepmc(ints, pops):
    q = (f"({' OR '.join(chr(34) + t + chr(34) for t in ints)}) AND ({' OR '.join(chr(34) + t + chr(34) for t in pops)}) "
         f"AND (randomized OR randomised OR placebo) AND (SRC:MED OR SRC:PPR)")
    ids, shas, cursor, n = [], [], "*", None
    while True:
        st, b = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                    {"query": q, "format": "json", "pageSize": 1000, "cursorMark": cursor, "resultType": "idlist"})
        shas.append(hashlib.sha256(b).hexdigest())
        if st != 200:
            return {"source": "EUROPEPMC", "query": q, "run_utc": now(), "state": "FETCH_FAILED", "ids": ids,
                    "error": b[:200].decode("utf-8", "replace"), "pages_sha256": shas}
        d = json.loads(b)
        n = d.get("hitCount", n)
        page = (d.get("resultList") or {}).get("result") or []
        ids += [(r.get("pmid") or f"{r.get('source')}:{r.get('id')}") for r in page]
        nxt = d.get("nextCursorMark")
        if not page or not nxt or nxt == cursor or len(ids) >= CAP:
            break
        cursor = nxt
    return {"source": "EUROPEPMC", "query": q, "run_utc": now(),
            "state": "COMPLETE" if n is None or len(ids) >= n else "TRUNCATED", "hits": n, "ids": ids, "pages_sha256": shas}


def euctr(ints):
    import g1_open_sources as osrc
    out_ids, shas, n = set(), [], 0
    for t in [x for x in ints if " " not in x or len(x) > 6][:6]:
        st, _ct, b, _u = osrc.fetch("https://www.clinicaltrialsregister.eu/ctr-search/search?query="
                                    + urllib.parse.quote(t), timeout=90)
        shas.append(hashlib.sha256(b or b"").hexdigest())
        if st != 200:
            continue
        page = b.decode("utf-8", "replace")
        m = re.search(r"(\d[\d,]*)\s+result\(s\) found", page)
        n += int(m.group(1).replace(",", "")) if m else 0
        out_ids |= set(re.findall(r"EudraCT Number:</span>\s*(\d{4}-\d{6}-\d{2})", page))
    return {"source": "EUCTR", "query": ints[:6], "run_utc": now(),
            "state": "FIRST_PAGE_ONLY" if n > len(out_ids) else "COMPLETE", "hits": n, "ids": sorted(out_ids),
            "pages_sha256": shas, "note": "the register pages 20 per page; ids are the first page per term"}


def held_ids(slug, ref_tracker=True):
    have = set()
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        for r in (d.get("records") or []) + (d.get("ctgov") or []):
            have |= {str(r.get("id")), str(r.get("nct") or "")}
    p = os.path.join(ROOT, "cache", slug, "retrieval_ledger.json")
    if os.path.exists(p):
        have |= set(map(str, (json.load(open(p, encoding="utf-8")).get("records") or {}).keys()))
    p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if os.path.exists(p):
        for s in (json.load(open(p, encoding="utf-8")).get("screening") or {}).get("records") or []:
            have.add(str(s["id"]).split(" · ")[-1])
    p = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json")
    if os.path.exists(p):
        for t in json.load(open(p, encoding="utf-8")).get("trials") or []:
            have.add(str(t.get("family") or "").replace("PMID ", ""))
            for c in ((t.get("registry_binding") or {}).get("candidates") or []):
                have.add(str(c.get("nct") or ""))
    have.discard("")
    return have


def fetch_new(pmids, ncts):
    """Typed records for NEW ids: PubMed efetch (harness.fetch._efetch) and CT.gov API v2 (title, conditions, arms)."""
    from harness import fetch
    recs = []
    pm = sorted(pmids)
    for i in range(0, len(pm), 150):
        for _ in range(3):
            try:
                recs += fetch._efetch(pm[i:i + 150])
                break
            except Exception:  # noqa: BLE001 - retried; a batch that never answers is reported below
                time.sleep(3)
        time.sleep(0.4)
    got = {r["id"] for r in recs}
    for n in sorted(ncts):
        st, b = get(f"https://clinicaltrials.gov/api/v2/studies/{n}")
        if st != 200:
            continue
        p = json.loads(b).get("protocolSection") or {}
        idm, cond, arms, des = (p.get("identificationModule") or {}), (p.get("conditionsModule") or {}), \
            (p.get("armsInterventionsModule") or {}), (p.get("designModule") or {})
        recs.append({"id": n, "id_type": "nct", "nct": n, "title": idm.get("officialTitle") or idm.get("briefTitle") or "",
                     "acronym": idm.get("acronym") or "", "conditions": cond.get("conditions") or [],
                     "interventions": [i.get("name") for i in arms.get("interventions") or []],
                     "arms": [a.get("label") for a in arms.get("armGroups") or []],
                     "abstract": ((p.get("descriptionModule") or {}).get("briefSummary") or ""),
                     "masking": ((des.get("designInfo") or {}).get("maskingInfo") or {}).get("masking"),
                     "allocation": (des.get("designInfo") or {}).get("allocation"),
                     "pubtypes": ["Randomized Controlled Trial"] if (des.get("designInfo") or {}).get("allocation") ==
                     "RANDOMIZED" else [], "source": "CT.gov API v2", "response_sha256": hashlib.sha256(b).hexdigest()})
    missing = sorted(set(pm) - got)
    return recs, missing


def run(slug):
    from harness import served_comparator as sc
    cfg = sc.served_config(slug, json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8")))
    ints, pops = concepts(cfg)
    srcs = [pubmed(ints, pops), ctgov(ints, pops), europepmc(ints, pops), euctr(ints)]
    have = held_ids(slug)
    new_pm = {i for s in srcs if s["source"] in ("PUBMED", "EUROPEPMC") for i in s.get("ids") or [] if str(i).isdigit()}
    new_pm -= have
    new_nct = {i for s in srcs if s["source"] == "CTGOV" for i in s.get("ids") or []} - have
    recs, missing = fetch_new(new_pm, new_nct)
    km = {}
    for k in KNOWN_MISSES.get(slug, []):
        km[k] = sorted({str(r["id"]) for r in recs if k.lower() in (str(r.get("title")) + " " + str(r.get("acronym")) + " "
                                                                     + str(r.get("id"))).lower()}
                       | ({k} if k in {i for s in srcs for i in s.get("ids") or []} else set()))
    out = {"slug": slug, "run_utc": now(), "concepts": {"intervention": ints, "population": pops}, "sources": srcs,
           "held_before": len(have), "new_pmids": sorted(new_pm), "new_ncts": sorted(new_nct),
           "records_fetched": len(recs), "pmids_not_fetched": missing, "known_misses_found": km,
           "writer": "scripts/g1_concept_search.py"}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    json.dump(recs, open(os.path.join(OUT, f"{slug}.records.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    return out


def main(argv):
    for s in [a for a in argv if not a.startswith("--")]:
        try:
            o = run(s)
            print(f"{s}: " + " | ".join(f"{x['source']} {x.get('state')} {x.get('hits')}" for x in o["sources"])
                  + f" | new PMIDs {len(o['new_pmids'])} new NCTs {len(o['new_ncts'])} fetched {o['records_fetched']}"
                  + (f" | known misses {o['known_misses_found']}" if o["known_misses_found"] else ""), flush=True)
        except Exception as exc:  # noqa: BLE001 - reported, never hidden
            print(s, "ERROR", type(exc).__name__, str(exc)[:300], flush=True)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
