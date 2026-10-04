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


def k_gap_fold(x):
    from kgap import k_gap as _kg
    return _kg.fold_dashes(str(x or ""))


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


_STOP = {"and", "of", "the", "in", "for", "with", "on", "a", "an", "to", "or", "by", "at", "after", "versus", "vs"}


def spells_out(acr, text, max_skip=3):
    """Does TEXT spell the acronym out? In order, each acronym letter taken from a word-start prefix of a CAPITALISED
    word ('Randomized ALdactone Evaluation Study' -> RALES), at most `max_skip` words skipped between two used words
    (EPHESUS skips 'Acute Myocardial Infarction'), at least 3 words used. Lower-case words are never used: a sentence-case
    title can spell almost anything."""
    a = re.sub(r"[^A-Z]", "", (acr or "").upper())
    words = re.findall(r"[A-Za-z]+", text or "")
    if len(a) < 4 or not words:
        return False

    def go(ai, wi, used, skipped):
        if ai == len(a):
            return used >= 3
        for j in range(wi, len(words)):
            if used and j - wi > max_skip:
                return False
            w = words[j]
            if w[0].isupper() and w[0].upper() == a[ai]:
                for k in range(min(len(w), len(a) - ai), 0, -1):
                    if w[:k].upper() == a[ai:ai + k] and go(ai + k, j + 1, used + 1, 0):
                        return True
            if not used and j - wi > 40:
                return False
        return False
    return go(0, 0, 0, 0)


def expansion_hits(acr, titles):
    """PMIDs whose title or study-group CollectiveName spells the acronym out. titles: {pmid: (title, collective)}."""
    return sorted(p for p, (ti, co) in titles.items() if spells_out(acr, ti) or spells_out(acr, co))


def comment_target(rec):
    """The article a Letter / Comment record comments on (PubMed CommentOn), when it is ONLY a letter / comment and
    links exactly one; else None."""
    pt = set(rec.get("pubtypes") or [])
    if not pt & {"Letter", "Comment", "Editorial"} or pt & {"Randomized Controlled Trial", "Clinical Trial"}:
        return None
    on = rec.get("comment_on") or []
    return on[0] if len(on) == 1 else None


def pubmed_records(pmids, offline):
    """PMID -> {title, collective, pubtypes, comment_on} from PubMed efetch XML; cached in outputs/k_gap/
    pubmed_records_identity.json so a rerun replays them (a failed fetch is never cached)."""
    import xml.etree.ElementTree as ET
    cp = os.path.join(OUT, "pubmed_records_identity.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({p for p in pmids if p and str(p).isdigit() and p not in cache})
    if todo:
        from harness import http
        for i in range(0, len(todo), 100):
            chunk = todo[i:i + 100]
            try:
                body = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                                     {"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"})
                root = ET.fromstring(body.encode("utf-8") if isinstance(body, str) else body)
            except Exception as exc:  # noqa: BLE001
                print("efetch failed", exc)
                continue
            for art in root.iter("PubmedArticle"):
                pm = (art.findtext(".//MedlineCitation/PMID") or "").strip()
                cache[pm] = {"title": "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else "",
                             "collective": " | ".join((c.text or "") for c in art.iter("CollectiveName")),
                             "pubtypes": [x.text for x in art.iter("PublicationType") if x.text],
                             "comment_on": [c.findtext("PMID") for c in art.iter("CommentsCorrections")
                                            if c.get("RefType") == "CommentOn" and c.findtext("PMID")]}
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def expansion_candidates(year, agents, offline):
    """PubMed: the year's RCT-typed papers naming a topic agent (cached query -> ids, outputs/k_gap/pubmed_expansion.json)."""
    cp = os.path.join(OUT, "pubmed_expansion.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    q = f"{year}[dp] AND ({ag}) AND randomized controlled trial[pt]"
    if q not in cache and not offline:
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                              {"db": "pubmed", "term": q, "retmode": "json", "retmax": 400})
            cache[q] = d.get("esearchresult", {}).get("idlist", [])
            with open(cp, "w", encoding="utf-8") as fh:
                json.dump(cache, fh, indent=1, sort_keys=True)
        except Exception as exc:  # noqa: BLE001
            print("esearch failed", exc)
    return q, cache.get(q) if isinstance(cache.get(q), list) else []


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
        unlinked = [p for p in pm if not link.get(p)]
        if ncts and unlinked and len(pm) > 1:
            # a self-naming paper with NO registry link could be ANOTHER trial of the same acronym (codex review 3 Oct)
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM_PARTLY_LINKED", "self_naming_pmids": pm,
                            "ncts": ncts, "unlinked": unlinked}
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
    # ---- acronym-EXPANSION route: an acronym + year label still unresolved ('RALES1999', 'EPHESUS2003'): the year's
    # RCT-typed papers naming a topic agent whose title or study-group name SPELLS THE ACRONYM OUT; exactly one
    for t in items:
        key = f"{t['slug']}::{t['label']}"
        if (results.get(key) or {}).get("state") == "RESOLVED":
            continue
        m = re.match(r"^\s*([A-Z][A-Z0-9-]{3,})\s*,?\s*\(?((?:19|20)\d\d)\)?", k_gap_fold(t["label"]))
        if not m:
            continue
        acr, year = m.group(1), m.group(2)
        agents = kt.topic_agents(topics[t["slug"]])
        q, ids = expansion_candidates(year, agents, offline)
        recs = pubmed_records(ids, offline)
        hits = expansion_hits(acr, {p: (recs.get(p, {}).get("title", ""), recs.get(p, {}).get("collective", ""))
                                    for p in ids if p in recs})
        if len(hits) == 1:
            p = hits[0]
            link = ic.pmid_to_ncts([p], snap).get(p) or {}
            results[key] = {"state": "RESOLVED", "basis": "ACRONYM_EXPANSION", "pmid": p,
                            "nct": next(iter(link), None) if len(link) == 1 else None, "scope": "IN_SCOPE",
                            "span": (recs[p]["title"] if spells_out(acr, recs[p]["title"]) else recs[p]["collective"])[:300],
                            "query": q}
        elif len(hits) > 1:
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM_EXPANSION", "pmids": hits, "query": q}
    # ---- COMMENT-ON route: a unit whose only report is a Letter / Comment is the article it comments on
    T_all = [t for t in T["trials"] if len(t.get("pmids") or []) == 1 and t.get("status") != "POOLED"]
    recs = pubmed_records([t["pmids"][0] for t in T_all], offline)
    for t in T_all:
        tgt = comment_target(recs.get(t["pmids"][0]) or {})
        if tgt:
            results[f"{t['slug']}::{t['label']}"] = {"state": "COMMENT_ON", "basis": "PUBMED_COMMENT_ON",
                                                     "from": t["pmids"][0], "pmid": tgt}
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
