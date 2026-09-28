"""Corpus-wide radius of lane NR's V1.0.1 regex fixes (read-only; writes only the dump/diff it is told to).

  python scripts/nr_v101_radius.py dump OUT.json        every value the fixed readers produce, from this tree's harness
  python scripts/nr_v101_radius.py diff BEFORE.json AFTER.json [--out REPORT.json]

What is dumped (keys are stable across trees, so BEFORE and AFTER diff exactly):
  extract   harness.extract.extract_trial on every cached record x every declared outcome of its topic, called as
            harness/pipeline.py:1197 calls it (abstract, keywords, intervention/comparator terms, declared_composite,
            estimand). SERVED when the record is a trial row of that outcome on the committed page.
  arm_ns    harness.extract._arm_ns per cached record (the per-arm sizes the count path pairs with).
  fu_compat harness.compat_check.derive_trial_dimensions(...)["follow_up_window"] for every trial row (pooled AND
            declared-absent) of every outcome of every committed page, with the topic's definition audit.
  fu_adm    harness.eligibility_chain._follow_up_value(pid, _record_text(rec, trial)) for the same rows.
  ep_adm    harness.eligibility_chain._endpoint_definition(pid, text)["surveillance_window"] for the same rows.
The count path's refusal code is read from extract_trial's reason text exactly as harness/absence.py reads it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import compat_check, eligibility_chain, extract  # noqa: E402


def _outcomes(cfg):
    return [cfg["primary_outcome"]] + list(cfg.get("secondary_outcomes") or []) + list(cfg.get("harm_outcomes") or [])


def _norm(v):
    if isinstance(v, dict):
        return {k: _norm(x) for k, x in sorted(v.items()) if k != "source"}
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    return v


def dump(out: Path) -> int:
    res = {"extract": {}, "arm_ns": {}, "fu_compat": {}, "fu_adm": {}, "ep_adm": {}}
    for cfgp in sorted((ROOT / "topics").glob("*.json")):
        slug = cfgp.stem
        rp = ROOT / "cache" / slug / "records.json"
        if not rp.exists():
            continue
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        records = json.loads(rp.read_text(encoding="utf-8"))
        recs = records.get("records") or []
        interv, comp = cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or []
        rv = ROOT / "docs" / "reviews" / slug / "review.json"
        review = json.loads(rv.read_text(encoding="utf-8")) if rv.exists() else {}
        served = {}
        for o in review.get("outcomes") or []:
            served[o.get("name")] = {eligibility_chain._pid(t.get("id") or t.get("label")) for t in o.get("trials") or []}
        for r in recs:
            rid, ab = str(r.get("id")), r.get("abstract") or ""
            res["arm_ns"][f"{slug}|{rid}"] = extract._arm_ns(ab, interv, comp)
            for spec in _outcomes(cfg):
                ex = extract.extract_trial(ab, spec["keywords"], interv, comp,
                                           declared_composite=extract.declared_is_composite(spec.get("name", "")),
                                           estimand=spec.get("estimand"))
                res["extract"][f"{slug}|{rid}|{spec['name']}"] = {
                    "served": rid in served.get(spec["name"], set()), "value": _norm(ex),
                    "reason": ex.get("reason") if ex.get("absent") else None}
        rmap = compat_check._rec_map(records)
        audit = compat_check._topic_definition_audit(slug, review)
        for o in review.get("outcomes") or []:
            rows = [("pooled", t) for t in o.get("trials") or []] + \
                   [("absent", t) for t in o.get("declared_absent_trials") or []]
            for kind, t in rows:
                pid = eligibility_chain._pid(t.get("id") or t.get("label"))
                key = f"{slug}|{o.get('name')}|{pid}|{kind}"
                dims = compat_check.derive_trial_dimensions(review, o, t, records, audit)
                fu = dims["follow_up_window"]
                res["fu_compat"][key] = {"value": fu.get("value"), "source": fu.get("source"), "span": fu.get("span")}
                rec = rmap.get(pid) or {}
                text = eligibility_chain._record_text(rec, t)
                # exactly what admission_record passes in THIS tree (V1.0.1: the row's window span and its estimates; the
                # head tree: the raw result span, or nothing)
                if hasattr(compat_check, "_window_span"):
                    v, s = eligibility_chain._follow_up_value(pid, text, compat_check._window_span(t, str(o.get("name") or "")),
                                                              compat_check._row_estimates(t))
                elif hasattr(compat_check, "_result_span"):
                    v, s = eligibility_chain._follow_up_value(pid, text, compat_check._result_span(t))
                else:
                    v, s = eligibility_chain._follow_up_value(pid, text)
                res["fu_adm"][key] = {"value": v, "span": s}
                res["ep_adm"][key] = {"value": eligibility_chain._endpoint_definition(pid, text).get("surveillance_window")}
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
        if sec == "extract":
            srv = [c for c in ch if (c["before"] or {}).get("served") or (c["after"] or {}).get("served")]
            refusals_b = sum(1 for k in keys if (b[sec].get(k) or {}).get("reason"))
            rep[sec]["served_changes"] = len(srv)
            rep[sec]["refusals_before"] = refusals_b
            rep[sec]["refusals_after"] = sum(1 for k in keys if (a[sec].get(k) or {}).get("reason"))
            rep[sec]["refusal_to_value"] = sum(1 for c in ch if (c["before"] or {}).get("reason") and not (c["after"] or {}).get("reason"))
            rep[sec]["value_to_refusal"] = sum(1 for c in ch if not (c["before"] or {}).get("reason") and (c["after"] or {}).get("reason"))
        print(f"{sec}: {len(ch)} of {len(keys)} change" + (
            f"; served {rep[sec]['served_changes']}; refusals {rep[sec]['refusals_before']} -> {rep[sec]['refusals_after']}"
            f" (refusal->value {rep[sec]['refusal_to_value']}, value->refusal {rep[sec]['value_to_refusal']})"
            if sec == "extract" else ""))
    if out:
        out.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    if cmd == "dump":
        sys.exit(dump(Path(sys.argv[2])))
    sys.exit(diff(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[5]) if len(sys.argv) > 5 else None))
