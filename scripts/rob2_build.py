"""Build per-pooled-trial registry-machine-signal-restricted assessments from the local AACT snapshot + registry-vs-pooled outcome
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
    """Return (primary-outcome-name, {pid: nct_or_None}) for EVERY pooled primary-outcome trial.
    Previously a trial with no NCT (RALES) was DROPPED and never RoB-assessed, and a trial whose NCT
    is not in the AACT snapshot (J-EMPHASIS NCT01115855, SOUL NCT03914326 -- registered abroad or
    absent) rendered as 'no registry match / unassessed' even though its identity is known to the
    Results table. Keep ALL pooled trials keyed by pid; the canonical NCT (from records) rides along
    for the AACT lookup but is NOT required for assessment -- the abstract-based RoB fallback covers
    blinding/randomisation for a trial AACT does not carry."""
    rev = json.load(open(f"{ROOT}/docs/reviews/{slug}/review.json", encoding="utf-8"))
    recs = {r["id"]: r for r in json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8"))["records"]}
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), None)
    out = {}
    for t in (prim or {}).get("trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "")
        nct = recs.get(pid, {}).get("nct") or (pid if pid.startswith("NCT") else None)
        out[pid] = (nct or None)
    return (prim or {}).get("name", ""), out


def main(argv):
    write = "--write" in argv
    slugs = [a for a in argv if not a.startswith("-")] or [
        s for s in sorted(os.listdir(f"{ROOT}/docs/reviews")) if os.path.exists(f"{ROOT}/docs/reviews/{s}/review.json")]
    topics = {s: pooled_ncts(s) for s in slugs}
    alln = set(nct.upper() for _, d in topics.values() for nct in d.values() if nct)
    if not any(d for _, d in topics.values()):
        print("no pooled trials"); return 0
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
            outcome = {"measure": r.get("measure") or "", "title": r.get("title") or "",
                       "description": r.get("description") or ""}
            if ot == "primary":
                regprim[nct].append(outcome)
            elif ot == "secondary" and (outcome["measure"] or outcome["title"] or outcome["description"]):
                regsec[nct].append(outcome)
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
        for pid, nct in d.items():
            NCT = nct.upper() if nct else None
            design = dict((designs.get(NCT) if NCT else None) or {}, attrition=attr.get(NCT) if NCT else None)
            ab = (recs.get(str(pid)) or "").lower()
            blinded_txt = any(kw in ab for kw in _BLIND_TXT)
            rand_txt = any(kw in ab for kw in _RAND_TXT)
            dom = rob2.assess(design, regprim.get(NCT, []) if NCT else [], pooled_out, _match,
                              registered_secondaries=(regsec.get(NCT, []) if NCT else []),
                              blinded_by_text=blinded_txt, randomized_by_text=rand_txt)
            assess[pid] = {"nct": nct, "registry_in_aact": bool(NCT and NCT in designs),
                           "assessed_from": ("registry+abstract" if (NCT and NCT in designs) else "abstract only"),
                           "overall": rob2.overall(dom), "domains": dom, "rob_basis": rob2.rob_basis(dom)}
        print(f"{slug}: " + "; ".join(f"{p}={a['overall'].split('(')[0].strip()}" for p, a in assess.items()))
        if write:
            json.dump({"source": f"AACT {os.path.basename(aact.snapshot_dir())} + registry-vs-pooled (D5)",
                       "output_family": rob2.OUTPUT_FAMILY,
                       "rob_basis": {"output_family": rob2.OUTPUT_FAMILY,
                                     "assessed_domains": [rob2.DOMAIN_LABELS[d] for d in rob2.MACHINE_DOMAINS],
                                     "unassessed_domains": ["D3_missing_outcome_data"]},
                       "trials": assess}, open(f"{ROOT}/cache/{slug}/rob2.json", "w", encoding="utf-8", newline=""),
                      indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
