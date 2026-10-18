"""Dated, append-preserving G1 search evidence; no extraction or admission.

Hardcode disclosure:
  Static | source URLs, transport policy, sponsor mappings and text-match rules.
  Dynamic | identifiers, OA flags, approval evidence, holdings and secondary rows.
Offline reads HEAD artefacts only; it never refreshes a network response. Restricted
regulator artefacts cross the metadata boundary only through regulator_summary.
An open copy with no outcome assessment is OPEN_NOT_ASSESSED.
"""
from __future__ import annotations

import argparse
import base64
import copy
import csv
import io
import xml.etree.ElementTree as ET
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
from urllib.parse import quote, urlencode, urlparse, unquote, urljoin
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

    def prime(self, paths):
        """Read the selected HEAD objects in one Git process (same snapshot contract)."""
        paths = sorted(set(paths) & self.paths)
        if not paths:
            return
        query = "".join(f"{self.head}:{p}\n" for p in paths).encode()
        data = subprocess.check_output(["git", "-C", str(self.root), "cat-file", "--batch"], input=query, stderr=subprocess.PIPE)
        stream = io.BytesIO(data)
        for path in paths:
            header = stream.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise ValueError(f"Missing committed blob: {path}")
            size = int(header[2])
            body = stream.read(size)
            if len(body) != size or stream.read(1) != b"\n":
                raise ValueError(f"Truncated committed blob: {path}")
            self.cache[path] = body

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
        if re.search(r"abuse|captcha|challenge", newurl, re.I):
            raise BotBlock("Blocked redirect to " + newurl)
        # A redirect is still a request: preserve per-host politeness.
        self.client.pause(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class BotBlock(ValueError):
    pass


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
            except OSError:
                if urlparse(url).hostname == "www.tga.gov.au" and attempt < 2:
                    self.sleep(2 ** attempt)
                    continue
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
    except BotBlock as exc:
        return record(source, url, when, "BLOCKED_BOT_CHALLENGE", str(exc)), None
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



# Static endpoint/sponsor routing; all matches, licences and verdicts come from responses.
PMDA_INDEX = "https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html"
ADCOMM_INDEX = "https://www.fda.gov/advisory-committees/advisory-committee-calendar"
SPONSOR_REGISTERS = {
    "pfizer": "https://www.pfizerclinicaltrials.com/find-a-trial",
    "regeneron": "https://clinicaltrials.regeneron.com/",
    "bayer": "https://clinicaltrials.bayer.com/",
    "glaxosmithkline": "https://www.gsk-studyregister.com/", "gsk": "https://www.gsk-studyregister.com/",
    "novartis": "https://www.novartis.com/clinicaltrials",
    "lilly": "https://trials.lilly.com/", "boehringer ingelheim": "https://www.mystudywindow.com/",
    "novo nordisk": "https://www.novonordisk-trials.com/",
    "amgen": "https://www.amgentrials.com/", "astrazeneca": "https://www.astrazenecaclinicaltrials.com/",
    "sanofi": "https://www.sanofi.com/en/our-science/clinical-trials",
    "hoffmann-la roche": "https://forpatients.roche.com/", "genentech": "https://forpatients.roche.com/",
    "janssen": "https://www.globaltrialfinder.jnj.com/", "merck sharp": "https://www.merckclinicaltrials.com/",
    "merck & co": "https://www.merckclinicaltrials.com/",
    "bristol-myers squibb": "https://www.bmsclinicaltrials.com/",
}


def word_in(term, text):
    return bool(term) and bool(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I))


def names_in(text, ids):
    return [n for n in ids.get("ncts", []) + [ids.get("acronym", "")] if word_in(n, text)]


