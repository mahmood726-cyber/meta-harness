"""V1.1 discovery: can comparator-reference seeding be RE-ENABLED for corticosteroids-cap-mortality?

The topic protocol disables seeding: "the fixed NCT deduplication rule can let later secondary/subgroup reports
replace the original trial report". This experiment runs the seeding the production adapter would run
(harness.fetch._refs: PubMed elink pubmed_pubmed_refs of the comparator PMID 38128217, then harness.fetch._efetch),
holds the raw results with sha256, and compares two groupings of (committed records + seeded records):

  A. the production dedup  (harness.pipeline._dedup: one record per NCT by pivotal, primacy, earliest year)
  B. V1.1 family linking   (evidence/discovery/glp1-ra-mace-t2d/screen.py trials(): a publication naming exactly one
                            NCT links to that trial; one naming two links neither; a publication cited by two
                            registrations links neither -- secondary reports JOIN a family, they never replace)

The property tested (the protocol's own worry): for every trial that is pooled today, and for each named positive
control, the report that represents the trial is the same with seeding as without it.

usage: python seeding_test.py fetch   (network, once; writes run/seed_*.json)
       python seeding_test.py check   (offline; writes run/SEEDING_RESULT.json)
"""
import hashlib
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
SLUG = "corticosteroids-cap-mortality"
RUN = os.path.join(HERE, "run")


