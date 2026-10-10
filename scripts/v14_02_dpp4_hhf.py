"""V14-02 (signed "sign v14", option A): admit omarigliptin and CARMELINA to dpp4-mace-t2d 'Hospitalization for heart failure'.

Typed, reproducible, nothing hand-entered:
  1. fetch each trial's PubMed AbstractText (efetch), normalised exactly as the binding lane did (scripts/g1_r6_dpp4_hf.py on
     g1/r6-dpp4-hf), and REFUSE unless its sha256 equals the hash the lane pinned and the signed item cites;
  2. hold it verbatim at outputs/held_abstracts/pubmed_<pmid>.txt (+ manifest.json with url, sha256, retrieved date);
  3. regex the effect out of the signed clause and write a canonical extracted_effect row into
     cache/dpp4-mace-t2d/verified_effects.json (key = the pool id: omarigliptin 28893244; CARMELINA 30418475, whose hHF
     paper is 30586723). The held record copy of 28893244 is ABRIDGED (1,138 of 2,124 chars) and omits this clause.

    python scripts/v14_02_dpp4_hhf.py [--offline]   (--offline re-derives the rows from the held files only)
"""
from __future__ import annotations

import datetime
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT]
HELD = os.path.join(ROOT, "outputs", "held_abstracts")
SLUG = "dpp4-mace-t2d"
OUTCOME = "Hospitalization for heart failure"
ITEM = "V14-02"
TARGETS = [  # pool id, abstract pmid, nct, pinned sha256 (lane record r6_dpp4_hf.json), signed clause
    ("28893244", "28893244", "NCT01703208", "6ade2476f3f931f8ef952c2afc46f2b11b3292361e933428cbb54784b6420c9b",
     "The hHF outcome occurred in 20/2092 patients in the omarigliptin group (0.96%; 0.51/100 patient-years) and 33/2100 "
     "patients in the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)"),
    ("30418475", "30586723", "NCT01897532", "94e500fb2025e3a5d004490722412507eb1aca81e62c61475b8cee6b17548705",
     "Linagliptin versus placebo did not affect the incidence of hHF (209/3494 [6.0%] versus 226/3485 [6.5%], "
     "respectively; hazard ratio [HR], 0.90; 95% CI, 0.74-1.08)"),
]
_NUM = r"(\d+(?:\.\d+)?)"
_HR = re.compile(r"(?:HR of|\[HR\],)\s*" + _NUM + r"\s*\(?;?\s*95% CI,?\s*" + _NUM + r"\s*[,-]\s*" + _NUM)
_COUNTS = re.compile(r"(?<![\d.])(\d+)/(\d+)(?![\d.])")  # never a rate such as 0.51/100


