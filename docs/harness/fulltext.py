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
