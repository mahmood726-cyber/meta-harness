"""R8-6 sweep, every topic: registry-only families and the reports that belong to them (read-only; the captain
regenerates). Three typed routes find a family's reports:
  AACT study_references (RESULT / DERIVED)   the PubMed DataBank accession ('<NCT>[si]')   the report TITLE printing the
  family's registered acronym (harness.trial_family.acronym_title_link, for a report with no identifier of its own).
Each linked report is classified:
  NEW_LINK_TITLE_ACRONYM    held, no identifier of its own, the title rule now attaches it (code fix in this branch)
  STALE_REGISTRY            held, AACT links it to exactly this one NCT, but cache/<slug>/family_registry.json has no
                            report_links row for it: fixed by regenerating the registry (scripts/trial_family_registry.py)
  MULTI_PARENT              held, linked to 2+ NCTs: a pooled / cross-trial paper, correctly never bridged
  NOT_HELD                  linked but never retrieved: a k-gap retrieval item (TRANSFORM-1's own report 31290965;
                            finerenone ARTS-DN Japan's report 28025025)

    python scripts/r8_6_report_links.py   -> outputs/k_gap/g1_binding/r8_6_report_links.json
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "r8_6_report_links.json")


def classify(p, n, held, pmid_ncts, links):
    """The kind of one linked report: parents counted over BOTH routes (AACT and the PubMed DataBank) -- a paper either
    route ties to 2+ registry families is MULTI_PARENT (codex r8-6-links-r1 #4: only AACT parents were counted)."""
    if p not in held:
        return "NOT_HELD"
    if len(pmid_ncts.get(p) or {n}) > 1:
        return "MULTI_PARENT"
    return "LINKED_IN_REGISTRY" if p in links else "STALE_REGISTRY"


def main():
    from harness import aact, http, fetch, trial_family as tf
    from harness.family_compact import read_registry
    topics = sorted(s for s in os.listdir(os.path.join(ROOT, "docs", "reviews"))
                    if os.path.isdir(os.path.join(ROOT, "docs", "reviews", s)))
    reg_only, recs_by, regs = {}, {}, {}
    for slug in topics:
        rp = os.path.join(ROOT, "cache", slug, "records.json")
        fp = os.path.join(ROOT, "cache", slug, "families.json")
        gp = os.path.join(ROOT, "cache", slug, "family_registry.json")
        if not (os.path.exists(rp) and os.path.exists(fp)):
            continue
        d = json.load(open(rp, encoding="utf-8"))
        recs_by[slug] = {str(r.get("id")): r for r in list(d.get("records") or []) + list(d.get("ctgov") or [])}
        regs[slug] = read_registry(Path(gp)) if os.path.exists(gp) else {}
        f = json.load(open(fp, encoding="utf-8"))
        items = f if isinstance(f, list) else (f.get("families") or f.get("nodes") or list(f.values()))
        reg_only[slug] = sorted({str(x.get("family_id") or x.get("id")).upper() for x in items
                                 if str(x.get("family_id") or x.get("id") or "").upper().startswith("NCT")
                                 and all(str(r.get("report_id")).upper().startswith("NCT") for r in x.get("reports") or [])})
    want = sorted({n for v in reg_only.values() for n in v})
    snap = os.environ.get("AACT_DIR") or "F:/AACT-storage/AACT/2026-08-30"
    by_nct = aact.nct_to_pmids(want, root=snap)
    pmid_ncts = {}
    for n, ps in by_nct.items():
        for p in ps:
            pmid_ncts.setdefault(p, set()).add(n)
    si = {}
    for n in want:  # noqa: B007
        try:
            time.sleep(0.35)
            q = http.get_json(f"{fetch.EUTILS}/esearch.fcgi", {"db": "pubmed", "term": f"{n}[si]", "retmode": "json",
                                                               "tool": "meta-harness", "email": "meta-harness@example.org"})
            si[n] = q["esearchresult"]["idlist"]
        except Exception as exc:  # noqa: BLE001 - a failed search is recorded, never read as 'no report'
            si[n] = f"NOT_CHECKED:{type(exc).__name__}"
    for n, ps in si.items():
        for p in ps if isinstance(ps, list) else []:
            pmid_ncts.setdefault(p, set()).add(n)
    res = {}
    for slug in sorted(reg_only):
        held, reg = recs_by[slug], regs[slug]
        links = reg.get("report_links") or {}
        index = reg.get("records") or {}
        rows = []
        for n in reg_only[slug]:
            cands = set(by_nct.get(n) or []) | (set(si[n]) if isinstance(si.get(n), list) else set())
            for p in sorted(cands):
                kind = classify(p, n, held, pmid_ncts, links)
                rows.append({"nct": n, "pmid": p, "kind": kind,
                             "routes": [x for x, ok in (("AACT", p in (by_nct.get(n) or [])),
                                                        ("PUBMED_SI", isinstance(si.get(n), list) and p in si[n])) if ok]})
        # the title-acronym rule over held reports that carry no identifier and no AACT row
        for p, r in held.items():
            if not p.isdigit() or r.get("nct") or tf.registry_ids(r) or links.get(p):
                continue
            nct, ev = tf.acronym_title_link(r, index)
            if nct:
                rows.append({"nct": nct, "pmid": p, "kind": "NEW_LINK_TITLE_ACRONYM", "routes": ["TITLE_ACRONYM"],
                             "acronym": ev["acronym"]})
        kinds = {}
        for x in rows:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
        res[slug] = {"registry_only_families": len(reg_only[slug]), "counts": kinds, "rows": rows,
                     "search_failures": [n for n in reg_only[slug] if not isinstance(si.get(n), list)]}
    tot = {}
    for t in res.values():
        for k, v in t["counts"].items():
            tot[k] = tot.get(k, 0) + v
    out = {"totals": tot, "topics": res}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(tot, indent=1))
    for s, t in res.items():
        if t["counts"]:
            print(s, t["counts"])
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
