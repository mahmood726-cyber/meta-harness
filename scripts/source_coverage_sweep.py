"""SOURCE COVERAGE SWEEP (E1, 11 Oct): every held source object, labelled from its own bytes (harness/source_coverage.py).

  documents  every held full-text / comparator file: cache/<slug>/ft_*, cache/<slug>/comparator_fulltext.txt,
             cache/<slug>/pmc_*_fulltext.txt, and cache/comparators/<pmid>/* text renderings.
  abstracts  every cached PubMed abstract that has a RETAINED acquisition (docs/acquisitions = the served bundle store,
             registry/source_acquisitions = E1 re-acquisitions): FULL_ABSTRACT / EXCERPT by the bundle's own preservation
             record. A cached abstract with no retained acquisition is UNKNOWN_COMPLETENESS -- never assumed full.

Writes registry/source_coverage.json (sorted, deterministic; no network). Nothing served reads it yet: wiring the
coverage into absence claims and the harms rung is a served change and goes to the captain as signing items.

    python scripts/source_coverage_sweep.py [--check]   (--check: exit 1 if the committed file differs from a fresh sweep)
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import source_coverage as sc  # noqa: E402

OUT = os.path.join(ROOT, "registry", "source_coverage.json")
DOC_GLOBS = ("cache/*/ft_*.txt", "cache/*/ft_*.xml", "cache/*/comparator_fulltext.txt", "cache/*/pmc_*_fulltext.txt",
             "cache/comparators/*/*fulltext*", "cache/comparators/*/*jats*.xml", "cache/comparators/*/body.txt")
STORES = ("docs/acquisitions", "registry/source_acquisitions")


def _rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def documents():
    files = sorted({_rel(f) for g in DOC_GLOBS for f in glob.glob(os.path.join(ROOT, g)) if not f.endswith(".meta.json")})
    out = {}
    for rel in files:
        raw = open(os.path.join(ROOT, rel), "rb").read()
        d = sc.label_document(raw)
        out[rel] = {"label": d["label"], "reason": d["reason"], "bundle_coverage": d["bundle_coverage"],
                    "sha256": sc.sha256(raw), "bytes": len(raw)}
    return out


def acquisitions():
    """{(slug, pmid): {path, sha256, store, date}} -- the LATEST retained EFetch response per record (append-only stores:
    a later dated directory is a newer acquisition, never an overwrite)."""
    out = {}
    for store in STORES:
        for man in sorted(glob.glob(os.path.join(ROOT, store, "*", "pubmed_efetch_*", "ACQUISITION.json"))):
            m = json.load(open(man, encoding="utf-8"))
            slug = m.get("slug") or os.path.basename(os.path.dirname(os.path.dirname(man)))
            for e in m.get("entries", []):
                pmid = (e.get("identifier") or {}).get("pmid")
                if pmid:
                    key = (slug, str(pmid))
                    cand = {"path": _rel(os.path.join(os.path.dirname(man), e["file"])), "sha256": e["sha256"],
                            "store": store, "date": m.get("acquisition_date")}
                    if key not in out or (cand["date"] or "") >= (out[key]["date"] or ""):
                        out[key] = cand
    return out


def abstracts(acq):
    import build_bundle
    out = {}
    for (slug, pmid), a in sorted(acq.items()):
        rp = os.path.join(ROOT, "cache", slug, "records.json")
        if not os.path.exists(rp):
            continue
        rec = next((r for r in json.load(open(rp, encoding="utf-8")).get("records") or [] if str(r.get("id")) == pmid), None)
        if rec is None:
            continue
        xml = open(os.path.join(ROOT, a["path"]), "rb").read()
        units = build_bundle.abstract_units(xml)
        if not units:
            lab = {"label": "METADATA" if not rec.get("abstract") else None,
                   "reason": "PUBMED_HAS_NO_ABSTRACT", "bundle_coverage": None}
        else:
            lab = sc.abstract_label(rec.get("abstract") or "", units)
        pres = lab.get("preservation") or {}
        out[f"cache/{slug}/records.json#PMID-{pmid}"] = {
            "label": lab["label"], "reason": lab["reason"], "bundle_coverage": lab["bundle_coverage"],
            "acquisition": a, "held_chars": len(rec.get("abstract") or ""),
            "missing_units": [u["text_if_missing"] for u in pres.get("units", []) if u.get("state") == "MISSING"]}
    return out


def sweep():
    docs = documents()
    abst = abstracts(acquisitions())
    return {"schema_version": 1, "writer": "scripts/source_coverage_sweep.py",
            "labels": {"vocabulary": list(sc.LABELS), "as_bundle_coverage_status": sc.BUNDLE_COVERAGE},
            "summary": {"documents": dict(sorted(Counter(v["label"] for v in docs.values()).items())),
                        "abstracts": dict(sorted(Counter(str(v["label"]) for v in abst.values()).items()))},
            "documents": docs, "abstracts": abst}


def main(argv):
    fresh = sweep()
    text = json.dumps(fresh, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in argv:
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        print("SOURCE_COVERAGE " + ("CURRENT" if old == text else "STALE"))
        return 0 if old == text else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(json.dumps(fresh["summary"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