def fetched(client, source, url, requests):
    memo = getattr(client, "_mandate_responses", None)
    if memo is None:
        memo = client._mandate_responses = {}
    if url in memo:
        cached_body, cached_failure, cached_request = copy.deepcopy(memo[url])
        requests.append(cached_request)
        if cached_failure:
            cached_failure["source"] = source
        return cached_body, cached_failure
    when = utc_now()
    try:
        status, body, when = client.get(url)
        requests.append(dict(url=url, when_utc=when, response_sha256=digest(body), status=status))
        if challenge(body):
            failure = record(source, url, when, "BLOCKED_BOT_CHALLENGE", "Bot/access challenge in HTTP response", body)
            memo[url] = (None, copy.deepcopy(failure), copy.deepcopy(requests[-1]))
            return None, failure
        if status != 200:
            failure = record(source, url, when, "ERROR", f"HTTP {status}; source search not completed", body)
            memo[url] = (None, copy.deepcopy(failure), copy.deepcopy(requests[-1]))
            return None, failure
        memo[url] = (body, None, copy.deepcopy(requests[-1]))
        return body, None
    except (OSError, ValueError) as exc:
        requests.append(dict(url=url, when_utc=when, response_sha256=None, error=f"{type(exc).__name__}: {exc}"))
        failure = record(source, url, when, "BLOCKED_BOT_CHALLENGE" if isinstance(exc, BotBlock) else "ERROR", f"{type(exc).__name__}: {exc}")
        memo[url] = (None, copy.deepcopy(failure), copy.deepcopy(requests[-1]))
        return None, failure


def html_listing(client, source, url, terms, ids):
    from bs4 import BeautifulSoup
    requests = []
    body, failure = fetched(client, source, url, requests)
    if failure:
        failure["requests"] = requests
        failure["query_terms"] = terms
        return failure
    soup = BeautifulSoup(body, "html.parser")
    main = soup.find("main") or soup
    text = main.get_text(" ", strip=True)
    matches = [{"title": a.get_text(" ", strip=True), "url": urljoin(url, a["href"])}
               for a in main.select("a[href]") if any(word_in(t, a.get_text(" ", strip=True)) for t in terms)]
    if matches:
        step, reason = "OPEN_NOT_ASSESSED", "Matching listing entries; trial text/outcome not assessed"
    elif re.search(r"no results|0 results|no matching", text, re.I):
        step, reason = "NOT_FOUND", "Search explicitly reports no matching entries"
    else:
        step, reason = "BLOCKED_JS_ONLY" if soup.find("script") and len(text) < 500 else "ERROR", "No verifiable search results; listing/search completeness not established"
    rec = record(source, url, requests[0]["when_utc"], step,
                 dict(query=terms, matches=matches, reason=reason), body)
    rec["requests"] = requests
    return rec


def pmda_search(client, agents, ids, terms, root=ROOT):
    from bs4 import BeautifulSoup
    from pypdf import PdfReader
    requests, reports, failures = [], [], []
    body, failure = fetched(client, "PMDA", PMDA_INDEX, requests)
    if failure:
        failure["requests"] = requests
        failure["query_terms"] = terms
        return failure
    queue, seen = [(PMDA_INDEX, body)], set()
    licence = None
    initial = BeautifulSoup(body, "html.parser")
    for a in initial.select("a[href]"):
        if a.get_text(" ", strip=True).casefold() == "site policy":
            policy_url = urljoin(PMDA_INDEX, a["href"])
            if urlparse(policy_url).hostname == "www.pmda.go.jp":
                policy, err = fetched(client, "PMDA", policy_url, requests)
                if policy and re.search(r"Public Data License\s*(?:\(Version\s*)?1\.0", BeautifulSoup(policy, "html.parser").get_text(" ", strip=True)):
                    licence = "Public Data License 1.0"
    while queue:
        url, page = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        soup = BeautifulSoup(page, "html.parser")
        if "Public Data License 1.0" in soup.get_text(" ", strip=True):
            licence = "Public Data License 1.0"
        for a in soup.select("a[href]"):
            link = urljoin(url, a["href"])
            if urlparse(link).hostname != "www.pmda.go.jp":
                continue
            context = (a.find_parent("tr") or a).get_text(" ", strip=True)
            if link.lower().endswith(".pdf") and "English" in a.get_text() and any(word_in(t, context) for t in agents):
                if any(r["url"] == link for r in reports):
                    continue
                pdf, err = fetched(client, "PMDA", link, requests)
                if err:
                    failures.append(err)
                    continue
                try:
                    cache = Path(root) / "outputs/k_gap/_reg/pmda"
                    cache.mkdir(parents=True, exist_ok=True)
                    text_path = cache / (digest(pdf) + ".txt")
                    if text_path.exists():
                        text = text_path.read_text(encoding="utf-8")
                    else:
                        text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf)).pages)
                        text_path.write_text(text, encoding="utf-8")
                    if not text.strip():
                        raise ValueError("PDF contains no extractable text")
                    doc_licence = "Public Data License 1.0" if "Public Data License 1.0" in text else licence
                    names = names_in(text, ids)
                    # Fixed rule: target phrase within 2000 characters of an exact trial name.
                    outcome = any(any(word_in(t, text[max(0,m.start()-2000):m.end()+2000]) for t in terms)
                                  for name in names for m in re.finditer(re.escape(name), text, re.I))
                    reports.append(dict(url=link, title=context, response_sha256=digest(pdf), licence=doc_licence,
                                        trial_names=names, target_near_trial=outcome, text_sha256=digest(text.encode())))
                except (ValueError, OSError, RuntimeError) as exc:
                    failures.append(dict(step_reached="ERROR", outcome=f"PDF parse: {type(exc).__name__}: {exc}"))
    named = [r for r in reports if r["trial_names"]]
    if named:
        opened = [r for r in named if r["licence"] == "Public Data License 1.0"]
        step = ("OPEN_OUTCOME_NOT_BINDABLE" if any(r["target_near_trial"] for r in opened)
                else "OPEN_NO_OUTCOME" if opened and terms else "OPEN_NOT_ASSESSED" if opened else "FOUND_NOT_OPEN")
    else:
        step = failures[0]["step_reached"] if failures else "NOT_FOUND"
    rec = record("PMDA", PMDA_INDEX, requests[0]["when_utc"], step,
                 dict(query=agents, reports=reports, failures=failures, licence=licence,
                      rule="Exact NCT/acronym; target phrase within 2000 characters; no effect binding"), body)
    rec["requests"] = requests
    return rec


