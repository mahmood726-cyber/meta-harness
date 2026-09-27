"""scripts/verify_lane_result.py: a Codex acquisition lane's FOUND rows are re-verified against the bytes it holds,
never trusted. Each defect class is planted on real held documents; the true rows must pass.
XML plants use OMNeON's committed CC0 JATS full text; the PDF plants need CARMELINA's accepted manuscript, which is
held locally only (not redistributed), and skip -- visibly -- where it is absent."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELD = os.path.join(ROOT, "evidence", "acquisition_cascade", "held")
XML = "OMNeON/PMC5594521.xml"
PDF = "CARMELINA/unpaywall.pdf"
SPAN = ("33/2100 patients in the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 "
        "(95% CI 0.35, 1.05)")


def _tree(tmp_path, rels):
    d = tmp_path / "evidence" / "acquisition_cascade"
    (d / "held").mkdir(parents=True)
    (tmp_path / ".lane").mkdir()
    led = {}
    for rel in rels:
        (d / "held" / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(HELD, rel), d / "held" / rel)
        raw = open(os.path.join(HELD, rel), "rb").read()
        led[rel] = {"sha256": hashlib.sha256(raw).hexdigest(), "source": "https://www.ebi.ac.uk/x",
                    "retrieved_utc": "2026-09-27T00:00:00Z", "representation": "ORIGINAL_VERBATIM"}
    (d / "held" / "HELD.json").write_text(json.dumps(led), encoding="utf-8")
    (d / "ATTEMPTS.jsonl").write_text(json.dumps({"url": "http://localhost:4000/x"}) + "\n", encoding="utf-8")
    return led


def _run(tmp_path, rows):
    (tmp_path / ".lane" / "RESULT.json").write_text(json.dumps({"rows": rows}), encoding="utf-8")
    p = subprocess.run([sys.executable, "-X", "utf8", os.path.join(ROOT, "scripts", "verify_lane_result.py"), str(tmp_path)],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    out = json.loads((tmp_path / ".lane" / "VERIFIED.json").read_text(encoding="utf-8"))
    return {r["id"]: r for r in out["rows"]}, out


def test_xml_plants(tmp_path):
    led = _tree(tmp_path, [XML])
    x = open(os.path.join(HELD, XML), encoding="utf-8").read()
    tw = next(t for t in re.findall(r"<table-wrap.*?</table-wrap>", x, flags=re.S)
              if "2092" in " ".join(re.findall(r"<thead\b.*?</thead>", t, flags=re.S)))
    row = re.findall(r"<tr>.*?</tr>", tw.split("</thead>")[1], flags=re.S)[1]
    ai, ci = [int(re.match(r"\d+", re.sub(r"<[^>]+>", "", c).strip()).group())
              for c in re.findall(r"<td.*?</td>", row, flags=re.S)[1:3]]
    assert "4202" in x and "4202" not in " ".join(re.findall(r"<thead\b.*?</thead>", tw, flags=re.S))
    j = x.find("4202")
    outside = x[max(0, j - 25):j + 4]
    assert outside in x and outside not in tw
    b = dict(topic="t", outcome="o", verdict="FOUND", document_ref=f"evidence/acquisition_cascade/held/{XML}",
             document_sha256=led[XML]["sha256"])
    v, out = _run(tmp_path, [
        dict(b, id="good", source_span=SPAN, values={"ci": 33, "n2i": 2100, "effect": 0.60, "ci_low": 0.35, "ci_high": 1.05}),
        dict(b, id="wrong-value", source_span=SPAN, values={"ci": 34}),
        dict(b, id="paraphrase", source_span=SPAN.replace("HR of", "hazard ratio of"), values={}),
        dict(b, id="wrong-hash", document_sha256="0" * 64, source_span=SPAN, values={}),
        dict(b, id="header-good", raw_span=row, source_span="x", values={"ai": ai, "n1i": 2092, "ci": ci, "n2i": 2100}),
        dict(b, id="header-wrong", raw_span=row, source_span="x", values={"ai": ai, "n1i": 2093}),
        dict(b, id="header-elsewhere-only", raw_span=row, source_span="x", values={"n1i": 4202}),
        dict(b, id="leading-zero", source_span="HR of 0.60 (95% CI 0.35, 1.05)", values={"effect": 0.6, "ci_low": 0.35}),
        # an arm-size span quoted from OUTSIDE the row's table: the number is in the paper, not in this table
        dict(b, id="arm-span-other-table", raw_span=row, source_span="x", n1i_span=outside,
             values={"ai": ai, "n1i": 4202, "ci": ci}),
        dict(topic="t", outcome="o", id="PMID 1", verdict="NOT_REPORTED", coverage_inspected="ABSTRACT_VERBATIM"),
    ])
    ok = {k: r["ok"] for k, r in v.items()}
    assert ok == {"good": True, "wrong-value": False, "paraphrase": False, "wrong-hash": False, "header-good": True,
                  "header-wrong": False, "header-elsewhere-only": False, "leading-zero": True,
                  "arm-span-other-table": False, "PMID 1": False}
    assert v["header-good"]["denominators_from_table_header"] == ["n1i", "n2i"]
    assert "localhost" in out["offroute_hosts"]


def test_zero_event_and_unchecked_plants(tmp_path):
    # a SYNTHETIC control document (namespace __control__): never data, never counted
    _tree(tmp_path, [])
    body = ('{"abstractText": "No serious adverse events were reported in either group. Adverse events were similar '
            'between groups. Forty-one patients were randomized to LA85 (n = 41) and 41 to placebo (n = 41)."}').encode()
    rel = "__control__/zero.json"
    (tmp_path / "evidence/acquisition_cascade/held/__control__").mkdir(parents=True)
    (tmp_path / "evidence/acquisition_cascade/held" / rel).write_bytes(body)
    h = hashlib.sha256(body).hexdigest()
    (tmp_path / "evidence/acquisition_cascade/held/HELD.json").write_text(json.dumps({rel: {
        "sha256": h, "source": "https://www.ebi.ac.uk/x", "retrieved_utc": "2026-09-27T00:00:00Z",
        "representation": "ORIGINAL_VERBATIM"}}), encoding="utf-8")
    b = dict(topic="t", outcome="o", verdict="REPORTED_ZERO_EVENTS",
             document_ref=f"evidence/acquisition_cascade/held/{rel}", document_sha256=h)
    v, _ = _run(tmp_path, [
        dict(b, id="zero-good", source_span="No serious adverse events were reported in either group",
             n1i_span="LA85 (n = 41)", n2i_span="placebo (n = 41)", values={"ai": 0, "n1i": 41, "ci": 0, "n2i": 41}),
        dict(b, id="zero-not-stated", source_span="Adverse events were similar between groups",
             n1i_span="LA85 (n = 41)", n2i_span="placebo (n = 41)", values={"ai": 0, "n1i": 41, "ci": 0, "n2i": 41}),
        dict(b, id="zero-no-arm-span", source_span="No serious adverse events were reported in either group",
             values={"ai": 0, "n1i": 41, "ci": 0, "n2i": 41}),
        dict(b, id="zero-wrong-arm", source_span="No serious adverse events were reported in either group",
             n1i_span="LA85 (n = 41)", n2i_span="placebo (n = 41)", values={"ai": 0, "n1i": 42, "ci": 0, "n2i": 41}),
        dict(topic="t", outcome="o", id="not-held", verdict="NOT_HELD"),
    ])
    assert {k: r["ok"] for k, r in v.items()} == {"zero-good": True, "zero-not-stated": False,
                                                  "zero-no-arm-span": False, "zero-wrong-arm": False, "not-held": None}


def test_thin_space_denominator_inside_the_same_table(tmp_path):
    # SYNTHETIC control: a Lancet-style table whose arm sizes sit in a body section row as '10 033'
    _tree(tmp_path, [])
    row = "<tr><td>Any event</td><td>30 (0·3%)</td><td>34 (0·3%)</td></tr>"
    body = ("<article><table><thead><tr><th/><th>Drug</th><th>Placebo</th></tr></thead><tbody>"
            "<tr><td>Thromboembolic</td><td>10 033</td><td>9985</td></tr>" + row +
            "</tbody></table><p>In all, 20 000 were screened.</p></article>").encode("utf-8")
    rel = "__control__/lancet.xml"
    (tmp_path / "evidence/acquisition_cascade/held/__control__").mkdir(parents=True)
    (tmp_path / "evidence/acquisition_cascade/held" / rel).write_bytes(body)
    h = hashlib.sha256(body).hexdigest()
    (tmp_path / "evidence/acquisition_cascade/held/HELD.json").write_text(json.dumps({rel: {
        "sha256": h, "source": "https://www.ebi.ac.uk/x", "retrieved_utc": "2026-09-27T00:00:00Z",
        "representation": "ORIGINAL_VERBATIM"}}), encoding="utf-8")
    b = dict(topic="t", outcome="o", verdict="FOUND", document_ref=f"evidence/acquisition_cascade/held/{rel}",
             document_sha256=h, raw_span=row, source_span="x")
    v, _ = _run(tmp_path, [
        dict(b, id="same-table", n1i_span="<td>10 033</td>", n2i_span="<td>9985</td>",
             values={"ai": 30, "n1i": 10033, "ci": 34, "n2i": 9985}),
        dict(b, id="outside-table", n1i_span="20 000 were screened", values={"ai": 30, "n1i": 20000}),
    ])
    assert {k: r["ok"] for k, r in v.items()} == {"same-table": True, "outside-table": False}


@pytest.mark.skipif(not os.path.exists(os.path.join(HELD, PDF)), reason="CARMELINA manuscript is held locally only")
def test_pdf_plants(tmp_path):
    pypdf = pytest.importorskip("pypdf")
    led = _tree(tmp_path, [PDF])
    pages = [re.sub(r"\s+", " ", p.extract_text() or "").strip() for p in pypdf.PdfReader(os.path.join(HELD, PDF)).pages]
    i = next(k for k, t in enumerate(pages) if "209 of 3494" in t)
    span = re.search(r"Hospitalization for heart failure occurred in 209 of 3494.*?\(HR, 0\.90; 95% CI, 0\.74-1\.08;",
                     pages[i]).group(0)
    other = next(k for k, t in enumerate(pages) if k != i and "3494" in t)
    b = dict(topic="t", outcome="o", verdict="FOUND", document_ref=f"evidence/acquisition_cascade/held/{PDF}",
             document_sha256=led[PDF]["sha256"])
    v, _ = _run(tmp_path, [
        dict(b, id="good", source_span=span, values={"ai": 209, "n1i": 3494, "effect": 0.9, "ci_low": 0.74, "ci_high": 1.08}),
        dict(b, id="wrong-ci", source_span=span, values={"ci_high": 1.18}),
        dict(b, id="not-on-page", source_span="Hospitalization for heart failure occurred in 210 of 3494", values={}),
        dict(b, id="header-other-page", source_span="Hospitalization for heart failure occurred in 209 of 3494",
             header_span=pages[other][:40], values={"n2i": 3485}),
    ])
    assert {k: r["ok"] for k, r in v.items()} == {"good": True, "wrong-ci": False, "not-on-page": False,
                                                  "header-other-page": False}
    assert v["good"]["representation"] == "pypdf page text"
