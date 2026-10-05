"""CITING-META TARGETS for the forest reader (5 Oct night): for every UNMATCHED comparator trial of a topic, the open-access
meta-analyses that CITE the trial's own report (Europe PMC CITES:<pmid>_MED, title says meta-analysis / systematic review,
OPEN_ACCESS:y; query + hit count + response sha256 recorded), and in each of them the figures that can pass admission --
decided BEFORE any model call, from the meta's own words only:

  kind          not a flow / PRISMA / funnel / bias / network / ranking / meta-regression / trial-sequential figure
  intervention  the caption or the meta's title names the topic's drug or listed class (secondary_meta_build
                .lane_intervention_refusal: the 35343397 class)
  admission     g1_admission_check.prefilter: the caption is the topic's outcome, the protocol's timepoint is stated by
                the caption or as the meta's single timepoint, the protocol's measure is stated

The k-gap two-source sweep caps discovery at 10 metas per trial and selects figures by caption words alone; this widens
discovery and narrows reading to figures that can count. Every downstream gate is unchanged (dual-model agreement,
reconstruction of the printed pool under the stated model, admission, cross-check, family, screen).

    python scripts/g1_citing_targets.py [--run] SLUG ...     -> registry/model_proposals/g1_citing_targets.json
    python scripts/g1_forest_reader.py --run --citing SLUG ... (dual-reads the recorded candidates)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

OUT = os.path.join(ROOT, "registry", "model_proposals", "g1_citing_targets.json")
META_TITLE = '(TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"meta-analyses" OR TITLE:"systematic review")'
NOT_A_RESULT_FIGURE = re.compile(r"\bflow\b|prisma|funnel|risk of bias|bias assessment|network (?:plot|diagram|geometry)|"
                                 r"network meta|\brank|sucra|meta-?regression|bubble|trial sequential|\bTSA\b|"
                                 r"search strategy|study selection|selection process", re.I)


def _j(p):
    return json.load(open(p, encoding="utf-8"))


def figure_candidates(slug, pmid, figs, title):
    """[(fig_id, caption)] -> the figures that can pass admission, before any read (see the module docstring)."""
    import g1_admission_check as ac
    import secondary_meta_build as smb
    terms = smb.topic_intervention_terms(slug)
    kept = []
    for fid, cap in figs:
        if not cap or NOT_A_RESULT_FIGURE.search(cap):
            continue
        if smb.lane_intervention_refusal(terms, cap, title):
            continue
        ok, why = ac.prefilter(slug, pmid, cap)
        if ok:
            kept.append({"fig_id": fid, "caption": cap[:300]})
    return kept


def citing(pmid, run, rec):
    """The OA metas citing one trial report: recorded query, hit count, response sha256, [pmid]."""
    if pmid in rec:
        return rec[pmid]
    if not run:
        return None
    from harness import http
    q = f"CITES:{pmid}_MED AND {META_TITLE} AND OPEN_ACCESS:y"
    st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                         {"query": q, "format": "json", "resultType": "lite", "pageSize": "200"}, tries=3)
    d = json.loads(b.decode("utf-8"))
    rec[pmid] = {"query": q, "hitCount": d.get("hitCount"), "sha256": hashlib.sha256(b).hexdigest(),
                 "metas": [r["pmid"] for r in (d.get("resultList") or {}).get("result") or [] if r.get("pmid")]}
    time.sleep(0.3)
    return rec[pmid]


def figures_of(pmid):
    import xml.etree.ElementTree as ET
    import g1_forest_reader as gfr
    jp = gfr.jats_path(pmid)
    if not jp:
        return None
    try:
        root = ET.parse(jp).getroot()
    except ET.ParseError:
        return None
    return [(f.get("id"), re.sub(r"\s+", " ", " ".join("".join(x.itertext()) for x in f.iter("caption"))).strip())
            for f in root.iter("fig")]


def unmatched_pmids(slug):
    """{label: [report pmids]} of the comparator trials the tracker file leaves unmatched (route not PRIMARY /
    TWO_SOURCE / SWEEP_*), from the k-gap table's identities."""
    import g1_tracker as gt
    tp = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json")
    if not os.path.exists(tp):
        return {}
    tr = _j(tp)
    open_labels = {x["label"][:60] for x in tr.get("trials") or [] if not gt.is_matched(x)}
    T = _j(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"))
    return {t["label"][:60]: [str(p) for p in t.get("pmids") or []]
            for t in T["trials"] if t["slug"] == slug and t["label"][:60] in open_labels and t.get("pmids")}


def discover(slug, run, rec):
    import g1_forest_reader as gfr
    from kgap import k_gap
    comp = str(gfr.comparator_of(slug))
    o = gfr._j(gfr.OUT) if os.path.exists(gfr.OUT) else {}
    held_keys = set((o.get("meta_results") or {})) | set((o.get("meta_skipped") or {}))
    cites, queries = {}, {}
    for lab, pmids in unmatched_pmids(slug).items():
        for pm in pmids:
            r = citing(pm, run, rec)
            if r:
                queries[pm] = {k: r[k] for k in ("query", "hitCount", "sha256")}
                for m in r["metas"]:
                    if m != comp:
                        cites.setdefault(m, set()).add(lab)
    cands, no_jats = [], []
    for m in sorted(cites):
        if run and not gfr.jats_path(m):
            k_gap.fetch_comparator_jats(m, gfr.FETCH_DATE)
        figs = figures_of(m)
        if figs is None:
            no_jats.append(m)
            continue
        for c in figure_candidates(slug, m, figs, gfr._meta_title(m, run)):
            key = f"{slug}::{m}::{c['fig_id']}"
            cands.append(dict(c, pmid=m, cites=sorted(cites[m]), already_read=key in held_keys))
    return {"comparator": comp, "queries": queries, "n_citing_metas": len(cites), "no_open_jats": no_jats,
            "candidates": cands}


def main(argv):
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")]
    out = _j(OUT) if os.path.exists(OUT) else {}
    rec = out.setdefault("_citing_queries", {})
    for s in slugs:
        out[s] = discover(s, run, rec)
        d = out[s]
        print(f"{s}: {d['n_citing_metas']} citing OA metas, {len(d['no_open_jats'])} without open JATS, "
              f"{len(d['candidates'])} admissible-looking figures ({sum(1 for c in d['candidates'] if not c['already_read'])} unread)")
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