def ahrq_search(client, terms):
    from scripts.g1_regulatory_source import LITARCH_LIST, LITARCH_BASE
    requests = []
    body, failure = fetched(client, "AHRQ_NIHR_HTA", LITARCH_LIST, requests)
    if failure:
        failure["requests"] = requests
        failure["query_terms"] = terms
        return failure
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig", errors="replace")))
    if not {"Publisher", "Title", "File"}.issubset(reader.fieldnames or []):
        return record("AHRQ_NIHR_HTA", LITARCH_LIST, requests[0]["when_utc"], "ERROR", "Missing litarch CSV columns", body)
    matches = [dict(title=r["Title"], url=urljoin(LITARCH_BASE, r["File"])) for r in reader
               if r["Publisher"] == "Agency for Healthcare Research and Quality (US)" and any(word_in(t, r["Title"]) for t in terms)]
    rec = record("AHRQ_NIHR_HTA", LITARCH_LIST, requests[0]["when_utc"], "OPEN_NOT_ASSESSED" if matches else "NOT_FOUND",
                 dict(provider="AHRQ", query=terms, matches=matches, scope="file list only; packages not fetched"), body)
    rec["requests"] = requests
    return rec


def sponsor_searches(client, ids):
    result = []
    if not ids.get("ncts"):
        ids.setdefault("notes", []).append("sponsor unknown")
        return result
    for nct in ids["ncts"]:
        requests = []
        url = "https://clinicaltrials.gov/api/v2/studies/" + nct
        body, failure = fetched(client, "SPONSOR_REGISTER", url, requests)
        if failure:
            result.append(failure)
            continue
        try:
            protocol = json.loads(body)["protocolSection"]
            if protocol["identificationModule"]["nctId"] != nct:
                raise ValueError("CT.gov NCT mismatch")
            sponsor = protocol["sponsorCollaboratorsModule"]["leadSponsor"]
            name = sponsor["name"]
        except (ValueError, KeyError, TypeError) as exc:
            result.append(record("SPONSOR_REGISTER", url, requests[0]["when_utc"], "ERROR", str(exc), body))
            continue
        ids.setdefault("lead_sponsors", []).append(name)
        if sponsor.get("class") != "INDUSTRY":
            ids.setdefault("notes", []).append(f"{nct}: academic/non-industry lead sponsor {name}; no sponsor register")
            continue
        target = next((u for key, u in SPONSOR_REGISTERS.items() if word_in(key, name)), None)
        if not target:
            result.append(record("SPONSOR_REGISTER", url, requests[0]["when_utc"], "ERROR", f"Own industry sponsor register mapping unavailable: {name}", body))
            continue
        rec = html_listing(client, "SPONSOR_REGISTER", target + ("&" if "?" in target else "?") + urlencode({"query": nct}), [nct], ids)
        rec["requests"] = requests + rec["requests"]
        rec["lead_sponsor"] = name
        result.append(rec)
    return result


