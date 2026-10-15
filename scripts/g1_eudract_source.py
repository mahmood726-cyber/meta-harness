"""EU CTR results discovery and conservative, deterministic candidate extraction.

Static: URL templates, licence, label vocabulary, 30-day TTL and request pause.
Dynamic: identifiers, endpoints and all values come only from source responses.
No population/timeframe binding or effect inversion is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

from bs4 import BeautifulSoup
from harness.lexicon import fold
from g1_regulatory_source import EMA_ACK, USER_AGENT, file_lock

BASE = "https://www.clinicaltrialsregister.eu"
CACHE_DIR = ROOT / "outputs" / "k_gap" / "_reg" / "eudract"
LICENCE = "EMA_REUSE_WITH_ACKNOWLEDGEMENT"
NUMBER = re.compile(r"(?<!\d)\d{4}-\d{6}-\d{2}(?!\d)")
TTL = 30 * 86400
PAUSE = 0.3
_HTTP_LOCK = threading.Lock()


def _fetch(url):
    # harness.http has a module-global UA, not a per-request header option.
    # Use the same stdlib transport without mutating another source's global UA.
    with _HTTP_LOCK:
        try:
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=30) as response:
                return response.read()
        finally:
            time.sleep(PAUSE)


def _text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def eudract_numbers(ncts, labels):
    """Sorted [{eudract_no, provenance: [{nct, url, field}]}].

    Labels are caller context only, never evidence for an identifier. Errors
    propagate rather than silently reporting that a trial has no EU identifier.
    """
    found = {}
    for nct in sorted(set(ncts)):
        if not re.fullmatch(r"NCT\d{8}", nct):
            raise ValueError(f"Invalid NCT identifier: {nct}")
        url = "https://clinicaltrials.gov/api/v2/studies/" + nct
        record = json.loads(_fetch(url))
        identification = record["protocolSection"]["identificationModule"]
        if identification.get("nctId") != nct:
            raise ValueError("CT.gov response identifier mismatch")
        sources = []
        for item in identification.get("secondaryIdInfos", []):
            sources.extend((no, url, "secondaryIdInfos.id") for no in NUMBER.findall(item.get("id", "")))
        search_url = BASE + "/ctr-search/search?query=" + quote(nct)
        soup = BeautifulSoup(_fetch(search_url), "html.parser")
        # Restrict to trial-result links, never dates/IDs in unrelated page prose.
        for link in soup.select('a[href]'):
            match = re.search(r"/ctr-search/trial/(\d{4}-\d{6}-\d{2})(?:/|$)", link["href"])
            if match and urlparse(urljoin(BASE, link["href"])).netloc == urlparse(BASE).netloc:
                sources.append((match[1], search_url, "search_result.trial_link"))
        for no, source_url, field in sources:
            provenance = {"nct": nct, "url": source_url, "field": field}
            records = found.setdefault(no, [])
            if provenance not in records:
                records.append(provenance)
    return [{"eudract_no": no, "provenance": found[no]} for no in sorted(found)]


def _rows(soup):
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"], recursive=False)
        if len(cells) >= 2 and not any(c.find("table") for c in cells):
            yield [_text(c) for c in cells]


def _endpoint_rows(soup):
    """Scope rows to the tables actually containing endpoint title fields."""
    seen = set()
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"], recursive=False)
        if len(cells) < 2 or _text(cells[0]).casefold() != "end point title":
            continue
        table = row.find_parent("table")
        if table is not None and id(table) not in seen:
            seen.add(id(table))
            yield from _rows(table)


def _parse(body, url):
    soup = BeautifulSoup(body, "html.parser")
    endpoints, ep, analysis = [], None, None
    headers, unit, measure, dispersion = [], "", "", ""
    fields = {"end point description": "description", "end point type": "type",
              "end point timeframe": "timeframe"}
    analysis_fields = {"statistical analysis description": "description", "method": "method",
                       "parameter type": "parameter", "point estimate": "point_estimate",
                       "parameter value": "point_estimate", "comparison groups": "comparison_groups",
                       "level": "ci_level", "sides": "sides", "lower limit": "lower",
                       "upper limit": "upper"}
    for row in _endpoint_rows(soup):
        label, values = row[0], row[1:]
        key = label.casefold().strip()
        if key == "end point title":
            ep = {"title": values[0], "description": "", "type": "", "timeframe": "",
                  "reporting_groups": [], "statistics": [], "analyses": []}
            endpoints.append(ep)
            analysis, headers, unit, measure, dispersion = None, [], "", "", ""
        elif ep is None:
            continue
        elif key in fields:
            ep[fields[key]] = values[0]
        elif key in ("statistical analysis title", "statistical analysis"):
            analysis = {"title": values[0]}
            ep["analyses"].append(analysis)
        elif analysis is not None:
            if key in analysis_fields:
                analysis[analysis_fields[key]] = values[0]
        elif key == "end point values":
            headers = values
            if len(set(headers)) != len(headers) or not all(headers):
                raise ValueError("Missing or duplicate endpoint group names")
            ep["reporting_groups"].extend({"title": h, "subjects_analysed": ""} for h in headers)
        elif key == "number of subjects analysed":
            if not headers or len(values) != len(headers):
                raise ValueError("Subject counts lack matching group headers")
            for group, value in zip(ep["reporting_groups"][-len(headers):], values):
                group["subjects_analysed"] = value
        elif key.startswith("units:"):
            unit = label.split(":", 1)[1].strip()
        elif key in ("unit", "units"):
            unit = values[0]
        elif key == "measure type":
            measure = values[0]
        elif key in ("dispersion", "dispersion type"):
            dispersion = values[0]
        elif headers and any(values):
            if len(values) != len(headers):
                raise ValueError("Statistic values lack matching group headers")
            # EU CTR prints e.g. 'mean (standard deviation)' as a row label.
            match = re.fullmatch(r"(.*?)\s*\((.*?)\)", label)
            ep["statistics"].append({"label": label, "measure_type": measure or (match[1].strip() if match else label),
                                     "unit": unit, "dispersion": dispersion or (match[2] if match else ""),
                                     "values": dict(zip(headers, values))})
    attachments = sorted({urljoin(BASE, a["href"]) for a in soup.select("a[href]")
                          if urlparse(urljoin(BASE, a["href"])).netloc == urlparse(BASE).netloc
                          and urlparse(urljoin(BASE, a["href"])).path.startswith(
                              "/ctr-search/rest/download/result/attachment/")})
    if not endpoints and not attachments:
        if re.search(r"results? (?:for this trial )?(?:are |is )?not (?:yet )?available|no results (?:are )?(?:yet )?available", _text(soup), re.I):
            return {"state": "NO_RESULTS"}
        raise ValueError("Unrecognised EU CTR results page")
    return {"state": "RESULTS", "url": url, "endpoints": endpoints, "attachments": attachments,
            "html_sha256": hashlib.sha256(body).hexdigest(), "agency": "EMA", "licence": LICENCE,
            "acknowledgement": EMA_ACK}


def eudract_results(eudract_no):
    """Fetch/cache raw HTML atomically; failed refreshes never use stale evidence."""
    if not NUMBER.fullmatch(eudract_no):
        raise ValueError("Invalid EudraCT number")
    url = BASE + "/ctr-search/trial/" + eudract_no + "/results"
    path = Path(CACHE_DIR) / (eudract_no + ".html")
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(str(path)):
        if path.exists() and 0 <= time.time() - path.stat().st_mtime < TTL:
            return _parse(path.read_bytes(), url)
        body = _fetch(url)
        result = _parse(body, url)
        # Same atomic replace pattern as regulatory_source._dump, preserving raw bytes.
        tmp = path.with_suffix(f".html.{os.getpid()}.tmp")
        try:
            tmp.write_bytes(body)
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)
        return result


def _matches(text, terms):
    return any(fold(t) and fold(t) in fold(text) for t in terms if t)


def _integer(value):
    return int(value) if re.fullmatch(r"\d+", value) else None


def _effect(analysis):
    if not re.fullmatch(r"95(?:\.0+)?\s*%?", analysis.get("ci_level", "")):
        return False
    if fold(analysis.get("sides", "")) not in ("2-sided", "two-sided", "2 sided", "two sided"):
        return False
    if not re.fullmatch(r"(?:hazard|odds|risk) ratio(?: \((?:HR|OR|RR)\))?", analysis.get("parameter", ""), re.I):
        return False
    values = [analysis.get(k, "") for k in ("lower", "point_estimate", "upper")]
    if not all(re.fullmatch(r"\d+(?:\.\d+)?", v) for v in values):
        return False
    lo, point, hi = map(float, values)
    return 0 < lo <= point <= hi and lo < hi


def eudract_typed(endpoints, outcome_terms, interv_terms, comp_terms, estimand):
    """Return all endpoint candidates; never bind, derive counts or invert effects.

    Estimand is retained as caller context. Divergences are observable text,
    not an assertion that a candidate matches the requested estimand.
    """
    candidates, refused = [], []
    for ep in endpoints:
        if not _matches(ep["title"] + " " + ep["description"], outcome_terms):
            continue
        arms = {}
        for group in ep["reporting_groups"]:
            intervention = _matches(group["title"], interv_terms)
            comparator = _matches(group["title"], comp_terms)
            role = "experimental" if intervention else "control"
            if intervention == comparator or role in arms:
                arms = {}
                break
            arms[role] = dict(group)
        if set(arms) != {"experimental", "control"}:
            refused.append({"title": ep["title"], "reason": "AMBIGUOUS_GROUP_MAPPING"})
            continue
        counts = []
        for stat in ep["statistics"]:
            if re.search(r"mean|median|percent|proportion|rate", fold(stat["measure_type"])):
                continue
            if fold(stat["unit"]) not in ("subjects", "participants", "patients", "number of subjects",
                                         "number of participants", "number of patients"):
                continue
            values = {}
            for role, arm in arms.items():
                value = _integer(stat["values"].get(arm["title"], ""))
                n = _integer(arm["subjects_analysed"])
                if value is None or n is None or not 0 <= value <= n:
                    break
                values[role] = {"count": value, "subjects_analysed": n}
            if len(values) == 2:
                counts.append({"label": stat["label"], "arms": values})
        population_text = " ".join([ep["description"], *(a.get("description", "") for a in ep["analyses"])])
        populations = sorted(set(re.findall(r"full analysis set|per[ -]protocol|modified(?: intention[ -]to[ -]treat)?|intention[ -]to[ -]treat",
                                            population_text, re.I)))
        effects = []
        for analysis in ep["analyses"]:
            comparison = re.split(r"\s+(?:v|vs|versus)\.?\s+", analysis.get("comparison_groups", ""), flags=re.I)
            names = {fold(arm["title"]): role for role, arm in arms.items()}
            if _effect(analysis) and len(comparison) == 2 and {fold(c) for c in comparison} == set(names):
                effects.append(dict(analysis, comparison_order=[names[fold(c)] for c in comparison]))
        candidates.append({"title": ep["title"], "arms": arms, "statistics": ep["statistics"], "counts": counts,
                           "effects": effects, "estimand": estimand,
                           "divergences": {"timeframe": ep["timeframe"], "analysis_population": populations,
                                           "measure_type": [s["measure_type"] for s in ep["statistics"]]}})
    return {"decision": "AMBIGUOUS" if len(candidates) > 1 else "CANDIDATE" if candidates else "REFUSED" if refused else "NO_MATCH",
            "candidates": candidates, "refused": refused}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["probe"])
    parser.add_argument("ncts", nargs="+")
    args = parser.parse_args(argv)
    for nct in args.ncts:
        numbers = eudract_numbers([nct], [])
        results = []
        for record in numbers:
            result = eudract_results(record["eudract_no"])
            results.append({"eudract_no": record["eudract_no"], "state": result["state"],
                            "endpoint_titles": [ep["title"] for ep in result.get("endpoints", [])]})
        print(json.dumps({"nct": nct, "numbers": numbers, "results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
