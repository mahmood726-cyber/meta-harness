"""A typed refusal's span must come from the document its reason names.

PLANT (fired pre-fix on main 9d4f4894): glp1 'Adverse events leading to discontinuation', EXSCEL (PMID 28910237)
was REFUSED_ON_EVIDENCE with the reason "held full-text discontinuation counts are restricted to serious adverse
events ..." while its source_span was the ABSTRACT (document_ref records.json#PMID-28910237, source_level 1), so
the harms ascertainment ladder on the served page said "held full text: NOT_CHECKED ... SPAN_NOT_VERIFIED" beside a
reason that quoted the full text. The full text holds the row the reason describes ('Serious adverse event that
resulted in permanent discontinuation of trial regimen' 108 (1.5) vs 104 (1.4)); the refusal now carries it.

The general rule this test enforces on every served review: a REFUSED_ON_EVIDENCE refusal whose reason cites
the full text does not cite the abstract as its span (a SIGNAL_SPURIOUS refusal locates the spurious signal, which
may well sit in the abstract). Pre-fix the rule fired on three rows: EXSCEL discontinuation, EXSCEL and LEADER
gastrointestinal adverse events."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FULLTEXT_RE = re.compile(r"\bfull[- ]text\b", re.I)
REGULATORY_RE = re.compile(r"\b(FDA|EMA|EPAR|label|Table \d+|medical review|statistical review)\b")


def _refusals():
    for path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        for outcome in review.get("outcomes", []):
            for row in outcome.get("declared_absent_trials", []) or []:
                if row.get("typed_refusal") or row.get("refusal_provenance"):
                    yield path.parent.name, outcome.get("name"), row


def test_refusal_citing_the_full_text_does_not_carry_the_abstract_as_its_span():
    offenders = []
    for slug, outcome, row in _refusals():
        reason = str(row.get("reason") or "")
        ref = str(row.get("document_ref") or "")
        if row.get("refusal_provenance") != "REFUSED_ON_EVIDENCE":
            continue  # SIGNAL_SPURIOUS and the mismatch codes locate the SIGNAL, which may well be the abstract
        if FULLTEXT_RE.search(reason) and ("records.json" in ref or row.get("source_level") == 1):
            offenders.append((slug, outcome, row.get("id"), ref))
    assert not offenders, f"refusal reasons citing the full text whose span is the abstract: {offenders}"


def test_refusal_span_is_verbatim_in_the_document_it_names():
    checked = 0
    for slug, outcome, row in _refusals():
        ref = str(row.get("document_ref") or "").split("#")[0]
        span = row.get("source_span") or row.get("verbatim_span")
        if not ref or not span:
            continue
        path = ROOT / ref
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name == "records.json":
            pid = str(row.get("id", "")).replace("PMID ", "")
            data = json.loads(text)
            rec = next((r for r in data.get("records", []) if str(r.get("id")) == pid), {})
            text = (rec.get("abstract") or "") + "\n" + (rec.get("fulltext") or "")
        assert span in text, f"{slug} / {outcome} / {row.get('id')}: span absent from {ref}"
        checked += 1
    assert checked > 0


def test_exscel_discontinuation_refusal_is_bound_to_the_full_text_row():
    review = json.loads((ROOT / "docs/reviews/glp1-ra-mace-t2d/review.json").read_text(encoding="utf-8"))
    outcome = next(o for o in review["outcomes"] if o["name"] == "Adverse events leading to discontinuation")
    row = next(r for r in outcome["declared_absent_trials"] if "28910237" in str(r.get("id")))
    assert row["document_ref"] == "cache/glp1-ra-mace-t2d/ft_28910237.txt"
    assert row["source_level"] == 2
    assert "Serious adverse event that resulted in permanent discontinuation of trial regimen" in row["source_span"]
    assert "108 (1.5)" in row["source_span"] and "104 (1.4)" in row["source_span"]
    assert not str(row["source_span"]).startswith("BACKGROUND:")
