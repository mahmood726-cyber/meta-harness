"""Typed-estimand completeness, n of N, for the lane's scope (U23, S16 and M rows that are bound, not set aside).
A field counts as BOUND when the ruling's evidence carries a span for it OR the gap pass (evidence/gaps/SUMMARY.json)
VERIFIED one (gap_check verifies its spans against held bytes). Treatment strategy is not in the gap schema, so
only the ruling's evidence counts for it. Writes evidence/sweeps/typed_completeness.json and prints the counts."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import verify_records as V
ROOT = V.ROOT
FIELDS = ("analysis_set", "treatment_strategy", "follow_up")
SCOPE = ("U23", "S16", "M")


def main():
    wl = json.load(open(os.path.join(ROOT, "evidence/worklist.json"), encoding="utf-8"))["rows"]
    gaps = json.load(open(os.path.join(ROOT, "evidence/gaps/SUMMARY.json"), encoding="utf-8"))
    rows, n_scope, set_aside = {}, 0, []
    for w in wl:
        if w["kind"] not in SCOPE:
            continue
        n_scope += 1
        a = json.load(open(os.path.join(ROOT, f"evidence/adjudication/{w['key']}.json"), encoding="utf-8"))
        if a["ruling"] == "SET_ASIDE":
            set_aside.append(w["key"]); continue
        ev, g = a.get("evidence") or {}, gaps.get(w["key"]) or {}
        rows[w["key"]] = {f: ("RULING_SPAN" if ev.get(f) else
                              "GAP_VERIFIED" if isinstance(g.get(f), dict) and g[f].get("state") == "VERIFIED" else
                              (a.get("unbound_reasons") or {}).get(f) or "UNBOUND") for f in FIELDS}
    c = {f: collections.Counter("BOUND" if v[f] in ("RULING_SPAN", "GAP_VERIFIED") else
                                "NOT_STATED_IN_ANY_AUTHENTIC_SOURCE_FOUND" if str(v[f]).startswith("NOT_STATED") else "UNBOUND"
                                for v in rows.values()) for f in FIELDS}
    out = {"population": {"N_scope": n_scope, "set_aside": set_aside, "N": len(rows),
                          "denominator": "U23+S16+M rows bound (not set aside)"},
           "fields": {f: dict(c[f]) for f in FIELDS},
           "rows_fully_bound": sum(1 for v in rows.values() if all(x in ("RULING_SPAN", "GAP_VERIFIED") for x in v.values())),
           "rows": rows}
    json.dump(out, open(os.path.join(ROOT, "evidence/sweeps/typed_completeness.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print(f"N={len(rows)} (of {n_scope} in scope; set aside {len(set_aside)}); fully bound {out['rows_fully_bound']} of {len(rows)}; "
          + "; ".join(f"{f}: " + ", ".join(f"{k} {v}" for k, v in sorted(c[f].items())) for f in FIELDS))


if __name__ == "__main__":
    main()
