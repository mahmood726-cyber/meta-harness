"""SOURCE-PRESERVATION CENSUS (pva, independent lane). Every held PubMed record in cache/<slug>/records.json at a commit is
compared with the abstract PubMed serves NOW, rebuilt with the harness's own formatter (harness/fetch.py::_efetch at the
same commit: each AbstractText as 'Label: text', joined with single spaces). Raw efetch XML is kept with its sha256 and UTC
time. Nothing in the repository is modified.

  python source_census.py --commit <sha> --out <dir on a drive with room>
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "C:/mh-lanes/pva"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def git(*a) -> str:
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL).stdout


def _txt(el):                       # identical to harness/fetch.py::_txt
    return "".join(el.itertext()).strip() if el is not None else ""


def rebuild(art) -> str:            # identical to the abstract expression in harness/fetch.py::_efetch
    return " ".join((a.get("Label", "") + ": " if a.get("Label") else "") + _txt(a)
                    for a in art.findall(".//Abstract/AbstractText")).strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip()


# sentence split: after . ? ! followed by space+capital/digit, and before a section label 'LABEL:' the formatter inserted
_SPLIT = re.compile(r"(?<=[.?!])\s+(?=[A-Z0-9(\[])|\s+(?=[A-Z][A-Z /&-]{2,40}:\s)")


def sentences(s: str) -> list[str]:
    return [x.strip() for x in _SPLIT.split(norm(s)) if len(x.strip()) > 3]


def fetch(pmids: list[str], raw_dir: Path, ledger: list) -> dict:
    got = {}
    for i in range(0, len(pmids), 150):
        batch = pmids[i:i + 150]
        q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(batch), "retmode": "xml",
                                    "tool": "meta-harness-pva-census", "email": "meta-harness@example.org"})
        url = f"{EUTILS}/efetch.fcgi?{q}"
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    body = r.read()
                if not body.lstrip().startswith(b"<?xml") and b"<PubmedArticleSet" not in body[:2000]:
                    raise ValueError("not an efetch XML payload")
                break
            except Exception as e:  # noqa: BLE001 -- bounded retry; a non-XML payload is never accepted
                if attempt == 3:
                    raise SystemExit(f"REFUSED: efetch failed for batch {i}: {e}")
                time.sleep(3 * (attempt + 1))
        name = f"efetch_{i // 150:03d}.xml"
        (raw_dir / name).write_bytes(body)
        ledger.append({"file": name, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
                       "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "url": url, "pmids": batch})
        for art in ET.fromstring(body).findall(".//PubmedArticle"):
            pm = _txt(art.find(".//MedlineCitation/PMID"))
            got[pm] = {"abstract": rebuild(art), "title": _txt(art.find(".//ArticleTitle")), "raw": name}
        time.sleep(0.4)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); raw = out / "raw"; raw.mkdir(parents=True, exist_ok=True)
    sha = git("rev-parse", a.commit).strip()
    served = {p.split("/")[-1] for p in git("ls-tree", "--name-only", sha, "docs/reviews/").split() if "." not in p.split("/")[-1]}
    files = [p for p in git("ls-tree", "-r", "--name-only", sha, "cache/").split()
             if re.fullmatch(r"cache/[^/]+/records\.json", p)]
    fulltexts = [p for p in git("ls-tree", "-r", "--name-only", sha, "cache/").split() if re.fullmatch(r"cache/[^/]+/ft_[^/]+", p)]
    held, other_kinds = [], {}
    for f in files:
        slug = f.split("/")[1]
        d = json.loads(git("show", f"{sha}:{f}") or "{}")
        for r in d.get("records", []) if isinstance(d, dict) else []:
            if r.get("id_type") != "pmid":
                other_kinds[r.get("id_type")] = other_kinds.get(r.get("id_type"), 0) + 1
                continue
            held.append({"slug": slug, "served_topic": slug in served, "pmid": str(r.get("id")), "file": f,
                         "title": r.get("title"), "abstract": r.get("abstract") or ""})
    pmids = sorted({h["pmid"] for h in held})
    print(f"commit {sha[:12]}: {len(files)} records.json, {len(held)} held pmid records ({len(pmids)} distinct), "
          f"served topics {len(served)}; other id types {other_kinds}; full-text files {len(fulltexts)}", flush=True)
    ledger = []
    now = fetch(pmids, raw, ledger)
    rows = []
    for h in held:
        cur = now.get(h["pmid"])
        if cur is None:
            cls, om, ad = "NOT_RETURNED_BY_PUBMED", [], []
        else:
            hs, cs = h["abstract"], cur["abstract"]
            if hs == cs:
                cls, om, ad = "IDENTICAL", [], []
            elif norm(hs) == norm(cs):
                cls, om, ad = "FORMAT_ONLY", [], []
            elif not hs.strip():
                cls, om, ad = "HELD_EMPTY", sentences(cs), []
            elif not cs.strip():
                cls, om, ad = "PUBMED_EMPTY", [], sentences(hs)
            else:
                hn, cn = norm(hs), norm(cs)
                om = [x for x in sentences(cs) if x not in hn]
                ad = [x for x in sentences(hs) if x not in cn]
                cls = "ABRIDGED" if om and not ad else ("ALTERED" if ad else "DIFFERS_NO_SENTENCE_LEVEL_CHANGE")
        rows.append({**{k: h[k] for k in ("slug", "served_topic", "pmid", "file", "title")}, "class": cls,
                     "held_len": len(h["abstract"]), "pubmed_len": len((cur or {}).get("abstract", "")),
                     "held_sha256": hashlib.sha256(h["abstract"].encode()).hexdigest(),
                     "pubmed_sha256": hashlib.sha256(((cur or {}).get("abstract", "")).encode()).hexdigest() if cur else None,
                     "raw": (cur or {}).get("raw"), "omitted_sentences": om, "added_sentences": ad})
    counts = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    doc = {"commit": sha, "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "population": {"records_json_files": len(files), "held_pmid_records": len(held), "distinct_pmids": len(pmids),
                          "served_topics": len(served), "other_id_types_not_compared": other_kinds,
                          "fulltext_files_not_compared": fulltexts},
           "counts": counts, "fetch_ledger": ledger, "rows": rows}
    (out / "census.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(counts), flush=True)
    for r in rows:
        if r["class"] not in ("IDENTICAL", "FORMAT_ONLY"):
            print(f"{r['class']:32} {r['slug'][:34]:34} {r['pmid']:>9} held {r['held_len']:5} pubmed {r['pubmed_len']:5} "
                  f"omit {len(r['omitted_sentences'])} add {len(r['added_sentences'])}", flush=True)


if __name__ == "__main__":
    main()
