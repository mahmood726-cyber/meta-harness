"""Registry-first pass (STRATEGY.md, Part 2). Registered by the commit that adds it; run AFTER that commit.
Finds GLP-1 RA cardiovascular outcome trials in ClinicalTrials.gov by what the REGISTRATION says -- whatever the
trial's status and whether or not it has published or posted anything -- so a trial that has no paper (like ASCEND
PLUS) is found by design rather than by accident. Every study retrieved is retained; the CVOT filter below is
deterministic and every criterion is recorded per study.
usage: registry_pass.py <held_dir> <run_dir>"""
import gzip, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search  # noqa: E402  (the registered search module: DRUGS, the logged fetcher)

# no condition restriction and no status restriction: the registration's own fields decide
REG_PARAMS = {
    "query.intr": " OR ".join(['"GLP-1"', '"glucagon-like peptide-1"', '"GLP-1 receptor agonist"'] + search.DRUGS),
    "query.outc": ('MACE OR "major adverse cardiovascular" OR "major adverse cardiac" OR "cardiovascular death" OR '
                   '"cardiovascular outcome" OR "myocardial infarction" OR stroke'),
    "query.term": "AREA[StudyType]INTERVENTIONAL",
}

T2D = re.compile(r"type\s*2\s*diabet|type\s*ii\s*diabet|\bT2DM?\b|diabetes mellitus,?\s*type\s*2|non-insulin-dependent", re.I)
GLP1 = re.compile(r"GLP-?1|glucagon[- ]like peptide[- ]1|" + "|".join(search.DRUGS), re.I)
PLACEBO = re.compile(r"placebo", re.I)
MACE = re.compile(r"\bMACE\b|major adverse cardi|cardiovascular death|death from cardiovascular|cardiovascular mortality", re.I)
MI = re.compile(r"myocardial infarction", re.I)
STROKE = re.compile(r"stroke", re.I)


def fields(s):
    ps = s.get("protocolSection") or {}
    idm, sm = ps.get("identificationModule") or {}, ps.get("statusModule") or {}
    dm, om = ps.get("designModule") or {}, ps.get("outcomesModule") or {}
    arms = ps.get("armsInterventionsModule") or {}
    em = ps.get("eligibilityModule") or {}
    prim = [(o.get("measure") or "") + " | " + (o.get("description") or "") for o in om.get("primaryOutcomes") or []]
    return {
        "nct": idm.get("nctId"), "acronym": idm.get("acronym", ""), "title": idm.get("briefTitle", ""),
        "official_title": idm.get("officialTitle", ""), "status": sm.get("overallStatus"),
        "why_stopped": sm.get("whyStopped", ""), "has_results": bool(s.get("hasResults")),
        "start": (sm.get("startDateStruct") or {}).get("date", ""),
        "completion": (sm.get("completionDateStruct") or {}).get("date", ""),
        "enrollment": (dm.get("enrollmentInfo") or {}).get("count"),
        "phases": dm.get("phases") or [], "allocation": (dm.get("designInfo") or {}).get("allocation", ""),
        "masking": ((dm.get("designInfo") or {}).get("maskingInfo") or {}).get("masking", ""),
        "conditions": (ps.get("conditionsModule") or {}).get("conditions") or [],
        "interventions": [f"{i.get('type', '')}: {i.get('name', '')}" for i in arms.get("interventions") or []],
        "arm_labels": [f"{a.get('type', '')}: {a.get('label', '')}" for a in arms.get("armGroups") or []],
        "primary_outcomes": prim,
        "eligibility_excerpt": (em.get("eligibilityCriteria") or "")[:1500],
        "reference_pmids": sorted({str(r["pmid"]) for r in (ps.get("referencesModule") or {}).get("references") or []
                                   if r.get("pmid")}),
    }


def criteria(f):
    p_text = " ".join(f["conditions"] + [f["title"], f["official_title"], f["eligibility_excerpt"]])
    prim = " ".join(f["primary_outcomes"])
    c = {
        "P_t2d": bool(T2D.search(p_text)),
        "I_glp1": any(GLP1.search(x) for x in f["interventions"] + f["arm_labels"]),
        "C_placebo": any(PLACEBO.search(x) for x in f["interventions"] + f["arm_labels"]),
        "randomised": f["allocation"] == "RANDOMIZED",
        "O_primary_cv": bool(MACE.search(prim) or (MI.search(prim) and STROKE.search(prim))),
    }
    c["cvot_candidate"] = all(c.values())
    return c


def main(held, run):
    os.makedirs(held, exist_ok=True)
    raw, token, total = [], None, None
    while True:
        params = dict(REG_PARAMS, pageSize=1000, countTotal="true", **({"pageToken": token} if token else {}))
        d = json.loads(search.fetch(search.CTGOV, params, held, f"regpass_{len(raw)}"))
        total = d.get("totalCount", total)
        raw += d["studies"]
        token = d.get("nextPageToken")
        if not token:
            break
        time.sleep(0.4)
    assert total is None or len(raw) == total, f"CT.gov paging: {len(raw)} of {total}"
    with gzip.open(os.path.join(held, "regpass_raw_studies.json.gz"), "wt", encoding="utf-8") as f:
        json.dump(raw, f)
    rows = []
    for s in raw:
        f = fields(s)
        rows.append(dict(f, criteria=criteria(f)))
    rows.sort(key=lambda r: r["nct"])
    with gzip.open(os.path.join(run, "records_registry_pass.json.gz"), "wt", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    json.dump({"params": REG_PARAMS, "count": total, "retrieved": len(rows),
               "cvot_candidates": [r["nct"] for r in rows if r["criteria"]["cvot_candidate"]]},
              open(os.path.join(run, "REGISTRY_PASS_SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    json.dump(search.LOG, open(os.path.join(run, "REQUEST_LOG_registry_pass.json"), "w", encoding="utf-8", newline="\n"),
              indent=0)
    print(total, "studies;", sum(r["criteria"]["cvot_candidate"] for r in rows), "CVOT candidates")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
