"""IDENTITY CHAIN for comparator trials with NO identity (class IDENTITY_UNRESOLVED): label -> PMID -> NCT, typed.

    ACRONYM labels   PubMed '"<ACRONYM>"[tiab] AND (<topic agents OR class terms>) AND randomized controlled trial[pt]'
                     (cached query, kgap k_gap_table.pubmed_acronym_ids) -> keep hits whose TITLE names the acronym
                     (k_gap_table.self_names) -> PMID->NCT via AACT study_references (kgap.identity_chain.pmid_to_ncts)
                     -> exactly ONE NCT: RESOLVED (its self-naming PMIDs listed; report = the earliest-id self-naming
                     PMID linked to that NCT as RESULT, else the earliest linked one)
    AUTHOR_YEAR      kgap.identity_chain.resolve: a RESULT/DERIVED study_references citation beginning with the surname
                     and carrying the year, interventional, naming a topic agent -> exactly one NCT
Then the AGENT: the self-naming titles (and the topic's class) decide IN_SCOPE (names a topic agent) / OTHER_AGENT:<m>
(names another known molecule: a class comparator's trial of another drug -- out of a drug-specific topic's scope) /
AGENT_UNSTATED. Two or more NCTs -> AMBIGUOUS, never a pick.

    python scripts/g1_identity_chain.py [--offline]   -> outputs/k_gap/identity_chain.json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from kgap import aact_adapter, identity_chain as ic  # noqa: E402
import k_gap_table as kt  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
NOT_A_REPORT = re.compile(r"\bprotocol\b|rationale and design|\bdesign and rationale\b|statistical analysis plan|"
                          r"\bbaseline characteristics\b|\bstudy design\b", re.I)


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv):
    offline = "--offline" in argv
    snap = aact_adapter.snapshot_dir()
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    topics = {}
    all_molecules = set()
    for f in os.listdir(os.path.join(ROOT, "topics")):
        if f.endswith(".json"):
            c = _j(os.path.join(ROOT, "topics", f))
            topics[f[:-5]] = c
            all_molecules |= {m.lower() for m in kt.molecule_names(c)}
    items = [t for t in T["trials"] if t["status"] == "UNRESOLVED" and not t["pmids"] and not t["ncts"]
             and t.get("drug") != "OTHER_AGENT"]
    acr_items, ay_items, results = [], [], {}
    for t in items:
        acr, ay = ic.label_keys(t["label"])
        if acr:
            acr_items.append((t, sorted(acr)))
        elif ay:
            ay_items.append(t)
        else:
            results[f"{t['slug']}::{t['label']}"] = {"state": "NO_KEY", "why": "label carries neither acronym nor author-year"}
    # ---- acronym route
    hits = {}
    for t, acrs in acr_items:
        cfg = topics[t["slug"]]
        terms = sorted(set(kt.topic_agents(cfg)) | set(cfg.get("intervention_class_terms") or []))
        pm = []
        for a in acrs:
            raw = next((x for x in kt.k_gap._label_tokens(t["label"])["acronyms"] if ic._fold(x) == a), a)
            pm += kt.pubmed_acronym_ids(raw, terms, offline)
        hits[(t["slug"], t["label"])] = (sorted(set(pm)), acrs, cfg)
    titles = kt.pubmed_titles_of(sorted({p for v in hits.values() for p in v[0]}), offline)
    selfn = {}
    for k, (pm, acrs, cfg) in hits.items():
        raw = kt.k_gap._label_tokens(k[1])["acronyms"] or acrs
        selfn[k] = [p for p in pm if any(kt.self_names(a, titles.get(p, ""), "") for a in raw)]
    link = ic.pmid_to_ncts(sorted({p for v in selfn.values() for p in v}), snap) if selfn else {}
    own = ic.result_pmids(sorted({n for d in link.values() for n in d}), snap) if link else {}
    own_titles = kt.pubmed_titles_of(sorted({p for v in own.values() for p in v}), offline) if own else {}
    for (slug, label), pm in selfn.items():
        cfg = topics[slug]
        ncts = sorted({n for p in pm for n in (link.get(p) or {})})
        key = f"{slug}::{label}"
        if not pm:
            results[key] = {"state": "NOT_FOUND", "basis": "ACRONYM", "pubmed_hits": hits[(slug, label)][0][:10]}
            continue
        if len(ncts) > 1:
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM", "self_naming_pmids": pm, "ncts": ncts}
            continue
        nct = ncts[0] if ncts else None
        # the trial's REPORT: its earliest own RESULT-typed reference in AACT; else (no registry link) the self-naming PMID
        # a protocol / design / analysis-plan paper is RESULT-typed in AACT but is not the result report (SMART's
        # earliest RESULT reference, PMID 28302179, is its published study protocol)
        reports = [p for p in (own.get(nct) or []) if not NOT_A_REPORT.search(own_titles.get(p, ""))]
        report = reports[0] if nct and reports else (sorted(pm)[0] if not nct else None)
        text = " ".join(titles.get(p, "") for p in pm).lower()
        agents = [a.lower() for a in kt.topic_agents(cfg)]
        if any(a in text for a in agents):
            scope = "IN_SCOPE"
        else:
            other = sorted(m for m in all_molecules if m in text and m not in agents)
            scope = f"OTHER_AGENT:{other[0]}" if other else "AGENT_UNSTATED"
        if not nct and len(pm) > 1:
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM_NO_REGISTRY_LINK", "self_naming_pmids": pm}
            continue
        results[key] = {"state": "RESOLVED", "basis": "ACRONYM_SELF_NAMING_TITLE" + ("+AACT_STUDY_REFERENCES" if nct else ""),
                        "nct": nct, "pmid": report, "self_naming_pmids": pm, "scope": scope,
                        "title": (own_titles.get(report) or titles.get(report, ""))[:200]}
    # ---- author-year route (AACT RESULT/DERIVED citations)
    if ay_items:
        R = ic.resolve([(t["slug"], t["label"], kt.topic_agents(topics[t["slug"]])) for t in ay_items], snap)
        for (slug, label), v in R.items():
            v = dict(v)
            if v["state"] == "RESOLVED":
                v["scope"] = "IN_SCOPE"            # the candidate already had to name a topic agent
            results[f"{slug}::{label}"] = v
    from collections import Counter
    out = {"n": len(items), "by_state": dict(Counter(v["state"] for v in results.values())),
           "by_scope": dict(Counter(v.get("scope") for v in results.values() if v["state"] == "RESOLVED")),
           "snapshot": {k: v for k, v in aact_adapter.snapshot().items() if k in ("id", "digest")}, "results": results}
    with open(os.path.join(OUT, "identity_chain.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n", "by_state", "by_scope")}))
    for k, v in results.items():
        if v["state"] == "RESOLVED":
            print("  ", k[:60], v["nct"], v["pmid"], v["scope"], v.get("title", "")[:70])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
