"""R4 measurement (read-only): does harness.extract._parse_k lose a stated trial count because its FIRST _K match is a
word that is not a number ('well-powered RCTs', 'Randomized controlled trials comparing ...')?

For every topic, on the comparator abstract and full text the pipeline reads (harness/pipeline.py build_comparator_core
and the comparator block), compare the served rule (first match only) with the first match that parses to a count.
Where the config carries a source-verified comparator_k, the auto value is not served -- reported, not hidden.

  python scripts/measure_k_shadow.py   -> outputs/regex_layer/K_SHADOW.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import extract  # noqa: E402


def first_parseable(text: str):
    for m in extract._K.finditer(text or ""):
        tok = m.group(1).lower()
        v = int(tok) if tok.isdigit() else extract._WORDNUM.get(tok)
        if v is not None:
            return v, m.group(0)
    return None, None


def distinct_parseable(text: str) -> list:
    out = []
    for m in extract._K.finditer(text or ""):
        tok = m.group(1).lower()
        v = int(tok) if tok.isdigit() else extract._WORDNUM.get(tok)
        if v is not None and v not in out:
            out.append(v)
    return out


def main() -> int:
    rows = []
    for cfgp in sorted((ROOT / "topics").glob("*.json")):
        slug = cfgp.stem
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        rp = ROOT / "cache" / slug / "records.json"
        if not rp.exists() or not cfg.get("comparator_pmid"):
            continue
        recs = {str(r.get("id")): r for r in json.loads(rp.read_text(encoding="utf-8")).get("records") or []}
        comp_abs = (recs.get(str(cfg["comparator_pmid"])) or {}).get("abstract") or ""
        fp = ROOT / "cache" / slug / "comparator_fulltext.txt"
        comp_full = fp.read_text(encoding="utf-8", errors="replace") if fp.exists() else ""
        served = extract._parse_k(extract._norm(comp_abs)) or extract._parse_k(extract._norm(comp_full))
        alt_a, span_a = first_parseable(extract._norm(comp_abs))
        alt_f, span_f = first_parseable(extract._norm(comp_full))
        alt = alt_a or alt_f
        first = extract._K.search(extract._norm(comp_abs)) or extract._K.search(extract._norm(comp_full))
        rows.append({"slug": slug, "comparator_k_override": cfg.get("comparator_k"),
                     "served_rule_k": served, "first_parseable_k": alt,
                     "first_match": first.group(0) if first else None,
                     "first_parseable_match": span_a or span_f,
                     "differs": served != alt,
                     # R4: a count is usable only when the text states exactly ONE distinct count; more is ambiguous
                     "distinct_counts_abstract": distinct_parseable(extract._norm(comp_abs)),
                     "distinct_counts_fulltext": distinct_parseable(extract._norm(comp_full)),
                     "auto_value_served": cfg.get("comparator_k") is None})
    res = {"topics_with_comparator": len(rows), "differ": sum(r["differs"] for r in rows),
           "differ_where_auto_value_is_served": sum(r["differs"] and r["auto_value_served"] for r in rows), "rows": rows}
    out = ROOT / "outputs" / "regex_layer" / "K_SHADOW.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"topics {res['topics_with_comparator']}; differ {res['differ']}; "
          f"differ where the auto value is served {res['differ_where_auto_value_is_served']}")
    for r in rows:
        if r["differs"]:
            print(" ", r["slug"], r["served_rule_k"], "->", r["first_parseable_k"], "| override", r["comparator_k_override"],
                  "| distinct abs", r["distinct_counts_abstract"], "full", r["distinct_counts_fulltext"][:6],
                  "|", r["first_match"], "|", r["first_parseable_match"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
