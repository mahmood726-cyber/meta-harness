"""Dated, append-preserving G1 search evidence; no extraction or admission.

Hardcode disclosure:
  Static | source URLs, transport policy, discovery aliases, PMDA ruling date.
  Dynamic | identifiers, OA flags, approval evidence, holdings and secondary rows.
Offline reads HEAD artefacts only; it never refreshes a network response. Restricted
regulator artefacts cross the metadata boundary only through regulator_summary.
An open copy with no outcome assessment is OPEN_NOT_ASSESSED.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urlparse, unquote
from urllib.request import Request, build_opener, HTTPRedirectHandler
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from scripts.g1_explanation_vocab import (STATES, REASON_CODES, STEPS, ACCESS_OUTCOMES, SOURCES, FRESH_DAYS)
from scripts.g1_regulatory_source import file_lock, AGENCY_LICENCE, PROMPT_OPEN, topic_agents
from scripts.g1_tracker import route_group

EMAIL = "meta-harness@example.org"
USER_AGENT = "meta-harness k-gap (meta-harness@example.org)"
META_FIELDS = ("label", "phase", "stage", "decision", "verdict", "ncts")
PROBE_DATE = "2026-10-15T00:00:00Z"
PMDA_NOTE = "PMDA skipped by Mahmood 13 Oct; re-ruling requested 15 Oct"
TTL = 7 * 86400


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def iso_z(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def digest(body):
    return hashlib.sha256(body).hexdigest()


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")


def valid_doi(value):
    return isinstance(value, str) and re.fullmatch(r"10\.\d{4,9}/\S+", value) is not None


def clean_identifier_dois(ids):
    """Fail closed on malformed provider identifiers; retain search history."""
    ids["dois"] = sorted({v for v in ids.get("dois", []) if valid_doi(v)})
    if "provenance" in ids:
        known = {v for key in ("pmids", "dois", "ncts", "eudract") for v in ids.get(key, [])}
        ids["provenance"] = {k: v for k, v in ids["provenance"].items() if k in known}


class Committed:
    """Snapshot all file names at HEAD; never use uncommitted identifier changes."""
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.head = self.git("rev-parse", "HEAD").decode().strip()
        self.paths = set(self.git("ls-tree", "-r", "--name-only", self.head).decode().splitlines())
        self.cache = {}

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def body(self, path):
        key = str(path).replace("\\", "/")
        if key not in self.paths:
            return None
        if key not in self.cache:
            self.cache[key] = self.git("show", f"{self.head}:{key}")
        return self.cache[key]

    def read(self, path, default=None):
        body = self.body(path)
        return json.loads(body) if body is not None else default

    def matching(self, pattern):
        import fnmatch
        return sorted(p for p in self.paths if fnmatch.fnmatchcase(p, pattern))

    def when(self, path):
        value = self.git("log", "-1", "--format=%cI", self.head, "--", str(path)).decode().strip()
        if not value:
            raise ValueError(f"No committed date for {path}")
        return iso_z(value)


def regulator_summary(path, read_bytes=None):
    """Return only allowed scalar metadata and the typed ncts identifier list.

    No document, candidate, reader or span field is accessed or returned. The JSON
    decoder necessarily consumes the enclosing file; its payload is never logged.
    """
    body = read_bytes(path) if read_bytes else Path(path).read_bytes()
    if body is None:
        return []
    rows = json.loads(body).get("rows", [])
    return [{key: ([n for n in row.get(key, []) if isinstance(n, str) and re.fullmatch(r"NCT\d{8}", n)]
                  if isinstance(row.get(key), list) else []) if key == "ncts" else row.get(key) if isinstance(row.get(key), (str, int, float, bool, type(None)))
             else None for key in META_FIELDS} for row in rows]


def record(source, query, when, step, outcome, body=None, sha=None):
    if source not in SOURCES or step not in STEPS + ACCESS_OUTCOMES:
        raise ValueError((source, step))
    return {"source": source, "identifier_or_query": query, "when_utc": iso_z(when),
            "step_reached": step, "outcome": outcome,
            "response_sha256": sha if sha is not None else digest(body) if body is not None else None}


def safe_url(url):
    emails = re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", unquote(url))
    if any(e != EMAIL for e in emails) or urlparse(url).username:
        raise ValueError("Unapproved email or credentials in request")
    if urlparse(url).scheme != "https":
        raise ValueError("HTTPS required")
    return url


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl)
        # A redirect is still a request: preserve per-host politeness.
        self.client.pause(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self, directory, opener=None, sleep=time.sleep, clock=time.monotonic):
        self.directory = Path(directory)
        self.sleep, self.clock, self.last = sleep, clock, {}
        redirect = SafeRedirect()
        redirect.client = self
        self.opener = opener or build_opener(redirect)

    def pause(self, url):
        host = urlparse(url).netloc
        delay = .34 - (self.clock() - self.last.get(host, -1e9))
        if delay > 0:
            self.sleep(delay)
        self.last[host] = self.clock()

    def get(self, url):
        safe_url(url)
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / (digest(url.encode()) + ".json")
        if path.exists():
            item = json.loads(path.read_text(encoding="utf-8"))
            age = time.time() - datetime.fromisoformat(item["when_utc"].replace("Z", "+00:00")).timestamp()
            if 0 <= age < TTL:
                return item["status"], base64.b64decode(item["body"]), item["when_utc"]
        for attempt in range(3):
            self.pause(url)
            when = utc_now()
            try:
                with self.opener.open(Request(url, headers={"User-Agent": USER_AGENT}), timeout=45) as response:
                    status, body = response.status, response.read()
            except HTTPError as exc:
                status, body = exc.code, exc.read()
                if (status == 429 or status >= 500) and attempt == 2:
                    raise
            if status == 429 or status >= 500:
                if attempt < 2:
                    self.sleep(2 ** attempt)
                    continue
            if 200 <= status < 300:
                atomic_json(path, {"status": status, "when_utc": when,
                                   "body": base64.b64encode(body).decode("ascii")})
            return status, body, when


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def merge_write(path, new):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(str(path)):
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"slug": new["slug"], "trials": {}}
        if old["slug"] != new["slug"]:
            raise ValueError("slug mismatch")
        for label, trial in new["trials"].items():
            if label not in old["trials"]:
                old["trials"][label] = copy.deepcopy(trial)
                continue
            dst = old["trials"][label]
            for key, val in trial["identifiers"].items():
                prior = dst["identifiers"].get(key)
                if key == "provenance":
                    merged = copy.deepcopy(prior or {})
                    for identifier, sources in val.items():
                        merged[identifier] = sorted(set(merged.get(identifier, []) + sources))
                    dst["identifiers"][key] = merged
                    continue
                dst["identifiers"][key] = sorted(set((prior or []) + val)) if isinstance(val, list) else (
                    bool(prior or val) if key == "approved_drug" else val or prior)
            dst["secondary_value_available"] |= trial["secondary_value_available"]
            for row in trial["searched"]:
                if row not in dst["searched"]:
                    dst["searched"].append(row)
        for trial in old["trials"].values():
            clean_identifier_dois(trial["identifiers"])
        old["written_utc"] = new["written_utc"]
        atomic_json(path, old)
        return old


def open_step(census):
    assessments = census if isinstance(census, list) else [census]
    assessment = " ".join(str(row.get(k) or "") for row in assessments for k in ("blocker_now", "decision", "stage", "outcome"))
    if "EXTRACTION" in assessment or "TYPED_NONE" in assessment:
        return "OPEN_OUTCOME_NOT_BINDABLE"
    if "OUTCOME_NOT_IN_SOURCE" in assessment:
        return "OPEN_NO_OUTCOME"
    return "OPEN_NOT_ASSESSED"


def challenge(body):
    return bool(re.search(rb"captcha|cloudflare|challenge-platform|verify (?:that )?you are human|access denied|request blocked|cf-chl|bot challenge", body, re.I))


def response_mapping(source, body, status=200, census=None, identifiers=None):
    """Pure source adapters, deliberately returning metadata rather than report text."""
    census, identifiers = census or {}, identifiers or {}
    if challenge(body):
        return "BLOCKED_BOT_CHALLENGE", "Public endpoint served a bot/access challenge"
    if status == 404:
        return "NOT_FOUND", "HTTP 404"
    if status != 200:
        return "ERROR", f"HTTP {status}"
    if source == "WHO_ICTRP":
        if re.search(rb"no (?:records|results|trials) found|0 records found", body, re.I):
            return "NOT_FOUND", "Public search explicitly reports no results"
        if re.search(rb"<script\b|javascript", body, re.I):
            return "BLOCKED_JS_ONLY", "ICTRP public page requires JavaScript"
        return "ERROR", "ValueError: unparseable ICTRP response; no results or JavaScript shell"
    try:
        obj = json.loads(body)
    except (ValueError, UnicodeError) as exc:
        return "ERROR", f"{type(exc).__name__}: {exc}"
    if not isinstance(obj, dict):
        return "ERROR", "ValueError: expected a JSON object"
    if source.startswith("PUBMED_EPMC"):
        hits = obj.get("resultList", {}).get("result", [])
        if "hitCount" not in obj or not isinstance(hits, list):
            return "ERROR", "Missing Europe PMC response schema"
        if not hits:
            return "NOT_FOUND", {"hits": obj["hitCount"]}
        if source == "PUBMED_EPMC_TITLE":
            names = identifiers.get("ncts", []) + [identifiers[k] for k in ("acronym", "title") if identifiers.get(k)]
            matches = set()
            for hit in hits[:25]:
                text = " ".join(str(hit.get(k) or "") for k in ("title", "abstractText"))
                if any(re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", text, re.I) for n in names):
                    pmid = str(hit.get("pmid") or hit.get("id") or "")
                    if (hit.get("pmid") or hit.get("source", "MED") == "MED") and re.fullmatch(r"[1-9]\d{0,8}", pmid):
                        matches.add(pmid)
            new = sorted(matches - set(map(str, identifiers.get("pmids", []))))
            return ("NEW_REPORT_FOUND" if new else "NOT_FOUND"), {
                "hits": obj["hitCount"], "examined": min(25, len(hits)),
                "reports_naming_trial": sorted(matches), "new_pmids": new,
                "outcome": "new report" if new else "no additional report" if matches else "no hit naming the trial"}
        hit = hits[0]
        meta = {k: hit.get(k) for k in ("id", "isOpenAccess", "license", "pmcid", "inEPMC", "doi")}
        if meta.get("doi") and not valid_doi(meta["doi"]):
            meta["reported_doi"] = meta["doi"]
            meta["doi"] = None
            meta["doi_validation_error"] = "Malformed provider DOI; not used as an identifier"
        meta["copy"] = ("https://europepmc.org/articles/" + hit["pmcid"]) if hit.get("pmcid") else hit.get("fullTextUrlList")
        if identifiers.get("pmid") and str(hit.get("id")) != identifiers["pmid"]:
            return "ERROR", "Europe PMC PMID mismatch"
        opened = hit.get("isOpenAccess") == "Y" or hit.get("inEPMC") == "Y"
        return (open_step(census) if opened else "FOUND_NOT_OPEN"), meta
    if source == "UNPAYWALL_DOI":
        if not isinstance(obj.get("is_oa"), bool):
            return "ERROR", "Missing Unpaywall is_oa"
        return (open_step(census) if obj["is_oa"] else "FOUND_NOT_OPEN"), {
            "copy": (obj.get("best_oa_location") or {}).get("url_for_pdf") or (obj.get("best_oa_location") or {}).get("url"),
            "is_oa": obj["is_oa"], "license": (obj.get("best_oa_location") or {}).get("license"),
            "outcome_assessment": "census only"}
    if source == "CTGOV_V2":
        nct = obj.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
        if not nct or identifiers.get("nct") and nct != identifiers["nct"]:
            return "ERROR", "CT.gov identifier missing or mismatched"
        present = bool(obj.get("resultsSection"))
        if obj.get("hasResults") is True and not present:
            return "ERROR", {"hasResults": True, "resultsSection_present": False, "error": "Inconsistent results metadata"}
        return ("OPEN_OUTCOME_NOT_BINDABLE" if present else "OPEN_NO_OUTCOME"), {
            "hasResults": obj.get("hasResults"), "resultsSection_present": present,
            "binding": "not assessed by search fetcher"}
    if source in ("EUCTR", "AACT"):
        state = obj.get("state")
        step = {"RESULTS": "OPEN_OUTCOME_NOT_BINDABLE", "NO_RESULTS": "OPEN_NO_OUTCOME",
                "PARSE_FAILED": "ERROR"}.get(state, "ERROR")
        meta = {"state": state}
        if step == "ERROR":
            meta["error"] = obj.get("reason") or f"Unparseable {source} response state: {state!r}"
        return step, meta
    return "ERROR", "Unrecognised source response"


def search(client, source, url, census=None, identifiers=None):
    when = utc_now()
    try:
        status, body, when = client.get(url)
        step, outcome = response_mapping(source, body, status, census, identifiers)
        return record(source, url, when, step, outcome, body), body
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return record(source, url, when, "ERROR", f"{type(exc).__name__}: {exc}"), None


def rows(obj):
    return obj if isinstance(obj, list) else (obj or {}).get("rows", [])


def identifier_fields(obj, source="", provenance=None):
    """Mine selected identity fields, excluding candidate/background/comparator data."""
    found = {"pmids": set(), "ncts": set(), "eudract": set()}
    def add(kind, value, field):
        found[kind].add(value)
        if provenance is not None:
            provenance.setdefault(value, set()).add(source + "#" + field)
    def walk(value, key="", field=""):
        if isinstance(value, dict):
            for k, v in value.items():
                if k not in ("candidates", "background_only", "comparator", "comparator_pmid", "meta_pmid"):
                    walk(v, k, field + "." + k if field else k)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, key, f"{field}[{i}]")
        elif isinstance(value, (str, int)):
            text = str(value)
            if key.lower() in ("pmid", "pmids", "report_pmid", "primary_pmid") and re.fullmatch(r"[1-9]\d{0,8}", text):
                add("pmids", text, field)
            if key in ("family", "identity"):
                for pmid in re.findall(r"\bPMID\s+(\d{1,9})\b", text):
                    add("pmids", pmid, field)
            for kind, pattern in (("ncts", r"\bNCT\d{8}\b"), ("eudract", r"\b\d{4}-\d{6}-\d{2}\b")):
                for value in re.findall(pattern, text):
                    add(kind, value, field)
    walk(obj)
    return found


def source_rows(repo, pattern):
    result = []
    for path in repo.matching(pattern):
        obj = repo.read(path)
        for i, row in enumerate(rows(obj)):
            result.append({**row, "slug": row.get("slug") or (obj.get("slug") if isinstance(obj, dict) else None),
                           "_source": path, "_field": f"rows[{i}]"})
    return result


def identifiers(trial, slug, identification, census, eu_probe, funnels=(), regulator=()):
    provenance = {}
    found = {"pmids": set(), "ncts": set(), "eudract": set()}
    def harvest(obj, source, field=""):
        extra = identifier_fields({field: obj} if field else obj, source, provenance)
        for key in found:
            found[key].update(extra[key])
    tracker = f"outputs/k_gap/g1/{slug}.json"
    harvest({k: trial.get(k) for k in ("family", "identity", "acquisition_cascade", "identification", "pmid", "ncts")}, tracker, f"trials[label={trial['label']}]")
    identity = trial.get("identity") if isinstance(trial.get("identity"), dict) else {}
    from scripts.g1_regulatory_source import _label_acronyms
    title = identity.get("title") or trial["label"]
    acronyms = sorted(_label_acronyms(trial["label"]), key=lambda s: (-len(s), s))
    acronym = identity.get("acronym") or (acronyms[0] if acronyms else "")
    for collection, fallback, fields in (
        (identification, "outputs/k_gap/registry_fill/IDENTIFICATION.json", ("pmid", "report_pmid", "identified", "ncts", "companions", "protocol")),
        (funnels, f"outputs/k_gap/registry_fill/{slug}.funnel.json", ("ncts", "eudract", "eudract_numbers")),
        (regulator, f"registry/g1_acquired_regulator/{slug}.json", ("ncts",))):
        for i, row in enumerate(collection):
            if row.get("slug", slug) == slug and row.get("label") == trial["label"]:
                harvest({k: row.get(k) for k in fields}, row.get("_source", fallback), row.get("_field", f"rows[{i}]"))
                title = row.get("title") or title
    dois = set()
    for i, row in enumerate(census):
        doi = (row.get("europepmc") or {}).get("doi")
        if str(row.get("pmid")) in found["pmids"] and valid_doi(doi):
            dois.add(doi)
            provenance.setdefault(doi, set()).add(row.get("_source", "outputs/k_gap/registry_fill/PHASE3_OPEN_CENSUS.json") + "#" + row.get("_field", f"rows[{i}]") + ".europepmc.doi")
    eu_path = "outputs/k_gap/registry_fill/EUDRACT_PROBE.json"
    for i, row in enumerate(eu_probe.get("trials", [])):
        if row.get("slug") == slug and row.get("label") == trial["label"]:
            harvest({k: row.get(k) for k in ("label", "ncts", "nct", "results")}, eu_path, f"trials[{i}]")
    for i, row in enumerate(eu_probe.get("ncts_probed", [])):
        # A shared EU number can describe multiple trials: reverse joins are unsafe.
        if row.get("nct") in found["ncts"]:
            harvest({k: row.get(k) for k in ("nct", "eudract_numbers")}, eu_path, f"ncts_probed[{i}]")
    return {**{k: sorted(v) for k, v in found.items()}, "dois": sorted(dois),
            "provenance": {k: sorted(v) for k, v in sorted(provenance.items())},
            "title": title, "acronym": acronym, "approved_drug": False}


def holding_record(row, path, when):
    agency = str(row.get("phase") or "").split(":")[-1]
    if agency not in ("FDA", "EMA"):
        return None
    stage = row.get("stage") or ""
    if stage == "MISSING":
        step = "NOT_FOUND"
    elif stage.startswith("NAMED"):
        step = "OPEN_NO_OUTCOME" if AGENCY_LICENCE.get(agency) in PROMPT_OPEN else "FOUND_NOT_OPEN"
    elif stage in ("READ", "TYPED") and row.get("verdict") != "ADMITTED":
        step = "OPEN_OUTCOME_NOT_BINDABLE"
    else:
        step = "ERROR"
    return record(agency, path, when, step, row, encoded(row))


DISCOVERY = {"TGA AusPARs": "TGA_AUSPAR", "FDA Advisory Committee briefing documents": "FDA_ADCOMM",
             "NIHR HTA": "AHRQ_NIHR_HTA", "AHRQ EPC": "AHRQ_NIHR_HTA"}
SPONSORS = ("Pfizer", "Regeneron", "Bayer", "GSK", "Novartis", "Lilly", "Boehringer Ingelheim",
            "Novo Nordisk", "Amgen", "AstraZeneca", "Sanofi", "Roche/Genentech")


def discovery_record(row, when=PROBE_DATE):
    source = DISCOVERY.get(row.get("source")) or ("SPONSOR_REGISTER" if row.get("source") in SPONSORS else None)
    status = row.get("status")
    if not source or status == "NOT_APPLICABLE" or not row.get("url"):
        return None
    step = status if status in STEPS + ACCESS_OUTCOMES else {
        "NAMED_NO_DATA": "OPEN_NO_OUTCOME", "PER_ARM_TARGET": "OPEN_OUTCOME_NOT_BINDABLE",
        "PER_ARM_OTHER": "OPEN_OUTCOME_NOT_BINDABLE"}.get(status, "ERROR")
    if step == "ERROR":
        evidence = row.get("how_checked") or ""
        if re.search(r"(?:without|requires?) JavaScript|JavaScript application shell", evidence, re.I):
            step = "BLOCKED_JS_ONLY"
        elif re.search(r"HTTP 403", evidence) and re.search(r"Request blocked|CloudFront", evidence, re.I):
            step = "BLOCKED_BOT_CHALLENGE"
    if step == "NOT_FOUND" and not row.get("how_checked"):
        return None
    return record(source, row["url"], row.get("when_utc") or row.get("retrieved_utc") or row.get("date") or when,
                  step, {k: row.get(k) for k in ("source", "status", "licence_or_terms", "outcome_match_note", "how_checked")},
                  sha=row.get("response_sha256"))


class Approval:
    def __init__(self, client):
        self.client, self.agents, self.ema = client, {}, None

    def approved(self, agent):
        from scripts.k_gap_regulatory_probe import ema_products, EMA_JSON
        if agent in self.agents:
            return self.agents[agent]
        url = "https://api.fda.gov/drug/drugsfda.json?" + urlencode({"search": f'openfda.generic_name:"{agent}"', "limit": 1000})
        status, body, _ = self.client.get(url)
        if status not in (200, 404):
            raise ValueError("openFDA approval lookup failed")
        approved = any(str(r.get("application_number", "")).startswith(("NDA", "BLA"))
                       for r in json.loads(body).get("results", []))
        if not approved:
            if self.ema is None:
                status, body, _ = self.client.get(EMA_JSON)
                if status != 200:
                    raise ValueError("EMA approval lookup failed")
                obj = json.loads(body)
                self.ema = obj if isinstance(obj, list) else obj.get("data") or obj.get("medicines") or []
            approved = bool(ema_products([agent], self.ema))
        self.agents[agent] = approved
        return approved


def secondary_available(trial, phase4):
    return route_group(trial.get("route")) in ("SECONDARY_SINGLE", "TWO_SOURCE") or any(
        r.get("label") == trial["label"] and r.get("value") is not None and
        (str(r.get("class", "")).startswith("SECONDARY_PROVISIONAL") or r.get("secondary_value_available") is True)
        for r in phase4)


def live_searches(client, ids, census):
    result = []
    for pmid in ids["pmids"]:
        row = [r for r in census if str(r.get("pmid")) == pmid]
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode({
            "query": f"EXT_ID:{pmid} SRC:MED", "resultType": "core", "format": "json"})
        rec, body = search(client, "PUBMED_EPMC_PMID", url, row, {"pmid": pmid})
        result.append(rec)
        if isinstance(rec["outcome"], dict) and valid_doi(rec["outcome"].get("doi")):
            ids["dois"] = sorted(set(ids["dois"] + [rec["outcome"]["doi"]]))
            ids.setdefault("provenance", {}).setdefault(rec["outcome"]["doi"], []).append(url + "#resultList.result[0].doi")
    query = ids["acronym"] or ids["title"]
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode({
        "query": 'TITLE:"' + query.replace('"', ' ') + '"', "pageSize": 25, "resultType": "core", "format": "json", "sort": "ID asc"})
    result.append(search(client, "PUBMED_EPMC_TITLE", url, identifiers=ids)[0])
    for doi in ids["dois"]:
        row = [r for r in census if r.get("europepmc", {}).get("doi") == doi]
        result.append(search(client, "UNPAYWALL_DOI", "https://api.unpaywall.org/v2/" + quote(doi, safe="") +
                             "?" + urlencode({"email": EMAIL}), row)[0])
    from scripts import g1_eudract_source as eu
    for nct in ids["ncts"]:
        url = "https://clinicaltrials.gov/api/v2/studies/" + nct
        result.append(search(client, "CTGOV_V2", url, identifiers={"nct": nct})[0])
        # Reuse identifier parser, routing every helper request through this transport.
        def fetch(url):
            status, body, _ = client.get(url)
            if status != 200:
                raise HTTPError(url, status, "Identifier request failed", None, None)
            return body
        try:
            with patch.object(eu, "_fetch", fetch):
                discovered = eu.eudract_numbers([nct], [])
                ids["eudract"] = sorted(set(ids["eudract"] + [r["eudract_no"] for r in discovered]))
                for item in discovered:
                    sources = ids.setdefault("provenance", {}).setdefault(item["eudract_no"], [])
                    sources.extend(p["url"] + "#" + p["field"] for p in item["provenance"])
                    ids["provenance"][item["eudract_no"]] = sorted(set(sources))
        except HTTPError as exc:
            step = "NOT_FOUND" if exc.code == 404 else "BLOCKED_BOT_CHALLENGE" if exc.code == 403 else "ERROR"
            result.append(record("EUCTR", nct, utc_now(), step, f"{type(exc).__name__}: {exc}"))
        except (OSError, ValueError, KeyError) as exc:
            result.append(record("EUCTR", nct, utc_now(), "ERROR", f"EudraCT identifier discovery failed: {type(exc).__name__}: {exc}"))
    if ids["ncts"]:
        from kgap import aact_adapter
        when = utc_now()
        try:
            aact_adapter.snapshot_dir()
            aact_adapter.ensure(ids["ncts"])
            for nct in ids["ncts"]:
                data = aact_adapter.registry_for(nct)
                meta = {"state": "RESULTS" if data and data.get("outcomes") else "NO_RESULTS",
                        "snapshot": (data or {}).get("_snapshot")}
                step, _ = response_mapping("AACT", encoded(meta))
                result.append(record("AACT", nct, when, step, meta, encoded(meta)))
        except (OSError, ValueError, KeyError) as exc:
            result.extend(record("AACT", nct, when, "ERROR", f"AACT snapshot unavailable: {type(exc).__name__}: {exc}") for nct in ids["ncts"])
    for no in ids["eudract"]:
        url = eu.BASE + "/ctr-search/trial/" + no + "/results"
        when = utc_now()
        try:
            status, body, when = client.get(url)
            if challenge(body) or status != 200:
                step, outcome = response_mapping("EUCTR", body, status)
            else:
                # Disable the helper's independent 30-day cache; retain our URL cache.
                with patch.object(eu, "CACHE_DIR", client.directory / "euctr"), patch.object(eu, "TTL", 0), patch.object(eu, "_fetch", lambda _: body):
                    parsed = eu.eudract_results(no)
                step, outcome = response_mapping("EUCTR", encoded({"state": parsed["state"], "reason": parsed.get("reason")}))
            result.append(record("EUCTR", url, when, step, outcome, body))
        except (OSError, ValueError, KeyError) as exc:
            result.append(record("EUCTR", url, when, "ERROR", f"EU CTR request/parser failed: {type(exc).__name__}: {exc}"))
    result.append(search(client, "WHO_ICTRP", "https://trialsearch.who.int/?" + urlencode({"query": query}))[0])
    return result


def health_canada(client, agent):
    """Public listing only; never follow a submission link or accept terms."""
    from scripts import g1_regulatory_source as reg
    url = reg.HC_SEARCH + "?dpq=" + quote(agent, safe="")
    when = utc_now()
    try:
        status, body, when = client.get(url)
        if status == 200 and not challenge(body):
            with patch.object(reg, "_hc_fetch", lambda _: body.decode("utf-8", "replace")), patch.object(reg, "_reg_dir", lambda: client.directory / "hc"):
                submissions = reg.hc_listing(agent)
            return record("HEALTH_CANADA", url, when, "BLOCKED_TERMS", {"submissions": submissions}, body)
        return record("HEALTH_CANADA", url, when, "BLOCKED_BOT_CHALLENGE" if challenge(body) else "ERROR", f"HTTP {status}", body)
    except (OSError, ValueError) as exc:
        return record("HEALTH_CANADA", url, when, "ERROR", f"{type(exc).__name__}: {exc}")


def run(slugs=None, offline=False, root=ROOT):
    repo = Committed(root)
    fill = "outputs/k_gap/registry_fill/"
    identification = source_rows(repo, fill + "IDENTIFICATION*.json")
    funnels = source_rows(repo, fill + "*.funnel.json")
    census = source_rows(repo, fill + "PHASE3_OPEN_CENSUS*.json")
    for path in repo.matching(fill + "phase3*/*.json"):
        obj = repo.read(path)
        for row in rows(obj):
            for base in census:
                slug = obj.get("slug") if isinstance(obj, dict) else row.get("slug")
                if base.get("slug") == slug and base.get("label") == row.get("label") and str(base.get("pmid")) == str(row.get("pmid")):
                    base.update({k: row[k] for k in ("stage", "decision") if k in row})
    phase4 = [r for p in repo.matching(fill + "*SECONDARY*.json") + repo.matching(fill + "phase4_*/*.json") for r in rows(repo.read(p))]
    probes = rows(repo.read("outputs/k_gap/regulatory_probe.json", {}))
    eu_probe = repo.read(fill + "EUDRACT_PROBE.json", {})
    samples = {r["id"]: r for r in repo.read(fill + "discovery/sample.json", {}).get("trials", [])}
    discovery = []
    for path in repo.matching(fill + "discovery/job_*.results.jsonl"):
        for line in repo.body(path).splitlines():
            if line.strip():
                r = json.loads(line)
                sample = samples.get(r.get("trial_id"), {})
                if sample.get("label") == r.get("label"):
                    discovery.append((sample.get("topic"), r))
    client = None if offline else Client(Path(root) / "outputs/k_gap/_search_log_cache")
    approval = Approval(client) if client else None
    paths = repo.matching("outputs/k_gap/g1/*.json")
    if slugs:
        paths = [f"outputs/k_gap/g1/{s}.json" for s in slugs]
    current_trials = []
    for path in paths:
        topic = repo.read(path)
        if topic is None or "trials" not in topic:
            raise ValueError(f"Missing committed tracker: {path}")
        slug = topic["slug"]
        agents = topic_agents(repo.read(f"topics/{slug}.json", {}))
        approved = any(r.get("slug") == slug and r.get("ema_products") for r in probes)
        if approval:
            approved = any(approval.approved(agent) for agent in agents) or approved
        holding_path = f"registry/g1_acquired_regulator/{slug}.json"
        summaries = regulator_summary(holding_path, repo.body)
        holding_time = repo.when(holding_path) if summaries else None
        out = {"slug": slug, "written_utc": utc_now(), "trials": {}}
        for trial in topic["trials"]:
            if route_group(trial.get("route")) == "PRIMARY":
                continue
            label = trial["label"]
            local_census = [r for r in census if r.get("slug") == slug and r.get("label") == label]
            ids = identifiers(trial, slug, identification, local_census, eu_probe, funnels, summaries)
            ids["approved_drug"] = approved
            searched = []
            if client:
                searched.extend(live_searches(client, ids, local_census))
            for row in summaries:
                if row.get("label") == label:
                    rec = holding_record(row, holding_path, holding_time)
                    if rec:
                        searched.append(rec)
            if approved:
                searched.append(record("PMDA", "policy decision", PROBE_DATE, "NOT_ATTEMPTED_PENDING_DECISION", PMDA_NOTE))
                searched.append(record("EMA_CLINICAL_DATA", "https://clinicaldata.ema.europa.eu/", PROBE_DATE,
                                       "BLOCKED_ACCOUNT", "Public clinical data portal requires account; no login attempted"))
                for source_slug, row in discovery:
                    if source_slug == slug and row.get("label") == label:
                        rec = discovery_record(row)
                        if rec:
                            searched.append(rec)
                # Public listing is metadata only. Offline may use it only if committed.
                hc_path = "outputs/k_gap/_reg/hc_listing.json"
                hc = repo.read(hc_path, {})
                for agent in agents:
                    meta = hc.get(agent.casefold())
                    if meta is not None:
                        searched.append(record("HEALTH_CANADA", agent, repo.when(hc_path), "BLOCKED_TERMS",
                                               {"submissions": meta.get("rows", []), "error": meta.get("error")}, encoded(meta)))
                    elif client:
                        searched.append(health_canada(client, agent))
            out["trials"][label] = {"identifiers": ids, "searched": searched,
                                      "secondary_value_available": secondary_available(trial, [r for r in phase4 if r.get("slug") == slug])}
        current_trials.extend(out["trials"].values())
        merged = merge_write(Path(root) / "registry/g1_search_log" / (slug + ".json"), out)
        recs = [r for t in merged["trials"].values() for r in t["searched"]]
        print(f"{slug}: trials={len(merged['trials'])}, records={len(recs)}, sources covered={','.join(sorted({r['source'] for r in recs})) or '(none)'}")

    from collections import Counter
    print(f"CURRENT RUN: trials={len(current_trials)}, trials with NCT={sum(bool(t['identifiers']['ncts']) for t in current_trials)}")
    counts = Counter((r["source"], r["step_reached"]) for t in current_trials for r in t["searched"])
    outcomes = Counter((r["source"], r["step_reached"], json.dumps(r["outcome"], sort_keys=True))
                       for t in current_trials for r in t["searched"])
    for (source, step), count in sorted(counts.items()):
        print(f"{source} | {step} | {count}")
    for (source, step, outcome), count in sorted(outcomes.items()):
        print(f"OUTCOME | {source} | {step} | {count} | {outcome}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--slugs", nargs="+")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    if args.slugs and any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s) for s in args.slugs):
        parser.error("Invalid slug")
    run(args.slugs, args.offline)


if __name__ == "__main__":
    main()
