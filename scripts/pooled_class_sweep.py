"""Pooled-class sweep: every pooled row of every review, with the admission state it was pooled under and two checks computable
from the served review.json alone (no rebuild):

  C1 extra_components_in_pooled_row     -- a NEAR_MATCH row with a named EXTRA component is contributing to the pool
  C2 missing_components_inconsistent    -- missing_components is [] while the row's component set differs from the target set

Three pooled states are kept apart, because the producer renders them alike: EXACT_TARGET_POOLED, NEAR_MATCH_POOLED, UNBOUND_POOLED
(no class, no definition span; admitted through the UNBOUND_LEGACY fail-open). pcsk9-mace's k=3 pool (2026-09-20) holds one of each,
and ODYSSEY OUTCOMES (PMID 30403574) is the positive control: extra ['unstable angina'], missing [] while it names coronary heart
disease death where the target names cardiovascular death.

The target set is read two ways and both are printed: the producer's own canonical set of the outcome name (harness.target_endpoint
.canonical_components -- the lexicon that _class_verdict compared against) and the union of the components of the EXACT_TARGET rows
in the same pool. C2 fires on either.

Usage: python scripts/pooled_class_sweep.py [--ref <git ref>] [--json out.json]
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import target_endpoint as te  # noqa: E402


def _list(v):
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str) and v.startswith("["):
        try:
            return [str(x) for x in json.loads(v.replace("'", '"'))]
        except Exception:
            return [v]
    return []


def reviews(ref: str | None):
    if ref:
        names = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", ref, "docs/reviews/"], capture_output=True, text=True,
                               stdin=subprocess.DEVNULL, encoding="utf-8").stdout.split()
        for d in sorted(names):
            raw = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{d.rstrip('/')}/review.json"], capture_output=True, stdin=subprocess.DEVNULL).stdout
            if raw:
                yield d.rstrip("/").split("/")[-1], json.loads(raw.decode("utf-8-sig"))
    else:
        for d in sorted((ROOT / "docs" / "reviews").iterdir()):
            p = d / "review.json"
            if p.exists():
                yield d.name, json.loads(p.read_text(encoding="utf-8-sig"))


def pooled_state(t: dict) -> str:
    cls, adm, b = t.get("target_endpoint_class"), t.get("endpoint_admissibility"), t.get("endpoint_binding")
    if cls == "EXACT_TARGET":
        return "EXACT_TARGET_POOLED"
    if cls == "NEAR_MATCH" or (adm or "").startswith("NEAR_MATCH"):
        return "NEAR_MATCH_POOLED"
    if b == "unbound_legacy" or adm == "UNBOUND_LEGACY" or not cls:
        return "UNBOUND_POOLED"
    return f"OTHER:{cls}"


def check_row(t: dict, target_lexicon: set, target_exact_union: set) -> dict:
    comps = set(_list(t.get("target_endpoint_components")))
    extra = _list(t.get("target_endpoint_extra_components"))
    missing = _list(t.get("target_endpoint_missing_components"))
    def lacks(target):          # target components the row does not name (should appear in missing_components)
        return sorted(target - comps) if comps and target else []
    def surplus(target):        # row components the target does not name (should appear in extra_components)
        return sorted(comps - target) if comps and target else []
    lacks_lex, lacks_exact = lacks(target_lexicon), lacks(target_exact_union)
    surplus_lex, surplus_exact = surplus(target_lexicon), surplus(target_exact_union)
    return {"row_components": sorted(comps), "extra_components": extra, "missing_components": missing,
            "C1_extra_components_in_pooled_row": bool(extra),
            # direction matters: a row that LACKS a target component with missing [] is the withdrawn-review defect; a row with a
            # SURPLUS component and extra [] against the lexicon target alone is usually the lexicon collapsing the target name
            "C2_missing_components_inconsistent": (not missing) and bool(lacks_lex or lacks_exact),
            "C3_extra_components_inconsistent": (not extra) and bool(surplus_lex or surplus_exact),
            "row_lacks": {"lexicon_canonical": lacks_lex, "exact_rows_union": lacks_exact},
            "row_surplus": {"lexicon_canonical": surplus_lex, "exact_rows_union": surplus_exact}}


def sweep(ref: str | None) -> dict:
    rows, n_reviews = [], 0
    for slug, rev in reviews(ref):
        n_reviews += 1
        for o in rev.get("outcomes", []):
            trials = o.get("trials") or []
            if not trials:
                continue
            spec = {"name": o.get("name"), "components": o.get("components") or o.get("canonical_components")}
            try:
                target_lex = set(te.canonical_components(spec) or [])
            except Exception:
                target_lex = set()
            exact_union = set()
            for t in trials:
                if t.get("target_endpoint_class") == "EXACT_TARGET":
                    exact_union |= set(_list(t.get("target_endpoint_components")))
            for t in trials:
                c = check_row(t, target_lex, exact_union)
                rows.append({"slug": slug, "outcome": o.get("name"), "primary": bool(o.get("primary")), "k": len(trials), "trial": t.get("id"),
                             "pooled_state": pooled_state(t), "target_endpoint_class": t.get("target_endpoint_class"),
                             "endpoint_admissibility": t.get("endpoint_admissibility"), "endpoint_binding": t.get("endpoint_binding"),
                             "definition_span": (t.get("endpoint_definition_span") or "")[:200] or None,
                             "target_set": {"lexicon_canonical": sorted(target_lex), "exact_rows_union": sorted(exact_union)}, **c})
    by_state = {}
    for r in rows:
        by_state[r["pooled_state"]] = by_state.get(r["pooled_state"], 0) + 1
    mixed = {}
    for r in rows:
        mixed.setdefault((r["slug"], r["outcome"]), set()).add(r["pooled_state"])
    mixed_pools = [{"slug": k[0], "outcome": k[1], "states": sorted(v)} for k, v in mixed.items() if len(v) > 1]
    return {"ref": ref or "WORKING_TREE", "reviews": n_reviews, "pooled_rows": len(rows), "by_pooled_state": by_state,
            "C1_hits": [r for r in rows if r["C1_extra_components_in_pooled_row"]],
            "C2_hits": [r for r in rows if r["C2_missing_components_inconsistent"]],
            "C3_hits": [r for r in rows if r["C3_extra_components_inconsistent"]],
            "pools_mixing_states": mixed_pools, "rows": rows}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    out = sweep(a.ref)
    print(f"pooled-class sweep @ {out['ref']}: {out['reviews']} reviews, {out['pooled_rows']} pooled rows, by state {out['by_pooled_state']}; "
          f"C1 hits {len(out['C1_hits'])}, C2 hits {len(out['C2_hits'])}, C3 hits {len(out['C3_hits'])}, pools mixing states {len(out['pools_mixing_states'])}")
    for name in ("C1_hits", "C2_hits", "C3_hits"):
        for r in out[name]:
            print(f"  {name[:2]} {r['slug']} | {r['outcome']} | {r['trial']} | {r['pooled_state']} | comps {r['row_components']} extra {r['extra_components']} "
                  f"missing {r['missing_components']} | lacks {r['row_lacks']} | surplus {r['row_surplus']}")
    for m in out["pools_mixing_states"]:
        print(f"  MIXED {m['slug']} | {m['outcome']} | {m['states']}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
