"""Shared open-full-text acquisition cascade (owned by the captain lane; topic lanes consume it).

WHY (2026-10-02). G1 tocilizumab read NO_PRIMARY_SOURCE for 12 of 19 comparator trials. Two of those are open in PMC
(RECOVERY PMC8084355, REMAP-CAP PMC7953461). The defects were in the shared cascade (scripts/lane_fulltext.py), as a
CLASS, not in the topic:
  1. every exception was swallowed and the trial counted "no_open_access": a throttled or failed request (NCBI allows
     3 requests/s without a key; the old loop made ~5/s) was recorded as a fact about the article;
  2. targets were only trials already in our outcomes, so a comparator's trial we never retrieved was never tried;
  3. one route (NCBI elink + efetch) and no record of WHY a text is missing.
This cascade replaces that: typed per-PMID states, bounded retry with backoff on 429/5xx/timeouts, a request-rate cap,
routes tried in order and each logged per trial (PMC via NCBI efetch -> Europe PMC fullTextXML -> Unpaywall OA PDF by
DOI; registry results status by NCT via CT.gov and by ISRCTN, numbers then read from the versioned AACT snapshot by the
topic lane), a target set that includes the comparator's trials, and a ledger.

States (cache/<slug>/fulltext_ledger.json, one row per PMID):
  HELD           a full text was already held (cache/<slug>/ft_<pmid>.txt); nothing fetched
  FETCHED        JATS with a <body> fetched now and written to ft_<pmid>.txt (route + sha256 recorded)
  NOT_IN_PMC     PubMed->PMC elink answered and names no same-article PMC record ('pubmed_pmc_refs' are CITING papers)
  NO_BODY        a PMC record exists but no route returned an article body (publisher-restricted or stub)
  FETCH_FAILED   a request failed after retries: says nothing about the article; re-run, never read as absence

NETWORK at acquisition time only. Replays read the held bytes and the ledger. `--dry-run` resolves and reports without
writing. Writing held full texts into a topic whose held texts are enabled can move served numbers on rebuild: those go
through DERIVED notices like any other change.

Usage: python scripts/fulltext_cascade.py SLUG [SLUG ...] [--dry-run] [--stage DIR] [--report OUT.json]
                                        [--pmids P1,P2] [--ncts N1,N2]
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "meta-harness/1.0 (research; fulltext cascade)"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EPMC_FT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
HELD, FETCHED, NOT_IN_PMC, NO_BODY, FETCH_FAILED = "HELD", "FETCHED", "NOT_IN_PMC", "NO_BODY", "FETCH_FAILED"
# a text taken OUT of the tree by a signed D8 decision (V12-08Q): carried forward from the previous ledger, never re-acquired
REMOVED_FROM_TREE_D8 = "REMOVED_FROM_TREE_D8"
STATES = (HELD, FETCHED, NOT_IN_PMC, NO_BODY, FETCH_FAILED, REMOVED_FROM_TREE_D8)
RETRY_STATUS = {429, 500, 502, 503, 504}


class FetchFailed(Exception):
    """A request failed after bounded retries: a fact about the request, never about the article."""


class Http:
    """GET with a request-rate cap and bounded retry/backoff. Injectable for tests."""

    def __init__(self, min_interval: float | None = None, tries: int = 4, backoff: float = 1.5, sleep=time.sleep):
        key = os.environ.get("NCBI_API_KEY")
        self.key = key
        self.min_interval = min_interval if min_interval is not None else (0.11 if key else 0.34)  # 10/s or 3/s
        self.tries, self.backoff, self.sleep = tries, backoff, sleep
        self._last = 0.0

    def get(self, url: str, params: dict | None = None, timeout: int = 60) -> bytes:
        params = dict(params or {})
        if self.key and url.startswith(EUTILS):
            params["api_key"] = self.key
        full = url + ("?" + urllib.parse.urlencode(params) if params else "")
        last = None
        for attempt in range(self.tries):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                self.sleep(wait)
            self._last = time.monotonic()
            try:
                with urllib.request.urlopen(urllib.request.Request(full, headers=UA), timeout=timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as exc:
                last = f"HTTP {exc.code}"
                if exc.code not in RETRY_STATUS:
                    raise FetchFailed(f"{last} for {url}") from exc
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                last = f"{type(exc).__name__}: {exc}"
            self.sleep(self.backoff * (2 ** attempt))
        raise FetchFailed(f"{last} after {self.tries} tries for {url}")


def resolve_pmcid(http: Http, pmid: str) -> str | None:
    """The article's OWN PMC id, or None when PubMed answers that it has none. Raises FetchFailed when it could not ask."""
    raw = http.get(EUTILS + "elink.fcgi", {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "retmode": "json",
                                            "linkname": "pubmed_pmc"})
    d = json.loads(raw.decode("utf-8"))
    for ls in (d.get("linksets") or [{}])[0].get("linksetdbs", []) or []:
        if ls.get("linkname") == "pubmed_pmc" and ls.get("links"):
            return str(ls["links"][0])
    return None


