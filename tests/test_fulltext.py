"""PMC full-text acquisition: structured tables keep per-arm values on their row; supplements are
discovered; spreadsheet/CSV bytes render to row-structured text. Pure functions, no network."""
import io
import sys
import os
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import fulltext  # noqa: E402

# A minimal PMC-style article: prose body + a results table with a per-arm mean/SD row (the exact
# thing body.itertext() flattens into soup) + a supplementary-material reference.
PMC_XML = """<article xmlns:xlink="http://www.w3.org/1999/xlink">
<body>
<sec><title>Results</title>
<p>Cold duration is reported per arm in Table 2.</p>
<table-wrap id="T2"><label>Table 2</label>
<caption><p>Duration of the common cold (days), by treatment arm</p></caption>
<table>
<thead><tr><th>Arm</th><th>n</th><th>Mean</th><th>SD</th></tr></thead>
<tbody>
<tr><td>Zinc</td><td>50</td><td>4.0</td><td>1.2</td></tr>
<tr><td>Placebo</td><td>48</td><td>7.1</td><td>1.5</td></tr>
</tbody>
</table>
</table-wrap>
<supplementary-material id="S1"><media xlink:href="appendix1.xlsx"/></supplementary-material>
</sec>
</body>
</article>"""


def test_parse_extracts_structured_table_with_per_arm_row():
    p = fulltext.parse_pmc_xml(PMC_XML)
    assert p["n_tables"] == 1
    tt = p["table_text"]
    assert "Table 2" in tt and "Duration of the common cold" in tt
    # the per-arm mean/SD stay on one line with their arm label — parseable, not soup
    assert "Zinc | 50 | 4.0 | 1.2" in tt
    assert "Placebo | 48 | 7.1 | 1.5" in tt


def test_supplement_hrefs_discovered():
    p = fulltext.parse_pmc_xml(PMC_XML)
    assert p["supplements"] == ["appendix1.xlsx"]


def test_combined_text_delimits_tables_from_prose():
    p = fulltext.parse_pmc_xml(PMC_XML)
    c = fulltext.combined_text(p)
    assert "Cold duration is reported per arm" in c       # prose
    assert "=== TABLES" in c                               # provenance delimiter
    assert c.index("Cold duration") < c.index("=== TABLES")  # prose before tables


def test_bad_xml_returns_empty_not_crash():
    p = fulltext.parse_pmc_xml("<not-valid")
    assert p == {"body_text": "", "table_text": "", "n_tables": 0, "supplements": []}


def test_xlsx_supplement_renders_row_structured_text():
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Arm", "Mean", "SD"])
    ws.append(["Melatonin", -19.1, 47.3])
    ws.append(["Placebo", -1.7, 47.8])
    buf = io.BytesIO()
    wb.save(buf)
    txt = fulltext.supplement_text_from_bytes("appendix1.xlsx", buf.getvalue())
    assert "Melatonin | -19.1 | 47.3" in txt
    assert "Placebo | -1.7 | 47.8" in txt


def test_non_spreadsheet_supplement_returns_empty():
    # a PDF/image supplement is not guessed at (no OCR); returns '' cleanly
    assert fulltext.supplement_text_from_bytes("figure1.pdf", b"%PDF-1.4 ...") == ""


def test_csv_supplement_renders_rows():
    data = b"arm,mean,sd\nzinc,4.0,1.2\nplacebo,7.1,1.5\n"
    txt = fulltext.supplement_text_from_bytes("data.csv", data)
    assert "zinc | 4.0 | 1.2" in txt and "placebo | 7.1 | 1.5" in txt
