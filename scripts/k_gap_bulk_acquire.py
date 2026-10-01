"""BULK ACQUISITION, up front, for every comparator / secondary trial: so verification never waits on the network.

Three lanes run concurrently (each lane is sequential inside, so no host is hammered):
  NCBI       abstracts (efetch, batched) + PMC OA full text (k_gap_counterfactual.pmc_fulltext_cached: PMCID resolved
             via idconv, paced; NO_PMCID recorded only when PMC says so; an empty body is never cached)
  Unpaywall  OA copies by DOI (kgap.k_gap.unpaywall_text; typed PDF/HTML text, never OCR)
  AACT       posted CT.gov results from the LOCAL snapshot (no network): one streaming pass over outcomes,
             outcome_analyses, outcome_measurements and outcome_counts, filtered to our NCTs
Writes: outputs/k_gap/_aact_results.json (gitignored) and outputs/k_gap/bulk_acquire.json (committed: what was found,
with digests and timings).

    python scripts/k_gap_bulk_acquire.py
"""
from __future__ import annotations

import concurrent.futures as cf
import csv
import hashlib
import io
import json
import os
import sys
import threading
import time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import k_gap_counterfactual as cfm  # noqa: E402
from kgap import k_gap  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
AACT_IDX = os.path.join(OUT, "_aact_results.json")
csv.field_size_limit(10 ** 8)
# set by the NCBI lane once the abstracts (which carry the DOIs) are written; the Unpaywall lane waits on it. Waiting on the
# cache FILE was wrong: it existed from earlier runs, so the lane read stale records (257 NO_DOI instead of 13).
RECORDS_READY = threading.Event()


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def trial_set():
    """Every trial identity we may need to verify: k-gap table rows (all topics) + secondary-tier families."""
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    pmids, ncts = set(), set()
    for r in T["trials"]:
        if r.get("drug") == "OTHER_AGENT":
            continue
        pmids.update(p for p in (r.get("pmids") or [])[:3] if str(p).isdigit())
        ncts.update(n for n in (r.get("ncts") or []) if str(n).startswith("NCT"))
    sd = os.path.join(ROOT, "registry", "secondary_meta")
    for f in os.listdir(sd):
        if f.startswith("search_") or f == "runs.json" or not f.endswith(".json"):
            continue
        for row in _j(os.path.join(sd, f)).get("rows", []):
            fam = str(row.get("family_id") or "")
            if fam.startswith("PMID "):
                pmids.add(fam[5:])
    return sorted(pmids), sorted(ncts)


def ncbi_lane(pmids):
    t0, st = time.time(), Counter()
    mp = os.path.join(OUT, "member_records.json")
    mrec = _j(mp) if os.path.exists(mp) else {}
    need = [p for p in pmids if p not in mrec]
    from harness import fetch
    for k in range(0, len(need), 100):                    # efetch in batches of 100 (one request each)
        try:
            for r in fetch._efetch(need[k:k + 100]):
                mrec[r["id"]] = r
        except Exception:  # noqa: BLE001 - a failed batch is retried on the next run, never recorded as absent
            st["EFETCH_BATCH_FAILED"] += 1
        time.sleep(0.4)
    with open(mp, "w", encoding="utf-8") as fh:
        json.dump(mrec, fh, indent=1, sort_keys=True)
    RECORDS_READY.set()
    for p in pmids:
        txt = cfm.pmc_fulltext_cached(p)                   # paced inside
        st["PMC_TEXT" if txt else "PMC_NONE"] += 1
    return {"lane": "NCBI", "secs": round(time.time() - t0, 1), "abstracts_held": sum(1 for p in pmids if p in mrec),
            **st}


def unpaywall_lane(pmids):
    t0, st = time.time(), Counter()
    mp = os.path.join(OUT, "member_records.json")
    RECORDS_READY.wait(timeout=3600)                        # DOIs come from the NCBI lane's abstracts
    mrec = _j(mp) if os.path.exists(mp) else {}
    for p in pmids:
        doi = (mrec.get(p) or {}).get("doi")
        if not doi:
            st["NO_DOI"] += 1
            continue
        u = k_gap.unpaywall_text(doi, os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"))
        st["UPW_TEXT" if u.get("text") else "UPW_NONE"] += 1
        time.sleep(0.1)
    return {"lane": "UNPAYWALL", "secs": round(time.time() - t0, 1), **st}


def _rows(name, want, key="nct_id"):
    snap = "F:/AACT-storage/AACT/2026-08-30"
    with open(os.path.join(snap, name), encoding="utf-8", errors="replace", newline="") as fh:
        rd = csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE)
        for r in rd:
            if r.get(key) in want:
                yield r


def aact_lane(ncts):
    t0 = time.time()
    want = set(ncts)
    idx = {n: {"outcomes": {}, "analyses": [], "groups": {}} for n in want}
    for r in _rows("outcomes.txt", want):
        idx[r["nct_id"]]["outcomes"][r["id"]] = {"title": r.get("title"), "time_frame": r.get("time_frame"),
                                                 "type": r.get("outcome_type")}
    for r in _rows("outcome_analyses.txt", want):
        idx[r["nct_id"]]["analyses"].append({"outcome_id": r["outcome_id"], "param_type": r.get("param_type"),
                                             "param_value": r.get("param_value"), "ci_lower": r.get("ci_lower_limit"),
                                             "ci_upper": r.get("ci_upper_limit")})
    counts, ns = {}, {}
    for r in _rows("outcome_measurements.txt", want):
        if (r.get("param_type") or "").upper() in ("COUNT_OF_PARTICIPANTS", "NUMBER", "COUNT_OF_UNITS") and \
                not (r.get("category") or r.get("classification")):
            try:
                counts[(r["nct_id"], r["outcome_id"], r["result_group_id"])] = int(float(r["param_value_num"]))
            except (TypeError, ValueError):
                pass
    for r in _rows("outcome_counts.txt", want):
        if (r.get("scope") or "").lower() == "measure":
            try:
                ns[(r["nct_id"], r["outcome_id"], r["result_group_id"])] = int(r["count"])
            except (TypeError, ValueError):
                pass
    for (n, oid, gid), c in counts.items():
        if (n, oid, gid) in ns:
            idx[n]["groups"].setdefault(oid, []).append({"group": gid, "count": c, "n": ns[(n, oid, gid)]})
    with open(AACT_IDX, "w", encoding="utf-8") as fh:
        json.dump(idx, fh)
    b = open(AACT_IDX, "rb").read()
    return {"lane": "AACT", "secs": round(time.time() - t0, 1), "ncts": len(want),
            "with_posted_outcomes": sum(1 for v in idx.values() if v["outcomes"]),
            "with_analyses": sum(1 for v in idx.values() if v["analyses"]),
            "with_group_counts": sum(1 for v in idx.values() if v["groups"]),
            "index_sha256": hashlib.sha256(b).hexdigest(), "index_bytes": len(b)}


def main():
    pmids, ncts = trial_set()
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(ncbi_lane, pmids), ex.submit(unpaywall_lane, pmids), ex.submit(aact_lane, ncts)]
        lanes = [f.result() for f in futs]
    out = {"pmids": len(pmids), "ncts": len(ncts), "wall_secs": round(time.time() - t0, 1), "lanes": lanes}
    with open(os.path.join(OUT, "bulk_acquire.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
