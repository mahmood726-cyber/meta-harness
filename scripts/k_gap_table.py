"""K-GAP TABLE: for every served topic with a comparator meta, the comparator's drug-specific included
set (from its included-studies TABLE, not its headline k) against our pool, trial by trial, with the
open source that could supply each missing trial's typed result.

Measurement only: reads committed caches + the local AACT snapshot + (network, cached) PMC idconv /
Europe PMC OA flags. It admits nothing and edits no topic page.

    python scripts/k_gap_table.py            # writes outputs/k_gap/{k_gap_table.json,k_gap_table.csv,SUMMARY.md}
    python scripts/k_gap_table.py --offline  # skip the OA probe (reads the cached probe if present)
"""
from __future__ import annotations

import csv
import glob
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
DATE = "2026-09-28"

MEASURE = {"EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH", "RESULT_INCOMPATIBLE", "ENGINE_CANNOT_CONSUME",
           "outcome_post_hoc_not_pooled"}
EXTRACT = {"COUNTS_PRESENT_NOT_CORROBORATED", "EXTRACTION_NOT_PERFORMED", "KNOWN_REPORTED_NOT_YET_EXTRACTED",
           "ENDPOINT_UNBOUND"}
ACQUIRE = {"SOURCE_NOT_RETRIEVED", "OUTCOME_NOT_IN_SOURCE", "outcome_not_reported"}
DELIBERATE_KINDS = {"refused_on_evidence", "result_withdrawn", "adjudicated_absent"}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _num(i):
    return re.sub(r"^(PMID|pmid)\s*", "", str(i or "")).strip().upper()


def topic_agents(topic: dict) -> list[str]:
    ag = topic.get("intervention_agents") or {}
    terms = list(ag.keys()) + [s for v in ag.values() for s in (v or [])] + list(topic.get("intervention_terms") or [])
    return sorted({t for t in terms if t and len(t) >= 3}, key=str.lower)


def molecule_names(topic: dict) -> list[str]:
    """Named molecules only (intervention_agents keys + synonyms) -- the vocabulary for "this row names ANOTHER
    served topic's drug". Class terms ("statin", "SGLT2 inhibitor") are excluded: they appear in background-
    therapy columns of trials of a different drug."""
    ag = topic.get("intervention_agents") or {}
    return sorted({t for t in list(ag.keys()) + [x for v in ag.values() for x in (v or [])] if t and len(t) >= 5})


def outcome_keywords(topic: dict) -> list[str]:
    po = topic.get("primary_outcome") or {}
    kws = [po.get("name") or ""] + list(po.get("keywords") or [])
    return [k for k in kws if k and len(k) >= 4 and k.lower() not in (
        "primary outcome", "primary end point", "primary endpoint", "primary efficacy end point",
        "risk of the primary end point", "primary end-point event", "composite primary end-point")]


def ours(slug: str) -> dict:
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), {})
    mem = prim.get("membership") or {}
    pooled = {_num(t.get("id")) for t in prim.get("trials", [])} | {_num(x) for x in mem.get("pooled", [])}
    pooled_fam = {_num(x) for x in mem.get("pooled_family_ids", [])}
    absent = {}
    for d in prim.get("declared_absent_trials", []):
        rec = {"reason_code": d.get("reason_code") or "", "absent_kind": d.get("absent_kind") or "",
               "reason": (d.get("reason") or "")[:240], "id": d.get("id")}
        for k in (d.get("id"), d.get("trial_family_id"), d.get("trial_id"), d.get("report_id")):
            if k:
                absent[_num(k)] = rec
    fams = []
    fp = os.path.join(ROOT, "cache", slug, "families.json")
    if os.path.exists(fp):
        for f in _j(fp).get("families", []):
            fams.append({"family_id": _num(f["family_id"]),
                         "reports": {_num(r["report_id"]) for r in f.get("reports", [])},
                         "acronyms": {k_gap.norm_acronym(a) for a in (f.get("aliases") or {}).get("acronym", [])},
                         "eligibility": (f.get("eligibility") or {}).get("state")})
    rec_ids, rec_acr, rec_text = set(), set(), []
    rp = os.path.join(ROOT, "cache", slug, "records.json")
    if os.path.exists(rp):
        rj = _j(rp)
        for r in rj.get("records", []):
            rec_ids.add(_num(r.get("id")))
            rec_text.append((_num(r.get("id")), r.get("title") or "", r.get("abstract") or ""))
            if r.get("nct"):
                rec_ids.add(_num(r["nct"]))
        for r in rj.get("ctgov", []) or []:
            rec_ids.add(_num(r.get("id")))
            if r.get("acronym"):
                rec_acr.add(k_gap.norm_acronym(r["acronym"]))
    return {"k": (prim.get("result") or {}).get("k"), "pooled": pooled, "pooled_fam": pooled_fam,
            "absent": absent, "families": fams, "rec_ids": rec_ids, "rec_acr": rec_acr, "records_text": rec_text,
            "estimand": (prim.get("estimand") or ""), "outcome": prim.get("name")}


def comparator_units(slug, pmid, agents, others=None):
    p = os.path.join(ROOT, "cache", "comparators", pmid, f"{DATE}_kgap_jats.xml")
    if not os.path.exists(p):
        return {"state": "NO_OPEN_JATS", "units": [], "tables_used": []}, None
    with open(p, "rb") as fh:
        body = fh.read()
    parsed = k_gap.parse_jats(body)
    inc = k_gap.included_trials(parsed, agents, others)
    inc["jats_file"] = os.path.relpath(p, ROOT).replace(os.sep, "/")
    inc["jats_sha256"] = k_gap.sha256(body)
    return inc, parsed


