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
from harness import k_gap  # noqa: E402

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
    terms = list(ag.keys()) + [s for v in ag.values() for s in (v or [])]
    if not terms:
        terms = list(topic.get("intervention_terms") or [])
    return sorted({t for t in terms if t and len(t) >= 3}, key=str.lower)


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
    rec_ids, rec_acr = set(), set()
    rp = os.path.join(ROOT, "cache", slug, "records.json")
    if os.path.exists(rp):
        rj = _j(rp)
        for r in rj.get("records", []):
            rec_ids.add(_num(r.get("id")))
            if r.get("nct"):
                rec_ids.add(_num(r["nct"]))
        for r in rj.get("ctgov", []) or []:
            rec_ids.add(_num(r.get("id")))
            if r.get("acronym"):
                rec_acr.add(k_gap.norm_acronym(r["acronym"]))
    return {"k": (prim.get("result") or {}).get("k"), "pooled": pooled, "pooled_fam": pooled_fam,
            "absent": absent, "families": fams, "rec_ids": rec_ids, "rec_acr": rec_acr,
            "estimand": (prim.get("estimand") or ""), "outcome": prim.get("name")}


def comparator_units(slug, pmid, agents):
    p = os.path.join(ROOT, "cache", "comparators", pmid, f"{DATE}_kgap_jats.xml")
    if not os.path.exists(p):
        return {"state": "NO_OPEN_JATS", "units": [], "tables_used": []}, None
    with open(p, "rb") as fh:
        body = fh.read()
    parsed = k_gap.parse_jats(body)
    inc = k_gap.included_trials(parsed, agents)
    inc["jats_file"] = os.path.relpath(p, ROOT).replace(os.sep, "/")
    inc["jats_sha256"] = k_gap.sha256(body)
    return inc, parsed


def resolve_unit(u, parsed, idx, agents_re):
    """Identity: cited ref PMID > NCT written in the unit > Author-Year against the comparator's own
    ref-list > acronym against AACT studies.acronym restricted to NCTs whose interventions name a topic
    agent. Each step records its basis; an acronym hitting >1 agent NCT is AMBIGUOUS, not guessed."""
    pmids = {c["pmid"] for c in u["cited"] if c.get("pmid")}
    ncts = set(u["ncts"])
    basis = []
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
    for p in list(pmids):
        for n, _t in idx["pmid_nct"].get(p, []):
            ncts.add(n)
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
    for n in list(ncts):
        for p, lst in idx["pmid_nct"].items():
            if any(x == n and t in ("RESULT", "DERIVED") for x, t in lst):
                pmids.add(p)
    return {"pmids": sorted(pmids), "ncts": sorted(ncts), "basis": basis}


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


def closable_by(cls, aact_src, oa):
    if cls in ("POOLED", "MEASURE_MISMATCH", "UNRESOLVED_IDENTITY"):
        return ""
    if aact_src["n_matches"] > 0:
        return "AACT_RESULTS"
    if oa:
        return "PMC_OA_FULLTEXT"
    return "NONE_OPEN_PROBED"


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


