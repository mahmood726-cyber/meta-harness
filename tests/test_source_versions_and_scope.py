"""Source versioning and protocol-text scope (V1.0.1), DOAC-VTE review (hash 5f9c2b44). Written BEFORE
harness/source_versions.py and harness/scope_decision.py.

(1) Hokusai-VTE: a sponsor CSR erratum (26 Feb 2015) is reported to move recurrent VTE 130 -> 131/4,118 and HR 0.89 ->
    0.90; the held FDA labels (2015 and 2023) still carry the original. A version chain per result with a governing
    decision; never a silent overwrite; a correction that is not held cannot govern.
(2) J-EINSTEIN: the erratum corrects some '1.4%' cells and explicitly not Table 3's -> per cell, never a global replace;
    symptomatic recurrence 1/78 vs 0/19, not the broader 1/78 vs 1/19.
(3) Scope from the protocol's own text: J-EINSTEIN and BOTTICELLI are eligible by I1-I4; a basis citing the
    comparator's trial list is refused.
"""
import copy
import json
import os

import pytest

from harness import pipeline

ROOT = pipeline.ROOT
SLUG = "doac-vte-recurrence"
PRIM = "Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)"


def _sv():
    from harness import source_versions
    return source_versions


def _sd():
    from harness import scope_decision
    return scope_decision


def _chain(prefix):
    return copy.deepcopy(next(c for c in _sv().load(ROOT, SLUG) if c["chain_id"].startswith(prefix)))


def test_hokusai_chain_keeps_the_original_while_the_unheld_erratum_is_pending():
    sv = _sv()
    ch = sv.verify_chain(ROOT, _chain("Hokusai-VTE:primary"))
    assert ch["governing"]["state"] == "PENDING" and ch["governing"]["version_id"] == "v0-article-2013"
    v = {x["version_id"]: x for x in ch["versions"]}
    assert v["v1-csr-erratum-2015-02-26"]["held"] is False and "terms" in v["v1-csr-erratum-2015-02-26"]["not_held_reason"]
    assert v["v1-csr-erratum-2015-02-26"]["value"]["ai"] == 131 and v["v0-fda-label-2023-10"]["value"]["ai"] == 130


def test_a_correction_that_is_not_held_cannot_govern():
    sv = _sv()
    ch = _chain("Hokusai-VTE:primary")
    ch["governing"] = {"state": "DECIDED", "version_id": "v1-csr-erratum-2015-02-26", "reason": "later"}
    with pytest.raises(ValueError, match="not held cannot govern"):
        sv.verify_chain(ROOT, ch)


def _review_with(chain, served):
    sv = _sv()
    rev = {"slug": SLUG, "outcomes": [{"name": chain["outcome"], "trials": [dict(served)], "declared_absent_trials": []}]}
    rev["source_versions"] = [sv.verify_chain(ROOT, chain)]
    return rev


def test_a_served_value_superseded_by_a_decided_version_is_refused():
    sv = _sv()
    ch = _chain("J-EINSTEIN")
    # plant: a decided correction whose value differs from the original, and the ORIGINAL still served
    ch["versions"][1]["value"] = {"ai": 2, "n1i": 78, "ci": 0, "n2i": 19}
    rev = _review_with(ch, {"id": "PMID 25717286", "ai": 1, "n1i": 78, "ci": 0, "n2i": 19})
    rev["outcomes"][0]["trials"][0]["version_chain"] = {"chain_id": ch["chain_id"]}
    assert [p["kind"] for p in sv.problems(rev)] == ["VERSION_SUPERSEDED_SERVED"]


def test_a_declared_chain_must_be_shown_on_its_row():
    sv = _sv()
    rev = _review_with(_chain("Hokusai-VTE:primary"), {"id": "PMID 23991658", "effect": 0.89})
    assert [p["kind"] for p in sv.problems(rev)] == ["VERSION_CHAIN_UNSHOWN"]
    sv.attach(rev, ROOT)
    assert rev["outcomes"][0]["trials"][0]["version_chain"]["chain_id"] == "Hokusai-VTE:primary:recurrent-VTE"
    assert sv.problems(rev) == []


