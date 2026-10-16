"""v3 benchmark: run the ten pre-registered Europe PMC class queries ONCE and freeze the ordered hit list.

    python scripts/bench_v3_query.py OUT_DIR

Reads the query strings from registry/benchmarks/PREREGISTRATION_G1_BENCH_v3.md (never a second copy), saves every
response page with its sha256, and writes OUT_DIR/hits_v3_ids.json ordered by sha256("20261016:" + PMID).
Fails closed on any non-200, non-JSON or HTML error page.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join(ROOT, "registry", "benchmarks", "PREREGISTRATION_G1_BENCH_v3.md")
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
SEED = "20261016"


def prereg_queries(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    m = re.search(r"\*\*Common filter F\*\*.*?:\s*\n\s*`(.+?)`", text, re.S)
    if not m:
        raise SystemExit("common filter F not found in the pre-registration")
    common = re.sub(r"\s+", " ", m.group(1)).strip()
    rows = re.findall(r"^\| (Q\d\d) \| ([^|]+?) \| ([^|]+?) \|$", text, re.M)
    if len(rows) != 10:
        raise SystemExit(f"expected 10 class queries, found {len(rows)}")
    return common, [(q, c.strip(), t.strip()) for q, c, t in rows]


def fetch(params: dict) -> tuple[dict, bytes]:
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                body = r.read()
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status}")
            data = json.loads(body)
            if "resultList" not in data:
                raise RuntimeError("no resultList in response")
            return data, body
        except Exception as exc:  # retried, then fails closed
            if attempt == 3:
                raise SystemExit(f"query failed after 4 attempts: {exc}: {url}")
            time.sleep(2 ** attempt)
    raise AssertionError


def main(out_dir: str) -> None:
    text = open(PREREG, encoding="utf-8").read()
    common, classes = prereg_queries(text)
    os.makedirs(os.path.join(out_dir, "pages"), exist_ok=True)
    hits: dict[str, dict] = {}
    log = []
    for qid, cls, terms in classes:
        query = f"{common} AND ({terms})"
        cursor, page = "*", 0
        n_q = 0
        while True:
            data, body = fetch({"query": query, "resultType": "lite", "format": "json",
                                "pageSize": 1000, "cursorMark": cursor})
            page += 1
            name = f"{qid}_p{page:03d}.json"
            with open(os.path.join(out_dir, "pages", name), "wb") as fh:
                fh.write(body)
            log.append({"query_id": qid, "page": page, "file": name,
                        "sha256": hashlib.sha256(body).hexdigest(),
                        "hitCount": data.get("hitCount")})
            res = data["resultList"].get("result") or []
            for r in res:
                pmid = r.get("pmid")
                if not pmid:
                    continue
                h = hits.setdefault(pmid, {"pmid": pmid, "pmcid": r.get("pmcid"), "title": r.get("title"),
                                           "pubYear": r.get("pubYear"), "classes": []})
                if qid not in h["classes"]:
                    h["classes"].append(qid)
                n_q += 1
            nxt = data.get("nextCursorMark")
            if not res or not nxt or nxt == cursor:
                break
            cursor = nxt
            time.sleep(1)
        print(qid, cls, "hits", n_q, flush=True)
    ordered = sorted(hits.values(), key=lambda h: hashlib.sha256(f"{SEED}:{h['pmid']}".encode()).hexdigest())
    for i, h in enumerate(ordered, 1):
        h["order"] = i
        h["primary_class"] = sorted(h["classes"])[0]
    out = {"prereg_sha256": hashlib.sha256(open(PREREG, "rb").read()).hexdigest(),
           "common_filter": common, "classes": [{"id": q, "class": c, "terms": t} for q, c, t in classes],
           "seed": SEED, "run_utc": datetime.now(timezone.utc).isoformat(), "pages": log,
           "n_unique": len(ordered), "hits": ordered}
    with open(os.path.join(out_dir, "hits_v3_ids.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("UNIQUE", len(ordered))


if __name__ == "__main__":
    main(sys.argv[1])
