"""Checklist A(e)/B3, the PRODUCER leg, independently of the lanes' own tests: run the real producer, build_bundle.build(slug,
check_only=True), in a worktree at <commit>, with ONE defect planted in memory into the review.json it reads (by wrapping
build_bundle._read_json). Report, per plant, the planted row's recorded admission (final + failing predicates) and whether the
row still enters the producer's pooled_reference. A rejection is demonstrated only if the row is refused AND (for the pool
rule) kept out of the pool. usage: producer_probe.py <worktree_root>"""
import copy
import importlib
import json
import sys
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(WT), str(WT / "scripts")]
sys.dont_write_bytecode = True
import build_bundle as bb  # noqa: E402

SLUG = "glp1-ra-mace-t2d"
LEADER, SUSTAIN6, REWIND, HARMONY = "27295427", "27633186", "31189511", "30291013"
real = bb._read_json


def row_of(review, pmid):
    prim = next(o for o in review["outcomes"] if o.get("primary"))
    return next(t for t in prim["trials"] if str(t.get("id") or t.get("label")).endswith(pmid))


def ci_truncated(r):
    t = row_of(r, LEADER); t["ci_low"] = float(str(t["ci_low"])[:3])          # 0.78 -> 0.7 (numeric prefix)


def component_swap(r):
    t = row_of(r, SUSTAIN6); t.update(effect=0.61, ci_low=0.38, ci_high=0.99)  # SUSTAIN-6's nonfatal-stroke numbers (a component)


def mixed_tuple(r):
    a, b = row_of(r, LEADER), row_of(r, SUSTAIN6); a.update(ci_low=b["ci_low"], ci_high=b["ci_high"])


def scale_relabel(r):
    row_of(r, LEADER)["scale"] = "OR"


PLANTS = {"none (control)": None, "numeric prefix: LEADER ci_low 0.78->0.7": ci_truncated,
          "component substituted: SUSTAIN-6 <- nonfatal stroke 0.61 (0.38-0.99)": component_swap,
          "mixed tuple: LEADER point + SUSTAIN-6 CI": mixed_tuple, "scale relabelled: LEADER HR -> OR": scale_relabel}


def run(plant):
    def planted(p):
        obj = real(p)
        if plant and str(p).replace("\\", "/").endswith(f"docs/reviews/{SLUG}/review.json"):
            obj = copy.deepcopy(obj)
            plant(obj)
        return obj
    bb._read_json = planted
    try:
        bundle, problems = bb.build(SLUG, check_only=True)
    finally:
        bb._read_json = real
    rows = {str(r["trial"]["id"]).replace("PMID ", ""): r for r in bundle["verification_rows"]}
    pooled = {str(i["id"]).replace("PMID ", "") for i in bundle["pooled_reference"]["inputs"]}
    out = {}
    for pmid in (LEADER, SUSTAIN6, HARMONY):
        adm = rows[pmid]["admission"] if pmid in rows else {}
        out[pmid] = {"final": adm.get("final"), "failing": [k for k, v in (adm.get("predicates") or {}).items()
                                                            if isinstance(v, dict) and v.get("state") not in (None, "PASS")][:6],
                     "in_pool": pmid in pooled}
    return out, problems, bundle["pooled_reference"].get("k"), (bundle["pooled_reference"].get("expected") or {}).get("estimate")


for name, plant in PLANTS.items():
    try:
        res, problems, k, est = run(plant)
        print(f"== {name}\n   pool k={k} estimate={est}  problems={len(problems)}")
        for pmid, v in res.items():
            print(f"   {pmid}: final={v['final']} in_pool={v['in_pool']} failing={v['failing']}")
    except Exception as e:  # noqa: BLE001 -- a producer that raises on a plant is a refusal of a kind; name it
        print(f"== {name}\n   PRODUCER RAISED {type(e).__name__}: {str(e)[:300]}")
