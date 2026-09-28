"""Comparator trial membership for ONE OUTCOME from the comparator's own outcome-level trial list (V1.0.1, sacubitril
review).

Ji 2023 (network meta-analysis, PMC10053170) includes 17 studies overall; its HFrEF composite (CV death or HHF) is
stated as "The composite CV outcome in patients with HFrEF was available in 10 trials." followed by a citation list of
exactly ten references, each with a PMID. That list IS the comparator's membership for the outcome our review pools;
the network-wide 17 is not. Its Table 1 names trials without reference links, so the table routes cannot bind it.

Given an anchor (the sentence's unique text), the outcome name in our protocol and an endpoint label, this writes one
trial_set member per cited reference into cache/<slug>/comparators.json, each bound to our outcome through
outcome_endpoints, with the alias span = the <ref> (PMID + printed name) and outcome_list_span = the sentence plus its
citation run (harness/comparator_panel.validate re-proves: the span prints "<k> trials" and cites exactly k references,
rid among them). Refuses unless the anchor is unique, the count is printed, and every cited reference carries a PMID.

usage: python scripts/comparator_outcome_list_members.py <slug> "<anchor>" "<our outcome>" "<endpoint label>" [--write]
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from harness.comparator_panel import outcome_list_rids, validate  # noqa: E402
import comparator_stated_k_members as sk  # noqa: E402


def run(slug, anchor, outcome, label, write):
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    ids = json.loads(sk._get(f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids={cfg['comparator_pmid']}&format=json&{sk.TOOL}"))
    pmcid = (ids.get("records") or [{}])[0].get("pmcid")
    if not pmcid:
        return {"state": "NOT_IN_PMC"}
    raw = sk._get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}&retmode=xml&{sk.TOOL}")
    xml = raw.decode("utf-8")
    lic = re.search(r"creativecommons\.org/(?:licenses|publicdomain)/[a-z-]+/[0-9.]+", xml)
    if not lic and 'license-type="open-access"' not in xml:
        return {"state": "NOT_OPEN_LICENSE", "pmcid": pmcid}
    if xml.count(anchor) != 1:
        return {"state": "REFUSED", "why": f"anchor occurs {xml.count(anchor)} times in the JATS (need exactly one)"}
    i = xml.index(anchor)
    k_m = re.search(r"\b(\d{1,3}) trials\.", anchor)
    if not k_m:
        return {"state": "REFUSED", "why": "the anchor prints no '<k> trials.'"}
    k = int(k_m.group(1))
    # the span runs from the anchor through the citation run that immediately follows it
    j = i + len(anchor)
    end = j
    for m in re.finditer(r"\s*,?\s*<xref\b[^>]*>.*?</xref>", xml[j:], re.S):
        if m.start() != end - j:
            break
        end = j + m.end()
    frag = xml[i:end]
    rids = outcome_list_rids(frag)
    if not rids or len(rids) != k:
        return {"state": "REFUSED", "why": f"the anchor states {k} trials but cites {len(rids or [])} references"}
    span_ol = {"start": i, "end": end, "quote": frag}
    sha = hashlib.sha256(raw).hexdigest()
    rel = f"cache/{slug}/comparator_pmc_jats.xml"
    members = []
    for rid in rids:
        rm = re.search(r'<ref id="%s">.*?</ref>' % re.escape(rid), xml, re.S)
        if not rm:
            return {"state": "REFUSED", "why": f"reference {rid} not found"}
        ref = rm.group(0)
        pmid = re.search(r'pub-id-type="pmid">(\d+)<', ref)
        if not pmid:
            return {"state": "REFUSED", "why": f"reference {rid} carries no PMID"}
        name = None
        for part in re.findall(r"<collab>(.*?)</collab>", ref, re.S) + re.findall(r"<article-title>(.*?)</article-title>", ref, re.S):
            acr = re.findall(r"\b([A-Z][A-Z0-9]{2,}(?:[-‐][A-Z0-9]+)*)\b", sk._plain(part))
            acr = [a for a in acr if not re.fullmatch(r"(?:HF|CV|RR|CI|USA|UK|DOI|II|III|IV)", a)]
            if acr:
                name = acr[0]
                break
        name = name or sk._plain(re.search(r"<surname>(.*?)</surname>", ref, re.S).group(1))
        span = {"start": rm.start(), "end": rm.end(), "quote": ref}
        members.append({"family_id": f"{name} [{rid}]", "name_in_source": name, "span": span,
                        "endpoint": label, "endpoint_span": span_ol,
                        "aliases": [{"id": pmid.group(1), "document_ref": rel, "document_sha256": sha, "span": span,
                                     "linked_rid": rid, "outcome_list_span": span_ol, "stated_k": k,
                                     "bound_by": f"the comparator's {label} list ('{anchor}') cites {rid}, which carries "
                                                 f"PMID {pmid.group(1)}"}]})
    out = {"state": "BOUND" if write else "WOULD_BIND", "pmcid": pmcid, "license": lic.group(0) if lic else "open-access",
           "k": k, "members": [(m["family_id"], m["aliases"][0]["id"]) for m in members]}
    if write:
        open(os.path.join(ROOT, rel), "wb").write(raw)
        p = os.path.join(ROOT, "cache", slug, "comparators.json")
        raw_panel = open(p, encoding="utf-8").read()
        panel = json.loads(raw_panel)
        c = next(x for x in panel if str(x["id"]) == str(cfg["comparator_pmid"]))
        if c.get("trial_set"):
            return {"state": "ALREADY_ENUMERATED", "k": len(c["trial_set"])}
        c["trial_set"] = members
        c["trial_set_document"] = {"document_ref": rel, "document_sha256": sha, "source": "PMC JATS (efetch db=pmc)",
                                   "pmcid": pmcid, "license": out["license"], "row_identity": "OUTCOME_CITATION_LIST",
                                   "table_caption": anchor}
        c["outcome_endpoints"] = dict(c.get("outcome_endpoints") or {}, **{outcome: label})
        validate(c, ROOT)
        open(p, "w", encoding="utf-8", newline="\n").write(
            json.dumps(panel, indent=2 if raw_panel.startswith("[\n  ") else 1, ensure_ascii=False)
            + ("\n" if raw_panel.endswith("\n") else ""))
    return out


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--write"]
    print(json.dumps(run(a[0], a[1], a[2], a[3], "--write" in sys.argv), indent=1, ensure_ascii=False))
