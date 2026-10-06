"""LICENCE GATE for recorded model calls (6 Oct: mc-60163e27 and 10 more locate records embedded full text that is not
CC BY / CC0 -- Unpaywall / held copies with no licence, or PMC copies under CC BY-NC / CC BY-NC-ND). A recorded prompt
is committed evidence, so a held text may enter a prompt only when its licence permits redistribution:

  ABSTRACT, AACT, REGULATORY    always (PubMed abstract record; CT.gov posted results; US-government text)
  PMC_OA / UNPAYWALL / HELD_*    only when Europe PMC records the ARTICLE's licence as CC BY or CC0
                                 (CC BY-NC, CC BY-ND, CC BY-NC-ND, CC BY-SA and 'no licence' are all excluded)

Licences are looked up once per PMID (Europe PMC REST 'core', field `license`) and cached in
outputs/k_gap/g1_binding/licences.json (metadata only). An unknown licence is CLOSED, never open.

BOTH must hold (the stricter of the repo guard and the lane rule):
  the repo's own guard (reproducible_ai/record_licence.py): PMC copy copy_licence == 'CC' (fulltext_index.json, written
  by scripts/g1_trial_acquire.pmc_copy from the PMC permissions), or the Unpaywall DOI copy licence 'cc*';
  AND the lane rule (CC BY / CC0 only): Europe PMC's licence for the article is CC BY or CC0 -- the repo guard alone
  accepts any Creative Commons licence, CC BY-NC included.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
CACHE = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "licences.json")
OPEN = {"cc by", "cc0", "cc-by", "cc-0", "public domain"}
ALWAYS = {"ABSTRACT", "AACT", "REGULATORY"}


def _load():
    return json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}


def licence(pmid, offline=False):
    """{'license': str|None, 'pmcid': str|None, 'open': bool} for a PMID; network once, then cached."""
    pmid = str(pmid or "")
    c = _load()
    if pmid in c:
        return c[pmid]
    if offline or not pmid:
        return {"license": None, "pmcid": None, "open": False, "state": "NOT_LOOKED_UP"}
    from harness import http
    r = http.get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                      {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core"}, tries=2)
    x = (r.get("resultList") or {}).get("result") or [{}]
    lic = (x[0].get("license") or "").strip().lower() or None
    v = {"license": lic, "pmcid": x[0].get("pmcid"), "open": lic in OPEN, "state": "LOOKED_UP"}
    c[pmid] = v
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(c, fh, indent=1, sort_keys=True)
    os.replace(CACHE + ".tmp", CACHE)
    return v


def repo_open(pmid, kind, offline=False):
    """The repo guard's verdict for one held copy: PMC_OA / HELD_CACHE_FT -> fulltext_index copy_licence == 'CC'
    (read once from the PMC permissions by g1_trial_acquire.pmc_copy when missing); UNPAYWALL -> the DOI copy's licence."""
    from reproducible_ai import record_licence as rl
    if kind == "UNPAYWALL":
        d = rl.pmid_doi(str(pmid))
        return bool(d) and str(rl.doi_licences().get(d) or "").startswith("cc")
    lic = rl.licences().get(str(pmid))
    if lic is None and not offline:
        import g1_trial_acquire as ta
        lic = ta.pmc_copy(str(pmid)).get("licence")
    return lic == "CC"


def gate(pmid, texts, offline=False):
    """(kept, dropped): texts is [(source kind, text)]; a full-text kind survives only when the repo guard marks that
    copy open AND the article's licence is CC BY / CC0."""
    kept, dropped = [], []
    lic = None
    for kind, t in texts:
        if kind in ALWAYS:
            kept.append((kind, t))
            continue
        lic = lic or licence(pmid, offline=offline)
        ok = lic.get("open") and repo_open(pmid, kind, offline=offline)
        (kept if ok else dropped).append((kind, t))
    return kept, [{"kind": k, "licence": (lic or {}).get("license"), "why": "LICENCE_NOT_CC_BY_OR_CC0_OR_COPY_NOT_OPEN"}
                  for k, _ in dropped]
