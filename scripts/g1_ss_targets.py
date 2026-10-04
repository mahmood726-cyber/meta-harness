"""SECONDARY_SINGLE supply: find independent open-access metas whose per-trial forest plots can give rows for the
comparator trials a topic still lacks, then hand them to the dual-model forest reader (g1_forest_reader --ss-targets).

  targets   the k-gap tracker's trials routed UNVERIFIED or NO_ROW, read at a PINNED commit of acq/k-gap
            (outputs/k_gap/g1/<slug>.json via `git show <sha>:...`; the sha is recorded); each target's identifier is
            its tracker `family` (a PMID or an NCT number)
  search    Europe PMC, open-access full text in Europe PMC, titled a meta-analysis:
              PMID  -> CITES:<pmid>_MED            (the meta's reference list cites the trial's report)
              NCT   -> "<nct>"                     (the registration number appears in the meta's full text)
            every query is recorded (url, http status, response sha256, hits) in
            registry/model_proposals/g1_ss_search/<slug>.json; offline runs read the record
  select    rank candidate metas by the number of DISTINCT target trials they cite; never the topic's comparator
            (anti-circularity: SECONDARY_SINGLE rows come from a meta that is not the comparator); keep the top
            --per-topic (default 3) citing >= 1 target, preferring metas not already read by the forest reader
  output    registry/model_proposals/g1_ss_selection.json: {slug: {pinned_ref, targets, selected: [pmid...],
            ranked: [...]}} -- frozen once written; the reader prompts replay from it

    python scripts/g1_ss_targets.py --ref <sha> --run [--per-topic 3] SLUG ...
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402

SEARCH_DIR = os.path.join(ROOT, "registry", "model_proposals", "g1_ss_search")
SELECTION = os.path.join(ROOT, "registry", "model_proposals", "g1_ss_selection.json")
TARGET_ROUTES = ("UNVERIFIED", "NO_ROW")
META_TITLE = '(TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"metaanalysis" OR TITLE:"meta-analyses")'
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def _git_json(ref, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{path}"], capture_output=True, encoding="utf-8")
    if r.returncode != 0:
        raise FileNotFoundError(f"{ref}:{path}")
    return json.loads(r.stdout)


def targets(slug, ref):
    """[(label, kind, id)] -- the tracker's trials routed UNVERIFIED / NO_ROW, with their family identifier (or None)."""
    d = _git_json(ref, f"outputs/k_gap/g1/{slug}.json")
    out = []
    for t in d.get("trials") or []:
        if t.get("route") not in TARGET_ROUTES:
            continue
        fam = str(t.get("family") or "")
        m = re.fullmatch(r"PMID (\d+)", fam)
        n = re.search(r"NCT\d{8}", fam + " " + str(t.get("label") or ""))
        out.append((t["label"], "PMID", m.group(1)) if m else (t["label"], "NCT", n.group(0)) if n else
                   (t["label"], None, None))
    return out


# the WIDE pass (4-5 Oct): systematic reviews and anything Europe PMC types as a meta-analysis, whatever the title
META_WIDE = ('(TITLE:"systematic review" OR TITLE:"pooled analysis" OR PUB_TYPE:"meta-analysis" OR '
             'PUB_TYPE:"systematic-review")')


def query_of(kind, ident, wide=False):
    q = f"CITES:{ident}_MED" if kind == "PMID" else f'"{ident}"'
    return f"{q} AND OPEN_ACCESS:y AND IN_EPMC:y AND {META_WIDE if wide else META_TITLE}"


def search(q, run, rec):
    """Hits [(pmid, title)] for one query; recorded in rec[q]."""
    if q in rec:
        return [tuple(h) for h in rec[q]["hits"]]
    if not run:
        return []
    from harness import http
    hits, cursor, pages = [], "*", []
    for _ in range(4):                                       # <= 4000 hits: ample for a CITES query on one trial
        try:
            st, b = http.get_raw(EPMC, {"query": q, "format": "json", "pageSize": "1000", "resultType": "lite",
                                        "cursorMark": cursor}, tries=3, timeout=90)
            d = json.loads(b.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - recorded; never fatal
            pages.append({"cursor": cursor, "error": type(exc).__name__})
            break
        pages.append({"cursor": cursor, "http_status": st, "sha256": hashlib.sha256(b).hexdigest()})
        res = (d.get("resultList") or {}).get("result") or []
        hits += [(r["pmid"], (r.get("title") or "")[:200]) for r in res if r.get("pmid")]
        nxt = d.get("nextCursorMark")
        if not res or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.2)
    rec[q] = {"pages": pages, "hits": hits, "fetched": time.strftime("%Y-%m-%d")}
    return hits


def already_read():
    if not os.path.exists(gfr.OUT):
        return set()
    o = gfr._j(gfr.OUT)
    return {k.split("::")[1] for k in (o.get("meta_results") or {}) if "::" in k} | \
           {k.split("::")[1] for k in (o.get("meta_skipped") or {}) if "::" in k}


def select(slug, ref, run, per_topic=3, wide=False):
    comp = gfr.comparator_of(slug)
    rp = os.path.join(SEARCH_DIR, f"{slug}.json")
    rec = gfr._j(rp) if os.path.exists(rp) else {}
    tg = targets(slug, ref)
    cover, titles = {}, {}
    for label, kind, ident in tg:
        if not kind:
            continue
        for pm, title in search(query_of(kind, ident), run, rec) + (search(query_of(kind, ident, True), run, rec)
                                                                    if wide else []):
            cover.setdefault(pm, set()).add(label)
            titles[pm] = title
    os.makedirs(SEARCH_DIR, exist_ok=True)
    gfr._save(rp, rec)
    seen = already_read()
    ranked = sorted(((pm, sorted(labs)) for pm, labs in cover.items() if pm != comp),
                    key=lambda x: (-len(x[1]), x[0] in seen, x[0]))
    selected = [pm for pm, labs in ranked if pm not in seen][:per_topic]
    return {"pinned_ref": ref, "comparator": comp,
            "targets": [{"label": l, "id_kind": k, "id": i} for l, k, i in tg],
            "targets_without_identifier": [l for l, k, _ in tg if not k],
            "selected": selected,
            "ranked": [{"pmid": pm, "n_targets": len(labs), "targets": labs, "title": titles.get(pm),
                        "already_read": pm in seen} for pm, labs in ranked[:15]]}


def main(argv):
    run = "--run" in argv
    ref = argv[argv.index("--ref") + 1]
    per = int(argv[argv.index("--per-topic") + 1]) if "--per-topic" in argv else 3
    wide = "--wide" in argv
    global SELECTION
    if wide:                                   # the wide pass keeps its own frozen selection beside the first
        SELECTION = SELECTION.replace(".json", "_wide.json")
    skip = {ref, str(per)}
    slugs = [a for a in argv if not a.startswith("--") and a not in skip]
    sel = gfr._j(SELECTION) if os.path.exists(SELECTION) else {}
    for slug in slugs:
        if slug in sel and not "--reselect" in argv:
            print(slug, "FROZEN (already selected)", sel[slug]["selected"])
            continue
        sel[slug] = select(slug, ref, run, per, wide)
        r = sel[slug]
        print(f"{slug}: targets {len(r['targets'])} (no id {len(r['targets_without_identifier'])}); selected "
              f"{r['selected']}")
        for x in r["ranked"][:6]:
            print(f"   {x['pmid']} n={x['n_targets']} read={x['already_read']} {x['title'][:90]}")
    gfr._save(SELECTION, sel)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
