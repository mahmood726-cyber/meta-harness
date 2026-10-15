"""K-gap IDENTIFICATION step (external review, 13 Oct): before phase 4, every PMID-bearing missing trial without a
registry id is resolved -- deterministic and source-linked first -- to its registry id(s), its protocol and its companion
/ primary-outcome publications. Identification gains are reported SEPARATELY from evidence gains.

Routes, strongest first (each records its source):
  A  PUBMED_DATABANK   the CURRENT PubMed record (efetch XML): DataBankList accession numbers and OtherID registry ids
  B  AACT_REFERENCE    AACT study_references: the PMID is the study's OWN publication (RESULT / DERIVED; never BACKGROUND)
  C  CTGOV_REFERENCE   CT.gov API v2: studies listing the PMID as a reference, kept only where the type is RESULT /
                       DERIVED, and only when exactly ONE study does
  E  FULLTEXT_REG      the trial's OWN held full text (phase 3) states the registration (registration-cue sentence rule)
  D  CANDIDATE         CT.gov search on the report's title words / acronym (+ sponsor when the abstract names one): a
                       unique hit is a CANDIDATE recorded for review, NEVER adopted (no source links the two)
For every NCT identified, the registry's own reference list gives the protocol / design paper and the companion (RESULT /
DERIVED) publications (source: the CT.gov record, response sha256).

    python scripts/g1_identify.py run [--slugs=a,b]  -> outputs/k_gap/registry_fill/IDENTIFICATION.json + .md
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
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "registry_fill")
EMAIL = "meta-harness@example.org"
_NCT = re.compile(r"NCT\d{8}")
_REG = re.compile(r"\b(?:NCT\d{8}|ISRCTN\d{8}|ACTRN\d{14}|DRKS\d{8}|ChiCTR[-A-Z0-9]{6,}|IRCT\d{6,}N?\d*|"
                  r"CTRI/\d{4}/\d{2,3}/\d{5,6}|UMIN\d{9}|JPRN-\w+|NTR\d{3,5}|PACTR\d{12,}|EudraCT\s*\d{4}-\d{6}-\d{2})\b", re.I)
OWN = ("RESULT", "DERIVED")
_STOP = {"the", "and", "with", "for", "from", "versus", "trial", "randomized", "randomised", "study", "patients", "effect",
         "effects", "controlled", "double", "blind", "placebo", "clinical", "comparison", "efficacy", "safety", "after",
         "among", "during", "between", "into", "their", "results", "treatment", "multicenter", "multicentre", "single"}


def scope(slugs=None):
    """Phase-1 funnel rows with a PMID and no NCT (the identity-less missing trials), active topics first."""
    import glob
    import g1_registry_fill as rf
    active = set(rf.active_slugs())
    rows = []
    for f in sorted(glob.glob(os.path.join(OUT, "*.funnel.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if slugs and d["slug"] not in slugs:
            continue
        for r in d["rows"]:
            if r.get("pmid") and not r.get("ncts") and r.get("stage") == "MISSING":
                rows.append(dict(r, slug=d["slug"], active=d["slug"] in active))
    return sorted(rows, key=lambda r: (not r["active"], r["slug"], r["label"]))


def pubmed_records(pmids):
    """{pmid: {title, abstract, registry_ids, xml_sha256}} from the current PubMed record."""
    from harness import http
    out = {}
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i + 100]
        x = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                          {"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "tool": "meta-harness", "email": EMAIL})
        time.sleep(0.4)
        for art in ET.fromstring(x).findall(".//PubmedArticle"):
            pmid = "".join(art.find(".//PMID").itertext()).strip()
            acc = ["".join(a.itertext()).strip() for a in art.findall(".//DataBankList/DataBank/AccessionNumberList/"
                                                                       "AccessionNumber")]
            oth = ["".join(o.itertext()).strip() for o in art.findall(".//OtherID")]
            te = art.find(".//ArticleTitle")          # an element with no children is FALSY: test `is None`
            title = "".join(te.itertext()).strip() if te is not None else ""
            ab = " ".join("".join(a.itertext()) for a in art.findall(".//Abstract/AbstractText"))
            ids = sorted({m.group(0).upper().replace(" ", "") for s in acc + oth for m in _REG.finditer(s)})
            fa = art.find(".//AuthorList/Author/LastName")
            out[pmid] = {"title": title, "abstract": ab, "registry_ids": ids, "databank": acc, "other_ids": oth,
                         "first_author": "".join(fa.itertext()).strip() if fa is not None else None,
                         "xml_sha256": hashlib.sha256(ET.tostring(art)).hexdigest()}
    return out


def ctgov(params):
    from harness import http
    st, b = http.get_raw("https://clinicaltrials.gov/api/v2/studies", params, tries=3, timeout=60)
    time.sleep(0.3)
    return (json.loads(b) if st == 200 else {}), hashlib.sha256(b or b"").hexdigest(), st


def references(study):
    return ((study.get("protocolSection") or {}).get("referencesModule") or {}).get("references") or []


def ctgov_by_reference(pmid):
    """Studies whose OWN publication (RESULT / DERIVED) is this PMID."""
    d, sha, st = ctgov({"query.term": f"AREA[ReferencePMID]{pmid}", "fields": "NCTId,BriefTitle,ReferencesModule",
                        "pageSize": "20"})
    own, bg = [], []
    for s in d.get("studies") or []:
        n = s["protocolSection"]["identificationModule"]["nctId"]
        types = {(r.get("type") or "").upper() for r in references(s) if str(r.get("pmid")) == str(pmid)}
        (own if types & set(OWN) else bg).append({"nct": n, "types": sorted(types)})
    return own, bg, sha, st


def title_words(title):
    return [w for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", title or "") if w.lower() not in _STOP][:8]


def acronym_of(label, title):
    for src in (label or "", title or ""):
        m = re.search(r"\b([A-Z][A-Z0-9-]{3,})\b", src)
        if m and not re.fullmatch(r"\d+", m.group(1)):
            return m.group(1)
    return None


def candidates(title, label):
    """CT.gov search on title words (and the acronym): unique hit -> CANDIDATE (recorded, never adopted)."""
    out = []
    words = title_words(title)
    if len(words) >= 3:
        d, sha, _st = ctgov({"query.term": " AND ".join(words[:5]), "fields": "NCTId,BriefTitle,OfficialTitle",
                             "pageSize": "5"})
        hits = [(s["protocolSection"]["identificationModule"]["nctId"],
                 s["protocolSection"]["identificationModule"].get("briefTitle")) for s in d.get("studies") or []]
        out.append({"route": "TITLE_WORDS", "query": " AND ".join(words[:5]), "hits": hits, "response_sha256": sha})
    acr = acronym_of(label, title)
    if acr:
        d, sha, _st = ctgov({"query.term": f"AREA[Acronym]{acr}", "fields": "NCTId,BriefTitle,Acronym", "pageSize": "5"})
        hits = [(s["protocolSection"]["identificationModule"]["nctId"],
                 s["protocolSection"]["identificationModule"].get("briefTitle")) for s in d.get("studies") or []]
        out.append({"route": "ACRONYM", "query": acr, "hits": hits, "response_sha256": sha})
    return out


def companions(nct):
    """Protocol / design paper and companion publications from the registry's own reference list."""
    d, sha, _st = ctgov({"query.term": f"AREA[NCTId]{nct}", "fields": "NCTId,ReferencesModule", "pageSize": "1"})
    refs = [r for s in d.get("studies") or [] for r in references(s)]
    proto = [r for r in refs if re.search(r"protocol|design|rationale|statistical analysis plan", r.get("citation") or "", re.I)]
    own = [r for r in refs if (r.get("type") or "").upper() in OWN]
    return {"source": f"CT.gov API v2 {nct} referencesModule (response sha256 {sha[:12]})",
            "protocol": [{"pmid": r.get("pmid"), "citation": (r.get("citation") or "")[:200]} for r in proto],
            "companion": [{"pmid": r.get("pmid"), "type": r.get("type"), "citation": (r.get("citation") or "")[:200]}
                          for r in own]}


