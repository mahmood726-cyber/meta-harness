"""Comparator trial membership from the comparator's OWN statement of k (V1.0.1, DPP-4 review).

Patoulias 2021 states "We finally pooled data from six trials in a total of 52520 patients[10-15]". Its held body text
prints the citation only as numbers; its PMC JATS links the range to references B10..B15, each carrying a PMID. The
cited range IS the comparator's trial list, so "count not stated" and "trial set not enumerated" are both false.

This route holds the comparator's PMC JATS (open licence only; same rule as comparator_row_citations.py jats), finds
the ONE sentence that states the trial count (harness/extract.stated_trial_count on the JATS text) and whose citation
is a single <xref> range, and writes one trial_set member per cited reference into cache/<slug>/comparators.json:
  family_id / name_in_source   the trial acronym printed in the reference (or a drug name when it has none)
  span                         the <ref id=..> element in the JATS (the name is inside it)
  aliases[0]                   id = the reference's PMID, span = the same <ref>, linked_rid, and stated_k_span (the
                               citing sentence), so harness/comparator_panel.validate re-proves the rid lies in the range
Nothing is written unless every cited reference carries a PMID (refuses otherwise).

usage: python scripts/comparator_stated_k_members.py <slug> [--write]
"""
import hashlib
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extract  # noqa: E402
from harness.comparator_panel import stated_k_range  # noqa: E402

TOOL = "tool=meta-harness&email=mahmood726%40gmail.com"


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness"}), timeout=60) as r:
        return r.read()


def _plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def run(slug, write):
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    ids = json.loads(_get(f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids={cfg['comparator_pmid']}&format=json&{TOOL}"))
    pmcid = (ids.get("records") or [{}])[0].get("pmcid")
    if not pmcid:
        return {"state": "NOT_IN_PMC"}
    raw = _get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}&retmode=xml&{TOOL}")
    xml = raw.decode("utf-8")
    lic = re.search(r"creativecommons\.org/(?:licenses|publicdomain)/[a-z-]+/[0-9.]+", xml)
    if not lic and 'license-type="open-access"' not in xml:
        return {"state": "NOT_OPEN_LICENSE", "pmcid": pmcid}
    # candidate sentences: <p> fragments whose plain text states k and whose citation is one xref range
    found = []
    for m in re.finditer(r"[^.<]*(?:<(?!/?p[ >])[^>]*>[^.<]*)*\.", xml):
        frag = m.group(0)
        k, _q = extract.stated_trial_count(_plain(frag))
        rng = stated_k_range(frag)
        if k and rng:
            found.append((m.start(), m.end(), k, rng))
    if len(found) != 1:
        return {"state": "REFUSED", "why": f"{len(found)} stated-k sentences with a cited range (need exactly one)"}
    a, b, k, rids = found[0]
    if len(rids) != k:
        return {"state": "REFUSED", "why": f"stated k={k} but the cited range has {len(rids)} references"}
    members = []
    for rid in rids:
        rm = re.search(r'<ref id="%s">.*?</ref>' % re.escape(rid), xml, re.S)
        if not rm:
            return {"state": "REFUSED", "why": f"reference {rid} not found"}
        ref = rm.group(0)
        pmid = re.search(r'pub-id-type="pmid">(\d+)<', ref)
        if not pmid:
            return {"state": "REFUSED", "why": f"reference {rid} carries no PMID"}
        text = _plain(ref)
        # the trial's printed name: an acronym in the group author (<collab>), else in the article title, else the drug
        # named in the title; never an identifier (PMC..., DOI) or a generic abbreviation
        _generic = r"(?:PMC\d+|DPP|RR|CI|USA|UK|MD|PHD|II|III|IV|T2D|T2DM|HF|MACE|DOI)(?:-\d+)?"
        name = None
        for part in re.findall(r"<collab>(.*?)</collab>", ref, re.S) + re.findall(r"<article-title>(.*?)</article-title>", ref, re.S):
            acr = [x for x in re.findall(r"\b([A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*)\b", _plain(part)) if not re.fullmatch(_generic, x)]
            if acr:
                name = acr[0]
                break
        if not name:
            title = _plain((re.search(r"<article-title>(.*?)</article-title>", ref, re.S) or [None, ""])[1])
            name = (re.search(r"\b([a-z]+gliptin|[a-z]+flozin|[a-z]+glutide|[a-z]+tide)\b", title) or [None, None])[1]
        if not name:
            return {"state": "REFUSED", "why": f"reference {rid}: no trial name printed"}
        span = {"start": rm.start(), "end": rm.end(), "quote": ref}
        members.append({"family_id": name, "name_in_source": name, "span": span, "endpoint": None,
                        "aliases": [{"id": pmid.group(1), "document_ref": f"cache/{slug}/comparator_pmc_jats.xml",
                                     "document_sha256": hashlib.sha256(raw).hexdigest(), "span": span,
                                     "linked_rid": rid,
                                     "stated_k_span": {"start": a, "end": b, "quote": xml[a:b]},
                                     "bound_by": f"the comparator's stated-k sentence cites {rids[0]}-{rids[-1]}; {rid} "
                                                 f"carries PMID {pmid.group(1)}"}]})
    out = {"state": "BOUND" if write else "WOULD_BIND", "pmcid": pmcid, "license": lic.group(0) if lic else "open-access",
           "k": k, "members": [(m["family_id"], m["aliases"][0]["id"]) for m in members]}
    if write:
        rel = f"cache/{slug}/comparator_pmc_jats.xml"
        open(os.path.join(ROOT, rel), "wb").write(raw)
        p = os.path.join(ROOT, "cache", slug, "comparators.json")
        raw_panel = open(p, encoding="utf-8").read()
        panel = json.loads(raw_panel)
        c = next(x for x in panel if str(x["id"]) == str(cfg["comparator_pmid"]))
        c["trial_set"] = members
        c["trial_set_document"] = {"document_ref": rel, "document_sha256": hashlib.sha256(raw).hexdigest()}
        c["k"] = None
        open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(panel, indent=2, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1], "--write" in sys.argv), indent=1))