def normalise(xml_article: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", " ".join(
        re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", xml_article, re.S))))).strip()


_BASES = ("databank accession number", "the article's own abstract")


def _exact(nct: str) -> str:
    return r"(?<![0-9A-Za-z])" + re.escape(nct) + r"(?![0-9A-Za-z])"


def witness(xml_article: str, nct: str):
    """(basis, evidence) where the article ITSELF names the trial: its databank accession numbers or its own abstract --
    never its reference list or linked comments (the lane's rule, codex r6-dpp4-hf-r1 #3); the identifier must match
    exactly (codex v14-apply-r3 g1#1: NCT017032080 is not NCT01703208). None when it does not."""
    own = re.sub(r"<ReferenceList>.*?</ReferenceList>|<CommentsCorrectionsList>.*?</CommentsCorrectionsList>", " ",
                 xml_article, flags=re.S)
    m = re.search(r"<AccessionNumber>" + re.escape(nct) + r"</AccessionNumber>", own)
    if m:
        return _BASES[0], m.group(0)
    ab = normalise(own)
    m = re.search(_exact(nct), ab)
    if m:
        return _BASES[1], ab[max(0, m.start() - 80):m.end() + 20]
    return None


def nct_witness(xml_article: str, nct: str):
    w = witness(xml_article, nct)
    return w[0] if w else None


def offline_identity_ok(doc: dict, nct: str) -> bool:
    """Offline, the recorded identity is accepted only when it is THIS trial's, its basis is a known witness kind, and
    its recorded evidence carries the exact identifier (codex v14-apply-r3 g1#2)."""
    return (doc.get("nct") == nct and doc.get("nct_basis") in _BASES
            and bool(re.search(_exact(nct), str(doc.get("nct_evidence") or ""))))


def fetch(pmids):
    from harness import http, fetch as hf
    url = f"{hf.EUTILS}/efetch.fcgi"
    x = http.get_text(url, {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml",
                            "tool": "meta-harness", "email": "meta-harness@example.org"})
    out = {}
    for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", x, re.S):
        out[re.search(r"<PMID[^>]*>(\d+)", art).group(1)] = (normalise(art), art)
    return url, out


def parse(span: str) -> dict:
    m, c = _HR.search(span), _COUNTS.findall(span)
    if not m or len(c) != 2:
        raise ValueError(f"signed clause does not parse: {span[:60]}")
    e, lo, hi = map(float, m.groups())
    if not lo < e < hi:
        raise ValueError(f"effect outside its interval: {e} ({lo}, {hi})")
    (et, nt), (ec, nc) = [tuple(map(int, x)) for x in c]
    return {"effect": e, "ci_low": lo, "ci_high": hi, "events_t": et, "n_t": nt, "events_c": ec, "n_c": nc}


def main(argv):
    offline = "--offline" in argv
    os.makedirs(HELD, exist_ok=True)
    man_path = os.path.join(HELD, "manifest.json")
    manifest = json.load(open(man_path, encoding="utf-8")) if os.path.exists(man_path) else {"documents": {}}
    if not offline:
        url, got = fetch([t[1] for t in TARGETS])
    rows = {}
    for pid, pmid, nct, sha, span in TARGETS:
        path = os.path.join(HELD, f"pubmed_{pmid}.txt")
        text, art = (open(path, encoding="utf-8").read(), None) if offline else got.get(pmid, ("", ""))
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest != sha:
            raise SystemExit(f"REFUSED {pmid}: abstract sha256 {digest} != pinned {sha} (source moved; apply nothing)")
        if span not in text:
            raise SystemExit(f"REFUSED {pmid}: signed clause not in its own abstract")
        # the trial identity is verified against the article itself (agy v14-apply-r1-agy #2), never trusted
        if offline:
            doc = manifest["documents"].get(f"pubmed_{pmid}.txt") or {}
            w = (doc.get("nct_basis"), doc.get("nct_evidence")) if offline_identity_ok(doc, nct) else None
        else:
            w = witness(art, nct)
        if not w:
            raise SystemExit(f"REFUSED {pmid}: the article does not itself name {nct} (databank accession or abstract)")
        if not offline:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            manifest["documents"][f"pubmed_{pmid}.txt"] = {
                "pmid": pmid, "nct": nct, "nct_basis": w[0], "nct_evidence": w[1], "source": url + f"?db=pubmed&id={pmid}&retmode=xml",
                "normalisation": "AbstractText elements joined by a space, tags stripped, HTML-unescaped, whitespace collapsed",
                "sha256": sha, "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "held_for": f"{ITEM} {SLUG} '{OUTCOME}'"}
        v = parse(span)
        rows[pid] = {"kind": "extracted_effect", "outcome": OUTCOME, "scale": "HR", "override": True,
                     "effect": v["effect"], "ci_low": v["ci_low"], "ci_high": v["ci_high"],
                     "source": f"PMID {pmid} ({nct}) PubMed abstract: hHF {v['events_t']}/{v['n_t']} v "
                               f"{v['events_c']}/{v['n_c']}; HR {v['effect']:.2f} ({v['ci_low']:.2f}-{v['ci_high']:.2f})",
                     "verification": f"{ITEM}: span found verbatim in the held abstract (sha256 {sha})",
                     "source_span": span, "document_ref": f"outputs/held_abstracts/pubmed_{pmid}.txt",
                     "source_level": 1, "provenance": "abstract_verified",
                     "reason": f"{ITEM} (signed by Mahmood, 'sign v14'): typed transcription from PMID {pmid}'s own PubMed "
                               f"abstract, held verbatim and pinned by sha256 {sha[:12]}; binding lane r6_dpp4_hf, two "
                               f"recorded readers agree."}
    if not offline:
        with open(man_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
    vpath = os.path.join(ROOT, "cache", SLUG, "verified_effects.json")
    data = json.load(open(vpath, encoding="utf-8"))
    for pid, row in rows.items():
        cur = data.get(pid)
        cur = [] if cur is None else (cur if isinstance(cur, list) else [cur])
        cur = [e for e in cur if e.get("outcome") != OUTCOME] + [row]
        data[pid] = cur
    with open(vpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({pid: {k: r[k] for k in ("effect", "ci_low", "ci_high", "source")}
                      for pid, r in rows.items()}))


if __name__ == "__main__":
    main(sys.argv[1:])
