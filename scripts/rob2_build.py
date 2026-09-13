"""Build per-pooled-trial RoB2 assessments from the local AACT snapshot + registry-vs-pooled outcome
(Domain 5), writing committed cache/<slug>/rob2.json. Measure-time; replayed offline; rendered.
    python scripts/rob2_build.py [--write] [<slug> ...]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact, rob2, embed


def _match(a, b):
    r = embed.rank(a, [b])
    return bool(r) and r[0][1] >= 0.45


def pooled_ncts(slug):
    rev = json.load(open(f"{ROOT}/docs/reviews/{slug}/review.json", encoding="utf-8"))
    recs = {r["id"]: r for r in json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8"))["records"]}
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), None)
    out = {}
    for t in (prim or {}).get("trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "")
        nct = recs.get(pid, {}).get("nct") or (pid if pid.startswith("NCT") else None)
        if nct:
            out[nct] = pid
    return (prim or {}).get("name", ""), out


def main(argv):
    write = "--write" in argv
    slugs = [a for a in argv if not a.startswith("-")] or [
        s for s in sorted(os.listdir(f"{ROOT}/docs/reviews")) if os.path.exists(f"{ROOT}/docs/reviews/{s}/review.json")]
    topics = {s: pooled_ncts(s) for s in slugs}
    alln = set(n for _, d in topics.values() for n in d)
    if not alln:
        print("no pooled NCTs"); return 0
    # one pass: designs
    designs = {}
    for r in aact._iter_rows(aact._table("designs")):
        if (r.get("nct_id") or "").upper() in alln:
            designs[(r.get("nct_id") or "").upper()] = r
    # participant-flow attrition for D3 (one pass over milestones)
    attr = aact.attrition(alln)
    # one pass: registered PRIMARY + SECONDARY outcomes (a registered secondary is prespecified -> not D5)
    regprim = {n: [] for n in alln}
    regsec = {n: [] for n in alln}
    for r in aact._iter_rows(aact._table("design_outcomes")):
        nct = (r.get("nct_id") or "").upper()
        if nct in alln:
            ot = (r.get("outcome_type") or "").lower()
            title = r.get("measure") or r.get("title") or ""
            if ot == "primary":
                regprim[nct].append(title)
            elif ot == "secondary" and title:
                regsec[nct].append(title)
    _BLIND_TXT = ("double-blind", "double blind", "double-masked", "double masked", "double-dummy",
                  "double dummy", "placebo-controlled", "placebo controlled", "triple-blind",
                  "quadruple-blind", "quadruple blind")
    # explicit random-ASSIGNMENT phrases (not a bare "randomized" mention) -> D1 source hierarchy
    _RAND_TXT = ("randomly assigned", "randomly allocated", "randomized to", "randomised to",
                 "were randomized", "were randomised", "randomization", "randomisation",
                 "randomly divided", "randomly stratified", "randomly received")
    for slug, (pooled_out, d) in topics.items():
        if not d:
            continue
        # per-trial abstract, for the RoB source hierarchy (trial text > registry masking > Booleans)
        recs = {str(r.get("id")): (r.get("abstract") or "")
                for r in json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8")).get("records", [])}
        assess = {}
        for nct, pid in d.items():
            design = dict(designs.get(nct.upper()) or {}, attrition=attr.get(nct.upper()))
            ab = (recs.get(str(pid)) or "").lower()
            blinded_txt = any(kw in ab for kw in _BLIND_TXT)
            rand_txt = any(kw in ab for kw in _RAND_TXT)
            dom = rob2.assess(design, regprim.get(nct.upper(), []), pooled_out, _match,
                              registered_secondaries=regsec.get(nct.upper(), []),
                              blinded_by_text=blinded_txt, randomized_by_text=rand_txt)
            assess[pid] = {"nct": nct, "overall": rob2.overall(dom), "domains": dom}
        print(f"{slug}: " + "; ".join(f"{p}={a['overall'].split('(')[0].strip()}" for p, a in assess.items()))
        if write:
            json.dump({"source": f"AACT {os.path.basename(aact.snapshot_dir())} + registry-vs-pooled (D5)",
                       "trials": assess}, open(f"{ROOT}/cache/{slug}/rob2.json", "w", encoding="utf-8", newline=""),
                      indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
