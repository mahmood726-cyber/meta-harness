"""Source preservation and coverage (V1.0.1), DPP-4 review. Written BEFORE harness/source_coverage.py.

(1) The committed record for OMNeON (PMID 28893244) is an EDITED abridgement of its abstract: both hHF result sentences
    are removed, so the page said HHF was "not found in the abstract" while the verbatim abstract reports hHF 20/2092 vs
    33/2100, HR 0.60 (0.35-1.05). Coverage (VERBATIM / EXCERPT / ALTERED / UNVERIFIED) is measured against the verbatim
    original held by the cascade; an absence on an EXCERPT or ALTERED record is never a publication-level claim.
(2) TECOS 3-point MACE from the EMA SmPC table (745/7,332 vs 746/7,339, HR 0.99 (0.89-1.10), ITT, Cox stratified by
    region), distinct from its 4-point primary; bound with its population and model.
(3) CARMELINA HHF 209 vs 226, HR 0.90 (0.74-1.08) from its results.
"""
import copy
import json
import os

import pytest

from harness import fetch, pipeline

ROOT = pipeline.ROOT
SLUG = "dpp4-mace-t2d"
HHF = "Hospitalization for heart failure"
MACE3 = "3-point major adverse cardiovascular events"
CACHE = {x["id"]: x for x in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))["records"]}


def _sc():
    from harness import source_coverage
    return source_coverage


def test_coverage_classes_against_the_verbatim_original():
    sc = _sc()
    assert sc.coverage_of("28893244", CACHE["28893244"]["abstract"])["coverage"] == sc.ALTERED
    assert sc.coverage_of("30418475", CACHE["30418475"]["abstract"])["coverage"] == sc.VERBATIM
    assert sc.coverage_of("26052984", CACHE["26052984"]["abstract"])["coverage"] == sc.VERBATIM
    v = sc.verbatim_record("28893244")["text"]
    s = sc._sentences(v)
    assert sc.classify(v, v) == sc.VERBATIM
    assert sc.classify(". ".join(s[:4]) + ".", v) == sc.EXCERPT
    assert sc.classify("anything", None) == sc.UNVERIFIED


def test_an_excerpt_that_omits_an_outcome_never_supports_an_absence_claim():
    # PLANT: OMNeON's abridged record, the outcome absent from it
    from harness import result_status as rs
    sc = _sc()
    row = {"id": "PMID 28893244", "reason_code": "OUTCOME_NOT_IN_SOURCE",
           "reason": "no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract"}
    rev = {"outcomes": [{"name": HHF, "trials": [], "declared_absent_trials": [dict(row)], "result": {}}]}
    sc.attach(rev, CACHE)
    rs.derive(rev, {HHF: ["hospitalization for heart failure", "heart failure"]})
    st = rev["outcomes"][0]["declared_absent_trials"][0]["result_status"]
    assert st["state"] == rs.REPORTED_UNRESOLVED and st["coverage"] == sc.ALTERED
    assert rs.problems(rev) == []
    stored = copy.deepcopy(rev)
    stored["outcomes"][0]["declared_absent_trials"][0]["result_status"] = {"state": rs.RETRIEVED_NOT_REPORTED}
    assert [p["kind"] for p in rs.problems(stored)] == ["ABSENCE_ON_EXCERPT"]
    # with no verbatim mention either, the state is 'publication not inspected', never 'not reported'
    assert rs.status_of({**row, "source_coverage": {"coverage": sc.EXCERPT}}, False, set())["state"] == rs.NOT_YET_RETRIEVED


def test_a_not_reported_statement_names_its_coverage():
    from harness import result_status as rs
    sc = _sc()
    row = {"id": "PMID 30418475", "reason_code": "OUTCOME_NOT_IN_SOURCE",
           "reason": "no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract",
           "source_coverage": sc.coverage_of("30418475", CACHE["30418475"]["abstract"])}
    st = rs.status_of(row, False, set())
    assert st["state"] == rs.RETRIEVED_NOT_REPORTED and st["coverage"] == sc.VERBATIM and "(verbatim)" in st["statement"]
    row2 = dict(row, source_coverage={"coverage": sc.UNVERIFIED})
    assert "coverage UNVERIFIED" in rs.status_of(row2, False, set())["statement"]


def test_held_originals_carry_hash_source_and_retrieval_time():
    led = json.load(open(os.path.join(ROOT, "evidence", "acquisition_cascade", "held", "HELD.json"), encoding="utf-8"))
    rows = {k: v for k, v in led.items() if not k.startswith("_")}
    assert rows and all(v.get("sha256") and v.get("source") and v.get("retrieved_utc") for v in rows.values())
    assert all(v.get("representation") == "ORIGINAL_VERBATIM" for v in rows.values())


_OUT = {}


