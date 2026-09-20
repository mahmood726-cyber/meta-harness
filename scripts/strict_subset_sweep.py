"""Strict-subset sweep: does any pooled row's bound measure TITLE name a strict subset of its outcome's own component set?

Both wrong published rows (dapagliflozin-hfpef-hosp / empagliflozin-hfpef-hosp, withdrawn 2026-09-19) share one property that needs
no binding logic to see: the registry measure title ('Subjects Included in the Endpoint of Cardiovascular Death') names a strict
subset of the clauses in the outcome's own NAME ('Composite cardiovascular death or worsening heart failure').

The comparison is LEXICON-FREE on purpose. The producer's pinned lexicon (harness/target_endpoint._components_from_text) maps
'worsening heart failure' to nothing, so under it the two-clause name collapses to {cardiovascular death} and the wrong title reads
as EXACT -- that collapse IS the mechanism of the defect, and a sweep built on it returns zero hits on the two known rows (measured
2026-09-20 before this rewrite). Here the outcome name is split on its coordinators ('or', 'and', ',', '/') after stripping
composite framing ('composite of', 'first occurrence of', 'time to', ...), and a clause is NAMED by the title when every content
word of the clause appears in the title (a bag of lowercase words; nothing else). A hit is: the title names >= 1 clause and misses
>= 1 clause. The lexicon's own reading is printed beside each row so the collapse is visible.

Two comparisons per row: TITLE (registry_title, else the row's definition span) and CLASS (the row's classified components).
Usage: python scripts/strict_subset_sweep.py [--ref <git ref>] [--json out.json]
"""
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import target_endpoint as te  # noqa: E402

_FRAMING = re.compile(r"\b(?:the )?(?:composite|composite outcome|composite end ?point|first occurrence|time to (?:the )?(?:first )?(?:occurrence|event)?|"
                      r"incidence|rate|risk|number|proportion|subjects? included in the end ?point|participants? with|patients? with|"
                      r"adjudicated|confirmed|primary|secondary|outcome|end ?point|event|events)\b(?:\s+of)?", re.I)
_SPLIT = re.compile(r"\s*(?:,|;|:|/|\bor\b|\band\b|\bplus\b)\s*", re.I)
_STOP = {"of", "the", "a", "an", "to", "for", "in", "from", "due", "with", "any", "cause", "causes", "nonfatal", "non-fatal", "fatal", "first",
         "all", "either", "both", "time", "adjudicated", "confirmed", "hospitalisation", "hospitalization", "hospitalisations", "hospitalizations",
         "major", "adverse", "events", "event", "non"}
_ABBREV = {"cv": ["cardiovascular"], "hf": ["heart", "failure"], "mi": ["myocardial", "infarction"], "hhf": ["heart", "failure"]}   # expansions, not judgements
_SYN = {"hospitalisation": "hospitalization", "hospitalisations": "hospitalization", "hospitalizations": "hospitalization",
        "haemorrhage": "hemorrhage", "cardio-vascular": "cardiovascular", "myocardial-infarction": "myocardial infarction"}


def words(text: str) -> set[str]:
    t = re.sub(r"[()\[\]]", " ", (text or "").lower()).replace("-", " ")     # 'heart-failure' == 'heart failure'; 'stroke--had' is two words
    out = set()
    for w in re.findall(r"[a-z]+", t):
        w = _SYN.get(w, w)
        if w in _ABBREV:
            out.update(_ABBREV[w]); continue
        if w not in _STOP:
            out.add(w)
    return out


def clauses(name: str) -> list[str]:
    body = _FRAMING.sub(" ", name or "")
    parts = [p.strip(" -:") for p in _SPLIT.split(body)]
    return [p for p in parts if words(p)]


def named_by(clause: str, title_words: set[str]) -> bool:
    cw = words(clause)
    return bool(cw) and cw <= title_words


def compare(name: str, title: str) -> dict:
    cl = clauses(name)
    tw = words(title)
    named = [c for c in cl if named_by(c, tw)]
    missed = [c for c in cl if not named_by(c, tw)]
    return {"clauses_of_outcome_name": cl, "named_by_title": named, "missed_by_title": missed,
            "strict_subset": bool(cl) and bool(named) and bool(missed) and len(cl) >= 2,
            "names_no_clause": bool(cl) and not named}


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


