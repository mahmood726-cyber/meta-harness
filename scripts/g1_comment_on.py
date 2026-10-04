"""Comparator references that are LETTERS / COMMENTS about a trial (sglt2-primary-prevention-hf's 'Isreb (19)' is a
letter, PMID 31509682, commenting on CREDENCE, PMID 30990260): the trial a letter is about is PubMed's own CommentOn link
(CommentsCorrections RefType="CommentOn"), never a guess from its title. Fetched once (network, acquisition time),
replayed offline from registry/comment_on.json with the request and the response's sha256.

  python scripts/g1_comment_on.py            -> registry/comment_on.json (every comparator-cited Letter/Comment/Editorial)
"""
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "registry", "comment_on.json")
NONPRIMARY = ("letter", "comment", "editorial")
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={}"


def is_comment(rec):
    pts = [p.lower() for p in (rec or {}).get("pubtypes") or []]
    return bool(pts) and any(any(n in p for n in NONPRIMARY) for p in pts) and \
        not any("randomized controlled trial" in p or "clinical trial" in p for p in pts)


def comment_on(xml):
    """PMIDs the record states it comments on, from its own CommentsCorrections list."""
    return sorted(set(re.findall(r'<CommentsCorrections RefType="CommentOn">.*?<PMID[^>]*>(\d+)</PMID>', xml, re.S)))


def cited_comment_pmids():
    """Every PMID a G1 tracker file seeds from a comparator reference whose held record is a letter/comment."""
    mem = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "member_records.json"), encoding="utf-8"))
    by = {str(v.get("id")): v for v in mem.values()}
    out = set()
    d = os.path.join(ROOT, "outputs", "k_gap", "g1")
    for f in os.listdir(d):
        for x in json.load(open(os.path.join(d, f), encoding="utf-8")).get("trials") or []:
            p = str(((x.get("seeded_funnel") or {}).get("pmid")) or "")
            if p and is_comment(by.get(p)):
                out.add(p)
    return sorted(out)


def main():
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for p in cited_comment_pmids():
        if p in prev:
            continue
        u = EFETCH.format(p)
        b = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "meta-harness/1.0"}), timeout=60).read()
        time.sleep(0.4)
        prev[p] = {"comment_on": comment_on(b.decode("utf-8", "replace")), "request": u,
                   "response_sha256": hashlib.sha256(b).hexdigest(),
                   "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(prev, indent=1, sort_keys=True) + "\n")
    print(json.dumps(prev, indent=1))


if __name__ == "__main__":
    sys.exit(main())
