"""kgap.k_gap._html_text must keep the document's STRUCTURE: paragraphs and table rows on their own lines, table cells
'|'-separated. It flattened every tag and newline into ONE line (13 Oct: two PMC article pages came back
as a single 71k-char line), so no line- or table-based deterministic reader could see a table in any HTML copy."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from kgap import k_gap  # noqa: E402
import g1_trial_acquire as ta  # noqa: E402

PAGE = """<html><head><script>var x = "<p>no</p>";</script><style>p{}</style></head><body>
<p>Background text about the trial.</p><div>Results follow.</div>
<table><caption>Table 2. Outcomes</caption>
<thead><tr><th>Outcome</th><th>Drug A (n&nbsp;=&nbsp;200)</th><th>Control B (n = 200)</th></tr></thead>
<tbody><tr><td>28-day all-cause mortality</td><td>40 (20.0)</td><td>50 (25.0)</td></tr>
<tr><td>Ventilator-free days, mean</td><td>1.5</td><td>2.5</td></tr></tbody></table>
<p>Discussion paragraph.</p></body></html>"""


def test_PLANT_html_tables_and_paragraphs_survive_as_lines():
    t = k_gap._html_text(PAGE)
    lines = [ln for ln in t.splitlines() if ln.strip()]
    assert len(lines) >= 6                                       # was 1
    assert "no</p>" not in t and "p{}" not in t                  # script / style dropped
    assert any("|" in ln and "(n = 200)" in ln and ln.count("(n = 200)") == 2 for ln in lines)
    assert "28-day all-cause mortality | 40 (20.0) | 50 (25.0)" in t
    assert "Background text about the trial." in lines[0] or "Background text about the trial." in t


def test_a_table_rendered_from_html_is_readable_by_table_tuple():
    tt = ta.table_tuple(k_gap._html_text(PAGE), ["28-day all-cause mortality", "mortality"], "28 days")
    assert tt and (tt[1]["events_t"], tt[1]["n_t"], tt[1]["events_c"], tt[1]["n_c"]) == (40, 200, 50, 200)


SECTIONED = """<table><thead><tr><th></th><th>Drug A (n = 200)</th><th>Control B (n = 200)</th></tr>
<tr><th></th><th>No. (%)</th><th>No. (%)</th></tr></thead>
<tbody><tr><td colspan="3">Primary outcome</td></tr>
<tr><td>Days free of support, mean</td><td>6.0</td><td>4.0</td></tr>
<tr><td colspan="3">Secondary outcomes</td></tr>
<tr><td>All-cause mortality</td><td>40 (20.0)</td><td>50 (25.0)</td></tr></tbody></table>"""


def test_PLANT_section_rows_and_blank_lines_do_not_end_a_table():
    # 13 Oct: CoDEX's table ended at its 'Primary outcome' section row (a one-cell row with no '|', after a blank line),
    # so table_tuple never reached the mortality row
    t = k_gap._html_text(SECTIONED)
    assert "\n\n" not in t
    tt = ta.table_tuple(t, ["all-cause mortality"], "28 days")
    assert tt and (tt[1]["events_t"], tt[1]["n_t"], tt[1]["events_c"], tt[1]["n_c"]) == (40, 200, 50, 200)