def sweep(ref: str | None) -> dict:
    rows, hits, collapsed, n_reviews = [], [], [], 0
    for slug, rev in reviews(ref):
        n_reviews += 1
        for o in rev.get("outcomes", []):
            name = o.get("name") or ""
            cl = clauses(name)
            lex = sorted(te._components_from_text(name) or [])
            if len(cl) >= 2 and len(lex) < len(cl):
                collapsed.append({"slug": slug, "outcome": name, "primary": bool(o.get("primary")), "clauses": cl, "lexicon_reading": lex,
                                  "pooled_rows": len(o.get("trials") or [])})
            for t in o.get("trials", []):
                title = t.get("registry_title") or ""
                defn = t.get("endpoint_definition_span") or ""
                tstring = title or defn
                tc = t.get("target_endpoint_components")
                if isinstance(tc, str):
                    try:
                        tc = json.loads(tc.replace("'", '"'))
                    except Exception:
                        tc = [tc]
                cls_string = " ; ".join(map(str, tc)) if isinstance(tc, list) else ""
                ct = compare(name, tstring) if tstring else None
                cc = compare(name, cls_string) if cls_string else None
                # an opaque registry title ('CEC Confirmed Composite Endpoints') names no clause; the enumeration then lives in the
                # measure description (the definition span) -- report which, never fold into a hit or a clear
                cd = compare(name, defn) if (title and defn) else None
                row = {"slug": slug, "outcome": name, "primary": bool(o.get("primary")), "trial": t.get("id"),
                       "provenance": t.get("provenance"), "endpoint_binding": t.get("endpoint_binding"), "target_endpoint_class": t.get("target_endpoint_class"),
                       "title_string": title or None, "definition_span_used_when_no_title": (None if title else (defn[:200] or None)),
                       "classified_components": tc if isinstance(tc, list) else None,
                       "TITLE": ct, "CLASS": cc, "DESCRIPTION_when_title_names_nothing": (cd if (ct and ct["names_no_clause"]) else None),
                       "lexicon_reading_of_outcome_name": lex,
                       "declared_components_in_topic": o.get("components") or o.get("canonical_components")}
                rows.append(row)
                if (ct and ct["strict_subset"]) or (cc and cc["strict_subset"]):
                    hits.append(row)
    return {"ref": ref or "WORKING_TREE", "reviews": n_reviews, "rows_swept": len(rows),
            "rows_with_a_title": sum(1 for r in rows if r["title_string"]),
            "rows_with_title_or_definition": sum(1 for r in rows if r["TITLE"]),
            "rows_with_classified_components": sum(1 for r in rows if r["CLASS"]),
            "outcomes_with_two_or_more_clauses": sum(1 for r in rows if r["TITLE"] and len(r["TITLE"]["clauses_of_outcome_name"]) >= 2),
            "hits": hits,
            "registry_titles_naming_no_clause": [{"slug": r["slug"], "outcome": r["outcome"], "trial": r["trial"], "title": r["title_string"],
                                                 "description_names": (r["DESCRIPTION_when_title_names_nothing"] or {}).get("named_by_title"),
                                                 "description_misses": (r["DESCRIPTION_when_title_names_nothing"] or {}).get("missed_by_title")}
                                                for r in rows if r["title_string"] and r["TITLE"] and r["TITLE"]["names_no_clause"]],
            "rows_not_swept": {"count": sum(1 for r in rows if not r["TITLE"] and not r["CLASS"]),
                               "why": "no registry title, no definition span, no classified components -- rows bound by no span (unbound_legacy) carry nothing to compare",
                               "primary_rows_among_them": sum(1 for r in rows if not r["TITLE"] and not r["CLASS"] and r["primary"])},
            "outcome_names_the_lexicon_collapses": collapsed,
            "method": "lexicon-free: outcome name split on coordinators after stripping composite framing; a clause is named when its content words are all in the title",
            "rows": rows}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    out = sweep(a.ref)
    print(f"strict-subset sweep @ {out['ref']}: {out['reviews']} reviews, {out['rows_swept']} pooled rows; {out['rows_with_a_title']} with a registry title, "
          f"{out['rows_with_title_or_definition']} with a title or definition span, {out['rows_with_classified_components']} with classified components; "
          f"{out['outcomes_with_two_or_more_clauses']} rows whose outcome name has >= 2 clauses; HITS {len(out['hits'])}")
    for h in out["hits"]:
        which = [k for k in ("TITLE", "CLASS") if h[k] and h[k]["strict_subset"]]
        print(f"  HIT {h['slug']} | {h['outcome']} | {h['trial']} | primary={h['primary']} | {'+'.join(which)} | class={h['target_endpoint_class']} binding={h['endpoint_binding']}")
        print(f"      string: {h['title_string'] or h['definition_span_used_when_no_title']}")
        c = h["TITLE"] or h["CLASS"]
        print(f"      named {c['named_by_title']} | missed {c['missed_by_title']} | lexicon reads the name as {h['lexicon_reading_of_outcome_name']} | declared {h['declared_components_in_topic']}")
    print(f"registry titles naming no clause of the outcome name: {len(out['registry_titles_naming_no_clause'])}")
    for r in out["registry_titles_naming_no_clause"]:
        print(f"  {r['slug']} | {r['trial']} | title: {r['title']} | description names {r['description_names']} misses {r['description_misses']}")
    print(f"rows not swept: {out['rows_not_swept']['count']} ({out['rows_not_swept']['primary_rows_among_them']} primary) -- {out['rows_not_swept']['why']}")
    print(f"outcome names the pinned lexicon collapses (>= 2 clauses, fewer lexicon components): {len(out['outcome_names_the_lexicon_collapses'])}")
    for c in out["outcome_names_the_lexicon_collapses"]:
        print(f"  {c['slug']} | {c['outcome']} | clauses {c['clauses']} -> lexicon {c['lexicon_reading']} | pooled rows {c['pooled_rows']} | primary={c['primary']}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
