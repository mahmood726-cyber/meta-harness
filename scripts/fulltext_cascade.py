"""Shared open-full-text acquisition cascade (owned by the captain lane; topic lanes consume it).

WHY (2026-10-02). G1 tocilizumab read NO_PRIMARY_SOURCE for 12 of 19 comparator trials. Two of those are open in PMC
(RECOVERY PMC8084355, REMAP-CAP PMC7953461). The defects were in the shared cascade (scripts/lane_fulltext.py), as a
CLASS, not in the topic:
  1. every exception was swallowed and the trial counted "no_open_access": a throttled or failed request (NCBI allows
     3 requests/s without a key; the old loop made ~5/s) was recorded as a fact about the article;
  2. targets were only trials already in our outcomes, so a comparator's trial we never retrieved was never tried;
  3. one route (NCBI elink + efetch) and no record of WHY a text is missing.
This cascade replaces that: typed per-PMID states, bounded retry with backoff on 429/5xx/timeouts, a request-rate cap,
two independent routes, a target set that includes the comparator's trials, and a ledger.

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
STATES = (HELD, FETCHED, NOT_IN_PMC, NO_BODY, FETCH_FAILED)
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


def acquire(http: Http, slug: str, pmid: str, dry_run: bool, root: Path = ROOT, stage: Path | None = None) -> dict:
    held = root / "cache" / slug / f"ft_{pmid}.txt"
    dest = (stage / slug / f"ft_{pmid}.txt") if stage else held
    row = {"pmid": pmid}
    if held.is_file():
        dest = held
        return dict(row, state=HELD, sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    try:
        pmcid = resolve_pmcid(http, pmid)
    except FetchFailed as exc:
        return dict(row, state=FETCH_FAILED, error=str(exc), step="elink")
    if not pmcid:
        return dict(row, state=NOT_IN_PMC)
    xml, route, notes = fetch_body(http, pmcid)
    row.update(pmcid=f"PMC{pmcid}", notes=notes)
    if xml is None:
        failed = [n for n in notes if "after" in n or "HTTP" in n]
        return dict(row, state=FETCH_FAILED if len(failed) == len(notes) and notes else NO_BODY)
    data = xml.encode("utf-8")
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return dict(row, state=FETCHED, route=route, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                written=(None if dry_run else dest.relative_to(root).as_posix() if dest.is_relative_to(root) else str(dest)))


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
    rows = []
    for pmid in sorted(tg):
        if not pmid.isdigit():
            rows.append({"pmid": pmid, "state": FETCH_FAILED, "why": tg[pmid]})
            continue
        rows.append(dict(acquire(http, slug, pmid, dry_run, root, stage), why=tg[pmid]))
    tally = {s: sum(r["state"] == s for r in rows) for s in STATES}
    ledger = {"slug": slug, "run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "dry_run": dry_run, "tally": tally, "rows": rows}
    if not dry_run and stage is None:
        (root / "cache" / slug / "fulltext_ledger.json").write_text(json.dumps(ledger, indent=1) + "\n",
                                                                   encoding="utf-8", newline="\n")
    return ledger


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pmids", default="")
    ap.add_argument("--ncts", default="")
    ap.add_argument("--stage", help="write fetched texts to STAGE/<slug>/ft_<pmid>.txt instead of cache/<slug>/ "
                                    "(a topic lane reviews them before admitting: held texts feed served pages)")
    ap.add_argument("--report", help="write every topic's ledger to this JSON file (also in --dry-run)")
    a = ap.parse_args(argv)
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