def has_body(xml: str) -> bool:
    return bool(re.search(r"<body[\s>]", xml or ""))


def fetch_body(http: Http, pmcid: str) -> tuple[str | None, str | None, list[str]]:
    """(xml, route, notes): NCBI efetch JATS first, Europe PMC fullTextXML second; the first WITH a <body> wins."""
    notes = []
    for route, getter in (("NCBI_EFETCH_PMC", lambda: http.get(EUTILS + "efetch.fcgi",
                                                                 {"db": "pmc", "id": pmcid, "retmode": "xml"})),
                          ("EUROPEPMC_FULLTEXTXML", lambda: http.get(EPMC_FT.format(pmcid=f"PMC{pmcid}")))):
        try:
            xml = getter().decode("utf-8", "replace")
        except FetchFailed as exc:
            notes.append(f"{route}: {exc}")
            continue
        if has_body(xml):
            return xml, route, notes
        notes.append(f"{route}: no <body> ({len(xml)} bytes)")
    return None, None, notes


def pmids_for_nct(http: Http, nct: str) -> list[str]:
    """PubMed records that carry this registration in their secondary-id field."""
    raw = http.get(EUTILS + "esearch.fcgi", {"db": "pubmed", "term": f"{nct}[si]", "retmode": "json", "retmax": 20})
    return list(json.loads(raw.decode("utf-8")).get("esearchresult", {}).get("idlist", []))


def targets(slug: str, root: Path = ROOT) -> dict[str, list[str]]:
    """{pmid: [why ...]}: our outcomes' trials, screened-in records, the topic's positive controls, and the comparator
    meta's trials where a lane has bound them to PMIDs (registry/secondary_meta/<slug>.json)."""
    out: dict[str, list[str]] = {}

    def add(pid, why):
        pid = str(pid or "").replace("PMID", "").strip()
        if pid.isdigit():
            out.setdefault(pid, [])
            if why not in out[pid]:
                out[pid].append(why)

    rv = root / "docs" / "reviews" / slug / "review.json"
    if rv.is_file():
        r = json.loads(rv.read_text(encoding="utf-8"))
        for o in r.get("outcomes") or []:
            for k in ("trials", "declared_absent_trials"):
                for t in o.get(k) or []:
                    add(t.get("id"), "our outcome")
        for rec in (r.get("screening") or {}).get("records") or []:
            if rec.get("decision") == "include":
                add(rec.get("id"), "screened in")
    topic = root / "topics" / f"{slug}.json"
    if topic.is_file():
        for p in json.loads(topic.read_text(encoding="utf-8")).get("positive_control_pmids") or []:
            add(p, "positive control")
    sm = root / "registry" / "secondary_meta" / f"{slug}.json"
    if sm.is_file():
        text = sm.read_text(encoding="utf-8")
        for p in re.findall(r'"(?:pmid|trial_pmid|report_pmid)"\s*:\s*"?(\d{6,9})', text):
            add(p, "comparator trial (secondary_meta)")
    return out


UNPAYWALL = "https://api.unpaywall.org/v2/{doi}"
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CTGOV = "https://clinicaltrials.gov/api/v2/studies/{nct}"
ISRCTN_API = "https://www.isrctn.com/api/query/format/default"
CONTACT = os.environ.get("UNPAYWALL_EMAIL", "meta-harness@example.org")


def identifiers(slug: str, pmid: str, root: Path = ROOT) -> dict:
    """DOI / NCT / ISRCTN for a PMID from the held records (no network)."""
    p = root / "cache" / slug / "records.json"
    if not p.is_file():
        return {}
    for r in json.loads(p.read_text(encoding="utf-8")).get("records") or []:
        if str(r.get("id")) == pmid:
            text = " ".join(str(r.get(k) or "") for k in ("abstract", "secondary_ids"))
            isr = re.search(r"ISRCTN\s?(\d{8})", text)
            return {"doi": r.get("doi"), "nct": r.get("nct"), "isrctn": f"ISRCTN{isr.group(1)}" if isr else None}
    return {}


