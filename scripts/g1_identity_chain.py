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


def context_year(context):
    """The year the comparator's OWN table row prints for the unit ('COPE study 1 Italy/2005 Open-label RCT'), only when
    the row states exactly one year."""
    ys = {int(y) for y in re.findall(r"(?<!\d)(19[5-9]\d|20[0-3]\d)(?!\d)", context or "")}
    return ys.pop() if len(ys) == 1 else None


def year_tiebreak(pmids, years, year):
    """The self-naming PMIDs published in the comparator row's year; the caller resolves only if exactly one remains."""
    return [p for p in pmids if years.get(p) == year]


def label_author(label):
    """A leading surname of an author label ('Finkelstein Y et al'); an all-caps acronym ('COPE study') is not one."""
    m = re.match(r"^\s*([A-Z][a-z][A-Za-z'\-]+)\b", label or "")
    return m.group(1) if m else None


_NOT_RESEARCH = {"News", "Comment", "Editorial", "Letter", "Review", "Published Erratum"}


def tiebreak_eligible(rec):
    """A paper the row-year tie-break may pick: a research report, never a news / comment / editorial / letter / review
    item, never a 'study of the month' digest ('RALES1999' first resolved to one of those)."""
    if set(rec.get("pubtypes") or []) & _NOT_RESEARCH:
        return False
    return not re.search(r"study of the month|journal club|in brief|digest", rec.get("title") or "", re.I)


_DRUG_TYPES = {"DRUG", "BIOLOGICAL", "DIETARY_SUPPLEMENT", "COMBINATION_PRODUCT", "GENETIC"}


def registry_acronym_identity(want, snap, agents_of):
    """REGISTRY identity for comparator acronyms nothing else resolved: AACT studies.acronym (folded) naming exactly ONE
    study -> its NCT; that study's REGISTERED interventions decide the scope (a topic agent among them -> IN_SCOPE; drug
    interventions but none of the topic's -> OTHER_AGENT:<the registered name>; none -> AGENT_UNSTATED). SCORED and
    SOLOIST-WHF (sotagliflozin) in a dapagliflozin topic: no title query can find them -- no topic registers that
    molecule -- but the registry names the trial and its drug. want: {folded acronym: [key, ...]}; agents_of(key) ->
    the topic's agents. Unique-or-nothing: two studies with one acronym -> AMBIGUOUS."""
    if not want:
        return {}
    hits = {}
    for r in ic._rows(snap, "studies.txt"):
        a = ic._fold(r.get("acronym") or "")
        if a and a in want:
            hits.setdefault(a, set()).add(r["nct_id"])
    names = registered_drugs(snap, {n for v in hits.values() for n in v})
    out = {}
    for a, keys in want.items():
        got = sorted(hits.get(a) or [])
        basis = "AACT_STUDIES_ACRONYM+REGISTERED_INTERVENTIONS"
        if len(got) > 1:
            # one acronym, several registrations ('SCORED': a snoring device, a transfusion study, a sotagliflozin
            # trial): the comparator's units are DRUG-vs-PLACEBO trials, so only a registration with a drug arm AND a
            # placebo arm can be one; exactly one such -> it, otherwise still ambiguous
            dvp = [n for n in got if drug_vs_placebo(names.get(n) or [])]
            if len(dvp) == 1:
                got, basis = dvp, basis + "+ONLY_DRUG_VS_PLACEBO_REGISTRATION"
        for key in keys:
            if not got:
                continue
            if len(got) > 1:
                out[key] = {"state": "AMBIGUOUS", "basis": "AACT_STUDIES_ACRONYM", "ncts": got[:10]}
                continue
            out[key] = dict(registry_scope(got[0], names.get(got[0]) or [], agents_of(key)), basis=basis,
                            state="RESOLVED", pmid=None)
    return out


def registered_drugs(snap, ncts):
    """{nct: [(type, name), ...]} -- every registered intervention of these studies (AACT interventions.txt)."""
    out = {}
    if ncts:
        for r in ic._rows(snap, "interventions.txt"):
            if r.get("nct_id") in ncts:
                out.setdefault(r["nct_id"], []).append(((r.get("intervention_type") or "").upper(),
                                                        (r.get("name") or "").strip()))
    return out