def _write(name, obj):
    os.makedirs(RUN, exist_ok=True)
    b = (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    open(os.path.join(RUN, name), "wb").write(b)
    return hashlib.sha256(b).hexdigest()


def fetch():
    from harness import fetch as F
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    refs = F._refs(str(cfg["comparator_pmid"]))
    recs = F._efetch([str(x) for x in refs]) if refs else []
    s1 = _write("seed_refs.json", {"adapter": "harness.fetch._refs", "comparator_pmid": cfg["comparator_pmid"],
                                   "retrieved_utc": t0, "pmids": refs})
    s2 = _write("seed_records.json", {"adapter": "harness.fetch._efetch", "retrieved_utc": t0, "records": recs})
    print(f"seeded {len(refs)} PMIDs; fetched {len(recs)} records; sha256 {s1[:12]} {s2[:12]}")


def fetch_crossref():
    """The production adapter returns NO references for this comparator (PubMed holds no pubmed_pubmed_refs links for
    38128217; the same call returns the GLP-1 comparator's list). A CANDIDATE V1.1 source: the comparator's reference
    list as deposited with Crossref (45 references, 32 with a DOI), each DOI resolved to a PMID by PubMed esearch
    '<doi>[doi]'. References without a DOI are listed, not guessed."""
    import urllib.request
    from harness import fetch as F
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    held = json.load(open(os.path.join(ROOT, "cache", SLUG, "comparator_identity.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(ROOT, "cache", SLUG, "comparator_identity.json")) else None
    doi = "10.1016/j.jcrc.2023.154507"
    req = urllib.request.Request("https://api.crossref.org/works/" + doi,
                                 headers={"User-Agent": "meta-harness V1.1 discovery (mailto:mahmood726@gmail.com)"})
    body = urllib.request.urlopen(req, timeout=60).read()
    refs = json.loads(body)["message"].get("reference") or []
    rows = []
    for r in refs:
        d = r.get("DOI")
        pm = F._esearch(f"{d}[doi]", 3) if d else []
        rows.append({"key": r.get("key"), "author": r.get("author"), "year": r.get("year"), "doi": d,
                     "pmids": pm, "state": "RESOLVED" if len(pm) == 1 else ("NO_DOI" if not d else f"{len(pm)}_PMIDS")})
    pmids = sorted({r["pmids"][0] for r in rows if r["state"] == "RESOLVED"})
    recs = F._efetch(pmids) if pmids else []
    s1 = _write("seed_refs_crossref.json", {"adapter": "candidate: Crossref reference list + PubMed esearch [doi]",
                                             "comparator_pmid": cfg["comparator_pmid"], "retrieved_utc": t0,
                                             "crossref_sha256": hashlib.sha256(body).hexdigest(), "references": rows,
                                             "pmids": pmids})
    s2 = _write("seed_records_crossref.json", {"adapter": "harness.fetch._efetch", "retrieved_utc": t0, "records": recs})
    print(f"crossref refs {len(refs)}; resolved {len(pmids)} PMIDs; fetched {len(recs)}; sha256 {s1[:12]} {s2[:12]}")


def _load_discovery_screen():
    p = os.path.join(ROOT, "evidence", "discovery", "glp1-ra-mace-t2d", "screen.py")
    spec = importlib.util.spec_from_file_location("disc_screen", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _as_pub(r):
    import re
    ncts = sorted(set(re.findall(r"NCT\d{8}", " ".join([str(r.get("nct") or "")] + [str(x) for x in r.get("databank_ncts") or []]))))
    abs_ncts = sorted(set(re.findall(r"NCT\d{8}", str(r.get("abstract") or ""))))
    return {"id": str(r["id"]), "databank_ncts": ncts, "abstract_ncts": abs_ncts, "nct": r.get("nct") or ""}


def check():
    from harness import pipeline
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    base = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    src = sys.argv[2] if len(sys.argv) > 2 else "pubmed"
    seed = json.load(open(os.path.join(RUN, "seed_records.json" if src == "pubmed" else "seed_records_crossref.json"),
                          encoding="utf-8"))["records"]
    have = {str(r.get("id")) for r in base.get("records") or []}
    new = [r for r in seed if str(r.get("id")) not in have]
    seeded = dict(base, records=list(base.get("records") or []) + new)
    import subprocess
    rev = json.loads(subprocess.run(["git", "-C", ROOT, "show", f"HEAD:docs/reviews/{SLUG}/review.json"],
                                    capture_output=True, text=True, encoding="utf-8").stdout)   # sparse worktree
    pooled = sorted({str(t["id"]).replace("PMID ", "") for o in rev["outcomes"] for t in o.get("trials") or []})
    controls = [str(x) for x in cfg.get("positive_control_pmids") or []]
    watch = sorted(set(pooled) | set(controls))
    pivotal = cfg.get("pivotal_trials")

    def survivors(blob):
        return {str(r.get("id")) for r in pipeline._dedup(blob, pivotal)}

    a0, a1 = survivors(base), survivors(seeded)
    by_id = {str(r.get("id")): r for r in seeded["records"]}
    displaced_A = []
    for pid in watch:
        if pid in a0 and pid not in a1:
            nct = (by_id.get(pid) or {}).get("nct")
            winner = next((i for i in a1 if (by_id.get(i) or {}).get("nct") == nct and nct), None)
            displaced_A.append({"report": pid, "nct": nct, "replaced_by": winner,
                                "replaced_by_title": (by_id.get(winner) or {}).get("title")})
    disc = _load_discovery_screen()
    ct = [{"id": n, "reference_pmids": [], "reference_types": {}} for n in sorted({r.get("nct") for r in seeded["records"] if r.get("nct")})]
    tr0, _, _ = disc.trials([_as_pub(r) for r in base["records"]], ct, [])
    tr1, _, _ = disc.trials([_as_pub(r) for r in seeded["records"]], ct, [])

    def fam_of(tr, pid):
        return next((tuple(t["ncts"]) for t in tr if f"PMID:{pid}" in t["members"]), None)

    moved_B = [{"report": pid, "family_without_seeding": fam_of(tr0, pid), "family_with_seeding": fam_of(tr1, pid)}
               for pid in watch if fam_of(tr0, pid) != fam_of(tr1, pid)]
    joined = [{"report": str(r["id"]), "title": r.get("title"), "joined_family": fam_of(tr1, str(r["id"]))}
              for r in new if fam_of(tr1, str(r["id"])) and any(fam_of(tr1, p) == fam_of(tr1, str(r["id"])) for p in watch)]
    out = {"seed_source": src, "comparator_pmid": cfg["comparator_pmid"], "seeded_pmids": len(seed), "new_records": len(new),
           "watched_reports": watch,
           "A_production_dedup": {"displaced": displaced_A,
                                  "verdict": "DEFECT_REPRODUCED" if displaced_A else "NO_DISPLACEMENT_ON_THIS_SEED_SET"},
           "B_family_linking": {"moved": moved_B, "secondary_reports_joined_a_watched_family": joined,
                                "verdict": "SEEDING_SAFE" if not moved_B else "SEEDING_UNSAFE"}}
    _write(f"SEEDING_RESULT_{src}.json", out)
    print(json.dumps({k: (v if k not in ("A_production_dedup", "B_family_linking") else {kk: vv for kk, vv in v.items()
                                                                                          if kk in ("verdict", "displaced", "moved")})
                      for k, v in out.items()}, indent=1, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    {"fetch": fetch, "fetch_crossref": fetch_crossref, "check": check}[sys.argv[1]]()
