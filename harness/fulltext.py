"""PMC OA full-text acquisition — body prose + STRUCTURED tables + supplementary files.

The plain `body.itertext()` join flattens table cells into unparseable soup, yet per-arm
means/SDs, event counts and person-time overwhelmingly live in tables (and in supplementary
spreadsheets/appendices). This module renders each `<table-wrap>` as row-structured text so a
per-arm value keeps its row context ("Zinc | 4.0 | 1.2  Placebo | 7.1 | 1.5"), and discovers +
extracts supplementary files. It NEVER interprets a number — it only makes the verbatim source
legible so the model can locate a span, deterministic code can parse it, and round-trip can decide.

Pure functions (parse_pmc_xml, _render_tables, supplement_hrefs) are network-free and fixture-tested;
fetch_supplements does the OA-package download and file-text extraction and is kept separate.
"""
from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
import zipfile

XLINK = "{http://www.w3.org/1999/xlink}href"


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _row_cells(tr) -> list[str]:
    """Cells of one <tr>, each cell's text flattened, preserving cell boundaries."""
    return [_clean(" ".join(c.itertext())) for c in tr if c.tag in ("td", "th")]


def _render_one_table(tw) -> str:
    """Render a <table-wrap> as row-structured text: label + caption, then each row as
    'cell | cell | cell'. Keeps a per-arm value on the same line as its row/column labels so a
    parser (or the model locating a span) sees the structure the flattened itertext destroys."""
    label_el = tw.find(".//label")
    label = _clean(" ".join(label_el.itertext())) if label_el is not None else ""
    cap_el = tw.find(".//caption")
    caption = _clean(" ".join(cap_el.itertext())) if cap_el is not None else ""
    lines = []
    for tr in tw.findall(".//tr"):
        cells = _row_cells(tr)
        if any(cells):
            lines.append(" | ".join(cells))
    if not lines:
        return ""
    head = f"TABLE {label}".strip() + (f": {caption}" if caption else "")
    return head + "\n" + "\n".join(lines)


def _render_tables(root) -> str:
    """All tables in the document, each block separated by a blank line."""
    blocks = [b for tw in root.findall(".//table-wrap") if (b := _render_one_table(tw))]
    return "\n\n".join(blocks)


def supplement_hrefs(root) -> list[str]:
    """xlink:href of every supplementary-material / inline-supplementary-material / media element —
    the file names inside the PMC OA package (spreadsheets, appendices, docx). De-duplicated, order
    preserved. These are where evidence has hidden; fetch_supplements resolves and extracts them."""
    out, seen = [], set()
    for tag in ("supplementary-material", "inline-supplementary-material", "media"):
        for el in root.findall(f".//{tag}"):
            href = el.get(XLINK)
            if href and href not in seen:
                seen.add(href)
                out.append(href)
    return out