def test_j_einstein_erratum_is_applied_per_cell_never_as_a_global_replace():
    sv = _sv()
    ch = _chain("J-EINSTEIN")
    cells = ch["versions"][0]["cells"]
    out = sv.apply_per_cell(cells, [ch["versions"][1]])
    assert out["results: symptomatic recurrent VTE, rivaroxaban %"] == "1.3%"
    assert out["Table 3: rivaroxaban %"] == "1.4%"          # 'calculated by another definition'
    assert out["Table 3: unchanged 2/71 %"] == "2.8%"
    naive = {k: ("1.3%" if v == "1.4%" else v) for k, v in cells.items()}
    assert naive["Table 3: rivaroxaban %"] != out["Table 3: rivaroxaban %"]    # what a global replace would have done
    with pytest.raises(ValueError, match="does not have"):
        sv.apply_per_cell(cells, [{"cells": {"Table 9: x": "1%"}}])


def test_j_einstein_uses_symptomatic_recurrence_not_the_broader_composite():
    kem = json.load(open(os.path.join(ROOT, "docs", "known_eligible_missing.json"), encoding="utf-8"))
    je = next(r for r in kem["topics"][SLUG] if r["trial"] == "J-EINSTEIN")
    st = je["result_states"][PRIM]
    assert st["state"] == "EXTRACTED_NOT_ADMITTED" and "(1/78; 1.4%)" in st["span"] and "none of the 19" in st["span"]
    assert "1/78 vs 1/19 is the broader composite" in st["basis"]
    bo = next(r for r in kem["topics"][SLUG] if r["trial"] == "BOTTICELLI")["result_states"][PRIM]
    assert bo["state"] == "REPORTED_UNRESOLVED" and "asymptomatic" in bo["witness"]["span"]


def test_scope_decisions_come_from_the_protocol_text():
    r = _sd().resolve(ROOT, SLUG)
    assert r["problems"] == []
    d = {x["trial"]: x for x in r["decisions"]}
    for name in ("J-EINSTEIN DVT and PE program", "BOTTICELLI DVT"):
        assert d[name]["decision"] == "ELIGIBLE"
        assert [c["rule"] for c in d[name]["criteria"]] == ["I1", "I2", "I3", "I4"]
        assert all(c["in_protocol"] and c["evidence"] for c in d[name]["criteria"])
    assert "J-EINSTEIN and BOTTICELLI" in r["search_limitation"]


def test_a_rule_not_in_the_protocol_or_a_comparator_list_basis_is_refused(tmp_path, monkeypatch):
    sd = _sd()
    doc = sd.load(ROOT, SLUG)
    bad = copy.deepcopy(doc)
    bad["decisions"][0]["criteria"][0]["protocol_span"] = "**I9** - phase 3 trials only"
    bad["decisions"][1]["decision"] = "INELIGIBLE"
    bad["decisions"][1]["basis"] = "not in the comparator's trial list of six phase-3 trials"
    monkeypatch.setattr(sd, "load", lambda root, slug: bad)
    kinds = sorted(p["kind"] for p in sd.resolve(ROOT, SLUG)["problems"])
    assert kinds == ["SCOPE_INHERITED_FROM_COMPARATOR", "SCOPE_RULE_NOT_IN_PROTOCOL"]


def test_hokusai_major_bleeding_is_reported_and_refused_on_estimand_not_as_absent():
    from harness import verified_inputs as vi
    rows = vi.load(SLUG)["verified_effects.json"]["23991658"]
    mb = next(r for r in rows if r["outcome"] == "Major bleeding")
    assert mb["provenance"] == "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH"
    assert mb["source_span"] == "Major Bleedingb, n (%) 56 (1.4) 66 (1.6)"
    assert mb["supersedes"]["provenance"] == "REFUSED_ON_EVIDENCE"
