"""Build per-pooled-trial registry-machine-signal-restricted assessments from the local AACT snapshot + registry-vs-pooled outcome
(Domain 5), writing committed cache/<slug>/rob2.json. Measure-time; replayed offline; rendered.
    python scripts/rob2_build.py [--write] [<slug> ...]
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact, embed, rob2


def _match(a, b):
    ranked = embed.rank(a, [b])
    return bool(ranked) and ranked[0][1] >= 0.45


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


def selected_endpoints(slug):
    """{pid: (text, role)} -- each pooled trial's SELECTED endpoint, from its own served row (r25): the registered
    outcome it is bound to (registry_title / registry_type), else its definition span, else the selected result's own
    source clause; role 'primary' / 'secondary' from the registry type or that clause, else None. Never the topic's
    generic outcome name."""
    rev = json.load(open(f"{ROOT}/docs/reviews/{slug}/review.json", encoding="utf-8"))
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), None)
    out = {}
    for t in (prim or {}).get("trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "")
        title = str(t.get("registry_title") or "") or None          # the registered outcome the row is bound to
        src = re.sub(r"^[^:]{0,80}\((?:registered estimand|target endpoint)\):\s*", "", str(t.get("source") or ""))
        rt = str(t.get("registry_type") or "").lower()
        if rt in ("primary", "secondary"):
            role = rt
        elif re.search(r"\bprimary[\s-]+(?:composite\s+)?(?:end\s*-?\s*point|outcome)", src, re.I):   # 'primary-outcome'
            role = "primary"
        elif re.search(r"\bsecondary\s+(?:end\s*-?\s*point|outcome)", src, re.I):
            role = "secondary"
        else:
            role = None
        out[pid] = (title, role)
    return out


def factor_terms(slug, ncts):
    """(our intervention terms, OTHER factors' intervention names) -- the latter from AACT interventions of the trial's
    registry records (drug / biological / device / procedure), minus ours and placebo-like controls (CLEAR: colchicine
    is ours; spironolactone and the stent are other factors)."""
    cfg = json.load(open(f"{ROOT}/topics/{slug}.json", encoding="utf-8"))
    ours = [x for x in (cfg.get("intervention_terms") or []) if isinstance(x, str)]
    ag = cfg.get("intervention_agents") or {}
    ours += [a for k, v in (ag.items() if isinstance(ag, dict) else []) for a in [k] + list(v or [])]
    ours += [a for a in (ag if isinstance(ag, list) else [])]
    # the COMPARATOR is not another factor (Hokusai-VTE's warfarin, esketamine's oral antidepressant)
    comp = [x for x in (cfg.get("comparator_terms") or []) if isinstance(x, str)]
    other = {}
    for nct in ncts:
        for name, typ in INTERVENTIONS.get(nct, []):
            if typ not in ("DRUG", "BIOLOGICAL", "DEVICE", "PROCEDURE"):
                continue
            if re.search(r"placebo|sham|standard|usual|control|matching|antidepressant", name, re.I) \
                    or rob2._names_any(name, ours) or rob2._names_any(name, comp):
                continue
            other[name] = 1
    # a factorial trial has >= 2 ACTIVE arms besides ours (CLEAR: spironolactone + stent); one other active
    # intervention is this trial's comparator or background therapy, never a factor whose outcomes are set aside
    return sorted(set(ours)), (sorted(other) if len(other) >= 2 else [])


INTERVENTIONS = {}


def topic_record_ncts(slug):
    data = json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8"))
    out = set()
    for row in data.get("records", []) or []:
        nct = str(row.get("nct") or "").upper()
        rid = str(row.get("id") or "").upper()
        if nct:
            out.add(nct)
        if rid.startswith("NCT"):
            out.add(rid)
    for row in data.get("ctgov") or []:
        nct = str(row.get("nct_id") or row.get("id") or "").upper()
        if nct:
            out.add(nct)
    for row in data.get("designs") or []:
        nct = str(row.get("nct_id") or row.get("id") or "").upper()
        if nct:
            out.add(nct)
    return out


def _derived_ncts_by_pmid(pmids):
    want = {str(p).strip() for p in pmids if str(p).strip().isdigit()}
    out = {p: [] for p in want}
    p = aact._table("study_references")
    if not p or not want:
        return out
    for r in aact._iter_rows(p):
        pmid = (r.get("pmid") or "").strip()
        nct = (r.get("nct_id") or "").upper()
        if pmid in want and nct and (r.get("reference_type") or "").upper() == "DERIVED":
            if nct not in out[pmid]:
                out[pmid].append(nct)
    return out


def main(argv):
    write = "--write" in argv
    slugs = [a for a in argv if not a.startswith("-")] or [
        s for s in sorted(os.listdir(f"{ROOT}/docs/reviews")) if os.path.exists(f"{ROOT}/docs/reviews/{s}/review.json")]
    raw_topics = {s: pooled_ncts(s) for s in slugs}
    topic_ncts = {s: topic_record_ncts(s) for s in slugs}
    linked = _derived_ncts_by_pmid(pid for _, d in raw_topics.values() for pid in d)
    topics = {}
    for slug, (pooled_out, d) in raw_topics.items():
        enriched = {}
        for pid, nct in d.items():
            registry_ncts = []
            if nct:
                registry_ncts.append(nct.upper())
            for linked_nct in linked.get(pid, []):
                if linked_nct not in registry_ncts:
                    registry_ncts.append(linked_nct)
            enriched[pid] = {"nct": nct, "registry_ncts": registry_ncts}
        topics[slug] = (pooled_out, enriched)
    alln = set(nct for _, d in topics.values() for item in d.values() for nct in item["registry_ncts"])
    all_design_ncts = set(alln)
    for ncts in topic_ncts.values():
        all_design_ncts.update(ncts)
    if not any(d for _, d in topics.values()):
        print("no pooled trials"); return 0
    # one pass: designs
    designs = {}
    for r in aact._iter_rows(aact._table("designs")):
        nct = (r.get("nct_id") or "").upper()
        if nct in all_design_ncts:
            designs[nct] = r
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
    # one pass: registered interventions (factorial trials: which factor a registered outcome belongs to)
    INTERVENTIONS.clear()
    for r in aact._iter_rows(aact._table("interventions")):
        nct = (r.get("nct_id") or "").upper()
        if nct in alln:
            INTERVENTIONS.setdefault(nct, []).append((r.get("name") or "", (r.get("intervention_type") or "").upper()))
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
        sel_of = selected_endpoints(slug)
        for pid, info in d.items():
            nct = info.get("nct")
            registry_ncts = info.get("registry_ncts") or []
            NCT = (nct.upper() if nct else None) or (registry_ncts[0] if registry_ncts else None)
            design = dict((designs.get(NCT) if NCT else None) or {}, attrition=attr.get(NCT) if NCT else None)
            ab = (recs.get(str(pid)) or "").lower()
            blinded_txt = any(kw in ab for kw in _BLIND_TXT)
            rand_txt = any(kw in ab for kw in _RAND_TXT)
            primaries = [out for rn in registry_ncts for out in regprim.get(rn, [])]
            secondaries = [out for rn in registry_ncts for out in regsec.get(rn, [])]
            title, role = sel_of.get(str(pid)) or (None, None)
            ours, other = factor_terms(slug, registry_ncts)
            dom = rob2.assess(design, primaries, pooled_out, _match,
                              registered_secondaries=secondaries,
                              blinded_by_text=blinded_txt, randomized_by_text=rand_txt,
                              selected={"registered_title": title, "role": role, "our_terms": ours,
                                        "other_factor_terms": other})
            basis = rob2.rob_basis(dom)
            assess[pid] = {"nct": nct, "registry_in_aact": bool(NCT and NCT in designs),
                           "assessed_from": ("registry+abstract" if (NCT and NCT in designs) else "abstract only"),
                           **({"registry_ncts": registry_ncts} if len(registry_ncts) > 1 else {}),
                           "overall": rob2.overall(dom), "domains": dom, "rob_basis": basis,
                           "assessed_domains": basis["assessed_domains"],
                           "unassessed_domains": basis["unassessed_domains"]}
        print(f"{slug}: " + "; ".join(f"{p}={a['overall'].split('(')[0].strip()}" for p, a in assess.items()))
        if write:
            registry_rows = {
                nct: dict(designs.get(nct) or {"nct_id": nct})
                for nct in sorted(topic_ncts.get(slug, set()))
            }
            json.dump(registry_rows, open(f"{ROOT}/cache/{slug}/registry_designs.json", "w", encoding="utf-8", newline=""),
                      indent=2, ensure_ascii=False)
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