def doi_from_epmc(http: Http, pmid: str) -> str | None:
    d = json.loads(http.get(EPMC_SEARCH, {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json"}).decode("utf-8"))
    res = (d.get("resultList") or {}).get("result") or []
    return res[0].get("doi") if res else None


def unpaywall_pdf(http: Http, doi: str) -> tuple[bytes | None, dict]:
    """(pdf bytes or None, location): the best OA location Unpaywall names, fetched when it is a PDF."""
    d = json.loads(http.get(UNPAYWALL.format(doi=urllib.parse.quote(doi)), {"email": CONTACT}).decode("utf-8"))
    loc = d.get("best_oa_location") or {}
    info = {"is_oa": d.get("is_oa"), "url": loc.get("url_for_pdf") or loc.get("url"), "host_type": loc.get("host_type"),
            "license": loc.get("license")}
    if not (d.get("is_oa") and loc.get("url_for_pdf")):
        return None, info
    data = http.get(loc["url_for_pdf"])
    return (data if data[:5] == b"%PDF-" else None), dict(info, pdf=data[:5] == b"%PDF-")


def registry_status(http: Http, ident: dict) -> dict:
    """Whether the registry holds results (CT.gov v2 hasResults; ISRCTN record). Numbers are read from the versioned
    AACT snapshot by the topic lane (kgap/aact_adapter), never from this live call."""
    out = {}
    if ident.get("nct"):
        try:
            d = json.loads(http.get(CTGOV.format(nct=ident["nct"]), {"fields": "hasResults"}).decode("utf-8"))
            out["ctgov"] = {"nct": ident["nct"], "has_results": bool(d.get("hasResults"))}
        except FetchFailed as exc:
            out["ctgov"] = {"nct": ident["nct"], "state": FETCH_FAILED, "error": str(exc)}
    if ident.get("isrctn"):
        try:
            x = http.get(ISRCTN_API, {"q": ident["isrctn"]}).decode("utf-8", "replace")
            out["isrctn"] = {"id": ident["isrctn"], "record": "totalCount=\"1\"" in x,
                             "results_mentioned": bool(re.search(r"<results|basicResults|publicationPlan", x))}
        except FetchFailed as exc:
            out["isrctn"] = {"id": ident["isrctn"], "state": FETCH_FAILED, "error": str(exc)}
    return out


def _write(data: bytes, dest: Path, dry_run: bool, root: Path):
    if dry_run:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest.relative_to(root).as_posix() if dest.is_relative_to(root) else str(dest)


def acquire(http: Http, slug: str, pmid: str, dry_run: bool, root: Path = ROOT, stage: Path | None = None,
            ident: dict | None = None) -> dict:
    """One trial report through the cascade: PMC (NCBI) -> Europe PMC -> Unpaywall OA PDF; registry results status by
    NCT (CT.gov) / ISRCTN alongside. Every route tried is logged in `routes`."""
    held = root / "cache" / slug / f"ft_{pmid}.txt"
    base = (stage / slug) if stage else (root / "cache" / slug)
    row = {"pmid": pmid, "routes": []}
    if held.is_file():
        return dict(row, state=HELD, sha256=hashlib.sha256(held.read_bytes()).hexdigest())
    ident = dict(ident if ident is not None else identifiers(slug, pmid, root))
    if ident.get("nct") or ident.get("isrctn"):
        row["registry"] = registry_status(http, ident)
    failures, pmc_record = 0, False
    try:
        pmcid = resolve_pmcid(http, pmid)
        row["routes"].append({"route": "PMC_ELINK", "outcome": f"PMC{pmcid}" if pmcid else "no same-article PMC record"})
    except FetchFailed as exc:
        pmcid, failures = None, failures + 1
        row["routes"].append({"route": "PMC_ELINK", "outcome": FETCH_FAILED, "error": str(exc)})
    if pmcid:
        pmc_record = True
        row["pmcid"] = f"PMC{pmcid}"
        xml, route, notes = fetch_body(http, pmcid)
        row["routes"] += [{"route": n.split(":", 1)[0], "outcome": n.split(":", 1)[1].strip()} for n in notes]
        failures += sum(1 for n in notes if "after" in n or "HTTP" in n)
        if xml is not None:
            data = xml.encode("utf-8")
            row["routes"].append({"route": route, "outcome": "body"})
            return dict(row, state=FETCHED, route=route, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                        written=_write(data, base / f"ft_{pmid}.txt", dry_run, root))
    doi = ident.get("doi")
    if not doi:
        try:
            doi = doi_from_epmc(http, pmid)
        except FetchFailed as exc:
            failures += 1
            row["routes"].append({"route": "EUROPEPMC_DOI", "outcome": FETCH_FAILED, "error": str(exc)})
    if doi:
        row["doi"] = doi
        try:
            pdf, loc = unpaywall_pdf(http, doi)
            row["routes"].append({"route": "UNPAYWALL", "outcome": "pdf" if pdf else "no OA pdf", **loc})
            if pdf:
                return dict(row, state=FETCHED, route="UNPAYWALL_PDF", bytes=len(pdf),
                            sha256=hashlib.sha256(pdf).hexdigest(),
                            written=_write(pdf, base / f"ft_{pmid}.pdf", dry_run, root))
        except FetchFailed as exc:
            failures += 1
            row["routes"].append({"route": "UNPAYWALL", "outcome": FETCH_FAILED, "error": str(exc)})
    tried = len([r for r in row["routes"] if r["route"] in ("PMC_ELINK", "NCBI_EFETCH_PMC", "EUROPEPMC_FULLTEXTXML",
                                                             "UNPAYWALL", "EUROPEPMC_DOI")])
    if tried and failures == tried:
        return dict(row, state=FETCH_FAILED)
    return dict(row, state=NO_BODY if pmc_record else NOT_IN_PMC)


def run(slug: str, http: Http, dry_run: bool = False, extra_pmids=(), extra_ncts=(), root: Path = ROOT,
        stage: Path | None = None) -> dict:
    tg = targets(slug, root)
    for p in extra_pmids:
        tg.setdefault(str(p), []).append("named on the command line")
    for nct in extra_ncts:
        try:
            for p in pmids_for_nct(http, nct):
                tg.setdefault(p, []).append(f"registration {nct} (PubMed secondary id)")
        except FetchFailed as exc:
            tg.setdefault(f"NCT:{nct}", []).append(f"FETCH_FAILED resolving {nct}: {exc}")
    prev = root / "cache" / slug / "fulltext_ledger.json"
    removed = {}
    if prev.is_file():
        removed = {str(r.get("pmid")): r for r in (json.loads(prev.read_text(encoding="utf-8")).get("rows") or [])
                   if r.get("state") == REMOVED_FROM_TREE_D8}
    rows = []
    for pmid in sorted(set(tg) | set(removed)):
        if pmid in removed:
            rows.append(removed[pmid])
            continue
        if not pmid.isdigit():
            rows.append({"pmid": pmid, "state": FETCH_FAILED, "why": tg[pmid]})
            continue
        rows.append(dict(acquire(http, slug, pmid, dry_run, root, stage), why=tg[pmid]))
    tally = {s: sum(r["state"] == s for r in rows) for s in STATES}
    ledger = {"slug": slug, "run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "dry_run": dry_run, "staged_to": str(stage) if stage else None, "tally": tally, "rows": rows}
    if not dry_run:
        # the LEDGER is always written to the topic (staged or not: nothing in the build reads it); staged TEXTS stay in
        # the stage until a topic lane admits them (captain order 8 Oct: a per-slug ledger on every run)
        (root / "cache" / slug).mkdir(parents=True, exist_ok=True)
        (root / "cache" / slug / "fulltext_ledger.json").write_text(json.dumps(ledger, indent=1) + "\n",
                                                                   encoding="utf-8", newline="\n")
    return ledger


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true", help="every topic with docs/reviews/<slug>/review.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pmids", default="")
    ap.add_argument("--ncts", default="")
    ap.add_argument("--stage", help="write fetched texts to STAGE/<slug>/ft_<pmid>.txt instead of cache/<slug>/ "
                                    "(a topic lane reviews them before admitting: held texts feed served pages)")
    ap.add_argument("--report", help="write every topic's ledger to this JSON file (also in --dry-run)")
    a = ap.parse_args(argv)
    if a.all:
        a.slugs = sorted(p.parent.name for p in (ROOT / "docs" / "reviews").glob("*/review.json"))
    if not a.slugs:
        ap.error("name topics or pass --all")
    http = Http()
    rc = 0
    stage = Path(a.stage).resolve() if a.stage else None
    report = {}
    for slug in a.slugs:
        led = run(slug, http, a.dry_run, [p for p in a.pmids.split(",") if p], [n for n in a.ncts.split(",") if n],
                  stage=stage)
        report[slug] = led
        print(f"{slug}: {led['tally']} ({'dry run' if a.dry_run else 'staged' if stage else 'ledger written'})",
              flush=True)
        rc |= 1 if led["tally"][FETCH_FAILED] else 0
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
