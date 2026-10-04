"""Acquire the trial's OWN open text for every UNVERIFIED comparator trial (G1 confirm-unverified, 3 Oct), through the
SHARED cascade only: PubMed record (abstract + DOI), PMC OA full text (k_gap_counterfactual.pmc_fulltext_cached), and an
Unpaywall OA copy by DOI (kgap.k_gap.unpaywall_text). Legitimate open sources only; nothing is fetched that the cascade
would not fetch. Writes outputs/k_gap/g1_confirm/acquire.json (per PMID: what was found, never a guess).

    python scripts/g1_confirm_acquire.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import k_gap_counterfactual as cfm  # noqa: E402
from kgap import k_gap  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
CONF = os.path.join(OUT, "g1_confirm")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def unverified_targets():
    """(slug, label, pmids, ncts) of every tracker row routed UNVERIFIED; PMIDs/NCTs from the row's family, the k-gap
    table row and the two-source sweep's identity for it (never typed)."""
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    tab = {(t["slug"], t["label"]): t for t in T["trials"]}
    ep = os.path.join(OUT, "g1_confirm", "extra_reports.json")
    extra = _j(ep) if os.path.exists(ep) else {}
    out = []
    for f in sorted(os.listdir(os.path.join(OUT, "g1"))):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        g = _j(os.path.join(OUT, "g1", f))
        sp = os.path.join(OUT, "sweep", f)
        sw = {t["label"]: t for t in (_j(sp).get("trials") or [])} if os.path.exists(sp) else {}
        for x in g.get("trials") or []:
            # a row THIS lane's hook flipped is still a target: the tracker file the binder reads may already carry the
            # previous run's flip, and dropping it would make a re-run unbind what it bound (3 Oct, Safdar)
            if x.get("route") != "UNVERIFIED" and \
                    not str(x.get("reclassified_by") or "").startswith("g1/confirm-unverified"):
                continue
            fam = str(x.get("family") or "")
            t = tab.get((slug, x["label"])) or {}
            s = sw.get(x["label"]) or {}
            pm = set(re.findall(r"\b\d{6,9}\b", fam)) | set(t.get("pmids") or []) | set(s.get("pmids") or [])
            nc = set(re.findall(r"NCT\d{8}", fam)) | set(t.get("ncts") or []) | set(s.get("ncts") or [])
            # other reports of THIS trial that its own held texts cite, located by a reading lane and resolved to a PMID
            # deterministically (outputs/k_gap/g1_confirm/extra_reports.json, provenance per entry)
            pm |= {e["pmid"] for e in extra.get(f"{slug}::{x['label']}", []) if str(e.get("pmid") or "").isdigit()}
            out.append({"slug": slug, "label": x["label"], "pmids": sorted(p for p in pm if p.isdigit()),
                        "ncts": sorted(nc)})
    return out


def main():
    os.makedirs(CONF, exist_ok=True)
    tg = unverified_targets()
    pmids = sorted({p for t in tg for p in t["pmids"]})
    mp = os.path.join(OUT, "member_records.json")
    mrec = _j(mp) if os.path.exists(mp) else {}
    need = [p for p in pmids if p not in mrec]
    from harness import fetch
    for k in range(0, len(need), 100):
        try:
            for r in fetch._efetch(need[k:k + 100]):
                mrec[r["id"]] = r
        except Exception as exc:  # noqa: BLE001 -- recorded; a failed batch is never 'absent'
            print("efetch batch failed:", exc)
        time.sleep(0.4)
    tmp = mp + f".{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(mrec, fh, indent=1, sort_keys=True)
    os.replace(tmp, mp)
    per, st = {}, Counter()
    for p in pmids:
        rec = {"abstract": bool((mrec.get(p) or {}).get("abstract"))}
        txt = cfm.pmc_fulltext_cached(p)
        rec["pmc_oa"] = bool(txt)
        doi = (mrec.get(p) or {}).get("doi")
        rec["doi"] = doi or None
        if doi:
            u = k_gap.unpaywall_text(doi, os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"))
            rec["unpaywall_oa"] = bool(u.get("text"))
            time.sleep(0.1)
        else:
            rec["unpaywall_oa"] = False
        st["PMC_OA" if rec["pmc_oa"] else ("UNPAYWALL_OA" if rec["unpaywall_oa"] else "NO_OPEN_FULL_TEXT")] += 1
        per[p] = rec
        print(p, rec, flush=True)
    res = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "targets": len(tg),
           "pmids": len(pmids), "tally": dict(st), "per_pmid": per}
    tmp = os.path.join(CONF, "acquire.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    os.replace(tmp, os.path.join(CONF, "acquire.json"))
    print(json.dumps(res["tally"]))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
