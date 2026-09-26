"""Report for the registry-first pass (STRATEGY.md Part 2): each CVOT candidate, the near misses (4 of 5 criteria),
and, for each reference trial, whether the text searches alone and the registry pass alone would have found it.
usage: registry_report.py <run dir> <held raw studies .json.gz>   (writes REGISTRY_PASS_REPORT.json)"""
import gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from performance import REFERENCE, SENSITIVITY  # noqa: E402  (the one definition of the reference set)

# the registered P criterion reads the whole eligibility text, so it cannot tell inclusion from exclusion; this
# reports, per candidate, which side the type 2 diabetes mention sits on (a disclosed reading, not a re-filter)
T2D = re.compile(r"type\s*2\s*diabet|\bT2DM?\b", re.I)


def t2d_side(raw_by_nct, nct):
    el = (((raw_by_nct.get(nct) or {}).get("protocolSection") or {}).get("eligibilityModule") or {}).get("eligibilityCriteria") or ""
    inc, _, exc = el.partition("Exclusion")
    cond = " ".join((((raw_by_nct.get(nct) or {}).get("protocolSection") or {}).get("conditionsModule") or {}).get("conditions") or [])
    return {"in_conditions": bool(T2D.search(cond) or re.search(r"diabetes mellitus,?\s*type\s*2", cond, re.I)),
            "in_inclusion": bool(T2D.search(inc)), "in_exclusion": bool(T2D.search(exc))}


def main(run, raw_path):
    rows = json.load(gzip.open(os.path.join(run, "records_registry_pass.json.gz"), "rt", encoding="utf-8"))
    raw = {s["protocolSection"]["identificationModule"]["nctId"]: s
           for s in json.load(gzip.open(raw_path, "rt", encoding="utf-8"))}
    perf = json.load(open(os.path.join(run, "PERFORMANCE.json"), encoding="utf-8"))
    trials = json.load(open(os.path.join(run, "TRIALS.json"), encoding="utf-8"))["trials"]
    p1_ncts = {n for t in trials for n in t["ncts"]}
    p1_ctgov = {r["id"] for r in json.load(gzip.open(os.path.join(run, "records_ctgov.json.gz"), "rt", encoding="utf-8"))}
    ref = {nct: name for name, _, nct in REFERENCE}
    sens = {nct: name for name, _, nct in SENSITIVITY}
    by = {r["nct"]: r for r in rows}

    def brief(r):
        c = r["criteria"]
        return {"nct": r["nct"], "acronym": r["acronym"], "title": r["title"], "status": r["status"],
                "has_results": r["has_results"], "enrollment": r["enrollment"], "masking": r["masking"],
                "start": r["start"], "completion": r["completion"], "interventions": r["interventions"],
                "primary_outcomes": [p[:300] for p in r["primary_outcomes"]],
                "criteria": c, "missing": [k for k, v in c.items() if k != "cvot_candidate" and not v],
                "t2d_mention": t2d_side(raw, r["nct"]),
                "in_part1": ("part1 registry search" if r["nct"] in p1_ctgov else
                             "part1 via a publication" if r["nct"] in p1_ncts else "not in part1"),
                "reference": ref.get(r["nct"]) or sens.get(r["nct"])}

    cands = [brief(r) for r in rows if r["criteria"]["cvot_candidate"]]
    near = [brief(r) for r in rows if not r["criteria"]["cvot_candidate"] and len(brief(r)["missing"]) == 1]
    per_ref = []
    for p in perf["reference"] + perf["sensitivity"]:
        r = by.get(p["nct"])
        per_ref.append({"trial": p["trial"], "nct": p["nct"], "pmid": p["pmid"],
                        "text_search_alone": {"pubmed": p["found"]["pubmed"],
                                              "europepmc_non_medline": p["found"]["europepmc_non_medline"]},
                        "part1_registry_search": p["found"]["ctgov"],
                        "registry_pass_retrieved": r is not None,
                        "registry_pass_cvot_candidate": bool(r and r["criteria"]["cvot_candidate"]),
                        "registry_pass_missing": (brief(r)["missing"] if r else None)})
    out = {"n_retrieved": len(rows), "n_cvot_candidates": len(cands),
           "reference_missed_by_text_search": [x["trial"] for x in per_ref
                                               if not (x["text_search_alone"]["pubmed"] or x["text_search_alone"]["europepmc_non_medline"])],
           "reference_retrieved_by_registry_pass": f"{sum(x['registry_pass_retrieved'] for x in per_ref[:len(REFERENCE)])} of {len(REFERENCE)}",
           "reference_passing_registry_filter": f"{sum(x['registry_pass_cvot_candidate'] for x in per_ref[:len(REFERENCE)])} of {len(REFERENCE)}",
           "per_reference": per_ref, "cvot_candidates": cands, "near_misses": near,
           # the question asked of this pass: finished trials with a cardiovascular PRIMARY outcome and nothing posted,
           # whatever the other four criteria say (so a filter miss cannot hide one)
           "finished_cv_primary_without_results": [brief(r) for r in rows if r["status"] in ("COMPLETED", "TERMINATED")
                                                   and not r["has_results"] and r["criteria"]["O_primary_cv"]]}
    json.dump(out, open(os.path.join(run, "REGISTRY_PASS_REPORT.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print(out["reference_retrieved_by_registry_pass"], "retrieved;", out["reference_passing_registry_filter"],
          "pass filter; text search missed:", out["reference_missed_by_text_search"])
    for c in cands:
        print(c["nct"], c["acronym"] or "-", c["status"], "results" if c["has_results"] else "no results",
              c["in_part1"], c["reference"] or "", c["t2d_mention"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
