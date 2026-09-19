"""Mahmood's binding constraint (19 Sep 2026) on the recovered regulatory results: every value goes through the
reproducible harness -- extracted from the held bytes by a regex over spans located verbatim in the held text, with
document_sha256 and offset; a number that arrives from a review note or a manifest field is not a source, and a value
with no located span is REFUSED whatever typed it (a regex reading a wrong cell is as wrong as a model inventing one).

Requirements: every held regulatory fact with a manifest effect carries `value_extraction` (mechanism regex, every
candidate reading listed) and `effect_verified_against_span`; the page prints a regulatory number only when the harness
read it from a located span, else prints WITHHELD; FREEDOM-CVO's HR is read from Table 19's located 3-point row and its
'4-point' reviewer remark is preserved as a conflicting passage under ADJ-GLP1-006 (PROPOSED); the membership
demonstration is computed only from a verified value on the primary pool's own strand. Plant: on bf2af50d the served
facts carry no value_extraction (the numbers were manifest fields), FREEDOM-CVO's only span was a pipe transcription.
"""
import json
import pathlib
import re

from harness import claimgraph, page

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"


def _review():
    return json.loads((ROOT / "docs/reviews" / SLUG / "review.json").read_text(encoding="utf-8"))


def test_every_held_fact_with_an_effect_is_harness_read_from_a_located_span():
    facts = _review().get("held_regulatory_facts") or []
    assert len(facts) >= 3
    for fact in facts:
        if (fact.get("decision") or {}).get("effect") is None:
            continue
        ve = fact.get("value_extraction") or {}
        assert ve.get("mechanism") == "regex", fact["trial"]
        assert fact.get("effect_verified_against_span") is True, (fact["trial"], ve)
        matched = ve["matched"]
        located = {s["kind"]: s for s in fact["spans"]}
        assert matched["span_kind"] in located and located[matched["span_kind"]].get("verbatim_located") is not False
        assert fact["document_sha256"] and fact["extracted_text_sha256"]


def test_freedom_cvo_is_a_source_conflict_read_from_table_19_with_the_4point_remark_preserved():
    fact = next(f for f in _review()["held_regulatory_facts"] if f["trial"] == "FREEDOM-CVO")
    kinds = {s["kind"] for s in fact["spans"]}
    assert {"table19_row_3p", "table19_row_4p", "text_onstudy_3p", "reviewer_remark_labels_4p", "definition_table19"} <= kinds
    assert fact["value_extraction"]["matched"]["span_kind"] == "table19_row_3p"
    assert fact["value_extraction"]["matched"]["estimate"] == 1.24
    assert fact["adjudication"]["id"] == "ADJ-GLP1-006" and fact["adjudication"]["state"] == "PROPOSED"
    assert fact["strand"] == "GLP1RA_ANY_DELIVERY" and fact["primary_strand"] == "CONVENTIONAL_GLP1RA"


def test_a_manifest_effect_with_no_located_span_is_not_verified_and_is_withheld_on_the_page():
    ve = claimgraph.value_extraction({"estimate": 0.5, "ci_low": 0.3, "ci_high": 0.8},
                                     [{"kind": "result", "span": "3-Point MACE | 0.50 (0.30, 0.80)", "verbatim_located": False},
                                      {"kind": "definition", "span": "MACE defined as CV death, MI, stroke", "pdf_page": 3}])
    assert ve["verified"] is False and ve["candidates"] == []
    review = _review()
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    row = next(r for r in primary["known_missing_sensitivity"]["rows"] if r["trial_key"] == "FLOW")
    row["held_fact"]["value_extraction"] = ve
    row["held_fact"]["effect_verified_against_span"] = False
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page.render_page(review)))
    assert "value WITHHELD" in text
    assert "0.82 (0.68, 0.98)" not in text


def test_demonstration_uses_only_a_verified_value_on_the_primary_strand():
    review = _review()
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    demo = primary["known_missing_sensitivity"]["membership_demonstration"]
    assert demo["adjudication"]["id"] == "ADJ-GLP1-005"
    elixa = next(f for f in review["held_regulatory_facts"] if f["trial"] == "ELIXA")
    assert elixa["effect_verified_against_span"] and elixa["strand"] == elixa["primary_strand"]
    assert demo["proposed"]["k"] == 9