def held_searches(trial, ids, slug, root=ROOT):
    from scripts import g1_regulatory_source as reg
    # Metadata-only boundary: no excerpts, readers, spans or text are returned.
    with patch.object(reg, "ROOT", str(root)), patch.object(reg, "SOURCES", str(Path(root)/"registry/regulatory_sources.json")), patch.object(reg, "study_codes", lambda _: {}):
        _, held = reg.regulatory_evidence({**trial, "ncts": ids["ncts"]}, [], slug, ids.get("acronym"))
    results = []
    for agency in ("FDA", "EMA"):
        matches = [{"url": url, "text_sha256": item["record"].get("text_sha256")}
                   for url, item in held.items() if item["record"].get("agency") == agency]
        results.append(record(agency, "registry/regulatory_sources.json", utc_now(), "FOUND_NOT_OPEN" if matches else "NOT_FOUND",
                              dict(scope="held document trial-name metadata only", matches=matches), encoded(matches)))
    return results


def pubmed_verdict(body, pmid, ids):
    root = ET.fromstring(body)
    article = next((a for a in root.findall(".//PubmedArticle") if a.findtext(".//MedlineCitation/PMID") == pmid), None)
    if article is None:
        raise ValueError("Requested PMID absent from PubMed response")
    abstract = " ".join(" ".join(e.itertext()) for e in article.findall(".//AbstractText"))
    title = " ".join(article.find(".//ArticleTitle").itertext()) if article.find(".//ArticleTitle") is not None else ""
    secondary = " ".join(e.text or "" for e in article.findall(".//AccessionNumber"))
    nct_match = any(word_in(n, abstract + " " + secondary) for n in ids.get("ncts", []))
    # Case-sensitive acronym prevents ordinary 'smart'/'hope' words matching trial names.
    acronym = ids.get("acronym", "")
    acronym_match = bool(len(re.sub(r"[^A-Za-z]", "", acronym)) >= 3 and re.search(r"(?<!\w)" + re.escape(acronym) + r"(?!\w)", title + " " + abstract))
    types = [e.text for e in article.findall(".//PublicationType")]
    acronym_match = acronym_match and bool(re.search(r"\btrial\b|randomi[sz]ed", title + " " + abstract, re.I))
    article_text = title + " " + abstract
    if acronym and re.search(re.escape(acronym) + r"(?:-[A-Za-z0-9]+|\s+(?:[IVX]+|[0-9]+)\b)", title):
        acronym_match = False  # a longer trial designation is not the requested acronym
    context = ids.get("topic_terms", [])
    expanded_in_title = bool(acronym and re.search(r"\(" + re.escape(acronym) + r"\)", title))
    if context and abstract and expanded_in_title and not any(word_in(t, article_text) for t in context):
        acronym_match = False
    other_ncts = set(re.findall(r"NCT\d{8}", abstract + " " + secondary))
    if other_ncts and ids.get("ncts") and not nct_match:
        acronym_match = False
    if not nct_match and not acronym_match:
        verdict = "NOT_THE_TRIAL"
    elif ("Randomized Controlled Trial" in types
          and not set(types) & {"Review", "Comment", "Editorial", "Letter", "Published Erratum", "Meta-Analysis", "News"}
          and not re.search(r"secondary analys[ie]s|post[ -]?hoc|pooled analysis|sub[ -]?(?:analysis|study)|exploratory analysis|economic analysis|cost.effectiveness|biomarker study|risk stratification|pre.specified analysis|study protocol|trial protocol|reanalysis", article_text, re.I)
          and not re.search(r"(?:data|findings|analysis) (?:from|of)\b|rationale and design|subgroup|protocol|follow.up|prognostic|predictive|economic|biomarker", title, re.I)
          and (not ids.get("topic_agents") or any(word_in(t, article_text) for t in ids["topic_agents"]))):
        verdict = "PRIMARY_REPORT"
    else:
        verdict = "COMPANION"
    return verdict, dict(nct_match=nct_match, acronym_match=acronym_match, publication_types=types, title=title, rule="exact NCT or contextual acronym; explicit secondary analyses override RCT tags")


