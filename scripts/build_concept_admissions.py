"""GENERATE the concept-admission registers (harness/concept_admission.py) -- never hand-edited.

For every topic: each family that is ELIGIBLE in cache/<slug>/families.json, is not represented in the RAW search cache
(records.json, never read through the overlay), and whose own report PMID family_discovery found by a concept / cross-link route,
is a CANDIDATE. A candidate becomes an ADMITTED register entry only when a signed item names it (SIGNED below, checked
against registry/v14_signatures.json) and its report's efetch abstract is held (outputs/held_abstracts, sha256 pinned
in the manifest, the article itself naming the NCT). Every other candidate is listed in the sweep, never applied.

    python scripts/build_concept_admissions.py --fetch      # hold the signed items' abstracts (efetch), then build
    python scripts/build_concept_admissions.py              # offline: re-verify the held bytes and rebuild

Writes cache/<slug>/concept_admissions.json for a topic with an admitted entry, and the sweep over all topics to
outputs/k_gap/g1_binding/concept_admissions_sweep.json.
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import concept_admission as ca  # noqa: E402

HELD = os.path.join(ROOT, "outputs", "held_abstracts")
# the signed items that admit a family's report into a topic's study set: (slug, pmid, nct) -> item
SIGNED = {("glp1-ra-mace-t2d", "38785209", "NCT03819153"): "V14-04"}


def _j(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return json.load(f)


def eligible_absent(slug: str) -> list[str]:
    """ELIGIBLE families with no record in the study set (by NCT) -- the population the route could act on."""
    cache = os.path.join(ROOT, "cache", slug)
    if not os.path.exists(os.path.join(cache, "families.json")):
        return []
    # the RAW search cache: reading it through the overlay would count an admitted report as already present
    records = _j("cache", slug, "records.json")
    in_set = {str(r.get("nct") or "").upper() for r in records.get("records") or []} - {""}
    return sorted(str(f.get("family_id")) for f in _j("cache", slug, "families.json").get("families") or []
                  if (f.get("eligibility") or {}).get("state") == "ELIGIBLE" and str(f.get("family_id")).upper() not in in_set)


def candidates(slug: str) -> list[dict]:
    cache = os.path.join(ROOT, "cache", slug)
    if not all(os.path.exists(os.path.join(cache, f)) for f in ("families.json", "family_discovery.json", "records.json")):
        return []
    records = _j("cache", slug, "records.json")         # the RAW search cache (see eligible_absent)
    in_set_ids = {str(r.get("id")) for r in records.get("records") or []}
    in_set_ncts = {str(r.get("nct") or "").upper() for r in records.get("records") or []} - {""}
    disc = _j("cache", slug, "family_discovery.json")
    found = {str(r.get("id")): r for r in (disc.get("r3_records") or []) + (disc.get("records") or [])}
    out = []
    for fam in _j("cache", slug, "families.json").get("families") or []:
        nct = str(fam.get("family_id") or "")
        if (fam.get("eligibility") or {}).get("state") != "ELIGIBLE" or nct.upper() in in_set_ncts:
            continue
        for rep in fam.get("reports") or []:
            pid = str(rep.get("report_id") or "")
            rec = found.get(pid)
            routes = [str(x).split("#")[0] for x in (rec or {}).get("found_by") or []]
            if not pid.isdigit() or pid in in_set_ids or not rec or not any(r in ca.CONCEPT_ROUTES for r in routes):
                continue
            out.append({"slug": slug, "pmid": pid, "nct": nct, "acronym": (fam.get("aliases") or {}).get("acronym"),
                        "title": rec.get("title"), "routes": rec.get("found_by_routes") or routes,
                        "role": rep.get("role"), "signed_item": SIGNED.get((slug, pid, nct))})
    return out


def hold(pmid: str, nct: str, item: str, slug: str) -> None:
    """efetch the report's abstract and hold it verbatim, refusing unless the article itself names the NCT."""
    import v14_02_dpp4_hhf as v2
    url, got = v2.fetch([pmid])
    if pmid not in got:
        raise SystemExit(f"REFUSED {pmid}: efetch returned no article")
    text, art = got[pmid]
    w = v2.witness(art, nct)
    if not w:
        raise SystemExit(f"REFUSED {pmid}: the article does not itself name {nct}")
    os.makedirs(HELD, exist_ok=True)
    with open(os.path.join(HELD, f"pubmed_{pmid}.txt"), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    mp = os.path.join(HELD, "manifest.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"documents": {}}
    man["documents"][f"pubmed_{pmid}.txt"] = {
        "pmid": pmid, "nct": nct, "nct_basis": w[0], "nct_evidence": w[1],
        "source": url + f"?db=pubmed&id={pmid}&retmode=xml",
        "normalisation": "AbstractText elements joined by a space, tags stripped, HTML-unescaped, whitespace collapsed",
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "held_for": f"{item} {slug}: the family's own report, admitted to the study set (concept-discovered)"}
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2, sort_keys=True)
        f.write("\n")


def entry(c: dict) -> dict:
    sig = (_j("registry", "v14_signatures.json").get("items") or {}).get(c["signed_item"]) or {}
    name = f"pubmed_{c['pmid']}.txt"
    man = (_j("outputs", "held_abstracts", "manifest.json").get("documents") or {}).get(name) or {}
    text = open(os.path.join(HELD, name), encoding="utf-8").read()
    disc = _j("cache", c["slug"], "family_discovery.json")
    rec = next(r for r in (disc.get("r3_records") or []) + (disc.get("records") or []) if str(r.get("id")) == c["pmid"])
    return {"state": ca.ADMITTED, "pmid": c["pmid"], "nct": c["nct"], "acronym": c["acronym"],
            "signed_item": c["signed_item"],
            "signature": {"choice": sig.get("choice"), "item_section_sha256": sig.get("item_section_sha256")},
            "discovery_routes": c["routes"],
            "eligibility_witness": {"file": f"cache/{c['slug']}/families.json", "family_id": c["nct"],
                                    "state": "ELIGIBLE", "report_role": c["role"]},
            "abstract_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "abstract_ref": f"outputs/held_abstracts/{name}", "nct_witness": man.get("nct_basis"),
            "record": {"id": c["pmid"], "id_type": "pmid", "title": rec.get("title"), "doi": rec.get("doi"),
                       "nct": c["nct"]}}


def main(argv):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    slugs = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "topics")) if f.endswith(".json")
                   and os.path.exists(os.path.join(ROOT, "docs", "reviews", f[:-5], "review.json")))
    sweep = {s: candidates(s) for s in slugs}
    for s, cs in sweep.items():
        admitted = []
        for c in cs:
            if not c["signed_item"]:
                continue
            if "--fetch" in argv:
                hold(c["pmid"], c["nct"], c["signed_item"], s)
            admitted.append(entry(c))
        if admitted:
            reg = {"generated_by": "scripts/build_concept_admissions.py (GENERATED, never hand-edited)",
                   "entries": admitted}
            with open(os.path.join(ROOT, "cache", s, ca.REGISTER), "w", encoding="utf-8", newline="\n") as f:
                json.dump(reg, f, indent=1, ensure_ascii=False)
                f.write("\n")
            ca.admitted_records(os.path.join(ROOT, "cache", s))      # re-verify what was just written; raises
    # REACH, not coverage: a topic without family_discovery.json holds no concept-discovery record, so the route can
    # derive no candidate there -- its ELIGIBLE-but-absent families are listed as such, never counted as 'none'
    reach = {s: os.path.exists(os.path.join(ROOT, "cache", s, "family_discovery.json")) for s in slugs}
    out = {"topics": len(slugs), "topics_with_discovery_records": sorted(s for s, ok in reach.items() if ok),
           "candidates": sum(len(v) for v in sweep.values()),
           "admitted": [c for v in sweep.values() for c in v if c["signed_item"]],
           "listed_not_applied": {s: [c for c in v if not c["signed_item"]] for s, v in sweep.items()
                                  if any(not c["signed_item"] for c in v)},
           "eligible_absent_without_discovery_record": {s: fams for s in slugs if not reach[s]
                                                        for fams in [eligible_absent(s)] if fams}}
    p = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "concept_admissions_sweep.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"topics {out['topics']} (discovery records held in {len(out['topics_with_discovery_records'])}); candidates "
          f"{out['candidates']}; admitted {len(out['admitted'])}")
    for s, v in out["listed_not_applied"].items():
        print(f"  {s}: {len(v)} listed (unsigned) -- {', '.join(str(c['acronym'] or c['nct']) for c in v[:6])}")
    for s, v in out["eligible_absent_without_discovery_record"].items():
        print(f"  {s}: {len(v)} ELIGIBLE families absent from the study set, no discovery record: {', '.join(v[:5])}")


if __name__ == "__main__":
    main(sys.argv[1:])