def parse_pmc_xml(xml: str) -> dict:
    """Parse a PMC article XML into {body_text, table_text, n_tables, supplements}. Pure; no network.
    body_text is the prose (as before); table_text is the row-structured table rendering; supplements
    is the list of hrefs to fetch. Returns empty fields on any parse failure (full text is optional)."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return {"body_text": "", "table_text": "", "n_tables": 0, "supplements": []}
    body = root.find(".//body")
    body_text = _clean(" ".join(body.itertext())) if body is not None else ""
    table_text = _render_tables(root)
    return {"body_text": body_text, "table_text": table_text,
            "n_tables": len(root.findall(".//table-wrap")),
            "supplements": supplement_hrefs(root)}


def combined_text(parsed: dict) -> str:
    """The full searchable text: prose then a clearly-delimited TABLES section. The delimiter lets a
    reader/model see which spans came from a table vs prose (provenance stays legible)."""
    parts = [parsed.get("body_text", "")]
    if parsed.get("table_text"):
        parts.append("\n\n=== TABLES (structured; cell boundaries = ' | ') ===\n" + parsed["table_text"])
    return "\n".join(p for p in parts if p).strip()


TABLES_MARKER = "=== TABLES (structured; cell boundaries = ' | ') ==="
SUPPLEMENT_MARKER = "=== SUPPLEMENTARY FILES ==="
# A table whose caption says it describes WHO was randomised, not WHAT happened to them. Its cells carry
# numbers next to outcome-like words ("history of atrial fibrillation 21 (18%)"), which the abstract
# extractor reads as event counts. Found 2026-09-29 by the k-gap full-text counterfactual: PMID 32295417
# ("Baseline demographic and clinical characteristics") admitted 202/206 vs 193/194 as outcome events, and
# PMID 39497860 an age table as a mean difference.
BASELINE_TABLE = re.compile(
    r"\bbaseline\b|\bdemographic|characteristics of (?:the )?(?:study |enrolled |included )?"
    r"(?:patients|participants|subjects|population|cohort|women|men|children)"
    r"|\b(?:patient|participant|subject|clinical|population) characteristics\b", re.I)


def _inline_table_span(prose: str, head: str, body: list[str]):
    """(start, end) of a table's flattened copy inside the prose, or None. Exact rebuilt text first; else ANCHORED:
    the label+caption as start and the last row's flattened text as end, found in that order and no further
    apart than 1.5x the table's own length (+200). A copy that repeats its label inside the table (DO-HEALTH,
    PMID 38199870: '... analyses. Table 1 Overall ...') defeats the exact match but not the anchors."""
    cap = _clean(head[len("TABLE "):].replace(": ", " ", 1)) if head.startswith("TABLE ") else _clean(head)
    rows = [_clean(ln.replace(" | ", " ")) for ln in body if ln.strip()]
    flat = _clean(" ".join([cap] + rows))
    i = prose.find(flat) if flat else -1
    if i >= 0:
        return i, i + len(flat)
    if not cap or not rows:
        return None
    # start anchor: the caption as rendered, else the caption text alone (no label, no trailing footnote marks,
    # first 60 chars) -- 'Table 1.: Baseline ... *' is rendered inline as 'Table 1. Baseline ...'
    capt = re.sub(r"^\S+\s+\S+?[.:]*\s*", "", cap) if cap.lower().startswith("table") else cap
    capt = re.sub(r"[\s*†‡§]+$", "", capt)[:60]
    starts = [k for k in (prose.find(cap), prose.find(capt) if len(capt) >= 15 else -1) if k >= 0]
    if not starts:
        return None
    i = min(starts)
    j = prose.find(rows[-1], i + min(len(cap), len(capt)))
    if j < 0:
        return None
    end = j + len(rows[-1])
    return (i, end) if end - i <= 1.5 * len(flat) + 200 else None


def _inline_trace(prose: str, head: str, body: list[str]) -> bool:
    """Any sign of the table inside the prose: its caption text, or any of its rows (flattened, >=25 chars)."""
    cap = _clean(head[len("TABLE "):].replace(": ", " ", 1)) if head.startswith("TABLE ") else _clean(head)
    rows = [_clean(ln.replace(" | ", " ")) for ln in body if ln.strip()]
    return (len(cap) >= 20 and cap in prose) or any(len(r) >= 25 and r in prose for r in rows)


def extraction_segments(text: str) -> dict:
    """Split a combined full text (combined_text output) into what an extractor may read as SEPARATE units:
    the prose (unchanged), and each row of each non-baseline table (verbatim 'cell | cell' lines, with the
    table's header line kept beside them for provenance). Baseline/demographic tables are DROPPED and listed.
    Supplementary-file lines are rows too. Nothing is rewritten: every row is a substring of the input, so a
    span taken from a row is a span of the committed source.

    Why rows are separate units: the extractor splits sentences on '. ' + capital, and table rows carry no
    periods, so a whole TABLES section was one 'sentence' in which a keyword in one row and numbers in another
    co-occurred."""
    text = text or ""
    if TABLES_MARKER not in text and SUPPLEMENT_MARKER not in text:
        return {"prose": text, "rows": [], "dropped_tables": [], "baseline_inline_not_located": []}
    prose, _, rest = text.partition(TABLES_MARKER) if TABLES_MARKER in text else (text, "", "")
    sup = ""
    if SUPPLEMENT_MARKER in prose:
        prose, _, sup = prose.partition(SUPPLEMENT_MARKER)
    if SUPPLEMENT_MARKER in rest:
        rest, _, sup = rest.partition(SUPPLEMENT_MARKER)
    rows, dropped, not_located = [], [], []
    for block in [b for b in rest.split("\n\n") if b.strip()]:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        head = lines[0].strip() if lines and lines[0].startswith("TABLE") else ""
        body = lines[1:] if head else lines
        if head and BASELINE_TABLE.search(head):
            dropped.append(head[:160])
            # parse_pmc_xml's body_text is <body> itertext, which INCLUDES every table flattened inline -- so a
            # baseline table dropped here was still read from the "prose" (PMID 39497860: its age table became
            # a mean difference). Remove that inline copy, rebuilt from the rendered block; if it cannot be
            # located verbatim, say so rather than pretend the prose is clean.
            span = _inline_table_span(prose, head, body)
            if span:
                prose = prose[:span[0]] + " " + prose[span[1]:]
            elif _inline_trace(prose, head, body):
                not_located.append(head[:160])   # part of the table IS in the prose but cannot be bounded
            # else: the table is not in the prose at all (its table-wrap sits outside <body>) -- nothing to remove
            continue
        rows += [{"table": head[:160], "row": ln.strip()} for ln in body]
    rows += [{"table": "SUPPLEMENT", "row": ln.strip()} for ln in sup.split("\n") if ln.strip()]
    return {"prose": _clean(prose), "rows": rows, "dropped_tables": dropped,
            "baseline_inline_not_located": not_located}


# ---- supplementary-file text extraction (network + file parsing; kept separate) --------------

def _xlsx_to_text(data: bytes, max_rows: int = 400) -> str:
    """Render an .xlsx as row-structured text (sheet name + each row 'cell | cell'). Read-only, values
    only (never formulas). Bounded so a huge supplement cannot blow up the cache."""
    import openpyxl  # local import: only needed when a supplement is actually a spreadsheet
    try:
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception:  # noqa: BLE001 - a corrupt/unsupported book is just "no text"
        return ""
    out = []
    for ws in wb.worksheets:
        out.append(f"SHEET {ws.title}")
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= max_rows:
                out.append("… (truncated)")
                break
            cells = [("" if c is None else str(c)) for c in row]
            if any(cells):
                out.append(" | ".join(cells))
    return "\n".join(out).strip()


def _csv_to_text(data: bytes, max_rows: int = 400) -> str:
    import csv as _csv
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return ""
    rows = list(_csv.reader(io.StringIO(text)))
    lines = [" | ".join(r) for r in rows[:max_rows] if any(x.strip() for x in r)]
    if len(rows) > max_rows:
        lines.append("… (truncated)")
    return "\n".join(lines).strip()


def supplement_text_from_bytes(name: str, data: bytes) -> str:
    """Extract row-structured text from a supplementary file by extension. Spreadsheets and CSV are
    the high-value formats (per-arm SD tables); other types return '' (no guessing, no OCR)."""
    n = (name or "").lower()
    if n.endswith((".xlsx", ".xlsm")):
        return _xlsx_to_text(data)
    if n.endswith(".csv") or n.endswith(".tsv"):
        return _csv_to_text(data)
    return ""


def iter_oa_package(tar_bytes: bytes):
    """Yield (member_name, bytes) for each file in a PMC OA .tar.gz package. Used to pull the actual
    supplement files, which the article XML references only by name."""
    import tarfile
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tf:
        for m in tf.getmembers():
            if m.isfile():
                f = tf.extractfile(m)
                if f is not None:
                    yield m.name, f.read()