def _outcome(name):
    if name not in _OUT:
        config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
        if "inp" not in _OUT:
            _OUT["inp"] = pipeline.outcome_inputs(SLUG, config, fetch.ensure(config, ""))
        spec, kind = next((s, k) for s, k in pipeline._outcome_specs(config) if s["name"] == name)
        _OUT[name] = pipeline.build_outcome_from_inputs(_OUT["inp"], spec, kind, SLUG)
    return _OUT[name]


def test_omneon_and_carmelina_hhf_are_bound_from_the_publications():
    rows = {t["id"]: t for t in _outcome(HHF)["trials"]}
    o, c = rows["PMID 28893244"], rows["PMID 30418475"]
    assert (o["effect"], o["ci_low"], o["ci_high"]) == (0.60, 0.35, 1.05) and o["hand_binding_state"] == "BOUND"
    assert (c["effect"], c["ci_low"], c["ci_high"]) == (0.90, 0.74, 1.08) and c["hand_binding_state"] == "BOUND"
    assert o["target_endpoint_class"] == c["target_endpoint_class"] == "EXACT_TARGET"


def test_tecos_3_point_mace_is_bound_from_the_ema_table_not_the_4_point_primary():
    t = next(t for t in _outcome(MACE3)["trials"] if t["id"] == "PMID 26052984")
    assert (t["effect"], t["ci_low"], t["ci_high"]) == (0.99, 0.89, 1.10)
    assert t["hand_binding_state"] == "BOUND" and t["target_endpoint_class"] == "EXACT_TARGET"
    from harness import hand_binding as hb, verified_inputs as vi
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    e = next(vi.runtime(x) for x in vi.load(SLUG)["verified_effects.json"]["26052984"] if x["outcome"] == MACE3)
    assert e["analysis_population"].startswith("intention-to-treat") and "stratified by region" in e["analysis_model"]
    # the 4-point primary row, same table, same document: a different composite, refused
    four = dict(e, id="PMID 26052984", effect=0.98, ci_low=0.89, ci_high=1.08,
                source_span=None)
    four.pop("source_span")
    cls = hb.bind_hand_row(config["primary_outcome"], four)
    assert cls["target_endpoint_class"] != "EXACT_TARGET"


def test_the_tecos_version_chain_names_its_population_model_and_the_row_it_is_not():
    from harness import source_versions as sv
    ch = sv.verify_chain(ROOT, next(c for c in sv.load(ROOT, SLUG) if c["chain_id"] == "TECOS:3-point-MACE"))
    v = {x["version_id"]: x for x in ch["versions"]}["v1-ema-smpc"]
    assert v["held"] and v["value"]["ai"] == 745 and v["value"]["n2i"] == 7339
    assert "stratified by region" in v["cells"]["model"] and "839" in v["cells"]["not this row"]
    assert ch["governing"]["state"] == "DECIDED"


# --- classifier error rate (2026-09-27): with 211 verbatim originals held, the sentence/label classifier graded 99
# ALTERED; the differences checked were section-label artefacts ('The aim of' -> 'The of' by a case-insensitive label
# strip, half-stripped 'Conclusions and relevance', unknown headings 'Study design' / 'Main outcome and measures').
# A heading difference is not an alteration; a changed number, an inserted or a removed result sentence is.
_LABEL_ONLY = [("balanced-crystalloids-vs-saline-mortality", "34375394"), ("colchicine-postop-af", "22090167"),
               ("probiotics-aad-prevention", "10547243"), ("omega3-cardiovascular-events", "20952767"),
               ("tocilizumab-covid19-mortality", "33080005")]


@pytest.mark.parametrize("slug,pmid", _LABEL_ONLY)
def test_heading_differences_are_not_alterations(slug, pmid):
    sc = _sc()
    recs = {str(x["id"]): x for x in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["records"]}
    assert sc.coverage_of(pmid, recs[pmid]["abstract"])["coverage"] == sc.VERBATIM


def test_real_edits_are_still_detected():
    sc = _sc()
    v = sc.verbatim_record("28893244")["text"]
    assert sc.classify(v, v) == sc.VERBATIM
    assert sc.classify(v.replace("20/2092", "21/2092"), v) == sc.ALTERED          # a changed number
    assert sc.classify(v.replace("placebo group", "placebo arm"), v) == sc.ALTERED  # a changed word
    plain = sc._plain(v)
    cut = plain.replace("The hHF outcome occurred in 20/2092 patients", "")
    assert sc.classify(cut, v) in (sc.EXCERPT, sc.ALTERED) and sc.classify(cut, v) != sc.VERBATIM
    first_half = plain[: len(plain) // 2].rsplit(". ", 1)[0] + "."
    assert sc.classify(first_half, v) == sc.EXCERPT                               # a prefix: an excerpt
    cov = sc.coverage_of("28893244", CACHE["28893244"]["abstract"])
    assert cov["coverage"] == sc.ALTERED and any("20/2092" in m for m in cov["missing_text"])  # named, not just counted