def pub_years(pmids, offline=False) -> dict:
    """PMID -> publication year (NCBI esummary pubdate; cached outputs/k_gap/pubmed_years.json)."""
    cp = os.path.join(OUT, "pubmed_years.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({x for x in pmids if x and x.isdigit() and x not in cache})
    if todo:
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                                  {"db": "pubmed", "id": ",".join(chunk), "retmode": "json"})
            except Exception as exc:  # noqa: BLE001
                print("esummary failed", exc)
                continue
            for x in chunk:
                m = re.match(r"(\d{4})", ((d.get("result") or {}).get(x) or {}).get("pubdate") or "")
                cache[x] = int(m.group(1)) if m else None
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def pubmed_ncts(pmids, offline=False) -> dict:
    """PMID -> the NCT PubMed itself attaches to the paper (DataBankList / 'ClinicalTrials.gov number' in the abstract),
    via harness.fetch._efetch's own selection. A SECONDARY report of a trial carries its trial's NCT here even when
    AACT's study_references never lists it (EMPA-REG secondary 26981940). Cached outputs/k_gap/pubmed_ncts.json."""
    cp = os.path.join(OUT, "pubmed_ncts.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({x for x in pmids if x and x.isdigit() and x not in cache})
    if todo:
        from harness import fetch
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                recs = fetch._efetch(chunk)
            except Exception as exc:  # noqa: BLE001
                print("efetch failed", exc)
                continue
            got = {r.get("id"): (r.get("nct") or "").upper() for r in recs}
            for x in chunk:
                cache[x] = got.get(x, "")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def pubmed_titles_of(pmids, offline=False) -> dict:
    """PMID -> PubMed title (esummary; shares outputs/k_gap/pubmed_titles.json with the identity reader)."""
    cp = os.path.join(OUT, "pubmed_titles.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({x for x in pmids if x and x.isdigit() and x not in cache})
    if todo:
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                                  {"db": "pubmed", "id": ",".join(chunk), "retmode": "json"})
            except Exception as exc:  # noqa: BLE001
                print("esummary failed", exc)
                continue
            for x in chunk:
                cache[x] = ((d.get("result") or {}).get(x) or {}).get("title", "")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def _title_key(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", k_gap.fold_dashes(t or "").lower()).strip()


def registered_before(n, year, idx) -> bool:
    """True unless we KNOW the registration was first submitted after the paper's publication year."""
    d = ((idx.get("study") or {}).get(n) or {}).get("study_first_submitted_date") or ""
    return not (year and d[:4].isdigit() and int(d[:4]) > int(year))


def resolve_unit(u, parsed, idx, agents_re, years=None, our_fams=None):
    """Identity: cited ref PMID > NCT written in the unit > Author-Year against the comparator's own
    ref-list > acronym against AACT studies.acronym restricted to NCTs whose interventions name a topic
    agent. Each step records its basis; an acronym hitting >1 agent NCT is AMBIGUOUS, not guessed."""
    basis = []
    # A citation link is trusted only when the row's own label does not contradict the reference it points to:
    # the omega-3 comparator's table is numbered one off from its reference list (28/28 links), so following the
    # link faithfully resolved every row to the trial in the row above.
    kept = []
    for c in u["cited"]:
        if c.get("basis") is None and u.get("distrust_links"):
            basis.append("xref_table_distrusted:" + u["distrust_links"])
            continue
        why = k_gap.label_ref_conflict(u, c, registry_acronyms_of(c.get("pmid"), idx)) if c.get("basis") is None else None
        if why:
            basis.append(f"xref_label_conflict:{why}")
        else:
            kept.append(c)
    pmids = {c["pmid"] for c in kept if c.get("pmid")}
    ncts = set(u["ncts"])
    if pmids:
        basis.append("comparator_ref_pmid")
    if ncts:
        basis.append("nct_in_table")
    if not pmids and u["author"] and u["year"] and parsed:
        hits = [r for r in parsed["refs"].values()
                if r.get("pmid") and r.get("first_author", "").lower() == u["author"].lower() and r.get("year") == u["year"]]
        if len(hits) == 1:
            pmids.add(hits[0]["pmid"])
            basis.append("author_year_ref_list")
        elif len(hits) > 1:
            basis.append(f"author_year_ambiguous:{len(hits)}")
    # PMID -> NCT only when AACT links the PMID to exactly ONE registration: a paper is cited as background by later
    # trials' registrations (Deftereos' PMIDs are listed by NCT04906720 and NCT06731595, colchicine trials of 2021+),
    # and following those links made Deftereos 'POOLED' via another paper of that NCT (COPPS-2).
    pmid_resolved = bool(pmids)
    years = years or {}
    mapped = sorted({n for p in pmids for n, _t in idx["pmid_nct"].get(p, []) if registered_before(n, years.get(p), idx)})
    dropped = sorted({n for p in pmids for n, _t in idx["pmid_nct"].get(p, [])} - set(mapped))
    if dropped:
        basis.append(f"pmid_nct_registered_after_publication:{','.join(dropped[:4])}")
    if len(mapped) > 1 and our_fams:
        ours = [n for n in mapped if n in our_fams]
        if len(ours) == 1:
            basis.append(f"pmid_nct_tiebreak_our_family:{ours[0]}")
            mapped = ours
    if not mapped:
        own = sorted({PUBNCT.get(p) for p in pmids if PUBNCT.get(p)})
        if len(own) == 1:
            mapped = own
            basis.append(f"pmid_nct_from_pubmed_record:{own[0]}")
    if len(mapped) == 1:
        ncts.add(mapped[0])
    elif len(mapped) > 1:
        basis.append(f"pmid_nct_ambiguous:{','.join(mapped[:4])}")
    if not ncts:
        for a in u["acronyms"]:
            cands = [n for n in idx["acr_nct"].get(k_gap.norm_acronym(a), []) if idx["agent_nct"].get(n)]
            cands = sorted(set(cands))
            if len(cands) == 1:
                ncts.add(cands[0])
                basis.append(f"acronym_aact:{a}")
                break
            if len(cands) > 1:
                basis.append(f"acronym_ambiguous:{a}:{','.join(cands[:4])}")
                continue
            tc = sorted({n for n in idx.get("acr_title_nct", {}).get(k_gap.norm_acronym(a), []) if idx["agent_nct"].get(n)})
            if len(tc) == 1:
                ncts.add(tc[0])
                basis.append(f"acronym_aact_title:{a}")
                break
            if len(tc) > 1:
                basis.append(f"acronym_title_ambiguous:{a}:{','.join(tc[:4])}")
    # NCT -> its PMIDs only when the NCT IS the identity (printed in the table, or an acronym match). When the identity is
    # a cited PMID, adding every other paper registered to its NCT is association, not identity.
    if not pmid_resolved:
        for n in list(ncts):
            pmids |= set(idx.get("nct_pmids", {}).get(n, []))
    return {"pmids": sorted(pmids), "ncts": sorted(ncts), "basis": basis}


def registry_acronyms_of(pmid, idx):
    """Acronyms the REGISTRY gives the trial(s) a PMID reports: AACT acronym field + parenthesised title acronyms."""
    out = []
    for n, _t in (idx.get("pmid_nct") or {}).get(pmid or "", []):
        st = (idx.get("study") or {}).get(n) or {}
        if st.get("acronym"):
            out.append(st["acronym"])
        out += [m.group(1) for m in k_gap._PAREN_ACRO.finditer(st.get("brief_title") or "")]
    return out


def distrust_shifted_tables(units, idx):
    """A publisher numbering shift is SYSTEMATIC: when >=3 and >=50% of a table's citation links contradict their
    rows' labels, no link in that table is trusted (every row then resolves from its own label). The omega-3
    comparator's Table 1 is one off from its reference list on 28 of 28 links."""
    by_table = {}
    for u in units:
        for c in u["cited"]:
            if c.get("basis") is None:
                by_table.setdefault(u["table"], []).append(
                    bool(k_gap.label_ref_conflict(u, c, registry_acronyms_of(c.get("pmid"), idx))))
    for u in units:
        v = by_table.get(u["table"], [])
        if len(v) and sum(v) >= 3 and sum(v) / len(v) >= 0.5:
            u["distrust_links"] = f"{sum(v)}/{len(v)} links in {u['table']} contradict their rows"
    return {t: (sum(v), len(v)) for t, v in by_table.items()}


def registry_agent(ncts, idx):
    """True/False when AACT interventions for the resolved NCTs do / do not name a topic agent; None when
    no NCT resolved or AACT holds no intervention rows."""
    vals = [idx["agent_nct"][n] for n in ncts if n in idx["agent_nct"]]
    return any(vals) if vals else None


def match_ours(ident, acronyms, o):
    ids = set(ident["pmids"]) | set(ident["ncts"])
    acr = {k_gap.norm_acronym(a) for a in acronyms}
    fam = None
    for f in o["families"]:
        if (ids & ({f["family_id"]} | f["reports"])) or (acr & f["acronyms"]):
            fam = f
            break
    fam_ids = ({fam["family_id"]} | fam["reports"]) if fam else set()
    allids = ids | fam_ids
    if allids & (o["pooled"] | o["pooled_fam"]):
        return "POOLED", fam, None
    for k in allids:
        if k in o["absent"]:
            return "DECLARED_ABSENT", fam, o["absent"][k]
    if fam or (allids & o["rec_ids"]) or (acr & o["rec_acr"]):
        return "IDENTIFIED_NOT_POOLED", fam, None
    return "NOT_IDENTIFIED", None, None


def aact_source(ncts, idx, kws, estimand):
    """Does AACT hold POSTED results for an outcome matching the topic's primary outcome? Returns the
    matching outcome rows with their type (param_type), timeframe and analysis population verbatim."""
    kre = re.compile("|".join(re.escape(k) for k in kws), re.I) if kws else None
    posted, matches = False, []
    for n in ncts:
        outs = idx["outcomes"].get(n, [])
        if outs:
            posted = True
        for oc in outs:
            if kre and kre.search(oc["title"] + " " + oc.get("time_frame", "")):
                matches.append({"nct": n, **{k: oc[k] for k in ("outcome_type", "title", "time_frame", "population",
                                                                "param_type", "units")}})
    return {"results_posted": posted, "outcome_matches": matches[:4], "n_matches": len(matches)}


def classify(status, absent, reg_agent, aact_src, oa):
    if status == "POOLED":
        return "POOLED"
    if status == "UNRESOLVED":
        return "UNRESOLVED_IDENTITY"
    if status == "SCOPE_MISMATCH":
        return "SCOPE_MISMATCH"
    if status == "DECLARED_ABSENT":
        rc, kind = absent["reason_code"], absent["absent_kind"]
        if rc in MEASURE or kind in ("refused_on_evidence", "engine_cannot_consume"):
            return "MEASURE_MISMATCH"
        if rc in EXTRACT:
            return "EXTRACTION_FROM_TABLE"
        if kind in DELIBERATE_KINDS and rc not in ACQUIRE:
            return "MEASURE_MISMATCH"
    if status == "IDENTIFIED_NOT_POOLED":
        pass
    open_src = aact_src["n_matches"] > 0 or oa
    if status == "NOT_IDENTIFIED":
        return "IDENTIFICATION"
    if status == "IDENTIFIED_NOT_POOLED":
        return "SCREEN_OR_ELIGIBILITY"
    return "ACQUISITION" if open_src else "GENUINELY_UNAVAILABLE_OPEN"


NOT_YET_EXTRACTED = {"IDENTIFICATION", "SCREEN_OR_ELIGIBILITY"}


def closable_by(cls, aact_src, oa, upw=False, abstract_hit=False):
    """Best open source for a typed result, in the harness's own ladder order for a trial of this class.
    The PubMed abstract counts only for a trial the pipeline has NOT yet tried to extract (not identified, or
    screened out): for a declared-absent trial the abstract was already read and found wanting."""
    if cls in ("POOLED", "MEASURE_MISMATCH", "UNRESOLVED_IDENTITY", "SCOPE_MISMATCH"):
        return ""
    if aact_src["n_matches"] > 0:
        return "AACT_RESULTS"
    if oa:
        return "PMC_OA_FULLTEXT"
    if upw:
        return "UNPAYWALL_OA_COPY"
    if abstract_hit and cls in NOT_YET_EXTRACTED:
        return "PUBMED_ABSTRACT_OUTCOME"
    return "NONE_OPEN_PROBED"


_EFFECT = re.compile(r"\b(?:HR|RR|OR|hazard ratio|risk ratio|relative risk|odds ratio|rate ratio|mean difference|"
                     r"difference)\b[^.;]{0,60}?\d|\b\d+\s*/\s*\d+\b|\b\d+\s*\(\s*\d+(?:\.\d+)?\s*%\)", re.I)


def abstract_reports_outcome(abstract: str, kws: list[str]) -> str | None:
    """A sentence of the abstract that names the topic outcome AND carries a numeric result (an effect with a
    number, n/N, or n (x%)). Returns the sentence (the span) or None. A signal that the abstract rung is worth
    running -- not an extraction, and never an admitted number."""
    if not abstract or not kws:
        return None
    kre = re.compile("|".join(re.escape(k) for k in kws), re.I)
    for sent in re.split(r"(?<=[.;])\s+", abstract):
        if kre.search(sent) and _EFFECT.search(sent):
            return sent[:300]
    return None


def trial_abstracts(pmids, offline) -> dict:
    """PMID -> {abstract, doi} via efetch (batched 150, cached outputs/k_gap/trial_abstracts.json)."""
    cp = os.path.join(OUT, "trial_abstracts.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({p for p in pmids if p.isdigit() and p not in cache})
    if todo:
        import time
        import xml.etree.ElementTree as ET
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                x = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                                  {"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"}, timeout=60)
            except Exception as exc:  # noqa: BLE001
                print("efetch failed", exc)
                continue
            for a in ET.fromstring(x).iter("PubmedArticle"):
                pm = a.find(".//PMID").text
                doi = next((e.text for e in a.iter("ArticleId") if e.get("IdType") == "doi" and e.text), "")
                cache[pm] = {"abstract": " ".join("".join(e.itertext()) for e in a.iter("AbstractText")), "doi": doi}
            time.sleep(0.4)
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def unpaywall_probe(dois, offline) -> dict:
    """DOI -> {is_oa, host_type, url} via Unpaywall (cached outputs/k_gap/unpaywall.json). Records where an OA
    copy is; fetching it is the adapter's job, not the probe's."""
    cp = os.path.join(OUT, "unpaywall.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({d.lower() for d in dois if d and d.lower() not in cache})
    if todo:
        import time
        import urllib.parse
        from harness import http
        for d in todo:
            try:
                r = http.get_json("https://api.unpaywall.org/v2/" + urllib.parse.quote(d),
                                  {"email": "meta-harness@example.org"}, tries=2)
                b = r.get("best_oa_location") or {}
                cache[d] = {"is_oa": bool(r.get("is_oa")), "host_type": b.get("host_type"),
                            "url": b.get("url_for_pdf") or b.get("url"), "license": b.get("license")}
            except Exception as exc:  # noqa: BLE001
                cache[d] = {"error": str(exc)[:160]}
            time.sleep(0.15)
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def oa_probe(pmids: list[str], offline: bool) -> dict:
    """PMID -> {pmcid, is_oa} via NCBI idconv (batches of 150) + Europe PMC OA flag. Cached."""
    cp = os.path.join(OUT, "oa_probe.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = sorted({p for p in pmids if p.isdigit() and p not in cache})
    if todo and not offline:
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                d = http.get_json("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/",
                                  {"ids": ",".join(chunk), "format": "json", "tool": "meta-harness",
                                   "email": "meta-harness@example.org"})
            except Exception as exc:  # noqa: BLE001
                print("idconv failed", exc)
                continue
            for r in d.get("records", []):
                p = str(r.get("pmid") or "")
                if p:
                    cache[p] = {"pmcid": r.get("pmcid") or "", "doi": r.get("doi") or "", "is_oa": None}
        pmcs = sorted({v["pmcid"] for v in cache.values() if v.get("pmcid") and v.get("is_oa") is None})
        for i in range(0, len(pmcs), 40):
            chunk = pmcs[i:i + 40]
            q = " OR ".join(f"PMCID:{c}" for c in chunk)
            try:
                d = http.get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                                  {"query": q, "format": "json", "resultType": "lite", "pageSize": 100})
            except Exception as exc:  # noqa: BLE001
                print("epmc failed", exc)
                continue
            flag = {r.get("pmcid"): r.get("isOpenAccess") == "Y" for r in d.get("resultList", {}).get("result", [])}
            for v in cache.values():
                if v.get("pmcid") in flag:
                    v["is_oa"] = flag[v["pmcid"]]
        os.makedirs(OUT, exist_ok=True)
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


PROP = os.path.join(ROOT, "registry", "model_proposals", "comparator_members.json")
YEARS: dict = {}
PUBNCT: dict = {}
TITLES: dict = {}
STORE = os.environ.get("K_GAP_AACT_STORE") or os.path.join(OUT, "_aact_store.json")
_AUTH_YR = re.compile(r"^([A-Z][A-Za-z'À-ſ‐-]+)[^0-9]{0,14}((?:19|20)\d\d)[a-z]?$")


def comparator_abstracts(pmids, offline) -> dict:
    """PMID -> PubMed abstract text for the comparators (cached outputs/k_gap/comparator_abstracts.json)."""
    cp = os.path.join(OUT, "comparator_abstracts.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [p for p in pmids if p not in cache]
    if todo and not offline:
        import xml.etree.ElementTree as ET
        from harness import http
        x = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                          {"db": "pubmed", "id": ",".join(todo), "retmode": "xml"})
        for a in ET.fromstring(x).iter("PubmedArticle"):
            cache[a.find(".//PMID").text] = " ".join("".join(e.itertext()) for e in a.iter("AbstractText"))
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


def proposal_units(slug: str, agents: list[str], others: list[str] | None = None) -> list[dict]:
    if not os.path.exists(PROP):
        return []
    it = _j(PROP)["items"].get(slug) or {}
    v = it.get("verification") or {}
    agent_re = re.compile("|".join(re.escape(a) for a in agents), re.I) if agents else None
    other_re = re.compile("|".join(re.escape(a) for a in others), re.I) if others else None
    out = []
    for s in v.get("admitted", []):
        lab = s["label"].strip()
        toks = k_gap._label_tokens(lab)
        m = _AUTH_YR.match(lab)
        acr = toks["acronyms"] or ([lab] if re.match(r"^[A-Z][A-Z0-9-]{2,}", lab) else [])
        hit = bool(agent_re and agent_re.search(lab + " " + s["quote"]))
        oth = bool(other_re and other_re.search(lab + " " + s["quote"]))
        out.append({"table": "proposal:" + it.get("record_id", ""), "layout": "text", "label": lab,
                    "context": s["quote"], "rids": [], "cited": [], "ncts": toks["ncts"], "acronyms": acr,
                    "author": toks["author"] or (m.group(1) if m else ""), "year": toks["year"] or (m.group(2) if m else ""),
                    "agent_hit": hit, "drug_match": "DRUG_MATCH" if hit else ("OTHER_AGENT" if oth else "AGENT_IMPLICIT"),
                    "design_stated": s["design_stated"]})
    return out


def self_names(acr, title, abstract) -> bool:
    """Does a record NAME ITSELF by this acronym -- in its title, or defined in parentheses in its abstract?"""
    core = k_gap.fold_dashes(re.sub(r"\s+(?:(?:19|20)\d\d|\d{1,3})$", "", (acr or "").strip()))
    core = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", core)
    if len(k_gap.norm_acronym(core)) < 4:
        return False
    pat = re.escape(core).replace("\\-", "[-\\s]?").replace("\\ ", "[-\\s]?")
    if re.search(rf"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])", k_gap.fold_dashes(title or ""), re.I):
        return True
    # exactly "(ACRONYM)": a parenthesised LIST "(CORE, CORP)" is a citation of several trials, not a definition
    return bool(re.search(rf"\(\s*{pat}\s*\)", k_gap.fold_dashes(abstract or ""), re.I))


def acronym_in_our_records(acronyms, recs, families):
    """An acronym-only label (ROCKET AF, HARMONY, CORE) resolved against OUR OWN held records: a record names ITSELF
    by an acronym in its TITLE, or DEFINES it in parentheses in its abstract ('... Stroke and Embolism Trial in Atrial
    Fibrillation (ROCKET AF)'). A bare mention does not count -- other trials' abstracts cite landmark trials in
    passing. Resolves only when every self-naming record falls in ONE of our trial families."""
    rep_to_fam = {}
    for f in families:
        for r in f["reports"]:
            rep_to_fam[r] = f
    for a in acronyms:
        core = k_gap.fold_dashes(re.sub(r"\s+(?:(?:19|20)\d\d|\d{1,3})$", "", a.strip()))
        if len(k_gap.norm_acronym(core)) < 4:
            continue
        pat = re.escape(core).replace("\\-", "[-\\s]?").replace("\\ ", "[-\\s]?")
        tre = re.compile(rf"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])")
        dre = re.compile(rf"\(\s*{pat}\s*[),;]")
        hits = {rid for rid, title, abstract in recs
                if tre.search(k_gap.fold_dashes(title or "")) or dre.search(k_gap.fold_dashes(abstract or ""))}
        fams = {rep_to_fam[h]["family_id"] for h in hits if h in rep_to_fam}
        if hits and len(fams) == 1 and all(h in rep_to_fam for h in hits):
            return rep_to_fam[next(iter(hits))], a, sorted(hits)
    return None, None, []


def family_by_acronym(acronyms, families):
    """Our own trial family whose registered acronym equals, or is a >=5-char prefix-extension of, the unit's
    acronym (RALES == RALES; HARMONY -> 'HARMONY Outcomes'). Our families are a small, topic-scoped set, so a
    prefix here cannot wander into an unrelated trial the way a registry-wide prefix search would."""
    for a in acronyms:
        na = k_gap.norm_acronym(a)
        if len(na) < 4:
            continue
        hits = [f for f in families if any(fa == na or (len(na) >= 5 and fa.startswith(na)) for fa in f["acronyms"])]
        if len(hits) == 1:
            return hits[0]
    return None


_COMP_DEFAULT = ["placebo", "sham", "usual care", "standard care", "standard of care", "no treatment", "control"]


_PLACEBO_TYPES = {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION"}


def comparator_scope(ncts, idx, topic):
    """Does the trial's registered design contain the topic's registered comparator? A comparator meta can
    include active-comparator trials (finerenone vs EPLERENONE in an MRA-vs-placebo topic); such a trial is a
    SCOPE difference, not a gap. Read from the ARM TYPE (design_groups.group_type), not intervention names: a
    double-dummy active-comparator trial lists 'placebo' among its interventions. For a placebo topic the
    comparator is present iff some arm is PLACEBO/SHAM/NO_INTERVENTION; for an active-comparator topic iff some
    arm's title names a comparator term. UNKNOWN when no NCT resolved or AACT holds no arms."""
    terms = list((topic.get("include") or {}).get("comparator_any") or []) or _COMP_DEFAULT
    groups = [g for n in ncts for g in (idx.get("design_groups") or {}).get(n, [])]
    if not groups:
        return {"state": "UNKNOWN"}
    placebo_topic = any(t.lower() in ("placebo", "sham", "control", "no treatment", "usual care") for t in terms)
    types = [g["group_type"].upper() for g in groups]
    tre = re.compile("|".join(re.escape(t) for t in terms), re.I)
    # placebo topic: the arm TYPE alone decides ('Eplerenone [25 mg] + Placebo' is ARTS-HF's ACTIVE arm, so a
    # title match on 'placebo' would call a double-dummy active-comparator trial placebo-controlled)
    present = any(t in _PLACEBO_TYPES for t in types) if placebo_topic else any(tre.search(g["title"]) for g in groups)
    st = "COMPARATOR_IN_REGISTRY_ARMS" if present else "COMPARATOR_NOT_IN_REGISTRY_ARMS"
    return {"state": st, "arm_types": sorted(set(types)), "terms": terms[:6]}


def pubmed_acronym(acr, agents, offline):
    """Last-resort identity for an acronym-only label (pre-registry trials): PubMed acronym[tiab] + topic agent +
    RCT publication type. One hit -> that PMID; several -> the EARLIEST (lowest PMID), with the hit count
    recorded in the basis so a reader sees it was a choice among n. Cached for replay.
    CHANGED 2026-09-29: several hits now resolve NOTHING. 'Earliest of n' mapped HARMONY (Outcomes) to a
    HARMONY-3 report (earliest of 14) -- a choice among n reports of a programme is not an identity."""
    cp = os.path.join(OUT, "pubmed_acronym.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    acr = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", acr)       # 'RALES1999' -> 'RALES'
    q = f'"{acr}"[tiab] AND ({ag}) AND randomized controlled trial[pt]'
    if q not in cache and not offline:
        import time
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                              {"db": "pubmed", "term": q, "retmode": "json", "retmax": 50})
            cache[q] = d.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:  # noqa: BLE001
            cache[q] = {"error": str(exc)[:200]}
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
        time.sleep(0.4)
    ids = cache.get(q)
    if isinstance(ids, list) and len(ids) == 1:
        return ids[0], q, 1
    return None, q, len(ids) if isinstance(ids, list) else 0


def pubmed_acronym_ids(acr, agents, offline):
    """All PMIDs for the acronym query pubmed_acronym runs (same cached query, same bytes)."""
    pubmed_acronym(acr, agents, offline)
    cp = os.path.join(OUT, "pubmed_acronym.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    acr2 = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", acr)
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    ids = cache.get(f'"{acr2}"[tiab] AND ({ag}) AND randomized controlled trial[pt]')
    return ids if isinstance(ids, list) else []


WIDE_DESIGN = ('(randomized controlled trial[pt] OR controlled clinical trial[pt] OR clinical trial[pt] OR '
               'randomi*[tiab] OR randomly[tiab])')


def author_year_wide_query(author, year, agents):
    """The widened design filter: a pre-registry trial indexed only as 'Controlled Clinical Trial' whose abstract says
    'randomly' (Nestler 1998, NEJM) is invisible to the RCT filter. Consulted only when the strict query finds nothing;
    design is decided later by the screen, never by this query."""
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    return f"{author}[1au] AND {year}[dp] AND ({ag}) AND {WIDE_DESIGN}"


def _esearch_cached(q, cache, offline):
    if q not in cache and not offline:
        import time
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                              {"db": "pubmed", "term": q, "retmode": "json", "retmax": 5})
            cache[q] = d.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:  # noqa: BLE001
            cache[q] = {"error": str(exc)[:200]}
        time.sleep(0.4)
        return True
    return False


def pubmed_author_year(author, year, agents, offline):
    """PMID for 'Author Year' + topic agent via NCBI ESearch -- admitted only when EXACTLY one hit.
    The strict RCT-filtered query first; only when it returns NO hit (an empty list, never an error), the widened design
    filter (author_year_wide_query). Queries and answers are cached (outputs/k_gap/pubmed_author_year.json) so a rerun
    replays them."""
    cp = os.path.join(OUT, "pubmed_author_year.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    q = f"{author}[1au] AND {year}[dp] AND ({ag}) AND (randomized controlled trial[pt] OR randomi*[tiab])"
    dirty = _esearch_cached(q, cache, offline)
    ids = cache.get(q)
    if ids == []:
        q = author_year_wide_query(author, year, agents)
        dirty = _esearch_cached(q, cache, offline) or dirty
        ids = cache.get(q)
    if dirty:
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return (ids[0] if isinstance(ids, list) and len(ids) == 1 else None), q, ids


def main(argv=None):
    argv = argv or sys.argv[1:]
    offline = "--offline" in argv
    log = lambda m: print(m, flush=True)  # noqa: E731
    os.makedirs(OUT, exist_ok=True)
    topics = []
    for f in sorted(glob.glob(os.path.join(ROOT, "cache", "*", "comparators.json"))):
        slug = os.path.basename(os.path.dirname(f))
        c = _j(f)[0]
        m = re.search(r"PMID (\d+)", c.get("citation", ""))
        topics.append((slug, m.group(1) if m else str(c["id"]), c.get("citation", "")))
    store = k_gap.AactStore(STORE)
    store.build_maps(log=log)
    abstracts = comparator_abstracts([t[1] for t in topics], offline)
    per = {}
    other_all = sorted({a for t in topics for a in molecule_names(_j(os.path.join(ROOT, "topics", t[0] + ".json")))},
                       key=str.lower)
    for slug, cpmid, cit in topics:
        topic = _j(os.path.join(ROOT, "topics", slug + ".json"))
        agents = topic_agents(topic)
        others = [a for a in other_all if not re.search("|".join(re.escape(x) for x in agents), a, re.I)]
        inc, parsed = comparator_units(slug, cpmid, agents, others)
        try:
            text, ref = k_gap.held_text(slug, DATE)
        except Exception as exc:  # noqa: BLE001
            text, ref = "", f"UNREADABLE: {exc}"
        held = {"ref": ref, **k_gap.held_text_identity(abstracts.get(cpmid, ""), text)}
        cands = [("JATS_TABLE", inc)]
        if held["state"] == "NAMED_ARTICLE":
            pu = proposal_units(slug, agents, others)
            if pu:
                cands.append(("MODEL_PROPOSAL_GATED", {"state": "PROPOSAL_GATED", "units": pu,
                                                       "tables_used": [pu[0]["table"]]}))
        per[slug] = {"topic": topic, "agents": agents, "others": others, "parsed": parsed, "ours": ours(slug),
                     "comparator_pmid": cpmid, "citation": cit, "held": held, "cands": cands, "tried": []}

    def prep(P, units):
        need = set()
        for u in units:
            if not u["cited"] and P["parsed"] and u["layout"] == "text":
                rs = k_gap.refs_by_number(u["label"], P["parsed"]["refs"])
                if rs and all(r.get("pmid") for r in rs):
                    u["cited"] = [{"pmid": r["pmid"], "doi": r.get("doi"), "basis": "label_ref_number"} for r in rs]
            if not u["cited"] and not u["ncts"] and u["author"] and u["year"]:
                refhit = None
                if P["parsed"]:
                    hits = [r for r in P["parsed"]["refs"].values() if r.get("pmid") and
                            r.get("first_author", "").lower() == u["author"].lower() and r.get("year") == u["year"]]
                    refhit = hits[0]["pmid"] if len(hits) == 1 else None
                if refhit:
                    u["cited"] = [{"pmid": refhit, "basis": "author_year_ref_list"}]
                else:
                    pm, q, ids = pubmed_author_year(u["author"], u["year"], P["agents"], offline)
                    u["pubmed_query"] = {"q": q, "ids": ids}
                    if pm:
                        u["cited"] = [{"pmid": pm, "basis": "pubmed_author_year_single_hit"}]
            for c in u["cited"]:
                need |= {n for n, _t in store.d["pmid"].get(c.get("pmid") or "", [])}
            need |= set(u["ncts"])
            for a in u["acronyms"]:
                need |= set(store.d["acr"].get(k_gap.norm_acronym(a), [])[:25])
        return need

    def resolve_rows(slug, P, units, source):
        tidx = store.index(P["agents"])
        P.setdefault("link_audit", {})[source] = distrust_shifted_tables(units, tidx)
        agents_re = re.compile("|".join(re.escape(a) for a in P["agents"]), re.I)
        out = []
        for u in units:
            ident = resolve_unit(u, P["parsed"], tidx, agents_re, years=YEARS,
                                 our_fams={f["family_id"] for f in P["ours"]["families"]})
            ident["basis"] += [c["basis"] for c in u["cited"] if c.get("basis")]
            if ident["pmids"] and not ident["ncts"]:
                # the cited PMID is a second record of a paper we HOLD (same title): EMPA-REG's NEJM article has two
                # PubMed records (26378978, 26981940); the comparator cites the other one. Exact normalised title only.
                keys = {_title_key(TITLES.get(p, "")) for p in ident["pmids"] if len(_title_key(TITLES.get(p, ""))) >= 30}
                same = {rid for rid, title, _ab in P["ours"]["records_text"] if _title_key(title) in keys}
                r2f = {r: f for f in P["ours"]["families"] for r in f["reports"]}
                fams = {r2f[x]["family_id"]: r2f[x] for x in same if x in r2f}
                if len(fams) == 1:
                    f = next(iter(fams.values()))
                    if f["family_id"].startswith("NCT"):
                        ident["ncts"] = [f["family_id"]]
                    ident["pmids"] = sorted(set(ident["pmids"]) | {x for x in same if x in f["reports"]})
                    ident["basis"].append(f"cited_title_equals_our_record:{','.join(sorted(same))[:40]}")
            if not ident["pmids"] and not ident["ncts"] and u["acronyms"]:
                fam_rec, acr_used, hits = acronym_in_our_records(u["acronyms"], P["ours"]["records_text"],
                                                                 P["ours"]["families"])
                if fam_rec:
                    ident["ncts"] = [fam_rec["family_id"]] if fam_rec["family_id"].startswith("NCT") else []
                    ident["pmids"] = sorted(x for x in fam_rec["reports"] if x.isdigit())
                    ident["basis"].append(f"acronym_self_named_in_our_records:{acr_used}:{','.join(hits[:3])}")
            if not ident["pmids"] and not ident["ncts"] and u["acronyms"]:
                # PubMed's reports of the acronym (RCT-typed, topic drug) INTERSECTED with the families we hold: PubMed
                # supplies the trial's reports, our corpus disambiguates. ROCKET AF: many PubMed reports, one family ours.
                ids = pubmed_acronym_ids(u["acronyms"][0], P["agents"], offline)
                r2f = {r: f for f in P["ours"]["families"] for r in f["reports"]}
                # the held record must NAME ITSELF by the acronym (title, or defined in parentheses): a held paper
                # that merely CITES the trial matched the tiab query too -- CORE resolved to a 2024 paper citing it
                named = {rid for rid, title, ab in P["ours"]["records_text"]
                         if self_names(u["acronyms"][0], title, ab)}
                fams = {r2f[i]["family_id"]: r2f[i] for i in ids if i in r2f and i in named}
                if len(fams) == 1:
                    f = next(iter(fams.values()))
                    ident["ncts"] = [f["family_id"]] if f["family_id"].startswith("NCT") else []
                    ident["pmids"] = sorted(x for x in f["reports"] if x.isdigit())
                    ident["basis"].append(f"pubmed_acronym_x_our_family:{u['acronyms'][0]}:{len(ids)}_hits")
            if not ident["pmids"] and not ident["ncts"]:
                fam_hit = family_by_acronym(u["acronyms"], P["ours"]["families"])
                if fam_hit:
                    ident["ncts"] = [fam_hit["family_id"]] if fam_hit["family_id"].startswith("NCT") else []
                    ident["pmids"] = sorted(x for x in fam_hit["reports"] if x.isdigit())
                    ident["basis"].append("acronym_our_family:" + fam_hit["family_id"])
                elif u["acronyms"] and u["layout"] == "text":
                    # only for a label the model QUOTED as an included study -- never a table row (the noac IPD
                    # baseline table's 'CHADS2 score' row resolved to a RE-LY sub-analysis through this path)
                    pm, q, n_hits = pubmed_acronym(u["acronyms"][0], P["agents"], offline)
                    u["pubmed_query"] = {"q": q, "n": n_hits}
                    if pm:
                        ident["pmids"] = [pm]
                        ident["basis"].append("pubmed_acronym_single_hit")
                        ident["ncts"] = [n for n, _t in tidx["pmid_nct"].get(pm, [])]
            reg = registry_agent(ident["ncts"], tidx)
            scope = comparator_scope(ident["ncts"], tidx, P["topic"])
            # the unit's own text naming our agent wins; else the REGISTRY decides when an NCT resolved; the
            # text "names another served topic's molecule" check applies only when the registry cannot speak.
            if u["agent_hit"] or reg:
                drug = "DRUG_MATCH"
            elif reg is False or u["drug_match"] == "OTHER_AGENT":
                drug = "OTHER_AGENT"
            else:
                drug = "AGENT_UNCONFIRMED"
            if not ident["pmids"] and not ident["ncts"]:
                status, fam, absent = "UNRESOLVED", None, None
            else:
                status, fam, absent = match_ours(ident, u["acronyms"], P["ours"])
                if status in ("NOT_IDENTIFIED", "IDENTIFIED_NOT_POOLED") and \
                        scope["state"] == "COMPARATOR_NOT_IN_REGISTRY_ARMS":
                    status = "SCOPE_MISMATCH"
            src = aact_source(ident["ncts"], tidx, outcome_keywords(P["topic"]), P["ours"]["estimand"])
            out.append({"slug": slug, "comparator_pmid": P["comparator_pmid"], "unit_source": source,
                        "table": u["table"], "layout": u["layout"], "label": u["label"], "context": u["context"][:300],
                        "drug": drug, "pmids": ident["pmids"], "ncts": ident["ncts"], "identity_basis": ident["basis"],
                        "pubmed_query": u.get("pubmed_query"), "design_stated": u.get("design_stated"),
                        "cited_doi": [c.get("doi") for c in u["cited"] if c.get("doi")],
                        "cited_pmids": sorted({c["pmid"] for c in u["cited"] if c.get("pmid")}),
                        "status": status, "family_id": fam["family_id"] if fam else "",
                        "family_eligibility": fam["eligibility"] if fam else "",
                        "declared_absent": absent, "aact": src, "comparator_scope": scope,
                        "study": {n: tidx["study"].get(n) for n in ident["ncts"]}})
        return out

    def n_elig(rs):
        return sum(r["drug"] != "OTHER_AGENT" and r["status"] != "UNRESOLVED" for r in rs)

    # round 1: every held candidate source for every topic (one batched AACT fact scan)
    need = set()
    for P in per.values():
        for _src, inc in P["cands"]:
            need |= prep(P, inc["units"])
        o = P["ours"]
        need |= {x for x in o["pooled_fam"] | set(o["absent"]) if x.startswith("NCT")}
    store.ensure_ncts(need, log=log)
    store.ensure_design_groups(log=log)
    cited = {c.get("pmid") for P in per.values() for _src, inc in P["cands"] for u in inc["units"]
             for c in u["cited"] if c.get("pmid")}
    YEARS.update(pub_years(cited, offline))
    PUBNCT.update(pubmed_ncts(cited, offline))
    TITLES.update(pubmed_titles_of(cited, offline))
    store.ensure_ncts({n for n in PUBNCT.values() if n}, log=log)
    store.ensure_registration_dates({n for p in cited for n, _t in store.d["pmid"].get(p, [])}, log=log)
    for slug, P in per.items():
        P["chosen"] = None
        for src, inc in P["cands"]:
            rs = resolve_rows(slug, P, inc["units"], src)
            P["tried"].append({"source": src, "units": len(rs), "drug_specific_resolved": n_elig(rs)})
            if P["chosen"] is None and n_elig(rs):
                P["chosen"], P["rows"], P["inc"] = src, rs, inc
    # round 2: reference seeding, only where no held source resolved a drug-specific trial
    need = set()
    for slug, P in per.items():
        if P["chosen"]:
            continue
        er = k_gap.fetch_epmc_references(P["comparator_pmid"], DATE, offline)
        pt = k_gap.pubmed_pubtypes([r["pmid"] for r in er["refs"]], os.path.join(OUT, "pubmed_pubtypes.json"), offline) \
            if er["refs"] else {}
        su = k_gap.reference_seed_units(er["refs"], pt, P["agents"])
        P["seed"] = {"state": "REFERENCE_SEEDED_CANDIDATES", "units": su, "tables_used": [er.get("file", "")],
                     "refs_held": len(er["refs"])}
        need |= prep(P, su)
    store.ensure_ncts(need, log=log)
    store.ensure_design_groups(log=log)
    cited2 = {c.get("pmid") for P in per.values() if P.get("seed") for u in P["seed"]["units"] for c in u["cited"]
              if c.get("pmid")}
    YEARS.update(pub_years(cited2, offline))
    PUBNCT.update(pubmed_ncts(cited2, offline))
    TITLES.update(pubmed_titles_of(cited2, offline))
    store.ensure_ncts({n for n in PUBNCT.values() if n}, log=log)
    store.ensure_registration_dates({n for p in cited2 for n, _t in store.d["pmid"].get(p, [])}, log=log)
    rows = []
    for slug, P in per.items():
        if not P["chosen"] and P.get("seed"):
            rs = resolve_rows(slug, P, P["seed"]["units"], "REFERENCE_SEED")
            P["tried"].append({"source": "REFERENCE_SEED", "units": len(rs), "drug_specific_resolved": n_elig(rs),
                               "refs_held": P["seed"]["refs_held"]})
            if n_elig(rs):
                P["chosen"], P["rows"], P["inc"] = "REFERENCE_SEED", rs, P["seed"]
        if not P["chosen"]:
            P["rows"], P["inc"] = [], {"state": "NONE", "tables_used": []}
        P["unit_source"] = P["chosen"] or "NONE"
        rows += P["rows"]
    oa = oa_probe([p for r in rows for p in r["pmids"] if r["status"] != "POOLED"], offline)
    notpooled = [r for r in rows if r["status"] not in ("POOLED", "UNRESOLVED")]
    abst = trial_abstracts([p for r in notpooled for p in r["pmids"][:4]], offline)
    for r in notpooled:
        r["dois"] = sorted({d for d in r["cited_doi"] if d} | {abst[p]["doi"] for p in r["pmids"][:4]
                                                                if p in abst and abst[p].get("doi")})
    upw = unpaywall_probe([d for r in notpooled for d in r.get("dois", [])], offline)
    for r in rows:
        oas = [oa.get(p, {}) for p in r["pmids"]]
        r["pmc_oa"] = [{"pmid": p, **oa.get(p, {})} for p in r["pmids"] if oa.get(p, {}).get("pmcid")]
        is_oa = any(v.get("is_oa") for v in oas)
        r["unpaywall"] = [{"doi": d, **upw.get(d.lower(), {})} for d in r.get("dois", []) if upw.get(d.lower(), {}).get("is_oa")]
        kws = outcome_keywords(per[r["slug"]]["topic"])
        r["abstract_outcome_span"] = next((sp for p in r["pmids"][:4]
                                           for sp in [abstract_reports_outcome((abst.get(p) or {}).get("abstract", ""), kws)]
                                           if sp), None)
        r["gap_class"] = classify(r["status"], r["declared_absent"], None, r["aact"], is_oa or bool(r["unpaywall"]))
        r["closable_by"] = closable_by(r["gap_class"], r["aact"], is_oa, bool(r["unpaywall"]),
                                       bool(r["abstract_outcome_span"]))
    topics_out = []
    for slug, cpmid, cit in topics:
        P = per[slug]
        tr = [r for r in rows if r["slug"] == slug]
        elig = [r for r in tr if r["drug"] != "OTHER_AGENT" and r["status"] != "UNRESOLVED"]
        if P["chosen"] == "JATS_TABLE":
            state = "TABLE_ENUMERATED"
        elif P["chosen"] == "MODEL_PROPOSAL_GATED":
            state = "PROPOSAL_ENUMERATED_GATED"
        elif P["chosen"] == "REFERENCE_SEED":
            state = "REFERENCE_SEED_CANDIDATES"
        else:
            state = "NOT_ENUMERABLE_OPEN"
        topics_out.append({
            "slug": slug, "comparator_pmid": cpmid, "comparator": cit[:160], "unit_source": P["unit_source"],
            "comparator_set_state": state, "held_text": P["held"], "tables_used": P["inc"]["tables_used"],
            "sources_tried": P["tried"], "link_audit": P.get("link_audit", {}),
            "our_k": P["ours"]["k"], "comparator_units": len(tr), "drug_specific_resolved": len(elig),
            "other_agent": sum(r["drug"] == "OTHER_AGENT" for r in tr),
            "unresolved_labels": sum(r["status"] == "UNRESOLVED" for r in tr),
            "pooled_of_theirs": sum(r["gap_class"] == "POOLED" for r in elig),
            "missing": sum(r["gap_class"] != "POOLED" for r in elig),
            "by_class": dict(Counter(r["gap_class"] for r in elig if r["gap_class"] != "POOLED")),
            "by_source": dict(Counter(r["closable_by"] for r in elig if r["closable_by"])),
            "missing_trials": [{"label": r["label"], "pmids": r["pmids"], "ncts": r["ncts"], "gap_class": r["gap_class"],
                                "closable_by": r["closable_by"]} for r in elig if r["gap_class"] != "POOLED"],
        })
    out = {"generated": DATE, "aact_snapshot": store.snap, "topics": topics_out, "trials": rows}
    with open(os.path.join(OUT, "k_gap_table.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, default=list)
    cols = ["slug", "comparator_pmid", "unit_source", "label", "drug", "status", "gap_class", "closable_by", "pmids",
            "ncts", "identity_basis", "family_id", "family_eligibility", "declared_reason_code", "aact_results_posted",
            "aact_outcome_match", "aact_param_type", "aact_time_frame", "aact_population", "pmc_oa", "table"]
    with open(os.path.join(OUT, "k_gap_table.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            m = r["aact"]["outcome_matches"][0] if r["aact"]["outcome_matches"] else {}
            w.writerow([r["slug"], r["comparator_pmid"], r["unit_source"], r["label"], r["drug"], r["status"],
                        r["gap_class"], r["closable_by"], ";".join(r["pmids"]), ";".join(r["ncts"]),
                        ";".join(r["identity_basis"]), r["family_id"], r["family_eligibility"],
                        (r["declared_absent"] or {}).get("reason_code", ""), r["aact"]["results_posted"],
                        m.get("title", ""), m.get("param_type", ""), m.get("time_frame", ""), m.get("population", "")[:160],
                        ";".join(x["pmcid"] for x in r["pmc_oa"] if x.get("is_oa")), r["table"]])
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    o = main()
    for t in o["topics"]:
        print(f"{t['slug'][:38]:38s} state={t['comparator_set_state'][:14]:14s} ourk={t['our_k']} units={t['comparator_units']:3d} "
              f"elig={t['drug_specific_resolved']:3d} pooled={t['pooled_of_theirs']:2d} miss={t['missing']:2d} "
              f"other={t['other_agent']:2d} unres={t['unresolved_labels']:2d} {t['by_class']} {t['by_source']}")