_NOT_A_DRUG = re.compile(r"placebo|standard|usual care|matching|vehicle", re.I)


def drug_vs_placebo(iv):
    return any(t in _DRUG_TYPES and not _NOT_A_DRUG.search(n) for t, n in iv) and any(_NOT_A_DRUG.search(n) for _t, n in iv)


def registry_scope(nct, iv, agents):
    """The scope of a registered trial from its REGISTERED interventions: a topic agent among them -> IN_SCOPE; drug
    interventions but none of the topic's -> OTHER_AGENT:<registered name>; none -> AGENT_UNSTATED. The registry row is
    the held span."""
    drugs = [n for t, n in iv if t in _DRUG_TYPES and n and not _NOT_A_DRUG.search(n)]
    low = " ".join(drugs).lower()
    if any(a.lower() in low for a in agents):
        scope = "IN_SCOPE"
    else:
        scope = f"OTHER_AGENT:{drugs[0].lower()}" if drugs else "AGENT_UNSTATED"
    return {"nct": nct, "scope": scope, "registered_interventions": [f"{t}: {n}" for t, n in iv][:6],
            "span": {"source": "AACT interventions.txt", "nct": nct, "text": "; ".join(f"{t}: {n}" for t, n in iv)[:300]}}


def pubmed_acronym_open(acr, offline, retmax=60):
    """PMIDs whose title/abstract names the acronym -- NO agent filter (the agent is what is being established); a
    recorded query (outputs/k_gap/pubmed_acronym_open.json) replayed offline."""
    cp = os.path.join(OUT, "pubmed_acronym_open.json")
    cache = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    q = f'"{acr}"[tiab]'
    if q not in cache and not offline:
        import time
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                              {"db": "pubmed", "term": q, "retmode": "json", "retmax": retmax})
            cache[q] = d.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:  # noqa: BLE001
            cache[q] = {"error": str(exc)[:200]}
        time.sleep(0.4)
        with open(cp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    v = cache.get(q)
    return v if isinstance(v, list) else []


def acronym_registration_identity(label, acrs, agents, snap, offline):
    """SELF-NAMING papers -> ONE registration -> its registered drug: a comparator acronym (SOLOIST-WHF) whose result
    paper does not name it ('Sotagliflozin in Patients with Diabetes and Recent Worsening Heart Failure') but whose
    secondary reports do ('... in the SOLOIST-WHF Trial'). Every self-naming paper the registry links must link to the
    SAME NCT (unique-or-nothing); the scope is read from that NCT's registered interventions. Returns a result or None."""
    raw = kt.k_gap._label_tokens(label)["acronyms"] or acrs
    pm = sorted({p for a in raw for p in pubmed_acronym_open(a, offline)})
    if not pm:
        return None
    titles = kt.pubmed_titles_of(pm, offline)
    selfn = [p for p in pm if any(kt.self_names(a, titles.get(p, ""), "") for a in raw)]
    link = ic.pmid_to_ncts(selfn, snap) if selfn else {}
    by = {}
    for p in selfn:
        for n in (link.get(p) or {}):
            by.setdefault(n, []).append(p)
    if len(by) != 1:
        return {"state": "AMBIGUOUS", "basis": "ACRONYM_SELF_NAMING+AACT_LINK", "ncts": sorted(by)[:6]} if by else None
    nct, papers = next(iter(by.items()))
    out = registry_scope(nct, registered_drugs(snap, {nct}).get(nct) or [], agents)
    out.update(state="RESOLVED", basis="ACRONYM_SELF_NAMING+AACT_LINK+REGISTERED_INTERVENTIONS", pmid=None,
               self_naming_linked=papers[:5], title_span=titles.get(papers[0], "")[:200])
    return out


_REF_METHODS = ("META_REFERENCE_NUMBER", "META_REFERENCE_SURNAME_YEAR", "META_REFERENCE_TITLE_ACRONYM", "NCT_IN_LABEL")


def reference_list_identity(slug, label, id_rows):
    """REVIEW_REFERENCE_LIST identity (5 Oct decision): a comparator unit with no identity of its own takes the PMID /
    NCT that a published meta's OWN reference list gives the same trial -- the forest-reader lane's row identity map
    (registry/model_proposals/g1_forest_row_identity.json), only rows mapped by a REFERENCE method (the citation number,
    surname + year, the whole acronym in a reference title, an NCT in the label), never by a tracker join alone.
    Resolved only when every such row agrees on ONE PMID (or, with no PMID, one NCT); several -> AMBIGUOUS."""
    rs = [r for r in id_rows if r.get("slug") == slug and r.get("comparator_label") == label and r.get("mapped")
          and any(m in _REF_METHODS for m in r.get("methods") or [])]
    if not rs:
        return None
    pm = sorted({str(r["pmid"]) for r in rs if r.get("pmid")})
    nc = sorted({str(r["nct"]) for r in rs if r.get("nct")})
    src = [{"meta": r.get("meta_pmid"), "comparator_meta": bool(r.get("is_comparator")), "row": r.get("row_label"),
            "methods": r.get("methods"), "reference": (r.get("reference") or "")[:160]} for r in rs]
    if len(pm) > 1 or (not pm and len(nc) > 1):
        return {"state": "AMBIGUOUS", "basis": "REVIEW_REFERENCE_LIST", "pmids": pm, "ncts": nc, "sources": src}
    if not pm and not nc:
        return None
    return {"state": "RESOLVED", "basis": "REVIEW_REFERENCE_LIST", "pmid": pm[0] if pm else None,
            "nct": nc[0] if len(nc) == 1 else None, "scope": "IN_SCOPE", "sources": src}


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
            # an author label with no year: the comparator's own row year completes the author-year key
            au, cy = label_author(t["label"]), context_year(t.get("context"))
            if au and cy:
                pm1, q1, ids1 = kt.pubmed_author_year(au, str(cy), kt.topic_agents(topics[t["slug"]]), offline)
                if pm1:
                    link1 = ic.pmid_to_ncts([pm1], snap).get(pm1) or {}
                    results[f"{t['slug']}::{t['label']}"] = {
                        "state": "RESOLVED", "basis": "AUTHOR_WITH_COMPARATOR_ROW_YEAR", "pmid": pm1, "scope": "IN_SCOPE",
                        "nct": next(iter(link1), None) if len(link1) == 1 else None, "query": q1, "row_year": cy}
                    continue
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
    # OTHER-AGENT RETRY: the query above names only the topic's own agents, so a comparator unit testing ANOTHER agent
    # (SCORED -- sotagliflozin -- in a dapagliflozin topic) can never be found, and so never be named OTHER_AGENT; it
    # stayed AGENT_UNCONFIRMED in N and a sweep row counted it. Retried once with every molecule any topic registers;
    # the scope rule below then decides IN_SCOPE / OTHER_AGENT from the self-naming titles, as for any other hit.
    for k in [k for k, v in selfn.items() if not v]:
        pm0, acrs, cfg = hits[k]
        pm2 = []
        for a in acrs:
            raw1 = next((x for x in kt.k_gap._label_tokens(k[1])["acronyms"] if ic._fold(x) == a), a)
            pm2 += kt.pubmed_acronym_ids(raw1, sorted(all_molecules), offline)
        pm2 = sorted(set(pm2) - set(pm0))
        if not pm2:
            continue
        titles.update(kt.pubmed_titles_of(pm2, offline))
        raw = kt.k_gap._label_tokens(k[1])["acronyms"] or acrs
        got = [p for p in pm2 if any(kt.self_names(a, titles.get(p, ""), "") for a in raw)]
        if got:
            hits[k] = (sorted(set(pm0) | set(pm2)), acrs, cfg)
            selfn[k] = got
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
        # the AGENT is read from EVERY self-naming title, before any ambiguity about which paper is the report: twelve
        # VERTIS CV papers that all name ertugliflozin and none dapagliflozin are an other-agent trial whichever of them
        # is its report (the report stays unresolved; only the scope is stated)
        _txt = " ".join(titles.get(p, "") for p in pm).lower()
        _ag = [a.lower() for a in kt.topic_agents(cfg)]
        _oth = sorted(m for m in all_molecules if m in _txt and m not in _ag)
        amb_scope = "IN_SCOPE" if any(a in _txt for a in _ag) else (f"OTHER_AGENT:{_oth[0]}" if _oth else "AGENT_UNSTATED")
        if len(ncts) > 1:
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM", "self_naming_pmids": pm, "ncts": ncts,
                            "scope": amb_scope}
            continue
        unlinked = [p for p in pm if not link.get(p)]
        if ncts and unlinked and len(pm) > 1:
            # a self-naming paper with NO registry link could be ANOTHER trial of the same acronym (codex review 3 Oct)
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM_PARTLY_LINKED", "self_naming_pmids": pm,
                            "ncts": ncts, "unlinked": unlinked, "scope": amb_scope}
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
            results[key] = {"state": "AMBIGUOUS", "basis": "ACRONYM_NO_REGISTRY_LINK", "self_naming_pmids": pm,
                            "scope": amb_scope}
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
    # ---- ROW-YEAR tie-break, LAST (weaker than a spelled-out acronym): an acronym still AMBIGUOUS among several
    # self-naming papers takes the one research report published in the comparator row's year (COPPS: 2010)
    for t in items:
        key = f"{t['slug']}::{t['label']}"
        v = results.get(key) or {}
        cy = context_year(t.get("context"))
        if v.get("state") != "AMBIGUOUS" or v.get("basis") != "ACRONYM" or not cy:
            continue
        pm_all = list(v.get("self_naming_pmids") or [])
        recs_y = pubmed_records(pm_all, offline)
        yrs = kt.pub_years(pm_all, offline)
        one = [p for p in year_tiebreak(pm_all, {p: yrs.get(p) for p in pm_all}, cy) if tiebreak_eligible(recs_y.get(p) or {})]
        if len(one) == 1:
            link1 = ic.pmid_to_ncts(one, snap).get(one[0]) or {}
            results[key] = {"state": "RESOLVED", "basis": "ACRONYM_SELF_NAMING_TITLE+COMPARATOR_ROW_YEAR", "pmid": one[0],
                            "nct": next(iter(link1), None) if len(link1) == 1 else None, "scope": "IN_SCOPE",
                            "row_year": cy, "from_ambiguous": pm_all}
    # ---- REVIEW_REFERENCE_LIST, LAST: a unit still without an identity takes the one PMID / NCT that published metas'
    # own reference lists give it (identification only; eligibility is our screen's, data never the comparator's)
    import secondary_meta_build as smb
    idm, pin = smb.forest_lane_results("forest_row_identity_v1")
    id_rows = (idm or {}).get("rows") or []
    for t in items:
        key = f"{t['slug']}::{t['label']}"
        if (results.get(key) or {}).get("state") == "RESOLVED":
            continue
        v = reference_list_identity(t["slug"], t["label"], id_rows)
        if v:
            if v["state"] == "RESOLVED" and v.get("pmid") and not v.get("nct"):
                link1 = ic.pmid_to_ncts([v["pmid"]], snap).get(v["pmid"]) or {}
                v["nct"] = next(iter(link1), None) if len(link1) == 1 else None
            v["lane"] = pin
            results[key] = v
    # ---- REGISTRY acronym route, last of all: AACT's own acronym field + the study's registered interventions
    want = {}
    for t, acrs in acr_items:
        key = f"{t['slug']}::{t['label']}"
        if (results.get(key) or {}).get("state") == "RESOLVED":
            continue
        for a in acrs:
            want.setdefault(a, []).append(key)
    for key, v in registry_acronym_identity(want, snap,
                                            lambda k: kt.topic_agents(topics[k.split("::", 1)[0]])).items():
        if (results.get(key) or {}).get("state") != "RESOLVED":
            results[key] = v
    # ---- self-naming papers -> one registration -> its registered drug (SOLOIST-WHF: AACT has no acronym for it)
    for t, acrs in acr_items:
        key = f"{t['slug']}::{t['label']}"
        prev = results.get(key) or {}
        if prev.get("state") == "RESOLVED" or str(prev.get("scope") or "").startswith("OTHER_AGENT"):
            continue
        v = acronym_registration_identity(t["label"], acrs, kt.topic_agents(topics[t["slug"]]), snap, offline)
        if v and (v["state"] == "RESOLVED" or not prev):
            results[key] = v
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
