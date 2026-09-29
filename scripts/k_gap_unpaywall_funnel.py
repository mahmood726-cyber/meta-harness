"""Unpaywall FUNNEL, trial by trial: found -> reaches extraction -> fetched -> parsed -> result located -> admitted.

The k-gap table counted 'an Unpaywall OA copy exists' per comparator trial; the adapter closed 1. This script puts
an n at every step so the drop is attributable, never averaged away:

  S0 FOUND            the table row has an is_oa Unpaywall location for one of the trial's DOIs
  S1 REACHES_EXTRACT  our pipeline got the trial as far as extraction (declared absent from the primary pool);
                      otherwise the copy cannot help and the blocker is upstream (identification / screening / scope)
  S2 FETCH_ATTEMPTED  the DOI went through kgap.unpaywall_text (the index holds it)
  S3 TEXT_PARSED      >= 3000 chars of typed text (PDF via pypdf, else HTML); else the recorded per-URL reason
  S4 RESULT_LOCATED   with the text added, the pipeline found a candidate for the primary outcome (the declared-
                      absent reason changed away from OUTCOME_NOT_IN_SOURCE, or the trial was admitted)
  S5 ADMITTED         the trial is in the counterfactual primary pool

    python scripts/k_gap_unpaywall_funnel.py [--reprobe]
--reprobe re-fetches DOIs whose cached result is NO_OA_TEXT without a recorded reason (network), so each failure
gets its per-URL status. Writes outputs/k_gap/unpaywall_funnel.json.
"""
from __future__ import annotations

import hashlib
import importlib
import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))   # AFTER ROOT: scripts/kgap.py must not shadow the kgap package
from kgap import k_gap  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
UPW_DIR = os.path.join(OUT, "_upw")
UPW_IDX = os.path.join(OUT, "unpaywall_text_index.json")
UPSTREAM = {"IDENTIFICATION": "S1_BLOCKED_IDENTIFICATION", "SCREEN_OR_ELIGIBILITY": "S1_BLOCKED_SCREENING",
            "UNRESOLVED_IDENTITY": "S1_BLOCKED_IDENTITY_UNRESOLVED", "SCOPE_MISMATCH": "S1_BLOCKED_SCOPE",
            "MEASURE_MISMATCH": "S1_BLOCKED_MEASURE", "POOLED": "ALREADY_POOLED"}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def oa_dois(row):
    return sorted({(u.get("doi") or "").lower() for u in (row.get("unpaywall") or [])
                   if isinstance(u, dict) and u.get("is_oa") and u.get("doi")})


def why_no_text(entry):
    """The recorded reason a found OA copy gave no usable text, from the per-URL attempts."""
    tried = entry.get("tried")
    if tried is None:
        return "REASON_NOT_RECORDED"
    if not tried:
        return "NO_OA_LOCATION_URL" if entry.get("n_oa_locations", 1) else "UNPAYWALL_LISTS_NO_OA_LOCATION"
    codes = []
    for t in tried:
        e = t.get("error") or ""
        if e:
            codes.append("HTTP_403" if "403" in e else "HTTP_404" if "404" in e else "HTTP_429" if "429" in e
                         else "TIMEOUT" if "timed out" in e.lower() else "FETCH_ERROR")
        elif t.get("kind") == "PDF":
            codes.append("PDF_TEXT_UNDER_3000" if t.get("text_bytes", 0) else "PDF_NO_TEXT_LAYER")
        else:
            codes.append("HTML_TEXT_UNDER_3000")      # landing page / JS shell / abstract-only page
    # the most informative code among the locations tried (a fetched short page beats a refused one)
    for c in ("PDF_NO_TEXT_LAYER", "PDF_TEXT_UNDER_3000", "HTML_TEXT_UNDER_3000", "HTTP_403", "HTTP_429",
              "HTTP_404", "TIMEOUT", "FETCH_ERROR"):
        if c in codes:
            return c
    return "UNKNOWN"


def reprobe(idx):
    n = 0
    for doi, e in list(idx.items()):
        if e.get("state") == "NO_OA_TEXT" and e.get("tried") is None:
            fp = os.path.join(UPW_DIR, hashlib.sha1(doi.encode("utf-8")).hexdigest()[:16] + ".txt")
            if os.path.exists(fp) and os.path.getsize(fp) == 0:
                os.remove(fp)                         # an empty cached result: re-fetch to record why
            k_gap.unpaywall_text(doi, UPW_DIR, UPW_IDX)
            n += 1
    print("reprobed", n, flush=True)