def fulltext_registrations(slug, label):
    """Route E: the registration the trial's OWN held full text states (phase 3 held copy; the same sentence rule as
    g1_registry_fill.registration_ncts: a registration cue, no prior / other-trial cue). Returns (ids, source) or ([], None)."""
    import g1_registry_fill as rf
    p = os.path.join(OUT, "phase3", f"{slug}.json")
    if not os.path.exists(p):
        return [], None
    r = next((x for x in json.load(open(p, encoding="utf-8"))["rows"] if x["label"] == label), None)
    s = (r or {}).get("source") or {}
    if not r or r.get("stage") not in ("TEXT", "TYPED", "MODEL"):
        return [], None
    if s.get("origin") == "PMC":
        import k_gap_counterfactual as cfm
        t = cfm.pmc_fulltext_cached(r["pmid"]) or ""
    else:
        from kgap import k_gap
        t = k_gap.unpaywall_text(s["doi"], os.path.join(ROOT, "outputs", "k_gap", "_upw"),
                                 os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json"))["text"] or ""
    ids = set()
    for sent in re.split(r"(?<=[.;])\s+", t):
        found = [m.group(0).upper().replace(" ", "") for m in _REG.finditer(sent)]
        if found and rf._REG_CUE.search(sent) and not rf._PRIOR_CUE.search(sent):
            ids.update(found)
    src = (f"held full text ({s.get('origin')} {s.get('pmcid') or s.get('doi')}; text sha256 "
           f"{hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]})") if ids else None
    return sorted(ids), src


def identify(rows):
    from kgap import aact_adapter, identity_chain as ic
    pm = pubmed_records(sorted({r["pmid"] for r in rows}))
    aact = ic.pmid_to_ncts([r["pmid"] for r in rows], aact_adapter.snapshot_dir())
    out = []
    for r in rows:
        p = pm.get(r["pmid"]) or {}
        res = {"slug": r["slug"], "label": r["label"], "pmid": r["pmid"], "active_topic": r["active"],
               "before": r.get("why"), "routes": {}, "identified": [], "identified_by": None}
        res["routes"]["A_PUBMED_DATABANK"] = {"registry_ids": p.get("registry_ids") or [], "databank": p.get("databank"),
                                              "other_ids": p.get("other_ids"), "xml_sha256": p.get("xml_sha256")}
        res["routes"]["B_AACT_REFERENCE"] = aact.get(r["pmid"]) or {}
        own, bg, sha, st = ctgov_by_reference(r["pmid"])
        res["routes"]["C_CTGOV_REFERENCE"] = {"own": own, "background_only": bg, "response_sha256": sha, "http": st}
        for route, ids in (("A_PUBMED_DATABANK", p.get("registry_ids") or []),
                           # ONE own-publication link only: a PMID that is the RESULT of two studies is ambiguous
                           ("B_AACT_REFERENCE", sorted(aact.get(r["pmid"]) or {}) if len(aact.get(r["pmid"]) or {}) == 1 else []),
                           ("C_CTGOV_REFERENCE", [o["nct"] for o in own] if len(own) == 1 else [])):
            if ids:
                res["identified"], res["identified_by"] = ids, route
                break
        if not res["identified"]:
            ids, src = fulltext_registrations(r["slug"], r["label"])
            res["routes"]["E_FULLTEXT_REGISTRATION"] = {"ids": ids, "source": src}
            if ids:
                res["identified"], res["identified_by"] = ids, "E_FULLTEXT_REGISTRATION"
        if not res["identified"] and (len(own) > 1 or len(aact.get(r["pmid"]) or {}) > 1):
            res["ambiguous"] = ("MULTIPLE_OWN_REGISTRATIONS: AACT " + ",".join(sorted(aact.get(r["pmid"]) or {})) +
                                "; CT.gov " + ",".join(o["nct"] for o in own))
        if not res["identified"]:
            res["candidates"] = candidates(p.get("title"), r["label"])
        ncts = [i for i in res["identified"] if i.startswith("NCT")]
        if ncts:
            res["publications"] = {n: companions(n) for n in ncts}
        res["title"] = p.get("title")
        out.append(res)
        print(("ACTIVE " if r["active"] else "       ") + r["slug"][:26], "|", r["label"][:30], "|",
              res["identified_by"] or ("AMBIGUOUS" if res.get("ambiguous") else "NOT_IDENTIFIED"), res["identified"], flush=True)
    return out


def companion_scope(slugs=None):
    """The REGISTERED missing trials (an NCT) not admitted: their companion / primary-outcome publications."""
    import glob
    import g1_registry_fill as rf
    active = set(rf.active_slugs())
    rows = []
    for f in sorted(glob.glob(os.path.join(OUT, "*.funnel.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if slugs and d["slug"] not in slugs:
            continue
        rows += [dict(r, slug=d["slug"], active=d["slug"] in active) for r in d["rows"] if r.get("ncts")
                 and r.get("stage") != "MISSING"]
    return sorted(rows, key=lambda r: (not r["active"], r["slug"], r["label"]))


def run_companions(argv):
    """Every OWN publication (RESULT / DERIVED) the registry lists for the trial, other than its report PMID: from AACT
    study_references (snapshot) and the live CT.gov reference list. Each is a further source for phase 3."""
    from kgap import aact_adapter, identity_chain as ic
    sl = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--slugs=")), None)
    rows = companion_scope(sl)
    snap = ic.result_pmids(sorted({n for r in rows for n in r["ncts"]}), aact_adapter.snapshot_dir())
    out = []
    for r in rows:
        live = {n: companions(n) for n in r["ncts"]}
        pm = {}
        for n in r["ncts"]:
            for p in snap.get(n) or []:
                pm.setdefault(p, set()).add(f"AACT study_references {n} (RESULT/DERIVED)")
            for c in live[n]["companion"]:
                if c.get("pmid"):
                    pm.setdefault(str(c["pmid"]), set()).add(f"CT.gov {n} reference type {c.get('type')}")
        comp = sorted(p for p in pm if p != str(r.get("pmid") or ""))
        out.append({"slug": r["slug"], "label": r["label"], "report_pmid": r.get("pmid"), "ncts": r["ncts"],
                    "active_topic": r["active"], "stage_phase1": r.get("stage"),
                    "companions": [{"pmid": p, "sources": sorted(pm[p])} for p in comp],
                    "protocol": [x for n in r["ncts"] for x in live[n]["protocol"]],
                    "registry_sources": {n: live[n]["source"] for n in r["ncts"]}})
        print(("ACTIVE " if r["active"] else "       ") + r["slug"][:26], "|", r["label"][:30], "| companions",
              len(comp), "| protocol", len(out[-1]["protocol"]), flush=True)
    doc = {"written": datetime.date.today().isoformat(), "writer": "scripts/g1_identify.py companions", "n": len(out),
           "with_companions": sum(bool(x["companions"]) for x in out),
           "companion_pmids": sum(len(x["companions"]) for x in out), "rows": out}
    json.dump(doc, open(os.path.join(OUT, "IDENTIFICATION_COMPANIONS.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print("COMPANIONS", doc["n"], "trials;", doc["with_companions"], "with companions;", doc["companion_pmids"], "PMIDs")


def rerun_phases(x):
    """Phases 1-2 again for a trial that GAINED an NCT (phase 3 is by PMID and already ran): AACT posted results ->
    binding -> stage 4 (deterministic arm pick, else codex + agy + adjudicator); then each regulator's naming + typed read."""
    import g1_registry_fill as rf
    import g1_tracker as gt
    import g1_trial_acquire as ta
    import g1_regulator_fill as rg
    slug, ncts = x["slug"], [i for i in x["identified"] if i.startswith("NCT")]
    cfg = rf.config(slug)
    po = cfg.get("primary_outcome") or {}
    comp = ta.comparator_pmid(slug, ta.tracker_file(slug, None))
    ev = ta.aact_evidence(ncts)
    ctg = {n: rf.ctgov_has_results(n) for n in ncts}
    out = {"ncts": ncts, "aact": {n: e.get("state") for n, e in ev.items()}, "ctgov": ctg}
    posted = [n for n, e in ev.items() if e.get("state") == "POSTED"]
    if not posted:
        out["phase1"] = rf.results_why(out["aact"], ctg)
    else:
        bindable = []
        for n in posted:
            reg = ev[n]["_reg"]
            for oid, o in reg["outcomes"].items():
                an = next((a for a in reg["analyses"] if a.get("outcome_id") == oid), None)
                groups = reg["groups"].get(oid) or []
                bv = gt.binding_verdict(po.get("name") or "", list(po.get("keywords") or []), o.get("title"),
                                        len({g["group"] for g in groups}),
                                        is_primary=(o.get("type") or "").upper() == "PRIMARY", analysis=an,
                                        estimand=po.get("estimand"), population=po.get("population"))
                if bv["verdict"] == "BINDABLE":
                    bindable.append({"nct": n, "outcome_id": oid, "title": o.get("title"), "time_frame": o.get("time_frame")})
        if not bindable:
            out["phase1"] = "NO_POSTED_OUTCOME_BINDS_TO_THE_PROTOCOL_OUTCOME"
        else:
            frow = {"label": x["label"], "pmid": x["pmid"], "ncts": ncts, "bindable_outcomes": bindable, "ctgov": ctg}
            r = rf.run_trial(slug, cfg, comp, frow)
            out["phase1"] = r["decision"]
            out["phase1_row"] = {k: r.get(k) for k in ("decision", "verdict", "admitted", "deterministic_pairs")}
    t = {"label": x["label"], "pmid": x["pmid"], "ncts": ncts, "slug": slug}
    out["phase2"] = {}
    for ag in ("FDA", "EMA", "NICE", "GBA"):
        try:
            rr = rg.run_trial(slug, ag, cfg, comp, t)
            out["phase2"][ag] = rr["decision"]
        except Exception as exc:  # noqa: BLE001 - typed
            out["phase2"][ag] = f"ERROR:{type(exc).__name__}"
    return out


def main(argv):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sl = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--slugs=")), None)
    rows = scope(sl)
    res = identify(rows)
    n = len(res)
    by = {}
    for x in res:
        by[x["identified_by"] or "NOT_IDENTIFIED"] = by.get(x["identified_by"] or "NOT_IDENTIFIED", 0) + 1
    for x in res:
        # NEW = an id the phase-1 funnel did not already hold (Young / Tong were already REGISTERED_OUTSIDE_CTGOV)
        x["newly_identified"] = bool(x["identified"]) and not any(i in str(x.get("before") or "") for i in x["identified"])
    nct_gain = [x for x in res if x["newly_identified"] and any(i.startswith("NCT") for i in x["identified"])]
    for x in nct_gain:
        x["rerun"] = rerun_phases(x)
        print("RERUN", x["slug"], x["label"], json.dumps(x["rerun"], default=str)[:400], flush=True)
    doc = {"written": datetime.date.today().isoformat(), "writer": "scripts/g1_identify.py", "n": n, "by_route": by,
           "newly_identified": sum(x["newly_identified"] for x in res),
           "gained_nct": len(nct_gain), "gained_any_registry_id": sum(bool(x["identified"]) for x in res),
           "active_topic_rows": sum(x["active_topic"] for x in res), "rows": res}
    json.dump(doc, open(os.path.join(OUT, "IDENTIFICATION.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    print("IDENTIFICATION", n, by, "gained NCT", len(nct_gain))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("run", "companions"):
        raise SystemExit("usage: run|companions [--slugs=a,b]")
    if a[0] == "companions":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        run_companions(a[1:])
    else:
        main(a[1:])
