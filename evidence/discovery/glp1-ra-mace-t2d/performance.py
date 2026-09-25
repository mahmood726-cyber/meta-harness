"""Discovery performance against the reference set (STRATEGY.md, performance report). Run only AFTER the screening
and AI-proposal commits. The reference set is read from the repository here and nowhere earlier.
usage: performance.py <run dir>   (writes PERFORMANCE.json)"""
import gzip, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# the served review's CONVENTIONAL_GLP1RA primary pool: the eligible trials of cache/glp1-ra-mace-t2d/records.json
# (SELECT and the eight-CVOT meta-analysis are that file's own non-eligible entries) plus FLOW, admitted by
# evidence/glp1_adjudication/FLOW.json. FREEDOM-CVO is eligible only for the any-delivery strand; reported separately.
REFERENCE = [("ELIXA", "26630143", "NCT01147250"), ("LEADER", "27295427", "NCT01179048"),
             ("SUSTAIN-6", "27633186", "NCT01720446"), ("EXSCEL", "28910237", "NCT01144338"),
             ("Harmony Outcomes", "30291013", "NCT02465515"), ("REWIND", "31189511", "NCT01394952"),
             ("PIONEER 6", "31185157", "NCT02692716"), ("AMPLITUDE-O", "34215025", "NCT03496298"),
             ("FLOW", "38785209", "NCT03819153"), ("SOUL", "40162642", "NCT03914326")]
SENSITIVITY = [("FREEDOM-CVO (ITCA 650; any-delivery strand only)", "34873344", "NCT01455896")]
REF_SOURCES = ["cache/glp1-ra-mace-t2d/records.json", "cache/glp1-ra-mace-t2d/verified_effects.json",
               "evidence/glp1_adjudication/FLOW.json", "evidence/glp1_adjudication/FREEDOM-CVO.json"]


def main(run):
    L = lambda n: json.load(gzip.open(os.path.join(run, f"records_{n}.json.gz"), "rt", encoding="utf-8"))
    pm, ct, ep = L("pubmed"), L("ctgov"), L("europepmc")
    in_pm = {r["id"] for r in pm}
    in_ct = {r["id"] for r in ct}
    in_ep = {r.get("pmid") for r in ep if r.get("pmid")}
    tr = json.load(open(os.path.join(run, "TRIALS.json"), encoding="utf-8"))["trials"]
    ai = {p["key"]: p for p in json.load(open(os.path.join(run, "AI_PROPOSALS.json"), encoding="utf-8"))["proposals"]}
    where = {m: t for t in tr for m in t["members"]}

    def one(name, pmid, nct):
        tp, tn = where.get(f"PMID:{pmid}"), where.get(f"NCT:{nct}")
        trials = sorted({t["trial"] for t in (tp, tn) if t})
        recs = [x for t in (tp, tn) if t for x in t["records"]]
        recs = list({x["key"]: x for x in recs}.values())
        return {"trial": name, "pmid": pmid, "nct": nct,
                "found": {"pubmed": pmid in in_pm, "ctgov": nct in in_ct, "europepmc_non_medline": pmid in in_ep},
                "found_any": bool(tp or tn),
                "dedup": ("one trial" if len(trials) == 1 and tp and tn else
                          "split across trials " + ",".join(trials) if len(trials) > 1 else
                          "publication only" if tp else "registration only" if tn else "not found"),
                "discovery_trials": trials,
                "trial_decision": ("include" if any(t["decision"] == "include" for t in (tp, tn) if t) else
                                   "exclude" if trials else None),
                "records": [{"key": x["key"], "decision": (x["screen"] or {}).get("decision"),
                             "rule_id": (x["screen"] or {}).get("rule_id"), "reason": (x["screen"] or {}).get("reason"),
                             "ai": ({k: ai[x["key"]][k] for k in ("proposal", "reason", "design_rct", "reports_mace")}
                                    if x["key"] in ai else None)} for x in recs]}

    ref = [one(*r) for r in REFERENCE]
    sens = [one(*r) for r in SENSITIVITY]
    ref_trials = {t for r in ref + sens for t in r["discovery_trials"]}
    others = []
    for t in tr:
        if t["decision"] == "include" and t["trial"] not in ref_trials:
            inc = [x for x in t["records"] if (x["screen"] or {}).get("decision") == "include"]
            others.append({"trial": t["trial"], "members": t["members"], "title": next((x.get("title") for x in inc), None),
                           "rule_id": sorted({x["screen"]["rule_id"] or "include" for x in inc}),
                           "ai_proposals": {x["key"]: ai[x["key"]]["proposal"] for x in t["records"] if x["key"] in ai},
                           "ai_reports_mace": sorted({ai[x["key"]]["reports_mace"] for x in t["records"] if x["key"] in ai})})
    scr = json.load(open(os.path.join(run, "SCREEN.json"), encoding="utf-8"))
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {"reference_read_at_commit": head, "reference_sources": REF_SOURCES,
           "recall_found": f"{sum(r['found_any'] for r in ref)} of {len(ref)}",
           "recall_included_by_deterministic_screen": f"{sum(r['trial_decision'] == 'include' for r in ref)} of {len(ref)}",
           "reference": ref, "sensitivity": sens,
           "other_included_trials": {"n": len(others),
                                     "n_with_any_ai_reports_mace_yes": sum("yes" in o["ai_reports_mace"] for o in others),
                                     "trials": others},
           "screened_out_records_by_rule": {k: v for k, v in scr["rule_counts"].items() if k != "include"},
           "n_trials": len(tr), "n_included_trials": sum(t["decision"] == "include" for t in tr)}
    json.dump(out, open(os.path.join(run, "PERFORMANCE.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    for r in ref + sens:
        print(f"{r['trial'][:22]:22} found={r['found']} {r['dedup']:28} det={r['trial_decision']} "
              + "; ".join(f"{x['key']}:{x['decision']}/{x['rule_id']}/ai={(x['ai'] or {}).get('proposal')}" for x in r["records"]))
    print(out["recall_found"], "found;", out["recall_included_by_deterministic_screen"], "included;", len(others),
          "other included trials,", out["other_included_trials"]["n_with_any_ai_reports_mace_yes"], "with AI MACE=yes")


if __name__ == "__main__":
    main(sys.argv[1])
