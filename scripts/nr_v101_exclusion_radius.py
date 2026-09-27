"""Corpus-wide radius of lane NR's V1.0.1 EXCLUSION POLARITY change (read-only; writes only the dump/diff it is told to).

  python scripts/nr_v101_exclusion_radius.py dump OUT.json
  python scripts/nr_v101_exclusion_radius.py diff BEFORE.json AFTER.json [--out REPORT.json]

Dumped from THIS tree's harness (BEFORE = the candidate's target_endpoint / hand_binding / verify_bundle / build_bundle):
  rows   every served row of every committed page (pooled AND declared-absent) that carries a `source`, classified by
         harness.target_endpoint.classify_bound(spec, abstract, source) -- the abstract route's own classifier -- with
         the outcome's registered spec: class, INCLUDES, EXCLUDES and the admissibility verdict (_class_verdict).
  defs   harness.target_endpoint._definition_sentences(abstract) for every cached record: each definition span with its
         INCLUDES (and, AFTER, EXCLUDES) -- the pool every named-endpoint result binds to.
  sents  harness.target_endpoint._components_from_text(sentence) for every sentence of every cached abstract: the
         component reader's whole radius, including sentences no current row binds to.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import extract, target_endpoint as te  # noqa: E402


def _outcomes(cfg):
    return [cfg["primary_outcome"]] + list(cfg.get("secondary_outcomes") or []) + list(cfg.get("harm_outcomes") or [])


def _pid(x):
    return str(x or "").replace("PMID ", "").strip()


def dump(out: Path) -> int:
    res = {"rows": {}, "defs": {}, "sents": {}}
    for cfgp in sorted((ROOT / "topics").glob("*.json")):
        slug = cfgp.stem
        rp = ROOT / "cache" / slug / "records.json"
        if not rp.exists():
            continue
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        recs = {str(r.get("id")): r for r in json.loads(rp.read_text(encoding="utf-8")).get("records") or []}
        specs = {o["name"]: o for o in _outcomes(cfg)}
        for rid, r in recs.items():
            ab = r.get("abstract") or ""
            res["defs"][f"{slug}|{rid}"] = [[d["span"][:160], sorted(d["components"]), sorted(d.get("excluded") or [])]
                                            for d in te._definition_sentences(ab)]
            for i, x in enumerate(extract._sentences(extract._norm(ab))):
                res["sents"][f"{slug}|{rid}|{i}"] = sorted(te._components_from_text(x))
        rv = ROOT / "docs" / "reviews" / slug / "review.json"
        if not rv.exists():
            continue
        review = json.loads(rv.read_text(encoding="utf-8"))
        for o in review.get("outcomes") or []:
            spec = specs.get(o.get("name")) or {"name": o.get("name")}
            rows = [("pooled", t) for t in o.get("trials") or []] + \
                   [("absent", t) for t in o.get("declared_absent_trials") or []]
            for kind, t in rows:
                pid = _pid(t.get("id") or t.get("label"))
                src = t.get("source") or ""
                rec = recs.get(pid)
                if not src or rec is None:
                    continue
                c = te.classify_bound(spec, rec.get("abstract") or "", src)
                v = te._class_verdict(spec, c["target_endpoint_class"], c.get("extra_components"),
                                      c.get("missing_components"), spec.get("name", ""), c.get("endpoint_binding_reason"))
                res["rows"][f"{slug}|{o.get('name')}|{pid}|{kind}"] = {
                    "class": c["target_endpoint_class"], "includes": c.get("target_components"),
                    "excludes": c.get("excluded_components") or [], "verdict": v.get("verdict"),
                    "admissible": v.get("admissible"), "definition_span": (c.get("endpoint_definition_span") or "")[:200]}
    out.write_text(json.dumps(res, ensure_ascii=False, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    print(f"dumped {out}: " + ", ".join(f"{k} {len(v)}" for k, v in res.items()))
    return 0


def diff(before: Path, after: Path, out: Path | None) -> int:
    b = json.loads(before.read_text(encoding="utf-8"))
    a = json.loads(after.read_text(encoding="utf-8"))
    rep = {}
    for sec in b:
        keys = sorted(set(b[sec]) | set(a.get(sec, {})))
        ch = [{"key": k, "before": b[sec].get(k), "after": a.get(sec, {}).get(k)} for k in keys
              if b[sec].get(k) != a.get(sec, {}).get(k)]
        rep[sec] = {"n": len(ch), "of": len(keys), "changes": ch}
        extra = ""
        if sec == "rows":
            flips = [c for c in ch if (c["before"] or {}).get("admissible") != (c["after"] or {}).get("admissible")]
            cls = [c for c in ch if (c["before"] or {}).get("class") != (c["after"] or {}).get("class")]
            rep[sec]["class_flips"] = len(cls)
            rep[sec]["admissibility_flips"] = len(flips)
            extra = f"; class flips {len(cls)}; admissibility flips {len(flips)}"
        print(f"{sec}: {len(ch)} of {len(keys)} change{extra}")
    if out:
        out.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "dump":
        sys.exit(dump(Path(sys.argv[2])))
    sys.exit(diff(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[5]) if len(sys.argv) > 5 else None))
