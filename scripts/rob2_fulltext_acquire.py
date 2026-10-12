"""Acquire the OPEN-ACCESS full texts of RoB 2 trials for REGEX reading (Mahmood, 12 Oct: 'extend' -- extend the regex
reading of held full texts). D8: regex may read any held text; a model prompt may not. These texts are therefore held in
a LOCAL store OUTSIDE the repository (ROBGRADE_FT_STORE, default F:/claude-temp/robgrade-ft): a non-CC text is never
committed. Each entry records the PMC XML's sha256, the parsed text's sha256 (the hash every regex span cites), and the
licence the article's OWN <permissions> name (record_licence.jats_licence).

    python scripts/rob2_fulltext_acquire.py [--calibration] [PMID ...]
Writes <store>/<pmid>/{pmc.xml, text.txt, meta.json}.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
STORE = os.environ.get("ROBGRADE_FT_STORE") or "F:/claude-temp/robgrade-ft"


def store_path(pmid):
    return os.path.join(STORE, str(pmid))


def held(pmid):
    """(text, meta) from the local store, or (None, None)."""
    d = store_path(pmid)
    if not os.path.exists(os.path.join(d, "meta.json")):
        return None, None
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    if meta.get("state") != "HELD":
        return None, meta
    with open(os.path.join(d, "text.txt"), "rb") as fh:
        b = fh.read()
    if hashlib.sha256(b).hexdigest() != meta.get("text_sha256"):
        raise RuntimeError(f"local full text for PMID {pmid} does not match its recorded sha256")
    return b.decode("utf-8"), meta


def acquire(pmid):
    from harness import fetch, http
    from harness import fulltext as ft
    from reproducible_ai import record_licence as rl
    d = store_path(pmid)
    os.makedirs(d, exist_ok=True)
    meta = {"pmid": str(pmid), "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        pmcid = fetch._resolve_pmcid(str(pmid))
    except Exception as exc:  # noqa: BLE001 - recorded, never 'no full text'
        meta.update(state="RESOLVE_FAILED", error=str(exc)[:200])
        pmcid = None
    if pmcid:
        meta["pmcid"] = pmcid
        try:
            xml = http.get_text(f"{fetch.EUTILS}/efetch.fcgi", {"db": "pmc", "id": pmcid, "retmode": "xml",
                                                               "tool": "meta-harness", "email": "meta-harness@example.org"})
            time.sleep(0.4)
        except Exception as exc:  # noqa: BLE001
            meta.update(state="FETCH_FAILED", error=str(exc)[:200])
            xml = None
        if xml is not None:
            if fetch.PUBLISHER_DISALLOWS_XML in xml[:4000]:
                meta["state"] = "PUBLISHER_DISALLOWS_XML"
            else:
                with open(os.path.join(d, "pmc.xml"), "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(xml)
                text = ft.combined_text(ft.parse_pmc_xml(xml))
                b = text.encode("utf-8")
                with open(os.path.join(d, "text.txt"), "wb") as fh:
                    fh.write(b)
                meta.update(state="HELD" if text.strip() else "EMPTY_BODY", xml_sha256=hashlib.sha256(xml.encode("utf-8")).hexdigest(),
                            text_sha256=hashlib.sha256(b).hexdigest(), chars=len(text),
                            licence=rl.jats_licence(os.path.join(d, "pmc.xml")))
    elif "state" not in meta:
        meta["state"] = "NO_PMCID"
    with open(os.path.join(d, "meta.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=1, sort_keys=True)
    return meta


UPW_CACHE = os.path.join(STORE, "_upw")
UPW_INDEX = os.path.join(STORE, "_upw_index.json")
ACQ_UPW = os.environ.get("ROBGRADE_SEED_UPW")       # optional: another lane's local Unpaywall cache, read only


def acquire_unpaywall(pmid, doi):
    """A legitimate OA copy through Unpaywall (kgap.k_gap.unpaywall_text, PDF or HTML -> text), for a trial PMC does not
    hold. Seeded read-only from another lane's local cache when one is named (same sha1(doi) key), else fetched.
    Licence: the Unpaywall location's own 'license' field; anything not cc-* is NOT_OPEN (regex only, as always here)."""
    import shutil
    from kgap import k_gap
    os.makedirs(UPW_CACHE, exist_ok=True)
    key = hashlib.sha1(doi.lower().encode("utf-8")).hexdigest()[:16]
    if ACQ_UPW and os.path.exists(os.path.join(ACQ_UPW, key + ".txt")) and not os.path.exists(os.path.join(UPW_CACHE, key + ".txt")):
        shutil.copyfile(os.path.join(ACQ_UPW, key + ".txt"), os.path.join(UPW_CACHE, key + ".txt"))
    r = k_gap.unpaywall_text(doi, UPW_CACHE, UPW_INDEX)
    text = r.get("text") or ""
    d = store_path(pmid)
    os.makedirs(d, exist_ok=True)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8")) if os.path.exists(os.path.join(d, "meta.json")) else {"pmid": str(pmid)}
    if text.strip():
        b = text.encode("utf-8")
        with open(os.path.join(d, "text.txt"), "wb") as fh:
            fh.write(b)
        lic = str(r.get("license") or "")
        meta.update(state="HELD", via="Unpaywall OA copy", doi=doi, source_url=r.get("url") or r.get("source_url"),
                    text_sha256=hashlib.sha256(b).hexdigest(), chars=len(text),
                    licence="CC" if lic.lower().startswith("cc") else f"NOT_OPEN ({lic or 'no licence stated'})",
                    pmc_state=meta.get("state"))
    else:
        meta.update(upw_state=r.get("state") or "NO_OA_TEXT", doi=doi)
    with open(os.path.join(d, "meta.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=1, sort_keys=True)
    return meta


def calibration_pmids():
    cal = json.load(open(os.path.join(ROOT, "outputs", "robgrade", "calibration.json"), encoding="utf-8"))
    return sorted({p["pmid"] for p in cal["pairs"]})


def main(argv):
    pmids = [a for a in argv if not a.startswith("--")] or (calibration_pmids() if "--calibration" in argv else [])
    from collections import Counter
    c = Counter()
    for p in pmids:
        _, m = held(p)
        if m is None or (m.get("state") != "HELD" and "--retry" in argv):
            m = acquire(p)
        if m.get("state") != "HELD" and "--unpaywall" in argv and not m.get("upw_state"):
            mem = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "member_records.json"), encoding="utf-8"))
            doi = ((mem.get(p) or {}).get("doi") or "").strip()
            if doi:
                m = acquire_unpaywall(p, doi)
        c[(m.get("state"), m.get("licence"))] += 1
        print(p, m.get("state"), m.get("licence"), m.get("chars"), flush=True)
    print(dict(c))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
