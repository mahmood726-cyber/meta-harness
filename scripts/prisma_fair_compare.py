"""FAIR PRISMA comparison against comparator OA full text.

This script fixes the abstract/full-page confound in the older comparator pass:
OURS is scored from the rendered review HTML, while the published comparator is
scored only after fetching its OA full text body where obtainable.

Outputs:
  - cache/<slug>/comparator_fulltext.txt
  - docs/prisma_fair.json
  - VERIFY-prisma-fair.md
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"
OUT_JSON = ROOT / "docs" / "prisma_fair.json"
OUT_MD = ROOT / "VERIFY-prisma-fair.md"

NCBI_EMAIL = "mahmood726@gmail.com"
NCBI_TOOL = "meta-harness-prisma-fair"
UNPAYWALL_EMAIL = "mahmood726@gmail.com"
UA = f"{NCBI_TOOL}/1.0 (mailto:{NCBI_EMAIL})"
MIN_FULLTEXT_BYTES = 1000

ITEMS = [
    "7 search strategy",
    "7 verbatim re-runnable",
    "8 dual independent screening",
    "16a flow diagram",
    "16b exclusions-with-reasons",
    "24 registration/PROSPERO",
]


def rx(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.I | re.S)


def rx_cs(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.S)


OURS_PATTERNS = {
    "7 search strategy": [
        rx(r"Full search strategy.{0,120}present"),
        rx(r"Search tab.{0,120}(PubMed|ClinicalTrials\.gov|queries)"),
        rx(r"PubMed.{0,250}ClinicalTrials\.gov"),
    ],
    "7 verbatim re-runnable": [
        rx(r"verbatim.{0,80}re-runnable"),
        rx(r"exact PubMed and ClinicalTrials\.gov queries are printed verbatim"),
        rx(r"\bAND\b.{0,120}\bOR\b"),
    ],
    "8 dual independent screening": [
        rx(r"Dual independent screening"),
        rx(r"Two independently-implemented rule screeners"),
        rx(r"Selection process.{0,220}(screeners|disagreement)"),
    ],
    "16a flow diagram": [
        rx(r"Study selection flow"),
        rx(r"PRISMA flow"),
        rx(r"identified.{0,120}screened.{0,120}excluded"),
    ],
    "16b exclusions-with-reasons": [
        rx(r"Exclusions with reasons"),
        rx(r"Every excluded record.{0,160}(reason|verbatim span)"),
        rx(r"excluded record's rule id, reason and verbatim span"),
    ],
    "24 registration/PROSPERO": [
        rx(r"Registration \(protocol commit SHA\)"),
        rx(r"registered at commit SHA"),
        rx(r"protocol commit SHA"),
    ],
}

COMPARATOR_PATTERNS = {
    "7 search strategy": [
        rx(
            r"(search strategy|search terms|electronic databases|databases were searched|"
            r"searched (MEDLINE|PubMed|Embase|Cochrane|CENTRAL|Web of Science|Scopus|ClinicalTrials))"
        ),
        rx(
            r"(MEDLINE|PubMed|Embase|Cochrane|CENTRAL|Web of Science|Scopus|ClinicalTrials\.gov)"
            r".{0,180}(searched|search strategy|search terms)"
        ),
    ],
    "7 verbatim re-runnable": [
        rx(r"\[(tiab|mesh|mh|tw|title/abstract)\]"),
        rx_cs(r"\b(MeSH|MESH|Emtree|tiab|TIAB|tw|TW|exp)\b.{0,180}\b(AND|OR|NOT)\b"),
        rx_cs(r"\b#\d+\b.{0,160}\b(AND|OR|NOT)\b"),
        rx_cs(r"\(.{0,120}\bAND\b.{0,160}\bOR\b.{0,120}\)"),
    ],
    "8 dual independent screening": [
        rx(r"two (reviewers|authors|investigators|researchers).{0,90}independent"),
        rx(r"independent(ly)?.{0,80}(screen|select|assess|review|extract)"),
        rx(r"disagreement.{0,100}(third|consensus|discussion)"),
        rx(r"\bkappa\b"),
    ],
    "16a flow diagram": [
        rx(r"PRISMA.{0,80}(flow|diagram)"),
        rx(r"flow diagram"),
        rx(r"records?.{0,60}identified.{0,120}records?.{0,60}screened"),
        rx(r"studies.{0,60}included.{0,100}(meta-analysis|analysis)"),
    ],
    "16b exclusions-with-reasons": [
        rx(r"reasons? for exclusion"),
        rx(r"(full[- ]text articles?|studies|records).{0,120}excluded.{0,120}reasons?"),
        rx(r"excluded.{0,120}(because|did not meet|irrelevant|not eligible)"),
    ],
    "24 registration/PROSPERO": [
        rx(r"PROSPERO"),
        rx(r"CRD420\d+"),
        rx(r"registration number"),
        rx(r"(protocol|review).{0,100}(registered|registration)"),
        rx(r"(registered|registration).{0,100}(protocol|INPLASY|OSF|Open Science Framework)"),
    ],
}


@dataclass
class FetchResult:
    source: str
    text: str
    note: str = ""

    @property
    def byte_len(self) -> int:
        return len(self.text.encode("utf-8"))


def get_bytes(url: str, params: dict[str, str] | None = None, tries: int = 3, timeout: int = 45) -> bytes:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": UA,
                    "Accept": "text/html,application/xml,application/json,application/pdf,*/*",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as handle:
                return handle.read()
        except Exception as exc:  # noqa: BLE001 - bounded retry, then raise
            last = exc
            time.sleep(0.5 * (2**attempt))
    raise RuntimeError(f"GET failed after {tries} tries: {url}; {last}")


def get_json(url: str, params: dict[str, str] | None = None) -> dict:
    return json.loads(get_bytes(url, params).decode("utf-8", "replace"))


def get_text(url: str, params: dict[str, str] | None = None) -> str:
    return get_bytes(url, params).decode("utf-8", "replace")


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def xml_body_to_text(xml_text: str) -> str:
    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError:
        return ""
    parts: list[str] = []
    for elem in root.iter():
        if local_name(elem.tag) == "body":
            parts.append(" ".join(elem.itertext()))
    return normalize_ws(" ".join(parts))


def html_to_text(markup: str) -> str:
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(markup, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        main = soup.find("article") or soup.find("main") or soup.body or soup
        return normalize_ws(main.get_text(" "))
    except Exception:  # noqa: BLE001 - fallback parser for lean environments
        text = re.sub(r"(?is)<(script|style|noscript|svg).*?</\1>", " ", markup)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        return normalize_ws(text)


def pdf_to_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(BytesIO(data))
        return normalize_ws(" ".join(page.extract_text() or "" for page in reader.pages))
    except Exception:
        return ""


def normalize_pmcid(value: str | None) -> str | None:
    if not value:
        return None
    value = str(value).strip()
    if re.fullmatch(r"\d+", value):
        return f"PMC{value}"
    m = re.search(r"PMC(\d+)", value, re.I)
    return f"PMC{m.group(1)}" if m else None


def numeric_pmcid(pmcid: str) -> str:
    return re.sub(r"^PMC", "", pmcid, flags=re.I)


def elink_pmcid(pmid: str) -> str | None:
    data = get_json(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi",
        {
            "dbfrom": "pubmed",
            "db": "pmc",
            "id": pmid,
            "retmode": "json",
            "tool": NCBI_TOOL,
            "email": NCBI_EMAIL,
        },
    )
    time.sleep(0.34)
    candidates: list[tuple[int, str]] = []
    for linkset in data.get("linksets", []):
        for db in linkset.get("linksetdbs", []):
            if db.get("dbto") != "pmc" or db.get("linkname") != "pubmed_pmc":
                continue
            for link in db.get("links", []):
                pmcid = normalize_pmcid(str(link))
                if pmcid:
                    candidates.append((0, pmcid))
    if not candidates:
        return None
    return sorted(candidates)[0][1]


def ncbi_pmc_fulltext(pmcid: str) -> str:
    xml_text = get_text(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        {
            "db": "pmc",
            "id": numeric_pmcid(pmcid),
            "rettype": "xml",
            "retmode": "xml",
            "tool": NCBI_TOOL,
            "email": NCBI_EMAIL,
        },
    )
    time.sleep(0.34)
    return xml_body_to_text(xml_text)


def europe_pmcid_for_pmid(pmid: str) -> str | None:
    data = get_json(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        {"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core"},
    )
    time.sleep(0.2)
    records = data.get("resultList", {}).get("result") or []
    if not records:
        return None
    return normalize_pmcid(records[0].get("pmcid"))


def europe_pmc_fulltext(pmcid: str) -> str:
    xml_text = get_text(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML")
    time.sleep(0.2)
    return xml_body_to_text(xml_text)


def unpaywall_locations(doi: str) -> Iterable[tuple[str, str]]:
    encoded = urllib.parse.quote(doi, safe="")
    data = get_json(f"https://api.unpaywall.org/v2/{encoded}", {"email": UNPAYWALL_EMAIL})
    seen: set[str] = set()
    locations = []
    best = data.get("best_oa_location")
    if best:
        locations.append(best)
    locations.extend(data.get("oa_locations") or [])
    for loc in locations:
        for key, kind in [("url_for_pdf", "PDF"), ("url", "HTML"), ("url_for_landing_page", "HTML")]:
            url = loc.get(key)
            if not url or url in seen:
                continue
            seen.add(url)
            yield kind, url


def unpaywall_fulltext(doi: str) -> FetchResult | None:
    try:
        locations = list(unpaywall_locations(doi))
    except Exception as exc:  # noqa: BLE001
        return FetchResult("NONE", "", f"Unpaywall metadata failed: {exc}")
    last_note = ""
    for kind, url in locations:
        try:
            data = get_bytes(url, tries=2, timeout=60)
            if kind == "PDF" or url.lower().split("?", 1)[0].endswith(".pdf") or data[:4] == b"%PDF":
                text = pdf_to_text(data)
                kind = "PDF"
            else:
                text = html_to_text(data.decode("utf-8", "replace"))
                kind = "HTML"
            if len(text.encode("utf-8")) >= MIN_FULLTEXT_BYTES:
                return FetchResult(f"Unpaywall {kind}: {url}", text)
            last_note = f"{kind} text too short from {url}"
        except Exception as exc:  # noqa: BLE001
            last_note = f"{kind} fetch failed from {url}: {exc}"
    return FetchResult("NONE", "", last_note or "Unpaywall had no usable OA location")


def fetch_comparator_fulltext(pmid: str, doi: str | None) -> FetchResult:
    notes: list[str] = []
    pmcid: str | None = None
    try:
        pmcid = elink_pmcid(pmid)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"NCBI elink failed: {exc}")

    if pmcid:
        try:
            text = ncbi_pmc_fulltext(pmcid)
            if len(text.encode("utf-8")) >= MIN_FULLTEXT_BYTES:
                return FetchResult(f"NCBI PMC efetch XML body: {pmcid}", text)
            notes.append(f"NCBI PMC body missing/short: {pmcid}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"NCBI PMC efetch failed for {pmcid}: {exc}")
        try:
            text = europe_pmc_fulltext(pmcid)
            if len(text.encode("utf-8")) >= MIN_FULLTEXT_BYTES:
                return FetchResult(f"Europe PMC fullTextXML: {pmcid}", text)
            notes.append(f"Europe PMC fullTextXML missing/short: {pmcid}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"Europe PMC fullTextXML failed for {pmcid}: {exc}")

    try:
        epmc_pmcid = europe_pmcid_for_pmid(pmid)
    except Exception as exc:  # noqa: BLE001
        epmc_pmcid = None
        notes.append(f"Europe PMC PMID lookup failed: {exc}")
    if epmc_pmcid and epmc_pmcid != pmcid:
        try:
            text = europe_pmc_fulltext(epmc_pmcid)
            if len(text.encode("utf-8")) >= MIN_FULLTEXT_BYTES:
                return FetchResult(f"Europe PMC fullTextXML: {epmc_pmcid}", text)
            notes.append(f"Europe PMC fullTextXML missing/short: {epmc_pmcid}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"Europe PMC fullTextXML failed for {epmc_pmcid}: {exc}")

    if doi:
        upw = unpaywall_fulltext(doi)
        if upw and upw.source != "NONE":
            return upw
        if upw and upw.note:
            notes.append(upw.note)

    return FetchResult("NONE", "", "; ".join(notes))


def quote_from_match(text: str, match: re.Match[str], max_words: int = 18) -> str:
    start, end = match.span()
    quote_start = start
    quote_end = min(len(text), end + 220)
    snippet = normalize_ws(text[quote_start:quote_end])
    words = snippet.split()
    if len(words) > max_words:
        snippet = " ".join(words[:max_words])
    return snippet


def score_item(text: str, patterns: list[re.Pattern[str]]) -> tuple[bool, str]:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return True, quote_from_match(text, match)
    return False, ""


def score_text(text: str, patterns_by_item: dict[str, list[re.Pattern[str]]]) -> dict[str, dict[str, object]]:
    return {
        item: {"present": present, "quote": quote}
        for item in ITEMS
        for present, quote in [score_item(text, patterns_by_item[item])]
    }


def read_review(slug: str) -> dict:
    with (REVIEWS / slug / "review.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def discover_slugs() -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files", "docs/reviews/*/review.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        slugs = [Path(line.strip()).parent.name for line in proc.stdout.splitlines() if line.strip()]
        if slugs:
            return sorted(slugs)
    except Exception:
        pass
    return sorted(path.name for path in REVIEWS.iterdir() if (path / "review.json").exists())


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def md_bool(value: object) -> str:
    if value is True:
        return "Y"
    if value is False:
        return "N"
    return "NA"


def make_markdown(results: dict[str, dict]) -> str:
    included = [slug for slug, row in results.items() if row["comparator_fulltext_source"] != "NONE"]
    excluded = [slug for slug, row in results.items() if row["comparator_fulltext_source"] == "NONE"]
    ours_win = 0
    comp_win = 0
    comparator_present = 0
    possible = len(included) * len(ITEMS)
    for slug in included:
        row = results[slug]
        for item in ITEMS:
            ours = bool(row["ours"][item])
            comp = bool(row["comparator"][item]["present"])
            comparator_present += int(comp)
            ours_win += int(ours and not comp)
            comp_win += int(comp and not ours)

    lines = [
        "# FAIR PRISMA Comparator Comparison",
        "",
        "Comparator scoring uses OA full text body where obtainable, not PubMed abstracts. "
        "Topics with no obtainable comparator full text are excluded from the fair item counts.",
        "",
        f"- Topics built: {len(results)}",
        f"- Comparator full text obtained: {len(included)}",
        f"- Comparator full text unobtainable/excluded: {len(excluded)}",
        f"- Countable topic-item cells: {possible}",
        f"- Comparator-present cells: {comparator_present}",
        f"- OURS present / comparator absent: {ours_win}",
        f"- Comparator present / OURS absent: {comp_win}",
        "",
        "## Per-topic Summary",
        "",
        "| slug | source | bytes | ours n/6 | comparator n/6 | ours-only | comparator-only |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for slug, row in results.items():
        ours_n = sum(1 for item in ITEMS if row["ours"][item])
        if row["comparator_fulltext_source"] == "NONE":
            comp_n = "excluded"
            topic_ours_win = "excluded"
            topic_comp_win = "excluded"
        else:
            comp_n_int = sum(1 for item in ITEMS if row["comparator"][item]["present"])
            topic_ours_win = str(
                sum(1 for item in ITEMS if row["ours"][item] and not row["comparator"][item]["present"])
            )
            topic_comp_win = str(
                sum(1 for item in ITEMS if row["comparator"][item]["present"] and not row["ours"][item])
            )
            comp_n = str(comp_n_int)
        source = row["comparator_fulltext_source"].replace("|", "\\|")
        lines.append(
            f"| `{slug}` | {source} | {row['comparator_fulltext_len']} | "
            f"{ours_n} | {comp_n} | {topic_ours_win} | {topic_comp_win} |"
        )

    if excluded:
        lines.extend(["", "## Excluded From Fair Count", ""])
        for slug in excluded:
            note = results[slug].get("fetch_note") or "no OA full text body obtainable"
            lines.append(f"- `{slug}`: {note}")

    lines.extend(["", "## Item Detail", ""])
    for slug, row in results.items():
        lines.extend([f"### {slug}", ""])
        lines.append("| item | ours | ours quote | comparator | comparator quote |")
        lines.append("|---|---:|---|---:|---|")
        for item in ITEMS:
            ours_quote = (row.get("ours_quotes") or {}).get(item, "")
            comp_entry = row["comparator"][item]
            comp_present = comp_entry["present"]
            comp_quote = comp_entry.get("quote", "")
            lines.append(
                f"| {item} | {md_bool(row['ours'][item])} | {escape_md(ours_quote)} | "
                f"{md_bool(comp_present)} | {escape_md(comp_quote)} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def fair_totals(results: dict[str, dict]) -> tuple[list[str], int, int]:
    included = [slug for slug, row in results.items() if row["comparator_fulltext_source"] != "NONE"]
    ours_win = sum(
        1
        for slug in included
        for item in ITEMS
        if results[slug]["ours"][item] and not results[slug]["comparator"][item]["present"]
    )
    comp_win = sum(
        1
        for slug in included
        for item in ITEMS
        if results[slug]["comparator"][item]["present"] and not results[slug]["ours"][item]
    )
    return included, ours_win, comp_win


def refresh_from_cache() -> int:
    with OUT_JSON.open(encoding="utf-8") as handle:
        results = json.load(handle)
    for slug, row in results.items():
        html_text = html_to_text((REVIEWS / slug / "index.html").read_text(encoding="utf-8"))
        ours_scored = score_text(html_text, OURS_PATTERNS)
        row["ours"] = {item: bool(ours_scored[item]["present"]) for item in ITEMS}
        row["ours_quotes"] = {
            item: str(ours_scored[item]["quote"]) for item in ITEMS if ours_scored[item]["present"]
        }
        cache_path = ROOT / row["comparator_fulltext_path"]
        if row["comparator_fulltext_source"] == "NONE":
            row["comparator"] = {item: {"present": None, "quote": ""} for item in ITEMS}
        else:
            row["comparator"] = score_text(cache_path.read_text(encoding="utf-8"), COMPARATOR_PATTERNS)
    with OUT_JSON.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(results, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    write_text(OUT_MD, make_markdown(results))
    included, ours_win, comp_win = fair_totals(results)
    print(f"Refreshed from cache for {len(results)} topics ({len(included)} included in fair count).")
    print(f"FAIR totals: ours-present/comparator-absent={ours_win}; comparator-present/ours-absent={comp_win}")
    return 0


def escape_md(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ")


def main(argv: list[str]) -> int:
    if "--refresh-from-cache" in argv:
        return refresh_from_cache()
    slugs = argv or discover_slugs()
    results: dict[str, dict] = {}

    for slug in slugs:
        review = read_review(slug)
        comparator = review.get("comparator") or {}
        pmid = str(comparator.get("pmid") or "").strip()
        doi = str(comparator.get("doi") or "").strip() or None
        html_text = html_to_text((REVIEWS / slug / "index.html").read_text(encoding="utf-8"))
        ours_scored = score_text(html_text, OURS_PATTERNS)
        ours = {item: bool(ours_scored[item]["present"]) for item in ITEMS}
        ours_quotes = {item: str(ours_scored[item]["quote"]) for item in ITEMS if ours_scored[item]["present"]}

        print(f"[{slug}] fetching comparator PMID {pmid}", flush=True)
        if pmid:
            fetched = fetch_comparator_fulltext(pmid, doi)
        else:
            fetched = FetchResult("NONE", "", "review.json comparator.pmid missing")

        cache_path = ROOT / "cache" / slug / "comparator_fulltext.txt"
        write_text(cache_path, fetched.text)

        if fetched.source == "NONE":
            comp = {item: {"present": None, "quote": ""} for item in ITEMS}
        else:
            comp = score_text(fetched.text, COMPARATOR_PATTERNS)

        results[slug] = {
            "pmid": pmid,
            "doi": doi,
            "comparator_fulltext_source": fetched.source,
            "comparator_fulltext_len": fetched.byte_len,
            "comparator_fulltext_path": str(cache_path.relative_to(ROOT)).replace("\\", "/"),
            "fetch_note": fetched.note,
            "ours": ours,
            "ours_quotes": ours_quotes,
            "comparator": comp,
        }
        comp_present = "NA" if fetched.source == "NONE" else sum(1 for item in ITEMS if comp[item]["present"])
        print(
            f"[{slug}] source={fetched.source} bytes={fetched.byte_len} "
            f"ours={sum(ours.values())}/6 comparator={comp_present}/6",
            flush=True,
        )

    with OUT_JSON.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(results, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    write_text(OUT_MD, make_markdown(results))

    included, ours_win, comp_win = fair_totals(results)
    print(f"\nFAIR totals: ours-present/comparator-absent={ours_win}; comparator-present/ours-absent={comp_win}")
    if len(included) != len(results):
        print(f"Excluded from fair count for unobtainable comparator full text: {len(results) - len(included)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
