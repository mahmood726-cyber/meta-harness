"""Corpus-wide `n of N` for the six statins-older-adults extractors (Mahmood 2026-09-28, 'fix all in harness').

For every topic it runs each extractor on the committed inputs (records.json, the family registry) and, for the pooled
rows, on the rebuilt review.json, and reports what the extractor CHANGED (n) of what it EXAMINED (N), naming every
changed item. Read-only; prints JSON.
  PYTHONIOENCODING=utf-8 python scripts/statins_extractor_census.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import (component_typing, measure_guard, registry_criteria, report_linkage, screen,  # noqa: E402
                     subgroup_provenance, trial_family)

PID = lambda x: (re.search(r"NCT\d{8}|\b\d{7,8}\b", str(x or "")) or re.search("", "")).group(0)
out = {k: {"n": 0, "N": 0, "items": []} for k in (
    "1_condition_label_excluded_by_criteria__screen", "1b_population_from_inclusion_criteria__family",
    "2_3_report_linkage", "4_rmst_on_ratio_scale", "5_subgroup_provenance_typed", "5b_subgroup_provenance_conflict",
    "6_component_set_typed", "6b_component_items_untyped")}
for fn in sorted(os.listdir(os.path.join(ROOT, "topics"))):
    if not fn.endswith(".json"):
        continue
    slug = fn[:-5]
    cfg = dict(json.load(open(os.path.join(ROOT, "topics", fn), encoding="utf-8")), slug=slug)
    rp = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(rp):
        continue
    d = json.load(open(rp, encoding="utf-8"))
    recs, ct = d.get("records") or [], d.get("ctgov") or []
    reg = trial_family.load_registry(ROOT, slug) or {}
    crit = {n: ((h.get("population") or {}).get("criteria") or {}).get("value") for n, h in reg.items()}
    inc = cfg.get("include") or {}
    # 1: screen decisions with vs without the registry-criteria rule, over every registry record
    for r in ct:
        o = out["1_condition_label_excluded_by_criteria__screen"]
        o["N"] += 1
        before = screen.screen_record(r, inc, set())
        after = screen.screen_record(r, dict(inc, _registry_criteria={k: v for k, v in crit.items() if v}), set())
        if tuple(before)[:2] != tuple(after)[:2]:
            o["n"] += 1
            o["items"].append(f"{slug}:{r['id']} {tuple(before)[1]}->{tuple(after)[1]}")
    # 2+3: derived report links over every publication without its own registration
    links = report_linkage.derive(recs, cfg)
    declared = {str(x.get("pmid")): x for x in (json.load(open(os.path.join(ROOT, "docs", "study_families.json"),
                                                                encoding="utf-8")).get("topics") or {}).get(slug, [])}
    o = out["2_3_report_linkage"]
    o["N"] += sum(1 for r in recs if not report_linkage._nct_of(r) and re.fullmatch(r"\d{6,9}", str(r.get("id"))))
    for x in links:
        o["n"] += 1
        agree = ("declared elsewhere: " + ("AGREES" if str(declared[x["pmid"]].get("parent_pmid")) == x["parent_pmid"]
                                          else "DISAGREES")) if x["pmid"] in declared else "new"
        o["items"].append(f"{slug}:{x['pmid']}->{x['parent_pmid']} ({'+'.join(r['rule'] for r in x['derived']['rules'])}; {agree})")
    # rebuilt review: families and pooled rows
    rv_p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if not os.path.exists(rv_p):
        continue
    rv = json.load(open(rv_p, encoding="utf-8"))
    for f in rv.get("trial_families") or []:
        o = out["1b_population_from_inclusion_criteria__family"]
        o["N"] += 1
        sp = (f.get("eligibility") or {}).get("span") or {}
        if sp.get("population_basis") == "REGISTRY_INCLUSION_CRITERIA" or sp.get("condition_labels_excluded_by_criteria"):
            o["n"] += 1
            o["items"].append(f"{slug}:{f['family_id']} ({sp.get('population_basis')}; excluded labels "
                              f"{sp.get('condition_labels_excluded_by_criteria') or []})")
    by_id = {str(r["id"]): r for r in recs}
    for oc in rv.get("outcomes") or []:
        for t in oc.get("trials") or []:
            pid = PID(t.get("id"))
            rec = by_id.get(pid) or {}
            out["4_rmst_on_ratio_scale"]["N"] += 1
            if measure_guard.measure_of(t) == "RMST_DIFFERENCE":
                out["4_rmst_on_ratio_scale"]["n"] += 1
                out["4_rmst_on_ratio_scale"]["items"].append(f"{slug}:{oc['name']}:{pid}")
            c = subgroup_provenance.classify(f"{rec.get('title') or ''} {rec.get('abstract') or ''}")
            out["5_subgroup_provenance_typed"]["N"] += 1
            if c["state"] != "UNSTATED":
                out["5_subgroup_provenance_typed"]["n"] += 1
                out["5_subgroup_provenance_typed"]["items"].append(f"{slug}:{oc['name']}:{pid} {c['state']}")
            ann = (((cfg.get("primary_outcome") or {}).get("trial_annotations") or {}).get(pid) or {}).get("evidence_unit")
            out["5b_subgroup_provenance_conflict"]["N"] += 1 if ann else 0
            if ann and str(ann).startswith("prespecified") and c["state"] in ("POST_HOC", "CONFLICTING_STATEMENTS"):
                out["5b_subgroup_provenance_conflict"]["n"] += 1
                out["5b_subgroup_provenance_conflict"]["items"].append(f"{slug}:{oc['name']}:{pid} {c['spans']}")
            typed = component_typing.derive(rec.get("abstract"))
            out["6_component_set_typed"]["N"] += 1
            if typed:
                out["6_component_set_typed"]["n"] += 1
                if typed["untyped"]:
                    out["6b_component_items_untyped"]["n"] += 1
                    out["6b_component_items_untyped"]["items"].append(f"{slug}:{oc['name']}:{pid} {typed['untyped']}")
            out["6b_component_items_untyped"]["N"] += 1 if typed else 0
print(json.dumps({k: {"n_of_N": f"{v['n']} of {v['N']}", "items": v["items"]} for k, v in out.items()}, indent=1,
                 ensure_ascii=False))
