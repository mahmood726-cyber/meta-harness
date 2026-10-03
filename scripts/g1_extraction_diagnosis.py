"""DIAGNOSE the class EXTRACTION:OUTCOME_NOT_IN_SOURCE trial by trial, deterministically (no model): which route could
supply the number, and what each route says now.

For every comparator trial blocked EXTRACTION:* in a tracker file this lane computes (lane-owned topics skipped):
  held       abstract / PMC OA text (outputs/k_gap/_ft) / held cache/<slug>/ft_<pmid>.txt / Unpaywall copy
  fulltext   harness.pipeline._fulltext_extract on each held text, the topic's registered spec: admitted value, or
             the refusal reason (the same rung the pool uses)
  registry   the tracker's AACT registry binding (BINDABLE / REFUSED + gate / NO_POSTED_RESULTS)
  second     non-comparator secondary-meta rows for the trial (state, route)
  route      the FIRST route that can close it: FULLTEXT_ADMITS / REGISTRY_BINDABLE / SECOND_META_VERIFIED /
             TEXT_HELD_NOT_ADMITTED (an extractor class to fix) / NO_OPEN_SOURCE_HELD (acquisition)

    python scripts/g1_extraction_diagnosis.py   -> outputs/k_gap/extraction_diagnosis.json
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "outputs", "k_gap")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def held_texts(slug, pmid, rec):
    out = []
    for ref, p in (("PMC_OA", os.path.join(OUT, "_ft", f"{pmid}.txt")),
                   ("HELD_CACHE_FT", os.path.join(ROOT, "cache", slug, f"ft_{pmid}.txt"))):
        if os.path.exists(p) and os.path.getsize(p) > 0:
            out.append((ref, open(p, encoding="utf-8", errors="replace").read()))
    doi = ((rec or {}).get("doi") or "").lower()
    if doi:
        up = os.path.join(OUT, "_upw", hashlib.sha1(doi.encode()).hexdigest()[:16] + ".txt")
        if os.path.exists(up) and os.path.getsize(up) > 0:
            from harness import fulltext as F
            out.append(("UNPAYWALL", F.UNSTRUCTURED_MARKER + "\n" + open(up, encoding="utf-8", errors="replace").read()))
    return out


def main():
    from harness import extract, pipeline
    lanes = set(_j(os.path.join(OUT, "g1_lanes.json")))
    mrec = _j(os.path.join(OUT, "member_records.json"))
    rows, tally = [], Counter()
    for f in sorted(os.listdir(os.path.join(OUT, "g1"))):
        if not f.endswith(".json") or f[:-5] in lanes:
            continue
        o = _j(os.path.join(OUT, "g1", f))
        slug = o["slug"]
        cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
        spec = dict(cfg["primary_outcome"])
        recs = {str(r.get("id")): r for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", [])}
        sec = _j(os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json")).get("rows", []) \
            if os.path.exists(os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json")) else []
        for x in o["trials"]:
            if not str(x.get("blocker") or "").startswith("EXTRACTION"):
                continue
            pmid = str((x.get("family") or "")).replace("PMID ", "") or ((x.get("seeded_funnel") or {}).get("pmid"))
            rec = recs.get(pmid) or mrec.get(pmid)
            texts = held_texts(slug, pmid, rec)
            ft = []
            for ref, t in texts:
                try:
                    r = pipeline._fulltext_extract(t, spec, cfg["intervention_terms"], cfg["comparator_terms"],
                                                   extract.declared_is_composite(spec["name"]))
                except Exception as exc:  # noqa: BLE001 - a crash is a finding, recorded
                    r = {"absent": True, "reason": f"CRASH {type(exc).__name__}: {exc}"[:200]}
                ft.append({"source": ref, "chars": len(t),
                           **({"admitted": {k: r.get(k) for k in ("ai", "n1i", "ci", "n2i", "effect", "ci_low",
                                                                    "ci_high", "scale") if r.get(k) is not None},
                               "span": (r.get("source") or "")[:240]} if not r.get("absent")
                              else {"refused": (r.get("reason") or "")[:200]})})
            rb = x.get("registry_binding") or {}
            fam = x.get("family")
            sm_rows = [{"meta": r["meta_pmid"], "state": r["state"]} for r in sec
                       if r.get("family_id") == fam and r["meta_pmid"] != o["comparator_pmid"]]
            if any("admitted" in z for z in ft):
                route = "FULLTEXT_ADMITS"
            elif rb.get("state") == "BINDABLE":
                route = "REGISTRY_BINDABLE"
            elif any(r["state"] in ("PRIMARY_VERIFIED", "TWO_SOURCE_VERIFIED") for r in sm_rows):
                route = "SECOND_META_VERIFIED"
            elif texts:
                route = "TEXT_HELD_NOT_ADMITTED"
            else:
                route = "NO_OPEN_SOURCE_HELD"
            tally[route] += 1
            rows.append({"slug": slug, "label": x["label"], "pmid": pmid, "blocker": x["blocker"], "route": route,
                         "abstract_held": bool(rec and rec.get("abstract")), "texts": [z for z in ft],
                         "registry": {"state": rb.get("state"), "gates": sorted({c.get("gate") or "BINDABLE"
                                                                                 for c in rb.get("candidates") or []})},
                         "second_meta": sm_rows})
    out = {"n": len(rows), "by_route": dict(tally), "rows": rows}
    with open(os.path.join(OUT, "extraction_diagnosis.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({"n": out["n"], "by_route": out["by_route"]}))
    refusals = Counter(re.sub(r"\d+", "#", z.get("refused", ""))[:90] for r in rows for z in r["texts"] if "refused" in z)
    for k, v in refusals.most_common(8):
        print(v, k)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