def main(argv=None):
    argv = argv or sys.argv[1:]
    offline = "--offline" in argv
    os.makedirs(OUT, exist_ok=True)
    topics = []
    for f in sorted(glob.glob(os.path.join(ROOT, "cache", "*", "comparators.json"))):
        slug = os.path.basename(os.path.dirname(f))
        c = _j(f)[0]
        m = re.search(r"PMID (\d+)", c.get("citation", ""))
        topics.append((slug, m.group(1) if m else str(c["id"]), c.get("citation", "")))
    per, all_p, all_n, all_a, all_agents = {}, set(), set(), set(), set()
    for slug, cpmid, cit in topics:
        topic = _j(os.path.join(ROOT, "topics", slug + ".json"))
        agents = topic_agents(topic)
        inc, parsed = comparator_units(slug, cpmid, agents)
        o = ours(slug)
        per[slug] = {"topic": topic, "agents": agents, "inc": inc, "parsed": parsed, "ours": o,
                     "comparator_pmid": cpmid, "citation": cit}
        all_agents |= set(agents)
        for u in inc["units"]:
            all_p |= {c["pmid"] for c in u["cited"] if c.get("pmid")}
            all_n |= set(u["ncts"])
            all_a |= set(u["acronyms"])
        all_p |= {x for x in o["pooled"] if x.isdigit()} | {x for x in o["absent"] if x.isdigit()}
        all_n |= {x for x in o["pooled_fam"] | set(o["absent"]) if x.startswith("NCT")}
        if parsed:
            all_p |= {r["pmid"] for r in parsed["refs"].values() if r.get("pmid")}
    print(f"AACT index: {len(all_p)} pmids, {len(all_n)} ncts, {len(all_a)} acronyms", flush=True)
    idx = k_gap.aact_index(all_p, all_n, all_a, sorted(all_agents))
    rows = []
    for slug, cpmid, cit in topics:
        P = per[slug]
        agents_re = re.compile("|".join(re.escape(a) for a in P["agents"]), re.I)
        # per-topic agent flag: recompute over this topic's agents only
        tidx = dict(idx)
        tidx["agent_nct"] = {n: any(agents_re.search(x) for x in v) for n, v in idx["interventions"].items()}
        for u in P["inc"]["units"]:
            ident = resolve_unit(u, P["parsed"], tidx, agents_re)
            reg = registry_agent(ident["ncts"], tidx)
            if u["drug_match"] == "OTHER_AGENT" or (u["drug_match"] == "AGENT_IMPLICIT" and reg is False):
                drug = "OTHER_AGENT"
            elif u["drug_match"] == "DRUG_MATCH" or reg:
                drug = "DRUG_MATCH"
            else:
                drug = "AGENT_UNCONFIRMED"
            if not ident["pmids"] and not ident["ncts"]:
                status, fam, absent = "UNRESOLVED", None, None
            else:
                status, fam, absent = match_ours(ident, u["acronyms"], P["ours"])
            src = aact_source(ident["ncts"], tidx, outcome_keywords(P["topic"]), P["ours"]["estimand"])
            rows.append({"slug": slug, "comparator_pmid": cpmid, "table": u["table"], "layout": u["layout"],
                         "label": u["label"], "context": u["context"][:300], "drug": drug,
                         "pmids": ident["pmids"], "ncts": ident["ncts"], "identity_basis": ident["basis"],
                         "cited_doi": [c.get("doi") for c in u["cited"] if c.get("doi")],
                         "status": status, "family_id": fam["family_id"] if fam else "",
                         "family_eligibility": fam["eligibility"] if fam else "",
                         "declared_absent": absent, "aact": src, "study": {n: tidx["study"].get(n) for n in ident["ncts"]}})
    oa = oa_probe([p for r in rows for p in r["pmids"] if r["status"] not in ("POOLED",)], offline)
    for r in rows:
        oas = [oa.get(p, {}) for p in r["pmids"]]
        r["pmc_oa"] = [{"pmid": p, **oa.get(p, {})} for p in r["pmids"] if oa.get(p, {}).get("pmcid")]
        is_oa = any(v.get("is_oa") for v in oas)
        r["gap_class"] = classify(r["status"], r["declared_absent"], None, r["aact"], is_oa)
        r["closable_by"] = closable_by(r["gap_class"], r["aact"], is_oa)
    # ---- per-topic rollup
    topics_out = []
    for slug, cpmid, cit in topics:
        P = per[slug]
        tr = [r for r in rows if r["slug"] == slug]
        elig = [r for r in tr if r["drug"] != "OTHER_AGENT" and r["status"] != "UNRESOLVED"]
        topics_out.append({
            "slug": slug, "comparator_pmid": cpmid, "comparator": cit[:160],
            "comparator_table_state": P["inc"]["state"], "tables_used": P["inc"]["tables_used"],
            "our_k": P["ours"]["k"], "comparator_units": len(tr),
            "drug_specific_resolved": len(elig),
            "other_agent": sum(r["drug"] == "OTHER_AGENT" for r in tr),
            "unresolved_labels": sum(r["status"] == "UNRESOLVED" for r in tr),
            "pooled_of_theirs": sum(r["gap_class"] == "POOLED" for r in elig),
            "missing": sum(r["gap_class"] != "POOLED" for r in elig),
            "by_class": dict(Counter(r["gap_class"] for r in elig if r["gap_class"] != "POOLED")),
            "by_source": dict(Counter(r["closable_by"] for r in elig if r["closable_by"])),
        })
    out = {"generated": DATE, "aact_snapshot": idx["snapshot"], "topics": topics_out, "trials": rows}
    with open(os.path.join(OUT, "k_gap_table.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, default=list)
    cols = ["slug", "comparator_pmid", "label", "drug", "status", "gap_class", "closable_by", "pmids", "ncts",
            "identity_basis", "family_id", "family_eligibility", "declared_reason_code", "aact_results_posted",
            "aact_outcome_match", "aact_param_type", "aact_time_frame", "aact_population", "pmc_oa", "table"]
    with open(os.path.join(OUT, "k_gap_table.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            m = r["aact"]["outcome_matches"][0] if r["aact"]["outcome_matches"] else {}
            w.writerow([r["slug"], r["comparator_pmid"], r["label"], r["drug"], r["status"], r["gap_class"],
                        r["closable_by"], ";".join(r["pmids"]), ";".join(r["ncts"]), ";".join(r["identity_basis"]),
                        r["family_id"], r["family_eligibility"],
                        (r["declared_absent"] or {}).get("reason_code", ""), r["aact"]["results_posted"],
                        m.get("title", ""), m.get("param_type", ""), m.get("time_frame", ""), m.get("population", "")[:160],
                        ";".join(x["pmcid"] for x in r["pmc_oa"] if x.get("is_oa")), r["table"]])
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    o = main()
    for t in o["topics"]:
        print(f"{t['slug'][:38]:38s} state={t['comparator_table_state'][:12]:12s} ourk={t['our_k']} units={t['comparator_units']:3d} "
              f"elig={t['drug_specific_resolved']:3d} pooled={t['pooled_of_theirs']:2d} miss={t['missing']:2d} "
              f"other={t['other_agent']:2d} unres={t['unresolved_labels']:2d} {t['by_class']} {t['by_source']}")
