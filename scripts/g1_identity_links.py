"""IDENTITY LINKS: a comparator unit cited by a PubMed report that names no registration, joined to the registered trial we
already pool (gap list 8 Oct, sacubitril-valsartan-hfref: the comparator's 'Tsutsui, 2021' = PMID 33731544 is PARALLEL-HF,
pooled as NCT02468232, but PubMed's record carries no NCT and CT.gov lists no reference, so no join existed and the trial
read NO_ROW while our own pool held it).

A link PMID -> NCT is written only when TWO independent typed facts agree, each with its verbatim span and digest:
  ONE_NCT_STATED_IN_OWN_REPORT        the trial's own report, from a legitimately open copy (g1_trial_acquire OPEN_COPY:
                                      PMC CC / author manuscript, or a CC Unpaywall / open-location copy), prints exactly one
                                      NCT id (g1_open_sources.stated_registration; several ids -> none)
  TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM   an acronym in the report's PubMed title (an all-capitals token, hyphenated
                                      parts allowed) equals that NCT's registered acronym (CT.gov API v2
                                      identificationModule.acronym; response sha256 recorded)
Anything less is recorded with why, never linked. The tracker joins a comparator unit through a link ONLY to a
registration already in our pool (join(), the same shape as SCREENED_VIA_OTHER_REPORT); it never adds a trial to a pool.

    python scripts/g1_identity_links.py PMID [PMID ...]   -> registry/identity_links.json
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
LINKS = os.path.join(ROOT, "registry", "identity_links.json")
UA = "meta-harness/1.0 (reproducible-ma; mailto:meta-harness@example.org)"
_ACRO = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]{1,})+|[A-Z]{3,}[0-9]*)(?![A-Za-z0-9])")


def load(path=None):
    p = path or LINKS
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def title_acronyms(title):
    """All-capitals tokens of a title ('PARALLEL-HF'), hyphenated parts allowed; common words never qualify."""
    return {m.group(1) for m in _ACRO.finditer(title or "")} - {"RCT", "HFREF", "HF", "CI", "HR"}


def registry_acronym(nct, fetch=None):
    """(acronym, response sha256) from CT.gov API v2; fetch is injectable for tests."""
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct}?fields=protocolSection.identificationModule"
    if fetch is None:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read()
    else:
        body = fetch(url)
    d = json.loads(body)
    return ((d.get("protocolSection") or {}).get("identificationModule") or {}).get("acronym"), \
        hashlib.sha256(body).hexdigest()


def decide(pmid, title, report_text, report_source, acronym_of):
    """{'nct', 'rules': [...]} when both rules hold, else {'refused': why}. Pure given its inputs (acronym_of: nct ->
    (acronym, sha256))."""
    import g1_open_sources as osrc
    nct = osrc.stated_registration(report_text or "")
    if not nct:
        n = len(set(osrc._NCT.findall(report_text or "")))
        return {"refused": "NO_OPEN_REPORT_TEXT" if not report_text else
                f"REPORT_STATES_{'NO' if n == 0 else 'SEVERAL'}_NCT ({n})"}
    m = re.search(rf".{{0,80}}{nct}.{{0,40}}", report_text, re.S)
    rule1 = {"rule": "ONE_NCT_STATED_IN_OWN_REPORT", "span": re.sub(r"\s+", " ", m.group(0)).strip(),
             "source": report_source, "text_sha256": hashlib.sha256(report_text.encode("utf-8")).hexdigest()}
    acro, sha = acronym_of(nct)
    hits = sorted(a for a in title_acronyms(title) if acro and a.upper() == acro.upper())
    if not hits:
        return {"refused": f"TITLE_ACRONYM_NOT_THE_REGISTRY_ACRONYM (registry {acro!r}, title "
                           f"{sorted(title_acronyms(title))})", "nct_stated": nct}
    rule2 = {"rule": "TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM", "span": hits[0], "title": title,
             "source": f"PubMed title PMID {pmid}; CT.gov API v2 {nct} identificationModule.acronym",
             "registry_response_sha256": sha}
    return {"nct": nct, "rules": [rule1, rule2]}


def held_open_report(pmid, slug):
    """(text, source label) of the trial's own report from a legitimately open copy, via the acquisition cascade."""
    import g1_trial_acquire as ga
    t = {"slug": slug, "label": pmid, "pmid": pmid, "ncts": []}
    whole, _s, sha = ga.text_evidence(pmid, [])
    if whole and ga.pmc_copy(pmid)["licence"] in ga.OPEN_COPY:
        return whole, f"PMC copy of PMID {pmid} ({ga.pmc_copy(pmid)['licence']}) text sha256 {sha}"
    whole, _s, sha, doi, lic = ga.unpaywall_evidence(pmid, [])
    if whole and str(lic or "").startswith("cc"):
        return whole, f"Unpaywall copy DOI {doi} ({lic}) of PMID {pmid} text sha256 {sha}"
    whole, _s, sha, doi, lic, url = ga.open_location_evidence(pmid, [])
    if whole and str(lic or "").startswith("cc"):
        return whole, f"open-location copy {url} ({lic}, host-page licence) of PMID {pmid} text sha256 {sha}"
    del t
    return "", None


def build(pmids, slug=""):
    import g1_open_sources as osrc
    cur = load()
    for pmid in pmids:
        meta = osrc.report_meta(pmid)
        text, src = held_open_report(pmid, slug)
        v = decide(pmid, meta.get("title"), text, src, registry_acronym)
        v["built"] = datetime.date.today().isoformat()
        v["writer"] = "scripts/g1_identity_links.py"
        cur[str(pmid)] = v
        print(pmid, json.dumps(v, ensure_ascii=False)[:400])
    with open(LINKS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cur, fh, indent=1, sort_keys=True, ensure_ascii=False)


def join(trials, comp_rows, rp, nct_pool, pooled_ids, matched_ids, routes, links=None):
    """Join each comparator unit we do not pool, whose report PMID has an identity LINK to a registration already in our
    pool (and not already matched), to that pool row. Returns [(x, pool_row_id, link)] for the caller to value. Never
    adds a trial to a pool: a link to a registration we do not pool does nothing."""
    links = load() if links is None else links
    out = []
    for x, t in zip(trials, comp_rows):
        p = rp.get(id(t))
        lk = links.get(str(p)) if p else None
        if x.get("in_our_pool") or not lk or not lk.get("nct"):
            continue
        via = nct_pool.get(lk["nct"])
        if not via or via not in pooled_ids or via in matched_ids:
            continue
        matched_ids.add(via)
        routes[x["route"]] = routes.get(x["route"], 0) - 1
        routes["PRIMARY"] = routes.get("PRIMARY", 0) + 1
        x.update(in_our_pool=True, route="PRIMARY", family=via, g1_countable=True, our_refusal=None,
                 basis=f"same registered trial {lk['nct']}: pooled as {via}; the comparator cites PMID {p}, joined by "
                       f"identity link ({' + '.join(r['rule'] for r in lk['rules'])}; registry/identity_links.json)",
                 matched_via_identity_link={"nct": lk["nct"], "pool_row": via, "comparator_cites": p,
                                            "rules": lk["rules"]})
        out.append((x, via, lk))
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    build([a for a in sys.argv[1:] if not a.startswith("--")],
          next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--slug=")), ""))
