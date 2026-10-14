"""Re-acquire open JATS replacements without modifying the served cache.

Responses are immutable in-memory captures before interpretation. Rejected bodies
are never persisted; their hashes and transport metadata remain in the manifest.
Existing dated manifests are refused: use a new date for a subsequent acquisition.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
from pathlib import Path
import re
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.copy_licence import classify_permissions  # noqa: E402
from harness.source_coverage import label_document  # noqa: E402

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
OA = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id="
HOSTS = {"www.ebi.ac.uk", "www.ncbi.nlm.nih.gov", "ftp.ncbi.nlm.nih.gov"}
MAX_BYTES = 64 * 1024 * 1024


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return p.scheme == "https" and p.hostname in HOSTS and not p.username and p.port in (None, 443)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Record redirects as outcomes; do not follow a challenge to another site.
        return None


def utc():
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Capture:
    payload: bytes
    requested_url: str
    final_url: str
    status: int | None
    headers: tuple
    started: str
    ended: str
    error: str | None = None

    def metadata(self):
        h = dict(self.headers)
        length = h.get("content-length")
        declared = int(length) if length and length.isdigit() else None
        encoding = re.search(br"encoding\s*=\s*['\"]([^'\"]+)", self.payload[:200])
        return dict(requested_url=self.requested_url, final_url=self.final_url,
                    http_status=self.status, content_type=h.get("content-type"),
                    declared_encoding=encoding.group(1).decode("ascii", "replace") if encoding else None,
                    acquired_utc={"start": self.started, "end": self.ended},
                    sha256=hashlib.sha256(self.payload).hexdigest(), bytes=len(self.payload),
                    content_length=declared, truncated=declared is not None and declared != len(self.payload),
                    error=self.error)


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(NoRedirect())
        self.last = None

    def fetch(self, url, route, attempts):
        if not safe_url(url):
            raise ValueError("unapproved acquisition URL")
        for number in range(3):
            if self.last is not None:
                time.sleep(max(0, 0.5 - (time.monotonic() - self.last)))
            self.last = time.monotonic()
            start = utc()
            try:
                try:
                    response = self.opener.open(urllib.request.Request(
                        url, headers={"User-Agent": "meta-harness-reacquire/1"}), timeout=60)
                except urllib.error.HTTPError as exc:
                    response = exc
                with response as resp:
                    error = None
                    try:
                        raw = resp.read(MAX_BYTES + 1)
                    except http.client.IncompleteRead as exc:
                        raw, error = exc.partial, "INCOMPLETE_READ"
                    if len(raw) > MAX_BYTES:
                        error = "SIZE_LIMIT"
                    cap = Capture(raw, url, resp.geturl(), resp.code,
                                  tuple((k.lower(), v) for k, v in resp.headers.items()), start, utc(), error)
            except (urllib.error.URLError, OSError, TimeoutError) as exc:
                cap = Capture(b"", url, url, None, (), start, utc(), type(exc).__name__)
            meta = cap.metadata()
            meta.update(route=route, attempt=number + 1, stored=False,
                        licence="NOT_OPEN", label=None, outcome="RESPONSE")
            attempts.append(meta)
            if cap.status == 429 or cap.status is not None and 500 <= cap.status <= 599:
                meta["outcome"] = "HTTP_ERROR"
                if number < 2:
                    time.sleep(2 ** number)
                    continue
            return cap, meta


def usable(cap, meta):
    if cap.error or meta["truncated"]:
        meta["outcome"] = cap.error or "TRUNCATED"
    elif cap.status != 200:
        meta["outcome"] = "HTTP_ERROR"
    elif not safe_url(cap.final_url):
        meta["outcome"] = "UNAPPROVED_FINAL_URL"
    elif (dict(cap.headers).get("content-type", "").split(";", 1)[0].strip().lower() == "text/html"
          or re.match(br"\s*(?:<\?xml\b[^>]*>\s*)?(?:<!--.*?-->\s*)*<(?:html|!doctype\s+html)\b",
                      cap.payload[:10000], re.I | re.S)):
        meta["outcome"] = "HTML_OR_CHALLENGE"
    else:
        return True
    meta["label"] = label_document(cap.payload)["label"]
    return False


def assess(raw, doc, pmcid, meta):
    meta["label"] = label_document(raw)["label"]
    try:
        tree = ET.fromstring(raw)
    except (ET.ParseError, LookupError):
        meta.update(licence="NOT_OPEN", outcome="INVALID_XML")
        return False
    # Normalize namespaces/attributes for the canonical permissions reader.
    permissions = []
    for el in tree.iter():
        if el.tag.split("}")[-1] == "permissions":
            permissions.append("<permissions>" + "".join(ET.tostring(c, encoding="unicode") for c in el)
                               + (el.text or "") + "</permissions>")
    text = ET.tostring(tree, encoding="unicode")
    lic, statement = classify_permissions("".join(permissions) + "\n" + text)
    meta.update(licence=lic, licence_statement=statement)
    ids = {}
    # Only the enclosing article's direct front/article-meta owns its identity.
    own_ids = tree.findall("./{*}front/{*}article-meta/{*}article-id") if tree.tag.split("}")[-1] == "article" else []
    for el in own_ids:
        ids.setdefault(el.get("pub-id-type"), set()).add((el.text or "").strip())
    pmc_ids = {v if v.startswith("PMC") else "PMC" + v for v in ids.get("pmc", set()) | ids.get("pmcid", set())}
    matched = (ids.get("pmid") == {doc["pmid"]} if doc.get("pmid") else pmc_ids == {pmcid})
    if pmc_ids and pmc_ids != {pmcid}:
        matched = False
    meta["returned_identifiers"] = {k: sorted(v) for k, v in ids.items() if k in ("pmid", "pmc", "pmcid")}
    if lic != "CC":
        meta["outcome"] = "LICENCE_REJECTED"
    elif tree.get("article-type") == "author-manuscript" or re.search(r"NIHMS\d+|author.manuscript", text, re.I):
        meta["outcome"] = "AUTHOR_MANUSCRIPT"
    elif meta["label"] != "FULLTEXT":
        meta["outcome"] = "NOT_FULLTEXT"
    elif not matched:
        meta["outcome"] = "IDENTIFIER_MISMATCH"
    else:
        meta["outcome"] = "ACCEPTED"
        return True
    return False


def _write_once(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as f:
            f.write(raw)
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ValueError(f"REFUSED: immutable acquisition differs: {path}")


def selected(registry, slug=None, pmids=None):
    docs = registry["documents"]
    items = docs.items() if isinstance(docs, dict) else ((d.get("path", ""), d) for d in docs)
    out = []
    for path, original in items:
        if original.get("label") not in {"STUB", "METADATA"}:
            continue
        doc = dict(original, path=path)
        parts = Path(path).parts
        doc["slug"] = doc.get("slug") or (parts[1] if len(parts) > 2 and parts[0] == "cache" else None)
        m = re.search(r"(?:^|/)ft_(\d+)\.", path)
        if not m:
            m = re.search(r"^cache/comparators/(\d+)/", path)
        doc["pmid"] = str(doc.get("pmid") or (m.group(1) if m else ""))
        doc["pmcid"] = str(doc.get("pmcid") or "")
        if not doc["pmid"] and not doc["pmcid"]:
            continue
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", doc["slug"] or ""):
            raise ValueError("invalid slug")
        for key, pattern in (("pmid", r"[1-9]\d*"), ("pmcid", r"PMC[1-9]\d*")):
            if doc[key] and not re.fullmatch(pattern, doc[key]):
                raise ValueError(f"invalid {key}")
        if (slug is None or doc["slug"] == slug) and (pmids is None or doc["pmid"] in pmids):
            out.append(doc)
    return sorted(out, key=lambda d: (d["slug"], d["pmid"], d["pmcid"], d["path"]))


def acquire(doc, client):
    entry = dict(source_path=doc["path"], pmid=doc["pmid"], pmcid=doc["pmcid"],
                 attempts=[], stored=False, outcome="NO_REPLACEMENT")
    attempts = entry["attempts"]
    pmcid = doc["pmcid"]
    if doc["pmid"]:
        url = EPMC + "search?query=EXT_ID:" + doc["pmid"] + "%20AND%20SRC:MED&format=json&resultType=core"
        cap, meta = client.fetch(url, "europepmc_search", attempts)
        if not usable(cap, meta):
            return entry, None
        try:
            results = json.loads(cap.payload)["resultList"]["result"]
            if not isinstance(results, list) or any(not isinstance(record, dict) for record in results):
                raise ValueError("search results must be a list of objects")
            matches = [r for r in results if str(r.get("id")) == doc["pmid"] and r.get("source") == "MED"]
            if len(matches) != 1 or not re.fullmatch(r"PMC[1-9]\d*", matches[0].get("pmcid", "")):
                raise ValueError("no unique PMID match")
            record = matches[0]
            if pmcid and pmcid != record["pmcid"]:
                raise ValueError("conflicting PMCID")
            pmcid = record["pmcid"]
            meta.update(outcome="RESOLVED", pmcid=pmcid, isOpenAccess=record.get("isOpenAccess"),
                        source_license=record.get("license"))
        except (ValueError, KeyError, TypeError):
            meta["outcome"] = "UNRESOLVED_IDENTIFIER"
            return entry, None
    entry["pmcid"] = pmcid
    cap, meta = client.fetch(EPMC + pmcid + "/fullTextXML", "europepmc_fulltext", attempts)
    if usable(cap, meta) and assess(cap.payload, doc, pmcid, meta):
        return entry, cap.payload
    # A denial/challenge terminates this document, not an invitation to route around it.
    if cap.status == 403 or meta["outcome"] == "HTML_OR_CHALLENGE":
        return entry, None
    cap, meta = client.fetch(OA + pmcid, "pmc_oa_service", attempts)
    if not usable(cap, meta):
        return entry, None
    try:
        tree = ET.fromstring(cap.payload)
        records = [r for r in tree.findall(".//record") if r.get("id") == pmcid]
        if len(records) != 1:
            raise ValueError("no unique OA record")
        links = [el for el in records[0].findall("link") if el.get("format") == "tgz"]
        if not links:
            raise ValueError("no JATS package")
        url = links[0].get("href", "")
        if url.startswith("ftp://ftp.ncbi.nlm.nih.gov/"):
            url = "https://" + url[len("ftp://"):]
        if not safe_url(url) or urllib.parse.urlsplit(url).hostname != "ftp.ncbi.nlm.nih.gov":
            raise ValueError("unapproved package")
        meta["outcome"] = "OA_PACKAGE_LINK"
    except (ET.ParseError, LookupError, ValueError):
        meta["outcome"] = "NO_OA_PACKAGE"
        return entry, None
    cap, meta = client.fetch(url, "pmc_oa_package", attempts)
    if not usable(cap, meta):
        return entry, None
    try:
        with tarfile.open(fileobj=io.BytesIO(cap.payload), mode="r:gz") as archive:
            members = [m for m in archive if m.isfile() and m.name.lower().endswith((".nxml", ".xml"))]
            if len(members) != 1 or members[0].size > MAX_BYTES:
                raise ValueError("ambiguous or oversized JATS package")
            raw = archive.extractfile(members[0]).read()
            candidate = dict(route="pmc_oa_jats", member=members[0].name,
                             sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), stored=False)
            attempts.append(candidate)
            if assess(raw, doc, pmcid, candidate):
                return entry, raw
    except (tarfile.TarError, ValueError, OSError, EOFError):
        meta["outcome"] = "INVALID_OA_PACKAGE"
    return entry, None


def run(registry, output, *, slug=None, pmids=None, dry_run=False, date=None):
    docs = selected(registry, slug, pmids)
    if dry_run:
        for doc in docs:
            print(f"{doc['slug']} {doc['pmid'] or doc['pmcid']}: Europe PMC search/fullTextXML -> NCBI PMC OA")
        return []
    date = date or datetime.now(timezone.utc).date().isoformat()
    datetime.strptime(date, "%Y-%m-%d")
    dirs = {d["slug"]: Path(output) / d["slug"] / ("fulltext_" + date) for d in docs}
    for directory in dirs.values():
        if (directory / "manifest.json").exists():
            raise ValueError("REFUSED: dated manifest already exists; choose a new acquisition date")
    client = Client()
    entries = {slug: [] for slug in dirs}
    for doc in docs:
        entry, raw = acquire(doc, client)
        if raw is not None:
            name = (doc["pmid"] or doc["pmcid"]) + ".xml"
            _write_once(dirs[doc["slug"]] / name, raw)
            entry.update(stored=True, file=name, outcome="STORED", sha256=hashlib.sha256(raw).hexdigest())
            entry["attempts"][-1]["stored"] = True
        else:
            entry["outcome"] = entry["attempts"][-1]["outcome"]
        last = entry["attempts"][-1]
        entry.update(licence=last.get("licence"), label=last.get("label"),
                     sha256=last["sha256"], reason=last["outcome"])
        entries[doc["slug"]].append(entry)
    for slug, directory in dirs.items():
        manifest = dict(schema_version=1, slug=slug, acquisition_date=date, entries=entries[slug],
                        origin_authentication="Declared TLS trust; hashes identify received bytes, not independent origin proof")
        _write_once(directory / "manifest.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return [e for group in entries.values() for e in group]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", type=Path, default=ROOT / "registry/source_coverage.json")
    ap.add_argument("--slug")
    ap.add_argument("--pmids", nargs="+", help="space- or comma-separated PMIDs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    pmids = {p for group in args.pmids for p in group.split(",")} if args.pmids else None
    run(json.loads(args.registry.read_text(encoding="utf-8")), ROOT / "registry/source_acquisitions",
        slug=args.slug, pmids=pmids, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
