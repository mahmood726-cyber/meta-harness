"""Deduplication and the deterministic screen for the discovery search (STRATEGY.md). Registered with the strategy.
usage: screen.py <records dir>   (reads records_{pubmed,ctgov,europepmc}.json.gz, writes TRIALS.json, SCREEN.json,
AI_SAMPLE.json into the same dir)"""
import copy, gzip, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from harness import screen as hscreen  # noqa: E402  (the pipeline's own deterministic screen)

# every CURATED, trial-specific list is removed: only the generic P/I/C/design criteria remain (STRATEGY.md)
STRIP = ("positive_control_pmids", "negative_control_pmids", "pubmed_queries", "seed_comparator_refs", "comparator_pmid",
         "companion_reports", "contrast_evictions", "extra_pmids")


def discovery_config():
    cfg = json.load(open(os.path.join(ROOT, "topics", "glp1-ra-mace-t2d.json"), encoding="utf-8"))
    cfg = copy.deepcopy(cfg)
    removed = [k for k in STRIP if k in cfg]
    for k in removed:
        cfg.pop(k)
    if "screen_overrides" in cfg.get("include", {}):
        cfg["include"].pop("screen_overrides")
        removed.append("include.screen_overrides")
    return cfg, removed


def load(d, name):
    return json.load(gzip.open(os.path.join(d, f"records_{name}.json.gz"), "rt", encoding="utf-8"))


def trials(pm, ct, ep):
    """Union-find over publications and registrations. A publication links to a registration only when it names
    exactly ONE NCT (a pooled analysis naming several would otherwise merge trials); a registration links to a
    publication its references list."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    pubs = {f"PMID:{r['id']}": r for r in pm}
    for r in ep:                                   # Europe PMC non-MEDLINE records; dedup by PMID where present
        key = f"PMID:{r['pmid']}" if r.get("pmid") else f"EPMC:{r['id']}"
        pubs.setdefault(key, r)
    regs = {f"NCT:{r['id']}": r for r in ct}
    multi = {}
    for k, r in pubs.items():
        find(k)
        ncts = sorted(set((r.get("databank_ncts") or []) + (r.get("abstract_ncts") or []) + ([r["nct"]] if r.get("nct") else [])))
        if len(ncts) == 1:
            union(k, f"NCT:{ncts[0]}")
        elif len(ncts) > 1:
            multi[k] = ncts
    for k, r in regs.items():
        find(k)
        for p in r.get("reference_pmids") or []:
            if (r.get("reference_types") or {}).get(p) in ("RESULT", "DERIVED") and f"PMID:{p}" in pubs:
                union(k, f"PMID:{p}")
    groups = {}
    for x in list(parent):
        groups.setdefault(find(x), []).append(x)
    out = []
    for i, (root, members) in enumerate(sorted(groups.items(), key=lambda kv: sorted(kv[1])[0])):
        out.append({"trial": f"T{i + 1:05d}", "members": sorted(members),
                    "ncts": sorted(m[4:] for m in members if m.startswith("NCT:")),
                    "pmids": sorted(m[5:] for m in members if m.startswith("PMID:")),
                    "in_registry_search": any(m in regs for m in members),
                    "multi_nct_publications": {m: multi[m] for m in members if m in multi}})
    return out, pubs, regs


def main(d):
    pm, ct, ep = load(d, "pubmed"), load(d, "ctgov"), load(d, "europepmc")
    tr, pubs, regs = trials(pm, ct, ep)
    cfg, removed = discovery_config()
    recs = list(pubs.values()) + [r for k, r in regs.items()]
    res = hscreen.run(recs, cfg)
    by = {}
    for dec in res["decisions"]:
        by[(dec["id_type"], str(dec["id"]))] = {k: dec.get(k) for k in ("decision", "rule_id", "reason", "span", "matched_intervention")}
    for t in tr:
        t["records"] = []
        for m in t["members"]:
            kind, ident = m.split(":", 1)
            r = pubs.get(m) or regs.get(m)
            if r is None:   # an NCT a publication names that the registry search did not retrieve (amendment 2)
                t["records"].append({"key": m, "id_type": "nct", "note": "named by a publication in this trial; "
                                     "not retrieved by the registry search", "screen": None})
                continue
            idt = r.get("id_type")
            t["records"].append({"key": m, "id_type": idt, "title": r.get("title"), "year": r.get("year"),
                                 "source": r.get("source"), "screen": by.get((idt, str(r["id"])))})
        t["decision"] = "include" if any((x["screen"] or {}).get("decision") == "include" for x in t["records"]) else "exclude"
    inc_recs = sorted(k for t in tr for x in t["records"] if (x["screen"] or {}).get("decision") == "include" for k in [x["key"]])
    exc_recs = sorted(x["key"] for t in tr for x in t["records"] if (x["screen"] or {}).get("decision") != "include")
    rng = random.Random(20260925)
    sample = sorted(rng.sample(exc_recs, min(200, len(exc_recs))))
    json.dump({"n_trials": len(tr), "n_included_trials": sum(t["decision"] == "include" for t in tr), "trials": tr},
              open(os.path.join(d, "TRIALS.json"), "w", encoding="utf-8", newline="\n"), indent=0, ensure_ascii=False)
    rules = {}
    for x in res["decisions"]:
        rules[x["rule_id"] or x["decision"]] = rules.get(x["rule_id"] or x["decision"], 0) + 1
    json.dump({"config_removed": removed, "n_records": len(recs), "rule_counts": rules,
               "included_records": inc_recs}, open(os.path.join(d, "SCREEN.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    json.dump({"seed": 20260925, "included_records": inc_recs, "excluded_sample": sample},
              open(os.path.join(d, "AI_SAMPLE.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(len(recs), "records,", len(tr), "trials,", sum(t["decision"] == "include" for t in tr), "trials included; rules", rules)


if __name__ == "__main__":
    main(sys.argv[1])
