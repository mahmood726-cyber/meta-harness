"""Does the served corpus contain the audit's shape? (external audit 2026-09-20: a result acquired the WRONG
endpoint definition because two definitions shared one component set and the binder took the first.)

Rule (read from the held documents and the served review.json objects):
  held document   = cache/<slug>/records.json abstract of every trial the review names (pooled or declared
                    absent), plus cache/<slug>/ft_<pid>.txt / pmc_<pid>_fulltext.txt when held
  definition      = target_endpoint._definition_sentences(text): a sentence naming an endpoint, with a definition
                    cue, enumerating components; carries its reference identity (ordinal / timepoint / population)
  SHARED-SET PAIR = two definitions in one document with the SAME component set and DIFFERENT reference identity
                    (this is E01 / E02: same events, different follow-up or population) -- the shape that can bind wrong
  REFERENCED ROW  = a served row whose endpoint_result_span carries an ordinal or a timepoint / population reference
  EXPOSED ROW     = a referenced or bare row bound by definition (endpoint_binding names a definition span) in a
                    document holding a shared-set pair -- the rows the audit's finding could have touched

Populations (denominators printed): documents scanned; documents with >= 2 definitions; documents with a
shared-set pair (named); served rows bound by definition; exposed rows (named, with what the selection now says).

Usage: python scripts/endpoint_reference_sweep.py [--json out.json]
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import hand_binding, target_endpoint as te  # noqa: E402


def _documents(slug: str, pids: set[str]):
    p = ROOT / "cache" / slug / "records.json"
    if not p.exists():
        return
    data = json.load(open(p, encoding="utf-8"))
    lists = [data.get("records") or []] + [v for k, v in data.items() if k != "records" and isinstance(v, list)
                                           and v and all(isinstance(x, dict) and "abstract" in x for x in v)]
    for lst in lists:
        for r in lst:
            if str(r.get("id")) in pids and r.get("abstract"):
                yield f"cache/{slug}/records.json#PMID-{r['id']}", r["abstract"]
    for pid in sorted(pids):
        for name in (f"ft_{pid}.txt", f"pmc_{pid}_fulltext.txt"):
            fp = ROOT / "cache" / slug / name
            if fp.exists():
                doc = hand_binding.resolve_document(f"cache/{slug}/{name}")
                if doc:
                    yield f"cache/{slug}/{name}", hand_binding.prose_of(doc)


def sweep() -> dict:
    out = {"documents_scanned": 0, "documents_with_2plus_definitions": 0, "shared_set_pairs": [],
           "rows_bound_by_definition": 0, "referenced_rows": [], "exposed_rows": []}
    for rp in sorted(glob.glob(str(ROOT / "docs" / "reviews" / "*" / "review.json"))):
        rev = json.load(open(rp, encoding="utf-8"))
        slug = rev.get("slug") or Path(rp).parent.name
        pids = set()
        rows = []
        for o in rev.get("outcomes") or []:
            for t in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
                pid = str(t.get("id") or "").replace("PMID ", "")
                pids.add(pid)
                rows.append((o.get("name"), pid, t))
        pair_docs = {}
        for ref, text in _documents(slug, pids):
            out["documents_scanned"] += 1
            defs = te._definition_sentences(text)
            if len(defs) >= 2:
                out["documents_with_2plus_definitions"] += 1
            by_set: dict[frozenset, list] = {}
            for d in defs:
                by_set.setdefault(frozenset(d["components"]), []).append(d)
            for comps, group in by_set.items():
                idents = {(d.get("ordinal"), d.get("timepoint"), d.get("population")) for d in group}
                spans = {d["span"] for d in group}
                if len(spans) >= 2 and len(idents) >= 2:
                    pair = {"slug": slug, "document": ref, "components": sorted(comps),
                            "definitions": [{"span": d["span"][:200], "ordinal": d.get("ordinal"),
                                             "timepoint": d.get("timepoint"), "population": d.get("population")} for d in group]}
                    out["shared_set_pairs"].append(pair)
                    pair_docs[ref] = pair
        for oname, pid, t in rows:
            span = t.get("endpoint_result_span") or ""
            binding = t.get("endpoint_binding") or ""
            if "definition" in binding:
                out["rows_bound_by_definition"] += 1
            ref = te._reference_of(span) if span else {}
            referenced = bool(span) and bool(ref.get("ordinal") or ref.get("timepoint") or ref.get("population"))
            if referenced:
                out["referenced_rows"].append({"slug": slug, "outcome": oname, "trial": pid, "reference": ref,
                                               "span": span[:160], "binding": binding})
            held = [d for d in pair_docs if d.endswith(f"PMID-{pid}") or f"_{pid}" in d]
            if held and "definition" in binding:
                b = te.bind_result_span(next(text for r_, text in _documents(slug, {pid}) if r_ == held[0]), span)
                out["exposed_rows"].append({"slug": slug, "outcome": oname, "trial": pid, "document": held[0],
                                            "served_definition": (t.get("endpoint_definition_span") or "")[:160],
                                            "now": b.get("binding"), "now_definition": (b.get("endpoint_definition_span") or "")[:160],
                                            "now_reason": b.get("binding_reason"), "pooled": "endpoint_admissibility" in t})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    r = sweep()
    print(f"endpoint-reference sweep: documents scanned {r['documents_scanned']}; with >= 2 definitions "
          f"{r['documents_with_2plus_definitions']}; SHARED-SET PAIRS (same components, different reference) "
          f"{len(r['shared_set_pairs'])}; served rows bound by definition {r['rows_bound_by_definition']}; "
          f"referenced rows {len(r['referenced_rows'])}; EXPOSED rows {len(r['exposed_rows'])}")
    for p in r["shared_set_pairs"]:
        print(f"  PAIR {p['slug']} | {p['document']} | {', '.join(p['components'])}")
        for d in p["definitions"]:
            print(f"       ordinal={d['ordinal']} timepoint={d['timepoint']} population={d['population']} | {d['span'][:110]}")
    for e in r["exposed_rows"]:
        print(f"  EXPOSED {e['slug']} | {e['outcome'][:30]} | {e['trial']} | pooled={e['pooled']} | now {e['now']}: {str(e['now_reason'])[:100]}")
    for x in r["referenced_rows"][:40]:
        print(f"  REF {x['slug']} | {x['outcome'][:30]} | {x['trial']} | {x['reference']} | {x['span'][:80]}")
    if args.json:
        json.dump(r, open(args.json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("written", args.json)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main())
