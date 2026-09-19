"""Capture-first acquisition objects for the served evidence bundle (fifth audit, 2026-09-19).

Two findings drive this script:

1. A row identifier and its hash do not provide the row contents needed to recompute that hash. The certificate-named
   cache/<slug>/aact_inputs.json carries {keys, sha256} per AACT source row and no bodies -- a reference that resolves
   to a promise. Resolvability is recursive: publishing records.json while it references unpublished bodies moves the
   404 one level down. This script re-selects those rows from the SAME snapshot (by name), recomputes each digest with
   the recorded method, refuses on any mismatch, and publishes the bodies.

2. The cached PubMed abstract for SOUL omits the safety sentence; the page's OUTCOME_NOT_IN_SOURCE for its
   gastrointestinal row is true of our cache and false of the cited abstract. The acquisition the cache was made from
   was never retained, so no preservation record can be built against it. This script acquires EFetch XML for every
   record as an IMMUTABLE acquisition object -- received payload, exact digest, requested and final addresses, time,
   content type, response status, declared encoding, truncation check (Content-Length vs received) -- created before
   any parsing. build_bundle.py then builds a preservation record (every abstract unit PRESERVED or MISSING) against
   it, which is what backs coverage_status instead of asserting it.

Limits, stated: a saved response and its hash establish WHAT WAS SAVED, not that it came from the claimed publisher.
Origin authentication needs an external observation or a declared trust assumption; this script records the latter
(TLS to eutils.ncbi.nlm.nih.gov; AACT static copy by folder name). The acquisitions here are POST-HOC (2026-09-19)
relative to the cache (2026-09-11); a difference between them is a discrepancy to record, not a fault to assign.

The acquisition store is append-only: an existing acquisition is never overwritten. Corrections create a new dated
version directory; old decisions keep the evidence they were made against.

Usage: python scripts/acquire_bundle_evidence.py <slug> [--pubmed] [--aact]   (default: both)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import aact  # noqa: E402
from harness.canonical import canonical_json, sha256_text  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
TOOL, EMAIL = "meta-harness-bundle", "meta-harness@example.org"  # the etiquette identity harness.fetch already uses
TODAY = time.strftime("%Y-%m-%d", time.gmtime())


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _write_once(path: Path, data: bytes) -> bool:
    """Append-only store: refuse to overwrite. Returns True if written, False if identical bytes already there."""
    if path.exists():
        if path.read_bytes() == data:
            return False
        raise SystemExit(f"REFUSED: {path.relative_to(ROOT).as_posix()} exists with different bytes; acquisitions are "
                         f"immutable -- create a new dated version directory instead")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def acquire_pubmed(slug: str) -> Path:
    records = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    pmids = sorted({str(r["id"]) for r in records["records"] if r.get("id_type", "pmid") == "pmid"})
    if records.get("comparator_pmid") and str(records["comparator_pmid"]) not in pmids:
        pmids.append(str(records["comparator_pmid"]))
    out_dir = ROOT / "docs" / "acquisitions" / slug / f"pubmed_efetch_{TODAY}"
    manifest_path = out_dir / "ACQUISITION.json"
    if manifest_path.exists():
        print(f"acquisition already exists: {manifest_path.relative_to(ROOT).as_posix()} (immutable; not repeated)")
        return out_dir
    entries = []
    for pmid in pmids:
        params = {"db": "pubmed", "id": pmid, "retmode": "xml", "tool": TOOL, "email": EMAIL}
        url = EUTILS + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": f"{TOOL}/1 ({EMAIL})", "Accept": "application/xml"})
        t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read()
            status = resp.status
            final_url = resp.geturl()
            headers = {k.lower(): v for k, v in resp.headers.items()}
        t1 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        declared_len = headers.get("content-length")
        truncation = {
            "content_length_header": int(declared_len) if declared_len and declared_len.isdigit() else None,
            "received_bytes": len(body),
            "transfer_encoding": headers.get("transfer-encoding"),
            "detected": (declared_len is not None and declared_len.isdigit() and int(declared_len) != len(body)),
            "well_formed_xml": None,
        }
        # Structural completeness of what was saved (not of the article): the document parses and closes.
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(body)
            truncation["well_formed_xml"] = True
            n_articles = len(root.findall(".//PubmedArticle"))
            returned_pmid = (root.findtext(".//PubmedArticle/MedlineCitation/PMID") or "").strip()
        except ET.ParseError:
            truncation["well_formed_xml"] = False
            n_articles, returned_pmid = 0, ""
        decl = body[:200].decode("ascii", "replace")
        encoding = "utf-8" if 'encoding="UTF-8"' in decl or "encoding='UTF-8'" in decl else "not declared in prolog"
        fname = f"{pmid}.xml"
        _write_once(out_dir / fname, body)
        entries.append({
            "identifier": {"pmid": pmid, "returned_pmid": returned_pmid, "n_articles_in_response": n_articles},
            "file": fname,
            "sha256": _sha256(body),
            "bytes": len(body),
            "requested_url": url.replace(EMAIL, "<email>"),
            "final_url": final_url.replace(EMAIL, "<email>"),
            "http_status": status,
            "content_type": headers.get("content-type"),
            "declared_encoding": encoding,
            "acquired_utc": {"start": t0, "end": t1},
            "truncation": truncation,
            "server_headers": {k: headers.get(k) for k in ("date", "last-modified", "etag", "ncbi-phid", "server") if k in headers},
        })
        print(f"  {pmid}: {status} {len(body)} B sha256 {entries[-1]['sha256'][:12]} pmid_returned={returned_pmid} "
              f"truncation_detected={truncation['detected']} xml_ok={truncation['well_formed_xml']}")
        time.sleep(0.4)
    manifest = {
        "schema_version": 1,
        "kind": "ACQUISITION",
        "slug": slug,
        "source": "PubMed E-utilities EFetch (db=pubmed, retmode=xml), one request per PMID",
        "acquired_by": "scripts/acquire_bundle_evidence.py",
        "acquisition_date": TODAY,
        "relation_to_cache": "POST-HOC: cache/<slug>/records.json was projected from EFetch responses on "
                             + str(records.get("fetched_utc")) + " which were not retained; these are fresh responses "
                             "and a difference between them and the cache is recorded as a discrepancy, not attributed",
        "origin_authentication": "DECLARED TRUST ASSUMPTION: TLS connection to eutils.ncbi.nlm.nih.gov; no external "
                                 "observation of origin; a saved response and its hash establish what was saved, not "
                                 "that it came from the claimed publisher",
        "immutability": "append-only; never overwritten; a correction is a new dated directory",
        "entries": entries,
    }
    _write_once(manifest_path, (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"wrote {manifest_path.relative_to(ROOT).as_posix()} ({len(entries)} responses)")
    return out_dir


def acquire_aact_rows(slug: str) -> Path:
    inputs = json.loads((ROOT / "cache" / slug / "aact_inputs.json").read_text(encoding="utf-8"))
    snapshot_name = inputs["snapshot"]
    snap = aact.snapshot_dir()
    if not snap or Path(snap).name != snapshot_name:
        raise SystemExit(f"REFUSED: local AACT snapshot is {snap!r}, aact_inputs.json was measured from {snapshot_name}; "
                         f"row bodies from a different snapshot would not reproduce the recorded digests")
    out_dir = ROOT / "docs" / "acquisitions" / slug / f"aact_rows_{snapshot_name}"
    manifest_path = out_dir / "ACQUISITION.json"
    if manifest_path.exists():
        print(f"acquisition already exists: {manifest_path.relative_to(ROOT).as_posix()} (immutable; not repeated)")
        return out_dir
    want = {n.upper() for n in inputs["requested_ncts"]}
    recorded = {t: {r["sha256"]: r["keys"] for r in rows} for t, rows in inputs["source_rows"].items()}
    bodies, unmatched, missing = {}, {}, {}
    for table, digests in recorded.items():
        found = {}
        for row in aact._iter_rows(str(Path(snap) / (table + ".txt"))):
            if (row.get("nct_id") or "").upper() not in want:
                continue
            h = sha256_text(canonical_json(row))
            if h in digests:
                found[h] = row
            else:
                unmatched.setdefault(table, []).append({"keys": {k: row[k] for k in ("nct_id", "id", "design_group_id", "intervention_id") if k in row}, "sha256": h})
        bodies[table] = [{"sha256": h, "keys": digests[h], "row": found[h]} for h in digests if h in found]
        lost = [h for h in digests if h not in found]
        if lost:
            missing[table] = lost
        print(f"  {table}: {len(found)}/{len(digests)} recorded rows re-selected and digest-matched"
              + (f"; {len(unmatched.get(table, []))} same-NCT rows in snapshot NOT in the recorded set" if unmatched.get(table) else ""))
    if missing:
        raise SystemExit(f"REFUSED: recorded digests with no matching body in snapshot {snapshot_name}: {missing}")
    payload = {
        "schema_version": 1,
        "kind": "AACT_SOURCE_ROW_BODIES",
        "slug": slug,
        "snapshot": snapshot_name,
        "row_hash_method": inputs["row_hash_method"],
        "resolves": f"cache/{slug}/aact_inputs.json#source_rows -- every {{keys, sha256}} there now has its header-keyed row body here; "
                    "sha256(canonical_json(row)) recomputes to the recorded digest for every row",
        "tables": bodies,
        "same_nct_rows_not_in_recorded_set": unmatched,
    }
    data = (json.dumps(payload, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    _write_once(out_dir / "rows.json", data)
    manifest = {
        "schema_version": 1,
        "kind": "ACQUISITION",
        "slug": slug,
        "source": f"local AACT static copy, snapshot folder {snapshot_name} (pipe-delimited table exports)",
        "acquired_by": "scripts/acquire_bundle_evidence.py",
        "acquisition_date": TODAY,
        "origin_authentication": "DECLARED TRUST ASSUMPTION: the snapshot folder was downloaded from "
                                 "aact.ctti-clinicaltrials.org by the author; the bundle proves only that these bodies "
                                 "hash to the digests recorded at measurement time from the same-named snapshot",
        "licence": "ClinicalTrials.gov data are US Government works; AACT redistributes them without restriction",
        "entries": [{"file": "rows.json", "sha256": _sha256(data), "bytes": len(data),
                     "rows": {t: len(v) for t, v in bodies.items()}}],
        "immutability": "append-only; never overwritten",
    }
    _write_once(manifest_path, (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"wrote {manifest_path.relative_to(ROOT).as_posix()}")
    return out_dir


def _source_references(obj, out):
    """Every {table, row_key, row_sha256, snapshot} reference reachable in a served object."""
    if isinstance(obj, dict):
        if "row_sha256" in obj and "table" in obj:
            out.append(obj)
        for v in obj.values():
            _source_references(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _source_references(v, out)


def acquire_review_source_rows(slug: str) -> Path:
    """Resolve the AACT rows review.json (trial_families) references by digest only -- the deeper level of the
    same defect. One streaming pass per referenced table, filtered to the referenced NCTs, hash-matched."""
    review = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
    refs = []
    _source_references(review, refs)
    snapshots = {r.get("snapshot") for r in refs}
    if len(snapshots) != 1:
        raise SystemExit(f"REFUSED: references span snapshots {snapshots}; one snapshot per resolution")
    snapshot_name = snapshots.pop()
    snap = aact.snapshot_dir()
    if not snap or Path(snap).name != snapshot_name:
        raise SystemExit(f"REFUSED: local AACT snapshot is {snap!r}, review.json references {snapshot_name}")
    out_dir = ROOT / "docs" / "acquisitions" / slug / f"aact_rows_{snapshot_name}"
    target = out_dir / "review_source_references.json"
    if target.exists():
        print(f"acquisition already exists: {target.relative_to(ROOT).as_posix()} (immutable; not repeated)")
        return out_dir
    by_table = {}
    for r in refs:
        by_table.setdefault(r["table"], {})[r["row_sha256"]] = r
    want = {str(r.get("nct_id") or "").upper() for r in refs} - {""}
    bodies, missing = {}, {}
    for table, digests in sorted(by_table.items()):
        path = Path(snap) / (table + ".txt")
        if not path.is_file():
            missing[table] = sorted(digests)
            continue
        found = {}
        t0 = time.time()
        for row in aact._iter_rows(str(path)):
            if (row.get("nct_id") or "").upper() not in want:
                continue
            h = sha256_text(canonical_json(row))
            if h in digests:
                found[h] = row
                if len(found) == len(digests):
                    break
        lost = sorted(h for h in digests if h not in found)
        if lost:
            missing[table] = lost
        bodies[table] = [{"sha256": h, "row_key": digests[h].get("row_key"), "nct_id": digests[h].get("nct_id"), "row": found[h]}
                         for h in sorted(digests) if h in found]
        print(f"  {table}: {len(found)}/{len(digests)} referenced rows re-selected and digest-matched ({time.time()-t0:.0f}s)", flush=True)
    payload = {
        "schema_version": 1,
        "kind": "AACT_SOURCE_ROW_BODIES",
        "slug": slug,
        "snapshot": snapshot_name,
        "row_hash_method": "sha256(canonical_json(header-keyed source row)); UTF-8",
        "resolves": f"every source_reference {{table, row_key, row_sha256, snapshot}} reachable in reviews/{slug}/review.json "
                    "(trial_families eligibility spans); sha256(canonical_json(row)) recomputes to row_sha256 for every row present",
        "referenced_rows": sum(len(v) for v in by_table.values()),
        "resolved_rows": sum(len(v) for v in bodies.values()),
        "unresolved": missing,
        "tables": bodies,
    }
    data = (json.dumps(payload, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    _write_once(target, data)
    # append an entry to the existing ACQUISITION.json is forbidden (immutable): write a sibling manifest instead
    manifest = {
        "schema_version": 1, "kind": "ACQUISITION", "slug": slug,
        "source": f"local AACT static copy, snapshot folder {snapshot_name}",
        "acquired_by": "scripts/acquire_bundle_evidence.py", "acquisition_date": TODAY,
        "origin_authentication": "DECLARED TRUST ASSUMPTION (see ACQUISITION.json in this directory)",
        "entries": [{"file": "review_source_references.json", "sha256": _sha256(data), "bytes": len(data),
                     "referenced_rows": payload["referenced_rows"], "resolved_rows": payload["resolved_rows"],
                     "unresolved_tables": sorted(missing)}],
        "immutability": "append-only; never overwritten",
    }
    _write_once(out_dir / "ACQUISITION.review_source_references.json", (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"wrote {target.relative_to(ROOT).as_posix()}: {payload['resolved_rows']}/{payload['referenced_rows']} rows; unresolved tables {sorted(missing)}")
    return out_dir


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--pubmed", action="store_true")
    ap.add_argument("--aact", action="store_true")
    ap.add_argument("--review-refs", action="store_true", help="resolve review.json AACT source_reference rows (slow: ~7 GB streamed)")
    a = ap.parse_args(argv)
    both = not (a.pubmed or a.aact or a.review_refs)
    if a.pubmed or both:
        acquire_pubmed(a.slug)
    if a.aact or both:
        acquire_aact_rows(a.slug)
    if a.review_refs or both:
        acquire_review_source_rows(a.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