def followup_reports(client, targets, root=ROOT):
    from collections import Counter
    counts = Counter()
    all_pmids = sorted({p for t in targets for p in t["outcome"]["new_pmids"]})
    batch_urls = {}
    for start in range(0, len(all_pmids), 50):
        batch = all_pmids[start:start+50]
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urlencode({"db":"pubmed", "id":",".join(batch), "retmode":"xml", "email":EMAIL})
        batch_urls.update({p: url for p in batch})
    for target in targets:
        slug, label = target["slug"], target["label"]
        ids = copy.deepcopy(target["identifiers"])
        definition = json.loads((Path(root)/"topics"/(slug+".json")).read_text(encoding="utf-8"))
        ids["topic_agents"] = topic_agents(definition)
        ids["topic_terms"] = sorted(set(ids["topic_agents"] + definition.get("include", {}).get("population_any", [])))
        accepted, entries = [], []
        for pmid in target["outcome"]["new_pmids"]:
            url = batch_urls[pmid]
            requests = []
            body, failure = fetched(client, "PUBMED_EPMC_PMID", url, requests)
            entry = dict(label=label, pmid=pmid, route="TITLE_SEARCH_FOLLOWUP", requests=requests)
            try:
                if failure:
                    raise ValueError(str(failure["outcome"]))
                verdict, evidence = pubmed_verdict(body, pmid, ids)
                entry.update(verdict=verdict, evidence=evidence)
                counts[verdict] += 1
                if verdict in ("PRIMARY_REPORT", "COMPANION"):
                    accepted.append(pmid)
                    ids.setdefault("provenance", {}).setdefault(pmid, []).append(url + "#" + verdict)
            except (ValueError, ET.ParseError) as exc:
                entry.update(error=str(exc), step_reached=failure["step_reached"] if failure else "ERROR")
                counts["ERROR"] += 1
            entries.append(entry)
        path = Path(root)/"registry/identity_searches"/(slug+".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock(str(path)):
            old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else dict(slug=slug, entries=[])
            for previous in old.setdefault("entries", []):
                replacement = next((e for e in entries if e["label"] == previous.get("label") and e["pmid"] == previous.get("pmid") and previous.get("route") == "TITLE_SEARCH_FOLLOWUP" and e.get("verdict") and e.get("verdict") != previous.get("verdict")), None)
                if replacement:
                    previous["superseded_by_response_sha256"] = replacement["requests"][0]["response_sha256"]
            old["entries"].extend(e for e in entries if e not in old["entries"])
            atomic_json(path, old)
        rejected = {e["pmid"] for e in entries if e.get("verdict") == "NOT_THE_TRIAL"} - set(ids.get("pmids", []))
        log_path = Path(root)/"registry/g1_search_log"/(slug+".json")
        if rejected and log_path.exists():
            with file_lock(str(log_path)):
                previous_log = json.loads(log_path.read_text(encoding="utf-8"))
                previous_trial = previous_log.get("trials", {}).get(label)
                if previous_trial:
                    prior_ids = previous_trial["identifiers"]
                    rejected_dois = {r["outcome"].get("doi") for r in previous_trial["searched"] if isinstance(r.get("outcome"), dict) and r["outcome"].get("id") in rejected} - set(ids.get("dois", []))
                    prior_ids["pmids"] = [p for p in prior_ids.get("pmids", []) if p not in rejected]
                    prior_ids["dois"] = [d for d in prior_ids.get("dois", []) if d not in rejected_dois]
                    for value in rejected | rejected_dois:
                        prior_ids.get("provenance", {}).pop(value, None)
                    note = "TITLE_SEARCH_FOLLOWUP corrected acronym collisions; superseded search history retained"
                    if note not in prior_ids.setdefault("notes", []):
                        prior_ids["notes"].append(note)
                    atomic_json(log_path, previous_log)
        ids["pmids"] = sorted(set(ids.get("pmids", []) + accepted))
        searched = []
        for pmid in accepted:
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode({"query":f"EXT_ID:{pmid} SRC:MED", "resultType":"core", "format":"json"})
            rec, _ = search(client, "PUBMED_EPMC_PMID", url, identifiers={"pmid":pmid})
            searched.append(rec)
            doi = rec["outcome"].get("doi") if isinstance(rec["outcome"], dict) else None
            if valid_doi(doi):
                ids["dois"] = sorted(set(ids.get("dois", []) + [doi]))
                ids.setdefault("provenance", {}).setdefault(doi, []).append(url+"#doi")
                searched.append(search(client,"UNPAYWALL_DOI","https://api.unpaywall.org/v2/"+quote(doi,safe="")+"?"+urlencode({"email":EMAIL}))[0])
        merge_write(Path(root)/"registry/g1_search_log"/(slug+".json"), dict(slug=slug, written_utc=utc_now(), trials={label:dict(identifiers=ids,searched=searched,secondary_value_available=False)}))
        print(f"FOLLOWUP {slug} | {label} | {dict(counts)}", flush=True)
    print("FOLLOWUP VERDICTS " + json.dumps(dict(counts), sort_keys=True), flush=True)
    return counts


def run(slugs=None, offline=False, root=ROOT, followup=None):
    repo = Committed(root)
    snapshot_paths = [p for p in repo.paths if p.endswith((".json", ".jsonl")) and not Path(p).name.startswith("_") and
                      p.startswith(("outputs/k_gap/registry_fill/", "outputs/k_gap/g1/", "topics/", "registry/g1_acquired_regulator/"))]
    repo.prime(snapshot_paths + ["outputs/k_gap/regulatory_probe.json", "outputs/k_gap/_reg/hc_listing.json"])
    print(f"HEAD snapshot loaded: {len(snapshot_paths)} files", flush=True)
    fill = "outputs/k_gap/registry_fill/"
    identification = source_rows(repo, fill + "IDENTIFICATION*.json")
    funnels = source_rows(repo, fill + "*.funnel.json")
    census = source_rows(repo, fill + "PHASE3_OPEN_CENSUS*.json")
    for path in repo.matching(fill + "phase3*/*.json"):
        if Path(path).name.startswith("_"):
            continue  # model call metadata is not a trial census
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
    if client and followup:
        followup_reports(client, json.loads(Path(followup).read_text(encoding="utf-8"))["new_report_found"], root)
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
            print(f"SEARCH {slug} | {label}", flush=True)
            searched = []
            existing_path = Path(root)/"registry/g1_search_log"/(slug+".json")
            if existing_path.exists():
                prior = json.loads(existing_path.read_text(encoding="utf-8")).get("trials", {}).get(label, {}).get("identifiers", {})
                ids["approved_drug"] = bool(ids["approved_drug"] or prior.get("approved_drug"))
                for key in ("pmids", "dois", "ncts", "eudract"):
                    ids[key] = sorted(set(ids[key] + prior.get(key, [])))
            if client:
                searched.extend(live_searches(client, ids, local_census))
            for row in summaries:
                if row.get("label") == label:
                    rec = holding_record(row, holding_path, holding_time)
                    if rec:
                        searched.append(rec)
            if client:
                missing = {a for a in ("FDA", "EMA") if not any(r.get("label") == label and str(r.get("phase", "")).split(":")[-1] == a for r in summaries)}
                if missing:
                    searched.extend(r for r in held_searches(trial, ids, slug, root) if r["source"] in missing)
            if ids["approved_drug"]:
                if client:
                    definition = repo.read(f"topics/{slug}.json", {})
                    condition = definition.get("registry_first", {}).get("cond") or definition.get("ctgov", {}).get("cond") or ""
                    terms = [condition] if isinstance(condition, str) and condition else []
                    searched.append(pmda_search(client, agents, ids, definition.get("primary_outcome", {}).get("keywords", []), root))
                    for agent in agents:
                        searched.append(html_listing(client, "TGA_AUSPAR", "https://www.tga.gov.au/resources/auspar", [agent], ids))
                        searched.append(html_listing(client, "FDA_ADCOMM", ADCOMM_INDEX, [agent], ids))
                        searched.append(html_listing(client, "AHRQ_NIHR_HTA", "https://www.journalslibrary.nihr.ac.uk/search/?"+urlencode({"q":agent}), [agent], ids))
                    searched.append(ahrq_search(client, agents + terms))
                    searched.extend(sponsor_searches(client, ids))
                searched.append(record("EMA_CLINICAL_DATA", "https://clinicaldata.ema.europa.eu/", PROBE_DATE,
                                       "BLOCKED_ACCOUNT", "Public clinical data portal requires account; no login attempted"))
                for source_slug, row in discovery:
                    if source_slug == slug and row.get("label") == label:
                        rec = discovery_record(row)
                        if rec and rec["source"] != "SPONSOR_REGISTER":
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
    parser.add_argument("--followup", type=Path, help="reading_targets.json")
    args = parser.parse_args(argv)
    if args.slugs and any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s) for s in args.slugs):
        parser.error("Invalid slug")
    run(args.slugs, args.offline, followup=args.followup)


if __name__ == "__main__":
    main()