def main(argv):
    idx = _j(UPW_IDX) if os.path.exists(UPW_IDX) else {}
    if "--reprobe" in argv:
        reprobe(idx)
        idx = _j(UPW_IDX)
    cf = importlib.import_module("k_gap_counterfactual")
    from harness import fulltext as _ftm
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    rows = [r for r in t["trials"] if oa_dois(r)]
    by_slug = {}
    for r in rows:
        by_slug.setdefault(r["slug"], []).append(r)
    out_rows, stage = [], Counter()
    for slug, rs in sorted(by_slug.items()):
        rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
        doi_of = {(x.get("doi") or "").strip().lower(): x.get("id") for x in rj.get("records", [])}
        base_core = cf.build(slug)
        prim = next((o for o in base_core["outcomes"] if o.get("primary")), {})
        pooled = {str(x.get("id", "")).replace("PMID ", "") for x in prim.get("trials", [])}
        absent = {str(d.get("id", "")).replace("PMID ", ""): d.get("reason_code")
                  for d in prim.get("declared_absent_trials", [])}
        # the S4/S5 counterfactual: every parsed OA text for this topic's declared-absent trials, added at once
        extra = {}
        for r in rs:
            for d in oa_dois(r):
                p = doi_of.get(d)
                if p in absent and d not in idx and "--reprobe" in argv:
                    # a declared-absent trial whose OA DOI the adapter never tried: try it, or S2 measures reach
                    k_gap.unpaywall_text(d, UPW_DIR, UPW_IDX)
                    idx.update(_j(UPW_IDX))
                e = idx.get(d) or {}
                if p in absent and e.get("state") == "OA_TEXT":
                    u = k_gap.unpaywall_text(d, UPW_DIR, UPW_IDX, offline=True)
                    if u.get("text"):
                        extra[p] = _ftm.UNSTRUCTURED_MARKER + "\n" + u["text"]
        cfc = cf.build(slug, extra_fulltext=extra) if extra else base_core
        cprim = next((o for o in cfc["outcomes"] if o.get("primary")), {})
        cpooled = {str(x.get("id", "")).replace("PMID ", "") for x in cprim.get("trials", [])}
        cabsent = {str(d.get("id", "")).replace("PMID ", ""): d.get("reason_code")
                   for d in cprim.get("declared_absent_trials", [])}
        for r in rs:
            dois = oa_dois(r)
            ours = [doi_of.get(d) for d in dois if doi_of.get(d)]
            rec = {"slug": slug, "label": r["label"], "gap_class": r["gap_class"], "dois": dois, "our_pmids": ours}
            if r["gap_class"] in UPSTREAM:
                rec["stage"] = UPSTREAM[r["gap_class"]]
            elif not any(p in absent for p in ours):
                rec["stage"] = ("S1_NOT_DECLARED_ABSENT:" + ("POOLED" if any(p in pooled for p in ours)
                                                             else "OA_DOI_NOT_OUR_RECORD"))
            else:
                p = next(p for p in ours if p in absent)
                d = next(d for d in dois if doi_of.get(d) == p)
                e = idx.get(d)
                rec.update({"pmid": p, "doi": d, "reason_before": absent[p]})
                if e is None:
                    rec["stage"] = "S2_FETCH_NOT_ATTEMPTED"
                elif e.get("state") != "OA_TEXT":
                    rec["stage"] = "S3_NO_TEXT:" + (why_no_text(e) if e.get("state") == "NO_OA_TEXT" else e.get("state"))
                    rec["host_type"] = e.get("host_type")
                elif p in cpooled:
                    rec["stage"] = "S5_ADMITTED"
                elif cabsent.get(p) != absent[p]:
                    rec["stage"] = "S4_LOCATED_NOT_ADMITTED:" + str(cabsent.get(p))
                else:
                    rec["stage"] = "S4_NOT_LOCATED:" + str(cabsent.get(p))
                rec["reason_after"] = cabsent.get(p)
            stage[rec["stage"]] += 1
            out_rows.append(rec)
        print(slug, dict(Counter(x["stage"] for x in out_rows if x["slug"] == slug)), flush=True)
    top = Counter(s.split(":")[0] for s in stage.elements())
    out = {"n_rows_found": len(out_rows), "by_stage": dict(sorted(stage.items())), "by_step": dict(sorted(top.items())),
           "rows": out_rows}
    with open(os.path.join(OUT, "unpaywall_funnel.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n_rows_found", "by_step", "by_stage")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
