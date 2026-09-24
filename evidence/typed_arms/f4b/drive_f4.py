"""Drive the F4 lane's producer (harness.pipeline.build_outcome_from_inputs, the path its own tests use) over the 34
held count entries, with and without evid2's overlay, and record what it computes.

usage: python drive_f4.py <F4 code root> <overlay.json or -> <out.json>

The F4 code root is a tree the F4 lane's patches were applied to (see RECONSTRUCTION.md); this script imports its
`harness` and never edits it. For each held entry (cache/<slug>/verified_arms.json, every object carrying ai/n1i/ci/n2i)
it builds the entry's outcome for that one trial and reports: the trial's count_binding_state / reason code, and the
observations the producer computed. An overlay entry adds ONLY `comparator_direction` and `contrast` to the held entry
-- never observations: observations are the producer's to compute."""
import copy, json, os, sys

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from harness import pipeline  # noqa: E402

overlay = {} if sys.argv[2] == "-" else json.load(open(sys.argv[2], encoding="utf-8"))
out_path = sys.argv[3]


def held_entries():
    for slug in sorted(os.listdir(os.path.join(ROOT, "cache"))):
        p = os.path.join(ROOT, "cache", slug, "verified_arms.json")
        if not os.path.isfile(p):
            continue
        va = json.load(open(p, encoding="utf-8"))
        for pid, v in va.items():
            items = v if isinstance(v, list) else [v]
            for i, e in enumerate(items):
                if isinstance(e, dict) and all(isinstance(e.get(k), (int, float)) and not isinstance(e.get(k), bool)
                                               for k in ("ai", "n1i", "ci", "n2i")):
                    yield slug, pid, (i if isinstance(v, list) else None), e, va


def spec_for(cfg, outcome):
    for kind, specs in (("primary", [cfg.get("primary_outcome")]), ("harm", cfg.get("harm_outcomes") or []),
                        ("secondary", cfg.get("secondary_outcomes") or [])):
        for s in specs:
            if s and s.get("name") == outcome:
                return kind, s
    return None, None


results = []
for slug, pid, idx, entry, va in held_entries():
    key = f"{slug}/{pid}" + (f"/{idx}" if idx is not None else "")
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    kind, spec = spec_for(cfg, entry.get("outcome"))
    recs = {str(r["id"]): r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["records"]}
    e = copy.deepcopy(entry)
    ov = overlay.get(key) or {}
    for k in ("comparator_direction", "contrast"):
        if k in ov:
            e[k] = ov[k]
    varm = copy.deepcopy(va[pid])
    if idx is not None:
        varm[idx] = e
    else:
        varm = e
    res = {"key": key, "slug": slug, "pid": pid, "outcome": entry.get("outcome"), "provenance": entry.get("provenance"),
           "tuple": [entry["ai"], entry["n1i"], entry["ci"], entry["n2i"]], "overlay": ov, "spec_kind": kind}
    if spec is None:
        res.update(state="NO_SPEC", reason="no outcome in the topic config has this entry's name")
        results.append(res)
        continue
    inp = {"config": cfg, "included": [{"id": pid, "id_type": "pmid", "decision": "include"}],
           "rec_by_id": {pid: recs.get(pid) or {"abstract": ""}},
           "interv": cfg["intervention_terms"], "comp": cfg["comparator_terms"],
           "cgr": {}, "ftbp": {}, "ojudg": None, "varms": {pid: varm}, "ljudg": None,
           "veffs": {}, "dsel": {}, "registry_designs": {}, "eligibility_contract": None}
    try:
        o = pipeline.build_outcome_from_inputs(inp, spec, "harm" if kind == "harm" else kind, slug)
    except Exception as ex:  # a crash is data, never a pass
        res.update(state="PRODUCER_ERROR", reason=f"{type(ex).__name__}: {ex}"[:400])
        results.append(res)
        continue
    trials = [t for t in o.get("trials", []) if str(t.get("id", "")).endswith(pid) or str(t.get("label")) == pid]
    absent = [a for a in o.get("declared_absent_trials", []) if pid in json.dumps(a)]
    if trials:
        t = trials[0]
        res.update(state="POOLED", count_binding_state=t.get("count_binding_state"),
                   reason_code=t.get("count_binding_reason_code"), observations=t.get("observations"),
                   arm_terms=t.get("count_arm_terms"))
    else:
        codes = sorted({str(a.get("reason_code") or a.get("count_binding_reason_code") or a.get("absent_kind")) for a in absent})
        res.update(state="NOT_POOLED", reason_codes=codes,
                   reasons=[str(a.get("reason") or a.get("endpoint_binding_reason") or "")[:300] for a in absent][:3],
                   observations=next((a.get("observations") for a in absent if a.get("observations")), None))
    results.append(res)
json.dump({"code_root": "F4 reconstruction (see RECONSTRUCTION.md)", "n": len(results), "results": results},
          open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
import collections  # noqa: E402
print(len(results), collections.Counter((r["state"], r.get("count_binding_state"), r.get("reason_code")) for r in results))
